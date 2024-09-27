from aiogram.types import Message
from loader import dp
from aiogram.filters import Command

#about commands
@dp.message(Command("about"))
async def about_commands(message:Message):
    await message.answer("Bot dan shikoyatingiz yoki taklifingiz bo'lsa📜\n👤Admin bilan bog'lanish tugmasini bosing\nYoki menu dan 📜 /xabar ni bosib murojatingizni yozing✅\nva xabaringizni yozib qoldiring✅Botdan foydalanish tartibi👇🏻\n👉🏻@hamster_sotib_oladigan_bot yozib o'z Hamster Kombat ingizni soting🙂")

