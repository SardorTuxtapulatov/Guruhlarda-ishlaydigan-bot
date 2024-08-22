from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command,and_f
from aiogram import F
from aiogram.types import Message,ChatPermissions,input_file
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filtersd.admin import IsBotAdminFilter
from filtersd.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware #new
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
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

    # Creating an inline keyboard with buttons
    inline_keyboard = [
        [InlineKeyboardButton(text="Add to Group", callback_data="add_to_group")],
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await message.answer(
        text="Assalomu alaykum, botimizga hush kelibsiz. Quyidagi tugma orqali guruhga qo'shish bo'yicha ko'rsatmalarni ko'rishingiz mumkin:",
        reply_markup=markup
    )

    


# from aiogram.types import CallbackQuery

# @dp.callback_query(lambda c: c.data == "add_to_group")
# async def handle_add_to_group(callback_query: CallbackQuery):
#     # Create an inline keyboard with buttons for each group
#     inline_keyboard = []
#     for channel_id in CHANNELS:
#         chat = await bot.get_chat(chat_id=channel_id)
#         button = InlineKeyboardButton(text=f"Invite {chat.title}", url=f"https://t.me/{chat.username}")
#         inline_keyboard.append([button])  # Each button as a row

#     markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

#     await callback_query.message.edit_text(
#         text="Quyidagi guruhlarga botni taklif qilishingiz mumkin:",
#         reply_markup=markup
#     )





# @dp.message(IsCheckSubChannels())
# async def kanalga_obuna(message:Message):
#     text = ""
#     inline_channel = InlineKeyboardBuilder()
#     for index,channel in enumerate(CHANNELS):
#         ChatInviteLink = await bot.create_chat_invite_link(channel)
#         inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
#     inline_channel.adjust(1,repeat=True)
#     button = inline_channel.as_markup()
#     await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)





#Admin panel uchun
@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)

@dp.message(Command("help"),IsBotAdminFilter(ADMINS))
async def ishf_admin(message:Message):
    await message.answer(text="Bu bot gruhlarni tartibga solib turadi")


@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = await db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.5)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()


@dp.message(and_f(F.reply_to_message,F.text=="/setphoto"))
async def setphoto_group(message:Message):
    await message.delete()
    photo =  message.reply_to_message.photo[-1].file_id
    file = await bot.get_file(photo)
    file_path = file.file_path
    file = await bot.download_file(file_path)
    file = file.read()
    await message.chat.set_photo(photo=input_file.BufferedInputFile(file=file,filename="sardor.jpg"))
    notification_message = await message.answer("Guruh rasmi uzgardi")
    await asyncio.sleep(10)  # 300 seconds = 5 minutes
    await notification_message.delete()


@dp.message(and_f(IsBotAdminFilter(ADMINS), F.text.startswith('/setname')))
async def set_name(message: Message):
    # Delete the command message to keep the chat clean
    await message.delete()

    # Extract the new group name from the command
    new_title = message.text.split("/setname", 1)[1].strip()

    # Check if a new title was provided
    if new_title:
        try:
            # Set the new group title
            await message.chat.set_title(new_title)
            # Notify the group about the title change
            notification_message = await message.answer(f"Guruh nomi o'zgartirildi: {new_title}")
            
            # Optionally delete the notification message after some time
            await asyncio.sleep(10)
            await notification_message.delete()
        except Exception as e:
            # Handle any errors that occur (e.g., insufficient permissions)
            logging.exception(f"Failed to set group title: {e}")
            await message.answer("Guruh nomini o'zgartirishda xatolik yuz berdi. Botda yetarli huquqlar borligiga ishonch hosil qiling.")
    else:
        await message.answer("Iltimos, guruh uchun yangi nomni kiriting.")



@dp.message(F.new_chat_member)
async def new_member(message:Message):
    user = message.new_chat_member.get("first_name")
    notification_message = await message.answer(f"{user} Guruhga xush kelibsiz!")
    await message.delete()
    await asyncio.sleep(10)  # 300 seconds = 5 minutes
    await notification_message.delete()      
#setadmin------------------------------------------------------------------------------------------------------

from aiogram import types

@dp.message(and_f(F.reply_to_message, F.text == "/setadmin"))
async def set_admin(message: Message):
    # Delete the command message to keep the chat clean
    await message.delete()

    # Get the chat (group) information
    chat = await bot.get_chat(message.chat.id)
    owner_id = chat.owner.user.id  # ID of the group owner

    # Get the command sender's ID
    user_id = message.from_user.id

    # Check if the command sender is the group owner
    if user_id == owner_id:
        # Get the user to be promoted (the one who was replied to)
        user_to_promote = message.reply_to_message.from_user.id
        
        try:
            # Promote the user to admin with the desired permissions
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
                f"{message.reply_to_message.from_user.first_name} has been promoted to admin."
            )
        except Exception as e:
            logging.exception(f"Failed to promote user: {e}")
            notification_message = await message.answer(
                "Failed to promote the user to admin. Please ensure the bot has sufficient permissions."
            )
    else:
        notification_message = await message.answer("Only the group owner can promote members to admin.")

    await asyncio.sleep(10)  # Optionally delete the notification after some time
    await notification_message.delete()

    # Log the action
    logging.info(f"Admin command executed by {message.from_user.full_name} ({message.from_user.id}) in chat {message.chat.title} ({message.chat.id}).")







#setadmin==================================================================================--------------------------

@dp.message(F.left_chat_member)
async def new_member(message:Message):
    # print(message.new_chat_member)
    user = message.left_chat_member.full_name
    notification_message = await message.answer(f"{user} Xayr!")
    await message.delete()
    await asyncio.sleep(10)  # 300 seconds = 5 minutes
    await notification_message.delete()    

@dp.message(and_f(F.reply_to_message,F.text=="/ban"))
async def ban_user(message:Message):
    await message.delete()
    user_id =  message.reply_to_message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhdan chiqarilib yuborildingiz.")
    await asyncio.sleep(10)  # 300 seconds = 5 minutes
    await notification_message.delete()

@dp.message(and_f(F.reply_to_message,F.text=="/unban"))
async def unban_user(message:Message):
    await message.delete()
    user_id =  message.reply_to_message.from_user.id
    await message.chat.unban_sender_chat(user_id)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga qaytishingiz mumkin.")
    await asyncio.sleep(10)  # 300 seconds = 5 minutes
    await notification_message.delete()
    

from time import time
@dp.message(and_f(F.reply_to_message,F.text=="/mute"))
async def mute_user(message:Message):
    await message.delete()
    user_id =  message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=False)
    
    until_date = int(time()) + 300  # 5 minutes block time
    await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} 5 minutga blocklandingiz")
    
    # Schedule the deletion of the notification message after 5 minutes
    await asyncio.sleep(20)  # 300 seconds = 5 minutes
    await notification_message.delete()


@dp.message(and_f(F.reply_to_message,F.text=="/unmute"))
async def unmute_user(message:Message):
    await message.delete()
    user_id =  message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=True)
    await message.chat.restrict(user_id=user_id,permissions=permission)
    notification_message = await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga yoza olasiz")

    await asyncio.sleep(10)  # 300 seconds = 5 minutes
    await notification_message.delete()



from time import time
xaqoratli_sozlar = {"tentak","jinni","axmoq","garang","dalbayob","ko't","dalban","iflos"}
@dp.message(and_f(F.chat.func(lambda chat: chat.type == "supergroup"),F.text ))
async def tozalash(message:Message):
    text = message.text
    print(text)
    for soz in xaqoratli_sozlar:
        print(soz,text.lower().find(soz))
        if text.lower().find(soz)!=-1 :
            user_id =  message.from_user.id
            until_date = int(time()) + 300 # 1minut guruhga yoza olmaydi
            permission = ChatPermissions(can_send_messages=False)
            await message.chat.restrict(user_id=user_id,permissions=permission,until_date=until_date)
            notification_message = await message.answer(text=f"{message.from_user.mention_html()} guruhda so'kinganingiz uchun 5 minutga blokga tushdingiz")
            await message.delete() 
            break
    await asyncio.sleep(20)  # 300 seconds = 5 minutes
    await notification_message.delete()


@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
            # await bot.restrict_chat_member(-1002143843957,6208545740,ChatPermissions(can_send_messages=True))
        except Exception as err:
        
            logging.exception(err)
            # @dp.startup()

   

#bot ishga tushganini xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)




async def main() -> None:
    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))
    await dp.start_polling(bot)
    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())
