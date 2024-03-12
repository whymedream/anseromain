import disnake
from disnake.ext import commands
from bot.functions import send_error, get_amount
from AaioAPI import AsyncAaioAPI
import uuid
import asyncio
from bot.mongodb import *

class Donate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.AaioClient = AsyncAaioAPI(
            'MjgyMGEyMmYtMWRiNS00MWU5LTkzMGQtYTFkMDhjZDAwMzA2OlNlbXRpMHBweCY5KXYlWU54JE1BR0tjJEcjQTBAJCow',
            'd3e9fa961d30eccbc7881a0c2c73e7f9',
            '391b1447-91f1-4d69-9a26-aa029a546d46'
            )
    
    @commands.command(name='донат', aliases = ['задонатить'])
    async def donate(self, ctx: commands.Context, amount = None):
        """
        **Покупка виртуальной валюты**\n
        Пример использования: `!донат 100`
        """
        if amount is None:
            await send_error(ctx, f'**Вы** не указали сумму доната')
            return
        try: amount = int(amount)
        except: await send_error(ctx, f'**Сумма** доната **должна быть** целым **числом**'); return
        if int(amount) < 100:
            await send_error(ctx, f'**Сумма** доната **не может быть** менее **100** рублей')
            return
        if int(amount):
            order_id=uuid.uuid4()
            aaurl = await self.AaioClient.create_payment(
                order_id=order_id, 
                amount=amount, 
                lang='ru', 
                currency='RUB', 
                description='Покупка игровой валюты'
                )
            emb = disnake.Embed()
            emb.title = 'Счет ожидает оплаты'
            emb.description = f'''
Для получения игровой валюты **нажмите на кнопку ниже** для оплаты счета, 
после оплаты **бот атоматически проверит статус счета**, 
и в случае **успешной оплаты игровая валюта зачислится на ваш баланс на сервере {ctx.guild.name}**
'''
            emb.add_field(name='Сумма платежа:', value=amount)
            emb.add_field(name='Кол-во покупаемой валюты:', value=f'{(amount*10000):,}')
            components = [
                disnake.ui.Button(label='Оплатить', url=aaurl)
            ]
            message = await ctx.author.send(embed=emb, components=components)
            while True:
                if await self.AaioClient.is_expired(order_id):
                    embexp = disnake.Embed()
                    embexp.add_field(name='Сумма платежа:', value=amount)
                    embexp.add_field(name='Кол-во покупаемой валюты:', value=f'{(amount*10000):,}')
                    components = [
                        disnake.ui.Button(label='Счет просрочен', disabled=True, style=disnake.ButtonStyle.danger)
                    ]
                    await message.edit(embed=embexp)
                    break
                elif await self.AaioClient.is_success(order_id):
                    embsuc = disnake.Embed()
                    embsuc.title = 'Счет оплачен'
                    embsuc.add_field(name='Сумма платежа:', value=amount)
                    embsuc.add_field(name='Кол-во покупаемой валюты:', value=f'{(amount*10000):,}')
                    components = [
                        disnake.ui.Button(label='Успешно', disabled=True, style=disnake.ButtonStyle.success)
                    ]
                    await message.edit(embed=embsuc)
                    await db.users.update_one({'gid': ctx.guild.id, 'uid':ctx.author.id}, {'$inc': {'balance': amount*10000}})
                    break
                else:
                    pass
                await asyncio.sleep(5)


def setup(bot: commands.Bot):
    bot.add_cog(Donate(bot))