# Используем стабильный Python 3.11
FROM python:3.11-slim

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Команда для запуска бота
CMD ["python", "bot.py"]
