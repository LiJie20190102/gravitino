---
slug: /flink-connector/flink-catalog-iceberg
keyword: flink connector iceberg catalog
license: This software is licensed under the Apache License version 2.
title: Flink 连接器：Iceberg Catalog
---
## 简介

Apache Gravitino Flink 连接器可用于读写 Iceberg 表，元数据由 Gravitino 服务器管理。
要启用 Flink 连接器，需下载 Iceberg Flink 运行时 JAR 并将其放置在 Flink classpath 中。

## 功能特性

### DML 和 DDL 操作

- `CREATE CATALOG`
- `CREATE DATABASE`
- `CREATE TABLE`
- `DROP TABLE`
- `ALTER TABLE`
- `INSERT INTO & OVERWRITE`
- `SELECT`

### 不支持的操作

- 分区操作
- 元数据表，例如：
  - `{iceberg_catalog}.{iceberg_database}.{iceberg_table}&snapshots`
- 查询 UDF
- `UPDATE` 子句
- `DELETE` 子句
- `CREATE TABLE LIKE` 子句

## 快速开始

### 前置条件

将 Iceberg Flink 运行时 JAR 和 Gravitino Flink 连接器运行时 JAR 放置在 Flink 安装目录的 `lib` 目录下。

Flink 客户端使用的 Iceberg 版本与 Gravitino 服务器（1.11.0）不同。根据下表选择与 Flink 版本匹配的 JAR 文件。

| Flink 版本 | Scala | Iceberg 版本 | Iceberg 客户端运行时构件        | Gravitino 连接器运行时构件                                   |
|---------------|-------|-----------------|----------------------------------------|------------------------------------------------------------------------|
| 1.18          | 2.12  | 1.9.2           | `iceberg-flink-runtime-1.18-1.9.2.jar` | `gravitino-flink-connector-runtime-1.18_2.12-${gravitino-version}.jar` |
| 1.19          | 2.12  | 1.10.2          | `iceberg-flink-runtime-1.19-1.10.2.jar` | `gravitino-flink-connector-runtime-1.19_2.12-${gravitino-version}.jar` |
| 1.20          | 2.12  | 1.11.0          | `iceberg-flink-runtime-1.20-1.11.0.jar` | `gravitino-flink-connector-runtime-1.20_2.12-${gravitino-version}.jar` |

将 `${gravitino-version}` 替换为 Gravitino 的发布版本。

:::caution
仅使用对应表格行中的 JAR 文件。在客户端 classpath 中混用不同版本的 Iceberg JAR 不兼容，可能导致运行时错误。
:::

## SQL 示例

```sql

-- Suppose iceberg_a is the Iceberg catalog name managed by Gravitino

USE CATALOG iceberg_a;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

CREATE TABLE sample (
    id BIGINT COMMENT 'unique id',
    data STRING NOT NULL
) PARTITIONED BY (data) 
WITH ('format-version'='2');

INSERT INTO sample
VALUES (1, 'A'), (2, 'B');

SELECT * FROM sample WHERE data = 'B';

```

## 视图

### 视图功能

- 支持 `CREATE VIEW`、`DROP VIEW`、`ALTER VIEW`（重命名和替换视图定义）、列出、加载和重命名由底层 Iceberg 后端管理的视图。
- 创建视图时，连接器以 `flink` 方言存储 SQL。
- 加载视图时，连接器优先尝试 `flink` 方言，然后回退到 `hive` 方言。
- 每个视图可以共存多种 SQL 表示（例如 `spark` 方言），并由 Gravitino 保留。

### 视图 SQL 示例

```sql
USE CATALOG iceberg_a;
USE mydb;

CREATE VIEW order_view AS SELECT id, amount FROM orders WHERE status = 'completed';

SHOW VIEWS;

SELECT * FROM order_view;

DROP VIEW order_view;
```

## Catalog 属性

Gravitino Flink 连接器将 catalog 中的以下属性转换为 Flink 连接器配置。


| Gravitino catalog 属性名 | Flink Iceberg 连接器配置 | 描述                                                                                                       |
|---------------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `catalog-backend`               | `catalog-type`                        | Catalog 后端类型，目前支持 `Hive` 和 `REST` catalog，`JDBC` 正在持续验证中 |
| `uri`                           | `uri`                                 | Catalog 后端 URI                                                                                               |
| `warehouse`                     | `warehouse`                           | Catalog 后端仓库                                                                                         |
| `io-impl`                       | `io-impl`                             | Iceberg 中 `FileIO` 的 IO 实现。                                                                    |
| `oss-endpoint`                  | `oss.endpoint`                        | 阿里云 OSS 服务的 endpoint。                                                                               |
| `oss-access-key-id`             | `client.access-key-id`                | 用于访问 OSS 数据的静态访问密钥 ID。                                                                 |
| `oss-secret-access-key`         | `client.access-key-secret`            | 用于访问 OSS 数据的静态秘密访问密钥。                                                             |

Gravitino catalog 属性名中带有 `flink.bypass.` 前缀的属性会传递给 Flink Iceberg 连接器。例如，使用 `flink.bypass.clients` 将 `clients` 传递给 Flink Iceberg 连接器。

## 存储

### OSS

此外，需下载 [阿里云 OSS SDK](https://gosspublic.alicdn.com/sdks/java/aliyun_java_sdk_3.10.2.zip)，并将 `aliyun-sdk-oss-3.10.2.jar`、`hamcrest-core-1.1.jar`、`jdom2-2.0.6.jar` 复制到 Flink classpath 中。