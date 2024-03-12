import disnake

from disnake.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))