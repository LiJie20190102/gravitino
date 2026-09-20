# 中文（zh-CN）文档翻译指南

## 概述

Gravitino 使用 [Co-op Translator](https://github.com/Azure/co-op-translator) 将英文文档自动翻译为中文。你只需维护英文文档（`docs/*.md`），当英文文档发生变化时，中文翻译会自动生成。

## 工作原理

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

## 文件结构

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

## 自定义

### 术语表 (`docs/i18n/gravitino-glossary.txt`)

每行一个术语。这些术语会作为“不要翻译”条目注入到 LLM 提示词中。根据需要添加或删除术语。

### 风格规则 (`docs/i18n/zh-CN-prompt.md`)

注入到每次翻译 API 调用中。控制：
- 专业语气（无 AI 腔）
- 术语约定（例如，"metadata lake" → "元数据湖"）
- 保留 Markdown 结构
- 技术标识符处理

## 必需的 GitHub Secrets

转到 **Settings → Secrets and variables → Actions** 并添加：

| Secret | 描述 | 是否必需？ |
|---|---|---|
| `OPENAI_API_KEY` | 你的 LLM 提供商的 API 密钥 | 是 |
| `OPENAI_CHAT_MODEL_ID` | 模型名称（例如 `gpt-4o`、`zhanlu/glm-5.2`） | 是 |
| `OPENAI_BASE_URL` | 用于兼容 OpenAI 的提供商的自定义 API 端点 | 可选 |

## 必需的仓库设置

转到 **Settings → Actions → General**：

1. 在 **Workflow permissions** 下，选择 **Read and write permissions**
2. 启用 **Allow GitHub Actions to create and approve pull requests**
3. 保存

## 手动触发

你可以通过 GitHub Actions UI 手动触发翻译：

1. 转到 **Actions** 标签页
2. 选择 **Docs zh-CN Translation** 工作流
3. 点击 **Run workflow**

## 本地翻译

```bash
pip install co-op-translator

# 在 .env 中设置凭据
cat > .env << 'EOF'
OPENAI_API_KEY=your-api-key
OPENAI_CHAT_MODEL_ID=gpt-4o
OPENAI_BASE_URL=https://your-endpoint/v1   # 可选
EOF

# 运行翻译（从 docs/i18n/ 读取术语表和提示词）
python scripts/run_translate.py
```

## 重要说明

- <strong>不要手动编辑</strong> `docs/translations/zh-CN/` 中的文件。它们是自动生成的。
- <strong>只编辑英文文档</strong>（位于 `docs/` 中）。中文翻译将自动跟进。
- 要自定义翻译行为，请编辑 `docs/i18n/zh-CN-prompt.md` 和 `docs/i18n/gravitino-glossary.txt`。
- 包装脚本（`scripts/run_translate.py`）会从仓库读取自定义文件，因此 GitHub Actions 和本地运行使用相同的配置。