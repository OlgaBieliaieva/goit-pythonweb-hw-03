FROM python:3.11

# Встановлюємо робочу директорію в контейнері
WORKDIR /app

# Копіюємо файли проєкту в контейнер
COPY . .

# Встановлюємо Poetry
RUN pip install --upgrade pip && pip install poetry

# Встановлюємо залежності без установки самого проєкту
RUN poetry install --no-root

# Відкриваємо порт для сервера
EXPOSE 3000

# Запускаємо сервер
CMD ["poetry", "run", "python", "main.py"]