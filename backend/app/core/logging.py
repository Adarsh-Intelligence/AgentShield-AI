from __future__ import annotations

import json
import logging
import sys
from prometheus_client import Counter, Histogram
from backend.app.config import settings


# Prometheus metrics
HTTP_REQUESTS_TOTAL = Counter(
    "agentshield_http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "agentshield_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

EVALUATIONS_TOTAL = Counter(
    "agentshield_evaluations_total",
    "Total evaluations performed",
    ["method", "status"],
)

SECURITY_FINDINGS_TOTAL = Counter(
    "agentshield_security_findings_total",
    "Total security findings identified",
    ["category", "severity"],
)

TEST_RUNS_TOTAL = Counter(
    "agentshield_test_runs_total",
    "Total test runs executed",
    ["status"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = getattr(record, "request_id")
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    if settings.is_production:
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
        )
    root_logger.addHandler(console_handler)


logger = logging.getLogger("agentshield")

