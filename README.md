# Wallet

---
## Описание

Wallet — это сервис, где пользователь может пополнять свой кошелек,  
снимать с него средства и проверять баланс.
---

## Архитектура и стек

- **Стек:** Django, DRF, PostgreSQL, Docker, pytest.
- **Архитектура:**
    - `backend/` — код сервиса
    - `nginx/` — настройки прокси
    - `tests/` — тесты
    - `docker-compose.yml` — запуск в контейнерах (Docker Compose)
    - `docker-compose.production.yml` — продакшен-конфигурация
---

## Установка

### Как развернуть проект на локальной машине

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/SlavaKlkv/wallet.git
    ```
   Перейдите в корень проекта:
   ```bash
    cd wallet
   ```

2. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    ```
    Для Linux/macOS
    ```bash
    source venv/bin/activate
    ```
    Для Windows:
    ```bash
    venv\Scripts\activate
    ```

3. Установите зависимости:
    ```bash
    pip install -r backend/requirements.txt
    ```

4. Создайте и заполните `.env`.

| Переменная              | Описание                                                                                         | Пример                 |
|-------------------------|--------------------------------------------------------------------------------------------------|------------------------|
| USE_SQLITE              | Использовать SQLite вместо PostgreSQL (1 — да, 0 — нет)                                          | 0                      |
| DEBUG                   | Включить режим отладки Django                                                                    | True                   |
| CSRF_TRUSTED_ORIGINS    | Доверенные домены для CSRF (через запятую)                                                       | https://site-domen.com |
| SECRET_KEY              | Секретный ключ Django                                                                            | your_secret_key        |
| POSTGRES_USER           | Пользователь PostgreSQL                                                                          | postgres_user          |
| POSTGRES_PASSWORD       | Пароль для PostgreSQL                                                                            | postgres_password      |
| POSTGRES_DB             | Название базы данных PostgreSQL                                                                  | db_name                |
| DB_HOST                 | Хост для подключения к БД (db — docker, localhost — локально)                                    | db                     |
| DB_PORT                 | Порт для подключения к БД                                                                        | 5432                   |
| COMPOSE_BAKE            | Ускоряет сборку Docker Compose при поддержке bake; обычно не требуется для локальной разработки) | true                   |
| MEDIA_ROOT              | Путь для хранения медиафайлов при запуске вне локального окружения        | /media                   |

---

5. Примените миграции

```bash
   python backend/manage.py migrate
```

6. Запуск тестов

```bash
   pytest
```

### Для соответствия PEP8
- Упорядочивание импортов
- Редактирование стиля
```bash
   isort .
   flake8 .
```

## Запуск через Docker Compose

Запуск приложения
    
```bash
   docker compose up
```

Для запуска без пересборки образов с пересозданием контейнеров даже,  
если не было изменений:
```bash
   docker compose up --build --force-recreate
```

Для пересборки всех образов без использования кеша:
```bash
   docker compose build --no-cache
   docker compose up
```

Остановка и удаление всех контейнеров
    
```bash
   docker compose down
```

---

## Примеры API-запросов
    
### Получить баланс
    
**GET** `/api/v1/wallets/uuid/`

Ответ:
```json
{
    "balance": 5250.37
}
```

---

### Пополнить кошелек
    
**POST** `/api/v1/wallets/uuid/operation/`

Тело запроса:
```json
{
  "operation_type": "deposit",
  "amount": 200
}
```

Ответ:
```json
{
    "balance": 5450.37
}
```

---

## Описание ошибок

Пример формата ошибок для 400, 401, 403, 404:

```json
{
  "detail": "Недостаточно средств."
}
```

---

## Лицензия

MIT

---

## Контакты

Telegram: slava_kulikov  
slava_kulikov@outlook.com
#
