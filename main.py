import asyncio
import glob

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp
import instaloader
import os
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

load_dotenv()
# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Максимальный размер файла (50 МБ)
MAX_FILE_SIZE = 50 * 1024 * 1024
# Максимальная длительность (5 минут)
MAX_DURATION = 5 * 60

# Инициализация Instaloader с кастомным именем файла
L = instaloader.Instaloader(filename_pattern="{shortcode}")


# Функция для скачивания видео из Instagram
def download_instagram_video(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if not post.is_video:
            return None, "Это не видео или рилс!"
        L.download_post(post, target="downloads")
        filename = f"downloads/{shortcode}.mp4"
        if not os.path.exists(filename):
            return None, f"Файл {filename} не был создан."
        return filename, None
    except Exception as e:
        return None, str(e)


# Функция для скачивания видео из YouTube в отдельном потоке
def download_youtube_video_in_thread(ydl, url):
    ydl.download([url])


# Команда /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Отправь мне ссылку на YouTube-видео (до 5 минут) для скачивания в 360p или ссылку на Instagram-видео/рилс для скачивания."
    )


# Обработчик ссылок
@dp.message()
async def download_video(message: types.Message):
    url = message.text

    if (
        "youtube.com" not in url
        and "youtu.be" not in url
        and "instagram.com" not in url
    ):
        await message.answer(
            "Пожалуйста, отправь действительную ссылку на YouTube или Instagram."
        )
        return

    try:
        status_message = await message.answer("Проверяю ссылку.")

        # Создаём папку для Instagram, если её нет
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        # Обработка Instagram
        if "instagram.com" in url:
            for i in range(3):
                await asyncio.sleep(1)
                await bot.edit_message_text(
                    text=f"Проверяю Instagram{'..' * (i % 3 + 1)}",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )

            filename, error = download_instagram_video(url)
            if error:
                await bot.edit_message_text(
                    text=f"Ошибка: {error}",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )
                return

            if not os.path.exists(filename):
                await bot.edit_message_text(
                    text=f"Файл {filename} не найден после скачивания.",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )
                return

            # Проверка размера файла
            file_size = os.path.getsize(filename)
            if file_size > MAX_FILE_SIZE:
                os.remove(filename)
                await bot.edit_message_text(
                    text="Файл слишком большой для отправки в Telegram (больше 50 МБ).",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )
                return

            # Отправка видео
            video = types.FSInputFile(filename)
            await message.answer_video(
                video=video, caption="Вот твоё видео из Instagram!"
            )
            await bot.delete_message(
                chat_id=message.chat.id, message_id=status_message.message_id
            )

            # Удаляем все файлы, связанные с этим постом
            for file in glob.glob(f"downloads/{url.split('/')[-2]}*"):
                if os.path.exists(file):
                    os.remove(file)

        # Обработка YouTube
        else:
            ydl_opts = {
                "format": "18",  # Стандартный формат 360p (H.264 + AAC)
                "outtmpl": "%(title)s.%(ext)s",
                "merge_output_format": "mp4",
                "noplaylist": True,
                "retries": 5,
                "retry_sleep": 5,
            }

            for i in range(3):
                await asyncio.sleep(1)
                await bot.edit_message_text(
                    text=f"Проверяю YouTube{'..' * (i % 3 + 1)}",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for attempt in range(3):
                    try:
                        info = ydl.extract_info(url, download=False)
                        break
                    except yt_dlp.utils.DownloadError as e:
                        if "429" in str(e):
                            await bot.edit_message_text(
                                text="Слишком много запросов, жду 10 секунд...",
                                chat_id=message.chat.id,
                                message_id=status_message.message_id,
                            )
                            time.sleep(10)
                        else:
                            raise
                else:
                    await bot.edit_message_text(
                        text="Не удалось получить информацию о видео после нескольких попыток.",
                        chat_id=message.chat.id,
                        message_id=status_message.message_id,
                    )
                    return

                duration = info.get("duration", 0)
                video_title = info.get("title", "video")

                if duration > MAX_DURATION:
                    await bot.edit_message_text(
                        text=f"Видео слишком длинное ({duration // 60} мин). Максимум — 5 минут.",
                        chat_id=message.chat.id,
                        message_id=status_message.message_id,
                    )
                    return

                await bot.edit_message_text(
                    text="Загрузка видео.",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )

                with ThreadPoolExecutor() as executor:
                    download_task = executor.submit(
                        download_youtube_video_in_thread, ydl, url
                    )
                    while not download_task.done():
                        for i in range(3):
                            await asyncio.sleep(1)
                            await bot.edit_message_text(
                                text=f"Загрузка видео{'..' * (i % 3 + 1)}",
                                chat_id=message.chat.id,
                                message_id=status_message.message_id,
                            )
                    download_task.result()

                filename = ydl.prepare_filename(info)

            file_size = os.path.getsize(filename)
            if file_size > MAX_FILE_SIZE:
                os.remove(filename)
                await bot.edit_message_text(
                    text="Файл слишком большой для отправки в Telegram (больше 50 МБ).",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id,
                )
                return

            video = types.FSInputFile(filename)
            await message.answer_video(
                video=video, caption=f"Вот твоё видео: {video_title}"
            )
            await bot.delete_message(
                chat_id=message.chat.id, message_id=status_message.message_id
            )
            os.remove(filename)

    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# docker build -t youtube-insta-bot .
# docker run -d --name bot-container youtube-insta-bot
# docker run -d --name bot-container --restart unless-stopped -e BOT_TOKEN="8114901552:AAHiaLk8o50brY2vG0dUbaxh9H6E9h-qPWQ" youtube-insta-bot
# docker logs bot-container
