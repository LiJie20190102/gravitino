---
title: "Spark Connector: JDBC Catalog"
slug: "/spark-connector/spark-catalog-jdbc"
keyword: "spark connector jdbc catalog"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino Spark 连接器提供了读取 JDBC 表的能力，其元数据由 Gravitino 服务器管理。

## 准备工作

1. 下载相应的 jdbc driver jar 到 Spark classpath 中。

## 能力

支持 MySQL 和 PostgreSQL。兼容 MySQL 的 OceanBase 可以使用 MySQL 驱动作为变通方案。不支持 MySQL 方言的 Doris 不受支持。

### DML 和 DDL 操作

- `CREATE TABLE`
- `DROP TABLE`
- `ALTER TABLE`
- `SELECT`
- `INSERT`

  :::info
JDBCTable 不支持分布式事务。在向 RDBMS 写入数据时，每个任务都是一个独立的事务。如果 spark 的部分任务成功而部分任务失败，就会产生脏数据。
  :::

### 不支持的操作

- `UPDATE`
- `DELETE`
- `TRUNCATE`

## SQL 示例

```sql
-- Suppose mysql_a is the mysql catalog name managed by Gravitino
USE mysql_a;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

CREATE TABLE IF NOT EXISTS employee (
  id bigint,
  name string,
  department string,
  hire_date timestamp
)
DESC TABLE EXTENDED employee;

INSERT INTO employee
VALUES
(1, 'Alice', 'Engineering', TIMESTAMP '2021-01-01 09:00:00'),
(2, 'Bob', 'Marketing', TIMESTAMP '2021-02-01 10:30:00'),
(3, 'Charlie', 'Sales', TIMESTAMP '2021-03-01 08:45:00');

SELECT * FROM employee WHERE date(hire_date) = '2021-01-01';


```

## 目录属性

Gravitino spark 连接器会将 catalog 属性中定义的以下属性名称转换为 Spark JDBC 连接器配置。

| Gravitino catalog 属性名称 | Spark JDBC 连接器配置 | 描述                                                                                       |
|---------------------------------|------------------------------------|---------------------------------------------------------------------------------------------------|
| `jdbc-url`                      | `url`                              | 用于连接数据库的 JDBC URL。例如，jdbc:mysql://localhost:3306                 |
| `jdbc-user`                     | `jdbc.user`                        | JDBC 用户名                                                                                    |
| `jdbc-password`                 | `jdbc.password`                    | JDBC 密码                                                                                     |
| `jdbc-driver`                   | `driver`                           | JDBC 连接的驱动程序。例如，com.mysql.jdbc.Driver 或 com.mysql.cj.jdbc.Driver |

带有 `spark.bypass.` 前缀的 Gravitino catalog 属性名称将传递给 Spark JDBC connector。

