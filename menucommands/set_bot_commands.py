from aiogram import Bot
from aiogram.methods.set_my_commands import BotCommand
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Botni ishga tushirish"),
        BotCommand(command="/help", description="Yordam"),
        BotCommand(command="/about", description="Biz haqimizda"),

    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())

async def set_default_command(bot: Bot):
    commands = [
        BotCommand(command="/ban", description="Botni ishga tushirish"),
        BotCommand(command="/unban", description="Yordam"),
        BotCommand(command="/mute", description="Biz haqimizda"),
        BotCommand(command="/unmute", description="Biz haqimizda"),
        BotCommand(command="/setadmin", description="Biz haqimizda"),
        BotCommand(command="/unadmin", description="Biz haqimizda"),
        BotCommand(command="/setadmin", description="Biz haqimizda"),

    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllGroupChats())