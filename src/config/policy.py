"""
Policy text loading for the reference implementation.

The default policy is a public-safe sample file. Deployments or experiments can
override it with POLICY_PATH without changing code.
"""

from pathlib import Path

from src.config.settings import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_policy_path(policy_path: str | Path | None = None) -> Path:
    """Resolve a policy path relative to the project root when needed."""
    configured_path = policy_path if policy_path is not None else settings.policy_path
    path = Path(configured_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def load_policy_text(policy_path: str | Path | None = None) -> str:
    """
    Load non-empty policy text from disk.

    Raises:
        FileNotFoundError: If the configured policy file does not exist.
        ValueError: If the configured policy file is empty.
    """
    path = resolve_policy_path(policy_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Policy file not found: {path}. Set POLICY_PATH or restore the sample policy."
        )

    policy_text = path.read_text(encoding="utf-8").strip()
    if not policy_text:
        raise ValueError(f"Policy file is empty: {path}")
    return policy_text
