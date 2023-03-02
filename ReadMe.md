# Сервис микроблогов

![](https://img.shields.io/badge/python-3.11-blue?style=flat-square)
![](https://img.shields.io/badge/fastAPI-0.92.0-blue)
![](https://img.shields.io/badge/sqlalchemy-2.0.3-blue)
![](https://img.shields.io/badge/database-postgreSQL-yellow)
![](https://img.shields.io/badge/docker-3.9-blue)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/expmax85/DiplomTweetfastApi)
![](https://img.shields.io/badge/swagger-valid-brightgreen)
![](https://img.shields.io/badge/license-MIT-green)
## Легенда
Для корпоративного сервиса микроблогов необходимо реализовать бэкенд
приложения. 
### Функциональные требования:
 1. Пользователь может добавить новый твит.
 2. Пользователь может удалить свой твит.
 3. Пользователь может зафоловить другого пользователя.
 4. Пользователь может отписаться от другого пользователя.
 5. Пользователь может отмечать твит как понравившийся.
 6. Пользователь может убрать отметку «Нравится».
 7. Пользователь может получить ленту из твитов отсортированных в
порядке убывания по популярности от пользователей, которых он
фоловит.
 8. Твит может содержать картинку.

### Нефункциональные требования:
1. Систему должно быть просто развернуть через Docker Compose.
2. Система не должна терять данные пользователя между запусками.
3. Все ответы сервиса должны быть задокументированы через Swagger. Документация должна быть доступна в момент запуска приложения.

### Дополнительные требования:
1. Использование PostgreSQL в качестве СУБД
2. Запуск приложения при деплое по одной команде докера
3. Наличие (интеграционных) тестов
4. Код должен соответствовать всем требованиям PEP (проверка линтерами)

## Описание реализации проекта

### Используемые технологии:
 - Python 3.11
 - Framework FastApi
 - SQLAlchemy 2.0 + asyncpg
 - Alembic
 - Docker, Docker compose
 - PostgreSQL
 - Redis
 - RabbitMQ
 - Celery + Flower
 - Nginx
 - EFK-стек

### Установка и использование:
Проект можно запустить в нескольких режимах:
1. Локальное развертывание проекта (без докера)
При локальном развертывании необходимо наличие Postgres, Redis RabbitMQ
 - Скачать репозиторий проекта:
```bash
git clone
cd Test_app 
```
 - Установить виртуальное окружение (при необходимости), зависимости
```bash
pip install -r dev_requirements.txt
```
- Подключить базу данных, Redis, RabbitMQ, заполнить файл `.env` по образцу `env.template`

- Выполнить миграции командой:
```bash
alembic upgrade head
```
- Запустить проект командой:
 ```bash
uvicorn src.main:app --reload
```
2. В режиме разработки:
Создать файл `dev.env`,заполнив его по образцу `env.template`, и выполнить команду:
```bash
sudo docker compose -f docker-compose-dev.yml --env-file dev.env up
```

3. В режиме тестования
Создать файл `test.env`,заполнив его по образцу `env.template`, и выполнить команду:
```bash
sudo docker compose -f docker-compose-test.yml --env-file test.env up
```

4. В режиме деплоя
Создать файл `.env`,заполнив его по образцу `env.template`, и выполнить команду:
```bash
sudo docker compose --env-file .env up -d
```

## Openapi (Swagger)
### Документация OpenAPI:
```
/api/docs
```

## Flower
Для отслеживания работы celery используется flower. Для входа, необходимо подключиться по корневому адресу проекта с портом, указанным в настройках (по умолчанию 5555), например:
```
http://127.0.0.1:5555/
```

## EFK-стек
К проекту подключены средства профилирования и логгирования EFK. Для входа в систему необходимо необходимо подключиться по корневому адресу проекта с портом, указанным в настройках kibana (по умолчанию 5601), например:
```
http://127.0.0.1:5601/
```