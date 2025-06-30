FROM python:3.9-slim

WORKDIR /app

# Устанавливаем зависимости для SQLite и сборки
RUN apt-get update && apt-get install -y \
    sqlite3 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

CMD ["python", "bot.py"]