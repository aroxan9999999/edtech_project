# EdTech Project

Этот проект представляет собой образовательную платформу с использованием Django для бэкенда и Aiogram для чат-бота в Telegram.

## Установка

### Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий:

```bash
git clone https://github.com/aroxan9999999/edtech_project
cd edtech_project
```

### Шаг 2: Создание виртуального окружения

Создайте виртуальное окружение и активируйте его:

```bash
python -m venv .venv
source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

Установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

Создайте файл `.env` на основе шаблона `.env.template` и заполните его необходимыми значениями:

```env
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=edtech_db
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

SECRET_KEY=your_secret_key
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

API_TOKEN=your_telegram_bot_token
```

### Шаг 5: Применение миграций

Примените миграции для создания необходимых таблиц в базе данных:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Шаг 6: Запуск сервера

Запустите сервер Django:

```bash
python manage.py runserver
```

### Шаг 7: Запуск чат-бота

В отдельном терминале запустите чат-бота:

```bash
python bot.py
```

## Структура проекта

- `edtech_project/` - Корневой каталог проекта
  - `edtech_project/settings.py` - Основные настройки Django
  - `edtech_project/urls.py` - Маршрутизация URL
  - `edtech_project/wsgi.py` - Настройки для WSGI сервера
  - `courses/` - Приложение для управления курсами
    - `models.py` - Модели данных
    - `views.py` - Представления
  - `bot.py` - Чат-бот на основе Aiogram

## Используемые технологии

- Python
- Django
- Aiogram
- PostgreSQL


