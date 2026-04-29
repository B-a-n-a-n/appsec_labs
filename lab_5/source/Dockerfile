# Этап 1: Сборка (Builder)
FROM python:3.11-slim AS builder
WORKDIR /app

# Устанавливаем системные зависимости для сборки pygame
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Собираем wheel-пакеты
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-slim
WORKDIR /app

# Нам нужны только базовые библиотеки SDL2 для запуска (без gcc)
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем собранные пакеты
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY pygamesteel_from_lab_2.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "pygamesteel_from_lab_2.py"]
