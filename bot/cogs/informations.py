import disnake
from disnake.ext import commands
from bot.mongodb import db
from bot.mongodb import get_user, get_currency
import asyncio
from bot.cogs.economy import task
import pymongo


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name='бот-инфо', aliases=['info', 'botinfo', 'bot-info', 'ботинфо'])
    async def bot(self, ctx: commands.Context):
        """
        **Посмотреть информацию о боте**\n
        Пример использования: `!бот-инфо`
        """
        regs = 0
        async for _ in db.users.find({}):
            regs += 1
        embed = disnake.Embed(color=0x303136)
        embed.title = 'Bot Information'
        embed.description = f"**~ Система**\n" \
                            f"**• Пинг:** `{round(self.bot.latency * 1000, 2)}мс`\n" \
                            f"**~ Сервера**\n" \
                            f"**• Количество серверов:** `{len(self.bot.guilds)}`\n" \
                            f"**• Зарегистрированные пользователи:** `{regs}`\n\n"
        embed.set_footer(text='Developer: Физик#3333, Лис#3221',
                        icon_url='https://emoji.gg/assets/emoji/5579-developerbadge.png?t=1616827671%27')
        embed.add_field(name='~ Ссылки',
                        value=f'[Пригласить бота](https://discord.com/api/oauth2/authorize?client_id=1105949383645745275&permissions=8&scope=bot)'\
                              f'\n[Сервер поддержки]('
                              f'https://discord.gg/xbNMu3JRUC)')
        ca = self.bot.user.created_at
        embed.add_field(inline=False, name="~ Bot creation date",
                        value=f'<t:{int(ca.timestamp())}> (<t:{int(ca.timestamp())}:R>)')

        embed.add_field(inline=False, name="ВНИМАНИЕ!",
                        value=f'Бот находится на стадии разработки!\nПо всем вопросам обращаться на сервер поддержки!')

        await ctx.send(embed=embed)
    
    @commands.command(name='профиль', aliases=['user-info', 'user-profile', 'юзер', 'пользователь', 'p', 'п', 'user'])
    async def profile(self, ctx: commands.Context, member: disnake.Member = None):
        """
        **Посмотреть профиль дискорд сервера (свой/другого участника)**\n
        Пример использования: `!профиль, !профиль @User123`
        """
        if member is None:
            member = ctx.author
        user = await get_user(ctx.guild.id, member.id)
        badges = await db.badges.find_one({'uid': member.id})
        if badges is None:
            await db.badges.insert_one({
            "uid": member.id,
            "badges": '',
            })
            badges = await db.badges.find_one({'uid': member.id})
        emb = disnake.Embed(color=0x2b2d31)
        emb.set_author(name=f'{member} | Профиль')
        emb.set_thumbnail(url=member.display_avatar)
        emb.set_footer(text=f'ID: {member.id}', icon_url=member.display_avatar)
        if member.id == 1064250083899625482:
            emb.add_field(name='`👷‍♂️`Должность', value='Разработчик')
        if member.id == 594200610631581697:
            emb.add_field(name='`👷‍♂️`Должность', value='Кот с кружкой')
        if badges['badges'] != '':
            emb.add_field(name='Значки', value=f'{badges["badges"]}', inline=False)
        emb.add_field(name=f'`💸`Баланс', value=f'{user["balance"]}')
        emb.add_field(name='`❤️`Симпатии', value=f'{user["likes"]}\n')
        emb.add_field(name='`✉`Количество сообщений', value=f'{user["messages"]}', inline=False)
        emb.add_field(name='`📩`Выполнено команд', value=f'{user["commands_done"]}')
        if ctx.author != member and ctx.author.id not in user["subscribers"]:
            components = [
                disnake.ui.Button(style=disnake.ButtonStyle.green, label='❤️', custom_id='like'),
            ]
        else:
            components = None
        message: disnake.Message = await ctx.send(embed=emb, components=components)
        try:
            button_click: disnake.MessageInteraction = await self.bot.wait_for('button_click', timeout=60.0, check=lambda i: i.author == ctx.author and i.message.id == message.id)
            if button_click.component.custom_id == 'like':
                await db.users.update_one({"gid": ctx.guild.id, "uid": member.id}, {"$inc": {"likes": 1}})
                await db.users.update_one({"gid": ctx.guild.id, "uid": member.id}, {"$push": {"subscribers": ctx.author.id}})
                user = await get_user(ctx.guild.id, member.id)
                emb_in_dm = disnake.Embed(color=0x2b2d31)
                emb_in_dm.set_author(name=f'{member} | Оповещения')
                emb_in_dm.description = f'{member.mention}\nВам выдали симпатию на сервере {ctx.guild.name}'
                emb_in_dm.add_field(name='`❤️`Количество симпатий:', value=f'{user["likes"]}')
                await member.send(embed=emb_in_dm)
                emb = disnake.Embed(color=0x2b2d31)
                emb.set_author(name=f'{member} | Профиль')
                emb.set_thumbnail(url=member.display_avatar)
                emb.set_footer(text=f'ID: {member.id}', icon_url=member.display_avatar)
                if badges["badges"] != '':
                    emb.add_field(name='Значки', value=f'{user["badges"]}', inline=False)
                emb.add_field(name=f'`💸`Баланс', value=f'{user["balance"]}')
                emb.add_field(name='`❤`Симпатии', value=f'{user["likes"]}\n')
                emb.add_field(name='`✉`Количество сообщений', value=f'{user["messages"]}', inline=False)
                emb.add_field(name='`📩`Выполнено команд', value=f'{user["commands_done"]}')
                await message.edit(components = [
                disnake.ui.Button(style=disnake.ButtonStyle.green, label='❤️', custom_id='like', disabled=True),
                ], embed=emb)
        except asyncio.TimeoutError:
            await message.edit(components = [
                disnake.ui.Button(style=disnake.ButtonStyle.green, label='❤️', custom_id='like', disabled=True),
            ])
    
    @commands.command(name='топ')
    async def top(self, ctx: disnake.MessageInteraction):
        """
        **Посмотреть топ по балансу на дискорд сервере**\n
        Пример использования: `!топ`
        """
        currency = await get_currency(ctx.guild.id)
        title = f'{currency}           Топ 10 по балансу          {currency}'
        param = 'balance'
        user_list = []
        async for _ in db.users.find({'gid': ctx.guild.id}) \
                .sort([(param, pymongo.DESCENDING)]).limit(10):
            if _ not in user_list:
                user_list.append(_)
        description = ''
        x = 0
        for user in user_list:
            i = user['uid']
            try:
                member = await ctx.guild.fetch_member(i)
                rew_list = ['🏆', '🥈', '🥉']
                x += 1
                if x <= 3:
                    description += f'\n{rew_list[x - 1]} **{member.display_name}**\n' \
                                   f'> **`💲 Наличные:` {task(user[param])}** {currency}\n' \
                                   f'> **`💳 Банк:` {task(user["bank"])}** {currency}\n'
                else:
                    description += f'\n{x}. {member.display_name}\n' \
                                   f'> `💲 Наличные:` {task(user[param])} {currency}\n' \
                                   f'> `💳 Банк:` {task(user["bank"])} {currency}\n'
            except (Exception,):
                await db.users.delete_one({'gid': ctx.guild.id, 'uid': user['uid']})
        embed = disnake.Embed(description=description, color=0x303136, title=title)
        await ctx.send(embed=embed)
    
    @commands.command(name='лтоп', aliases=['лайк-топ'])
    async def ltop(self, ctx: disnake.MessageInteraction):
        """
        **Посмотреть топ по симпатиям на дискорд сервере**\n
        Пример использования: `///`
        """
        currency = await get_currency(ctx.guild.id)
        title = f'❤️           Топ 10 по симпатиям          ❤️'
        param = 'likes'
        user_list = []
        async for _ in db.users.find({'gid': ctx.guild.id}) \
                .sort([(param, pymongo.DESCENDING)]).limit(10):
            if _ not in user_list:
                user_list.append(_)
        description = ''
        x = 0
        for user in user_list:
            i = user['uid']
            try:
                member = await ctx.guild.fetch_member(i)
                rew_list = ['🏆', '🥈', '🥉']
                x += 1
                if x <= 3:
                    description += f'\n{rew_list[x - 1]} **{member.display_name}**\n' \
                                   f'> **`❤️ Симпатии:` {task(user[param])}**\n'
                else:
                    description += f'\n{x}. {member.display_name}\n' \
                                   f'> **`❤️ Симпатии:` {task(user[param])}**\n'
            except (Exception,):
                await db.users.delete_one({'gid': ctx.guild.id, 'uid': user['uid']})
        embed = disnake.Embed(description=description, color=0x303136, title=title)
        await ctx.send(embed=embed)
        
        

def setup(bot):
    bot.add_cog(Info(bot))