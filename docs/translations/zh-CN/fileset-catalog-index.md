---
slug: /fileset-catalog-index
date: 2025-01-13
keyword: Fileset catalog index S3 GCS ADLS OSS
license: This software is licensed under the Apache License version 2.
title: 文件集目录索引
---
## Fileset catalog 概述

Gravitino Fileset catalog 索引包含以下章节：

- [Fileset catalog 概述与特性](./fileset-catalog.md)：本章概述了 Fileset catalog 的功能、能力以及相关配置。
- [通过 Gravitino API 管理 Fileset catalog](./manage-fileset-metadata-using-gravitino.md)：本章说明如何使用 Gravitino API 管理 fileset 元数据，并提供详细示例。
- [结合 Gravitino 虚拟文件系统使用 Fileset catalog](how-to-use-gvfs.md)：本章说明如何将 Fileset catalog 与 Gravitino 虚拟文件系统结合使用，并提供详细示例。

## 结合云存储的 Fileset catalog

每种云后端都有专属页面，包含可运行的端到端示例，涵盖 catalog 设置和
Java/Hadoop 数据访问。S3、GCS、ADLS 和 OSS 页面还涵盖 Python 和 pandas；COS
目前尚无 Python 数据面实现：

- [使用 Fileset catalog 管理 Amazon S3](./fileset-catalog-with-s3.md)。
- [使用 Fileset catalog 管理 Google Cloud Storage](./fileset-catalog-with-gcs.md)。
- [使用 Fileset catalog 管理 Azure Data Lake Storage](./fileset-catalog-with-adls.md)。
- [使用 Fileset catalog 管理 Alibaba Cloud OSS](./fileset-catalog-with-oss.md)。
- [使用 Fileset catalog 管理 Tencent Cloud COS](./fileset-catalog-with-cos.md)。

未来将添加更多存储选项，敬请期待！