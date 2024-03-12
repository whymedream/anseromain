import disnake
import traceback
from disnake.ext import commands

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.errors_channel_id = 1192998646745149543

'''    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        try:
            channel = self.bot.get_channel(self.errors_channel_id)
            orig_error = getattr(error, "original", error)
            error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
            emb = disnake.Embed()
            emb.add_field(name="Error", value=f'```{error_msg}```', inline=False)
            emb.add_field(name="Command", value=ctx.command, inline=False)
            emb.add_field(name="Channel", value=ctx.channel, inline=False)
            emb.add_field(name="User", value=ctx.author, inline=False)
            emb.add_field(name="Guild", value=ctx.guild, inline=False)
            emb.add_field(name="Message", value=ctx.message.content, inline=False)
            await channel.send(embed=emb)
        except:
            print(error_msg)'''

def setup(bot):
    bot.add_cog(Errors(bot))
