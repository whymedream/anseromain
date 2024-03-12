import disnake
from asyncio import sleep
from disnake.ext import commands
from bot.mongodb import db
from disnake.utils import get
import asyncio


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='настройки', aliases=["настроить", "set"])
    async def settings(self, ctx: commands.Context):
        """
        **Настройка функционала бота**\n
        Пример использования: `!настройки`
        """
        if ctx.author.guild_permissions.manage_guild:
            embed = disnake.Embed(title="Настройка Ansero", color=0x2b2d31)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
            components = [
                disnake.ui.Button(label="Настройка", style=disnake.ButtonStyle.primary, custom_id=f'set_{ctx.guild.id}'),
                disnake.ui.Button(label="Текущие настройки", style=disnake.ButtonStyle.green, custom_id=f'curset_{ctx.guild.id}'),
                disnake.ui.Button(label="Отмена", style=disnake.ButtonStyle.danger, custom_id=f'cancel_{ctx.guild.id}')
            ]
            await ctx.send(embed=embed, components=components)
        else: await ctx.send("У вас нет разрешения на использование данной команды.")
    
    @commands.Cog.listener()
    async def on_button_click(self, ctx: disnake.MessageInteraction):
        await ctx.response.defer()
        if ctx.user.guild_permissions.manage_guild:
            if ctx.component.custom_id == f'cancel_{ctx.guild.id}':
                await ctx.send("Отменено", delete_after=5)
                await sleep(3)
                await ctx.message.delete()
                return
            elif ctx.component.custom_id == f'curset_{ctx.guild.id}':
                embed = disnake.Embed(title="Текущие настройки Ansero", color=0x2b2d31)
                embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                server = await db.guilds.find_one({"gid": ctx.guild.id})
                embed.add_field(name="", value=f'**Префикс: `{server["prefix"]}`**', inline=False)
                embed.add_field(name="", value=f'**Работа: `{server["work"][0]} - {server["work"][1]}`**', inline=False)
                embed.add_field(name="", value=f'**Бонус: `{server["bonus"][0]} - {server["bonus"][1]}`**', inline=False)
                embed.add_field(name="", value=f'**Ограбление: `{server["crime"][0]} - {server["crime"][1]}`**', inline=False)
                embed.add_field(name="", value=f'**Начальный баланс: `{server["crime"][0]} - {server["crime"][1]}`**', inline=False)
                components = [
                    disnake.ui.Button(label="Настройка", style=disnake.ButtonStyle.primary, custom_id=f'set_{ctx.guild.id}'),
                    disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.danger, custom_id=f'back_{ctx.guild.id}')
                ]
                await ctx.edit_original_message(embed=embed, components=components)
            elif ctx.component.custom_id == f'set_{ctx.guild.id}':
                embed = disnake.Embed(title="Настройка Ansero", color=0x2b2d31)
                embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                components =[
                [
                    disnake.ui.Select(
                        custom_id='selectoption',
                        placeholder="Выберите меню для настройки Ansero",
                        options=[
                            disnake.SelectOption(label="Настройка префикса", value="prefix"),
                            disnake.SelectOption(label="Настройка работы", value="work"),
                            disnake.SelectOption(label="Настройка бонуса", value="bonus"),
                            disnake.SelectOption(label="Настройка ограбления", value="crime"),
                            disnake.SelectOption(label="Настройка начального баланса", value="initbal"),
                            disnake.SelectOption(label="Настройка модерации", value="moderation"),
                            disnake.SelectOption(label="Аудит", value="audit"),
                        ]
                    )
                ],
                [
                    disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.danger, custom_id=f'back_{ctx.guild.id}'),
                ]
                ]
                await ctx.message.edit(embed=embed, components=components)
            elif ctx.component.custom_id == f'back_{ctx.guild.id}':
                await self.settings(ctx)
            elif ctx.component.custom_id == f'on_{ctx.guild.id}':
                await db.guilds.update_one({"gid": ctx.guild.id}, {"$set":{'audit': True}})
                category = await ctx.guild.create_category('Аудит')
                money_channel = await ctx.guild.create_text_channel('Денежный', category = category)
                voice_channel = await ctx.guild.create_text_channel('Голосовой', category = category)
                roles_channel = await ctx.guild.create_text_channel('Роли', category = category)
                text_channel = await ctx.guild.create_text_channel('Текстовый', category = category)
                await db.guilds_audit.update_one({"gid": ctx.guild.id}, {"$set":{
                    'money_audit_chn': money_channel.id,
                    "voice_audit_chn": voice_channel.id,
                    "roles_audit_chn": roles_channel.id,
                    "text_channel_audit_chn": text_channel.id,
                    }})
                emb = disnake.Embed()
                emb.title = 'Настройка Ansero | Аудит - Включено'
                emb.description = f'''
Вы успешно включили аудит на вашем дискорд сервере
Созданые каналы:
{money_channel.mention}
{voice_channel.mention}
{roles_channel.mention}
{text_channel.mention}
'''
                emb.add_field(name='Внимание!', value='Название каналов вы можете поменять под себя.\nЭто действие никак не повлияет на работоспособность аудита.')
                emb.color = 0x2b2d31
                await ctx.message.edit(
                    embed=emb,
                    components=None
                )

            elif ctx.component.custom_id == f'off_{ctx.guild.id}':
                await db.guilds.update_one({"gid": ctx.guild.id}, {"$set":{'audit': False}})
                await db.guilds.update_one({"gid": ctx.guild.id}, {"$set":{
                    "money_audit_chn": None,
                    "voice_audit_chn": None,
                    "roles_audit_chn": None,
                    "text_channel_audit_chn": None,
                }})
                try:
                    category = get(ctx.guild.categories, name="Аудит")
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()
                except:
                    await ctx.send(embed=disnake.Embed(
                    title="Внимание!",
                    description='''
Боту неудалось автоматически удалисть каналы и котегорию аудита.\nВы можете сделать это врочуную.  
'''
                    ))
                emb = disnake.Embed()
                emb.title = 'Настройка Ansero | Аудит - Выключено'
                emb.description = 'Вы успешно выключили аудит на вашем дискорд сервере'
                emb.color = 0x2b2d31
                await ctx.message.edit(
                    embed=emb,
                    components=None
                )
            elif ctx.component.custom_id == f'offmod_{ctx.guild.id}':
                await db.guilds.update_one({"gid": ctx.guild.id}, {"$set":{'moderation': False}})
                emb = disnake.Embed()
                emb.title = 'Настройка Ansero | Модерация - Выключено'
                emb.description = 'Вы успешно выключили аудит на вашем дискорд сервере'
                emb.color = 0x2b2d31
                await ctx.message.edit(
                    embed=emb,
                    components=None
                )
            elif ctx.component.custom_id == f'onmod_{ctx.guild.id}':
                await db.guilds.update_one({"gid": ctx.guild.id}, {"$set":{'moderation': True}})
                emb = disnake.Embed()
                emb.title = 'Настройка Ansero | Модерация - Включено'
                emb.description = 'Вы успешно выключили аудит на вашем дискорд сервере'
                emb.color = 0x2b2d31
                await ctx.message.edit(
                    embed=emb,
                    components=None
                )
    
    @commands.Cog.listener()
    async def on_dropdown(self, ctx: disnake.MessageInteraction):
        value = ctx.values[0]
        if 'prefix' in value:
            modal = disnake.ui.Modal(title="Введите новый префикс", components=[disnake.ui.TextInput(label="Префикс", min_length=1, max_length=4, custom_id="pref")])
            await ctx.response.send_modal(modal)
        if 'work' in value:
            modal = disnake.ui.Modal(title="Введите мин./макс. кол-во денег за работу", components=[
                disnake.ui.TextInput(label="Минимум", min_length=1, max_length=40, custom_id="work_min"),
                disnake.ui.TextInput(label="Максимум", min_length=1, max_length=40, custom_id="work_max"),
                ])
            await ctx.response.send_modal(modal)
        if 'bonus' in value:
            modal = disnake.ui.Modal(title="Введите мин./макс. кол-во денег за бонус", components=[
                disnake.ui.TextInput(label="Минимум", min_length=1, max_length=40, custom_id="bonus_min"),
                disnake.ui.TextInput(label="Максимум", min_length=1, max_length=40, custom_id="bonus_max"),
                ])
            await ctx.response.send_modal(modal)
        if 'crime' in value:
            modal = disnake.ui.Modal(title="Введите мин./макс. кол-во денег за ограбление", components=[
                disnake.ui.TextInput(label="Минимум", min_length=1, max_length=40, custom_id="crime_min"),
                disnake.ui.TextInput(label="Максимум", min_length=1, max_length=40, custom_id="crime_max"),
                ])
            await ctx.response.send_modal(modal)
        if 'initbal' in value:
            modal = disnake.ui.Modal(title="Введите новый начальный баланс", components=[disnake.ui.TextInput(label="Начальный баланс", min_length=1, max_length=40,
                                                                                                            custom_id="initbal")])
            await ctx.response.send_modal(modal)
        if 'moderation' in value:
            guild = await db.guilds.find_one({'gid': ctx.guild.id})
            emb = disnake.Embed(color=0x2b2d31)
            emb.title = 'Настройка Ansero | Модерация'
            emb.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
            emb.set_footer(text='Нажимай на кнопки чтобы включить/выключить команды модерации на сервере')
            if guild['moderation'] is True:
                components = [
                    [disnake.ui.Button(label='Выключить модерацию', style=disnake.ButtonStyle.danger, custom_id=f'offmod_{ctx.guild.id}')],
                    [disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.danger, custom_id=f'back_{ctx.guild.id}')]
                ]
            else:
                components = [
                    [disnake.ui.Button(label='Включить модерацию', style=disnake.ButtonStyle.danger, custom_id=f'onmod_{ctx.guild.id}')],
                    [disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.danger, custom_id=f'back_{ctx.guild.id}')]
                ]
            await ctx.message.edit(embed=emb, components=components)
            await ctx.response.defer()

        if 'audit' in value:
            guild = await db.guilds.find_one({'gid': ctx.guild.id})
            if guild['audit'] is False:
                components=[[
                    disnake.ui.Button(label="Включить", style=disnake.ButtonStyle.green, custom_id=f'on_{ctx.guild.id}'),
                ],
                    disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.danger, custom_id=f'back_{ctx.guild.id}'),
                ]
            else:
                components=[[
                    disnake.ui.Button(label="Выключить", style=disnake.ButtonStyle.red, custom_id=f'off_{ctx.guild.id}'),
                ],
                    disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.danger, custom_id=f'back_{ctx.guild.id}'),
                ]
            await ctx.message.edit(
                embed=disnake.Embed(title="Настройка Ansero | Аудит", color=0x2b2d31),
                components=components)
            await ctx.response.defer()
        
    
    
    @commands.Cog.listener()
    async def on_modal_submit(self, ctx: disnake.ModalInteraction):
        await ctx.response.defer()
        if ctx.data.components[0]["components"][0]["custom_id"] == 'pref':
            await db.guilds.update_one({"gid": ctx.guild.id}, {"$set": {"prefix": ctx.data.components[0]["components"][0]["value"]}})
            await ctx.edit_original_message(f'Новый префикс: `{ctx.data.components[0]["components"][0]["value"]}`')
            await sleep(3)
            await ctx.message.delete()
        if ctx.data.components[0]["components"][0]["custom_id"] == 'work_min':
            try:
                if int(ctx.data.components[0]["components"][0]["value"]) and int(ctx.data.components[1]["components"][0]["value"]):
                    await db.guilds.update_one({"gid": ctx.guild.id}, {"$set": {"work": 
                                                                                [
                                                                                    int(ctx.data.components[0]["components"][0]["value"]),
                                                                                    int(ctx.data.components[1]["components"][0]["value"])
                                                                                ]}})
                    await ctx.edit_original_message(f'Минимальное и максимальное количество денег получаемых за работу было изменено на:'\
                                                    f'`{ctx.data.components[0]["components"][0]["value"]}`-`{ctx.data.components[1]["components"][0]["value"]}`')
                    await ctx.message.delete()
            except:
                await ctx.send("Введите минимальное и максимальное количество денег за работу в **числовом формате**", delete_after=5.0)
                await ctx.message.delete()
        if ctx.data.components[0]["components"][0]["custom_id"] == 'bonus_min':
            try:
                if int(ctx.data.components[0]["components"][0]["value"]) and int(ctx.data.components[1]["components"][0]["value"]):
                    await db.guilds.update_one({"gid": ctx.guild.id}, {"$set": {"bonus": 
                                                                                [
                                                                                    int(ctx.data.components[0]["components"][0]["value"]),
                                                                                    int(ctx.data.components[1]["components"][0]["value"])
                                                                                ]}})
                    await ctx.edit_original_message(f'Минимальное и максимальное количество денег получаемых за бонус было изменено на:'\
                                                    f'`{ctx.data.components[0]["components"][0]["value"]}`-`{ctx.data.components[1]["components"][0]["value"]}`')
                    await ctx.message.delete()
            except:
                await ctx.send("Введите минимальное и максимальное количество денег за бонус в **числовом формате**", delete_after=5.0)
                await ctx.message.delete()
        
        if ctx.data.components[0]["components"][0]["custom_id"] == 'crime_min':
            try:
                if int(ctx.data.components[0]["components"][0]["value"]) and int(ctx.data.components[1]["components"][0]["value"]):
                    await db.guilds.update_one({"gid": ctx.guild.id}, {"$set": {"crime": 
                                                                                [
                                                                                    int(ctx.data.components[0]["components"][0]["value"]),
                                                                                    int(ctx.data.components[1]["components"][0]["value"])
                                                                                ]}})
                    await ctx.edit_original_message(f'Минимальное и максимальное количество денег получаемых за ограбление было изменено на:'\
                                                    f'`{ctx.data.components[0]["components"][0]["value"]}`-`{ctx.data.components[1]["components"][0]["value"]}`')
                    await ctx.message.delete()
            except:
                await ctx.send("Введите минимальное и максимальное количество денег за ограбление в **числовом формате**", delete_after=5.0)
                await ctx.message.delete()
        
        if ctx.data.components[0]["components"][0]["custom_id"] == 'initbal':
            await db.guilds.update_one({"gid": ctx.guild.id}, {"$set": {"initial_balance": ctx.data.components[0]["components"][0]["value"]}})
            await ctx.edit_original_message(f'начальный баланс был изменён на: `{ctx.data.components[0]["components"][0]["value"]}`')
            await sleep(3)
            await ctx.message.delete()
        
    

def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))