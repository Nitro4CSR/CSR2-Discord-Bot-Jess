import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import tunes_manager
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class CommunityTuneCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('COMMUNITY_TUNE_CMD_NAME'), description=localisation.get('COMMUNITY_TUNE_CMD_DESC'))
    @discord.app_commands.describe(tune_id=localisation.get('COMMUNITY_TUNE_CMD_TUNE_ID'), car=localisation.get('COMMUNITY_TUNE_CMD_CAR'), tier=localisation.get('COMMUNITY_TUNE_CMD_TIER'), rarity=localisation.get('COMMUNITY_TUNE_CMD_RARITY'), purpose=localisation.get('COMMUNITY_TUNE_CMD_PURPOSE'), creator=localisation.get('COMMUNITY_TUNE_CMD_CREATOR'))
    @app_commands.choices(rarity=helpers.load_command_options_rarity(localisation))
    @app_commands.choices(tier=helpers.load_command_options_tier(localisation))
    async def communitytunes(self, interaction: discord.Interaction, car: str = None, tune_id: int = None, tier: str = None, rarity: str = None, purpose: str = None, creator: str = None):
        await interaction.response.defer()
        try:
            header = localisation.get('COMMUNITY_TUNE_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('COMMUNITY_TUNE_CMD_NAME')} car: {car} tune_id: {tune_id} tier: {tier} rarity: {rarity} purpose: {purpose} creator: {creator}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('COMMUNITY_TUNE_CMD_NAME')} car: {car} tune_id: {tune_id} tier: {tier} rarity: {rarity} purpose: {purpose} creator: {creator}"
            if any([car, tune_id, tier, rarity, purpose, creator]):
                results = await tunes_manager.query_tune(car, tune_id, tier, rarity, purpose, creator)
                if results:
                    logger.info(f"{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}")
                    log += f"\n{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}"
                    route = await helpers.get_send_route(len(results), interaction.user.id, interaction.guild.id if interaction.guild else None)
                    if route == 2:
                        await interaction.followup.send(f"{localisation.get('MSG_WARNING_OVER_LIMITS')}" if interaction.guild else f"{localisation.get('MSG_WARNING_OVER_LIMIT')}")
                    else:
                        messages, log = await self.create_embeds(results, log)
                        log = await self.send_channel(interaction, messages, log) if route == 0 else await self.send_dms(interaction, messages, log)
                else:
                    await interaction.followup.send(f"{localisation.get('MSG_NOTICE_NO_RESULTS')}")
                    logger.info(f"{header}{localisation.get('LOG_NO_RESULTS')}")
                    log += f"\n{header}{localisation.get('LOG_NO_RESULTS')}"
            else:
                await interaction.followup.send(f"{localisation.get('MSG_ERROR_NO_VARIABLE')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('LOG_ERROR_NO_VARIABLE')}")
                log += f"\n{header}{localisation.get('LOG_ERROR_NO_VARIABLE')}"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def create_embeds(self, results: list, log: str):
        header = localisation.get('COMMUNITY_TUNE_LOG_HEADER')
        logger.info(f"{header}{localisation.get('LOG_BUILD_EMBEDS')}")
        log += f"\n{header}{localisation.get('LOG_BUILD_EMBEDS')}"
        messages = []
        batch = []
        for row in results:
            result = list(row)
            result[59] = 0.000 if not result[59] else result[59]
            embed = discord.Embed(
                title=result[2],
                description=f"# {await helpers.emojify_tier(result[3])}   {await helpers.emojify_rarity(result[4])}",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_PP')} {result[5]}\n{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_EVO')} {result[6]}", value=f"", inline=False)
            embed.add_field(name=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_PART')}                                      {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_UPGRADES')}", value=f"`{localisation.get('PART_EN_MO')}        {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[7]}\n{localisation.get('PART_TU_BA')}       {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[14]}\n{localisation.get('PART_IN_IN')}     {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[21]}\n{localisation.get('PART_NI_OV')}   {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[28]}\n{localisation.get('PART_BODY')}                {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[35]}\n{localisation.get('PART_TIRES')}               {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[42]}\n{localisation.get('PART_TRANSMISSION')}        {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} {result[49]}`", inline=False)
            embed.add_field(name=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_PART')}                                Fusions", value=f"\n**`{localisation.get('PART_EN_MO')}`**`\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[8]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[9]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[10]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[11]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[12]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[13]}`**`\n{localisation.get('PART_TU_BA')}`**`\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[15]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[16]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[17]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[18]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[19]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[20]}`**`\n{localisation.get('PART_IN_IN')}`**`\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[22]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[23]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[24]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[25]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[26]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[27]}`", inline=False)
            embed.add_field(name=f"`{localisation.get('PART_NI_OV')}`", value=f"` - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[29]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[30]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[31]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[32]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[33]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[34]}`\n**`{localisation.get('PART_BODY')}`**`\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[36]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[37]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[38]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[39]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[40]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[41]}`\n**`{localisation.get('PART_TIRES')}`**`\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[43]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[44]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[45]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[46]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[47]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[48]}`\n**`{localisation.get('PART_TRANSMISSION')}`**`\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 1:         {result[50]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 2:         {result[51]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 3:         {result[52]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 4:         {result[53]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 5:         {result[54]}\n - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_STAGE')} 6:         {result[55]}`\n", inline=False)
            embed.add_field(name=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_TUNING')}", value=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_NOS')} {result[56]}\n{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_FD')} {result[57]}\n{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_TP')} {result[58]}\n\n{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_DYNO')} {float(result[59]):.3f}", inline=False)
            embed.add_field(name=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_PURPOSE')} {result[60]}", value=f"**{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_USAGE')}**\n{result[61]}\n\n-# {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_CREATOR')} {result[62]} ({result[63]})", inline=False)
            embed.set_footer(text=f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_TUNE_ID')} {result[0]} - {localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_DB_NAME')} {result[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            batch.append(embed)

            if len(batch) == 2:
                messages.append(batch)
                batch = []

        if batch:
            messages.append(batch)

        logger.info(f"{header}{localisation.get('LOG_EMBEDS_BUILD')}")
        log += f"\n{header}{localisation.get('LOG_EMBEDS_BUILD')}"
        return messages, log

    async def send_channel(self, interaction: discord.Interaction, messages: list, log: str):
        header = localisation.get('CUSTOMSQL_LOG_HEADER')
        await interaction.followup.send(f"{localisation.get('MSG_NOTICE_FETCH')}")
        for message in messages:
            await interaction.followup.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{localisation.get('LOG_DONE_CHANNEL')}")
        log += f"\n{header}{localisation.get('LOG_DONE_CHANNEL')}"
        return log

    async def send_dms(self, interaction: discord.Interaction, messages: list, log: str):
        header = localisation.get('CUSTOMSQL_LOG_HEADER')
        if interaction.guild:
            await interaction.followup.send(f"{localisation.get('MSG_NOTICE_OVER_SERVER_LIMIT')}")
        try:
            await interaction.user.send(f"{localisation.get('MSG_NOTICE_FETCH')}") if interaction.guild else await interaction.followup.send(f"{localisation.get('MSG_NOTICE_FETCH')}")
        except discord.Forbidden:
            await interaction.followup.send(f"{localisation.get('MSG_WARNING_DMS_CLOSED')}", ephemeral=True)
            logger.info(f"{header}{localisation.get('LOG_ERROR_CLOSED')}")
            log += f"\n{header}{localisation.get('LOG_ERROR_CLOSED')}"
            return log
        for message in messages:
            await interaction.user.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{localisation.get('LOG_DONE_DM')}")
        log += f"\n{header}{localisation.get('LOG_DONE_DM')}"
        if interaction.guild:
            await interaction.followup.send(f"{localisation.get('MSG_NOTICE_SENT_DMS')}", ephemeral=True)
        return log

async def setup(bot):
    await bot.add_cog(CommunityTuneCog(bot))
