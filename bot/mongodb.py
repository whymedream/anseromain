from motor.motor_asyncio import AsyncIOMotorClient
import json

with open('bot/config.json', 'r') as f:
    data = json.load(f)

db = AsyncIOMotorClient(data["DB"]["DB_SETTINGS"]["url"])[data["DB"]["DB_SETTINGS"]["db_name"]]

async def get_user(guild_id, user_id):
    user = await db.users.find_one({"gid": guild_id, "uid": user_id})
    server = await db.guilds.find_one({"gid": guild_id})
    if user is None:
        await db.users.insert_one({
            "gid": guild_id,
            "uid": user_id,
            "balance": server['initial_balance'],
            "bank": 0,
            'likes': 0,
            "messages": 0,
            "commands_done": 0,
            "subscribers": [],
            "active games": {
                "crash": False,
                "black_jack": False
            }
            })
        await db.badges.insert_one({
            "uid": user_id,
            "badges": '',
        })
    return user


async def remove_user(guild_id, user_id):
    """Удаление пользователя из базы данных. Использовать только в events"""
    user = await db.users.find_one({"gid": guild_id, "uid": user_id})
    if user is not None:
        await db.users.delete_one({"gid": guild_id, "uid": user_id})
    else: pass

async def get_server(guild_id):
    """Поиск сервера в базе данных. Если пользователь не найден, то добавляем его в бд"""
    server = await db.guilds.find_one({"gid": guild_id})
    if server is None:
        await db.guilds.insert_one({
            "gid": guild_id,
            "prefix": "!",
            "work": [5000, 10000],
            "bonus": [500, 2000],
            "crime": [2500, 10000],
            "currency": data["EMOJI"]["default_currency"],
            'initial_balance': 5000,
            'audit': False, 
            'moderation': True
            })
    return server

async def remove_server(guild_id):
    """Удаление сервера из базы данных"""
    server = await db.guilds.find_one({"gid": guild_id})
    if server is not None:
        await db.guilds.delete_one({"gid": guild_id})
    else: pass

async def add_server_audit(guild_id):
    """Добавление аудита сервера в базу данных"""
    server = await db.guilds_audit.find_one({"gid": guild_id})
    if server is None:
        await db.guilds_audit.insert_one({
            "gid": guild_id,
            "money_audit_chn": None,
            "voice_audit_chn": None,
            "roles_audit_chn": None,
            "text_channel_audit_chn": None,
            })
    else: pass

async def remove_server_audit(guild_id):
    """Удаление аудита сервера из базы данных"""
    server = await db.guilds_audit.find_one({"gid": guild_id})
    if server is not None:
        await db.guilds_audit.delete_one({"gid": guild_id})
    else: pass

async def get_prefix(bot, message):
    """Получение префикса из базы данных"""
    server = await db.guilds.find_one({"gid": message.guild.id})
    if server is not None:
        return server["prefix"]
    else: return "!"

async def get_currency(guild_id):
    """Получение значка валюты из базы данных"""
    server = await db.guilds.find_one({"gid": guild_id})
    if server is not None:
        return server["currency"]
    else: return "<a:998158048952586280:1106708060564623520>"

    
