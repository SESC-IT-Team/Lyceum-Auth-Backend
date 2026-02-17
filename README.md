# Auth API

Микросервис авторизации: FastAPI, PostgreSQL, JWT (access + refresh).

## Запуск

```bash
cp .env.example .env
# Отредактируйте .env при необходимости

# Локально (uv)
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-compose up --build
```

После первого запуска создайте админа (один раз): см. раздел «Первый админ» ниже.

## API

- `POST /api/v1/auth/login` — логин (login, password) → access_token, refresh_token
- `POST /api/v1/auth/logout` — инвалидация refresh token (тело: refresh_token)
- `POST /api/v1/auth/refresh` — обмен refresh_token на новую пару токенов
- `POST /api/v1/auth/verify` — проверка access token (для других микросервисов), заголовок `Authorization: Bearer <token>`
- `GET /api/v1/auth/me` — текущий пользователь
- `GET/POST/PATCH/DELETE /api/v1/users` — CRUD пользователей (только админ)

## Примеры curl

Базовый URL (локально): `http://localhost:8000`.

### Логин

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"admin"}'
```

Ответ: `{"access_token":"...","refresh_token":"...","expires_in":1800,"token_type":"bearer"}`. Сохраните `access_token` и при необходимости `refresh_token`.

### Текущий пользователь (me)

```bash
export TOKEN="<access_token из login>"
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Верификация токена (для других сервисов)

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

Ответ: `{"user_id":"...","role":"admin","permissions":[...]}`.

### Logout

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"<refresh_token>\"}"
```

### Обновление токенов (refresh)

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"<refresh_token>\"}"
```

### Список пользователей (админ)

```bash
curl -s http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```

### Создание пользователя (админ)

```bash
curl -s -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "last_name":"Ivanov",
    "first_name":"Ivan",
    "middle_name":"Ivanovich",
    "login":"student1",
    "password":"secret",
    "role":"student",
    "gender":"male",
    "class_name":"10A",
    "graduation_year":2026
  }'
```

Роли: `admin`, `teacher`, `student`, `staff`. Пол: `male`, `female`.

### Обновление пользователя (админ)

```bash
curl -s -X PATCH "http://localhost:8000/api/v1/users/<user_uuid>" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Ivan Updated"}'
```

### Удаление пользователя (админ)

```bash
curl -s -X DELETE "http://localhost:8000/api/v1/users/<user_uuid>" \
  -H "Authorization: Bearer $TOKEN"
```

## Первый админ

CRUD пользователей доступен только админу. Первого админа нужно создать вручную (один раз).

Вариант 1 — скрипт (пароль по умолчанию `admin`):

```bash
uv run python -m scripts.create_admin
```

Вариант 2 — хеш пароля вручную и вставка в БД:

```bash
uv run python -c "
from passlib.context import CryptContext
p = CryptContext(schemes=['argon2'], deprecated='auto')
print(p.hash('your_password'))
"
# Затем в psql: INSERT INTO users (id, last_name, first_name, login, password_hash, role, gender) VALUES ...
```
