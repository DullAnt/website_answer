# Website Answer

Локальный API-сервис для поиска информации в Newton/wiki, извлечения текста со страниц и генерации ответа через локальную Ollama-модель.

## Что должно быть на сервере

- Python 3.10 или 3.11.
- Ollama.

## Установка

Создать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate
```

Установить зависимости:

```bash
python -m pip install -r requirements.txt
```

Если сервер без интернета, заранее подготовить `wheelhouse` на машине с интернетом:

```bash
python -m pip download -r requirements.txt -d wheelhouse
```

На сервере установить так:

```bash
python -m pip install --no-index --find-links wheelhouse -r requirements.txt
```

## Настройка

Скопировать пример окружения:

```bash
cp .env.example .env
```
Для локальной проверки не на сервере можно использовать SearXNG/Yandex:


Проверка SearXNG:

```bash
curl -G "http://127.0.0.1/searxng/search" \
  --data-urlencode "q=python programming language" \
  --data "format=json" \
  --data "engines=yandex"
```

Если в ответе есть `unresponsive_engines` и `yandex timeout`, значит проблема в доступе SearXNG к Yandex/сети. Это не ошибка Ollama и не ошибка генерации тем.

#Выключите ВПН для работы

Основные параметры для Newton:

```env
SEARCH_ENGINE=newton
NEWTON_BASE_URL=https://newton.psbank.ru
NEWTON_SEARCH_PATH=/api/internal/search/resultByGroups
NEWTON_WHERE=iblock_wiki
NEWTON_ROOT_SECTION_ID=0
NEWTON_FETCH_FULL_PAGES=true
```

Основные параметры Ollama:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=<локальная ollama-модель> пример gemma2:2b
EMBEDDING_MODEL=<локальная embedding-модель> пример intfloat/multilingual-e5-large
DEVICE=<ваш девайс> пример cpu
```

## Запуск API

```bash
python main_api.py
```

По умолчанию API запускается на:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Проверка

Проверить, что API живой:

```bash
curl http://127.0.0.1:8000/api/health
```

Проверить поиск:

```bash
curl http://127.0.0.1:8000/api/health/search
```

Пример запроса ответа:

```bash
curl -X POST http://127.0.0.1:8000/api/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"как оформить зарплатную карту","max_results":5,"save_pages":true}'
```

## Важные замечания

- В режиме `newton` Tavily не нужен.
- Ollama и модели не устанавливаются через `requirements.txt`.
- Если embedding-модель отсутствует локально, приложение может попытаться скачать ее из интернета.
- Старый каталог `searxng_docker/` не является готовым deploy-бандлом для Newton-режима.

Если используется reasoning/think-модель, например Qwen3, нужно указать ее реальное имя из `ollama list`:

```env
OLLAMA_MODEL=qwen3:8b
```

Текущий код обращается к Ollama как к обычной chat-модели. Если модель возвращает служебный блок `<think>...</think>`, он не может попасть в ответ.
