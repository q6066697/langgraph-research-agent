# Self-hosted инференс через vLLM (Qwen2.5-7B-Instruct-AWQ)

Тот же ReAct-агент, но вместо облачного API (OpenAI/Anthropic) работает
на локальной модели, поднятой через vLLM с OpenAI-совместимым
эндпоинтом. Проверено на бесплатном Tesla T4 (16 ГБ).

## Запуск сервера

    vllm serve Qwen/Qwen2.5-7B-Instruct-AWQ \
      --quantization awq \
      --dtype half \
      --max-model-len 4096 \
      --gpu-memory-utilization 0.9 \
      --enable-auto-tool-choice \
      --tool-call-parser hermes \
      --port 8000

## Подключение агента

Провайдер выбирается переменной окружения `PROVIDER=vllm` — ветка с
`ChatOpenAI`, направленная на локальный сервер (base_url
http://localhost:8000/v1, api_key "EMPTY").

## Грабли T4 и tool calling (разобрано на практике)

- **bfloat16 на T4.** T4 (compute capability 7.5) не поддерживает
  bfloat16, а AWQ и так требует float16 -> флаг `--dtype half`, иначе
  сервер падает при старте.
- **tool_choice="auto".** Без `--enable-auto-tool-choice` vLLM отвечает
  ошибкой 400 на `tool_choice:"auto"` от OpenAI/LangChain-клиента.
- **Парсер вызовов.** Для Qwen2.5-Instruct — `--tool-call-parser
  hermes`. Coder-версия с этим парсером ломается, поэтому Instruct.
- **Attention-бэкенд.** На T4 нет FlashAttention 2 (нужна CC >= 8) —
  vLLM автоматически откатывается на Triton-backend.
- **Контекст.** `--max-model-len 4096`; при длинной выдаче поиска
  уменьшать `max_results` или поднимать лимит.

## Проверка

Полный ReAct-цикл отработал на self-hosted модели: агент сам сформировал
вызов инструмента, LangGraph выполнил веб-поиск через Tavily, модель
вернула ответ с цитированием источников — без ошибок.
