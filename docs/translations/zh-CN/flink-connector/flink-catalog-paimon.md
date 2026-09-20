---
slug: /flink-connector/flink-catalog-paimon
keyword: flink connector paimon catalog
license: This software is licensed under the Apache License version 2.
title: 'Flink 连接器: Paimon Catalog'
---
## 简介

本文档提供了配置和使用 Apache Gravitino Flink 连接器 (connector) 以访问由 Gravitino 服务器管理的 Paimon catalog 的全面指南。

## 功能特性

### Paimon 表类型

* AppendOnly 表
* 主键表（带 bucket 分布）

### 分布

* 通过 `bucket-key` 和 `bucket` 表属性进行 HASH 分布。
* 仅支持 HASH 策略。不支持 Range 或其他策略。
* 当指定了 `bucket-key` 而未指定 `bucket` 时，bucket 数量默认为 auto。

### 操作类型

支持 Flink SQL 中的大多数 DDL 和 DML 操作，但不支持以下操作：

- 函数操作
- 分区操作
- 查询 UDF
- `LOAD` 语句
- `UNLOAD` 语句
- `CREATE TABLE LIKE` 语句
- `TRUCATE TABLE` 语句
- `UPDATE` 语句
- `DELETE` 语句
- `CALL` 语句

## 前提条件

* Paimon 1.2.0 已通过全面测试。

其他 Paimon 版本可能也可用，但未经过全面测试。

## 快速开始

### 前提条件

将以下 JAR 文件放置在 Flink 安装目录的 lib 目录下：

- 与 Flink 次版本匹配的 Paimon Flink 连接器 JAR 文件
- 与 Flink 次版本匹配的 Gravitino Flink 连接器 runtime JAR 文件

| Flink 版本 | Paimon 连接器 artifact | Gravitino runtime artifact |
|---------------|---------------------------|----------------------------|
| 1.18          | `paimon-flink-1.18-${paimon-version}.jar` | `gravitino-flink-connector-runtime-1.18_2.12-${gravitino-version}.jar` |
| 1.19          | `paimon-flink-1.19-${paimon-version}.jar` | `gravitino-flink-connector-runtime-1.19_2.12-${gravitino-version}.jar` |
| 1.20          | `paimon-flink-1.20-${paimon-version}.jar` | `gravitino-flink-connector-runtime-1.20_2.12-${gravitino-version}.jar` |

### SQL 示例

```sql

-- Suppose paimon_catalog is the Paimon catalog name managed by Gravitino
USE CATALOG paimon_catalog;
-- Execute statement succeed.

SHOW DATABASES;
-- +---------------------+
-- |       database name |
-- +---------------------+
-- |             default |
-- | gravitino_paimon_db |
-- +---------------------+

SET 'execution.runtime-mode' = 'batch';
-- [INFO] Execute statement succeed.

SET 'sql-client.execution.result-mode' = 'tableau';
-- [INFO] Execute statement succeed.

CREATE TABLE paimon_table_a (
    aa BIGINT,
    bb BIGINT
);

SHOW TABLES;
-- +----------------+
-- |     table name |
-- +----------------+
-- | paimon_table_a |
-- +----------------+


SELECT * FROM paimon_table_a;
-- Empty set

INSERT INTO paimon_table_a(aa,bb) VALUES(1,2);
-- [INFO] Submitting SQL update statement to the cluster...
-- [INFO] SQL update statement has been successfully submitted to the cluster:
-- Job ID: 74c0c678124f7b452daf08c399d0fee2

SELECT * FROM paimon_table_a;
-- +----+----+
-- | aa | bb |
-- +----+----+
-- |  1 |  2 |
-- +----+----+
-- 1 row in set
```

#### 分布示例

```sql
-- Create a primary key table with HASH distribution on the 'id' column with 4 buckets
-- The distribution metadata is persisted in Gravitino and can be verified via the Gravitino API or client.
CREATE TABLE paimon_bucketed_table (
    id BIGINT,
    name STRING,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'bucket-key' = 'id',
    'bucket' = '4'
);
```

## 视图

### 视图功能特性

- 支持 `CREATE VIEW`、`DROP VIEW`、`ALTER VIEW`（重命名和替换视图定义），以及对存储在 Paimon catalog 中的视图进行列出、加载和重命名操作。
- 创建视图时，连接器会存储两种 SQL 表示形式：一种使用 `flink` 方言 (dialect)，另一种使用 `query` 方言（Paimon 的规范方言），两者使用相同的扩展 SQL 文本。
- 加载视图时，连接器会按 `flink` → `hive` → `query` 的顺序尝试方言。使用第一个可用的表示形式。
- 视图支持取决于所选的 Paimon 后端 (backend)；并非所有后端都实现了 Paimon 视图 API。

### 视图 SQL 示例

```sql
USE CATALOG paimon_a;
USE mydb;

CREATE VIEW summary_view AS SELECT category, SUM(amount) AS total FROM orders GROUP BY category;

SHOW VIEWS;

SELECT * FROM summary_view;

DROP VIEW summary_view;
```

## Catalog 属性

Gravitino Flink 连接器会将以下在 catalog 属性中定义的属性名称转换为 Flink Paimon 连接器配置。

| Gravitino catalog 属性名称 | Flink Paimon 连接器配置 | 描述                                                                                                                                                                                                |
|---------------------------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `catalog-backend`               | `metastore`                          | Gravitino Paimon catalog 的 Catalog 后端。支持 `filesystem`。                                                                                                                                        |
| `warehouse`                     | `warehouse`                          | catalog 的 Warehouse 目录。本地文件系统使用 `file:///user/hive/warehouse-paimon/`，HDFS 使用 `hdfs://namespace/hdfs/path`，S3 使用 `s3://{bucket-name}/path/`，阿里云 OSS 使用 `oss://{bucket-name}/path` |

带有 `flink.bypass.` 前缀的 Gravitino catalog 属性名称将传递给 Flink Paimon 连接器。例如，使用 `flink.bypass.clients` 将 `clients` 传递给 Flink Paimon 连接器。