---
title: "Spark Connector: User-Defined Functions"
slug: "/spark-connector/spark-connector-udf"
keyword: "spark connector UDF user-defined function"
license: "This software is licensed under the Apache License version 2."
---

## 概述

Apache Gravitino Spark 连接器支持加载已注册的用户定义函数 (UDF)
在 Gravitino 函数注册表中。一旦函数被
[在 Gravitino 中注册](../manage-user-defined-function-using-gravitino.md)，Spark 就能发现并
通过标准的 Spark SQL 语法调用它——无需额外的 `CREATE FUNCTION` 语句。

:::note
只有带有 `RuntimeType.SPARK` 的 **Java 实现**在 Spark 中受支持
连接器。在 Gravitino 中注册的 SQL 和 Python 实现尚不能被调用
直接从 Spark 调用。计划在未来的版本中提供对其他语言的支持。
:::

## 先决条件

在 Spark 中使用 Gravitino UDFs 之前，请确保满足以下条件：

1. **Spark 连接器已配置**且目录可访问
（参见 [Spark 连接器设置](spark-connector.md)）。
2. 该函数已**在 Gravitino 中注册**，且至少包含一个定义，该定义包含
针对 `RuntimeType.SPARK` 的 Java 实现
（参见 [注册函数](../manage-user-defined-function-using-gravitino.md#register-a-function)）。
3. **包含 UDF 类的 JAR** 在 Spark classpath 上可用（例如通过
`--jars` 或 `spark.jars` 配置）。

## Java UDF 要求

函数实现中 `className` 指定的 Java 类必须实现 Spark 的
`org.apache.spark.sql.connector.catalog.functions.UnboundFunction` 接口。有关
实现自定义 Spark 函数的详细信息，请参阅
[Spark DataSource V2 Functions 文档](https://spark.apache.org/docs/latest/api/java/org/apache/spark/sql/connector/catalog/functions/UnboundFunction.html)。

要点：

- 该类必须具有一个**公共无参构造函数**。
- 该类必须位于 **Spark driver 和 executor 类路径**上。
- 只有带有 `RuntimeType.SPARK` 的函数对 Spark 连接器可见；实现
针对其他运行时（例如 `TRINO`）的会被过滤掉。

## 在 Spark SQL 中调用函数

使用完全限定的三段式名称 `catalog.schema.function_name` 来调用
Gravitino 注册的函数：

```sql
-- Call a scalar function
SELECT my_catalog.my_schema.add_one(42);

-- Use in a query
SELECT id, my_catalog.my_schema.add_one(value) AS incremented
FROM my_catalog.my_schema.my_table;
```

:::tip
通过先设置默认目录和模式来简化语法：

```sql
USE my_catalog;
USE my_schema;
SELECT add_one(42);
```
:::

## 发现函数

Spark 连接器仅公开具有至少一个 Java 实现的函数，该实现带有
`RuntimeType.SPARK`。仅有非 Spark 实现（例如 `TRINO`）的函数不会
被列出或加载。

```sql
-- List all available functions in a schema (includes Gravitino UDFs with Spark runtime)
SHOW FUNCTIONS IN my_catalog.my_schema;
```
