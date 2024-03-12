import disnake
from disnake.ext import commands
import json
from bot.mongodb import *
import math

with open('bot/config.json', 'r') as f:
    data = json.load(f)
intents=disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

bot.load_extensions("bot/cogs")
print('Cogs connected to Ansero')

class AnseroHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        embed = disnake.Embed(title="Help")
        commands_count = 0
        for cog, cog_commands in mapping.items():
            filtered = await self.filter_commands(cog_commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            for _ in command_signatures:
                commands_count += 1
            command_signatures_filtered = []
            for command in command_signatures:
                command_signatures_filtered.append('> • ' + command.replace('_', ''))
            if command_signatures_filtered:
                cog_name = getattr(cog, "qualified_name", "Help")
                if cog_name.lower() not in ['owner']:
                    embed.add_field(name=cog_name, value="\n".join(command_signatures_filtered), inline=False)
        embed.add_field(name='Всего команд:', value=commands_count, inline=False)
        embed.add_field(name='Официальный сервер:', value='[Ansero bot](https://discord.gg/anserobot)', inline=False)
        embed.add_field(name='Разработчик:', value='[wmd](https://discord.com/users/1064250083899625482/)', inline=False)
        embed.add_field(name='Владелец:', value='[Лис](https://discord.com/users/594200610631581697/)', inline=False)
        embed.colour = 0x2b2d31
        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_error_message(self, error):
        embed = disnake.Embed(title="Ошибка:", description=error, color=disnake.Colour.red())
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1107059277157376000/1107685797966127245/tug4d-1.gif')
        embed.set_footer(text='Упс!')
        channel = self.get_destination()

        await channel.send(embed=embed)
    
    async def send_command_help(self, command):
        embed = disnake.Embed(title=self.get_command_signature(command), color=0x2b2d31)
        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            embed.add_field(name="Синонимы", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_cog_help(self, cog):
        embed = disnake.Embed(title=cog.qualified_name or "Нет категории", description=cog.description, color=0x2b2d31)

        if filtered_commands := await self.filter_commands(cog.get_commands()):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "Справочное сообщение не найдено... ", inline=False)

        await self.get_destination().send(embed=embed)


bot.help_command = AnseroHelp()


@bot.event
async def on_message(message: disnake.Message):
    await get_server(message.guild.id)
    await add_server_audit(message.guild.id)
    await get_user(message.guild.id, message.author.id)
    await bot.process_commands(message)

bot.run(data["API"]['token'])
