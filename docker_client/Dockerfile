# Используем базовый образ с Python
FROM python:3.10-slim

# Устанавливаем системные зависимости, включая Tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    libnss3 \
    libx11-6 \
    && apt-get clean

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости Python (если есть requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем клиентское приложение
CMD ["python", "clientdock.py"]
