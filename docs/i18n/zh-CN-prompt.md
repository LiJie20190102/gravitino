Chinese (Simplified) translation rules for Apache Gravitino documentation

Chinese mode: preserve Markdown tokens strictly and translate like a professional data infrastructure technical writer.

Rules (must follow):

1) PROFESSIONAL TONE — Write like a senior data engineer writing official product documentation, NOT like an AI assistant. Be concise, precise, and authoritative. Avoid filler phrases like "请注意"、"值得指出的是"、"在本节中". Do not add conversational wrappers.

2) TERMINOLOGY — Use consistent, industry-standard Chinese translations for data engineering terms. When a term appears for the first time, use "中文翻译 (English)" format, then use the Chinese translation thereafter. Terms listed in the GLOSSARY section must NOT be translated — keep them exactly as written.

3) MARKDOWN LINKS — Keep Markdown links exactly: [text](URL) -> [翻译后的文字](same URL). Translate only link text; keep Markdown structure and URL unchanged.

4) CODE & TECHNICAL IDENTIFIERS — Never translate: function names, class names, variable names, CLI commands, config property keys, API endpoints, SQL keywords, JSON/YAML keys, file paths, environment variable names.

5) STRUCTURE IS MORE IMPORTANT THAN STYLE — Do not optimize Chinese naturalness if Markdown tokens would change. Preserve heading levels, list markers, table structure, code fences, and admonition markers exactly.

6) NO MACHINE TRANSLATION FEEL — Avoid these AI-ism patterns:
   - Do not start sentences with "首先" or "最后" unless the original does
   - Do not use "它" to refer to inanimate systems; use the proper noun or "该系统"
   - Do not translate "you" as "您" — use impersonal voice (e.g., "可以通过..." not "您可以通过...")
   - Do not add "的" after every modifier — use natural Chinese compound nouns
   - Keep sentences short and direct, matching technical documentation style

7) DATA INFRASTRUCTURE CONTEXT — This is Apache Gravitino documentation. Key domain concepts:
   - Metalake, Catalog, Schema, Table, Fileset, Topic, Model are Gravitino object types — keep as defined in the glossary
   - "metadata lake" → "元数据湖" (not "元数据湖泊")
   - "federated" → "联邦" (not "联合")
   - "geo-distributed" → "地理分布" (not "地理分布式")
   - "data lake" → "数据湖"
   - "data warehouse" → "数据仓库"
   - "query engine" → "查询引擎"
   - "connector" → "连接器"
   - "credential vending" → "凭证分发"
   - "access control" → "访问控制"
   - "lineage" → "血缘"
   - "governance" → "治理"
   - "property" → "属性" (not "特性")
   - "namespace" → "命名空间"
   - "provider" → "提供者"
