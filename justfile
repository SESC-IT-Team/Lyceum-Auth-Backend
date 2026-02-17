# Команды для управления проектом Auth Service

# Установка зависимостей
install:
    uv sync

# Запуск проекта локально (требует запущенную БД)
run:
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Запуск проекта через Docker Compose
up:
    docker-compose up --build

# Запуск проекта в фоновом режиме
up-d:
    docker-compose up -d --build

# Остановка проекта
down:
    docker-compose down

# Остановка проекта с удалением volumes
down-v:
    docker-compose down -v

# Просмотр логов
logs:
    docker-compose logs -f auth-api

# Выполнение миграций базы данных
migrate:
    uv run alembic upgrade head

# Создание новой миграции
migration name:
    uv run alembic revision --autogenerate -m "{{name}}"

# Откат последней миграции
rollback:
    uv run alembic downgrade -1

# Запуск тестов
test:
    uv run pytest

# Запуск тестов с покрытием
test-cov:
    uv run pytest --cov=app --cov-report=html

# Форматирование кода
format:
    uv run ruff format .

# Проверка кода линтером
lint:
    uv run ruff check .

# Форматирование и проверка
check:
    just format && just lint

# Создание .env файла из примера (если не существует)
env-setup:
    @if [ ! -f .env ]; then \
        cp .env.example .env && \
        echo ".env файл создан из .env.example"; \
    else \
        echo ".env файл уже существует"; \
    fi

# Полная настройка проекта (установка зависимостей + создание .env)
setup: env-setup install
    @echo "Проект настроен. Используйте 'just up' для запуска через Docker или 'just run' для локального запуска."

# Очистка кэша Python
clean:
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
    @echo "Кэш Python очищен"

# Просмотр статуса сервисов
status:
    docker-compose ps

# Перезапуск сервисов
restart:
    docker-compose restart

# Выполнение команды в контейнере auth-api
exec cmd:
    docker-compose exec auth-api {{cmd}}

# Открытие shell в контейнере auth-api
shell:
    docker-compose exec auth-api /bin/bash

# Просмотр переменных окружения
env:
    @cat .env 2>/dev/null || echo ".env файл не найден"
