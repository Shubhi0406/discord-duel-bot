import discord
import asyncio
from datetime import datetime, timezone
from stats import *
import settings

class Buttons(discord.ui.View):
    def __init__(self, ctx, target, *, timeout=120):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.target = [target]
        self.clicked = False
    
    @discord.ui.button(label="Accept",style=discord.ButtonStyle.green, custom_id="accept")
    async def accept_duel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clicked = True

        # only allow targeted user to click buttons
        if interaction.user in self.target:
            await interaction.response.edit_message(content="Duel accepted! I will create a thread and wait for 5 seconds. You may begin at 'GO!'.", view=None)
            await asyncio.sleep(1)
            thread = await interaction.message.create_thread(name=f"Duel at {datetime.now(timezone.utc).strftime('%m/%d/%Y, %H:%M:%S')}", auto_archive_duration=1440)
            settings.duels[thread] = {}

            # 5 sec countdown
            countdown_message = await thread.send("Begin in 5...")
            for i in range(4, 0, -1):
                await asyncio.sleep(1)
                await countdown_message.edit(content=f"Begin in {i}...")
            await asyncio.sleep(1)
            await countdown_message.edit(content="GO!")

            # set duel information and player stats
            self.target.append(self.ctx.author)
            settings.duels[thread]["members"] = self.target
            create_user_stats(self.target, thread)
            await send_stats(thread, self.target, settings.duels[thread]["player_stats"])
            
        else:
            await interaction.response.send_message("You are not authorized to accept this duel.", ephemeral=True)
    
    @discord.ui.button(label="Decline",style=discord.ButtonStyle.red, custom_id="decline")
    async def decline_duel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clicked = True
        # only allow targeted user to respond
        if interaction.user in self.target:
            await interaction.response.edit_message(content="Duel declined.", view=None)
        else:
            await interaction.response.send_message("You are not authorized to decline this duel.", ephemeral=True)
    
    # expire challenge if no response for 2 mins
    async def on_timeout(self) -> None:
        if self.clicked:
            return
        return await self.ctx.reply("The challenge has expired.")