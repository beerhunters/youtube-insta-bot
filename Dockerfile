# Используем официальный образ Python 3.11 на основе slim (лёгкий вариант)
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости, включая ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей (если есть requirements.txt) или устанавливаем их напрямую
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт бота
COPY main.py ./

# Указываем команду для запуска бота
CMD ["python", "main.py"]