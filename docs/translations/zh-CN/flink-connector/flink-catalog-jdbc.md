---
slug: /flink-connector/flink-catalog-jdbc
keyword: flink connector jdbc catalog
license: This software is licensed under the Apache License version 2.
title: Flink 连接器：JDBC 目录
---
## 简介

本文档提供了配置和使用 Apache Gravitino Flink 连接器以访问由 Gravitino 服务器管理的 JDBC catalog 的完整指南。

## 功能

### JDBC 类型

* MYSQL
* POSTGRESQL

## 快速入门

### 前置条件

将以下 JAR 文件放置在 Flink 安装目录的 lib 目录中：

- 与 Flink 小版本匹配的 Flink JDBC 连接器 JAR
- 与 Flink 小版本匹配的 Gravitino Flink 连接器运行时 JAR
- JDBC 驱动

| Flink 版本 | Flink JDBC 连接器版本 | Gravitino 运行时构件 |
|---------------|------------------------------|----------------------------|
| 1.18          | `3.2.0-1.18`                 | `gravitino-flink-connector-runtime-1.18_2.12-${gravitino-version}.jar` |
| 1.19          | `3.3.0-1.19`                 | `gravitino-flink-connector-runtime-1.19_2.12-${gravitino-version}.jar` |
| 1.20          | `3.3.0-1.20`                 | `gravitino-flink-connector-runtime-1.20_2.12-${gravitino-version}.jar` |

接下来，在 Gravitino 中创建 JDBC catalog 时，添加 `flink.bypass.default-database` 属性，值为默认数据库名称。


```text
flink.bypass.default-database=db  
```

对于 PostgreSQL catalog，如果未设置 `flink.bypass.default-database`，则回退到 catalog 的 `jdbc-database` 属性。这一区别对 PostgreSQL 至关重要，因为 Flink 的 "database" 对应的是 PostgreSQL schema，而非 PostgreSQL 数据库本身；JDBC 连接始终指向 `jdbc-database`（或 `flink.bypass.default-database` 覆盖值），而 `SHOW TABLES FROM <schema>` 和表扫描则使用 schema 名称访问该数据库内的表。

### SQL 示例

```sql
-- Suppose jdbc_catalog is the JDBC catalog name managed by Gravitino

USE CATALOG jdbc_catalog;

SHOW DATABASES;
-- +------------------+
-- |    database name |
-- +------------------+
-- |          mysql   |
-- +------------------+
     
CREATE DATABASE jdbc_database;
-- [INFO] Execute statement succeed.

SHOW DATABASES;
-- +------------------+
-- |    database name |
-- +------------------+
-- |          mysql   |
-- |  jdbc_database   |
-- +------------------+

USE jdbc_database;
-- [INFO] Execute statement succeed.
    
SET 'execution.runtime-mode' = 'batch';
-- [INFO] Execute statement succeed.

SET 'sql-client.execution.result-mode' = 'tableau';
-- [INFO] Execute statement succeed.
     
USE jdbc_database;
-- [INFO] Execute statement succeed.

SHOW TABLES;
-- Empty set

CREATE TABLE jdbc_table_a (
   aa BIGINT NOT NULL PRIMARY KEY NOT ENFORCED,
   bb BIGINT
);
-- [INFO] Execute statement succeed.

SHOW TABLES;
-- +--------------+
-- |   table name |
-- +--------------+
-- | jdbc_table_a |
-- +--------------+
-- 1 row in set

INSERT INTO jdbc_table_a VALUES(1,2);

SELECT * FROM jdbc_table_a;
-- +----+----+
-- | aa | bb |
-- +----+----+
-- |  1 |  2 |
-- +----+----+
-- 1 row in set

INSERT INTO jdbc_table_a VALUES(2,3);
-- [INFO] Submitting SQL update statement to the cluster...
-- [INFO] SQL update statement has been successfully submitted to the cluster:
-- Job ID: bc320828d49b97b684ed9f622f1b8aca

INSERT INTO jdbc_table_a VALUES(1,4);
-- [INFO] Submitting SQL update statement to the cluster...
-- [INFO] SQL update statement has been successfully submitted to the cluster:
-- Job ID: bc320828d49b97b684ed9f622f1b8aca

SELECT * FROM jdbc_table_a;
-- +----+----+
-- | aa | bb |
-- +----+----+
-- |  1 |  4 |
-- |  2 |  3 |
-- +----+----+
-- 2 rows in set
     
```

## Catalog 属性

Gravitino Flink 连接器会将以下 catalog 属性中定义的属性名称转换为 Flink JDBC 连接器配置。

| Gravitino catalog 属性名 | Flink JDBC 连接器配置 | 说明                                                                                          |
|:--------------------------------|:-----------------------------------|:--------------------------------------------------------------------------------------------|
| `jdbc-url`                      | `base-url`                         | catalog 的 JDBC URL                                                                         |
| `username`                      | `username`                         | 账户用户名                                                                                      |
| `password`                      | `password`                         | 账户密码                                                                                      |
| `flink.bypass.default-database` | `default-database`                 | 连接的默认数据库。对于 PostgreSQL，未设置时回退到 `jdbc-database`。 |
| `jdbc-database`                 | (见上文)                        | PostgreSQL catalog 必需；catalog 连接的 PostgreSQL 数据库。          |