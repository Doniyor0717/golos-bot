import os
import asyncio
import numpy as np
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from pydub import AudioSegment

API_TOKEN = '7665343622:AAEsZukl81sEw3MpLRpb6b3on9KiOT4D7HQ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def speed_change_natural(sound, speed=1.5):
    # Ovozni massivga o'tkazamiz
    samples = np.array(sound.get_array_of_samples())
    
    # Time stretching: Faqat vaqtni qisqartiramiz, tonni o'zgartirmaymiz
    # Bu oddiyroq usul, lekin burunduq effektini yo'qotadi
    indices = np.round(np.arange(0, len(samples), speed))
    indices = indices[indices < len(samples)].astype(int)
    new_samples = samples[indices]
    
    # Yangi audio ob'ektini yaratish
    return sound._spawn(new_samples)

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    file_id = message.voice.file_id
    input_path = f"in_{file_id}.ogg"
    output_path = f"out_{file_id}.ogg"

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, input_path)

    try:
        # Audioni yuklash
        audio = AudioSegment.from_file(input_path)
        
        # Tabiiy tezlashtirish (burunduq bo'lmasligi uchun)
        # speed_change funksiyasi pydub ichida tezlikni ton bilan birga o'zgartiradi
        # Biz uni kadrlar chastotasini to'g'irlash orqali bajaramiz
        fast_audio = audio.speedup(playback_speed=1.5, chunk_size=150, crossfade=25)

        # Saqlash
        fast_audio.export(output_path, format="ogg", codec="libopus")

        await message.reply_voice(FSInputFile(output_path), caption="1.5x (Tabiiy ovoz) ✅")

    except Exception as e:
        await message.reply(f"Xatolik: {e}")
    
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

