"""Loader for the `skills/` folder (AI system prompts & context).

Prompts live as plain-text files under `skills/prompts/*.md`. This loader
resolves them relative to the repo root (independent of CWD) and substitutes
`{{KEY}}` placeholders at call time, so `utils/*.py` can request a prompt by
name instead of hard-coding prompt text.

Usage:
    from utils.skills import load_prompt
    system = load_prompt("echo_analyst", current_date="Tuesday, Jan 1, 2026", citation_rule="", context="...")
"""
import os
import logging

logger = logging.getLogger(__name__)

# Repo root = parent of this utils/ dir (i.e. <repo>/)
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
_PROMPTS_DIR = os.path.join(_REPO_ROOT, "skills", "prompts")
_CONTEXT_DIR = os.path.join(_REPO_ROOT, "skills", "context")


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_context(name: str) -> str:
    """Return the raw contents of a skills/context file (no substitution)."""
    path = os.path.join(_CONTEXT_DIR, f"{name}.md")
    if not os.path.exists(path):
        logger.warning("Unknown context file: %s", path)
        return ""
    return _read_file(path)


def load_prompt(name: str, **kwargs) -> str:
    """Read a skills/prompts/<name>.md template and substitute {{KEY}} kwargs.

    Every keyword argument maps to a {{KEY}} token (token is the uppercased
    kwarg name). Tokens not supplied are replaced with an empty string so no
    raw braces leak into the prompt.
    """
    path = os.path.join(_PROMPTS_DIR, f"{name}.md")
    if not os.path.exists(path):
        logger.warning("Unknown prompt: %s", path)
        return ""
    text = _read_file(path)

    # Build a lookup of {{TOKEN}} -> value
    replacements = {f"{{{{{k.upper()}}}}}": str(v if v is not None else "") for k, v in kwargs.items()}

    # Replace any remaining {{...}} tokens with empty string
    import re
    text = re.sub(r"\{\{\s*([A-Z0-9_]+)\s*\}\}", "", text) if not kwargs else text

    for token, value in replacements.items():
        text = text.replace(token, value)

    # Drop leftover unreplaced tokens
    text = re.sub(r"\{\{\s*[A-Za-z0-9_]+\s*\}\}", "", text)
    return text
