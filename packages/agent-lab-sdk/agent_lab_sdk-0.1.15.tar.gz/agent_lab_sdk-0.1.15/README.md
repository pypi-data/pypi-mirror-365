# Agent Lab SDK

Набор утилит и обёрток для упрощённой работы с LLM, Agent Gateway и метриками в проектах Giga Labs.

## Установка

```bash
pip install agent_lab_sdk
```

## Содержание

1. [Модуль `agent_lab_sdk.llm`](#1-модуль-agent_lab_sdkllm)
2. [Модуль `agent_lab_sdk.llm.throttled`](#2-модуль-agent_lab_sdkllmthrottled)
3. [Модуль `agent_lab_sdk.metrics`](#3-модуль-agent_lab_sdkmetrics)
4. [Хранилище](#4-хранилище)
5. [Схема](#5-схема)
6. [Сборка и публикация](#6-сборка-и-публикация)

---

## 1. Модуль `agent_lab_sdk.llm`

### 1.1. Получение модели

```python
from agent_lab_sdk.llm import get_model

# Использует токен из окружения по умолчанию
model = get_model()

# Передача явных параметров
model = get_model(
    access_token="YOUR_TOKEN",
    timeout=60,
    scope="GIGACHAT_API_CORP"
)
```

> если не передавать access_token, токен будет выбран через GigaChatTokenManager

> планы на ближайшее будущее: get_model оборачивает внутри себя throttled классы.

### 1.2. Менеджеры токенов

| Класс                  | Описание                                                                                | Пример использования                            |
| ---------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `AgwTokenManager`      | Кеширование + получение токена через Agent Gateway                                      | `token = AgwTokenManager.get_token("provider")` |
| `GigaChatTokenManager` | Кеширование + получение через GigaChat OAuth с использованием пользовательских секретов | `token = GigaChatTokenManager.get_token()`      |

### 1.3. Переменные окружения

| Переменная                               | Описание                                                 | Значение по умолчанию / Пример                      |
| ---------------------------------------- | -------------------------------------------------------- | --------------------------------------------------- |
| `GIGACHAT_SCOPE`                         | Scope GigaChat API                               | `GIGACHAT_API_PERS`                                 |
| `GLOBAL_GIGACHAT_TIMEOUT`                | Таймаут запросов к GigaChat (секунды)                    | `120`                                               |
| `USE_TOKEN_PROVIDER_AGW`                 | Использовать `AgwTokenManager`                           | `true`                                              |
| `GIGACHAT_CREDENTIALS`                   | Базовые креды для GigaChat (`b64(clientId:secretId)`)    | `Y2xpZW50SWQ6c2VjcmV0SWQ=`                          |
| `GIGACHAT_TOKEN_PATH`                    | Путь к файлу кеша токена GigaChat                        | `/tmp/gigachat_token.json`                          |
| `GIGACHAT_TOKEN_FETCH_RETRIES`           | Количество попыток получения токена (GigaChat)           | `3`                                                 |
| `USE_GIGACHAT_ADVANCED`                  | Включает запрос токена GigaChat API в продвинутом режиме | `true`                                              |
| `GIGACHAT_BASE_URL`                      | Базовый URL GigaChat для расширенного режима             | `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` |
| `TOKEN_PROVIDER_AGW_URL`                 | URL Agent Gateway для получения AGW-токена               | `https://agent-gateway.apps.advosd.sberdevices.ru`  |
| `TOKEN_PROVIDER_AGW_DEFAULT_MAX_RETRIES` | Макс. попыток запроса токена (AGW)                       | `3`                                                 |
| `TOKEN_PROVIDER_AGW_TIMEOUT_SEC`         | Таймаут запроса к AGW (секунды)                          | `5`                                                 |

---

<a name="throttled"></a>

## 2. Модуль `agent_lab_sdk.llm.throttled`

Позволяет ограничивать число одновременных вызовов к GigaChat и сервису эмбеддингов, автоматически собирая соответствующие метрики.

```python
from agent_lab_sdk.llm import GigaChatTokenManager
from agent_lab_sdk.llm.throttled import ThrottledGigaChat, ThrottledGigaChatEmbeddings

access_token = GigaChatTokenManager.get_token()

# Чат с учётом ограничений
chat = ThrottledGigaChat(access_token=access_token)
response = chat.invoke("Привет!")

# Эмбеддинги с учётом ограничений
emb = ThrottledGigaChatEmbeddings(access_token=access_token)
vectors = emb.embed_documents(["Text1", "Text2"])
```

### 2.1. Переменные окружения для ограничения

| Переменная                        | Описание                                    | Значение по умолчанию |
| --------------------------------- | ------------------------------------------- | --------------------- |
| `MAX_CHAT_CONCURRENCY`            | Максимум одновременных чат-запросов         | `100000`              |
| `MAX_EMBED_CONCURRENCY`           | Максимум одновременных запросов эмбеддингов | `100000`              |
| `EMBEDDINGS_MAX_BATCH_SIZE_PARTS` | Макс. размер батча частей для эмбеддингов   | `90`                  |

### 2.2. Метрики

Метрики доступны через `agent_lab_sdk.metrics.get_metric`:

| Метрика                   | Описание                                       | Тип       |
| ------------------------- | ---------------------------------------------- | --------- |
| `chat_slots_in_use`       | Число занятых слотов для чата                  | Gauge     |
| `chat_waiting_tasks`      | Число задач, ожидающих освобождения слота чата | Gauge     |
| `chat_wait_time_seconds`  | Время ожидания слота чата (секунды)            | Histogram |
| `embed_slots_in_use`      | Число занятых слотов для эмбеддингов           | Gauge     |
| `embed_waiting_tasks`     | Число задач, ожидающих слота эмбеддингов       | Gauge     |
| `embed_wait_time_seconds` | Время ожидания слота эмбеддингов (секунды)     | Histogram |

---

<a name="metrics"></a>

## 3. Модуль `agent_lab_sdk.metrics`

Предоставляет удобный интерфейс для создания и управления метриками через Prometheus-клиент.

### 3.1. Основные функции

```python
from agent_lab_sdk.metrics import get_metric

# Создать метрику
g = get_metric(
    metric_type="gauge",               # тип: "gauge", "counter" или "histogram"
    name="my_gauge",                   # имя метрики в Prometheus
    documentation="Моя метрика gauge"  # описание
)

# Увеличить счётчик
g.inc()

# Установить конкретное значение
g.set(42)
```

### 3.2. Пример использования в коде

```python
from agent_lab_sdk.metrics import get_metric
import time

# Счётчик HTTP-запросов с метками
reqs = get_metric(
    metric_type="counter",
    name="http_requests_total",
    documentation="Всего HTTP-запросов",
    labelnames=["method", "endpoint"]
)
reqs.labels("GET", "/api").inc()

# Гистограмма задержек
lat = get_metric(
    metric_type="histogram",
    name="http_request_latency_seconds",
    documentation="Длительность HTTP-запроса",
    buckets=[0.1, 0.5, 1.0, 5.0]
)
with lat.time():
    time.sleep(0.5)

print(reqs.collect())
print(lat.collect())
```

## 4. Хранилище

### 4.1 SD Ассетница

функция `store_file_in_sd_asset` сохраняет base64‑файл в хранилище S3 и отдаёт публичную ссылку на файл

```python
from agent_lab_sdk.storage import store_file_in_sd_asset

store_file_in_storage("my-agent-name-filename.png", file_b64, "giga-agents")
```

### 4.2 AGW Checkpointer

AGW поддерживает langgraph checkpoint API и в SDK представлен `AsyncAGWCheckpointSaver`, который позволяет сохранять состояние графа в AGW напрямую. 

## 5. Схема

TODO: описание LogMessage

## 6. Сборка и публикация

1. Установка twine

```bash
pip install --upgrade build twine
```

2. Собрать и загрузить в pypi

перед обновлением сборки нужно не забыть поменять версию в [pyproject.toml](/pyproject.toml)
```bash
python -m build && python -m twine upload dist/*
```

3. Ссылка на проект pypi

> https://pypi.org/project/agent-lab-sdk/

4. установка локально в editable mode. Предварительно может потребоваться выбрать необходимое окружение
```bash
pip install -e .
```

# Примеры использования

TBD