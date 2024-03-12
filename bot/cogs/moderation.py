import disnake
from bot.functions import send_error
from disnake.ext import commands
from bot.cogs.economy import INVISIBLE
from bot.mongodb import *

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='очистить', aliases=['cls'])
    async def clear(self, ctx: commands.Context, amount = None):
        """
        **Очистить сообщение в канале(только администратор/модератор)**\n
        Пример использования: `!очистить, !очистить 10`
        """
        if amount is None:
            await send_error(ctx, "Укажите количество сообщений для удаления.")
            return
        try: amount = int(amount)
        except: pass
        if isinstance(amount, int) is False:
            await send_error(ctx, "Количество сообщений должно быть целым числом.")
            return
        if ctx.author.guild_permissions.administrator: 
            await ctx.channel.purge(limit=amount)
            await ctx.send(f"Очищено {amount} сообщений.")
        else: await ctx.send("У вас нет разрешения на использование данной команды.")
    
    @commands.command(name='кик', aliases=['выгнать', 'кикнуть'])
    async def kick(self, ctx: commands.Context, member: disnake.Member, *, reason = 'по решению модерации'):
        """
        **Выгнать пользователя с дискорд сервера(только администратор/модератор)**\n
        Пример использования: `!кик @User123 причина`
        """
        if ctx.author.guild_permissions.kick_members:
            guild = await db.guilds.find_one({'gid': ctx.guild.id})
            if guild['moderation'] is False:
                await send_error(ctx, f'На вашем сервере отключена модерация.\nВключить модерацию можно через команду {ctx.prefix}настроить')
                return
            await member.kick(reason = reason)
            emb = disnake.Embed()
            emb.colour = INVISIBLE
            emb.add_field(name = f"Пользователь успешно выгнан с сервера {ctx.guild.name}", value = f"{member.mention} ({member.id})", inline=False)
            emb.add_field(name = "Причина", value = reason, inline=False)
            if ctx.author.guild_permissions.kick_members:
                emb.add_field(name = "Модератор", value = ctx.author.mention, inline=False)
            elif ctx.author.guild_permissions.administrator:
                emb.add_field(name = "Администратор", value = ctx.author.mention, inline=False)
            await ctx.send(embed = emb)
        else: await send_error(ctx, "У вас нет разрешения на использование данной команы.")
    
    @commands.command(name='бан', aliases=['забанить'])
    async def ban(self, ctx: commands.Context, member: disnake.Member, *, reason = 'по решению модерации'):
        """
        **Забанить польщователя на дискорд сервере(только администратор/модератор)**\n
        Пример использования: `!бан @User123 причина`
        """
        if ctx.author.guild_permissions.ban_members:
            guild = await db.guilds.find_one({'gid': ctx.guild.id})
            if guild['moderation'] is False:
                await send_error(ctx, f'На вашем сервере отключена модерация.\nВключить модерацию можно через команду {ctx.prefix}настроить')
                return
            await member.ban(reason = reason)
            emb = disnake.Embed()
            emb.colour = INVISIBLE
            emb.add_field(name = f"Пользователь успешно забанен на сервере {ctx.guild.name}", value = f"{member.mention} ({member.id})", inline=False)
            emb.add_field(name = "Причина", value = reason, inline=False)
            if ctx.author.guild_permissions.ban_members:
                emb.add_field(name = "Модератор", value = ctx.author.mention, inline=False)
            elif ctx.author.guild_permissions.administrator:
                emb.add_field(name = "Администратор", value = ctx.author.mention, inline=False)
            await ctx.send(embed = emb)
        else: await send_error(ctx, "У вас нет разрешения на использование данной команы.")
    
    @commands.command(name='мут', aliases=['замутить'])
    async def mute(self, ctx: commands.Context, member: disnake.Member, duration = 3600.0, *, reason = 'по решению модерации'):
        """
        **Замутить участника дискорд сервера(только администратор/модератор)**\n
        Пример использования: `!мут @User123 10с`
        """
        if ctx.author.guild_permissions.mute_members:
            guild = await db.guilds.find_one({'gid': ctx.guild.id})
            if guild['moderation'] is False:
                await send_error(ctx, f'На вашем сервере отключена модерация.\nВключить модерацию можно через команду {ctx.prefix}настроить')
                return
            def convert(time):
                pos = ["s","m","h","d","с","м","ч","д"]

                time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d": 3600*24, "с" : 1, "м" : 60, "ч" : 3600, "д": 3600*24}

                unit = time[-1]

                if unit not in pos:
                    return -1
                try:
                    val = int(time[:-1])
                except:
                    return -2

                return val * time_dict[unit]

            await member.timeout(duration=float(convert(duration)), reason = reason)
            emb = disnake.Embed()
            emb.colour = INVISIBLE
            emb.add_field(name = f"Пользователь успешно замьючен на сервере {ctx.guild.name}", value = f"{member.mention} ({member.id})", inline=False)
            emb.add_field(name = "Причина", value = reason, inline=False)
            if ctx.author.guild_permissions.mute_members:
                emb.add_field(name = "Модератор", value = ctx.author.mention, inline=False)
            elif ctx.author.guild_permissions.administrator:
                emb.add_field(name = "Администратор", value = ctx.author.mention, inline=False)
            await ctx.send(embed = emb)
        else: await send_error(ctx, "У вас нет разрешения на использование данной команы.")




def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))