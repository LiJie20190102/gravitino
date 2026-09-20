---
title: "Trino Connector: PostgreSQL Catalog"
slug: "/trino-connector/catalog-postgresql"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

PostgreSQL 目录允许在外部 PostgreSQL 数据库中查询和创建表。
这可用于在 PostgreSQL 和 Hive 等不同系统之间，或在不同 PostgreSQL 实例之间联接数据。

## 要求

要连接到 PostgreSQL，您需要：
- PostgreSQL 10.x 或更高版本。
- 从 Trino 协调器和工作节点到 PostgreSQL 的网络访问权限。端口 5432 是默认端口。

## 大小写敏感

PostgreSQL 将未加引号的标识符视为不区分大小写。
例如，表名 MyTable 等同于 mytable 和 MYTABLE。

但是，如果你使用带引号的标识符创建表，例如 "MyTable"，它就会区分大小写，并且必须精确引用为 "MyTable"。

当将 Gravitino Trino 连接器与 PostgreSQL 一起使用时，必须使用不带引号的标识符以避免大小写敏感问题。
否则，包含大写字母的模式名、表名或列名可能无法找到。

## 创建表

目前，Apache Gravitino Trino 连接器仅支持基本的 PostgreSQL 建表语句，涉及字段、允许为空和注释。但是，它不支持主键、索引、默认值和自增等高级功能。
Gravitino Trino 连接器支持 `CREATE TABLE AS SELECT`。

:::note
不支持 `CREATE OR REPLACE TABLE AS SELECT`。作为替代方案，请使用 `DROP TABLE` 然后再使用 `CREATE TABLE AS SELECT`。
:::

## 修改表

Gravitino Trino 连接器支持以下修改表操作：
- 重命名表
- 添加列
- 删除列
- 重命名列
- 修改列类型
- 设置表属性

## 选择

Gravitino Trino 连接器支持大多数 SELECT 语句，能够成功执行查询。
它不支持某些查询优化，例如索引和下推。

## 更新

仅支持带有常量赋值和谓词的 `UPDATE` 语句。另请参阅 [UPDATE 限制](https://trino.io/docs/current/connector/postgresql.html#update-limitation)。

## 删除

如果指定了 `WHERE` 子句，则仅删除匹配的行。否则，将删除表中的所有行。另请参阅 [DELETE 限制](https://trino.io/docs/current/connector/postgresql.html#delete-limitation)。

## 合并

不支持。

## 表和模式属性

PostgreSQL 的表和模式不支持属性。

## 示例

在通过 Gravitino 在 Trino 中使用 PostgreSQL 目录之前，请完成以下步骤：

- 在 Gravitino 中创建 metalake 和 catalog。假设 metalake 名称为 `test` 且 catalog 名称为 `postgresql_test`，那么你可以使用以下代码在 Gravitino 中创建它们：

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "test",
  "comment": "comment",
  "properties": {}
}' http://gravitino-host:8090/api/metalakes

curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "postgresql_test",
  "type": "RELATIONAL",
  "comment": "comment",
  "provider": "jdbc-postgresql",
  "properties": {
    "jdbc-url": "jdbc:postgresql://postgresql-host/mydb",
    "jdbc-user": "<user>",
    "jdbc-password": "<password>",
    "jdbc-database": "mydb",
    "jdbc-driver": "org.postgresql.Driver"
  }
}' http://gravitino-host:8090/api/metalakes/test/catalogs
```
有关 PostgreSQL 目录的更多信息，请参阅 [PostgreSQL 目录](../jdbc-postgresql-catalog.md)。

- 将配置 `gravitino.metalake` 的值设置为您创建的名为 'test' 的 metalake，并启动 Trino 容器。

使用 Trino CLI 连接到 Trino 容器并运行查询。

列出所有 Gravitino 管理的目录：

```sql 
SHOW CATALOGS;
```

结果类似于：

```text
    Catalog
----------------
 gravitino
 jmx
 system
 postgresql_test
(4 rows)

Query 20231017_082503_00018_6nt3n, FINISHED, 1 node
```

`gravitino` 目录是由 Trino 目录配置定义的目录。
`postgresql_test` 目录是您在 Gravitino 中创建的目录。
其他目录是常规的用户配置的 Trino 目录。

### 创建表和模式

在 `postgresql_test` 目录中创建一个名为 `database_01` 的新模式。

```sql
CREATE SCHEMA postgresql_test.database_01;
```

在模式 `postgresql_test.database_01` 中创建一个名为 `table_01` 的新表。

```sql
CREATE TABLE postgresql_test.database_01.table_01
(
name varchar,
salary int
);
```

### 写入数据

向表 `table_01` 中插入数据：

```sql
INSERT INTO postgresql_test.database_01.table_01 (name, salary) VALUES ('ice', 12);
```

从 select 将数据插入到表 `table_01` 中：

```sql
INSERT INTO postgresql_test.database_01.table_01 (name, salary) SELECT * FROM postgresql_test.database_01.table_01;
```

将数据更新到表 `table_01` 中：

```sql
UPDATE postgresql_test.database_01.table_01 SET name = 'ice_update' WHERE salary = 12;
```

从表 `table_01` 中删除数据：

```sql
DELETE FROM postgresql_test.database_01.table_01 WHERE salary = 12;
DELETE FROM postgresql_test.database_01.table_01;
```

### 查询数据

查询 `table_01` 表：

```sql
SELECT * FROM postgresql_test.database_01.table_01;
```

### 修改表

向 `table_01` 表添加一个新列 `age`：

```sql
ALTER TABLE postgresql_test.database_01.table_01 ADD COLUMN age int;
```

从 `table_01` 表中删除 `age` 列：

```sql
ALTER TABLE postgresql_test.database_01.table_01 DROP COLUMN age;
```

将 `table_01` 表重命名为 `table_02`：

```sql
ALTER TABLE postgresql_test.database_01.table_01 RENAME TO postgresql_test.database_01.table_02;
```

### 丢弃

删除模式：

```sql
DROP SCHEMA postgresql_test.database_01;
```

删除表：

```sql
DROP TABLE postgresql_test.database_01.table_01;
```
