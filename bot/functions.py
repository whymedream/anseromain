import disnake
from disnake.ext import commands
from bot.mongodb import *

async def send_error(ctx: commands.Context, message: disnake.Message):
    emb = disnake.Embed()
    emb.set_author(name=f'{ctx.author}', icon_url=ctx.author.display_avatar, url=f'https://discordapp.com/users/{ctx.author.id}/')
    emb.add_field(name=f'Ошибка:', value=f'{message}')
    emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/1107059277157376000/1107685797966127245/tug4d-1.gif')
    emb.set_footer(text='Упс!')
    emb.colour = disnake.Colour.red()
    await ctx.send(embed=emb)
    return

def get_amount(iamount, user_obj: object):
    if type(iamount) == float:
        return
    if iamount in ['all', 'full', 'все', 'всё']:
        amount = int(user_obj['balance'])
    elif iamount in ['half', 'половину', 'половина']:
        amount = int(user_obj['balance'] / 2)
    elif int(iamount):
        amount = int(iamount)
    
    return amount

async def start_game(user: object, game_name: str):
    await db.users.update_one({'gid': user['gid'], 'uid': user['uid']}, {'$set': {'active games': {game_name: True}}})

async def end_game(user: object, game_name: str):
    await db.users.update_one({'gid': user['gid'], 'uid': user['uid']}, {'$set': {'active games': {game_name: False}}})

async def send_money_log(self, ctx: commands.Context, content: str=None, embed: disnake.Embed = None):
    money_audit_channel_id = await db.guilds_audit.find_one({"gid": ctx.guild.id})
    money_audit_channel_id = money_audit_channel_id['money_audit_chn']
    money_audit_channel = self.bot.get_channel(money_audit_channel_id)
    components = [
        disnake.ui.Button(label='Перейти к сообщению', url=ctx.message.jump_url)
    ]
    if money_audit_channel is None:

        return
    await money_audit_channel.send(content=content, embed=embed, components=components)
