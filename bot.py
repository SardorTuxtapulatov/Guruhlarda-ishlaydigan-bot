from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, and_f
from aiogram import F
from aiogram.types import Message, ChatPermissions, input_file
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands import set_default_commands
from baza.sqlite import Database
from filtersd.admin import IsBotAdminFilter
from filtersd.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id

    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)
    except Exception as e:
        logging.exception(f"Failed to add user: {e}")

    inline_keyboard = [
        [InlineKeyboardButton(text="Add to Group", callback_data="add_to_group")],
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await message.answer(
        text="Assalomu alaykum, botimizga hush kelibsiz. Quyidagi tugma orqali guruhga qo'shish bo'yicha ko'rsatmalarni ko'rishingiz mumkin:",
        reply_markup=markup
    )

@dp.message(Command("admin"), IsBotAdminFilter(ADMINS))
async def is_admin(message: Message):
    await message.answer(text="Admin menu", reply_markup=admin_keyboard.admin_button)

@dp.message(Command("help"), IsBotAdminFilter(ADMINS))
async def ishf_admin(message: Message):
    await message.answer(text="Bu bot gruhlarni tartibga solib turadi")

@dp.message(F.text == "Foydalanuvchilar soni", IsBotAdminFilter(ADMINS))
async def users_count(message: Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text == "Reklama yuborish", IsBotAdminFilter(ADMINS))
async def advert_dp(message: Message, state: FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message: Message, state: FSMContext):
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = await db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0], from_chat_id=from_chat_id, message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.5)

    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()

@dp.message(and_f(F.reply_to_message, F.text == "/setadmin"))
async def set_admin(message: Message):
    await message.delete()

    chat = await bot.get_chat(message.chat.id)
    user_id = message.from_user.id

    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        owner = next((admin.user.id for admin in admins if admin.status == "creator"), None)

        if user_id == owner:
            user_to_promote = message.reply_to_message.from_user.id

            try:
                await bot.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_to_promote,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True
                )
                notification_message = await message.answer(
                    f"{message.reply_to_message.from_user.first_name} admin qilib tayinlandi."
                )
            except Exception as e:
                logging.exception(f"Failed to promote user: {e}")
                notification_message = await message.answer(
                    "Foydalanuvchini admin qilishda xatolik yuz berdi. Botda yetarli huquqlar borligiga ishonch hosil qiling."
                )
        else:
            notification_message = await message.answer("Faqat guruh egasi foydalanuvchini admin qilib tayinlashi mumkin.")

        await asyncio.sleep(10)
        await notification_message.delete()

        logging.info(f"Admin command executed by {message.from_user.full_name} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id}).")

    except Exception as e:
        logging.exception(f"Failed to retrieve chat administrators: {e}")
        await message.answer("Xatolik yuz berdi. Administratorlar ro'yxatini olishda muammo bo'ldi.")


#unadmin----------------------------------------------------------------------------------------
@dp.message(and_f(F.reply_to_message, F.text == "/unadmin"))
async def unadmin_user(message: Message):
    await message.delete()

    chat = await bot.get_chat(message.chat.id)
    user_id = message.from_user.id

    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        owner = next((admin.user.id for admin in admins if admin.status == "creator"), None)

        if user_id == owner:
            user_to_demote = message.reply_to_message.from_user.id

            try:
                # Demote the user, removing all admin privileges
                await bot.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_to_demote,
                    can_change_info=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False
                )
                notification_message = await message.answer(
                    f"{message.reply_to_message.from_user.first_name} adminlikdan olib tashlandi."
                )
            except Exception as e:
                logging.exception(f"Failed to demote user: {e}")
                notification_message = await message.answer(
                    "Foydalanuvchini adminlikdan olishda xatolik yuz berdi. Botda yetarli huquqlar borligiga ishonch hosil qiling."
                )
        else:
            notification_message = await message.answer("Faqat guruh egasi foydalanuvchini adminlikdan olib tashlashi mumkin.")

        await asyncio.sleep(10)
        await notification_message.delete()

        logging.info(f"Unadmin command executed by {message.from_user.full_name} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id}).")

    except Exception as e:
        logging.exception(f"Failed to retrieve chat administrators: {e}")
        await message.answer("Xatolik yuz berdi. Administratorlar ro'yxatini olishda muammo bo'ldi.")
#unadmin---------------------------------------------------------------------------------------------------------------------------------

@dp.message(F.left_chat_member)
async def new_member(message: Message):
    user = message.left_chat_member.full_name
    notification_message = await message.answer(f"{user} Xayr!")
    await message.delete()
    await asyncio.sleep(10)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/ban"))
async def ban_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhdan chiqarilib yuborildi.")
    await asyncio.sleep(10)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/unban"))
async def unban_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    await message.chat.unban_sender_chat(user_id)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga qaytishingiz mumkin.")
    await asyncio.sleep(10)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/mute"))
async def mute_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=False)
    until_date = int(time()) + 300
    await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} 5 minutga blocklandingiz")
    await asyncio.sleep(20)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/unmute"))
async def unmute_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=True)
    await message.chat.restrict(user_id=user_id, permissions=permission)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga yoza olasiz")
    await asyncio.sleep(10)
    await notification_message.delete()

xaqoratli_sozlar = {"tentak", "jinni", "axmoq", "garang", "dalbayob", "ko't", "dalban", "iflos"}
@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"), F.text))
async def tozalash(message: Message):
    text = message.text
    for soz in xaqoratli_sozlar:
        if soz in text.lower():
            user_id = message.from_user.id
            until_date = int(time()) + 300
            permission = ChatPermissions(can_send_messages=False)
            await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
            notification_message = await message.answer(text=f"{message.from_user.mention_html()} guruhda so'kinganingiz uchun 5 minutga blokka tushdingiz")
            await message.delete()
            await asyncio.sleep(20)
            await notification_message.delete()
            break

@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin), text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin), text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)

async def main() -> None:
    global bot, db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
