# Roadmap

**[Русский](#русский) | [中文](#中文) | [English](#english)**

---

## Русский

### Сейчас (v0.x — активное наполнение)

- [x] Скелет проекта: 4 слоя (модель личности, кейсы, линзы, гид по обучению агента)
- [x] `PERSONALITY_MODEL.yaml`: ценности, риск-профиль, 25 эвристик, 12 паттернов, управленческий слой
- [x] Кодовое слово «Слепок!» — захват задачи в кейс прямо во время работы
- [x] 8 реальных кейсов (один — в процессе)
- [x] `training_data/` — синтетический датасет с протоколом против галлюцинаций
- [x] `tools/` — context-loader и RAG-lite поиск (pure Python, без тяжёлых зависимостей)
- [x] `tools/` укреплён по итогам код-ревью: валидация схемы (падает громко), Layer 4 реально в контексте, лёгкий стемминг, вес/флаг по статусу (rejected не выглядит советом), `--compact`/`--json`/`--min-score`, 13 pytest-тестов, CI
- [ ] Завершить кейс C008 (мега-проект, 400 000 пользователей)
- [ ] Закрыть открытые вопросы (`OPEN_QUESTIONS.md`): пороги P10/P11, P12 в финансах, сигнал усталости H006
- [ ] Подтвердить или заменить оставшийся черновик (`lenses/pareto-pragmatist-lens.draft.md`)
- [ ] Ежедневная практика: минимум 1 кейс или линза в день (см. TELOS)

### Дальше (v0.y — расширение и проверка)

- [ ] Больше линз — покрыть основные типы решений (не только «много неизвестных»)
- [ ] Расширить `training_data/` новыми батчами с верификацией человеком
- [ ] Попробовать fine-tuning или prompt-tuning небольшой локальной модели на `training_data/`
- [ ] Простой REPL/CLI поверх `rag_query.py` для запросов во время реальной работы
- [ ] `evals/` — harness калибровки: набор вопросов + рубрика из 4 критериев `GUIDE_FOR_FINE_TUNING.md`, измерение совпадения ответов агента с авторскими решениями (превращает «персонализацию» из декларации в метрику)
- [ ] `SYSTEM_PROMPT.md` — готовый системный промпт, ссылающийся на контекст + правила агента («спроси, не додумывай»)
- [ ] `capture_case.py` — CLI-скаффолд нового кейса из `_template.md` с автопроверкой frontmatter, для потока «Слепок!»

### Потом (v1.0+ — если оправдано ростом)

- [ ] Пересмотреть RAG-подход (полноценная vector DB), **только если** корпус вырастет на порядки — не раньше (см. H002/N+1 Rule)
- [ ] Открытый вклад сообщества: абстрактные синтетические пары через Pull Request (лицензия уже CC BY-SA 4.0)

---

## 中文

### 现在（v0.x — 积极填充中）

- [x] 项目骨架：4 层（人格模型、案例、思维透镜、智能体训练指南）
- [x] `PERSONALITY_MODEL.yaml`：价值观、风险画像、25 条启发式规则、12 个模式、管理层
- [x] 代号「Слепок!」（"蓝图!"）— 在工作过程中直接把任务捕获为案例
- [x] 8 个真实案例（其中一个仍在进行中）
- [x] `training_data/` — 带反幻觉协议的合成数据集
- [x] `tools/` — 上下文加载器与 RAG-lite 检索（纯 Python，无重型依赖）
- [x] 根据代码评审加固 `tools/`：模式验证（严格失败）、第 4 层真正进入上下文、轻量词干处理、按状态加权/标记（rejected 不会被误当作建议）、`--compact`/`--json`/`--min-score`、13 个 pytest 测试、CI
- [ ] 完成案例 C008（超大型项目，40 万用户）
- [ ] 解决 `OPEN_QUESTIONS.md` 中的开放问题：P10/P11 阈值、P12 在金融场景、H006 疲劳信号
- [ ] 确认或替换剩余的草稿（`lenses/pareto-pragmatist-lens.draft.md`）
- [ ] 每日实践：至少每天新增 1 个案例或思维透镜（见 TELOS）

### 接下来（v0.y — 扩展与验证）

- [ ] 更多思维透镜 — 覆盖更多类型的决策（不止「多个未知数」）
- [ ] 用经人工验证的新批次扩充 `training_data/`
- [ ] 尝试在 `training_data/` 上对小型本地模型做微调或提示调优
- [ ] 在 `rag_query.py` 之上构建一个简单的 REPL/CLI，用于实际工作中的即时查询
- [ ] `evals/` — 校准工具：基于 `GUIDE_FOR_FINE_TUNING.md` 四条标准的问题集与评分标准，衡量智能体回答与作者决策的一致程度
- [ ] `SYSTEM_PROMPT.md` — 现成的系统提示词，链接上下文与智能体规则（「不确定就问，不要臆测」）
- [ ] `capture_case.py` — 基于 `_template.md` 的新案例脚手架 CLI，自动校验 frontmatter，服务于「蓝图！」捕获流程

### 更远的未来（v1.0+ — 仅在规模增长确有必要时）

- [ ] 重新评估 RAG 方案（完整的向量数据库）——**仅当**语料库规模增长数量级时才考虑，现在不需要（见 H002/N+1 Rule）
- [ ] 开放社区贡献：通过 Pull Request 提交抽象的合成数据对（许可证已是 CC BY-SA 4.0）

---

## English

### Now (v0.x — actively filling in)

- [x] Project skeleton: 4 layers (personality model, cases, lenses, agent fine-tuning guide)
- [x] `PERSONALITY_MODEL.yaml`: values, risk profile, 25 heuristics, 12 patterns, management layer
- [x] Codeword trigger — capture a task as a case right while working on it
- [x] 8 real cases (one still in progress)
- [x] `training_data/` — synthetic dataset with an anti-hallucination protocol
- [x] `tools/` — context loader and RAG-lite search (pure Python, no heavy dependencies)
- [x] `tools/` hardened per a code review: schema validation (fails loudly), Layer 4 actually reaches the context, lightweight stemming, status-based weighting/flag (rejected content can't look like advice), `--compact`/`--json`/`--min-score`, 13 pytest tests, CI
- [ ] Finish case C008 (mega-project, 400,000 users)
- [ ] Close open questions (`OPEN_QUESTIONS.md`): P10/P11 thresholds, P12 in finance, H006 fatigue signal
- [ ] Confirm or replace the one remaining draft (`lenses/pareto-pragmatist-lens.draft.md`)
- [ ] Daily practice: at least one case or lens per day (see TELOS)

### Next (v0.y — expansion and verification)

- [ ] More lenses — cover more decision types, not just "many unknowns"
- [ ] Grow `training_data/` with new human-verified batches
- [ ] Try fine-tuning or prompt-tuning a small local model on `training_data/`
- [ ] A simple REPL/CLI on top of `rag_query.py` for live queries during real work
- [ ] `evals/` — a calibration harness: a question set + a rubric from `GUIDE_FOR_FINE_TUNING.md`'s 4 criteria, measuring how closely agent answers match the authorial decisions
- [ ] `SYSTEM_PROMPT.md` — a ready-to-use system prompt referencing the context and the agent rules ("ask, don't guess")
- [ ] `capture_case.py` — a CLI that scaffolds a new case from `_template.md` with automatic frontmatter validation, for the "Слепок!" capture flow

### Later (v1.0+ — only if growth justifies it)

- [ ] Revisit the RAG approach (a full vector DB) **only if** the corpus grows by an order of magnitude — not before (see H002/N+1 Rule)
- [ ] Open community contribution: abstract synthetic pairs via Pull Request (already CC BY-SA 4.0 licensed)
