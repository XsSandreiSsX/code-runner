<div align="center">

<h1>
  code-<span style="color:#00AFFF;">runner</span>
</h1>

<h3>
  Сервис для запуска пользовательского кода в безопасной среде и проверки решений на тестах
</h3>

<p>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/RabbitMQ-broker-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" alt="RabbitMQ">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>


<p>
  README доступен на:
  <a href="./README.ru.md">Русском</a> ·
  <a href="./README.md">English</a>
</p>

</div>

---

## Навигация

- [Возможности](#возможности)
- [Стек](#стек)
- [Быстрый запуск](#быстрый-запуск)
- [CLI-команды](#cli-команды)
- [О проекте](#о-проекте)
- [Эндпоинты](#эндпоинты)
- [Статус Submission](#статус-submission)
- [Вердикты Submission](#вердикты-submission)
- [Как это работает](#как-это-работает)
- [Авторизация](#авторизация)
- [Изолированная среда](#изолированная-среда)
- [Примеры запросов и ответов](#примеры-запросов-и-ответов)
- [Roadmap](#roadmap)

---

## Возможности

* **Test suites** — создание, получение, обновление и удаление наборов тестов
* **Code execution** — запуск пользовательского Python-кода в изолированной среде
* **Sandboxing** — ограниченный запуск через `nsjail` без доступа к основной системе
* **Resource limits** — контроль времени выполнения и потребляемой памяти
* **Async processing** — обработка отправок через Celery workers
* **Queue-based architecture** — передача задач на выполнение через RabbitMQ
* **Result tracking** — получение статуса, вердикта и информации о прохождении тестов
* **Service authorization** — JWT-авторизация внешних сервисов
* **Docker setup** — запуск API, worker, базы данных, брокера и backend-хранилища через Docker Compose

---

## Стек

| Layer | Technologies               |
| --- |----------------------------|
| **API** | FastAPI, Pydantic v2       |
| **Database** | PostgreSQL, SQLAlchemy 2.0 |
| **Queue** | Celery                     |
| **Message broker** | RabbitMQ                   |
| **Result backend** | Redis                      |
| **Sandbox** | nsjail                     |
| **CLI** | Typer, Rich                |
| **Infrastructure** | Docker, Docker Compose     |

---

## Быстрый запуск

```bash
git clone https://github.com/xssandreissx/code-runner
cd code-runner

cp .env.example .env
docker compose up --build
```

---

## CLI-команды

### Сервисы

**Добавить новый сервис:**

```bash
docker compose exec fastapi python -m app.cli add-service
```

**Обновить JWT-секрет сервиса:**

```bash
docker compose exec fastapi python -m app.cli refresh-jwt
```

**Удалить сервис:**

```bash
docker compose exec fastapi python -m app.cli delete-service
```

### Тестовые наборы данных

**Посмотреть список тестовых проблем:**

```bash
docker compose exec fastapi python -m app.cli list-problems
```

**Посмотреть данные демонстрационной проблемы:**

```bash
docker compose exec fastapi python -m app.cli check-problem
```

**Загрузить набор тестов в базу данных:**

```bash
docker compose exec fastapi python -m app.cli insert-problem
```

**Запустить judge-test для проверки работоспособности сервиса:**

```bash
docker compose exec fastapi python -m app.cli judge-test
```

---

## О проекте

`code-runner` можно интегрировать с обучающими платформами, онлайн-курсами, внутренними LMS или собственными сервисами для проверки решений.

Основная задача проекта — безопасно запускать пользовательский код, проверять его на заранее подготовленных тестах и возвращать результат выполнения.

В проекте намеренно нет сущностей вроде названия задачи, описания, сложности или темы.  
`code-runner` отвечает только за запуск кода и проверку результата, а хранение задач остаётся на стороне внешнего сервиса.

---

## Эндпоинты

### Test suites

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/testsuite` | Создать набор тестов |
| `GET` | `/testsuite/{testsuite_id}` | Получить набор тестов |
| `PATCH` | `/testsuite/{testsuite_id}` | Обновить набор тестов |
| `DELETE` | `/testsuite/{testsuite_id}` | Удалить набор тестов |

### Submissions

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/submission` | Отправить код на проверку |
| `GET` | `/submission/{submission_id}` | Получить статус и вердикт решения |

---

## Статус Submission

| Status | Description |
| --- | --- |
| `IN_QUEUE` | Решение находится в очереди |
| `RUNNING` | Решение находится в процессе проверки |
| `FINISHED` | Проверка завершена. Доступна информация о вердикте |

## Вердикты Submission

| Verdict | Description |
| --- | --- |
| `ACCEPTED` | Решение прошло все тесты |
| `WRONG_ANSWER` | Ответ не совпал с ожидаемым |
| `TIME_LIMIT_EXCEEDED` | Превышено ограничение по времени |
| `MEMORY_LIMIT_EXCEEDED` | Превышено ограничение по памяти |
| `RUNTIME_ERROR` | Ошибка во время выполнения |
| `INTERNAL_ERROR` | Внутренняя ошибка сервиса |

---

## Как это работает

1. Внешний сервис создаёт набор тестов.
2. Внешний сервис отправляет код на проверку по `testsuite_id`.
3. API создаёт submission и отправляет задачу в очередь.
4. Celery worker запускает код в изолированной среде.
5. Результат сохраняется в базе данных.
6. Внешний сервис получает статус и вердикт по `submission_id`.

---

## Авторизация

Все защищённые эндпоинты требуют JWT-токен в заголовке `Authorization`.

```bash
Authorization: Bearer <JWT_TOKEN>
```

Для каждого внешнего сервиса в `code-runner` создаётся отдельная запись и уникальный JWT-секрет.

Внешний сервис подписывает JWT своим секретом и использует полученный токен при обращении к API.

Для локальной генерации тестового токена можно использовать:

```bash
python utils/jwt_generator.py
```

---

## Изолированная среда

Каждый тест запускается отдельно в изолированной среде через `nsjail`.

* Создаётся отдельная рабочая директория для запуска
* Используется подготовленный rootfs вместо прямого доступа к системе хоста
* Ограничивается доступ к сети
* Применяются Linux namespaces и cgroups
* Ограничивается время выполнения
* Ограничивается память и количество процессов
* Ограничивается запись в файловую систему
* Пользовательский код запускается отдельно от API и базы данных

---

## Примеры запросов и ответов

<details>
<summary><b>Создание набора тестов</b></summary>

### Запрос

```bash
curl -X 'POST' \
  'http://localhost:8000/testsuite' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
  "time_limit": 1,
  "memory_limit": 128,
  "test_cases": [
    {
      "stdin": "3 4",
      "stdout": "7"
    },
    {
      "stdin": "10 15",
      "stdout": "25"
    }
  ]
}'
```

### Ответ

```json
{
  "status": "success",
  "data": {
    "id": 1
  },
  "detail": "Successfully created new test suite"
}
```

</details>

<details>
<summary><b>Отправить решение на проверку</b></summary>

### Запрос

```bash
curl -X 'POST' \
  'http://localhost:8000/submission' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
  "testsuite_id": 1,
  "source_code": "a, b = map(int, input().split())\nprint(a + b)"
}'
```

### Ответ

```json
{
  "status": "success",
  "data": {
    "submission_id": 1,
    "submission_status": "IN_QUEUE"
  },
  "detail": "Submission created successfully"
}
```

</details>

<details>
<summary><b>Проверить решение</b></summary>

### Запрос

```bash
curl -X 'GET' \
  'http://localhost:8000/submission/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

### Ответ

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "testsuite_id": 1,
    "status": "FINISHED",
    "verdict": "ACCEPTED",
    "failed_test_index": 0,
    "error_message": "",
    "time_used": 83,
    "memory_used": 12,
    "tests_passed": 100
  },
  "detail": "Submission found successfully"
}
```

</details>

---

## Roadmap

- [x] Создание и управление наборами тестов
- [x] JWT-авторизация сервисов
- [x] Отправка решений на проверку
- [x] Поддержка языка Python
- [x] Запуск кода в изолированной среде (`nsjail`)
- [x] PostgreSQL
- [x] Проверка тестов и сохранение результатов
- [x] Асинхронная обработка через Celery + RabbitMQ

- [ ] Поддержка нескольких языков программирования
- [ ] Compilation step для компилируемых языков
- [ ] Assert-тесты для углублённой проверки решений
- [ ] Ограничения через `seccomp`
- [ ] Ограничение размера stdout/stderr
- [ ] Детальная статистика выполнения по каждому тесту
- [ ] Метрики и мониторинг worker-процессов

---

<div align="center">
  <p><b>XsSandreiSsX</b> · MIT License</p>
</div>
