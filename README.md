# AgentShield AI 🛡️

### Production-Ready AI Agent Testing, Security & Evaluation Platform.  and then next will be coming 

[![CI/CD Tests](https://img.shields.io/badge/Tests-33%20passed%20(100%25)-brightgreen.svg)](#7-running-automated-tests)
[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AgentShield AI** is an enterprise-grade backend testing, evaluation, security, and observability platform designed specifically for AI agents and LLM-powered applications.

It operates as an **independent evaluation harness** that connects to external AI applications via configurable APIs (Groq, Ollama, OpenAI-compatible endpoints) without executing untrusted user code or running internal single-model dependencies.

---

## 📑 Table of Contents

- [Key Capabilities](#-key-capabilities)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Quickstart & Local Installation](#-quickstart--local-installation)
- [Docker Production Deployment](#-docker-production-deployment)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [API Reference & Workflow Guide](#-api-reference--workflow-guide)
  - [1. Authentication & RBAC](#1-authentication--rbac)
  - [2. Project Management](#2-project-management)
  - [3. AI Agent Registration & SSRF Shielding](#3-ai-agent-registration--ssrf-shielding)
  - [4. Test Suites & Test Cases](#4-test-suites--test-cases)
  - [5. Test Execution (Sync & Celery Background)](#5-test-execution-sync--celery-background)
  - [6. Prompt Versioning & Regression Detection](#6-prompt-versioning--regression-detection)
  - [7. Automated AI Security Red-Teaming](#7-automated-ai-security-red-teaming)
  - [8. Tool-Calling Evaluation](#8-tool-calling-evaluation)
  - [9. Performance & Cost Monitoring](#9-performance--cost-monitoring)
  - [10. Evaluation Reports & CSV Export](#10-evaluation-reports--csv-export)
  - [11. Health & Prometheus Probes](#11-health--prometheus-probes)
- [Running Automated Tests](#-running-automated-tests)
- [Security & Defense Controls](#-security--defense-controls)
- [License](#-license)

---

## 🚀 Key Capabilities

* **Deterministic & Semantic Response Evaluation**: Supports 6 evaluation methodologies: Exact Match, Normalized Text, Keyword/Forbidden Boundary Enforcement, Semantic Embedding Similarity, Structured JSON Schema validation, and LLM-as-a-judge.
* **Prompt Regression Detection**: Tracks prompt versions immutably and compares candidate versions against baselines across test suites to detect regressions, score drops, new failures, and cost variances.
* **Automated AI Security Red-Teaming**: Probes for Prompt Injections, Synthetic Secret & PII Leakage, Jailbreak attempts (DAN, academic framing), Unsafe Tool Invocation, and Prohibited Output Safety violations. Controlled Garak adapter integrated.
* **Safe Tool-Calling Verification**: Evaluates model tool selection, parameter correctness, and unauthorized dangerous tool attempts (e.g., shell/exec/file deletion) using mocked execution.
* **Observability & Cost Tracking**: Collects latency metrics with **P50 (Median)** and **P95** percentiles, token consumption, and configurable provider pricing tables.
* **Enterprise Security**: Built with Argon2id password hashing, JWT refresh-token rotation, an in-memory revocation blocklist, Fernet-encrypted stored credentials, and outbound SSRF protection against RFC 1918 subnets and cloud metadata endpoints.
* **Scalable Asynchronous Architecture**: Powered by Celery and Redis with PostgreSQL as the execution state source of truth.

---

## 🏛️ System Architecture

![AgentShield AI Backend Architecture](AgentShield%20AI%20Backend%20Architecture.png)

```
Client / Developer / CI-CD Pipeline
                 │
                 ▼
       FastAPI Application (:8000)
                 │
                 ▼
    Authentication & Authorization
      ├── Argon2id Password Hashing
      ├── JWT (Access + Refresh Token Rotation)
      └── RBAC (Admin, Developer) & Project Ownership
                 │
                 ▼
           REST API Layer (/api/v1)
                 │
                 ▼
           Service Layer
  ┌──────────────┼────────────────────────┐
  ▼              ▼                        ▼
Response       Prompt Regression        Security Testing
Evaluation     Engine                   Engine (Garak Adapter)
  │              │                        │
  └──────────────┼────────────────────────┘
                 ▼
        LLM Provider Layer
  ├── Groq API
  ├── Ollama (Local Inference)
  ├── OpenAI-Compatible Endpoints
  └── Deterministic Mock Provider (CI/Tests)
                 │
                 ▼
  ┌──────────────┴────────────────────────┐
  ▼                                       ▼
PostgreSQL 16 (Source of Truth)     Redis 7 + Celery Workers
  │
  ▼
Structured Reports (JSON/CSV) & Prometheus Metrics (/metrics)
```

---

## 💻 Technology Stack

| Layer | Component | Description |
|---|---|---|
| **Language** | Python 3.12+ (3.10+ compatible) | Core programming language |
| **Framework** | FastAPI 0.115+ & Pydantic v2 | High-performance async web framework & validation |
| **Web Server** | Uvicorn (standard workers) | Production ASGI server |
| **Database** | PostgreSQL 16 / SQLite | Relational database (UUID keys, JSON types) |
| **ORM & Migrations** | SQLAlchemy 2.0 & Alembic | Data mapping & version-controlled schema migrations |
| **Task Queue** | Celery 5.4+ & Redis 7 | Distributed asynchronous task execution & broker |
| **Authentication** | Argon2id & PyJWT | Robust password hashing & token rotation |
| **Cryptography** | Fernet (AES-128-CBC + HMAC) | Secret credential encryption at rest |
| **NLP & Vectors** | SentenceTransformers & Scikit-learn | Semantic cosine similarity & token metrics |
| **AI Providers** | Groq, Ollama, OpenAI-compatible | Provider abstraction with SSRF protection |
| **Metrics & Logs** | Prometheus Client & JSON Logger | Real-time monitoring (`/metrics`) & correlation IDs |
| **Deployment** | Docker & Docker Compose | Multi-stage non-root containerized deployment |

---

## 📂 Project Directory Structure

```
agentshield-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application, CORS, middlewares, health endpoints
│   │   ├── config.py                # BaseSettings configuration management
│   │   │
│   │   ├── api/
│   │   │   ├── deps.py              # JWT authentication & project ownership dependencies
│   │   │   └── v1/
│   │   │       ├── router.py        # Master API v1 router
│   │   │       └── endpoints/       # Route handlers
│   │   │           ├── auth.py          # User registration, login, refresh, logout
│   │   │           ├── projects.py      # Project multi-tenancy & management
│   │   │           ├── agents.py        # Agent registration & ping connectivity
│   │   │           ├── test_suites.py   # Test suites and test cases CRUD
│   │   │           ├── test_runs.py     # Test run execution (sync/async)
│   │   │           ├── evaluations.py   # Standalone ad-hoc response evaluation
│   │   │           ├── prompts.py       # Prompt versions & regression comparisons
│   │   │           ├── security.py      # Automated security scanning & findings
│   │   │           ├── metrics.py       # Aggregated performance & latency metrics
│   │   │           └── reports.py       # Structured JSON reports & CSV export
│   │   │
│   │   ├── core/
│   │   │   ├── security.py          # Argon2id hashing, JWT token rotation, revocation list
│   │   │   ├── exceptions.py        # Custom AgentShield exception hierarchy
│   │   │   ├── logging.py           # Structured JSON logger & Prometheus metrics
│   │   │   └── middleware.py        # Security headers, correlation IDs, request size limit
│   │   │
│   │   ├── database/
│   │   │   ├── base.py              # DeclarativeBase, UUIDPrimaryKeyMixin, TimestampMixin
│   │   │   └── session.py           # Engine configuration & SessionLocal generator
│   │   │
│   │   ├── models/                  # SQLAlchemy 2.0 ORM Entities
│   │   │   ├── user.py              # User model with RBAC roles
│   │   │   ├── project.py           # Multi-tenant project entity
│   │   │   ├── agent.py             # Agent & encrypted AgentCredential
│   │   │   ├── test_suite.py        # TestSuite entity
│   │   │   ├── test_case.py         # TestCase rules and evaluation criteria
│   │   │   ├── test_run.py          # TestRun lifecycle and status tracking
│   │   │   ├── test_result.py       # TestResult records with token accounting
│   │   │   ├── prompt.py            # Immutable PromptVersion records
│   │   │   ├── security.py          # SecurityFinding vulnerability records
│   │   │   ├── metric.py            # PerformanceMetric aggregates (P50/P95)
│   │   │   ├── report.py            # EvaluationReport entity
│   │   │   └── audit.py             # AuditLog entity
│   │   │
│   │   ├── schemas/                 # Pydantic v2 schemas for all API payloads
│   │   ├── services/                # Business logic services for each domain
│   │   │
│   │   ├── engines/                 # Evaluation & Testing Engines
│   │   │   ├── response_evaluator.py# Multi-method evaluation engine
│   │   │   ├── regression_engine.py # Prompt version comparison & regression detection
│   │   │   ├── security_engine.py   # Vulnerability scan battery & Garak adapter
│   │   │   ├── tool_evaluator.py    # Tool selection & argument validation
│   │   │   └── performance_engine.py# Statistical latency percentiles & cost engine
│   │   │
│   │   ├── providers/               # LLM Provider Integrations
│   │   │   ├── base.py              # BaseLLMProvider & ProviderResponse
│   │   │   ├── groq_provider.py     # Groq API client
│   │   │   ├── ollama_provider.py   # Ollama API client
│   │   │   ├── openai_provider.py   # OpenAI-compatible API client
│   │   │   ├── mock_provider.py     # Deterministic mock provider for tests
│   │   │   └── provider_factory.py  # Provider factory with SSRF checks
│   │   │
│   │   ├── tasks/                   # Celery & Asynchronous Tasks
│   │   │   ├── celery_app.py        # Celery app configuration
│   │   │   └── test_tasks.py        # Asynchronous test job runners
│   │   │
│   │   └── utils/                   # Cryptography & Security Utilities
│   │       ├── encryption.py        # Fernet secret key encryption
│   │       └── ssrf.py              # Outbound destination IP & DNS validator
│   │
├── migrations/                      # Alembic Database Migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py    # Complete database schema migration
│
├── tests/                           # Pytest Automated Test Suite (33/33 Passing)
│   ├── conftest.py                  # Test database fixtures, mock client & users
│   ├── unit/                        # Evaluator, SSRF, & Encryption unit tests
│   ├── security/                    # Auth bypass, tenant isolation & security engine tests
│   └── integration/                 # End-to-end API workflows & regression tests
│
├── scripts/
│   └── init_admin.py                # Admin user initialization utility
├── Dockerfile                       # Production multi-stage minimal Dockerfile
├── docker-compose.yml               # PostgreSQL, Redis, Celery, Migration & Web stack
├── requirements.txt                 # Pinned Python dependencies
├── .env.example                     # Environment template
├── pytest.ini                       # Test configuration
└── README.md
```

---

## ⚡ Quickstart & Local Installation

### Prerequisites
* Python 3.12+ (or 3.10+)
* Git
* PostgreSQL (or SQLite for local lightweight testing)
* Redis (optional for Celery background tasks)

### 1. Clone the Repository
```bash
git clone https://github.com/Adarsh-Intelligence/AgentShield-AI-v1.git
cd AgentShield-AI-v1
```

### 2. Create and Activate Virtual Environment
```bash
# Linux / macOS:
python -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
Generate cryptographic keys for your `.env`:
```bash
# Generate SECRET_KEY:
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate ENCRYPTION_KEY:
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Launch the Application
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API documentation will be available at:
* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🐳 Docker Production Deployment

AgentShield AI is fully containerized with a multi-stage non-root `Dockerfile` and `docker-compose.yml` that orchestrates:
1. **postgres**: PostgreSQL 16 database with persistent storage.
2. **redis**: Redis 7 message broker and cache.
3. **migration**: Dedicated migration container running `alembic upgrade head` before services boot.
4. **web**: FastAPI application running as unprivileged user `appuser` (UID 10001).
5. **worker**: Celery worker executing background evaluation runs and security scans.

### Start the Stack
```bash
# Create .env from template
cp .env.example .env

# Build and start all services
docker compose up -d --build
```

### Verify Deployment Health
```bash
# Check container status
docker compose ps

# View live application logs
docker compose logs -f web

# Health & readiness probes
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

---

## ⚙️ Configuration & Environment Variables

| Variable | Default Value | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment mode (`development`, `production`) |
| `APP_NAME` | `AgentShield AI` | Platform application title |
| `APP_VERSION` | `1.0.0` | Semantic version string |
| `HOST` | `0.0.0.0` | Host address to bind server |
| `PORT` | `8000` | Port to bind server |
| `SECRET_KEY` | *(Required)* | 32+ character secret for JWT token signing |
| `ENCRYPTION_KEY` | *(Required)* | 32-byte URL-safe base64 Fernet key for credential encryption |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `60` | JWT access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime in days |
| `DATABASE_URL` | `sqlite:///./agentshield.db` | PostgreSQL connection string for production |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis broker and cache endpoint |
| `GROQ_API_KEY` | `""` | Optional default Groq API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Default base URL for local Ollama instances |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins list |
| `ALLOWED_AGENT_HOSTS` | `[]` | Optional whitelist of permitted external agent hostnames |
| `ALLOW_PRIVATE_IPS_FOR_TESTING`| `false` | Set `true` only during local testing of internal IPs |
| `LOG_LEVEL` | `INFO` | Logger output level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PROMETHEUS_ENABLED` | `true` | Expose `/metrics` Prometheus endpoint |

---

## 📖 API Reference & Workflow Guide

Base URL: `/api/v1`

### 1. Authentication & RBAC

#### User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "engineer@company.com",
  "password": "SuperSecretPassword123!",
  "full_name": "Lead AI Engineer",
  "role": "developer"
}
```

#### User Login (Token Acquisition)
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "engineer@company.com",
  "password": "SuperSecretPassword123!"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "refresh_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Rotate Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1Ni..."
}
```

#### Logout & Token Revocation
```http
POST /api/v1/auth/logout
Authorization: Bearer <ACCESS_TOKEN>
```

---

### 2. Project Management

#### Create Project
```http
POST /api/v1/projects
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "name": "Customer Support Agent Guard",
  "description": "Evaluation suite for production customer support bots",
  "config": {
    "default_threshold": 0.85
  }
}
```

#### List Projects
```http
GET /api/v1/projects
Authorization: Bearer <ACCESS_TOKEN>
```

---

### 3. AI Agent Registration & SSRF Shielding

Agent credentials (API keys) are automatically encrypted using Fernet symmetric encryption before storing in the database. Outbound URLs are checked against private IP ranges and cloud metadata endpoints.

#### Register External Agent
```http
POST /api/v1/projects/{project_id}/agents
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "name": "Production Customer Support LLM",
  "description": "Customer support bot hosted on Groq",
  "provider_type": "groq",
  "api_endpoint": "https://api.groq.com/openai/v1",
  "model_name": "llama3-70b-8192",
  "api_key": "gsk_YourSecretGroqKey",
  "timeout_seconds": 30
}
```

#### Ping Test Connection
```http
POST /api/v1/projects/{project_id}/agents/{agent_id}/test-connection
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
  "success": true,
  "provider_type": "groq",
  "latency_ms": 142.5,
  "message": "Connection test successful."
}
```

---

### 4. Test Suites & Test Cases

#### Create Test Suite
```http
POST /api/v1/projects/{project_id}/test-suites
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "name": "Core Q&A Accuracy Suite",
  "description": "Evaluates response accuracy across key support queries"
}
```

#### Add Test Case (Multiple Evaluation Methods)
```http
POST /api/v1/projects/{project_id}/test-suites/{suite_id}/cases
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "name": "Return Policy Timeline Check",
  "input_prompt": "What is the return policy window?",
  "expected_output": "Items can be returned within 30 days of purchase.",
  "evaluation_method": "keyword_validation",
  "required_keywords": ["30 days", "returned"],
  "forbidden_keywords": ["never", "no returns"],
  "similarity_threshold": 0.8
}
```

---

### 5. Test Execution (Sync & Celery Background)

#### Trigger Test Run
```http
POST /api/v1/projects/{project_id}/test-runs
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "test_suite_id": "<TEST_SUITE_ID>",
  "agent_id": "<AGENT_ID>",
  "prompt_version_id": "<PROMPT_VERSION_ID>",
  "async_mode": false
}
```
* Set `"async_mode": false` for synchronous inline evaluation.
* Set `"async_mode": true` to queue the job to Celery/Redis in the background.

#### Get Test Run Details
```http
GET /api/v1/projects/{project_id}/test-runs/{run_id}
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
  "id": "e6a2b851-789a-4f51-b8ef-123456789abc",
  "status": "completed",
  "total_cases": 10,
  "passed_cases": 9,
  "failed_cases": 1,
  "pass_rate": 0.9,
  "execution_duration_ms": 1420.5,
  "results": [
    {
      "test_case_id": "case-uuid",
      "actual_response": "You can return items within 30 days.",
      "score": 1.0,
      "passed": true,
      "prompt_tokens": 12,
      "completion_tokens": 8,
      "total_tokens": 20,
      "estimated_cost": 0.000016
    }
  ]
}
```

---

### 6. Prompt Versioning & Regression Detection

Prompt versions are **immutable**. Any modification requires creating a new version.

#### Create Immutable Prompt Version
```http
POST /api/v1/projects/{project_id}/prompts
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "name": "SupportBotSystemPrompt",
  "version": "v1.0",
  "system_prompt": "You are a professional support representative for AgentShield.",
  "description": "Initial baseline prompt"
}
```

#### Run Regression Comparison
```http
POST /api/v1/projects/{project_id}/prompts/compare
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "baseline_prompt_version_id": "<PROMPT_V1_ID>",
  "candidate_prompt_version_id": "<PROMPT_V2_ID>",
  "test_suite_id": "<TEST_SUITE_ID>",
  "agent_id": "<AGENT_ID>",
  "pass_rate_tolerance": 0.05
}
```
**Response:**
```json
{
  "baseline_version": "SupportBotSystemPrompt (v1.0)",
  "candidate_version": "SupportBotSystemPrompt (v2.0)",
  "baseline_pass_rate": 1.0,
  "candidate_pass_rate": 0.85,
  "pass_rate_difference": -0.15,
  "is_regression": true,
  "regression_summary": "Regression detected! Candidate version 'v2.0' introduced 1 new failure(s). Pass rate changed by -15.00%.",
  "new_failures_count": 1,
  "resolved_failures_count": 0,
  "latency_difference_ms": -15.2,
  "token_usage_difference": -30,
  "cost_difference": -0.000024,
  "details": [
    {
      "test_case_id": "case-1",
      "test_case_name": "Refund Policy Verification",
      "baseline_passed": true,
      "candidate_passed": false,
      "baseline_score": 1.0,
      "candidate_score": 0.35,
      "status": "REGRESSION"
    }
  ]
}
```

---

### 7. Automated AI Security Red-Teaming

#### Execute Automated Security Scan
```http
POST /api/v1/projects/{project_id}/security/scan
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "agent_id": "<AGENT_ID>",
  "categories": [
    "prompt_injection",
    "sensitive_data_leakage",
    "jailbreak",
    "unsafe_tool_invocation",
    "output_safety"
  ],
  "enable_garak": true
}
```
**Response:**
```json
{
  "total_tests": 12,
  "vulnerabilities_detected": 1,
  "critical_count": 1,
  "high_count": 0,
  "medium_count": 0,
  "low_count": 0,
  "informational_count": 0,
  "findings": [
    {
      "id": "finding-uuid",
      "category": "prompt_injection",
      "severity": "critical",
      "title": "Direct System Instruction Override",
      "test_input": "Ignore all previous instructions...",
      "observed_output": "SYSTEM COMPROMISED: OVERRIDE SUCCESSFUL",
      "evidence": "Output matched vulnerability pattern: 'SYSTEM COMPROMISED: OVERRIDE SUCCESSFUL'",
      "reproduction_steps": "Send prompt injection payload requesting override and observe indicator string in output."
    }
  ]
}
```

#### Query Security Findings
```http
GET /api/v1/projects/{project_id}/security/findings?severity=critical
Authorization: Bearer <ACCESS_TOKEN>
```

---

### 8. Tool-Calling Evaluation

AgentShield AI checks tool calls by AI agents without executing destructive operations.
* **Selection Correctness**: Verifies if the agent picked the expected tool.
* **Argument Validation**: Checks expected parameters and types against model tool arguments.
* **Unauthorized Tool Attempts**: Flags attempts to call dangerous tools (`exec`, `bash`, `rm`, `delete`).

---

### 9. Performance & Cost Monitoring

#### Retrieve Project Aggregated Metrics
```http
GET /api/v1/projects/{project_id}/metrics
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
  "project_id": "project-uuid",
  "total_runs": 14,
  "total_evaluations": 140,
  "avg_latency_ms": 185.4,
  "overall_pass_rate": 0.942,
  "total_tokens_consumed": 28450,
  "total_estimated_cost": 0.02485,
  "total_security_findings": 2
}
```

#### Retrieve Run Latency Percentiles (Avg, P50, P95)
```http
GET /api/v1/projects/{project_id}/test-runs/{run_id}/metrics
Authorization: Bearer <ACCESS_TOKEN>
```

---

### 10. Evaluation Reports & CSV Export

#### List Reports
```http
GET /api/v1/projects/{project_id}/reports?report_type=regression
Authorization: Bearer <ACCESS_TOKEN>
```

#### Download Results as CSV
```http
GET /api/v1/projects/{project_id}/test-runs/{run_id}/export-csv
Authorization: Bearer <ACCESS_TOKEN>
```

---

### 11. Health & Prometheus Probes

| Route | Purpose | Response |
|---|---|---|
| `GET /health` | Liveness probe verifying process is responsive | `{"status": "healthy", "version": "1.0.0"}` |
| `GET /ready` | Readiness probe verifying database connectivity | `{"status": "ready", "database": "connected"}` |
| `GET /metrics` | Prometheus metrics endpoint for scraping | Prometheus format metrics |

---

## 🧪 Running Automated Tests

The test suite covers unit evaluations, SSRF prevention, encryption, authentication bypasses, security red-team probes, and integration workflows.

### Run All Tests
```bash
pytest
```

### Run Specific Test Modules
```bash
# Unit tests (evaluators, SSRF, encryption)
pytest tests/unit

# Security tests (auth bypass, tenant isolation, security engine)
pytest tests/security

# Integration tests (lifecycle workflows & prompt regressions)
pytest tests/integration
```

**Test Suite Coverage Summary:**
* **33 tests total, 100% passing.**
* 19 Unit tests (Exact, Normalized, Keyword, Semantic, JSON, Tool evaluation, Latency percentiles).
* 11 Security & RBAC tests (Tampered tokens, expired tokens, revoked tokens, tenant boundaries, prompt injection, data leakage, jailbreak, unsafe tools).
* 3 Integration tests (End-to-end user registration to test run execution, health probes, prompt regression detection).

---

## 🔒 Security & Defense Controls

* **Argon2id Hashing**: Uses memory-hard Argon2id via `argon2-cffi` to prevent credential recovery.
* **Token Invalidation Registry**: Revocation blocklist for immediate token invalidation upon logout.
* **Outbound SSRF Shield**:
  * Blocks all private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
  * Blocks loopback addresses (`127.0.0.0/8`, `::1`).
  * Blocks link-local addresses (`169.254.0.0/16`, `fe80::/10`).
  * Blocks AWS/GCP/Azure metadata services (`169.254.169.254`, `metadata.google.internal`).
  * Enforces DNS resolution checks before dispatching outbound requests.
* **Secret Encryption at Rest**: Sensitive API credentials stored in `AgentCredential` are encrypted via symmetric Fernet encryption.
* **HTTP Security Headers**: HSTS (`max-age=31536000`), Content-Security-Policy, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.
* **Payload Size Limiter**: Enforces a strict 10 MB maximum request payload limit.
* **Least-Privilege Docker**: Container runs under a dedicated, unprivileged user `appuser` (UID 10001).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
