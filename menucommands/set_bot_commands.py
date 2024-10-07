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
        BotCommand(command="/ban", description="foydalanuvchiga ban berib guruhdan chiqarish"),
        BotCommand(command="/unban", description="foydalanuvchini bandan chiqarish"),
        BotCommand(command="/mute", description="foydalanuvchini guruhga yozishini cheklash"),
        BotCommand(command="/unmute", description="foydalanuvchiga imtiyozlarini qaytarish"),
        BotCommand(command="/setadmin", description="foydalanuvchiga admin berish"),
        BotCommand(command="/unadmin", description="foydalanuchidan adminni olish"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllGroupChats())