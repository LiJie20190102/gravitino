---
title: "Spark Connector: Paimon Catalog"
slug: "/spark-connector/spark-catalog-paimon"
keyword: "spark connector paimon catalog"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino Spark 连接器提供了读写 Paimon 表的能力，其元数据由 Gravitino 服务器管理。

## 准备工作

1. 在 Spark 配置中将 `spark.sql.gravitino.enablePaimonSupport` 设置为 `true`。
2. 下载 Paimon Spark runtime jar 到 Spark classpath。

:::info
Paimon 目录仅在 Spark 3.5 上可用。Paimon 首次发布 `paimon-spark-4.0` 是在
Paimon 1.3.0，高于 Gravitino 当前依赖的版本，因此 Spark 4 连接器构建时
不包含 Paimon 类。
:::

## 能力

### DDL 和 DML 操作

- `CREATE NAMESPACE`
- `DROP NAMESPACE`
- `LIST NAMESPACE`
- `LOAD NAMESPACE`
- 不支持返回用户指定的配置；spark-connector 目前仅支持 FilesystemCatalog。
- `CREATE TABLE`
- 不支持分布和排序顺序。
- `DROP TABLE`
- `ALTER TABLE`
- `LIST TABLE`
- `DESRICE TABLE`
- `SELECT`
- `INSERT INTO & OVERWRITE`
- `Schema Evolution`
- `PARTITION MANAGEMENT`，例如 `LIST PARTITIONS`、`ALTER TABLE ... DROP PARTITION ...`

:::info
目前仅支持 HDFS 上的 Paimon FilesystemCatalog。
:::

#### 不支持的操作

- `ALTER NAMESPACE`
- Paimon 不支持修改命名空间。
- 行级操作，例如 `MERGE INTO`、`DELETE`、`UPDATE`、`TRUNCATE`
- 元数据表，例如 `{paimon_catalog}.{paimon_database}.{paimon_table}$snapshots`
- 其他 Paimon 扩展 SQL，例如 `Tag`
- Call 语句
- 视图
- 时间旅行
- Hive 和 Jdbc 后端，以及用于 FilesystemCatalog 的对象存储

## SQL 示例

```sql
-- Suppose paimon_catalog is the Paimon catalog name managed by Gravitino
USE paimon_catalog;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

CREATE TABLE IF NOT EXISTS employee (
  id bigint,
  name string,
  department string,
  hire_date timestamp
) PARTITIONED BY (name);

SHOW TABLES;
DESC TABLE EXTENDED employee;

INSERT INTO employee
VALUES
(1, 'Alice', 'Engineering', TIMESTAMP '2021-01-01 09:00:00'),
(2, 'Bob', 'Marketing', TIMESTAMP '2021-02-01 10:30:00'),
(3, 'Charlie', 'Sales', TIMESTAMP '2021-03-01 08:45:00');

SELECT * FROM employee WHERE name = 'Alice';

SHOW PARTITIONS employee;
ALTER TABLE employee DROP PARTITION (`name`='Alice');
```

## 目录属性

Gravitino spark connector 会将在 catalog properties 中定义的以下属性名称转换为 Spark Paimon connector 配置。

| Gravitino 目录属性名称 | Spark Paimon 连接器配置 | 描述               |
|---------------------------------|--------------------------------------|---------------------------|
| `catalog-backend`               | `metastore`                          | Catalog 后端类型      |
| `uri`                           | `uri`                                | Catalog 后端 uri       |
| `warehouse`                     | `warehouse`                          | Catalog 后端仓库 |

带有 `spark.bypass.` 前缀的 Gravitino catalog 属性名称会被传递给 Spark Paimon 连接器。例如，使用 `spark.bypass.client-pool-size` 将 `client-pool-size` 传递给 Spark Paimon 连接器。
