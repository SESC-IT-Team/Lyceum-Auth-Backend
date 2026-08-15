# Lyceum Users API

Backend-сервис для централизованного управления **пользователями и связанными с ними данными** экосистемы СУНЦ УрФУ.

Сервис предоставляет REST API для:

- управления пользователями (создание, чтение, обновление, удаление);
- поиска и фильтрации пользователей по множеству параметров;
- управления связями **родитель ↔ ребёнок**;
- управления участниками подразделений;
- получения информации о текущем авторизованном пользователе;
- синхронизации учётной записи пользователя с **Authentik** (внешний IdP).

> **Важно:** сервис не является Identity Provider и не реализует собственный механизм аутентификации. Authentik используется как внешняя система управления учётными записями, а Users API отвечает исключительно за доменные данные пользователей. Проверка токенов выполняется через `sesc-auth-sdk` с помощью JWKS.

---

## Содержание

- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Основные сущности](#основные-сущности)
- [Схема базы данных](#схема-базы-данных)
- [API](#api)
  - [Users API](#users-api)
  - [Departments API](#departments-api)
  - [Healthcheck](#healthcheck)
- [Авторизация](#авторизация)
- [Переменные окружения](#переменные-окружения)
- [Запуск](#запуск)
- [Docker](#docker)
- [Миграции](#миграции)
- [Структура проекта](#структура-проекта)
- [Документация API (Swagger)](#документация-api-swagger)

---

## Архитектура

Сервис реализован по принципам **Clean Architecture** с разделением на четыре слоя:

```text
┌──────────────────────────────────────────────┐
│                 Presentation                 │
│                                              │
│        FastAPI / Routers / Schemas           │
└───────────────────────┬──────────────────────┘
                        │
┌───────────────────────▼──────────────────────┐
│                 Application                  │
│                                              │
│       UserService / DepartmentService        │
│           AuthentikService                   │
└───────────────────────┬──────────────────────┘
                        │
┌───────────────────────▼──────────────────────┐
│                    Domain                    │
│                                              │
│   User / DepartmentMember / Filters /        │
│   PaginationAndSorting / Enums               │
└───────────────────────┬──────────────────────┘
                        │
┌───────────────────────▼──────────────────────┐
│                Infrastructure                │
│                                              │
│   PostgreSQL / SQLAlchemy / Repositories     │
└──────────────────────────────────────────────┘

                 ┌─────────────────┐
                 │    Authentik    │
                 │  External IdP   │
                 └────────┬────────┘
                          │ account sync
                          │ JWKS / token validation
                          ▼
                   Users API (this)
```

**Слои и их ответственность:**

| Слой | Назначение |
|---|---|
| `presentation` | HTTP-роутеры, Pydantic-схемы, dependency injection |
| `application` | Бизнес-логика, оркестрация сервисов, транзакции |
| `domain` | Доменные сущности, перечисления, правила (без зависимостей от фреймворков) |
| `infrastructure` | ORM-модели, репозитории, подключение к БД |

---

## Технологический стек

| Компонент | Технология |
|---|---|
| Язык | Python 3.13+ |
| Веб-фреймворк | FastAPI 0.115+ |
| ASGI-сервер | Uvicorn |
| ORM | SQLAlchemy 2.x (async) |
| База данных | PostgreSQL 15 |
| Async-драйвер | asyncpg |
| Миграции | Alembic |
| Валидация | Pydantic 2.x |
| Аутентификация | `sesc-auth-sdk` + Authentik (JWKS) |
| Rate limiting | SlowAPI |
| Контейнеризация | Docker / Docker Compose |
| Менеджер зависимостей | uv |
| Тесты | pytest + pytest-asyncio |
| Анализ кода | Pyrefly |

**`sesc-auth-sdk`** — внутренняя библиотека команды ([GitHub](https://github.com/SESC-IT-Team/Lyceum-Auth-SDK)), предоставляющая:
- `LyceumAuth` — базовый класс проверки токена;
- `TokenValidationSettings` — настройки валидации JWT;
- `JWKSManager` — менеджер ключей JWKS;
- Перечисления `Role`, `Gender`, `Scope`, `Department`, `DepartmentMemberPosition`;
- `AccessTokenPayload` — схема payload токена.

---

## Основные сущности

### User

Пользователь системы. Хранится в базе данных Users API и синхронизируется с Authentik.

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `id` | UUID | — | Первичный ключ (auto) |
| `last_name` | string | Да | Фамилия |
| `first_name` | string | Да | Имя |
| `middle_name` | string | Нет | Отчество |
| `full_name` | string | — | Вычисляется: `last_name first_name middle_name` |
| `login` | string | Да | Уникальный логин |
| `roles` | list[Role] | Да | Роли: `admin`, `teacher`, `student`, `parent`, `staff`, `guest`, `graduate` |
| `gender` | Gender | Да | `male` / `female` |
| `birthday` | date | Нет | Дата рождения |
| `grade` | int (8–11) | Нет | Класс (для учеников) |
| `letter` | string (А–Я) | Нет | Буква класса (кириллица) |
| `class_name` | string | — | Вычисляется: `grade + letter`, например `10А` |
| `graduation_year` | int | Нет | Год выпуска |
| `lives_in_dormitory` | bool | Да | Проживание в общежитии |
| `created_at` | datetime | — | Время создания (UTC) |
| `updated_at` | datetime | — | Время последнего обновления (UTC) |

Пример объекта:

```json
{
  "id": "2c8d7b8e-3c0d-4b4f-9f4e-123456789abc",
  "last_name": "Иванов",
  "first_name": "Иван",
  "middle_name": "Иванович",
  "full_name": "Иванов Иван Иванович",
  "gender": "male",
  "roles": ["student"],
  "lives_in_dormitory": true,
  "birthday": "2009-05-12",
  "grade": 10,
  "letter": "А",
  "class_name": "10А",
  "graduation_year": 2027,
  "login": "ivanov",
  "created_at": "2026-02-17T10:20:00Z",
  "updated_at": "2026-05-01T12:00:00Z"
}
```

### DepartmentMember

Участие пользователя в подразделении. Один пользователь может быть участником нескольких подразделений.

| Поле | Тип | Описание |
|---|---|---|
| `user` | User | Данные пользователя |
| `department` | Department | Подразделение (enum, см. [допустимые значения](#departments-api)) |
| `position` | DepartmentMemberPosition | `admin` или `worker` |
| `created_at` | datetime | Время добавления |
| `updated_at` | datetime | Время последнего обновления |

Ограничение: один пользователь имеет **не более одной позиции** в одном подразделении.

---

## Схема базы данных

### Таблица `users`

| Колонка | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | UUID | PK, default uuid4 | Первичный ключ |
| `pk` | INTEGER | NOT NULL | ID пользователя в Authentik |
| `last_name` | VARCHAR(255) | NOT NULL | Фамилия |
| `first_name` | VARCHAR(255) | NOT NULL | Имя |
| `middle_name` | VARCHAR(255) | NULLABLE | Отчество |
| `full_name` | VARCHAR(255) | NULLABLE | Денормализованное полное имя |
| `roles` | Role[] | NOT NULL | Массив ролей (ARRAY enum) |
| `gender` | Gender | NOT NULL | Пол |
| `birthday` | DATE | NULLABLE | Дата рождения |
| `grade` | INTEGER | NULLABLE, CHECK 8–11 | Класс |
| `letter` | VARCHAR(10) | NULLABLE, CHECK `^[А-Я]$` | Буква класса |
| `class_name` | VARCHAR(64) | NULLABLE | Денормализованное название класса |
| `graduation_year` | INTEGER | NULLABLE | Год выпуска |
| `login` | VARCHAR(255) | UNIQUE, INDEX | Логин |
| `lives_in_dormitory` | BOOLEAN | NOT NULL | Общежитие |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Время создания |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | Время обновления |

### Таблица `department_members`

| Колонка | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | UUID | PK, default uuid4 | Первичный ключ |
| `user_id` | UUID | FK → users.id CASCADE | Пользователь |
| `department` | Department | NOT NULL | Подразделение |
| `position` | DepartmentMemberPosition | NOT NULL | Позиция (`admin`/`worker`) |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Время добавления |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | Время обновления |

Уникальное ограничение: `UNIQUE(user_id, department)` — один пользователь, одна позиция в подразделении.

### Таблица `parent_child`

Таблица связи «родитель – ребёнок» (many-to-many).

| Колонка | Тип | Ограничения | Описание |
|---|---|---|---|
| `parent_id` | UUID | PK, FK → users.id CASCADE | Родитель |
| `child_id` | UUID | PK, FK → users.id CASCADE | Ребёнок |

Ограничение: `CHECK(parent_id != child_id)` — запрет самоссылки.

---

## API

Все эндпоинты находятся под базовым префиксом `/api/v1`.

### Условные обозначения

В колонке **Доступ** указаны необходимые scope и роль через `+`:

- `scope` — OAuth2 scope из токена;
- `role` — роль пользователя, проверяемая в базе данных.

---

## Users API

### Текущий пользователь

#### `GET /api/v1/users/me`

Возвращает данные текущего авторизованного пользователя.

| | |
|---|---|
| **Доступ** | `profile` |
| **Ответ** | `UserResponse` |

---

#### `GET /api/v1/users/me/children`

Возвращает список детей текущего пользователя.

| | |
|---|---|
| **Доступ** | `auth:children:read` |
| **Параметры** | [пагинация, сортировка, фильтрация](#параметры-пагинации) |
| **Ответ** | `UserListResponse` |

---

#### `GET /api/v1/users/me/children/{child_id}`

Возвращает конкретного ребёнка текущего пользователя.

| | |
|---|---|
| **Доступ** | `auth:children:read` |
| **Ответ** | `UserResponse` |

---

### Список пользователей

#### `GET /api/v1/users`

Возвращает постраничный список пользователей с поддержкой фильтрации и сортировки.

| | |
|---|---|
| **Доступ** | `auth:users:read` + `admin` |
| **Параметры** | [пагинация, сортировка, фильтрация](#параметры-пагинации) |
| **Ответ** | `UserListResponse` |

```http
GET /api/v1/users?limit=20&offset=0&sort_by=created_at&order=descending
```

Ответ:

```json
{
  "users": [...],
  "total": 100,
  "offset": 0,
  "limit": 20
}
```

---

### Параметры пагинации

| Параметр | По умолчанию | Описание |
|---|---|---|
| `offset` | `0` | Смещение (≥ 0) |
| `limit` | `20` | Размер страницы (≥ 1) |
| `sort_by` | `created_at` | Поле сортировки |
| `order` | `descending` | `ascending` или `descending` |

### Поля сортировки пользователей (`sort_by`)

```
first_name   middle_name   last_name   full_name
grade        letter        class_name  graduation_year
login        gender        lives_in_dormitory
created_at   updated_at
```

### Параметры фильтрации пользователей

| Параметр | Тип | Описание |
|---|---|---|
| `ids` | UUID[] | Фильтр по списку UUID |
| `search` | string | Поиск по логину, имени, фамилии, отчеству (ILIKE) |
| `gender` | `male`\|`female` | Пол |
| `roles` | Role[] | Роли (пересечение массивов) |
| `grades` | int[] | Классы/параллели |
| `letters` | string[] | Буквы классов |
| `graduation_years` | int[] | Годы выпуска |
| `class_names` | string[] | Названия классов (например `10А`) |
| `lives_in_dormitory` | bool | Проживание в общежитии |

Фильтры комбинируются. Примеры:

```http
GET /api/v1/users?roles=student&grades=10&letters=А
GET /api/v1/users?search=Иван&lives_in_dormitory=true
GET /api/v1/users?ids=uuid1&ids=uuid2
```

---

### Создание пользователя

#### `POST /api/v1/users`

Создаёт пользователя в базе данных и синхронизирует учётную запись с Authentik.

| | |
|---|---|
| **Доступ** | `auth:users:create` + `admin` |
| **Тело** | `UserCreate` |
| **Ответ** | `201 UserResponse` |

**Тело запроса `UserCreate`:**

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `last_name` | string | Да | Фамилия |
| `first_name` | string | Да | Имя |
| `middle_name` | string | Нет | Отчество |
| `login` | string | Да | Уникальный логин |
| `roles` | Role[] | Да | Роли |
| `gender` | Gender | Да | Пол |
| `lives_in_dormitory` | bool | Нет (false) | Общежитие |
| `grade` | int | Нет | Класс (8–11) |
| `letter` | string | Нет | Буква класса (кириллица А–Я) |
| `graduation_year` | int | Нет | Год выпуска |
| `birthday` | date | Нет | Дата рождения |

```json
{
  "last_name": "Иванов",
  "first_name": "Иван",
  "middle_name": "Иванович",
  "login": "ivanov",
  "roles": ["student"],
  "gender": "male",
  "grade": 10,
  "letter": "А",
  "graduation_year": 2027,
  "birthday": "2009-05-12",
  "lives_in_dormitory": true
}
```

При создании пользователя:
1. Проверяется уникальность логина.
2. Создаётся учётная запись в Authentik.
3. Сохраняются доменные данные в PostgreSQL.
4. При ошибке на любом шаге выполняется откат.

---

### Получение пользователя

#### `GET /api/v1/users/{user_id}`

Возвращает пользователя по UUID.

| | |
|---|---|
| **Доступ** | `auth:users:read` + `admin` |
| **Ответ** | `UserResponse` |

---

### Обновление пользователя

#### `PATCH /api/v1/users/{user_id}`

Обновляет доменные данные пользователя. Все поля необязательны.

| | |
|---|---|
| **Доступ** | `auth:users:read`, `auth:users:update` + `admin` |
| **Тело** | `UserInfoUpdate` |
| **Ответ** | `UserResponse` |

**Тело запроса `UserInfoUpdate`** (все поля необязательны):

```json
{
  "first_name": "Пётр",
  "grade": 11,
  "letter": "Б",
  "lives_in_dormitory": false
}
```

---

### Обновление пароля

#### `PUT /api/v1/users/{user_id}/password`

Устанавливает новый пароль для учётной записи пользователя в Authentik.

| | |
|---|---|
| **Доступ** | `auth:users:update` + `admin` |
| **Тело** | `UserPasswordUpdate` |
| **Ответ** | `204 No Content` |

```json
{
  "password": "new-secure-password"
}
```

> Пароль не хранится в доменной модели — только в Authentik.

---

### Удаление пользователя

#### `DELETE /api/v1/users/{user_id}`

Удаляет пользователя из базы данных и из Authentik.

| | |
|---|---|
| **Доступ** | `auth:users:delete` + `admin` |
| **Ответ** | `204 No Content` |

---

### Родители и дети

Отношение «родитель – ребёнок» — many-to-many между пользователями.

```text
Parent
  ├── Child 1
  ├── Child 2
  └── Child 3
```

#### `GET /api/v1/users/{user_id}/parents`

Возвращает список родителей пользователя. Поддерживаются пагинация, сортировка, фильтрация.

| | |
|---|---|
| **Доступ** | `auth:users:read` + `admin` |
| **Ответ** | `UserListResponse` |

---

#### `PATCH /api/v1/users/{user_id}/parents`

Добавляет и/или удаляет связи с родителями.

| | |
|---|---|
| **Доступ** | `auth:users:update` + `admin` |
| **Ответ** | `204 No Content` |

```json
{
  "ids_to_add": ["uuid-parent-1"],
  "ids_to_delete": ["uuid-old-parent"]
}
```

---

#### `GET /api/v1/users/{user_id}/children`

Возвращает список детей пользователя. Поддерживаются пагинация, сортировка, фильтрация.

| | |
|---|---|
| **Доступ** | `auth:users:read` + `admin` |
| **Ответ** | `UserListResponse` |

---

#### `PATCH /api/v1/users/{user_id}/children`

Добавляет и/или удаляет связи с детьми.

| | |
|---|---|
| **Доступ** | `auth:users:update` + `admin` |
| **Ответ** | `204 No Content` |

```json
{
  "ids_to_add": ["uuid-child-1"],
  "ids_to_delete": ["uuid-old-child"]
}
```

---

### Сводная таблица Users API

| Метод | Эндпоинт | Scope | Роль | Описание |
|---|---|---|---|---|
| GET | `/users/me` | `profile` | — | Текущий пользователь |
| GET | `/users/me/children` | `auth:children:read` | — | Дети текущего пользователя |
| GET | `/users/me/children/{child_id}` | `auth:children:read` | — | Конкретный ребёнок |
| GET | `/users` | `auth:users:read` | `admin` | Список пользователей |
| POST | `/users` | `auth:users:create` | `admin` | Создать пользователя |
| GET | `/users/{user_id}` | `auth:users:read` | `admin` | Получить пользователя |
| PATCH | `/users/{user_id}` | `auth:users:read`, `auth:users:update` | `admin` | Обновить пользователя |
| PUT | `/users/{user_id}/password` | `auth:users:update` | `admin` | Обновить пароль |
| DELETE | `/users/{user_id}` | `auth:users:delete` | `admin` | Удалить пользователя |
| GET | `/users/{user_id}/parents` | `auth:users:read` | `admin` | Родители пользователя |
| PATCH | `/users/{user_id}/parents` | `auth:users:update` | `admin` | Обновить родителей |
| GET | `/users/{user_id}/children` | `auth:users:read` | `admin` | Дети пользователя |
| PATCH | `/users/{user_id}/children` | `auth:users:update` | `admin` | Обновить детей |

---

## Departments API

Все эндпоинты подразделений находятся под префиксом `/api/v1/departments/{department_name}`.

`{department_name}` — это **строгий enum** (`Department`), принимает только следующие значения:

| Значение | Описание |
|---|---|
| `academic_department` | Учебный отдел |
| `olympiad_support_department` | Отдел сопровождения олимпиад |
| `medical_station` | Медпункт |
| `educational_department` | Воспитательный отдел |
| `library` | Библиотека |
| `it_department` | IT-отдел |
| `laboratory_of_tech_teaching_aids` | Лаборатория технических средств обучения |
| `competitive_selection_department` | Отдел конкурсного отбора |
| `additional_education_department` | Отдел дополнительного образования |
| `dormitory` | Общежитие |

Пример для IT-отдела:

```
/api/v1/departments/it_department/members
```

### Список участников

#### `GET /api/v1/departments/{department_name}/members`

Возвращает участников подразделения.

| | |
|---|---|
| **Доступ** | `auth:users:read` + `admin` |
| **Параметры** | пагинация, сортировка, фильтрация пользователей + `positions` |
| **Ответ** | `DepartmentMemberListResponse` |

Дополнительный параметр фильтрации:

| Параметр | Тип | Описание |
|---|---|---|
| `positions` | DepartmentMemberPosition[] | Фильтр по позиции: `admin`, `worker` |

### Поля сортировки участников подразделения

```
position        created_at       updated_at
user.first_name  user.middle_name  user.last_name  user.full_name
user.grade       user.letter       user.class_name user.graduation_year
user.login       user.gender       user.lives_in_dormitory
user.created_at  user.updated_at
```

Ответ:

```json
{
  "members": [
    {
      "user": { ...UserResponse },
      "position": "worker",
      "created_at": "2026-03-01T10:00:00Z",
      "updated_at": "2026-05-01T12:00:00Z"
    }
  ],
  "total": 5,
  "offset": 0,
  "limit": 20
}
```

---

#### `GET /api/v1/departments/{department_name}/members/me`

Возвращает информацию о текущем авторизованном пользователе в подразделении.

| | |
|---|---|
| **Доступ** | `profile` |
| **Ответ** | `DepartmentMemberResponse` |

---

#### `GET /api/v1/departments/{department_name}/members/workers`

Возвращает пользователей подразделения с позицией `worker`.

| | |
|---|---|
| **Доступ** | `auth:users:read` + позиция `admin` в данном подразделении |
| **Параметры** | пагинация ([поля сортировки — пользовательские](#поля-сортировки-пользователей-sort_by)), фильтрация пользователей |
| **Ответ** | `UserListResponse` |

> Доступ проверяется через `require_department_admin`: текущий пользователь должен быть участником подразделения с позицией `DepartmentMemberPosition.admin`. Это **позиция внутри подразделения**, не системная роль `admin`.

---

#### `GET /api/v1/departments/{department_name}/members/{user_id}`

Возвращает конкретного участника подразделения.

| | |
|---|---|
| **Доступ** | `auth:users:read` + `admin` |
| **Ответ** | `DepartmentMemberResponse` |

---

#### `PUT /api/v1/departments/{department_name}/members/{user_id}`

Добавляет пользователя в подразделение или изменяет его позицию (upsert).

| | |
|---|---|
| **Доступ** | `auth:users:update` + `admin` |
| **Тело** | `SetDepartmentMemberPositionRequest` |
| **Ответ** | `204 No Content` |

```json
{
  "position": "worker"
}
```

---

#### `DELETE /api/v1/departments/{department_name}/members/{user_id}`

Удаляет пользователя из подразделения.

| | |
|---|---|
| **Доступ** | `auth:users:update` + `admin` |
| **Ответ** | `204 No Content` |

---

### Сводная таблица Departments API

| Метод | Эндпоинт | Scope | Роль | Описание |
|---|---|---|---|---|
| GET | `/departments/{dept}/members` | `auth:users:read` | `admin` | Список участников |
| GET | `/departments/{dept}/members/me` | `profile` | — | Текущий пользователь в подразделении |
| GET | `/departments/{dept}/members/workers` | `auth:users:read` | позиция `admin` в подразделении | Список работников |
| GET | `/departments/{dept}/members/{user_id}` | `auth:users:read` | `admin` | Конкретный участник |
| PUT | `/departments/{dept}/members/{user_id}` | `auth:users:update` | `admin` | Добавить/изменить позицию |
| DELETE | `/departments/{dept}/members/{user_id}` | `auth:users:update` | `admin` | Удалить участника |

---

## Healthcheck

#### `GET /health`

Проверка работоспособности сервиса. Авторизация не требуется.

```bash
curl http://localhost:8000/health
```

---

## Авторизация

Users API не является Identity Provider. Каждый запрос должен содержать **access token**, выданный Authentik.

### Поток авторизации

```text
┌───────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Access Token │──────▶│  sesc-auth-sdk   │──────▶│   Users API      │
│ (Bearer JWT)  │       │ JWKS validation  │       │                  │
└───────────────┘       └────────┬─────────┘       │  fetch User      │
                                 │ user_id (sub)   │  check roles     │
                                 └────────────────▶│  check scopes    │
                                                   └──────────────────┘
```

1. Клиент передаёт Bearer-токен в заголовке `Authorization`.
2. `sesc-auth-sdk` проверяет подпись токена через JWKS (публичные ключи Authentik).
3. Из payload извлекается `sub` (user UUID).
4. Пользователь загружается из базы данных.
5. Проверяются требуемые роли и scopes.

### OAuth2 Scopes

| Scope | Описание |
|---|---|
| `profile` | Базовый доступ к собственным данным |
| `auth:users:read` | Чтение данных других пользователей |
| `auth:users:create` | Создание пользователей |
| `auth:users:update` | Обновление данных пользователей |
| `auth:users:delete` | Удаление пользователей |
| `auth:children:read` | Чтение данных собственных детей |

### Роли

| Роль | Описание |
|---|---|
| `admin` | Полный доступ к управлению пользователями |
| `teacher` | Преподаватель |
| `student` | Ученик |
| `parent` | Родитель |
| `staff` | Сотрудник |
| `guest` | Гость |
| `graduate` | Выпускник |

### Rate Limiting

Сервис использует `slowapi` для ограничения частоты запросов по IP-адресу клиента.

---

## Переменные окружения

Настройки хранятся в файле `.env`. Шаблон — `.env.example`.

### База данных

| Переменная | Тип | По умолчанию | Описание |
|---|---|---|---|
| `POSTGRES_HOST` | string | `postgres` | Хост PostgreSQL |
| `POSTGRES_PORT` | int | `5432` | Порт PostgreSQL |
| `POSTGRES_USER` | string | `postgres` | Пользователь БД |
| `POSTGRES_PASSWORD` | string | `postgres` | Пароль БД |
| `POSTGRES_DB` | string | `auth` | Имя базы данных |

### Аутентификация и Authentik

| Переменная | Тип | По умолчанию | Описание |
|---|---|---|---|
| `AUTHENTIK_URL` | string | `http://authentik:9000` | URL Authentik |
| `SA_AUTH_ADMIN_APP_API_TOKEN` | string | **(обязательно)** | API-токен сервисного аккаунта для работы с Authentik API |
| `USERS_PATH` | string | `''` | Путь пользователей в Authentik |
| `ALLOWED_ISSUERS` | JSON array | — | Список допустимых issuer для JWT-токенов |

### Приложение

| Переменная | Тип | По умолчанию | Описание |
|---|---|---|---|
| `ALLOWED_ORIGINS` | JSON array | `["http://localhost:8000"]` | CORS-разрешённые источники |
| `COOKIE_SECURE` | bool | `false` | Флаг `Secure` для cookies |
| `COOKIE_SAMESITE` | `lax`\|`none`\|`strict` | `lax` | Политика `SameSite` для cookies |
| `COOKIE_DOMAIN` | string | `.localhost` | Домен cookies |
| `ROOT_PATH` | string | `/` | Корневой путь FastAPI (для работы за reverse proxy) |

### Администратор

| Переменная | Тип | По умолчанию | Описание |
|---|---|---|---|
| `ADMIN_LOGIN` | string | `admin` | Логин администратора по умолчанию |
| `ADMIN_PASSWORD` | string | `admin` | Пароль администратора по умолчанию |

> При первом запуске сервис автоматически создаёт администратора с указанными логином и паролем, если такой пользователь ещё не существует.

### Деплой (опционально, для Traefik)

| Переменная | Тип | Описание |
|---|---|---|
| `DOMAIN` | string | Домен для Traefik-роутинга |
| `TLS_RESOLVER` | string | Резолвер TLS (`letsencrypt` или `selfsigned`) |

---

## Запуск

### Требования

- Python 3.13+
- PostgreSQL 15+
- [`uv`](https://docs.astral.sh/uv/) — менеджер зависимостей

Для Docker: Docker + Docker Compose.

### Локальный запуск

```bash
git clone https://github.com/SESC-IT-Team/Lyceum-Auth-Backend.git
cd Lyceum-Auth-Backend
```

Установка зависимостей:

```bash
uv sync
```

Создание конфигурации:

```bash
cp .env.example .env
```

Отредактируйте `.env`: укажите параметры подключения к PostgreSQL, URL Authentik и обязательный `SA_AUTH_ADMIN_APP_API_TOKEN`.

Применение миграций:

```bash
uv run alembic upgrade head
```

Запуск сервера:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервис будет доступен на `http://localhost:8000`.

---

## Docker

### Сборка и запуск (разработка)

```bash
docker compose -f dev-docker-compose.yml up --build
```

Порты в dev-режиме: `8000` (API), `5432` (PostgreSQL).

### Продакшн

```bash
cp .env.example .env
# отредактировать .env

docker compose up -d --build
```

Продакшн-конфиг (`docker-compose.yml`) включает:
- Интеграцию с **Traefik** (path routing `/auth-back`, TLS);
- Подключение к внешним сетям `traefik-public` и `logging`;
- Health check: `curl http://localhost:8000/health`.

### Структура сервисов

| Сервис | Образ | Описание |
|---|---|---|
| `auth-api` | Build from Dockerfile | FastAPI-приложение |
| `postgres` | `postgres:15-alpine` | База данных |

### Dockerfile

Образ собирается на базе `python:3.13.14-alpine`. Зависимости устанавливаются через `uv`. При старте контейнера (`entrypoint.sh`) автоматически выполняются миграции Alembic, затем запускается Uvicorn.

---

## Миграции

Применить все миграции:

```bash
uv run alembic upgrade head
```

Создать новую миграцию (автогенерация из изменений моделей):

```bash
uv run alembic revision --autogenerate -m "описание изменения"
```

Откатить последнюю миграцию:

```bash
uv run alembic downgrade -1
```

Посмотреть текущую версию:

```bash
uv run alembic current
```

---

## Структура проекта

```text
Lyceum-Auth-Backend/
├── app/
│   ├── main.py                    # Точка входа FastAPI, lifespan, middleware
│   ├── config.py                  # Settings (pydantic BaseSettings)
│   │
│   ├── application/               # Бизнес-логика
│   │   ├── interfaces/            # Абстрактные интерфейсы репозиториев
│   │   └── services/
│   │       ├── user_service.py    # Управление пользователями
│   │       ├── department_service.py  # Управление подразделениями
│   │       └── authentik_service.py   # Интеграция с Authentik API
│   │
│   ├── domain/                    # Доменный слой (без внешних зависимостей)
│   │   ├── entities/              # User, DepartmentMember, AuthentikUser,
│   │   │                          # UserFilters, PaginationAndSorting
│   │   └── enums/                 # UserSortableField, DepartmentMemberSortableField,
│   │                              # SortingOrder
│   │
│   ├── infrastructure/            # Инфраструктурный слой
│   │   ├── database.py            # Async engine, session factory
│   │   ├── models/                # SQLAlchemy ORM-модели
│   │   └── repositories/          # Реализации репозиториев + helpers
│   │       └── helpers/           # Фильтрация, сортировка, маппинг полей
│   │
│   └── presentation/              # HTTP-слой
│       ├── api/v1/
│       │   ├── user.py            # Роутер /api/v1/users
│       │   └── department.py      # Роутер /api/v1/departments
│       ├── schemas/               # Pydantic-схемы запросов и ответов
│       └── dependencies.py        # DI: Auth, сервисы, репозитории
│
├── migrations/                    # Alembic-миграции
│   ├── env.py
│   └── versions/
│
├── scripts/
│   └── create_admin.py            # Создание администратора при старте
│
├── Dockerfile
├── docker-compose.yml             # Продакшн
├── dev-docker-compose.yml         # Разработка
├── entrypoint.sh                  # Миграции + запуск uvicorn
├── alembic.ini
└── pyproject.toml
```

### Описание слоёв

#### `domain`

Чистые Python-объекты без зависимостей от фреймворков. Содержит:

- `User`, `DepartmentMember`, `AuthentikUser` — доменные сущности;
- `UserFilters`, `DepartmentMemberFilters` — параметры фильтрации;
- `PaginationAndSorting[T]` — пагинация и сортировка;
- `UserSortableField`, `DepartmentMemberSortableField`, `SortingOrder` — перечисления.

#### `application`

Оркестрирует бизнес-операции:

- `UserService` — CRUD пользователей, управление связями родитель–ребёнок, транзакционный откат при ошибках;
- `DepartmentService` — CRUD участников подразделений, upsert-логика;
- `AuthentikService` — HTTP-интеграция с Authentik REST API.

#### `infrastructure`

- `UserRepository` / `DepartmentRepository` — реализации репозиториев на SQLAlchemy;
- Вспомогательные функции: `apply_user_filters_to_query`, `apply_pagination_and_sorting`, `map_sortable_field`;
- Маппинг ORM-моделей в доменные сущности (`model_to_entity`).

#### `presentation`

- FastAPI-роутеры с dependency injection;
- Pydantic-схемы: `UserCreate`, `UserInfoUpdate`, `UserResponse`, `UserListResponse`, `UserPasswordUpdate`, `SetDepartmentMemberPositionRequest`, `DepartmentMemberResponse`, `DepartmentMemberListResponse`;
- `Auth` — кастомный класс поверх `LyceumAuth` из SDK, загружает пользователя из БД и проверяет роли.

---

## Документация API (Swagger)

После запуска приложения интерактивная документация доступна по адресам:

| Интерфейс | URL |
|---|---|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

---

## Лицензия

Проект является частью IT-инфраструктуры **СУНЦ УрФУ**.

Условия использования и лицензирования определяются владельцами репозитория.
