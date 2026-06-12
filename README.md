<div align="center">

<h1>
  code-<span style="color:#00AFFF;">runner</span>
</h1>

<h3>
  A service for running user-submitted code in a secure sandbox and validating solutions against test cases
</h3>

<p>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/RabbitMQ-broker-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white" alt="RabbitMQ">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

<p>
  README is available in:
  <a href="./README.ru.md">Russian</a> ·
  <a href="./README.md">English</a>
</p>

</div>

---

## Navigation

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [About the Project](#about-the-project)
- [Endpoints](#endpoints)
- [Submission Status](#submission-status)
- [Submission Verdicts](#submission-verdicts)
- [How It Works](#how-it-works)
- [Authorization](#authorization)
- [Sandboxed Environment](#sandboxed-environment)
- [Request and Response Examples](#request-and-response-examples)
- [Roadmap](#roadmap)

---

## Features

* **Test suites** — create, retrieve, update, and delete test suites
* **Code execution** — run user-submitted Python code in an isolated environment
* **Sandboxing** — restricted execution through `nsjail` without access to the host system
* **Resource limits** — control execution time and memory usage
* **Async processing** — process submissions through Celery workers
* **Queue-based architecture** — send execution tasks through RabbitMQ
* **Result tracking** — retrieve status, verdict, and test execution information
* **Service authorization** — JWT authorization for external services
* **Docker setup** — run the API, worker, database, broker, and result backend with Docker Compose

---

## Tech Stack

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

## Quick Start

```bash
git clone https://github.com/xssandreissx/code-runner
cd code-runner

cp .env.example .env
docker compose up --build
```

---

## CLI Commands

### Services

**Add a new service:**

```bash
docker compose exec fastapi python -m app.cli add-service
```

**Refresh a service JWT secret:**

```bash
docker compose exec fastapi python -m app.cli refresh-jwt
```

**Delete a service:**

```bash
docker compose exec fastapi python -m app.cli delete-service
```

### Test datasets

**Show the list of demo problems:**

```bash
docker compose exec fastapi python -m app.cli list-problems
```

**Show data for a demo problem:**

```bash
docker compose exec fastapi python -m app.cli check-problem
```

**Insert a test suite into the database:**

```bash
docker compose exec fastapi python -m app.cli insert-problem
```

**Run judge-test to check service functionality:**

```bash
docker compose exec fastapi python -m app.cli judge-test
```

---

## About the Project

`code-runner` can be integrated with educational platforms, online courses, internal LMS systems, or custom services for checking programming solutions.

The main goal of the project is to safely run user-submitted code, check it against predefined tests, and return the execution result.

The project intentionally does not include entities such as problem title, description, difficulty, or topic.  
`code-runner` is responsible only for code execution and result checking, while problem storage remains on the external service side.

---

## Endpoints

### Test suites

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/testsuite` | Create a test suite |
| `GET` | `/testsuite/{testsuite_id}` | Get a test suite |
| `PATCH` | `/testsuite/{testsuite_id}` | Update a test suite |
| `DELETE` | `/testsuite/{testsuite_id}` | Delete a test suite |

### Submissions

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/submission` | Submit code for checking |
| `GET` | `/submission/{submission_id}` | Get submission status and verdict |

---

## Submission Status

| Status | Description |
| --- | --- |
| `IN_QUEUE` | The solution is waiting in the queue |
| `RUNNING` | The solution is currently being checked |
| `FINISHED` | The check is finished. Verdict information is available |

## Submission Verdicts

| Verdict | Description |
| --- | --- |
| `ACCEPTED` | The solution passed all tests |
| `WRONG_ANSWER` | The output does not match the expected result |
| `TIME_LIMIT_EXCEEDED` | The execution time limit was exceeded |
| `MEMORY_LIMIT_EXCEEDED` | The memory limit was exceeded |
| `RUNTIME_ERROR` | An error occurred during execution |
| `INTERNAL_ERROR` | An internal service error occurred |

---

## How It Works

1. An external service creates a test suite.
2. The external service submits code for checking by `testsuite_id`.
3. The API creates a submission and sends a task to the queue.
4. A Celery worker runs the code in an isolated environment.
5. The result is saved to the database.
6. The external service retrieves the status and verdict by `submission_id`.

---

## Authorization

All protected endpoints require a JWT token in the `Authorization` header.

```bash
Authorization: Bearer <JWT_TOKEN>
```

For each external service, `code-runner` creates a separate record and a unique JWT secret.

The external service signs a JWT with its secret and uses the generated token when calling the API.

For local test token generation, you can use:

```bash
python utils/jwt_generator.py
```

---

## Sandboxed Environment

Each test is executed separately in an isolated environment through `nsjail`.

* A separate working directory is created for execution
* A prepared rootfs is used instead of direct access to the host system
* Network access is restricted
* Linux namespaces and cgroups are applied
* Execution time is limited
* Memory usage and the number of processes are limited
* File system writes are restricted
* User-submitted code runs separately from the API and the database

---

## Request and Response Examples

<details>
<summary><b>Create a test suite</b></summary>

### Request

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

### Response

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
<summary><b>Submit a solution for checking</b></summary>

### Request

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

### Response

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
<summary><b>Check a submission</b></summary>

### Request

```bash
curl -X 'GET' \
  'http://localhost:8000/submission/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

### Response

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

- [x] Create and manage test suites
- [x] JWT authorization for services
- [x] Submit solutions for checking
- [x] Python language support
- [x] Run code in an isolated environment (`nsjail`)
- [x] PostgreSQL
- [x] Test checking and result persistence
- [x] Async processing through Celery + RabbitMQ

- [ ] Support multiple programming languages
- [ ] Compilation step for compiled languages
- [ ] Assert-based tests for deeper solution checking
- [ ] Restrictions through `seccomp`
- [ ] Limit stdout/stderr size
- [ ] Detailed per-test execution statistics
- [ ] Metrics and monitoring for worker processes

---

<div align="center">
  <p><b>XsSandreiSsX</b> · MIT License</p>
</div>
