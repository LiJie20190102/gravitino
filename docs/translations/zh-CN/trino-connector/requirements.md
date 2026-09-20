---
title: "Trino Connector Requirements"
slug: "/trino-connector/requirements"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

安装和部署 Apache Gravitino Trino 连接器需要以下环境配置：

- Trino 服务器版本应在 Trino-server-440 和 Trino-server-478 之间。
本文档中的示例默认使用 Trino `469`。
- 如果您使用不受支持的 Trino 版本，可以将 `gravitino.trino.skip-version-validation` 设置为 `true`。
不受支持的版本未经过全面测试。
- 确保所有运行 Trino 的节点都能访问 Gravitino 服务器的端口，默认端口为 8090。
- 确保所有运行 Trino 的节点都能访问真实的 catalogs 资源，例如 Hive、Iceberg、MySQL、PostgreSQL 等。
- 确保您已在 Trino 中安装以下连接器：Hive、Iceberg、MySQL、PostgreSQL。
- 确保您已在 Trino coordinator 配置中将 `catalog.management` 设置为 `dynamic`。
