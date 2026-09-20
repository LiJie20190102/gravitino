# Chinese (zh-CN) Documentation Translation Guide

## Overview

Gravitino uses [Co-op Translator](https://github.com/Azure/co-op-translator) to automatically translate English docs to Chinese. You only maintain the English docs (`docs/*.md`), and Chinese translations are generated automatically when English docs change.

## How It Works

```
Developer edits English docs/*.md
        │
        ▼
  Push to main branch
        │
        ▼
  GitHub Action triggers (only when docs/** changed)
        │
        ▼
  Co-op Translator detects changed files (SHA256 hash diff)
        │
        ▼
  Translates only the changed Markdown files to zh-CN
  (using glossary + style rules from docs/i18n/)
        │
        ▼
  Opens a PR with translated files
        │
        ▼
  Reviewer checks & merges
```

## File Structure

```
docs/
├── overview.md                      # English source (you maintain this)
├── how-to-install.md
├── ...
├── translations/
│   └── zh-CN/                        # Auto-generated, do NOT manually edit
│       ├── overview.md               # Chinese translation
│       └── ...
└── i18n/
    ├── README.md                     # This file
    ├── zh-CN-prompt.md               # Translation style rules (injected into LLM prompt)
    └── gravitino-glossary.txt        # Terms that must NOT be translated (one per line)

scripts/
└── run_translate.py                  # Wrapper: loads glossary + prompt, calls co-op-translator

.github/workflows/
└── docs-translate-zh-cn.yml          # GitHub Action workflow
```

## Customization

### Glossary (`docs/i18n/gravitino-glossary.txt`)

One term per line. These terms are injected into the LLM prompt as "do not translate" entries. Add or remove terms as needed.

### Style Rules (`docs/i18n/zh-CN-prompt.md`)

Injected into every translation API call. Controls:
- Professional tone (no AI-isms)
- Terminology conventions (e.g., "metadata lake" → "元数据湖")
- Markdown structure preservation
- Technical identifier handling

## Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description | Required? |
|---|---|---|
| `OPENAI_API_KEY` | API key for your LLM provider | Yes |
| `OPENAI_CHAT_MODEL_ID` | Model name (e.g. `gpt-4o`, `zhanlu/glm-5.2`) | Yes |
| `OPENAI_BASE_URL` | Custom API endpoint for OpenAI-compatible providers | Optional |

## Required Repository Settings

Go to **Settings → Actions → General**:

1. Under **Workflow permissions**, select **Read and write permissions**
2. Enable **Allow GitHub Actions to create and approve pull requests**
3. Save

## Manual Trigger

You can manually trigger translation via GitHub Actions UI:

1. Go to **Actions** tab
2. Select **Docs zh-CN Translation** workflow
3. Click **Run workflow**

## Local Translation

```bash
pip install co-op-translator

# Set up credentials in .env
cat > .env << 'EOF'
OPENAI_API_KEY=your-api-key
OPENAI_CHAT_MODEL_ID=gpt-4o
OPENAI_BASE_URL=https://your-endpoint/v1   # optional
EOF

# Run translation (reads glossary + prompt from docs/i18n/)
python scripts/run_translate.py
```

## Important Notes

- **Do NOT manually edit** files in `docs/translations/zh-CN/`. They are auto-generated.
- **Only edit English docs** in `docs/`. Chinese translations will follow automatically.
- To customize translation behavior, edit `docs/i18n/zh-CN-prompt.md` and `docs/i18n/gravitino-glossary.txt`.
- The wrapper script (`scripts/run_translate.py`) reads customization files from the repo, so GitHub Actions and local runs use the same configuration.
