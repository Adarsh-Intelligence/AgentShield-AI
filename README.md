# AgentShield AI

### Production-Ready AI Agent Testing, Security & Evaluation Platform

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AgentShield AI is a developer-focused backend platform designed to test, evaluate, secure, and monitor AI agents and LLM-powered applications before and during production deployment.

It provides automated testing capabilities to identify:
* **Prompt Regressions**: Detect performance drops and newly introduced failures across prompt revisions.
* **Prompt Injection & Jailbreaks**: Validate whether adversarial instructions can escape system context boundaries.
* **Sensitive Data Leakage**: Detect exposure of confidential tokens, synthetic secrets, API keys, and PII.
* **Unsafe Tool-Calling**: Monitor and flag unauthorized or dangerous tool execution attempts.
* **AI Response Evaluation**: Multi-criteria evaluation (Exact match, Normalized text, Keyword validation, Semantic similarity, Structured JSON, and LLM-as-a-judge).
* **Performance & Token Cost Monitoring**: Track latency percentiles (Avg, P50, P95), token consumption, and configurable provider cost models.
* **Independent External Testing**: Connects to any external agent via Groq, Ollama, OpenAI-compatible APIs, or custom HTTP endpoints with full SSRF protection.

---

## 1. System Architecture

AgentShield AI is built as a **Modular Monolith** with strict domain isolation:

```
Client / Developer
       │
       ▼
 FastAPI Application
       │
       ▼
 Authentication & RBAC (Argon2id + JWT + Token Revocation)
       │
       ▼
 REST API Layer (/api/v1)
       │
       ▼
 Service Layer (Project, Agent, Evaluation, Regression, Security, Reports)
       │
 ┌─────┴──────────────────┬──────────────────────┐
 ▼                        ▼                      ▼
Response Evaluation   Regression Testing     Security Testing
Engine                Engine                 Engine
 └─────┬──────────────────┴──────────────────────┘
       ▼
 LLM Provider Layer (Groq, Ollama, OpenAI-Compatible, Mock)
       │
       ▼
 PostgreSQL 16 (Source of Truth) + Redis 7 (Celery Broker)
       │
       ▼
 Structured Reports, Prometheus Metrics & Audit Logs
```

---

## 2. Technology Stack

* **Language**: Python 3.12+ (3.10+ compatible runtime)
* **API Framework**: FastAPI, Pydantic v2, Uvicorn
* **Database & ORM**: PostgreSQL (Production) / SQLite (Local testing), SQLAlchemy 2.x, Alembic
* **Authentication**: Argon2id password hashing, JWT with refresh token rotation and revocation blocklist
* **Background Tasks**: Celery & Redis for asynchronous test run dispatch
* **Security & SSRF**: Cryptographic secret encryption (Fernet/AES-GCM), outbound DNS/IP validation, strict private IP blocking
* **Evaluation & AI**: SentenceTransformers, Scikit-learn, Groq API, Ollama, OpenAI-compatible providers, Mock provider
* **Monitoring**: Prometheus client metrics (`/metrics`), structured JSON logging, correlation IDs (`X-Request-ID`)
* **Deployment**: Multi-stage non-root Dockerfile, Docker Compose

---

## 3. Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint, middlewares & health routes
│   ├── config.py                # Pydantic BaseSettings environment configuration
│   │
│   ├── api/                     # REST API Layer
│   │   ├── deps.py              # Auth & project ownership verification dependencies
│   │   └── v1/
│   │       ├── router.py        # Master API v1 router
│   │       └── endpoints/       # Route handlers
│   │           ├── auth.py
│   │           ├── projects.py
│   │           ├── agents.py
│   │           ├── test_suites.py
│   │           ├── test_runs.py
│   │           ├── evaluations.py
│   │           ├── prompts.py
│   │           ├── security.py
│   │           ├── metrics.py
│   │           └── reports.py
│   │
│   ├── core/                    # Core Infrastructure
│   │   ├── security.py          # Argon2 hashing, JWT sign/verify, revocation registry
│   │   ├── exceptions.py        # Structured custom exception hierarchy
│   │   ├── logging.py           # Structured JSON logger & Prometheus metrics
│   │   └── middleware.py        # Security headers, correlation IDs, size limits
│   │
│   ├── database/                # Database Layer
│   │   ├── base.py              # DeclarativeBase, UUIDPrimaryKeyMixin, TimestampMixin
│   │   └── session.py           # Engine & SessionLocal pool configuration
│   │
│   ├── models/                  # SQLAlchemy 2.0 Database Models
│   │   ├── user.py              # User & RBAC roles (admin, developer)
│   │   ├── project.py           # Project multi-tenancy & ownership
│   │   ├── agent.py             # Agent & encrypted AgentCredential
│   │   ├── test_suite.py        # TestSuite collection
│   │   ├── test_case.py         # TestCase definitions & evaluation criteria
│   │   ├── test_run.py          # TestRun lifecycle & status tracking
│   │   ├── test_result.py       # Individual test case outcomes & token usage
│   │   ├── prompt.py            # Immutable PromptVersion records
│   │   ├── security.py          # SecurityFinding records
│   │   ├── metric.py            # PerformanceMetric aggregates (P50/P95)
│   │   ├── report.py            # Structured EvaluationReport entities
│   │   └── audit.py             # AuditLog actions
│   │
│   ├── schemas/                 # Pydantic v2 Request/Response Schemas
│   ├── services/                # Business Logic Services
│   ├── engines/                 # Evaluation & Security Testing Engines
│   │   ├── response_evaluator.py# Multi-criteria response evaluators
│   │   ├── regression_engine.py # Prompt version comparison & regression detection
│   │   ├── security_engine.py   # Security scanning & probe battery
│   │   ├── tool_evaluator.py    # Tool selection & argument validation
│   │   └── performance_engine.py# Latency percentiles & cost estimation
│   │
│   ├── providers/               # LLM Provider Abstractions
│   │   ├── base.py              # BaseLLMProvider & ProviderResponse
│   │   ├── groq_provider.py     # Groq API client
│   │   ├── ollama_provider.py   # Ollama API client
│   │   ├── openai_provider.py   # OpenAI-compatible API client
│   │   ├── mock_provider.py     # Deterministic mock provider for CI/tests
│   │   └── provider_factory.py  # Provider factory with SSRF checks
│   │
│   ├── tasks/                   # Celery & Asynchronous Background Tasks
│   │   ├── celery_app.py        # Celery application configuration
│   │   └── test_tasks.py        # Background task runners
│   │
│   └── utils/                   # Cryptography & Network Utilities
│       ├── encryption.py        # Fernet credential encryption
│       └── ssrf.py              # Outbound URL & IP validation
│
├── migrations/                  # Alembic Migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py# Full schema creation
│
├── tests/                       # Automated Test Suite (100% Pass)
│   ├── conftest.py              # Fixtures, test client & isolated in-memory DB
│   ├── unit/                    # Evaluator, SSRF, & Encryption unit tests
│   ├── security/                # Auth bypass, tenant isolation & security engine tests
│   └── integration/             # Full lifecycle API workflow & regression tests
│
├── scripts/                     # Operational utilities
├── Dockerfile                   # Multi-stage non-root production Dockerfile
├── docker-compose.yml           # PostgreSQL, Redis, Celery Worker, Web & Migration
├── requirements.txt             # Pinned production dependencies
├── .env.example                 # Environment variable template
└── README.md
```

---

## 4. Quickstart & Local Installation

### Prerequisites
* Python 3.12+ (or Python 3.10+)
* Git
* (Optional) Docker & Docker Compose

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/your-org/agentshield-ai.git
cd agentshield-ai

python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment configuration:
```bash
cp .env.example .env
```

Generate a secure secret key and Fernet encryption key:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```
Paste the keys into your `.env` file.

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive OpenAPI documentation is immediately accessible at:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Docker Deployment

AgentShield AI comes configured with a complete production deployment stack featuring PostgreSQL, Redis, Celery workers, automatic database migrations, and health checks.

### Running with Docker Compose

```bash
# 1. Create .env from template
cp .env.example .env

# 2. Build and launch all services
docker compose up -d --build
```

### Services Started:
1. **postgres**: PostgreSQL 16 database storing all platform entities.
2. **redis**: Redis 7 message broker and cache.
3. **migration**: Dedicated migration container running `alembic upgrade head` before web starts.
4. **web**: FastAPI application running with non-root user `appuser` on port 8000.
5. **worker**: Celery worker executing background evaluation runs and scans.

### Checking Deployment Health:
```bash
# Check status of containers
docker compose ps

# Inspect logs
docker compose logs -f web

# Probe health endpoint
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

---

## 6. API Workflow & Endpoints Guide

All API endpoints are prefixed with `/api/v1`.

### 1. Authentication
* `POST /api/v1/auth/register`: Register user (`admin` or `developer`).
* `POST /api/v1/auth/login`: Authenticate and receive JWT access and refresh tokens.
* `POST /api/v1/auth/refresh`: Rotate refresh token and obtain fresh access token.
* `POST /api/v1/auth/logout`: Revoke token.
* `GET /api/v1/auth/me`: Get current authenticated user profile.

**Example Registration Request:**
```json
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "dev@company.com",
  "password": "SuperSecretPassword123!",
  "full_name": "Lead AI Engineer",
  "role": "developer"
}
```

### 2. Project Management
* `POST /api/v1/projects`: Create project.
* `GET /api/v1/projects`: List owned projects.
* `GET /api/v1/projects/{project_id}`: Get project details.
* `PATCH /api/v1/projects/{project_id}`: Update project configuration.
* `DELETE /api/v1/projects/{project_id}`: Delete project.

### 3. Agent Registration
* `POST /api/v1/projects/{project_id}/agents`: Register an external agent.
* `GET /api/v1/projects/{project_id}/agents`: List registered agents.
* `POST /api/v1/projects/{project_id}/agents/{agent_id}/test-connection`: Ping external model.

**Example Register Agent (SSRF Protected & Credential Encrypted):**
```json
POST /api/v1/projects/{project_id}/agents
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "name": "Customer Support LLM",
  "provider_type": "groq",
  "api_endpoint": "https://api.groq.com/openai/v1",
  "model_name": "llama3-70b-8192",
  "api_key": "gsk_YourSecretGroqKey",
  "timeout_seconds": 30
}
```

### 4. Test Suites & Test Cases
* `POST /api/v1/projects/{project_id}/test-suites`: Create test suite.
* `POST /api/v1/projects/{project_id}/test-suites/{suite_id}/cases`: Add test case.

**Supported Evaluation Methods:**
* `exact_match`: Verbatim string equality after whitespace trimming.
* `normalized_text`: Punctuation, capitalization, and whitespace invariant match.
* `keyword_validation`: Enforces presence of required keywords and absence of forbidden keywords.
* `semantic_similarity`: Cosine distance embedding similarity against threshold.
* `structured_json`: Validates output against expected JSON schema and keys.
* `llm_judge`: Evaluates response using an evaluator model rubric.

### 5. Executing Test Runs
* `POST /api/v1/projects/{project_id}/test-runs`: Trigger evaluation run.
  * Set `"async_mode": false` for synchronous execution.
  * Set `"async_mode": true` for queued background job execution via Celery/Redis.
* `GET /api/v1/projects/{project_id}/test-runs/{run_id}`: Retrieve results, pass rate, latency percentiles, and token accounting.

### 6. Prompt Versioning & Regression Testing
* `POST /api/v1/projects/{project_id}/prompts`: Create an immutable prompt version.
* `POST /api/v1/projects/{project_id}/prompts/compare`: Execute regression comparison.

**Example Regression Compare Request:**
```json
POST /api/v1/projects/{project_id}/prompts/compare
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "baseline_prompt_version_id": "<PROMPT_V1_ID>",
  "candidate_prompt_version_id": "<PROMPT_V2_ID>",
  "test_suite_id": "<SUITE_ID>",
  "agent_id": "<AGENT_ID>",
  "pass_rate_tolerance": 0.05
}
```

**Example Comparison Response:**
```json
{
  "baseline_version": "SupportPrompt (v1.0)",
  "candidate_version": "SupportPrompt (v2.0)",
  "baseline_pass_rate": 1.0,
  "candidate_pass_rate": 0.85,
  "pass_rate_difference": -0.15,
  "is_regression": true,
  "regression_summary": "Regression detected! Candidate version 'v2.0' introduced 1 new failure(s). Pass rate changed by -15.00%.",
  "new_failures_count": 1,
  "resolved_failures_count": 0,
  "latency_difference_ms": -12.4,
  "token_usage_difference": -45,
  "cost_difference": -0.000035,
  "details": [
    {
      "test_case_id": "case-1",
      "test_case_name": "Return Policy Check",
      "baseline_passed": true,
      "candidate_passed": false,
      "baseline_score": 1.0,
      "candidate_score": 0.4,
      "status": "REGRESSION"
    }
  ]
}
```

### 7. AI Security Testing
* `POST /api/v1/projects/{project_id}/security/scan`: Execute automated red-team security test battery.
* `GET /api/v1/projects/{project_id}/security/findings`: Query detected vulnerabilities filtered by severity (`critical`, `high`, `medium`, `low`, `informational`).

**Test Categories Covered:**
1. **Prompt Injection**: System prompt override and context delimiter escape attempts.
2. **Sensitive Data Leakage**: Detection of synthetic secrets, API keys, passwords, and PII.
3. **Jailbreak Testing**: Resistance to DAN personas, hypothetical academic bypasses, and ethical constraint evasion.
4. **Unsafe Tool Invocation**: Flagging attempts to invoke dangerous system tools (`exec`, `bash`, `rm`, `delete`).
5. **Output Safety**: Verification of toxic and prohibited content guardrails.

---

## 7. Running Tests

AgentShield AI contains a comprehensive automated test battery covering unit, security, integration, and performance workflows.

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
# Unit tests
pytest tests/unit

# Security & Access Control tests
pytest tests/security

# Integration tests
pytest tests/integration
```

---

## 8. Security & Reliability Controls

* **Argon2id Password Hashing**: State-of-the-art password security resistant to GPU/ASIC cracking.
* **Token Revocation Registry**: Allows immediate invalidation of JWT tokens on logout or security events.
* **Multi-Tenant Project Ownership**: Access is restricted strictly to resource owners, verified at the dependency layer.
* **Outbound SSRF Protection**:
  * Blocks all private RFC 1918 addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
  * Blocks loopback addresses (`127.0.0.0/8`, `::1`).
  * Blocks link-local addresses (`169.254.0.0/16`, `fe80::/10`).
  * Blocks cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`).
  * Enforces DNS resolution checking before executing outbound HTTP requests.
* **Stored Credential Encryption**: API keys are encrypted at rest using Fernet symmetric encryption.
* **Security Headers**: HSTS, Content-Security-Policy, X-Frame-Options (`DENY`), and X-Content-Type-Options (`nosniff`).
* **Non-Root Docker Container**: Application runs as unprivileged user `appuser` (UID 10001).

---

## 9. License

This project is licensed under the MIT License.

