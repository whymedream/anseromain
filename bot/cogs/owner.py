import disnake
from bot.cogs.economy import INVISIBLE
from disnake.ext import commands
import json
from bot.functions import send_error
from bot.mongodb import *
import ast

with open('bot/config.json', 'r') as f:
    owner_data = json.load(f)

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, text: str = None):
        with open('bot/config.json', 'r') as f:
            data = json.load(f)
        if ctx.author.id in data['BOT']["owner_ids"]:
            await ctx.message.delete()
            if text is None:
                await ctx.author.send('Вы не указали текст для отправки.')
            emb = disnake.Embed(description=text)
            emb.color = INVISIBLE
            await ctx.send(embed=emb)
        else:
            await send_error(ctx, 'Данная команда доступна только для создателей бота.')

    @commands.command(aliases=['add_badge', 'ab'])
    async def addbadge(self, ctx: commands.Context, icon: str = None, id: int = None):
        with open('bot/config.json', 'r') as f:
            data = json.load(f)
        if ctx.author.id in data['BOT']["owner_ids"]:
            if icon is None and id is None:
                await ctx.author.send(f'Пример использования: {ctx.prefix}add_badge :heart: <ID пользователя> <ID сервера>')
            if icon is None:
                await ctx.author.send('Вы не указали значок для добавления.')
            else:
                if id is None:
                    id = ctx.author.id
                badges = await db.badges.find_one({'uid': id})
                await db.badges.update_one({"uid": id}, {'$set': {'badges': badges['badges']+f' {icon}'}})
                await ctx.send('Значок добавлен.')
    

    @commands.command(aliases=["eval", "exec"])
    async def e(self, ctx, *, cmd):
        if ctx.author.id in owner_data["BOT"]["owner_ids"]:
            try:
                fn_name = "_eval_expr"
                cmd = cmd.strip("` ")
                cmd = "\n".join(f" {i}" for i in cmd.splitlines())
                body = f"async def {fn_name}():\n{cmd}"
                parsed = ast.parse(body)
                body = parsed.body[0].body
                insert_returns(body)
                env = {"self": self,
                        'bot': self.bot,
                        'disnake': disnake,
                        'commands': commands,
                        'ctx': ctx,
                        '__import__': __import__,
                        'users': db.users,
                        "db": db}
                exec(compile(parsed, filename="<ast>", mode="exec"), env)
                result = (await eval(f"{fn_name}()", env))
            except Exception as error:
                emb = disnake.Embed(title=f"❌ Произошла ошибка", description=str(error), color=0xff0000)
                await ctx.send(embed=emb)
        else:
            await ctx.send("Отказано в доступе")
    
    @commands.command()
    async def emoji_all(self, ctx):
        if ctx.author.id in owner_data["BOT"]["owner_ids"]:
            emb = disnake.Embed()
            emb.title = 'Стандартные эмоджи бота:'
            emoji = owner_data['EMOJI']
            for item in emoji.items():
                emb.add_field(name=item[0], value=item[1])
            await ctx.send(embed=emb)
        else:
            await ctx.send("Отказано в доступе")

def setup(bot: commands.Bot):
    bot.add_cog(Owner(bot))