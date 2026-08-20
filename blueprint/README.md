# Personal Engineering Blueprint

**[Русский](#русский) | [中文](#中文) | [English](#english)**

---

## Русский

Цифровой слепок инженерных и управленческих решений — не база фактов, а модель того, **почему** и **как** принимаются решения: инженерные (архитектура, выбор стека, код-ревью) и управленческие (приоритизация, кадровые вызовы, кризис-менеджмент) вопросы, с точки зрения архитектора, ведущего команду.

Это не просто документация, а практика построения и настройки AI-агентов.

### Структура (4 слоя)

1. [`PERSONALITY_MODEL.yaml`](PERSONALITY_MODEL.yaml) — **Слой 1.** Ценности, приоритеты, риск-профиль, когнитивные искажения, эвристики принятия решений.
2. [`cases/`](cases/) — **Слой 2.** Коллекция реальных кейсов «Решение → Рассуждение» (RAG-база).
3. [`lenses/`](lenses/) — **Слой 3.** Ментальные фильтры — вопросы, которые задаются себе перед решением определённого типа.
4. [`GUIDE_FOR_FINE_TUNING.md`](GUIDE_FOR_FINE_TUNING.md) — **Слой 4.** Как исправлять агента, обученного на этом материале, и куда агент логирует свои сомнения ([`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)).

### Статус

Скелет создан 2026-08-20, наполняется в реальном времени. Кейсы и линзы пишутся только автором — вживую или под диктовку; AI-агент не сочиняет их содержание.

### Правило для агента, работающего с этим слепком

Этот агент — не автор, но должен задавать те же вопросы, что и он, и приходить к тому же выводу в большинстве случаев. Если не уверен — обязан спросить, а не додумывать.

---

## 中文

一份工程与管理决策的数字快照——不是事实的堆砌，而是关于**为什么**以及**如何**做出决策的模型：作为带领团队的架构师，涉及工程问题（架构设计、技术栈选择、代码评审）与管理问题（优先级排序、人员挑战、危机管理）。

这不仅是文档，更是构建和调优 AI 智能体的实践。

### 结构（4 层）

1. [`PERSONALITY_MODEL.yaml`](PERSONALITY_MODEL.yaml) — **第 1 层。** 价值观、优先级、风险画像、认知偏差、决策启发式规则。
2. [`cases/`](cases/) — **第 2 层。** 真实案例集「决策 → 推理」（RAG 知识库）。
3. [`lenses/`](lenses/) — **第 3 层。** 思维透镜——在做出某类决策之前会问自己的问题。
4. [`GUIDE_FOR_FINE_TUNING.md`](GUIDE_FOR_FINE_TUNING.md) — **第 4 层。** 如何纠正基于此材料训练的智能体，以及智能体应把疑问记录在哪里（[`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)）。

### 状态

骨架创建于 2026-08-20，正在实时填充中。案例和思维透镜只能由作者本人撰写——亲自写或口述；AI 智能体不会替其编造内容。

### 使用此蓝图的智能体应遵循的规则

这个智能体不是作者本人，但应该提出与作者相同的问题，并在多数情况下得出相同的结论。如果不确定——必须提问，而不是臆测。

---

## English

A digital blueprint of engineering and management decisions — not a database of facts, but a model of **why** and **how** decisions get made: engineering questions (architecture, tech-stack choices, code review) and management questions (prioritization, people challenges, crisis management), from the perspective of an architect leading a team.

This isn't documentation — it's practice in building and tuning AI agents.

### Structure (4 layers)

1. [`PERSONALITY_MODEL.yaml`](PERSONALITY_MODEL.yaml) — **Layer 1.** Values, priorities, risk profile, cognitive biases, decision-making heuristics.
2. [`cases/`](cases/) — **Layer 2.** A collection of real "Decision → Reasoning" cases (a RAG knowledge base).
3. [`lenses/`](lenses/) — **Layer 3.** Mental filters — questions asked of oneself before a certain type of decision.
4. [`GUIDE_FOR_FINE_TUNING.md`](GUIDE_FOR_FINE_TUNING.md) — **Layer 4.** How to correct an agent trained on this material, and where the agent logs its doubts ([`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)).

### Status

Skeleton created 2026-08-20, being filled in in real time. Cases and lenses are written only by the author — live or dictated; the AI agent does not invent their content.

### Rule for an agent working with this blueprint

This agent is not the author, but should ask the same questions the author would, and reach the same conclusion most of the time. If unsure — it must ask, not guess.
