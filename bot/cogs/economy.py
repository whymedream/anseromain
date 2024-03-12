import disnake
from bot.mongodb import *
from disnake.ext import commands
import random
import datetime
import asyncio
import pymongo
from bot.functions import *
INVISIBLE = 0x2b2d31

with open('bot/config.json', 'r') as f:
    emoji_data = json.load(f)

def task(value):
    return f'{value:,}'


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='баланс', aliases=['bal', 'бал', '$'])
    async def balance(self, ctx: commands.Context, member: disnake.Member = None):
        """
        **Посмотреть баланс (свой/другого участника)**\n
        Пример использования: `!баланс`/`!баланс @User123`
        """
        if member is None:
            member = ctx.author
        currency = await get_currency(ctx.guild.id)
        mem = await db.users.find_one({'gid': member.guild.id, 'uid': member.id})
        emb = disnake.Embed()
        emb.set_author(name=f'{member}', icon_url=member.display_avatar, url=f'https://discordapp.com/users/{member.id}/')
        emb.add_field(name=f'Наличные:', value=f'{mem["balance"]:,} {currency}')
        emb.add_field(name=f'Банк:', value=f'{mem["bank"]:,} {currency}')
        emb.add_field(name=f'Всего:', value=f'{(mem["balance"] + mem["bank"]):,} {currency}')
        emb.colour = INVISIBLE
        await ctx.send(embed=emb)
    
    @commands.command(name='депозит', aliases=['dep', 'деп'])
    async def deposit(self, ctx: commands.Context, iamount):
        """
        **Положить деньги в банк**\n
        Пример использования: `!депозит 100`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        currency = await get_currency(ctx.guild.id)
        amount = get_amount(iamount, user)
        if amount <= 0:
            await send_error(ctx, f'Количество **денег для депозита** должно быть больше **0**')
            return
        elif user['balance'] < amount:
            await send_error(ctx, f'Для депозита нехватает **{task(amount-user["balance"])} {currency}**')
            return
        await db.users.update_one({'gid': ctx.guild.id, 'uid':ctx.author.id}, {'$inc': {'balance': -amount, 'bank': amount}})
        gifs = [
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683970956673106/HopefulPlasticIchthyostega-size_restricted.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683976891609220/u_8e7d8ddc7161a53354168700c1d4a8f3_800.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683979043283074/5badf72a895a0a9d6ff371ef364d56af.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683980947501179/72qy.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107684014678093956/money_piles.gif',
        ]
        emb = disnake.Embed()
        emb.set_author(name=f'{ctx.author} | депозит в банк', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["creditcard1"]}**Переведено:** {task(amount)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["creditcard"]}**Банк:** {task(user["bank"]+amount)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Наличные:** {task(user["balance"]-amount)} {currency}', inline=False, name='')
        emb.colour = INVISIBLE
        emb.set_thumbnail(url=random.choice(gifs))
        await ctx.send(embed=emb)
    
    @commands.command(name='вывод', aliases=['with'])
    async def withdraw(self, ctx: commands.Context, iamount):
        """
        **Вывести деньги из банка**\n
        Пример использования: `!вывод 100`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        currency = await get_currency(ctx.guild.id)
        if iamount in ['all', 'full', 'все', 'всё']:
            amount = int(user['bank'])
        elif iamount in ['half', 'половину', 'половина']:
            amount = int(user['bank'] / 2)
        elif int(iamount):
            amount = int(iamount)
        if amount <= 0:
            await send_error(ctx, f'Количество **денег для вывода** из банка должно быть больше **0**')
            return
        elif user['bank'] < amount:
            await send_error(ctx, f'Для вывода нехватает **{task(amount-user["bank"])} {currency}**')
            return
        await db.users.update_one({'gid': ctx.guild.id, 'uid':ctx.author.id}, {'$inc': {'balance': amount, 'bank': -amount}})
        gifs = [
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683970956673106/HopefulPlasticIchthyostega-size_restricted.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683976891609220/u_8e7d8ddc7161a53354168700c1d4a8f3_800.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683979043283074/5badf72a895a0a9d6ff371ef364d56af.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683980947501179/72qy.gif',
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107684014678093956/money_piles.gif',
        ]
        emb = disnake.Embed()
        emb.set_author(name=f'{ctx.author} | вывод из банка', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["creditcard1"]}**Выведено:** {task(amount)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["creditcard"]}**Банк:** {task(user["bank"]-amount)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Наличные:** {task(user["balance"]+amount)} {currency}   ', inline=False, name='')
        emb.set_thumbnail(url=random.choice(gifs))
        emb.colour = INVISIBLE
        await ctx.send(embed=emb)
    
    @commands.command(name='перевести', aliases=['перевод', 'transfer'])
    async def pay(self, ctx: commands.Context, member = None, iamount = None):
        """
        **Перевести деньги другому пользователю**\n
        Пример использования: `!перевести @User123 100`
        """
        if member is None or iamount is None:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nПример: {ctx.prefix}pay <@Пользователь> <сумма(целое число)>')
            return
        try: iamount = int(iamount)
        except: iamount = str(iamount)
        if type(iamount) == str and iamount not in ['all', 'full', 'все', 'всё',
                                                        'half', 'половину', 'половина']:
            await send_error(ctx, f'Проверте аргументы использованой команды!\nСумма перевода должна быть целым числом!\nВозможно вы хотели написать: **all**, **full**, **все**, **всё**, **half**, **половину**')
            return
        mem_id = int(str(member).replace('<@', '').replace('>', ''))
        try: member = ctx.guild.get_member(mem_id)
        except: pass
        if isinstance(member, disnake.Member) is False:
            await send_error(ctx, f'Проверте аргументы использованой команды!\nПользователь которому вы хотите передать средства должен быть упомянут\n<@Пользователь>')
        member1 = await get_user(ctx.guild.id, ctx.author.id)
        member2 = await get_user(ctx.guild.id, member.id)
        currency = await get_currency(ctx.guild.id)
        if iamount in ['all', 'full', 'все', 'всё']:
            amount = int(member1['balance'])
        elif iamount in ['half', 'половину', 'половина']:
            amount = int(member1['balance'] / 2)
        elif int(iamount):
            amount = int(iamount)
        if amount <= 0:
            await send_error(ctx, f'Количество **денег для перевода** другому пользователю должно быть больше **0**')
            return
        elif member1['balance'] < amount:
            await send_error(ctx, f'Для перевода нехватает **{task(amount-member1["balance"])} {currency}**')
            return
        elif ctx.author == member:
            await send_error(ctx, f'Вы не можете перевести деньги самому себе!')
            return
        await db.users.update_one({'gid': ctx.guild.id, 'uid':ctx.author.id}, {'$inc': {'balance': -amount}})
        await db.users.update_one({'gid': ctx.guild.id, 'uid':member.id}, {'$inc': {'balance': amount}})
        gifs = [
            'https://cdn.discordapp.com/attachments/1107059277157376000/1107683979043283074/5badf72a895a0a9d6ff371ef364d56af.gif'
        ]
        emb = disnake.Embed()
        emb.set_author(name=f'{ctx.author} | перевод', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["creditcard1"]}**Переведено:** {task(amount)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Баланс** {ctx.author.mention}: {task(member1["balance"]-amount)}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Баланс** {member.mention}: {task(member2["balance"]+amount)}', inline=False, name='')
        emb.set_thumbnail(url=random.choice(gifs))
        emb.colour = INVISIBLE
        await ctx.send(embed=emb)
    
    @commands.command(name='бонус')
    @commands.cooldown(1, 18000 * 1 * 1, commands.BucketType.member)
    async def bonus(self, ctx: commands.Context):
        """
        **Получить бонусную валюту**\n
        Пример использования: `!бонус`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        likes = user['likes']
        server = await get_server(ctx.guild.id)
        currency = await get_currency(ctx.guild.id)
        count = random.randint(server['bonus'][0], server['bonus'][1])
        count = int(int(count))+int(((likes*count)*0.1))
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': count}})
        emb = disnake.Embed()
        emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["bonus"]}**Бонус:** {task(count)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] + count)} {currency}', inline=False, name='')
        emb.color = INVISIBLE
        await ctx.send(embed=emb)

    
    @bonus.error
    async def bonus_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
            await send_error(ctx, f'До получения бонуса подождите: {retry_after}')
    
    @commands.command(name='работа', aliases=['работать'])
    @commands.cooldown(1, 7200 * 1 * 1, commands.BucketType.member)
    async def work(self, ctx: commands.Context):
        """
        **Заработать виртуальную валюту**\n
        Пример использования: `!работа`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        likes = user['likes']
        server = await get_server(ctx.guild.id)
        currency = await get_currency(ctx.guild.id)
        count = random.randint(server['work'][0], server['work'][1])
        count = int(int(count))+int(((likes*count)*0.1))
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': count}})
        emb = disnake.Embed()
        emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["salary"]}**Заработанные средства:** {task(count)} {currency}', inline=False, name='')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] + count)} {currency}', inline=False, name='')
        emb.color = INVISIBLE
        await ctx.send(embed=emb)
    
    @work.error
    async def work_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
            await send_error(ctx, f'Для того чтобы сходить на работу подождите: {retry_after}')
    
    @commands.command(name='ограбить')
    @commands.cooldown(1, 7200 * 1 * 1, commands.BucketType.member)
    async def crime(self, ctx: commands.Context):
        """
        **Ограбить пользователя**\n
        Пример использования: `!ограбить @User123`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        server = await get_server(ctx.guild.id)
        currency = await get_currency(ctx.guild.id)
        count = random.randint(server['crime'][0], server['crime'][1])
        chance = random.randint(0,100)
        if chance <= 50:
            reasons = [
                'Вас укусила собака',
                'Вас заметил сосед',
                'За вами приехала полиция',
                'Вас схватила полиция',
                'В доме хозяина была злая собака',
            ]
            emb = disnake.Embed()
            emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
            emb.description = 'К сожалению ограбление не удалось'
            emb.color = INVISIBLE
            await ctx.send(embed=emb)
            return
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': count}})
        emb = disnake.Embed()
        emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        emb.add_field(value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] + count)} {currency}', inline=False, name='')
        emb.color = INVISIBLE
        await ctx.send(embed=emb)
    
    @crime.error
    async def crime_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
            await send_error(ctx, f'Для того чтобы сходить на ограбление подождите: {retry_after}')
    
    @commands.command(name='казино', aliases=['ставка'])
    async def casino(self, ctx: commands.Context, iamount = None):
        """
        **Сыграть в казино**\n
        Пример использования: `!казино 100`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        currency = await get_currency(ctx.guild.id)
        if iamount is None:
            await send_error(ctx, 'Укажите сумму ставки')
            return
        amount = get_amount(iamount, user)
        if amount < 50:
            await send_error(ctx, f'Количество **денег для ставки в казино** должно быть больше **50**')
            return

        elif amount > user['balance']:
            await send_error(ctx, f'Для ставки нехватает: **{task(amount-user["balance"])} {currency}**')
            return

        chance = random.randint(0,100)

        if chance <= 77:
            x = 0
        elif 77 < chance <= 88:
            x = 2
        elif 70 < chance <= 99:
            x = 3
        else:
            x = 10
        
        if x in [2,3,10]:
            await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount*x}})
            emb = disnake.Embed()
            emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["win"]}**Вы выиграли:** {task(amount*x)} {currency}', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["ratio"]}**Коэффициент:** X{task(x)}', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] + amount*x)} {currency}', inline=False)
            emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/1107059277157376000/1109182631213531156/e1fcac3345d9276db6904b590474f894.gif')
            emb.color = disnake.Colour.green()
            await ctx.send(embed=emb)
        else:
            await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': -amount}})
            emb = disnake.Embed()
            emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["money_minus"]}**Вы проиграли:** -{task(amount)} {currency}', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["ratio"]}**Коэффициент:** X{task(x)}', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] - amount)} {currency}', inline=False)
            emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/1107059277157376000/1109182631213531156/e1fcac3345d9276db6904b590474f894.gif')
            emb.color = disnake.Colour.red()
            await ctx.send(embed=emb)
    
    @commands.command(name='монетка')
    async def coin(self, ctx: commands.Context, iamount = None):
        """
        **Подкинуть монетку**\n
        Пример использования: `!монетка 100`
        """
        currency = await get_currency(ctx.guild.id)
        user = await get_user(ctx.guild.id, ctx.author.id)
        if iamount is None:
            await send_error(ctx, 'Укажите сумму ставки')
            return
        amount = get_amount(iamount, user)
        
        if amount < 50:
            await send_error(ctx, f'Количество **денег для игры в монетку** должно быть больше **50**')
            return
        
        if user['balance'] < amount:
            await send_error(ctx, f'Для игры в монетку нехватает: **{task(amount-user["balance"])} {currency}**')
            return
        

        await db.users.update_one({"uid": ctx.author.id, "gid": ctx.guild.id},
                               {"$inc": {"balance": -amount}})

        emb_button = disnake.Embed().set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}',
                                                icon_url=ctx.author.display_avatar.url)
        emb_button.description = f'Выберите сторону монетки'
        emb_button.set_footer(text='Нажмите на кнопку выбранной стороны')
        emb_button.colour = INVISIBLE
        components = [
            disnake.ui.Button(label=f'Орёл🦅', style=disnake.ButtonStyle.primary, custom_id='eagle'),
            disnake.ui.Button(label=f'Решка💸', style=disnake.ButtonStyle.primary, custom_id='coin'),
        ]
        button_mes: disnake.Message = await ctx.send(embed=emb_button, components=components)
        try:
            button: disnake.MessageInteraction = await self.bot.wait_for(
                'button_click',
                check=lambda x: x.author == ctx.author,
                timeout=90.0)
        except asyncio.TimeoutError:
            await ctx.send('Время вышло!')
        await button_mes.delete()
        d = random.randint(0, 100)
        if d <= 32:
            s = button.component.custom_id
        else:
            if button.component.custom_id == "eagle":
                s = "coin"
            else:
                s = "eagle"
        if s == button.component.custom_id.lower():
            emb = disnake.Embed()
            emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["win"]}**Вы выиграли:** {task(amount)} {currency}', inline=False)
            if s == "coin":
                emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["cointoss"]}**Выпала:** Решка', inline=False)
            else:
                emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["cointoss"]}**Выпал:** Орёл', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["ratio"]}**Коэффициент:** X{task(2)}', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] + amount)} {currency}', inline=False)
            emb.color = disnake.Colour.green()
            if s == "coin":
                emb.set_image(
                    url="https://i.pinimg.com/originals/52/91/f5/5291f56897d748b1ca0a10c90023588d.gif")
            else:
                emb.set_image(
                    url="https://i.pinimg.com/originals/52/91/f5/5291f56897d748b1ca0a10c90023588d.gif")
            await db.users.update_one({"uid": ctx.author.id, "gid": ctx.guild.id},
                                   {"$inc": {"balance": amount * 2}})
            return await ctx.send(embed=emb)
        else:
            emb = disnake.Embed()
            emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["money_minus"]}**Вы проиграли:** -{task(amount)} {currency}', inline=False)
            if s == "coin":
                emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["cointoss"]}**Выпала:** Решка', inline=False)
            else:
                emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["cointoss"]}**Выпал:** Орёл', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["ratio"]}**Коэффициент:** X{task(0)}', inline=False)
            emb.add_field(name='', value=f'> {emoji_data["EMOJI"]["money"]}**Баланс:** {task(user["balance"] - amount)} {currency}', inline=False)
            emb.color = disnake.Colour.red()
            if s == "coin":
                emb.set_image(
                    url="https://i.pinimg.com/originals/52/91/f5/5291f56897d748b1ca0a10c90023588d.gif")
            else:
                emb.set_image(
                    url="https://i.pinimg.com/originals/52/91/f5/5291f56897d748b1ca0a10c90023588d.gif")
            await ctx.send(embed=emb)
    
    @commands.command(name='магазин', aliases=['шоп'])
    async def shop(self, ctx: commands.Context):
        """
        **Посмотреть магазин с ролями сервера**\n
        Пример использования: `!магазин`
        """
        currency = await get_currency(ctx.guild.id)
        items = []
        embeds = []
        x = 1
        embed = disnake.Embed(color=INVISIBLE, title=f'{emoji_data["EMOJI"]["shoppingcart"]}     МАГАЗИН РОЛЕЙ     {emoji_data["EMOJI"]["shoppingcart"]}').set_footer(
            text=f'{ctx.prefix}buy-role <Номер роли>\n{ctx.prefix}add-role <@Роль>(администратор)')
        async for _ in db.shop.find({'gid': ctx.guild.id}) \
                .sort([('price', pymongo.DESCENDING)]).limit(10):
            if _ not in items:
                items.append(_)
        for item in items:
            role = ctx.guild.get_role(item['rid'])
            if role:
                embed.add_field(name=f'Номер: **#{x}**',
                                value=f'**Роль: **{role.mention}\n**Цена:** {task(item["price"])} {currency}',
                                inline=False)
                if x % 10 == 0:
                    embeds.append(embed)
                    embed = disnake.Embed(color=0x303136, title=f'{emoji_data["EMOJI"]["shoppingcart"]}     МАГАЗИН РОЛЕЙ     {emoji_data["EMOJI"]["shoppingcart"]}').set_footer(
                        text=f'{ctx.prefix}buy-role <Номер роли>')
                x += 1
            else:
                await db.shop.delete_one({'gid': ctx.guild.id, 'rid': item['rid']})
        else:
            if x == 1:
                embed.add_field(name=f'Магазин ролей пуст', value=f'...', inline=False)
            embeds.append(embed)
        if embeds:
            try:
                await ctx.send(embed=embeds[0])
            except (Exception,):
                pass
        else:
            embed = disnake.Embed(description=f'Магазин ролей пуст...', color=0x303136)
            await ctx.send(embed=embed)

    @commands.command(name='купить-роль', aliases=['купить_роль', 'купить', 'buy-role', 'buy', 'buy_role'])
    async def buyrole(self, ctx: commands.Context, num: int):
        """
        **///**\n
        Пример использования: `!купить-роль 1(номер роли)`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        currency = await get_currency(ctx.guild.id)
        items = []
        x = 1
        async for _ in db.shop.find({'gid': ctx.guild.id}) \
                .sort([('price', pymongo.DESCENDING)]).limit(10):
            if _ not in items:
                items.append(_)
        for item in items:
            role = ctx.guild.get_role(item['rid'])
            if role:
                if num == x:
                    if role not in ctx.author.roles:
                        new_balance = user['balance'] - item['price']
                        if new_balance >= 0:
                            try:
                                await ctx.author.add_roles(role, reason='покупка через магазин')
                                await db.users.update_one(
                                    {'gid': ctx.guild.id, 'uid': ctx.author.id},
                                    {'$set': {'balance': new_balance}})
                                return await ctx.send(embed=disnake.Embed(
                                    description=f'Вы успешно купили роль {role.mention}',
                                    color=INVISIBLE))

                            except (Exception,) as err:
                                print(err)
                                await send_error(ctx, f'Боту **недостаточно разрешений** для выдачи роли')
                                return
                        else:
                            await send_error(ctx, f'Для покупки роли **нехватает**: **{task(item["price"]-user["balance"])} {currency}**')
                            return
                    else:
                        await send_error(ctx, f'У вас **уже есть** роль {role.mention}')
                        return
                x += 1
            else:
                await send_error(ctx, f'Данной роли не найдено в магазине ролей')
                return

    @commands.command(name='добавить-роль', aliases=['добавить', 'добавить_роль', 'add-role', 'add_role'])
    async def addrole(self, ctx: commands.Context, role = None, price = None):
        """
        **Добавить роль в магазин ролей(только администратор)**\n
        Пример использования: `!добавить-роль @role 100(цена)`
        """
        currency = await get_currency(ctx.guild.id)
        if role is None or price is None:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nПример: {ctx.prefix}addrole <@Роль> <цена(целое число)>')
            return
        try: role = ctx.guild.get_role(int(str(role).replace('<@&', '').replace('>', '')))
        except: pass
        if isinstance(role, disnake.Role) is False:
            await send_error(ctx, f'Проверте аргуменыты использованой команды!\nРоль должна быть упомянута\n<@Роль>')
            return
        try: price = int(price)
        except: pass
        if isinstance(price, int) is False:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nЦена роли должна быть целым числом')
            return
        if ctx.author.guild_permissions.administrator:
            if not await db.shop.find_one({'gid': ctx.guild.id, 'rid': role.id}):
                await db.shop.insert_one({'gid': ctx.guild.id, 'rid': role.id, 'price': price})
                await ctx.send(embed=disnake.Embed(
                    description=f'Роль {role.mention} добавлена в магазин ролей, за {task(price)} {currency}',
                    color=INVISIBLE))
            else:
                await send_error(ctx, f'Роль {role.mention} **уже есть** в магазине ролей')
                return
        else:
            await send_error(ctx, f'**Вам** не хватает прав для использования этой команды')
            return

    @commands.command(name='удалить-роль', aliases=['удалить', 'удалить_роль', 'del-role', 'del_role', 'delete_role'])
    async def delrole(self, ctx: commands.Context, role: disnake.Role):
        """
        **Удалить роль из магазина ролей(только администратор)**\n
        Пример использования: `!удалить-роль @role`
        """
        if role is None:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nПример: {ctx.prefix}deleterole <@Роль>')
        elif isinstance(role, disnake.Role) is False:
            await send_error(ctx, f'Проверте аргуменыты использованой команды!\nРоль должна быть упомянута\n<@Роль>')
        if ctx.author.guild_permissions.administrator:
            if await db.shop.find_one({'gid': ctx.guild.id, 'rid': role.id}):
                await db.shop.delete_one({'rid': role.id})
                await ctx.send(
                    embed=disnake.Embed(description=f'Роль {role.mention} удалена из магазин ролей',
                                        color=INVISIBLE))
            else:
                await send_error(ctx, f'Роли {role.mention} **ещё нет* в магазине ролей')
                return
        else:
            await send_error(ctx, f'**Вам** не хватает прав для использования этой команды')
            return

    @commands.command(name='продать-роль', aliases=['продать', 'продать_роль', 'sell-role', 'sell_role', 'sell'])
    async def sellrole(self, ctx: commands.Context, num = None):
        """
        **Продать роль**\n
        Пример использования: `!продать-роль 1(номер роли)`
        """
        currency = await get_currency(ctx.guild.id)
        if num is None:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nПример: {ctx.prefix}sellrole <Номер(целое число)>')
            return
        try: num = int(num)
        except: pass
        if isinstance(num, int) is False:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nНомер продаваемой роли должен быть целым числом')
            return
        items = []
        async for _ in db.shop.find({'gid': ctx.guild.id}) \
                .sort([('price', pymongo.DESCENDING)]).limit(10):
            if _ not in items:
                items.append(_)
        try:
            role = ctx.guild.get_role(items[num - 1]['rid'])
        except (Exception,):
            await send_error(ctx, f'Данной роли либо **не существует**, либо она **не добавлена** в магазин')
            return
        if role in ctx.author.roles:
            role_db = items[num - 1]
            if role_db:
                await ctx.author.remove_roles(role)
                user = await get_user(ctx.guild.id, ctx.author.id)
                role_price = round(role_db['price'] / 2)
                await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                                       {'$inc': {'balance': role_price}})
                await ctx.send(embed=disnake.Embed(
                    description=f'Вы успешно продали роль {role.mention} за {task(role_price)} {currency}!',
                    color=0x303136))
            else:
                await send_error(ctx, f'Данной роли нету в магазине на этом сервере')
                return
        else:
            await send_error(ctx, f'У вас нет данной роли')
            return

    @commands.command(name='выдать-валюту', aliases=['выдать'])
    async def give(self, ctx: commands.Context, member: disnake.Member, amount: int):
        """
        **Выдать валюту пользователю (только администратор)**\n
        Пример использования: `!выдать-валюту @User123 100`
        """
        if ctx.author.guild_permissions.administrator or ctx.author.id in data['BOT']['owner_ids']:
            currency = await get_currency(ctx.guild.id)
            member = await ctx.guild.fetch_member(member.id)
            if member is None:
                await send_error(ctx, f'Данного пользователя нет на этом сервере'); return
            if amount < 1:
                await send_error(ctx, f'Минимальная сумма выдачи денег пользователю 1 {currency}')
                return
            await db.users.update_one({'gid': ctx.guild.id, 'uid': member.id}, {'$inc': {'balance': amount}})
            embed=disnake.Embed(
                description=f'Администратор: {ctx.author.mention}\nВыданые средства: {task(amount)}{currency}\nПользователь: {member.mention}',
                color=INVISIBLE)
            embed.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
            message = await ctx.send(embed=embed)
            await send_money_log(self, ctx, embed=embed)
            await message.add_reaction(f'✅')            
        else:
            await send_error(ctx, 'У вас нет прав для использования этой команды!')
            return

    @commands.command(name='забрать-валюту', aliases=['снять'])
    async def take(self, ctx: commands.Context, member, amount: int):
        """
        **Забрать валюту у пользователя(только администратор)**\n
        Пример использования: `!забрать-валюту @User123 100`
        """
        currency = await get_currency(ctx.guild.id)
        if ctx.author.guild_permissions.administrator or ctx.author.id in data['BOT']['owner_ids']:
            member = ctx.guild.get_member(int(str(member).replace('<@', '').replace('>', '')))
            if member is None:
                await send_error(ctx, f'Данного пользователя нет на этом сервере'); return
            user = await get_user(ctx.guild.id, member.id)
            if user['balance'] >= amount:
                await db.users.update_one({'gid': ctx.guild.id, 'uid': member.id}, {'$inc': {'balance': -amount}})
                embed=disnake.Embed(
                description=f'Администратор: {ctx.author.mention}\nЗабранные средства: {task(amount)}{currency}\nПользователь: {member.mention}',
                color=INVISIBLE)
                embed.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
                message = await ctx.send(embed=embed)  
                await message.add_reaction(f'✅')
            else:
                await send_error(ctx, f'У пользователя нехватает {member.mention} {task(amount-user["balance"])}{currency}')
                return
        else:
            await send_error(ctx, 'У вас нет прав для использования этой команды!')
            return
    
    @commands.command(name='сброс-экономики', aliases=['сброс'])
    async def reset(self, ctx: commands.Context):
        """
        **Сброс экономики на сервере**\n
        Пример использования: `!сброс-экономики`
        """
        if ctx.author.guild_permissions.administrator:
            server = await db.guilds.find_one({"gid": ctx.guild.id})
            await db.users.update_many({'gid': ctx.guild.id}, {'$set': {
                'balance': server['initial_balance'],
                'bank': 0,
                'cases': 0,
                'subs': 0,
            }}
                              )
            message = await ctx.send(embed=disnake.Embed(
                description=f'**Средства всех участников были успешно сброшены**',
                color=0x303136))
            await message.add_reaction(f'✅')
        else:
            await send_error(ctx, 'У вас нет прав для использования этой команды')
            return

    @commands.command(name='собрать-прибыль', aliases=['колект', 'коллект', 'собирать', 'собрать'])
    @commands.cooldown(1, 3600 * 2 * 1, commands.BucketType.member)
    async def collect(self, ctx: commands.Context):
        """
        **Собрать прибыль с купленых в магазине ролей**\n
        Пример использования: `!собрать-прибыль`
        """
        currency = await get_currency(ctx.guild.id)
        items = []
        x = 1
        amount = 0
        user = await db.users.find_one({'gid': ctx.guild.id, 'uid': ctx.author.id})
        embed = disnake.Embed(color=0x303136,
                              title=f'{emoji_data["EMOJI"]["success"]} Доход с ролей получен!') \
            .set_footer(
            text='Ansero | Коллект', icon_url=self.bot.user.display_avatar).set_author(
            name=f'{ctx.author.display_name} | Коллект',
            icon_url=ctx.author.display_avatar)
        async for _ in db.shop.find({'gid': ctx.guild.id}) \
                .sort([('price', pymongo.DESCENDING)]).limit(10):
            if _ not in items:
                items.append(_)
        for item in items:
            role = ctx.guild.get_role(item['rid'])
            if role:
                if role in ctx.author.roles:
                    embed.add_field(name=f'',
                                    value=f'**`{x}` - {role.mention} | {task(int(item["price"] / 100))} {currency}**',
                                    inline=False)
                    try:
                        amount += int(item['price'] / 100)
                    except(Exception,):
                        amount += 1
                else:
                    pass
            else:
                await db.shop.delete_one({'gid': ctx.guild.id, 'rid': item['rid']})
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id},
                               {'$set': {'balance': int(user['balance'] + amount)}})
        embed.add_field(name=f'',
                        value=f'{emoji_data["EMOJI"]["creditcard1"]}`Всего собрано`: **{amount:,}** {currency}',
                        inline=False)
        await ctx.send(embed=embed)

    @collect.error
    async def collect_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
            await ctx.send(embed=disnake.Embed(color=disnake.Colour.red(), title="Error!",
                                               description=f'**Коллект будет доступен через: '
                                                           f'{retry_after}**'))
    
    @commands.command(name='краш')
    async def crash(self, ctx: commands.Context, iamount = None):
        """
        **Сыграть в краш**\n
        Пример использования: `!краш 100`
        """
        user = await get_user(ctx.guild.id, ctx.author.id)
        currency = await get_currency(ctx.guild.id)
        if iamount is None:
            await send_error(ctx, 'Укажите сумму ставки')
            return
        amount = get_amount(iamount, user)
        if int(amount) <= 0:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nСтавка должна быть целым числом')
            return
        if amount > user['balance']:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nНедостаточно средств!')
            return
        if user['active games']['crash'] is True:
            await send_error(ctx, 'Завершите прошлую игру, для начала сдедующей')
            return
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': -amount}})
        await start_game(user, 'crash')
        xchance = random.randint(0, 100)
        if xchance < 50:
            chance = random.randint(0, 4)
        elif xchance >= 50 and xchance < 75:
            chance = random.randint(0, 9)
        elif xchance >= 80 and xchance < 95:
            chance = random.randint(2, 10)
        elif xchance >= 95 and xchance < 99:
            chance = random.randint(10, 100)
        else:
            chance = 0
        fchance = 0
        emb = disnake.Embed(color=INVISIBLE)
        emb.set_author(name=f'{ctx.author} | Crash', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
        message = await ctx.send(embed=emb)
        while True:
            if fchance != chance:
                await message.edit(embed = disnake.Embed(description=f'''
> {emoji_data["EMOJI"]["crash"]}Коэффициент: {fchance}X
> {emoji_data["EMOJI"]["money_crash"]}Вы получите: {amount*fchance}
                ''', colour=disnake.Colour.blue(), title='Идет игра').set_image(url='https://i.gifer.com/StHR.gif'),
                components=[disnake.ui.Button(style=disnake.ButtonStyle.green, label=f'Забрать {amount*fchance}',
                emoji=f'✅', custom_id='stop')])
                try:
                    button_clicked: disnake.MessageInteraction = await self.bot.wait_for('button_click', check=lambda b: b.user == ctx.author, timeout=1.5)
                    if button_clicked.component.custom_id == f'stop':
                        await message.edit(embed = disnake.Embed(description=f'''
> {emoji_data["EMOJI"]["crash"]}Коэффициент: {fchance}X
> {emoji_data["EMOJI"]["money_crash"]}Вы получили: {amount*fchance} {currency}
> {emoji_data["EMOJI"]["money"]}Баланс: {task(user["balance"] + (amount*fchance) - amount)} {currency}
> {emoji_data["EMOJI"]["ratio"]}Конечный коэффициент: {chance}X
                                ''', colour=disnake.Colour.green(), title='Вы выиграли').set_image(url='https://i.gifer.com/StHR.gif'),
                                components=[disnake.ui.Button(style=disnake.ButtonStyle.primary, label=f'Вы забрали {amount*fchance}',
                                                                                                    emoji=f'✅', disabled=True)])
                        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount*fchance}})
                        await end_game(user, 'crash')
                        break
                except asyncio.TimeoutError:
                    await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount}})
                    await ctx.send(f'{ctx.author.mention} время вышло, сумма ставки возвращена на баланс')
                    await end_game(user, 'black_jack')
            else:
                await message.edit(embed = disnake.Embed(description=f'''
> {emoji_data["EMOJI"]["crash_minus"]}Коэффициент: {fchance}X
> {emoji_data["EMOJI"]["money_minus"]}Вы проиграли: {amount} {currency}
> {emoji_data["EMOJI"]["money"]}Баланс: {task(user["balance"] - amount)} {currency}
                ''', colour=disnake.Colour.red(), title='Вы проиграли'), components=None)
                await end_game(user, 'crash')
                break
            fchance += 1

    
    
    @commands.command(name='блекджек', aliases=['bj', 'бж', 'блэкжек'])
    async def blackjack(self, ctx: commands.Context, iamount = None):
        """
        **Сыграть в блекджек**\n
        Пример использования: `!блекджек 100`
        """
        if iamount is None:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nПример: {ctx.prefix}crash <сумма(целое число)>')
            return
        user = await get_user(ctx.guild.id, ctx.author.id)
        amount = get_amount(iamount, user)
        if int(amount) <= 0:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nСтавка должна быть целым числом')
            return
        if amount > user['balance']:
            await send_error(ctx, f'Проверьте аргуменыты использованой команды!\nНедостаточно средств!')
            return
        if user['active games']['black_jack'] is True:
            await send_error(ctx, 'Завершите прошлую игру, для начала сдедующей')
            return
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': -amount}})
        await start_game(user, 'black_jack')
        deck = [6,7,8,9,10,2,3,4,11] * 4
        random.shuffle(deck)
        player_cards = [deck.pop(), deck.pop()]
        dealer_cards = [deck.pop(), deck.pop()]
        dbuttons = [
            disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Hit", disabled=True),
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="Stand", disabled=True),
        ]
        if sum(player_cards) == 21:
            embed = disnake.Embed(title="Blackjack!")
            embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
            embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
            embed.description = f'Результат: Вы выиграли\n+{amount}'
            embed.colour = disnake.Colour.green()
            embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            await ctx.send(embed=embed, components=dbuttons)
            await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount*2}})
            await end_game(user, 'black_jack')
            return

        # Check if the dealer has blackjack
        if sum(dealer_cards) == 21:
            embed = disnake.Embed(title="Dealer has blackjack!")
            embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
            embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
            embed.description = f'Результат: Вы проиграли\n-{amount}'
            embed.colour = disnake.Colour.red()
            embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            await ctx.send(embed=embed, components=dbuttons)
            await end_game(user, 'black_jack')
            return
        buttons = [
            disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Hit"),
            disnake.ui.Button(style=disnake.ButtonStyle.secondary, label="Stand"),
        ]
        embed = disnake.Embed(title="Blackjack")
        embed.add_field(name="Ваша рука", value=f"{sum(player_cards)}")
        embed.add_field(name="Рука диллера", value=f"{sum(dealer_cards)}")
        embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
        embed.colour = disnake.Colour.blue()
        message = await ctx.send(embed=embed, components=buttons)
        # Start the player's turn
        while True:
            choice = await self.bot.wait_for('button_click', check=lambda x: x.author == ctx.author, timeout=180.0)
            try:
                if choice.component.label == "Hit":
                    # Deal the player another card
                    player_cards.append(deck.pop())

                    # Check if the player has busted
                    if sum(player_cards) > 21:
                        embed = disnake.Embed(title="Blackjack")
                        embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
                        embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
                        embed.description = f'Результат: Перебор\n-{amount}'
                        embed.colour = disnake.Colour.red()
                        embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
                        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                        await message.edit(embed=embed, components=dbuttons)
                        await end_game(user, 'black_jack')
                    elif sum(player_cards) == 21:
                        embed = disnake.Embed(title="Blackjack")
                        embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
                        embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
                        embed.description = f'Результат: Вы выиграли\n+{amount}'
                        embed.colour = disnake.Colour.green()
                        embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
                        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                        await message.edit(embed=embed, components=dbuttons)
                        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount*2}})
                        await end_game(user, 'black_jack')
                        return
                    else:
                        embed = disnake.Embed(title="Blackjack")
                        embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
                        embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
                        embed.colour = disnake.Colour.blue()
                        embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
                        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
                        await message.edit(embed=embed)

                elif choice.component.label == "Stand":
                    break
            except asyncio.TimeoutError:
                await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount}})
                await ctx.send(f'{ctx.author.mention} время вышло, сумма ставки возвращена на баланс')
                await end_game(user, 'black_jack')

        # Start the dealer's turn
        while sum(dealer_cards) < 17:
            dealer_cards.append(deck.pop())

        # Compare the player's hand to the dealer's hand
        if sum(player_cards) > sum(dealer_cards) or sum(dealer_cards)>21:
            embed = disnake.Embed(title="Blackjack")
            embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
            embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
            embed.description = f'Результат: Вы выиграли\n+{amount}'
            embed.colour = disnake.Colour.green()
            embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            await message.edit(embed=embed, components=dbuttons)
            await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount*2}})
            await end_game(user, 'black_jack')
        elif sum(player_cards) < sum(dealer_cards) and sum(dealer_cards)<=21:
            embed = disnake.Embed(title="Blackjack")
            embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
            embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
            embed.description = f'Результат: Вы проиграли\n-{amount}'
            embed.colour = disnake.Colour.red()
            embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            await message.edit(embed=embed, components=dbuttons)
            await end_game(user, 'black_jack')
        else:
            embed = disnake.Embed(title="Blackjack")
            embed.add_field(name="Ваша рука:", value=f"{sum(player_cards)}")
            embed.add_field(name="Рука диллера:", value=f"{sum(dealer_cards)}")
            embed.description = f'Результат: Ничья\nСумма ставки возвращена на баланс'
            embed.colour = disnake.Colour.yellow()
            embed.set_thumbnail(url='https://thumbs.gfycat.com/AromaticIncompleteBetafish-size_restricted.gif')
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            await message.edit(embed=embed, components=dbuttons)
            await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': amount}})
            await end_game(user, 'black_jack')

    
        
def setup(bot: commands.Bot):
    bot.add_cog(Economy(bot))  