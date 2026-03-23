FROM python:3.11

# Установка зависимостей для сборки pydantic-core
RUN apt-get update && apt-get install -y build-essential curl

# Устанавливаем rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Рабочая папка
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Обновляем pip и ставим зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Запуск бота
CMD ["python", "bot.py"]
