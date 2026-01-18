# UZ AI Factory — Дневник Разработки

## 📅 13.01.2026 — День 1

### 🎯 Цель сессии:
Собрать MVP-конвейер для поиска болей узбекского рынка

### ✅ Выполнено:
- [x] Базовый Dashboard UI (React + Vite)
- [x] Zustand store с XP-системой
- [x] Реструктуризация под uz-ai-factory
- [ ] Агенты сбора данных

### 📊 Источники данных (бесплатные):
| Источник | Агент | Лимит | Статус |
|----------|-------|-------|--------|
| Google Trends | google_trends.py | Без лимита | ⏳ |
| YouTube API | youtube_scanner.py | 10k/день | ⏳ |
| Yandex.uz | yandex_uz.py | Без лимита | ⏳ |
| Facebook Groups | fb_groups.py | Без лимита | ⏳ |
| Telegram | tg_scanner.py | Без лимита | ⏳ |
| RSS (daryo, kun) | rss_scraper.py | Без лимита | ⏳ |
| Auto-Discovery | auto_discover.py | — | ⏳ |

### 🔍 Ключевые запросы для Узбекистана:
- учёба онлайн, работа на дому, доставка еды
- подготовка к ЕНТ, курсы узбекского, фриланс
- ремонт квартир Ташкент, продажа одежды instagram
- кредит онлайн, оплата коммунальных
- IT курсы для девочек, английский для мигрантов

### 🐛 Дневник Ошибок:
| Время | Ошибка | Гипотеза | Решение |
|-------|--------|----------|---------|
| — | — | — | — |

---

## 📈 Прогресс: 20% | XP: +300

## 📅 14.01.2026 — День 2

- Выявлено категорий: 8
- Топ боли: Образование (85), Работа (65), Бизнес (35)
- Сгенерирован отчет: `data/top_pains_2026-01-14.md`

### 🐛 Дневник Ошибок:
| Время | Ошибка | Гипотеза | Решение |
|-------|--------|----------|---------|
| 12:45 | 404 models/gemini-3.0-flash not found | Неверные названия моделей | Использовал `debug_gemini.py` для получения списка. Правильные: `gemini-3-flash-preview` |
| 13:10 | Batch parsing error | Пустой ответ от API | Добавил обработку исключений и проверку API ключа |

---

## 📈 Прогресс: 35% | XP: +650

- [x] CLI интерфейс для быстрого тестирования.

### 📊 Результаты теста:
- **Тренды**: Найдены инсайты по ВТО, золотым запасам и военным учениям.
- **Боли**: Выявлены проблемы с блокировками соцсетей и регистрацией блогеров.
- **Copycats**: Найдены 4 EdTech модели (Uchi.ru, Skyeng и др.) для адаптации в Узб.

### 🐛 Дневник Ошибок:
| Время | Ошибка | Гипотеза | Решение |
|-------|--------|----------|---------|
| 13:00 | Отсутствие контекста СНГ | Агенты искали только по Узб | Добавил параметр `region="CIS"` и расширил промпты |

---

## 📈 Прогресс: 55% | XP: +1200

---

## 📅 15.01.2026 — День 3

### 🎯 Цель сессии:
Унификация UI/UX архитектуры (Variant D: Split View)

### ✅ Выполнено:

#### Миграция библиотек:
- [x] Все агенты (5 штук) мигрированы с `google.generativeai` на `google.genai`
- [x] Обновлены imports, client init, safety settings

#### Unified Store:
- [x] Расширен `useAppStore.ts` для Factory, Intelligence, Projects
- [x] Добавлено 15+ новых actions (setFactoryIdea, addFactoryLog, completeFactoryPhase, etc.)
- [x] Интеграция XP: `completeFactoryPhase(phase, xpReward)` 

#### WebSocket Service:
- [x] Создан `src/services/websocket.ts` — Singleton класс
- [x] Auto-reconnect с exponential backoff (max 5 попыток)
- [x] XP rewards при `phase_complete` сообщениях

#### Perplexity API:
- [x] Добавлены endpoints: `POST /api/intelligence/scan`, `GET /api/intelligence/pains`
- [x] Новый метод `full_scan(topic, region)` в `PerplexitySuite`
- [x] Кэширование результатов в `PUBLIC_DATA_DIR/latest_scan.json`

#### Layout Refactor:
- [x] Рефакторинг `App.tsx` → nested routes с `<Outlet />`
- [x] Создано 4 View компонента: `DashboardView`, `FactoryView`, `IntelligenceView`, `ProjectsView`
- [x] Обновлен `Sidebar.tsx` с новой навигацией
- [x] Комплексные CSS стили в `Views.css`

#### Iteration Loop:
- [x] Добавлен `refine_prd(original_prd, qa_feedback)` в `cpo.py`
- [x] `boss.py`: `MAX_ITERATIONS=3`, автоматический рефайн при QA FAIL
- [x] `server.py`: WebSocket handler с iteration loop

#### Fixes:
- [x] Environment-based CORS (`CORS_ORIGINS` env variable)
- [x] TypeScript ошибки исправлены (unused imports)

### 📁 Созданные файлы:
```
src/
├── views/
│   ├── DashboardView.tsx
│   ├── FactoryView.tsx
│   ├── IntelligenceView.tsx
│   ├── ProjectsView.tsx
│   └── Views.css
├── services/
│   └── websocket.ts
```

### 🔄 Изменённые файлы:
- `src/App.tsx` — nested routes
- `src/stores/useAppStore.ts` — unified state  
- `src/components/dashboard/Layout.tsx` — Outlet
- `src/components/dashboard/Sidebar.tsx` — new nav
- `api/server.py` — intelligence API + iteration loop
- `agents/boss.py` — iteration loop
- `agents/cpo.py` — refine_prd method
- `agents/perplexity_suite.py` — full_scan method

### ✅ Build Status:
```
npm run build
✓ 2125 modules transformed
✓ built in 18.99s
Exit code: 0
```

---

## 📈 Прогресс: 85% | XP: +2500

### 📋 Осталось (Nice-to-Have):
- [ ] Rate limiting API
- [ ] Error toasts в UI
- [ ] Multi-user support (сейчас localStorage)
- [ ] Database вместо file-based storage

---

## 🏗 Архитектура (текущая)

```
Frontend (React + Vite)
├── DashboardView   → Stats, Projects, Insights
├── FactoryView     → Input | Console | Artifacts
├── IntelligenceView→ Perplexity Scan + Create Startup
└── ProjectsView    → Project list + Artifact viewer

Backend (FastAPI)
├── /api/projects/* → CRUD для проектов
├── /api/intelligence/* → Perplexity Suite
└── /api/factory/ws → WebSocket для streaming

AI Agents
├── TheBoss         → Orchestrator (with iteration loop)
├── CPO             → PRD + refine_prd
├── TechLead        → Tech Spec
├── CMO             → Marketing Plan
├── SalesHead       → Sales Kit
├── QALead          → Quality Audit
└── PerplexitySuite → Market Intelligence
```

---

## 📅 15.01.2026 (вечер) — Vertex AI Integration

### 🎯 Цель сессии:
Полная интеграция Vertex AI ($1000 кредит) — Agent Builder RAG + Smart Collector

### ✅ Выполнено:

#### Phase 1: Agent Builder RAG
- [x] Создан `services/vector_search_service.py` — UzSearchService
- [x] Интеграция RAG в `boss.py` через `_enrich_context_with_rag()`
- [x] GCS Bucket: `gs://uz-ai-factory-knowledge`
- [x] Vertex AI Data Store: `uz-factory-knowledge`
- [x] Обновлён `config.py` с `DATA_STORE_ID`

#### Smart Collector (Автономный агент)
- [x] Создан `agents/smart_collector.py` — поиск PDF в Google, загрузка в GCS
- [x] Google Custom Search API интеграция
- [x] Планировщик: `--schedule` для еженедельного обновления

#### Загруженные документы:
- ✅ Законы о сельском хозяйстве Узбекистана
- ✅ Аграрное финансирование (World Bank)
- ✅ QARORI (налоговый кодекс)
- ✅ Финтех рынок Узбекистана
- ✅ Закон об электронном правительстве
- ✅ Исследование ООН 2024
- ✅ 10+ других PDF документов

### 📁 Созданные файлы:
```
services/
└── vector_search_service.py  # RAG сервис для Agent Builder

agents/
└── smart_collector.py        # Автономный сборщик документов

setup_gcp.py                  # Скрипт настройки GCP инфраструктуры
```

### 🔄 Изменённые файлы:
- `agents/boss.py` — добавлен `_enrich_context_with_rag()`
- `agents/config.py` — добавлены `DATA_STORE_ID`, `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID`

### 🐛 Дневник Ошибок:
| Время | Ошибка | Гипотеза | Решение |
|-------|--------|----------|---------|
| 20:10 | gcloud не установлен | CLI отсутствует | Использовал Python SDK |
| 20:30 | Custom Search API 403 | API не активирован | Включили API в консоли GCP |

---

## 📈 Прогресс: 95% | XP: +3500

### 🏗 Обновлённая архитектура:

```
AI Agents
├── TheBoss         → Orchestrator + RAG Context
├── CPO             → PRD + refine_prd
├── TechLead        → Tech Spec
├── CMO             → Marketing Plan
├── SalesHead       → Sales Kit
├── QALead          → Quality Audit
├── PerplexitySuite → Market Intelligence
└── SmartCollector  → Auto PDF Search → GCS → Vertex AI

Vertex AI Integration
├── Agent Builder   → RAG Data Store (auto-indexed)
├── GCS Bucket      → gs://uz-ai-factory-knowledge
└── Custom Search   → Auto PDF collection
```

### 📋 Следующие шаги:
- [ ] Phase 2: Batch Prediction для анализа болей
- [ ] Phase 3: Миграция агентов на Vertex SDK
- [ ] Тестирование RAG с реальными запросами

---

## 📅 15.01.2026 (ночь) — Ralph Wiggum Loop

### 🎯 Цель сессии:
Внедрение Ralph Wiggum Pattern для автономных self-correcting агентов

### ✅ Выполнено:

#### Ralph Loop v3 (`agents/ralph_loop.py`)
- [x] JSON Sanitization (очистка Markdown-оберток)
- [x] Sliding Window (только последняя ошибка)
- [x] Oscillation Detection (проверяет ВСЮ историю)
- [x] Emergency Stop (90% similarity)
- [x] Loop_ID телеметрия
- [x] Timeouts (60s per iteration)
- [x] Cost tracking (`total_tokens`, `estimated_cost_usd`)

#### Интеграция в Boss
- [x] `boss.py --ralph` флаг
- [x] `run_with_ralph()` метод
- [x] `_ralph_iteration()` wrapper

### 📁 Созданные файлы:
```
agents/
├── ralph_loop.py      # 280 lines, production-ready
└── smart_collector.py # Auto PDF search
```

### ✅ Тест:
```
🧪 Testing RalphLoop v3...
[21:06:43] [0d017602] [START] Task: Write a poem...
[21:06:44] [0d017602] [SUCCESS] Completed in 3 iterations

✅ Success: True | 🔢 Iterations: 3 | ⏱️ Elapsed: 1.01s
```

---

## 📈 Прогресс: 98% | XP: +4500

---

## 📅 15.01.2026 (ночь) — Batch Prediction

### 🎯 Цель сессии:
Массовый анализ данных через Vertex AI с 75% экономией

### ✅ Выполнено:

#### BatchAnalyzerPro (`agents/batch_analyzer.py`)
- [x] Job Registry (idempotency — защита от дублей)
- [x] Pre-flight validation (проверка токенов)
- [x] GCS auto-upload
- [x] Subfolder collection (обход Vertex выходной структуры)
- [x] Cost estimation (расчёт стоимости до запуска)
- [x] CLI interface

### 💰 Экономика:
- Online: $0.625 / 1000 постов
- Batch: $0.155 / 1000 постов (экономия 75%)

### 📁 Созданные файлы:
```
agents/
└── batch_analyzer.py  # 380 lines, production-ready
data/batch/
├── input/             # JSONL файлы для отправки
├── output/            # Результаты от Vertex
└── job_registry.json  # Трекинг джобов
```

---

## 📈 Прогресс: 100% | XP: +5000 🎉

---

## 📅 15.01.2026 (ночь) — Vertex SDK Migration

### 🎯 Цель сессии:
Унификация всех агентов под Vertex AI SDK

### ✅ Выполнено:

#### VertexClient (`agents/vertex_client.py`)
- [x] Service Account authentication (credentials.json)
- [x] Auto fallback (SA → API Key)
- [x] Singleton pattern
- [x] Token tracking
- [x] Unified для всех агентов

### ✅ Тест:
```
🔑 Using Service Account: credentials.json
✅ Vertex AI Client initialized (Service Account)
   Using Vertex: True
   Project: nodal-reserve-471921-n1
```

---

## 🎉 ИТОГ ДНЯ 3 — Vertex AI полностью интегрирован!

| Компонент | Строки | Описание |
|-----------|--------|----------|
| `ralph_loop.py` | 280 | Автономный self-correcting loop |
| `batch_analyzer.py` | 380 | Массовый анализ с 75% экономией |
| `smart_collector.py` | 200 | Авто-сбор PDF в GCS |
| `vector_search_service.py` | 130 | RAG для Agent Builder |
| `vertex_client.py` | 240 | Unified Vertex AI клиент |
| **ИТОГО** | **1230** | Production-ready код |

---

## 🚀 СТРАТЕГИЧЕСКАЯ КАРТА РАЗВИТИЯ (v2.0)

### 🔴 КРИТИЧЕСКИ ВАЖНО (Неделя 1)

#### 1. Database Migration
**Проблема:** Сейчас file-based storage (JSON). Не масштабируется.
**Решение:** PostgreSQL + SQLAlchemy
```
- Таблицы: projects, pains, documents, jobs
- Миграции через Alembic
- Connection pooling
```

#### 2. Auth & Multi-User
**Проблема:** Сейчас localStorage. Один пользователь.
**Решение:** Supabase Auth или Firebase
```
- JWT токены
- Row-level security
- Team workspaces
```

#### 3. API Rate Limiting
**Проблема:** Нет защиты от перегрузки.
**Решение:** Redis + slowapi
```
- 60 req/min для free tier
- 1000 req/min для premium
```

---

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ (Неделя 2)

#### 4. Agent Orchestration v2 (CrewAI/LangGraph)
**Проблема:** Boss.py — линейный пайплайн.
**Решение:** Graph-based orchestration
```
- Параллельные агенты
- Conditional branching
- Human-in-the-loop
```

#### 5. Memory Layer (Long-term)
**Проблема:** Агенты не помнят предыдущие сессии.
**Решение:** Vector DB + User Memory
```
- ChromaDB/Pinecone для embeddings
- User preference learning
- Project history context
```

#### 6. Monitoring & Observability
**Проблема:** Нет видимости в production.
**Решение:** LangSmith или Langfuse
```
- Trace каждого вызова
- Cost tracking per project
- Error alerting
```

---

### 🟢 РАСШИРЕНИЕ (Неделя 3-4)

#### 7. Multi-Language Support
**Решение:** Добавить узбекский, казахский, киргизский
```
- Промпты на 4 языках
- Автодетект языка пользователя
- Локализованные отчёты
```

#### 8. Marketplace Integration
**Решение:** API для партнёров
```
- REST API для внешних приложений
- Webhook уведомления
- Billing integration
```

#### 9. Mobile App (PWA)
**Решение:** Progressive Web App
```
- Offline support
- Push notifications
- Camera for document scan
```

---

### 🔵 MOONSHOT (Месяц 2+)

#### 10. Fine-tuned UZ Model
**Описание:** Дообучить модель на узбекских данных
```
- 100K+ узбекских текстов
- Vertex AI tuning
- Специализация на локальных болях
```

#### 11. Agentic Marketplace
**Описание:** Платформа для покупки/продажи AI-агентов
```
- Agent templates
- Revenue sharing
- Community marketplace
```

---

## 🏗 Финальная архитектура (v2.0)

```
┌─────────────────────────────────────────────────────────────┐
│                     UZ AI FACTORY v2.0                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + Vite + PWA)                              │
│  ├── Dashboard      → Stats, XP, Leaderboard                │
│  ├── Factory        → Ralph Mode | Standard | Batch         │
│  ├── Intelligence   → Perplexity + RAG Search               │
│  └── Marketplace    → Agent Store (future)                  │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + PostgreSQL + Redis)                     │
│  ├── /api/auth/*         → Supabase Auth                    │
│  ├── /api/projects/*     → CRUD + History                   │
│  ├── /api/agents/*       → Agent Orchestration              │
│  ├── /api/batch/*        → Batch Prediction Jobs            │
│  └── /api/factory/ws     → WebSocket + Ralph Streaming      │
├─────────────────────────────────────────────────────────────┤
│  AI Layer                                                   │
│  ├── VertexClient        → Unified SDK (SA auth)            │
│  ├── RalphLoop           → Self-correcting autonomy         │
│  ├── BatchAnalyzer       → 75% cost savings                 │
│  ├── SmartCollector      → Auto knowledge base              │
│  └── UzSearchService     → RAG from Agent Builder           │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure                                             │
│  ├── GCS                 → gs://uz-ai-factory-knowledge     │
│  ├── Vertex AI           → Agent Builder, Batch, Models     │
│  ├── PostgreSQL          → Projects, Jobs, Users            │
│  └── Redis               → Rate limiting, Cache, Sessions   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Прогресс: 100% (Phase 1) | XP: +5500 🎉

**Следующий milestone:** Database Migration + Auth (Неделя 1)

---

## 📅 16.01.2026 — День 4

### 🎯 Цель сессии:
Автономная работа (6 часов) — Унификация агентов, Тестирование, Сканеры

### ✅ Выполнено:

#### Час 1: BaseAgent + Унификация
- [x] Создан `agents/base.py` — базовый класс `BaseAgent`
- [x] Создан `agents/exceptions.py` — кастомные исключения (`RateLimitError`, `TimeoutError`, `AIClientError`)
- [x] `AgentResult` — стандартизированный формат ответа
- [x] `PromptMixin` — переиспользуемые промпты

#### Час 2: Миграция всех агентов
- [x] `agents/cmo.py` → наследует от `BaseAgent`
- [x] `agents/sales_head.py` → наследует от `BaseAgent`
- [x] `agents/qa_lead.py` → наследует от `BaseAgent`
- [x] `agents/cpo.py` → наследует от `BaseAgent`
- [x] `agents/tech_lead.py` → наследует от `BaseAgent`
- [x] `agents/pain_extractor.py` → наследует от `BaseAgent`
- [x] Удалены локальные инициализации `genai` клиента
- [x] Все AI-вызовы через `self.generate()`

#### Час 3: Error Handling + Retry
- [x] Установлен `tenacity` для retry-логики
- [x] `@retry` декоратор в `BaseAgent.generate()`:
  - 3 попытки с экспоненциальным backoff (4-10 сек)
  - Обработка: `RateLimitError`, `TimeoutError`, `AIClientError`

#### Час 4: Test Infrastructure
- [x] `tests/conftest.py` — фикстуры (`mock_vertex_client`, `base_agent`)
- [x] `tests/test_base_agent.py` — тесты инициализации, retry, build_result
- [x] `tests/test_ralph.py` — тесты oscillation, max_iterations, JSON parsing
- [x] `pytest.ini` — конфигурация
- [x] **Результат**: 8/8 тестов пройдено ✅

#### Час 5: Scanners
- [x] `agents/lex_scanner.py` — парсинг Lex.uz (законодательство)
- [x] `agents/xarid_scanner.py` — парсинг Xarid.uz (госзакупки)
- ⚠️ Публичные API отсутствуют, используется HTML-парсинг

#### Час 6: Health Check
- [x] `agents/health_check.py` — проверка системы:
  - Environment Variables: ✅
  - Vertex AI Connection: ✅ (Service Account)
  - Agent Imports: ✅

### 📁 Созданные файлы:
```
agents/
├── base.py           # NEW (~180 lines)
├── exceptions.py     # NEW (~50 lines)
├── lex_scanner.py    # NEW (~65 lines)
├── xarid_scanner.py  # NEW (~75 lines)
├── health_check.py   # NEW (~100 lines)

tests/
├── __init__.py       # NEW
├── conftest.py       # NEW (~30 lines)
├── test_base_agent.py # NEW (~30 lines)
├── test_ralph.py     # NEW (~70 lines)

pytest.ini            # NEW (~3 lines)
```

### 🔄 Изменённые файлы:
- `agents/vertex_client.py` — фикс импортов, fallback для `response.text`
- `agents/cmo.py` — наследование от BaseAgent
- `agents/sales_head.py` — наследование от BaseAgent
- `agents/qa_lead.py` — наследование от BaseAgent
- `agents/cpo.py` — наследование от BaseAgent
- `agents/tech_lead.py` — наследование от BaseAgent
- `agents/pain_extractor.py` — наследование от BaseAgent, добавлен `Any` в imports

### 🐛 Дневник Ошибок:
| Время | Ошибка | Гипотеза | Решение |
|-------|--------|----------|---------|
| 22:00 | `ModuleNotFoundError: config` | pytest не видит root | Добавлен `sys.path.insert(0, BASE_DIR)` в `vertex_client.py` |
| 22:05 | `NameError: Dict not defined` | Пропущен import | Добавлен `from typing import Dict, Any` |
| 22:07 | `NameError: Any not defined` | Пропущен import в pain_extractor | Добавлен `Any` в typing imports |
| 12:03 | `NoneType has no attribute 'lower'` | `response.text` может быть None | Добавлен `return response.text or ""` |

### ✅ Health Check Output:
```
🏥 UZ AI Factory Health Check
============================
1. Environment Variables:
   ✅ GOOGLE_APPLICATION_CREDENTIALS
   ✅ VERTEX_PROJECT_ID
   ✅ VERTEX_LOCATION

2. Vertex AI Connection:
   ✅ Vertex AI Client initialized (Service Account)
   ✅ Vertex AI is reachable and generating

3. Agents Integrity:
   ✅ All agents imported successfully
============================
Health Check Complete.
```

---

## 📈 Прогресс: 100% (Phase 2) | XP: +6500 🎉

**Статус системы:** Готова к деплою ✅

---

## 📅 16.01.2026 (вечер) — MCP Integration Phase 1

### 🎯 Цель сессии:
Внедрение Model Context Protocol для унификации инструментов агентов

### ✅ Выполнено:

#### MCP Package (`agents/mcp/`)
- [x] `mcp_to_gemini.py` — Sanitizer схем для Vertex AI совместимости
  - Удаляет `anyOf`, `oneOf`, `allOf` (ломают Vertex API)
  - Удаляет `default`, `const` (путают модель)
  - Рекурсивная очистка nested properties
- [x] `mcp_bridge.py` — Connection Manager
  - Singleton pattern для connection pooling
  - Namespacing тулов (`server__toolname`)
  - Signal handling (SIGINT) для предотвращения zombie processes
  - Sync wrappers для совместимости с текущим sync кодом
- [x] `config.py` — Конфигурации серверов
  - filesystem, memory, brave-search, fetch, puppeteer, github
  - Windows/Linux совместимость
  - Auto-validation API keys
- [x] `mcp_enabled_agent.py` — Base class для MCP-агентов
  - Tool discovery и registration
  - Tool dispatch для Gemini function calls

#### Тесты
- [x] `tests/test_mcp.py` — **10/10 тестов прошли** ✅
  - TestSanitizeSchema: 6 тестов
  - TestMCPBridge: 3 теста
  - TestMCPToolToGemini: 1 тест

### 📁 Созданные файлы:
```
agents/mcp/
├── __init__.py           # Package exports
├── mcp_to_gemini.py      # Schema sanitizer (~100 lines)
├── mcp_bridge.py         # Connection manager (~280 lines)
├── config.py             # Server configs (~150 lines)
├── mcp_enabled_agent.py  # Base agent class (~170 lines)

mcp_config.json           # Root config for IDE
tests/test_mcp.py         # Unit tests (~130 lines)
```

### 🔧 Hardened Features (по рекомендациям Senior Review):
| Проблема | Решение |
|----------|---------|
| Vertex AI не переносит anyOf/oneOf | `sanitize_schema()` удаляет их |
| Zombie processes при crash | Signal handling + atexit cleanup |
| Конфликты имён тулов | Namespacing: `server__toolname` |
| Sync/Async несовместимость | Sync wrappers в MCPBridge |

### 📋 Следующие шаги (Phase 2):
- [ ] `pip install mcp` — установка SDK
- [ ] Получить Brave API Key
- [ ] Интеграция brave-search + fetch серверов
- [ ] Создать MarketResearcher агент

---

## 📈 Прогресс: 100% (Phase 3) | XP: +7500 🎉

---

## 📅 16.01.2026 (вечер) — Agent Skills System

### 🎯 Цель сессии:
Внедрение Data-Driven Architecture через Agent Skills — переиспользуемые Markdown-инструкции с lazy loading

### ✅ Выполнено:

#### SkillManager Service (`services/skill_manager.py`)
- [x] Singleton pattern для глобального кэша
- [x] Lazy loading — полный контент загружается только по запросу
- [x] YAML frontmatter parsing (name, description, triggers, tools_required)
- [x] TTL-based garbage collection через `ActiveSkill` dataclass
- [x] CLI интерфейс для тестирования

#### BaseAgent Integration (`agents/base.py`)
- [x] `use_skill(skill_name)` — как Vertex AI Function Calling tool (НЕ regex!)
- [x] `clear_active_skills()` — очистка контекста после задачи
- [x] `garbage_collect_skills()` — автоматическое удаление по TTL
- [x] `get_skills_for_prompt()` — Discovery Phase (только названия)
- [x] `get_skill_tool_schema()` — JSON schema для Vertex AI

#### First Skills
- [x] `uz-procurement-analyzer` — анализ госзакупок Xarid.uz
- [x] `vertex-batch-operator` — Batch Prediction с JSONL
- [x] `prd-standard-uz` — стандарт PRD для Узбекистана

### 📁 Созданные файлы:
```
services/
└── skill_manager.py           # ~280 lines

.agent/skills/
├── uz-procurement-analyzer/
│   └── SKILL.md               # ~60 lines
├── vertex-batch-operator/
│   └── SKILL.md               # ~90 lines
└── prd-standard-uz/
    └── SKILL.md               # ~100 lines

tests/
└── test_skill_manager.py      # ~180 lines, 11 tests
```

### 🔄 Изменённые файлы:
- `agents/base.py` — добавлены Skills методы (~140 новых строк)

### ✅ Test Results:
```
python -m pytest tests/ -v
============================= 29 passed in 16.54s =============================
```

### 🏗 Архитектура Skills:
```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT SKILLS FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DISCOVERY PHASE (Lightweight)                            │
│     ├── Agent calls get_skills_for_prompt()                  │
│     └── Returns: skill names + descriptions (saves tokens)   │
│                                                              │
│  2. ACTIVATION PHASE (Function Calling)                      │
│     ├── Agent calls use_skill("prd-standard-uz")             │
│     ├── SkillManager loads full SKILL.md content             │
│     └── Returns: detailed instructions + tracks TTL          │
│                                                              │
│  3. EXECUTION PHASE                                          │
│     └── Agent follows skill instructions                     │
│                                                              │
│  4. CLEANUP PHASE (Garbage Collection)                       │
│     ├── clear_active_skills() — manual cleanup               │
│     └── garbage_collect_skills() — TTL-based auto cleanup    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 🧩 SKILL.md Format:
```yaml
---
name: skill-name
description: Short description for Discovery Phase
context: "When to use this skill"
triggers:
  - "keyword1"
  - "keyword2"
tools_required:
  - tool_name
version: "1.0"
---

# Skill Title

## Detailed Instructions
...
```

### 📋 Следующие шаги:
- [ ] Интеграция `generate_with_skills()` в CPO
- [ ] Semantic Router для 50+ skills (embeddings)
- [ ] Marketplace: импорт/экспорт skill packages

---

## 📅 16.01.2026 (ночь) — Autonomous Skills (Agentic Pattern)

### 🎯 Цель сессии:
Переключение с "Imperative" на "Declarative/Agentic" паттерн — модель САМА решает какой скилл вызвать

### ✅ Выполнено (по рекомендации Senior Review):

#### BaseAgent Improvements
- [x] `generate_with_skills()` — автономный цикл, модель решает какие скиллы загружать
- [x] `use_skill()` — теперь возвращает список доступных скиллов при ошибке (self-correction)
- [x] `clear_active_skills(purge_history=True)` — реально удаляет текст скиллов из истории
- [x] `_conversation_history` — отслеживание диалога для multi-turn
- [x] `_skill_message_ids` — трекинг сообщений со скиллами для GC
- [x] `reset_conversation()` — полный сброс истории

### 📊 Паттерн использования:

```python
# ✅ ПРАВИЛЬНО (Agentic) — модель САМА решает
response = agent.generate_with_skills(
    prompt="Create PRD for food delivery app",
    max_skill_calls=3,
    auto_cleanup=True
)

# ❌ НЕПРАВИЛЬНО (Imperative) — программист решает
prd_skill = agent.use_skill("prd-standard-uz")  # Hardcoded!
```

### ✅ Test Results:
```
python -m pytest tests/ -v
============================= 29 passed in 32.10s =============================
```

---

## 📈 Прогресс: 100% (Phase 5) | XP: +9500 🎉

---

## 📅 17.01.2026 — Фаза 1-2: Стабилизация и Боевое Тестирование

### 🎯 Цель сессии:
Перевести V2 из прототипа в боевую систему. Убить V1, добавить мониторинг, провести battle testing.

### ✅ Фаза 1: Неделя Стабилизации (5 вечеров за 1 ночь)

#### Вечер 1: "Убить V1"
- [x] Создана ветка `legacy/v1` с бэкапом старого кода
- [x] `agents/cpo.py` → re-export CPOv2 (V1 код удалён)
- [x] `config.py` — убран `ENABLE_V2_AGENTS` флаг
- [x] `boss.py` — удалены все V1/V2 conditionals, V2 теперь default

#### Вечер 2: "Battle Tests"
- [x] `tools/battle_report.py` — сбор метрик из всех worktrees
- [x] `tools/real_test_cases.py` — 5 реальных задач для Узбекистана
- [x] `tools/cleanup_old_tasks.py` — автоочистка старых задач (cron)

#### Вечер 3: "Circuit Breaker для Skills"
- [x] `services/circuit_breaker.py` — защита от cascade failures Vertex AI
- [x] `/api/health/vertex` endpoint — статус Circuit Breaker
- [x] Паттерн CLOSED → OPEN → HALF_OPEN для graceful recovery

#### Вечер 4: "Meta Heartbeat"
- [x] `boss.monitor_task()` — проверяет heartbeat агентов
- [x] Автоматическое убийство зависших агентов (>30 сек без heartbeat)
- [x] Обновление META.yml с `status: failed, reason: heartbeat_timeout`

#### Вечер 5: "Cleanup & Observability"
- [x] `docs/README_V2.md` — документация новой архитектуры
- [x] `.env.example` — шаблон переменных окружения

### ✅ Фаза 2: Боевое Тестирование

#### Неделя 1: Feature Flags & Rollback
- [x] `tools/daily_report.py` — ежедневный отчёт (для cron)
- [x] `agents/auto_discovery.py` — автоматический скан болей

#### Battle Test Results (5/5 успешно):
```
| Task ID     | Title                          | Status    | XP |
|-------------|--------------------------------|-----------|-----|
| battle-001  | EdTech для ЕНТ                | completed | 50  |
| battle-002  | CRM для дистрибьюторов        | completed | 50  |
| battle-003  | Агрегатор доставки            | completed | 50  |
| battle-004  | Финтех для кредитных союзов   | completed | 50  |
| battle-005  | IoT для полива                | completed | 50  |
```
**Total XP: 250**

### 🐛 Исправленные баги:
| Время | Ошибка | Решение |
|-------|--------|---------|
| 01:42 | UnicodeEncodeError cp1251 emoji | `sys.stdout.reconfigure(encoding='utf-8')` |
| 01:45 | META.yml not found (wrong cwd) | AgentRunner теперь запускает из project root |

### 📊 Git History:
```
6635ea4 fix: AgentRunner cwd and CPO encoding for Windows
764ab8d feat: Phase 2 - Auto-Discovery, Daily Report
b108897 feat: Phase 1 - Circuit Breaker, Health, Heartbeat, README V2
0131b6b feat: Battle testing tools
bf2305a BREAKING: Remove V1 agents, V2 is now default
v0.9.0-finish-line (tag)
```

### 📁 Новые файлы:
```
services/circuit_breaker.py     # Circuit Breaker pattern
tools/battle_report.py          # Сбор метрик
tools/real_test_cases.py        # Генерация тест-кейсов
tools/cleanup_old_tasks.py      # Автоочистка (cron)
tools/daily_report.py           # Ежедневный отчёт
agents/auto_discovery.py        # Автоматический скан болей
docs/README_V2.md               # Документация V2
.env.example                    # Шаблон конфигурации
```

### 🚀 Как использовать:
```bash
# Battle testing
python tools/real_test_cases.py    # Создать 5 задач
python tools/battle_report.py      # Собрать отчёт

# Auto-discovery (cron)
python agents/auto_discovery.py --dry-run
0 9 * * 1-5 python agents/auto_discovery.py

# Daily report (cron)
python tools/daily_report.py
0 23 * * * python tools/daily_report.py
```

---

## 📈 Прогресс: V2 Production Ready | XP: +10,000 🎉

---

## 🔧 [2026-01-19] n8n Orchestration Layer

### 🎯 Цель:
Развертывание n8n как центральной платформы оркестрации AI-агентов с интеграцией бесплатных LLM провайдеров.

### ✅ Выполнено:

#### 1. Docker Stack (n8n + SearxNG + Cloudflare)
```yaml
# docker-compose.yml
services:
  n8n:        # http://localhost:5678
  searxng:    # http://localhost:8080 (Unlimited FREE search)
  cloudflared: # Cloudflare Tunnel
```

#### 2. Интегрированные API:
| Provider | Модель | Лимит/день | Назначение |
|----------|--------|------------|------------|
| **Groq** | llama-3.1-8b | 14.4K req | Массовые задачи |
| **Groq** | llama-3.3-70b | 1K req | Сложные задачи |
| **Tavily** | Search API | 1K/мес | Deep Research |
| **Exa.ai** | Neural Search | $10 credits | Semantic Search |
| **SearxNG** | Multi-engine | ∞ | Self-hosted поиск |

#### 3. Созданные воркфлоу:
```
n8n-cloudflare/
├── qualifizer_router_v2.json   # Intent Router + Agents
├── deep_research_agent.json    # Multi-source research
├── groq_research_agent.json    # Groq + Tavily pipeline
└── docker-compose.yml          # Full stack
```

#### 4. Стратегия экономии LLM:
```
90% → Groq FREE (llama-3.1-8b, llama-3.3-70b)
5%  → Gemini Pro (backup)
5%  → Vertex AI ($1000 credit, только RAG)
```

### 📁 Новые файлы:
```
n8n-cloudflare/
├── docker-compose.yml          # Docker stack
├── .env.example                 # API keys template
├── config.yml                   # Cloudflare Tunnel config
├── qualifizer_router_v2.json   # Main router workflow
├── deep_research_agent.json    # Research workflow
└── groq_research_agent.json    # Groq + Tavily workflow
```

### 🚀 Как использовать:
```bash
cd n8n-cloudflare
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d

# Access:
# n8n: http://localhost:5678
# SearxNG: http://localhost:8080
```

---

## 📈 Прогресс: n8n Orchestration Ready | XP: +15,000 🚀


