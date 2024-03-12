import disnake
from bot.cogs.economy import INVISIBLE
from disnake.ext import commands
from bot.functions import send_error
from bot.mongodb import *

with open('bot/config.json', 'r') as f:
    emoji_data = json.load(f)

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='симпатия', aliases=['лайк'])
    async def like(self, ctx: commands.Context, member: disnake.User = None):
        """
        **Выдать симпатию пользователю дискорд сервера**\n
        Пример использования: `!симпатия @User123`
        """
        user = await get_user(ctx.guild.id, member.id)
        badges = await db.badges.find_one({'uid': member.id})
        if badges is None:
            await db.badges.insert_one({
            "uid": member.id,
            "badges": '',
            })
            badges = await db.badges.find_one({'uid': member.id})
        if member is None:
            await send_error(ctx, 'Укажите пользователя которому вы хотите выдать симпатию\nПример: !like @Ansero')
            return
        else:
            if ctx.author == member:
                await send_error(ctx, 'Вы не можете выдать симпатию самому себе')
                return
            elif ctx.author.id not in user["subscribers"]:
                await db.users.update_one({"gid": ctx.guild.id, "uid": member.id}, {"$inc": {"likes": 1}})
                await db.users.update_one({"gid": ctx.guild.id, "uid": member.id}, {"$push": {"subscribers": ctx.author.id}})
                user = await get_user(ctx.guild.id, member.id)
                emb_in_dm = disnake.Embed(color=0x2b2d31)
                emb_in_dm.set_author(name=f'{member} | Оповещения')
                emb_in_dm.description = f'{member.mention}\nВам выдали симпатию на сервере {ctx.guild.name}'
                emb_in_dm.add_field(name='`❤️`Количество симпатий:', value=f'{user["likes"]}')
                await member.send(embed=emb_in_dm)
                await ctx.message.add_reaction(emoji_data["EMOJI"]["success"])
            else:
                await send_error(ctx, 'Вы уже выдали симпатию этому пользователю')
                return

def setup(bot: commands.Bot):
    bot.add_cog(Other(bot))