# Architecture Decision Records (ADR)

## ADR-001: Выбор технологического стека

### Статус
Принято

### Контекст
Необходимо выбрать технологии для реализации кроссплатформенного приложения трекера здоровья с AI-наставником.

### Решение

#### Backend: FastAPI (Python)
**Причины выбора:**
- Асинхронная производительность
- Автоматическая генерация OpenAPI документации
- Встроенная валидация через Pydantic
- Отличная интеграция с LangChain для AI
- Простота развертывания

**Альтернативы:**
- Django: Слишком тяжеловесный для REST API
- Flask: Требует много дополнительных библиотек
- Node.js: Менее удобен для AI/ML интеграций

#### Desktop: Tauri + React
**Причины выбора:**
- Малый размер бандла (<10MB vs 50MB+ Electron)
- Нативная производительность через Rust
- Безопасность (no Node.js в runtime)
- React - популярный и хорошо поддерживаемый

**Альтернативы:**
- Electron: Слишком тяжелый, проблемы с безопасностью
- Flutter Desktop: Менее зрелый для десктопа
- Native (Qt/GTK): Сложная поддержка трех платформ

#### iOS: Native Swift/SwiftUI
**Причины выбора:**
- Лучшая производительность и UX
- Полный доступ к iOS API (HealthKit, Widgets)
- Долгосрочная поддержка Apple
- SwiftUI - современный декларативный UI

**Альтернативы:**
- React Native: Ограничения в нативных функциях
- Flutter: Больше размер приложения
- PWA: Нет доступа к многим нативным API

#### Database: PostgreSQL
**Причины выбора:**
- Надежность и производительность
- JSONB для гибких структур данных
- Полнотекстовый поиск из коробки
- Отличная поддержка в SQLAlchemy

**Альтернативы:**
- MySQL: Менее функциональный
- MongoDB: Избыточен для структурированных данных
- SQLite: Не подходит для многопользовательского API

### Последствия
- (+) Современный, производительный стек
- (+) Хорошая экосистема и документация
- (+) Легко найти разработчиков
- (-) Три разные кодовые базы для клиентов
- (-) Необходимость знания нескольких языков

---

## ADR-002: Архитектура системы

### Статус
Принято

### Контекст
Определить общую архитектуру системы для обеспечения масштабируемости и надежности.

### Решение
**Трехуровневая архитектура с API-first подходом:**

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  Desktop (Tauri) | iOS (Swift) | Web    │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│           Application Layer             │
│         FastAPI REST API                │
│    Business Logic | Auth | LLM          │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│            Data Layer                   │
│   PostgreSQL | Redis | File Storage     │
└─────────────────────────────────────────┘
```

**Принципы:**
1. **Separation of Concerns** - четкое разделение слоев
2. **API-First** - все через REST API
3. **Stateless** - сервер не хранит состояние сессии
4. **Cache-First** - агрессивное кэширование

### Последствия
- (+) Легко масштабировать горизонтально
- (+) Можно независимо развивать клиенты
- (+) Единая бизнес-логика на сервере
- (-) Сетевая задержка для всех операций
- (-) Необходимость в offline-first стратегии

---

## ADR-003: Стратегия аутентификации

### Статус
Принято

### Контекст
Выбрать безопасный и удобный механизм аутентификации.

### Решение
**JWT с Refresh Token Pattern**

```python
# Access Token (15 минут)
{
  "sub": "user_id",
  "type": "access",
  "exp": 1234567890,
  "iat": 1234567890
}

# Refresh Token (7 дней)
{
  "sub": "user_id",
  "type": "refresh",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Flow:**
1. Login → получить access + refresh tokens
2. Использовать access token для API запросов
3. При истечении access token → использовать refresh token
4. Refresh token ротация при обновлении
5. Logout → инвалидация refresh token

**Безопасность:**
- Хранение: Keychain (iOS), Credential Store (Desktop)
- HTTPS only
- Secure + HttpOnly cookies для web (будущее)
- Rate limiting на auth endpoints

### Последствия
- (+) Stateless аутентификация
- (+) Короткоживущие access tokens
- (+) Возможность отзыва через refresh tokens
- (-) Сложность управления двумя токенами
- (-) Необходимость refresh flow на клиентах

---

## ADR-004: Offline-First стратегия

### Статус
Принято

### Контекст
Приложение должно работать без постоянного интернета.

### Решение
**Локальная БД + синхронизация**

```typescript
// Desktop: SQLite через Tauri
// iOS: CoreData/SQLite

interface SyncStrategy {
  // 1. Локальное сохранение всех изменений
  saveLocal(data: any): Promise<void>

  // 2. Добавление в очередь синхронизации
  addToSyncQueue(operation: SyncOperation): Promise<void>

  // 3. Периодическая синхронизация
  sync(): Promise<SyncResult>

  // 4. Разрешение конфликтов
  resolveConflict(local: any, remote: any): any
}
```

**Правила конфликтов:**
- Last-Write-Wins для простых полей
- Merge для массивов (meals, exercises)
- User choice для критических данных

**Синхронизация:**
- При запуске приложения
- При восстановлении соединения
- Каждые 5 минут при активности
- Перед выходом

### Последствия
- (+) Полноценная работа offline
- (+) Быстрый отклик UI
- (+) Сохранность данных
- (-) Сложность разрешения конфликтов
- (-) Дублирование данных

---

## ADR-005: LLM интеграция

### Статус
Принято

### Контекст
Интегрировать AI-наставника для анализа и рекомендаций.

### Решение
**LangChain + Multiple LLM Providers**

```python
class LLMStrategy:
    providers = [
        OpenAIProvider(model="gpt-4-turbo"),     # Primary
        AnthropicProvider(model="claude-3"),      # Fallback
        LocalProvider(model="llama3")            # Offline
    ]

    async def generate(self, prompt: str) -> str:
        for provider in self.providers:
            try:
                return await provider.generate(prompt)
            except ProviderError:
                continue
        raise AllProvidersFailedError()
```

**Кэширование:**
- Redis для готовых summary (TTL 24 часа)
- Embeddings для похожих запросов
- Prompt versioning для A/B тестов

**Промпты:**
- Structured output (JSON)
- Few-shot examples
- Temperature 0.7 для креативности
- Max tokens limits

### Последствия
- (+) Резилиентность через fallback
- (+) Возможность offline через local LLM
- (+) Контроль расходов через кэширование
- (-) Зависимость от внешних API
- (-) Необходимость мониторинга качества

---

## ADR-006: Структура данных

### Статус
Принято

### Контекст
Спроектировать гибкую и расширяемую структуру данных.

### Решение
**Day-centric модель**

```
Day (основная сущность)
├── Meals[]
│   └── MealItems[]
├── Exercises[]
│   └── ExerciseSets[]
├── WaterIntakes[]
├── SleepRecords[]
├── MoodRecords[]
├── Notes[]
└── LLMSummary
```

**Принципы:**
- Один день = одна запись (уникальность по user_id + date)
- Soft delete для истории
- JSONB для гибких полей
- Нормализация только где критично

**Версионирование:**
```sql
-- Для критических изменений
CREATE TABLE day_history (
    id SERIAL PRIMARY KEY,
    day_id INTEGER REFERENCES days(id),
    version INTEGER,
    data JSONB,
    changed_at TIMESTAMPTZ
);
```

### Последствия
- (+) Простота запросов для дня
- (+) Гибкость через JSONB
- (+) История изменений
- (-) Дублирование в агрегациях
- (-) Необходимость в индексах

---

## ADR-007: Тестирование

### Статус
Принято

### Контекст
Обеспечить качество и надежность системы.

### Решение
**Пирамида тестирования**

```
        E2E (5%)
       /    \
    Integration (25%)
   /          \
Unit Tests (70%)
```

**Стратегия:**
- Unit: Бизнес-логика, утилиты
- Integration: API endpoints, БД
- E2E: Критические user flows

**Инструменты:**
- Backend: pytest, pytest-asyncio
- Desktop: Jest, React Testing Library
- iOS: XCTest, XCUITest
- API: Postman/Newman

**CI Requirements:**
- Coverage > 80% для unit tests
- Все тесты проходят перед merge
- Performance regression tests

### Последствия
- (+) Высокая надежность
- (+) Быстрая обратная связь
- (+) Уверенность в рефакторинге
- (-) Время на написание тестов
- (-) Поддержка тестовых данных

---

## ADR-008: Мониторинг и логирование

### Статус
Принято

### Контекст
Обеспечить наблюдаемость системы в продакшене.

### Решение
**Structured Logging + Metrics**

```python
# Структурированные логи
logger.info("user_action", extra={
    "user_id": user.id,
    "action": "day_created",
    "date": day.date,
    "duration_ms": 145
})

# Метрики
metrics.increment("api.requests", tags=["endpoint:create_day"])
metrics.histogram("api.response_time", 145, tags=["endpoint:create_day"])
```

**Stack:**
- Logs: JSON → Elasticsearch
- Metrics: Prometheus + Grafana
- Traces: OpenTelemetry
- Errors: Sentry

**Алерты:**
- API response time > 1s
- Error rate > 1%
- LLM failures > 10/hour
- Database connections > 80%

### Последствия
- (+) Быстрое обнаружение проблем
- (+) Данные для оптимизации
- (+) Аудит действий пользователей
- (-) Дополнительная инфраструктура
- (-) Costs for storage

---

## ADR-009: Безопасность данных

### Статус
Принято

### Контекст
Защитить персональные данные пользователей.

### Решение
**Defense in Depth**

```python
# 1. Encryption at rest
class EncryptedField(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value:
            return encrypt(value)

    def process_result_value(self, value, dialect):
        if value:
            return decrypt(value)

# 2. Encryption in transit
# - TLS 1.3 minimum
# - Certificate pinning on mobile

# 3. Data minimization
# - Удаление старых refresh tokens
# - Архивирование старых данных
# - Анонимизация при удалении аккаунта

# 4. Access controls
# - Row-level security
# - API rate limiting
# - Input validation
```

**GDPR Compliance:**
- Right to erasure
- Data portability (export)
- Consent management
- Privacy by design

### Последствия
- (+) Защита пользовательских данных
- (+) Соответствие регуляциям
- (+) Доверие пользователей
- (-) Сложность реализации
- (-) Performance overhead

---

## ADR-010: Deployment стратегия

### Статус
Принято

### Контекст
Определить процесс развертывания и обновления.

### Решение
**GitOps + Progressive Rollout**

```yaml
# Environments
Development → Staging → Production

# Deployment
- GitHub Actions для CI/CD
- Docker containers
- Kubernetes для orchestration
- Blue-Green deployment

# Desktop Updates
- Tauri Updater
- Semantic versioning
- Delta updates
- Rollback capability

# iOS Updates
- TestFlight for beta
- Phased release (7 days)
- Feature flags
```

**Мониторинг деплоя:**
- Canary deployment (5% → 25% → 100%)
- Automatic rollback при ошибках
- Feature flags для постепенного включения

### Последствия
- (+) Безопасные деплои
- (+) Быстрый rollback
- (+) A/B testing возможности
- (-) Сложность инфраструктуры
- (-) Необходимость в DevOps expertise

---

## ADR-011: Масштабирование

### Статус
Планируется

### Контекст
Подготовиться к росту нагрузки.

### Решение
**Horizontal Scaling Strategy**

```
Load Balancer (nginx)
         ↓
┌────────┴────────┐
│                 │
API Server 1    API Server N
│                 │
└────────┬────────┘
         ↓
   PostgreSQL (Master)
         ↓
   Read Replicas

+ Redis Cluster (Cache)
+ CDN (Static assets)
```

**Оптимизации:**
- Database connection pooling
- Query optimization (EXPLAIN ANALYZE)
- Caching strategy (Redis)
- CDN для статики
- Background jobs (Celery)

**Метрики масштабирования:**
- < 100ms p95 response time
- > 99.9% uptime
- Support 10K concurrent users

### Последствия
- (+) Готовность к росту
- (+) High availability
- (+) Performance SLA
- (-) Инфраструктурные costs
- (-) Операционная сложность

---

## Принципы принятия решений

1. **Простота > Сложность** - выбираем простое решение, если оно решает 80% кейсов
2. **Безопасность по умолчанию** - все новые features проходят security review
3. **Data-Driven** - решения основаны на метриках и данных
4. **User-First** - приоритет пользовательскому опыту
5. **Maintainability** - код должен быть понятен новым разработчикам

## Процесс принятия ADR

1. **Proposal** - любой может предложить ADR
2. **Discussion** - обсуждение в течение 3 дней
3. **Decision** - голосование tech lead + senior devs
4. **Implementation** - после принятия обязательно к исполнению
5. **Review** - пересмотр через 6 месяцев или при изменении контекста