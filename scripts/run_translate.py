#!/usr/bin/env python3
"""
Wrapper script for co-op-translator with Gravitino-specific customization.

Reads customization files from the repository (not from the installed package):
  - docs/i18n/gravitino-glossary.txt  — terms that must NOT be translated (one per line)
  - docs/i18n/zh-CN-prompt.md          — translation style rules injected into the LLM prompt

Credentials are read from .env or environment variables:
  OPENAI_API_KEY        — API key for the LLM provider
  OPENAI_CHAT_MODEL_ID  — Model name (e.g. gpt-4o, zhanlu/glm-5.2)
  OPENAI_BASE_URL       — API endpoint (optional, for OpenAI-compatible providers)
"""
import os
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
I18N_DIR = REPO_ROOT / "docs" / "i18n"


def read_glossary():
    """Read glossary terms from docs/i18n/gravitino-glossary.txt."""
    path = I18N_DIR / "gravitino-glossary.txt"
    if not path.exists():
        return []
    terms = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            term = line.strip()
            if term and not term.startswith("#"):
                terms.append(term)
    return terms


def install_language_template(terms):
    """
    Install the zh-CN language template and glossary into the co-op-translator package.

    co-op-translator reads language templates from:
      <package_dir>/templates/language/<code>.md

    We copy our docs/i18n/zh-CN-prompt.md there so the built-in prompt builder picks it up.
    We also set glossary terms via the Python API.
    """
    import shutil
    import importlib.resources

    # Copy language template
    src = I18N_DIR / "zh-CN-prompt.md"
    if src.exists():
        try:
            # Find the package templates/language directory
            import co_op_translator
            pkg_dir = Path(co_op_translator.__file__).parent
            lang_dir = pkg_dir / "templates" / "language"
            lang_dir.mkdir(parents=True, exist_ok=True)
            dst = lang_dir / "zh-CN.md"
            shutil.copy2(src, dst)
        except Exception as e:
            print(f"Warning: could not install language template: {e}")

    # Set glossary terms
    try:
        from co_op_translator.glossary import set_glossary_terms
        set_glossary_terms(terms)
    except Exception as e:
        print(f"Warning: could not set glossary: {e}")


def read_env():
    """Read credentials from .env file (bypasses shell key masking)."""
    env_vars = {}
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k] = v
    return env_vars


def main():
    # Read customization files from repo
    glossary = read_glossary()
    print(f"Glossary: {len(glossary)} terms from docs/i18n/gravitino-glossary.txt")

    # Read credentials
    env_vars = read_env()
    key = env_vars.get("OPENAI_API_KEY", "")
    model = env_vars.get("OPENAI_CHAT_MODEL_ID", "gpt-4o")
    base_url = env_vars.get("OPENAI_BASE_URL", "")

    if "..." in key:
        print("ERROR: OPENAI_API_KEY contains '...' (masked). Set a real key in .env")
        sys.exit(1)

    print(f"API key: {key[:8]}...{key[-4:]}" if key else "API key: (not set)")
    print(f"Model: {model}")
    print(f"Base URL: {base_url or '(default)'}")
    print()

    # Install customization into co-op-translator
    install_language_template(glossary)

    # Build environment
    env = {**os.environ, **env_vars, "PYTHONIOENCODING": "utf-8"}

    # Run co-op-translator
    docs_dir = REPO_ROOT / "docs"
    cmd = [
        sys.executable, "-m", "co_op_translator",
        "-l", "zh-CN",
        "-r", str(docs_dir),
        "-md", "-y",
        "--no-disclaimer",
    ]

    print(f"Running: co-op-translator -l zh-CN -r docs -md -y --no-disclaimer")
    print()

    result = subprocess.run(cmd, env=env, cwd=str(REPO_ROOT))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
