---
title: "Trino Connector SQL Support"
slug: "/trino-connector/sql-support"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

该连接器提供对存储在 Apache Gravitino 中的数据和元数据的读取和写入访问。

### 全局可用语句

- [EXPLAIN](https://trino.io/docs/current/sql/explain.html)
- [EXPLAIN ANALYZE](https://trino.io/docs/current/sql/explain-analyze.html)
- [PREPARE](https://trino.io/docs/current/sql/prepare.html)
- [USE](https://trino.io/docs/current/sql/use.html)

### 读操作

- [SELECT](https://trino.io/docs/current/sql/select.html)
- [DESCRIBE](https://trino.io/docs/current/sql/describe.html)
- [SHOW CATALOGS](https://trino.io/docs/current/sql/show-catalogs.html)
- [SHOW COLUMNS](https://trino.io/docs/current/sql/show-columns.html)
- [SHOW CREATE SCHEMA](https://trino.io/docs/current/sql/show-create-schema.html)
- [SHOW CREATE TABLE](https://trino.io/docs/current/sql/show-create-table.html)
- [SHOW SCHEMAS](https://trino.io/docs/current/sql/show-schemas.html)
- [SHOW TABLES](https://trino.io/docs/current/sql/show-tables.html)

### 写入操作

- [INSERT](https://trino.io/docs/current/sql/insert.html)
- [INSERT INTO SELECT](https://trino.io/docs/current/sql/insert.html)
- [UPDATE](https://trino.io/docs/current/sql/update.html)
- [DELETE](https://trino.io/docs/current/sql/delete.html)
- [MERGE](https://trino.io/docs/current/sql/merge.html)

### 模式与表管理

- [CREATE TABLE](https://trino.io/docs/current/sql/create-table.html)
- [CREATE TABLE AS SELECT](https://trino.io/docs/current/sql/create-table-as.html) (不支持 `CREATE OR REPLACE TABLE AS SELECT`)
- [DROP TABLE](https://trino.io/docs/current/sql/drop-table.html)
- [ALTER TABLE](https://trino.io/docs/current/sql/alter-table.html)
- [CREATE SCHEMA](https://trino.io/docs/current/sql/create-schema.html)
- [DROP SCHEMA](https://trino.io/docs/current/sql/drop-schema.html)
- [COMMENT](https://trino.io/docs/current/sql/comment.html)

### 事务

- [START TRANSACTION](https://trino.io/docs/current/sql/start-transaction.html)
- [COMMIT](https://trino.io/docs/current/sql/commit.html)
- [ROLLBACK](https://trino.io/docs/current/sql/rollback.html)

有关更多信息，请参阅 Trino [SQL 语句支持](https://trino.io/docs/current/language/sql-support.html#sql-globally-available)
