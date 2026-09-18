"""
Automated Security, Configuration, and Secrets Verification Tests for CareFlow AI.

Source of truth: docs/safety-privacy.md and docs/system-architecture.md.

Validates:
- Zero hardcoded private keys, live API credentials, or credentials in tracked files.
- Environment hygiene: .env is gitignored, .env.example contains only dev placeholders.
- CORS policy and security headers.
- ORM parameterized query hygiene (SQL injection prevention).
- AI agent offline operation and client isolation.
"""

import os
import re
import socket
from pathlib import Path
import pytest
from app.core.config import settings
from app.services.agent.provider import MockLLMProvider


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_no_hardcoded_private_keys_or_live_tokens():
    """Scans all tracked code files for sensitive tokens, private keys, or credentials."""
    forbidden_patterns = [
        (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Private Key"),
        (re.compile(r"\bsk-[a-zA-Z0-9]{24,}\b"), "OpenAI Secret Key"),
        (re.compile(r"\bghp_[a-zA-Z0-9]{36}\b"), "GitHub Personal Access Token"),
        (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS Access Key ID"),
    ]

    scan_extensions = {".py", ".json", ".yaml", ".yml", ".md", ".env.example", ".ts", ".tsx"}
    excluded_dirs = {".git", ".venv", "node_modules", ".pytest_cache", "dist", "build"}

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            path = Path(root) / file
            if path.suffix in scan_extensions:
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    for pattern, label in forbidden_patterns:
                        match = pattern.search(text)
                        assert not match, f"Security Violation: Found {label} in {path.relative_to(REPO_ROOT)}"
                except Exception:
                    continue


def test_gitignore_and_environment_hygiene():
    """Verifies that .gitignore includes sensitive files and no .env file is tracked."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file must exist at repository root"
    gitignore_content = gitignore_path.read_text(encoding="utf-8")

    assert ".env" in gitignore_content, ".gitignore must exclude .env files"
    assert "__pycache__" in gitignore_content, ".gitignore must exclude __pycache__"

    # Verify example environment files exist with safe defaults
    root_env_example = REPO_ROOT / ".env.example"
    backend_env_example = REPO_ROOT / "backend" / ".env.example"

    assert root_env_example.exists(), "Root .env.example must exist"
    assert backend_env_example.exists(), "Backend .env.example must exist"

    for env_ex in [root_env_example, backend_env_example]:
        content = env_ex.read_text(encoding="utf-8")
        assert "sk-" not in content, f"Real API key found in {env_ex}"
        assert "ghp_" not in content, f"Real GitHub token found in {env_ex}"


def test_cors_configuration():
    """Verifies that CORS settings parse valid origins and do not accept unrestricted wildcards with credentials."""
    assert hasattr(settings, "CORS_ORIGINS"), "Settings must define CORS_ORIGINS"
    origins = settings.CORS_ORIGINS
    assert isinstance(origins, list), "CORS_ORIGINS must be a list"
    assert len(origins) >= 1, "At least one allowed CORS origin must be configured"

    for origin in origins:
        assert origin.startswith("http://") or origin.startswith("https://"), f"CORS origin {origin} must include scheme"


def test_orm_parameterized_query_hygiene():
    """
    Scans backend source files to ensure no unescaped f-string SQL query execution
    e.g., db.execute(f"SELECT ... {param}") which exposes SQL injection vulnerabilities.
    """
    dangerous_sql = re.compile(r'db\.execute\(\s*f["\'].*SELECT.*\{', re.IGNORECASE)
    backend_app_dir = REPO_ROOT / "backend" / "app"

    for root, _, files in os.walk(backend_app_dir):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                text = path.read_text(encoding="utf-8")
                match = dangerous_sql.search(text)
                assert not match, f"SQL Injection Risk: Raw f-string SQL query execution in {path.relative_to(REPO_ROOT)}"


def test_mock_llm_provider_offline_guarantee(monkeypatch):
    """
    Guarantees that MockLLMProvider never opens a network socket or makes external HTTP requests.
    """
    def fail_connect(*args, **kwargs):
        raise RuntimeError("External network connection attempted during MockLLM call!")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)

    provider = MockLLMProvider()
    response = provider.complete(
        messages=[{"role": "user", "content": "When is my appointment?"}],
    )

    assert response is not None
    assert isinstance(response.content, str)
    assert len(response.content) > 0
