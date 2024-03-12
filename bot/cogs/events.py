import disnake
from bot.mongodb import *
from disnake.ext import commands
import datetime
from asyncio import sleep
from random import randint
from bot.mongodb import get_prefix, db
INVISIBLE = 0x2b2d31

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        with open('bot/config.json', 'r') as f:
            data = json.load(f)
        print('--------------------------------------')
        print(f'{self.bot.user} has connected to Discord!')
        print('BOT INFO:')
        print(f' Username: {self.bot.user.name}')
        print(f' ID: {self.bot.user.id}')
        print(f' Version: {data["BOT"]["version"]}')
        print('--------------------------------------')
        while True:
            await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"{len(self.bot.guilds)} серверов!"))
            await sleep(10)
            await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"!help"))
            await sleep(10)
            await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"!settings"))
    
    @commands.Cog.listener('on_message')
    async def on_message_l(self, message: disnake.Message):
        if message.author == self.bot.user or message.author.bot:
            return
        await db.users.update_one({'gid': message.guild.id, 'uid': message.author.id}, {'$inc': {'messages': 1}})
    
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        chance = randint(0, 100)
        await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'commands_done': 1}})
        if chance >= 96:
            count = randint(100, 1000)
            currency = await get_currency(ctx.guild.id)
            await db.users.update_one({'gid': ctx.guild.id, 'uid': ctx.author.id}, {'$inc': {'balance': count}})
            await ctx.channel.send(f'{ctx.author.mention}\nЗа активное использование бота **Ansero** вы получили вознаграждение: {count}{currency}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        emb = disnake.Embed()
        emb.set_author(name=f'{guild.name}')
        emb.set_footer(text=f'ID: {guild.id}')
        emb.add_field(name='Создатель', value=f'{guild.owner} | {guild.owner.id}', inline=False)
        emb.add_field(name='Создан', value=f'{guild.created_at.strftime("%d.%m.%Y %H:%M:%S")}', inline=False)
        emb.add_field(name='Владелец', value=f'{guild.owner}', inline=False)
        emb.add_field(name='Количество участников', value=f'{guild.member_count}', inline=False)
        emb.add_field(name='Количество ролей', value=f'{len(guild.roles)}', inline=False)
        emb.add_field(name='Количество каналов', value=f'{len(guild.channels)}', inline=False)
        channel = self.bot.get_channel(1109210069972828261)
        await channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        await remove_server(guild.id)
        await remove_server_audit(guild.id)
        for member in guild.members:
            await remove_user(guild.id, member.id)
        emb = disnake.Embed()
        emb.set_author(name=f'{guild.name}')
        emb.set_footer(text=f'ID: {guild.id}')
        emb.add_field(name='Создатель', value=f'{guild.owner} | {guild.owner.id}', inline=False)
        emb.add_field(name='Создан', value=f'{guild.created_at.strftime("%d.%m.%Y %H:%M:%S")}', inline=False)
        emb.add_field(name='Владелец', value=f'{guild.owner}', inline=False)
        emb.add_field(name='Количество участников', value=f'{guild.member_count}', inline=False)
        emb.add_field(name='Количество ролей', value=f'{len(guild.roles)}', inline=False)
        emb.add_field(name='Количество каналов', value=f'{len(guild.channels)}', inline=False)
        channel = self.bot.get_channel(1109210111248969779)
        await channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        await get_user(member.guild.id, member.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        await remove_user(member.guild.id, member.id)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before, after):
        voice_audit_channel_id = await db.guilds_audit.find_one({"gid": member.guild.id})
        voice_audit_channel_id = voice_audit_channel_id['voice_audit_chn']
        voice_audit_channel = self.bot.get_channel(voice_audit_channel_id)
        if voice_audit_channel is None:
            return
        # присоединение к каналу
        if before.channel is None and after.channel is not None:
            emb = disnake.Embed()
            emb.add_field(name="Пользователь", value=f"{member.mention}", inline=False)
            emb.add_field(name="Присоединился к каналу", value=f"{after.channel.mention}", inline=False)
            emb.timestamp = datetime.datetime.now()
            emb.color = INVISIBLE
            emb.set_footer(text=f'ID пользователя: {member.id}', icon_url=member.display_avatar.url)
            await voice_audit_channel.send(embed=emb)

        # покинул канал
        elif before.channel is not None and after.channel is None:
            emb = disnake.Embed()
            emb.add_field(name="Пользователь", value=f"{member.mention}", inline=False)
            emb.add_field(name="Покинул канал", value=f"{before.channel.mention}", inline=False)
            emb.timestamp = datetime.datetime.now()
            emb.color = INVISIBLE
            emb.set_footer(text=f'ID пользователя: {member.id}', icon_url=member.display_avatar.url)
            await voice_audit_channel.send(embed=emb)

        # перешел в другой канал
        elif before.channel is not None and after.channel is not None:
            emb = disnake.Embed()
            emb.add_field(name="Пользователь", value=f"{member.mention}", inline=False)
            emb.add_field(name="Перешёл в другой канал", value=f"", inline=False)
            emb.add_field(name="Покинутый канал", value=f"{before.channel.mention}", inline=False)
            emb.add_field(name="Новый канал", value=f"{after.channel.mention}", inline=False)
            emb.timestamp = datetime.datetime.now()
            emb.color = INVISIBLE
            emb.set_footer(text=f'ID пользователя: {member.id}', icon_url=member.display_avatar.url)
            await voice_audit_channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: disnake.Role):
        roles_audit_channel_id = await db.guilds_audit.find_one({"gid": role.guild.id})
        roles_audit_channel_id = roles_audit_channel_id['roles_audit_chn']
        roles_audit_channel = self.bot.get_channel(roles_audit_channel_id)
        if roles_audit_channel is None:
            return
        emb = disnake.Embed()
        emb.add_field(name="Была создана новая роль", value=f"{role.mention}", inline=False)
        emb.timestamp = datetime.datetime.now()
        emb.color = INVISIBLE
        emb.set_footer(text=f'ID роли: {role.id}')
        await roles_audit_channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: disnake.Role):
        roles_audit_channel_id = await db.guilds_audit.find_one({"gid": role.guild.id})
        roles_audit_channel_id = roles_audit_channel_id['roles_audit_chn']
        roles_audit_channel = self.bot.get_channel(roles_audit_channel_id)
        if roles_audit_channel is None:
            return
        emb = disnake.Embed()
        emb.add_field(name="Была удалена роль", value=f"{role}", inline=False)
        emb.timestamp = datetime.datetime.now()
        emb.color = INVISIBLE
        emb.set_footer(text=f'ID роли: {role.id}')
        await roles_audit_channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: disnake.Role, after: disnake.Role):
        roles_audit_channel_id = await db.guilds_audit.find_one({"gid": before.guild.id})
        roles_audit_channel_id = roles_audit_channel_id['roles_audit_chn']
        roles_audit_channel = self.bot.get_channel(roles_audit_channel_id)
        if roles_audit_channel is None:
            return
        emb = disnake.Embed()
        emb.add_field(name="Была обновлена роль", value=f"{before.mention}", inline=False)
        emb.add_field(name="Прошлое название", value=f"{before.name}", inline=False)
        emb.add_field(name="Новое название", value=f"{after.name}", inline=False)
        before_perms = ''
        after_perms = ''
        for permis in before.permissions:
            for perm in permis:
                before_perms += str(perm).replace(",", " \n").replace("True", ": Да\n").replace("False", ": Нет\n")
        for new_permis in after.permissions:
            for new_perm in new_permis:
                after_perms += str(new_perm).replace(",", " \n").replace("True", ": Да\n").replace("False", ": Нет\n")
        #emb.description = f'''
#Сатарые разрешения:
#{before_perms}
#Новые разрешения:
#{after_perms}
#        '''
        emb.timestamp = datetime.datetime.now()
        emb.color = INVISIBLE
        emb.set_footer(text=f'ID роли: {before.id}')
        await roles_audit_channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        if message.author == self.bot.user or message.author.bot:
            return
        text_audit_channel_id = await db.guilds_audit.find_one({"gid": message.guild.id})
        text_audit_channel_id = text_audit_channel_id['text_channel_audit_chn']
        text_audit_channel = self.bot.get_channel(text_audit_channel_id)
        if text_audit_channel is None:
            return
        emb = disnake.Embed()
        emb.add_field(name="Было удалено сообщение", value=f"{message.content}", inline=False)
        emb.add_field(name='Автор сообщения', value=f"{message.author.mention}", inline=False)
        emb.timestamp = datetime.datetime.now()
        emb.color = INVISIBLE
        emb.set_footer(text=f'ID сообщения: {message.id}\nID пользователя: {message.author.id}')
        await text_audit_channel.send(embed=emb)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author == self.bot.user or before.author.bot:
            return
        text_audit_channel_id = await db.guilds_audit.find_one({"gid": before.guild.id})
        text_audit_channel_id = text_audit_channel_id['text_channel_audit_chn']
        text_audit_channel = self.bot.get_channel(text_audit_channel_id)
        if text_audit_channel is None:
            return
        emb = disnake.Embed()
        emb.add_field(name="Было изменено сообщение", value=f"{before.content}", inline=False)
        emb.add_field(name='Автор сообщения', value=f"{before.author.mention}", inline=False)
        emb.add_field(name='Контент изменённого сообщения', value=f"{after.content}",)
        emb.timestamp = datetime.datetime.now()
        emb.color = INVISIBLE
        emb.set_footer(text=f'ID сообщения: {before.id}\nID пользователя: {before.author.id}')
        await text_audit_channel.send(embed=emb)



def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))