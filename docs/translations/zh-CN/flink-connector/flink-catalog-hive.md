---
slug: /flink-connector/flink-catalog-hive
keyword: flink connector hive catalog
license: This software is licensed under the Apache License version 2.
---
## 简介

通过 Apache Gravitino Flink 连接器，访问 Hive Catalog 中的数据或管理元数据变得简单直接，能够跨不同 Hive Catalog 实现无缝联邦查询。

## 功能特性

支持 Flink SQL 中的大多数 DDL 和 DML 操作，但不包括以下操作：

- 函数操作
- 分区操作
- 查询 UDF
- `LOAD` 子句
- `UNLOAD` 子句
- `CREATE TABLE LIKE` 子句
- `TRUCATE TABLE` 子句
- `UPDATE` 子句
- `DELETE` 子句
- `CALL` 子句

## 通用表

Flink 通用表是非 Hive 表。其 schema 和分区键存储在表
Hive metastore 的属性中。Gravitino Flink 连接器遵循 Flink Hive catalog 的行为：

- 如果 `connector=hive`，则该表被视为 Hive 表，并使用正常的 Hive schema 存储。
- 如果缺少连接器或连接器不是 `hive`，则该表被视为通用表。Gravitino
  会存储一个空的 Hive schema，并将 schema 和分区键序列化到 `flink.*` 属性中。
  在需要兼容性时，还会使用 `is_generic` 标志。

加载或更改表时，Gravitino Flink 连接器通过
`is_generic`、`flink.connector` 和 `flink.connector.type` 属性检测通用表。通用表会
从序列化的 `flink.*` 属性中重建。Hive 表继续使用原生
Hive schema。

:::note
创建原始 Hive 表时，需显式设置 `connector=hive`。否则，该表在 HiveCatalog 中
默认创建为通用表。从 Apache Flink 1.18 起，
与 ManagedTable 相关的 API 已被弃用，因此应避免依赖托管表的行为。建议优先
使用兼容 Hive 的表（使用 Hive 方言或设置 `connector=hive`）或外部通用表（设置
显式的 `connector`）。详情请参阅 Flink 关于 Hive 通用表的文档：
https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/table/hive/hive_catalog/#generic-tables
:::

## 前置条件

* Hive metastore 2.x
* HDFS 2.x 或 3.x

## SQL 示例

```sql

// Suppose hive_a is the Hive catalog name managed by Gravitino
USE CATALOG hive_a;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

SET 'execution.runtime-mode' = 'batch';
-- [INFO] Execute statement succeed.

SET 'sql-client.execution.result-mode' = 'tableau';
-- [INFO] Execute statement succeed.

// Create a raw hive table; make sure to set 'connector'='hive'.
CREATE TABLE IF NOT EXISTS employees (
    id INT,
    name STRING,
    dt INT
)
PARTITIONED BY (dt) WITH (
  'connector'='hive'
);

// Create a generic jdbc table
CREATE TABLE IF NOT EXISTS jdbc_table (
  id INT,
  name STRING
) WITH (
  'connector'='jdbc',
  'url'='jdbc:postgresql://127.0.0.1:5432/postgres',
  'table-name'='jdbc_table',
  'username'='xx',
  'password'='xx',
  'driver'='org.postgresql.Driver'
);

DESC EXTENDED employees;

INSERT INTO employees VALUES (1, 'John Doe', 20240101), (2, 'Jane Smith', 20240101);
SELECT * FROM employees WHERE dt = 20240101;
```

## 视图

### 视图功能特性

- 支持对存储在 Hive Metastore Service 中的视图执行 `CREATE VIEW`、`DROP VIEW`、`ALTER VIEW`（重命名和替换视图定义）、列出、加载和重命名操作。
- 创建视图时，连接器使用 `flink` 方言存储 SQL，并自动记录 `flink.schema.num-columns` 属性，该属性充当 Hive catalog 所需的方言标记。
- 加载视图时，连接器首先尝试 `flink` 方言，然后回退到 `hive` 方言。
- 由其他引擎（例如 Spark）使用不同方言标记创建的视图在 `SHOW VIEWS` 中可见，但无法被 Flink 连接器加载。
- 对于 Flink 创建的视图，`defaultCatalog` 和 `defaultSchema` 始终存储为 `null`。

### 视图 SQL 示例

```sql
USE CATALOG hive_a;
USE mydatabase;

CREATE VIEW employee_view AS SELECT id, name FROM employees WHERE dt = 20240101;

SHOW VIEWS;

SELECT * FROM employee_view;

DROP VIEW employee_view;
```

## Catalog 属性

Flink Hive 连接器的配置与原始 Flink Hive 连接器相同。
带有 `flink.bypass.` 前缀的 Gravitino catalog 属性名将传递给 Flink Hive 连接器。例如，使用 `flink.bypass.hive-conf-dir` 将 `hive-conf-dir` 传递给 Flink Hive 连接器。
已验证的 catalog 属性如下所示。Gravitino Catalog 中任何其他带有 `flink.bypass.` 前缀的属性将被 Gravitino Flink 连接器忽略。

| Gravitino catalog 属性中的属性名 | Flink Hive 连接器配置 | 描述           |
|-----------------------------------------------|------------------------------------|-----------------------|
| `flink.bypass.default-database`               | `default-database`                 | Hive 默认数据库 |
| `flink.bypass.hive-conf-dir`                  | `hive-conf-dir`                    | Hive 配置目录         |
| `flink.bypass.hive-version`                   | `hive-version`                     | Hive 版本          |
| `flink.bypass.hadoop-conf-dir`                | `hadoop-conf-dir`                  | Hadoop 配置目录       |
| `metastore.uris`                              | `hive.metastore.uris`              | Hive metastore uri    |

:::caution
在 Gravitino Catalog 属性中设置其他 Hadoop 属性（带有 `hadoop.`、`dfs.`、`fs.`、`hive.` 前缀）。如果设置，将覆盖
来自 `hive-conf-dir` 和 `hadoop-conf-dir` 的配置。
:::