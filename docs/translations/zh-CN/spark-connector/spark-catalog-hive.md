---
title: "Spark Connector: Hive Catalog"
slug: "/spark-connector/spark-catalog-hive"
keyword: "spark connector hive catalog"
license: "This software is licensed under the Apache License version 2."
---

## 简介

借助 Apache Gravitino Spark 连接器，访问数据或管理 Hive catalog 中的元数据变得简单直接，从而实现跨不同 Hive catalog 的无缝联邦查询。

## 能力

支持 SparkSQL 中的大多数 DDL 和 DML 操作，除了以下操作：

- 函数操作（支持 Gravitino UDF，请参见 [Spark 连接器 - 用户定义函数](spark-connector-udf.md)）
- 分区操作
- 视图 DDL 操作（`CREATE VIEW`、`DROP VIEW`、`ALTER VIEW`）
- `LOAD` 子句
- `CREATE TABLE LIKE` 子句
- `TRUNCATE TABLE` 子句


:::info
不支持使用 `org.apache.hadoop.hive.serde2.OpenCSVSerde` 行格式读写表。
:::

## 先决条件

* Hive metastore 2.x
* HDFS 2.x 或 3.x

## SQL 示例


```sql

// Suppose hive_a is the Hive catalog name managed by Gravitino
USE hive_a;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

// Create table
CREATE TABLE IF NOT EXISTS employees (
    id INT,
    name STRING,
    age INT
)
PARTITIONED BY (department STRING)
STORED AS PARQUET;
DESC TABLE EXTENDED employees;

INSERT OVERWRITE TABLE employees PARTITION(department='Engineering') VALUES (1, 'John Doe', 30), (2, 'Jane Smith', 28);
INSERT OVERWRITE TABLE employees PARTITION(department='Marketing') VALUES (3, 'Mike Brown', 32);

SELECT * FROM employees WHERE department = 'Engineering';
```


## 视图

不支持 Spark DDL 视图操作（`CREATE VIEW`、`DROP VIEW`、`ALTER VIEW`）。但是，可以使用 `SELECT` 读取存储在 Hive Metastore 中的现有视图。当 `SELECT` 引用视图名称时，连接器会从 Gravitino 加载该视图的 SQL 定义，解析查询并执行它。

:::caution
当前实现使用 `LocalScan` 在 Spark driver 上物化所有视图结果。这仅适用于小型或有界视图。查询大型或无界视图可能会耗尽 driver 内存并导致 OOM 错误。
:::

```sql
-- Assumes a view was created via Gravitino API, Flink, or Hive directly
SELECT * FROM employee_view;
```

## 目录属性

Gravitino spark connector 将把在 catalog 属性中定义的以下属性名称转换为 Spark Hive connector 配置。

| Gravitino catalog 属性中的属性名称 | Spark Hive connector 配置 | 描述                |
|-----------------------------------------------|------------------------------------|----------------------------|
| `metastore.uris`                              | `hive.metastore.uris`              | Hive metastore uri 地址 |

带有 `spark.bypass.` 前缀的 Gravitino catalog 属性名称会被传递给 Spark Hive connector。例如，使用 `spark.bypass.hive.exec.dynamic.partition.mode` 将 `hive.exec.dynamic.partition.mode` 传递给 Spark Hive connector。


:::caution
当使用 `spark-sql` shell 客户端时，你必须在 Gravitino Hive catalog 属性中显式设置 `spark.bypass.spark.sql.hive.metastore.jars`。将默认的 `builtin` 值替换为适合你环境的设置。
:::


## 存储

### S3

参考[使用s3的Hive目录](../hive-catalog-with-cloud-storage.md)来设置带有s3存储的Hive目录。要查询存储在s3中的数据，您需要使用`spark.sql.catalog.${hive_catalog_name}.fs.s3a.access.key`和`spark.sql.catalog.${hive_catalog_name}.fs.s3a.secret.key`将s3密钥添加到Spark配置中。此外，下载[hadoop aws jar](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws)和[aws java sdk jar](https://mvnrepository.com/artifact/com.amazonaws/aws-java-sdk-bundle)，并将它们放在Spark的classpath中。
