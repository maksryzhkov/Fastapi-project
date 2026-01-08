# FastAPI Микросервисы

Два микросервиса на FastAPI с хранением данных в SQLite и Docker контейнеризацией.

## Сервисы

### 1. ToDo-сервис

- Порт: 8000
- Документация: http://localhost:8000/docs
- Эндпоинты:
  - POST /items - создание задачи
  - GET /items - получение списка задач
  - GET /items/{id} - получение задачи по ID
  - PUT /items/{id} - обновление задачи
  - DELETE /items/{id} - удаление задачи

### 2. URL Shortener

- Порт: 8001
- Документация: http://localhost:8001/docs
- Эндпоинты:
  - POST /shorten - создание короткой ссылки
  - GET /{short_id} - перенаправление по короткой ссылке
  - GET /stats/{short_id} - статистика по ссылке

# Запуск локально

## Установка и запуск ToDo сервиса

### Переходим в директорию сервиса
cd todo_app

### Устанавливаем зависимости
pip install -r requirements.txt

### Запускаем сервис
uvicorn main:app --host 0.0.0.0 --port 8000

## Установка и запуск URL сервиса

### Переходим в директорию сервиса
cd shorturl_app

### Устанавливаем зависимости
pip install -r requirements.txt

### Запускаем сервис
uvicorn main:app --host 0.0.0.0 --port 8001

# Запуск через Docker

## Создаем именованные тома для хранения данных
docker volume create todo_data
docker volume create shorturl_data

## Запускаем ToDo сервис
docker run -d -p 8000:80 -v todo_data:/app/data вашлогин/todo-service:latest

## Запускаем сервис сокращения URL
docker run -d -p 8001:80 -v shorturl_data:/app/data вашлогин/shorturl-service:latest
