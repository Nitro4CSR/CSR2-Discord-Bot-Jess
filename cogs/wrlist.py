import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WRlistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_wrlist", description="❗Select one more variable from above❗ Compiles a custom list of WR times")
    @app_commands.describe(car="Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car", rarity="Select an option from Above", tier="Select an option from Above", csr2_version="The CSR2 version the car was released in format: `<OTA_version (optional)> <release_version>`")
    @app_commands.choices(rarity=[app_commands.Choice(name="5 Gold Stars", value="(LENGTH(records.★) == 125 AND records.★ LIKE '<:G%')"), app_commands.Choice(name="5 Purple Stars", value="(LENGTH(records.★) == 125 AND records.★ LIKE '<:P%')"), app_commands.Choice(name="5 Stars", value="LENGTH(records.★) == 125"), app_commands.Choice(name="4 Gold Stars", value="(LENGTH(records.★) == 100 AND records.★ LIKE '<:G%')"), app_commands.Choice(name="4 Purple Stars", value="(LENGTH(records.★) == 100 AND records.★ LIKE '<:P%')"), app_commands.Choice(name="4 Stars", value="LENGTH(records.★) == 100"), app_commands.Choice(name="3 Gold Stars", value="(LENGTH(records.★) == 75 AND records.★ LIKE '<:G%')"), app_commands.Choice(name="3 Purple Stars", value="(LENGTH(records.★) == 75 AND records.★ LIKE '<:P%')"), app_commands.Choice(name="3 Stars", value="LENGTH(records.★) == 75"), app_commands.Choice(name="2 Gold Stars", value="(LENGTH(records.★) == 50 AND records.★ LIKE '<:G%')"), app_commands.Choice(name="2 Purple Stars", value="(LENGTH(records.★) == 50 AND records.★ LIKE '<:P%')"), app_commands.Choice(name="2 Stars", value="LENGTH(records.★) == 50"), app_commands.Choice(name="1 Gold Stars", value="(LENGTH(records.★) == 25 AND records.★ LIKE '<:G%')"), app_commands.Choice(name="1 Purple Stars", value="(LENGTH(records.★) == 25 AND records.★ LIKE '<:P%')"), app_commands.Choice(name="1 Stars", value="LENGTH(records.★) == 25"), app_commands.Choice(name="Gold Stars", value="records.★ LIKE '%:GS:%'"), app_commands.Choice(name="Purple Stars", value="records.★ LIKE '%:PS:%'"), app_commands.Choice(name="Non Star", value="records.★ LIKE '%0 Stars%'")])
    @app_commands.choices(tier=[app_commands.Choice(name="Tier 5/T5", value="<:T5:1331668428318183467>"), app_commands.Choice(name="Tier 4/T4", value="<:T4:1331668411394035794>"), app_commands.Choice(name="Tier 3/T3", value="<:T3:1331668398567850126>"), app_commands.Choice(name="Tier 2/T2", value="<:T2:1331668383996838011>"), app_commands.Choice(name="Tier 1/T1", value="<:T1:1331668370902356039>")])
    async def wrlist_command(self, interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        logger.info(f"The following command has been used: /csr2_wrlist car: {car}, rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
        log = f"The following command has been used: /csr2_wrlist car: {car}, rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
        await interaction.response.defer()
        
        # Use default tier "T5" only if car, rarity, and tier are all None
        if not any([car, rarity, tier, csr2_version]):
            tier = "T5"

        # Fetch results
        results, log = await self.fetch_all_results(interaction, car, rarity, tier, csr2_version, log)
        logger.info(f"{len(results)} results found")
        log += f"\n{len(results)} results found"
        
        if len(results) > 0:
            # Determine if we need to split into two embeds
            t1_t3_results = []
            t4_t5_results = []

            for row in results:
                if any(tier in row[3] for tier in ["T1", "T2", "T3"]):
                    t1_t3_results.append(row)
                if any(tier in row[3] for tier in ["T4", "T5"]):
                    t4_t5_results.append(row)

            if t1_t3_results and t4_t5_results:
                logger.info("2 embeds")
                view1 = PaginatedView(t1_t3_results, interaction.user, car, rarity, "T1-T3", csr2_version)
                view2 = PaginatedView(t4_t5_results, interaction.user, car, rarity, "T4-T5", csr2_version)
                
                await interaction.followup.send("**T1 - T3 Results**", embed=await view1.get_embed_page(), view=view1)
                await interaction.followup.send("**T4 - T5 Results**", embed=await view2.get_embed_page(), view=view2)
                await in_app_logging.send_log(self.bot, log, interaction)
            else:
                logger.info("1 embed")
                view = PaginatedView(results, interaction.user, car, rarity, tier, csr2_version)
                await view.start(interaction)
                await in_app_logging.send_log(self.bot, log, interaction)
        else:
            logger.info("Sending message...")
            log += "Sending message..."
            await in_app_logging.send_log(self.bot, log, interaction)
            await interaction.followup.send("No results found.")

    async def fetch_all_results(self, interaction: discord.Interaction, car: str, rarity: str, tier: str, csr2_version: str, log: str):
        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Construct the query with optional filters
        parameters = []
        query = """\nSELECT records."Ingame Name Clarification", records."WR-BEST ET", records."★", records.UniqueID\nFROM records"""
        
        if csr2_version:
            query += """\nJOIN info ON records.UniqueID = info.UniqueID"""

        query += """\nWHERE "WR-BEST ET" IS NOT NULL AND "WR-BEST ET" <> '0.000'"""

        if car:
            # Validate the input value
            primary_key_valid = car.startswith('T') and len(car) > 1 and car[1] in '12345'
            db_name_valid = "_" in car
            if primary_key_valid:
                query += """ AND records.UniqueID COLLATE NOCASE LIKE ?"""
            elif db_name_valid:
                query += """ AND records."DB Name" COLLATE NOCASE LIKE ?"""
            else:
                query += """ AND records."Ingame Name Clarification" COLLATE NOCASE LIKE ?"""
            parameters.append(f"%{car}%")

        # Add rarity and tier filter if provided
        if rarity:
            query += f""" AND {rarity}"""
        if tier:
            query += """ AND records.Un LIKE ?"""
            parameters.append(f"%{tier}%")
        if csr2_version:
            if "OTA" in csr2_version:
                csr2_version = f"""Added into the game in {csr2_version[:4]} Update {csr2_version[5:]}"""
            else:
                csr2_version = f"""Added into the game in Update {csr2_version}"""
            query += """ AND info."Vision Info" LIKE ?"""
            parameters.append(f"{csr2_version}%")
        query += """\nORDER BY records."WR-BEST ET" """

        logger.info(f"The following query has been used: {query}\nThe following parameters were used: {parameters}")
        log += f"\nThe following query has been used: {query}\nThe following parameters were used: {parameters}"

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            return rows, log
        except sqlite3.OperationalError as e:
            logger.error(f"Database error occurred: {e}")
            await interaction.followup.send(f"Database error occurred: {e}")
            log += f"\nDatabase error occurred: {e}"
            await in_app_logging.send_log(self.bot, log, interaction)
            return []
        finally:
            conn.close()

class PageJumpModal(discord.ui.Modal, title="Jump to Page"):
    page_number = discord.ui.TextInput(label="Enter Page Number or +/- Offset", required=True)

    def __init__(self, view: "PaginatedView"):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            input_text = self.page_number.value.strip()
            if input_text.startswith(('+', '-')):
                offset = int(input_text)
                new_page = (self.view.page_number + offset - 1) % self.view.max_pages + 1
            else:
                new_page = int(input_text)
                if new_page < 1 or new_page > self.view.max_pages:
                    new_page = (new_page - 1) % self.view.max_pages + 1

            self.view.page_number = new_page
            embed = await self.view.get_embed_page()
            await interaction.response.edit_message(embed=embed, view=self.view)
        except ValueError:
            await interaction.response.send_message("Invalid input. Please enter a number.", ephemeral=True)

class PaginatedView(discord.ui.View):
    def __init__(self, results, user, car, rarity, tier, csr2_version):
        super().__init__(timeout=300)
        self.results = results
        self.user = user
        self.car = car
        self.rarity = rarity
        self.tier = tier
        self.csr2_version = csr2_version
        self.page_number = 1
        self.page_size = 10
        self.max_pages = len(results) // self.page_size + (1 if len(results) % self.page_size != 0 else 0)
        self.message = None

    async def get_embed_page(self):
        start_index = (self.page_number - 1) * self.page_size
        end_index = start_index + self.page_size
        page_results = self.results[start_index:end_index]

        # Handle None values for title
        car_display = self.car if self.car else "Any Car"
        if self.rarity:
            if "125" in self.rarity:
                if "<:G" in self.rarity:
                    self.rarity = "5 Gold Stars"
                elif "<:P" in self.rarity:
                    self.rarity = "5 Purple Stars"
                else:
                    self.rarity = "5 Stars"
            elif "100" in self.rarity:
                if "<:G" in self.rarity:
                    self.rarity = "4 Gold Stars"
                elif "<:P" in self.rarity:
                    self.rarity = "4 Purple Stars"
                else:
                    self.rarity = "4 Stars"
            elif "75" in self.rarity:
                if "<:G" in self.rarity:
                    self.rarity = "3 Gold Stars"
                elif "<:P" in self.rarity:
                    self.rarity = "3 Purple Stars"
                else:
                    self.rarity = "3 Stars"
            elif "50" in self.rarity:
                if "<:G" in self.rarity:
                    self.rarity = "2 Gold Stars"
                elif "<:P" in self.rarity:
                    self.rarity = "2 Purple Stars"
                else:
                    self.rarity = "2 Stars"
            elif "25" in self.rarity:
                if "<:G" in self.rarity:
                    self.rarity = "1 Gold Star"
                elif "<:P" in self.rarity:
                    self.rarity = "1 Purple Star"
                else:
                    self.rarity = "1 Star"
            else:
                self.rarity = "Any Rarity"

        rarity_display = f"{self.rarity}" if self.rarity else "Any Rarity"
        tier_display = f"Tier {self.tier}" if self.tier else "Any Tier"
        version_display = f"CSR Version {self.csr2_version}" if self.csr2_version else "Any Version"

        logger.info(f"Constructing Embed for page {self.page_number}")
        embed = discord.Embed(
            title=f"WR List for {car_display}, {rarity_display}, {tier_display}, {version_display}",
            description="\n".join(
                f"{start_index + i + 1}. {row[0]}\n{row[2]} | {float(row[1]):.3f}s"
                for i, row in enumerate(page_results)
            ),
            color=discord.Color(0xff00ff)
        )
        embed.set_footer(text=f"Page {self.page_number} of {self.max_pages}")
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        return embed

    async def start(self, interaction: discord.Interaction):
        logger.info(f"Sending initial Embed with buttons")
        embed = await self.get_embed_page()
        self.message = await interaction.followup.send(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You can't interact with this button!", ephemeral=True)
            return

        self.page_number -= 1
        if self.page_number < 1:
            self.page_number = self.max_pages
        
        logger.info(f"Going to previous page: {self.page_number}")
        embed = await self.get_embed_page()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You can't interact with this button!", ephemeral=True)
            return

        self.page_number += 1
        if self.page_number > self.max_pages:
            self.page_number = 1

        logger.info(f"Going to next page: {self.page_number}")
        embed = await self.get_embed_page()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Jump to Page", style=discord.ButtonStyle.secondary)
    async def jump_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("You can't interact with this!", ephemeral=True)
        await interaction.response.send_modal(PageJumpModal(self))

    async def on_timeout(self):
        logger.info("Button view timed out, restarting pagination.")
        new_view = PaginatedView(self.results, self.user, self.car, self.rarity, self.tier, self.csr2_version)
        embed = await new_view.get_embed_page()
        if self.message:
            await self.message.edit(embed=embed, view=new_view)
        self.stop()

async def setup(bot):
    await bot.add_cog(WRlistCog(bot))
