---
slug: /daft-connector
keyword: daft connector
license: This software is licensed under the Apache License version 2.
title: Daft 连接器
---
<!--
  Licensed to the Apache Software Foundation (ASF) under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  The ASF licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing,
  software distributed under the License is distributed on an
  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  KIND, either express or implied.  See the License for the
  specific language governing permissions and limitations
  under the License.
-->

## 概述

[Daft](https://docs.daft.ai/) 是一个用于 Python 的分布式 DataFrame 库，专为大规模数据集上的复杂数据工作流而设计。它提供了熟悉的 DataFrame API，同时具备强大的分布式计算能力，可大规模处理数据。

## Gravitino 的 Daft 连接器

Daft 连接器实现了 Daft 与 Apache Gravitino 统一元数据管理系统之间的无缝集成。该连接器允许 Daft 用户：

- 访问由 Gravitino 管理的表和文件集
- 利用 Gravitino 跨不同数据源的统一元数据层
- 受益于云存储系统的自动凭证管理

## 文档

有关安装、配置、使用示例和 API 参考的完整文档，请访问：

**[Daft Gravitino 连接器文档](https://docs.daft.ai/en/latest/connectors/gravitino/)**

Daft 官方文档提供以下方面的全面指南：

- 安装和设置说明
- 认证配置
- 完整的 API 参考
- 使用示例和最佳实践
- 兼容性信息和限制

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免责声明**：
本文件由 AI 翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 翻译完成。尽管我们力求准确，但请注意，自动翻译可能包含错误或不准确之处。原始语言版文件应视为权威来源。对于重要信息，建议使用专业人工翻译。我们对因使用本翻译而产生的任何误解或误释不承担责任。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->