# Tools

Два скрипта, ноль тяжёлых зависимостей (только `pyyaml`).

## `build_context.py`

Собирает весь слепок (`PERSONALITY_MODEL.yaml`, `cases/`, `lenses/`,
`training_data/pairs/`) в два файла в корне проекта:

- `context.md` — единый markdown, готов к вставке в system prompt/контекст
  любого агента (Claude Code, кастомный Python-агент, что угодно).
- `context.json` — плоский список типизированных чанков (id, type, status,
  title, text, source_file) для программного использования (RAG).

```bash
python tools/build_context.py
```

Безопасно перезапускать в любой момент — только читает файлы слепка,
ничего в них не пишет. Перегенерировать после любого обновления
`PERSONALITY_MODEL.yaml`/кейсов/линз.

## `rag_query.py`

RAG-lite поиск по контексту: чистый Python TF-IDF + косинусное сходство,
пересчитывается на лету при каждом запросе (корпус маленький — миллисекунды).
Без персистентного индекса, без pickle.

```bash
python tools/rag_query.py "автоматизировать сейчас или потом"
python tools/rag_query.py "canary deployment" --top-k 3
python tools/rag_query.py "TDD" --type heuristic,pattern
python tools/rag_query.py "риск" --rebuild   # форсировать пересборку context.json
```

Если `context.json` ещё нет — соберёт его сам перед поиском.

## Почему не полноценная vector DB

Корпус сейчас — ~8 кейсов, 25 эвристик, 52 синтетические пары ≈ 150
чанков. Полноценная vector DB (Pinecone/Qdrant/Chroma) с embedding-моделью
для такого объёма — избыточная сложность (см. H001/H002/N+1 Rule в
`PERSONALITY_MODEL.yaml`). Когда корпус вырастет на порядки — тогда и
есть смысл пересмотреть подход, не раньше.
