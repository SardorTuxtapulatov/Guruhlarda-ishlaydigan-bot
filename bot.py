from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, and_f
from aiogram import F
from aiogram.types import Message, ChatPermissions, input_file, ReplyKeyboardRemove
from data import config
import asyncio
import time
from funksiya.funksiya import create_inline_keyboard
import logging
from states.bulimlar import AdminStates,ShortNickStates,LongNickStates
import sys
from aiogram import types
from menucommands.set_bot_commands import set_default_commands, set_default_command
from buttonlar import inline_menu
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
from aiogram.types import CallbackQuery, ContentType
from keyboard_buttons.admin_keyboard import start_button
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    if message.chat.type == 'private':
        await message.answer("Salom 👋",reply_markup=start_button)
    else:
        await message.answer("Salom 👋", reply_markup=ReplyKeyboardRemove())

        
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id) #foydalanuvchi bazaga qo'shildi
        await message.answer("Men o'zbekcha.. reklamalarni, ssilkalarni Guruhlarda o'chirib beraman 👨🏻‍✈️\n<i>Guruhga qoʻshilgan a'zolarni, kirdi - chiqdi 🗑 va so'kingan 🔞+ xabarlarini oʻchiradi.</i>\n\nMen ishlashim uchun Guruhizga qo'shib ADMIN berishingiz kerak😄", reply_markup=inline_menu, parse_mode='html')
        
    except:
        await message.answer(text="Men o'zbekcha reklamalarni, silkalarni Guruhlarda o'chirib beraman 👨🏻‍✈️\n\n<i>Guruhga qoʻshilgan a'zolarni, kirdi - chiqdi 🗑 va so'kingan 🔞+ xabarlarini oʻchiradi.</i>\n\nMen ishlashim uchun Guruhizga qo'shib ADMIN berishingiz kerak😄", reply_markup=inline_menu )


# @dp.message(CommandStart())
# async def start_command(message: Message):
#     full_name = message.from_user.full_name
#     telegram_id = message.from_user.id

#     try:
#         db.add_user(full_name=full_name, telegram_id=telegram_id)
#     except Exception as e:
#         logging.exception(f"Failed to add user: {e}")

#     inline_keyboard = [
#         [InlineKeyboardButton(text="➕ GURUHGA QO'SHISH ➕", url="t.me/guruhlar_qorovuli_bot?startgroup=uz")],
#     ]
#     inline_keyboard1 = [
#         [InlineKeyboardButton(text="🚫SO'KINISH O'CHIRISH👈", url="t.me/guruhlar_qorovuli_bot?startgroup=uz")],
#     ]

#     markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

#     await message.answer(
#         text="Men o'zbekcha reklamalarni, ssilkalarni Guruhlarda o'chirib beraman 👨🏻‍✈️ Guruhga qoʻshilgan a'zolarni, kirdi - chiqdi 🗑 va so'kingan 🔞+ xabarlarini oʻchiradi. Men ishlashim uchun Guruhizga qo'shib ADMIN berishingiz kerak😄",
#         reply_markup=markup
#     )

@dp.message(Command("admin"), IsBotAdminFilter(ADMINS))
async def is_admin(message: Message):
    await message.answer(text="Admin menu", reply_markup=admin_keyboard.admin_button)

@dp.message(Command("about"), IsBotAdminFilter(ADMINS))
async def ishf_admin(message: Message):
    await message.answer(text="Bot dan shikoyatingiz yoki taklifingiz bo'lsa📜\n👤Admin bilan bog'lanish tugmasini bosing\nYoki menu dan 📜 \"👨‍💼 Admin\" ni bosib murojatingizni yozing✅\nva xabaringizni yozib qoldiring✅Botdan foydalanish tartibi👇🏻\n👉🏻 @guruhlar_qorovuli_bot Bu bot sizning guruhingizni silka va so'kinishlardan tozalaydi🙂")

@dp.message(Command("help"), IsBotAdminFilter(ADMINS))
async def ishf_admin(message: Message):
    await message.answer(text="🔥 Buyruqlar \nBotdan foydalanish uchun ... \n /about - Bot haqida \n\nAdmin bilan bog'lanmoqchi bo'lsangiz \"👨‍💼 Admin\" tugmasini bosing va ✉️ Xabaringizni yozib qoldiring ! ")

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
    users = db.all_users_id()
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

@dp.message(and_f(F.reply_to_message, F.text == "/setadmin@guruhlar_qorovuli_bot"))
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
@dp.message(and_f(F.reply_to_message, F.text == "/unadmin@guruhlar_qorovuli_bot"))
async def unadmin_user(message: Message):
    await message.delete()

    chat = await bot.get_chat(message.chat.id)
    user_id = message.from_user.id

    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        owner = next((admin.user.id for admin in admins if admin.status == "creator"), None)
        adminstrator = next((admin.user.id for admin in admins if admin.status == "adminstrator"), None)

        if (user_id == owner) or user_id == adminstrator:
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
async def left_member(message: Message):
    user = message.left_chat_member.full_name
    notification_message = await message.answer(f"{user} Xayr!")
    await message.delete()
    await asyncio.sleep(10)
    await notification_message.delete()

@dp.message(F.new_chat_member)
async def new_member(message: Message):
    user = message.new_chat_members[0].full_name
    # print(user)
    notification_message = await message.answer(f"{user} Hush kelibsiz!")
    await message.delete()
    await asyncio.sleep(10)
    await notification_message.delete()


@dp.message(and_f(F.reply_to_message, F.text == "/ban@guruhlar_qorovuli_bot"))
async def ban_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhdan chiqarilib yuborildi.")
    await asyncio.sleep(10)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/unban@guruhlar_qorovuli_bot"))
async def unban_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    await message.chat.unban_sender_chat(user_id)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga qaytishingiz mumkin.")
    await asyncio.sleep(10)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/mute@guruhlar_qorovuli_bot"))
async def mute_user(message: Message):
    
    user_id = message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=False)
    until_date = int(time.time()) + 300
    await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} 5 minutga blocklandingiz")
    await message.delete()
    await asyncio.sleep(20)
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message, F.text == "/unmute@guruhlar_qorovuli_bot"))
async def unmute_user(message: Message):
    await message.delete()
    user_id = message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=True)
    await message.chat.restrict(user_id=user_id, permissions=permission)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga yoza olasiz")
    await asyncio.sleep(10)
    await notification_message.delete()

xaqoratli_sozlar = {"tentak", "jinni", "axmoq", "garang","zebra", "tvar","mol","dalbayob", "ko't", "dalban", "iflos"}
@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"), F.text))
async def tozalash(message: Message):
    text = message.text
    if "zebra" in text.lower():
            await message.answer(text=f"{message.from_user.mention_html()} O'zing zebra")
    for soz in xaqoratli_sozlar:

        if soz in text.lower():
            user_id = message.from_user.id
            until_date = int(time.time()) + 300
            permission = ChatPermissions(can_send_messages=False)
            await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
            notification_message = await message.answer(text=f"{message.from_user.mention_html()} guruhda so'kinganingiz uchun 5 minutga blokka tushdingiz")
            await message.delete()
            await asyncio.sleep(20)
            await notification_message.delete()
            break


#Qo'llanma
@dp.message(F.text == "📙Qo'llanma", F.chat.type  == 'private')
async def guide_handler(message: Message, state: FSMContext):
    text = """
    Botdan foydalanish uchun qo'llanma 📂:
    1 Botdan foydalanish uchun botimizni guruhga admin qiling.
    2 /ban foydalanuvchiga ban berib guruhdan chiqarish
    3 /unban foydalanuvchini bandan chiqarish
    4 /mute foydalanuvchini guruhga yozishini cheklash
    5 /unmute foydalanuvchiga imtiyozlarini qaytarish
    6 /setadmin foydalanuvchiga admin berish
    7 /unadmin foydalanuchidan adminni olish
    """
    await message.answer(text=text)


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Admin message handler
@dp.message(F.text == "👨‍💼Admin", F.type == 'private')
async def admin_message(message: Message, state: FSMContext):
    await message.answer("Admin uchun xabar yuboring:")
    await state.set_state(AdminStates.waiting_for_admin_message)

@dp.message(AdminStates.waiting_for_admin_message, F.content_type.in_([
    ContentType.TEXT, ContentType.AUDIO, ContentType.VOICE, ContentType.VIDEO,
    ContentType.PHOTO, ContentType.ANIMATION, ContentType.STICKER, 
    ContentType.LOCATION, ContentType.DOCUMENT, ContentType.CONTACT,
    ContentType.VIDEO_NOTE
]))

async def handle_admin_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""  # Some users may not have a last name

    # Use username if available, otherwise use first name + last name
    if username:
        user_identifier = f"@{username}"
    else:
        user_identifier = f"{first_name} {last_name}".strip()  # Remove any extra spaces

    video_note = message.video_note
    inline_keyboard = create_inline_keyboard(user_id)
    for admin_id in ADMINS:
        try:
            if video_note:
                print('adfs', message.video_note.file_id)
                # Echo the video note back to the user
                await bot.send_video_note(
                    admin_id,
                    video_note.file_id,
                    reply_markup=inline_keyboard
                )
            elif message.text:
                await bot.send_message(
                    admin_id,
                    f"Foydalanuvchi: {user_identifier}\nXabar:\n{message.text}",
                    reply_markup=inline_keyboard
                )
            elif message.audio:
                await bot.send_audio(
                    admin_id,
                    message.audio.file_id,
                    caption=f"Foydalanuvchi: {user_identifier}\nAudio xabar",
                    reply_markup=inline_keyboard
                )
            elif message.voice:
                await bot.send_voice(
                    admin_id,
                    message.voice.file_id,
                    caption=f"Foydalanuvchi: {user_identifier}\nVoice xabar",
                    reply_markup=inline_keyboard
                )
            elif message.video:
                await bot.send_video(
                    admin_id,
                    message.video.file_id,
                    caption=f"Foydalanuvchi: {user_identifier}\nVideo xabar",
                    reply_markup=inline_keyboard
                )
            elif message.photo:
                await bot.send_photo(
                    admin_id,
                    message.photo[-1].file_id,  # using the highest resolution photo
                    caption=f"Foydalanuvchi: {user_identifier}\nRasm xabar",
                    reply_markup=inline_keyboard
                )
            elif message.animation:
                await bot.send_animation(
                    admin_id,
                    message.animation.file_id,
                    caption=f"Foydalanuvchi: {user_identifier}\nGIF xabar",
                    reply_markup=inline_keyboard
                )
            elif message.sticker:
                await bot.send_sticker(
                    admin_id,
                    message.sticker.file_id,
                    reply_markup=inline_keyboard
                )
            elif message.location:
                await bot.send_location(
                    admin_id,
                    latitude=message.location.latitude,
                    longitude=message.location.longitude,
                    reply_markup=inline_keyboard
                )
            elif message.document:
                await bot.send_document(
                    admin_id,
                    message.document.file_id,
                    caption=f"Foydalanuvchi: {user_identifier}\nHujjat xabar",
                    reply_markup=inline_keyboard
                )
            elif message.contact:
                await bot.send_contact(
                    admin_id,
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=message.contact.last_name or "",
                    reply_markup=inline_keyboard
                )
        except Exception as e:
            logging.error(f"Error sending message to admin {admin_id}: {e}")

    await state.clear()
    await bot.send_message(user_id, "Admin sizga javob berishi mumkin.", reply_markup=admin_keyboard.start_button)

# Callback query handler for the reply button
@dp.callback_query(lambda c: c.data.startswith('reply:'))
async def process_reply_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split(":")[1])
    await callback_query.message.answer("Javobingizni yozing. Sizning javobingiz foydalanuvchiga yuboriladi.",reply_markup=admin_keyboard.start_button)
    await state.update_data(reply_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_reply_message)
    await callback_query.answer()

# Handle admin reply and send it back to the user
@dp.message(AdminStates.waiting_for_reply_message)
async def handle_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    original_user_id = data.get('reply_user_id')

    if original_user_id:
        try:
            if message.text:
                await bot.send_message(original_user_id, f"Admin javobi:\n{message.text}", reply_markup=admin_keyboard.start_button)
            
            elif message.voice:
                await bot.send_voice(original_user_id, message.voice.file_id, reply_markup=admin_keyboard.start_button)

            elif message.video_note:
                await bot.send_video_note(original_user_id, message.video_note.file_id, reply_markup=admin_keyboard.start_button)

            elif message.audio:
                await bot.send_audio(original_user_id, message.audio.file_id, reply_markup=admin_keyboard.start_button)
            
            elif message.sticker:
                await bot.send_sticker(original_user_id, message.sticker.file_id, reply_markup=admin_keyboard.start_button)
            
            elif message.video:
                await bot.send_video(original_user_id, message.video.file_id, reply_markup=admin_keyboard.start_button)

            await state.clear()  # Clear state after sending the reply
        except Exception as e:
            logger.error(f"Error sending reply to user {original_user_id}: {e}")
            await message.reply("Xatolik: Javob yuborishda xato yuz berdi.")
    else:
        await message.reply("Xatolik: Javob yuborish uchun foydalanuvchi ID topilmadi.")



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
    await set_default_command(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())











