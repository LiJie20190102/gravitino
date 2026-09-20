---
title: "Trino Connector"
slug: "/trino-connector/trino-connector"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Trino 可以使用 `Apache Gravitino` 提供的 Trino 连接器来管理和访问数据，该连接器通常被称为 `Gravitino Trino connector`。
在 Trino 中配置 Gravitino Trino connector 后，Trino 可以自动从 Gravitino 加载 catalog 元数据，允许用户在 Trino 中直接访问这些 catalog。
与 Gravitino 集成后，Trino 可以操作所有 Gravitino 数据，无需额外配置。 
Gravitino Trino connector 使用 [Trino 动态 catalog 管理机制](https://trino.io/docs/current/admin/properties-catalog.html) 来加载 catalog。
当 Gravitino Trino connector 从 Gravitino 服务器检索 catalog 时，它会生成一个 `CREATE CATALOG` 语句并执行
在当前 Trino 服务器上执行该语句，以向 Trino 注册这些 catalog

该连接器支持多个 Trino 版本。有关支持的版本范围，请参见[要求](requirements.md)。本文档中的示例将 Trino `469` 设为默认。

:::note
一旦 Gravitino 中的 catalog 等元数据发生更改，Trino 就可以通过 Gravitino 自行更新，此过程通常需要 
约 3~10 秒。
:::

默认情况下，将 Gravitino 的 catalog 加载到 Trino 中遵循以下命名约定：

```text
{catalog}
```

在查询中的用法如下：

```text
SELECT * from catalog.dbname.tablename
```

