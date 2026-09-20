---
title: "Trino Connector: MySQL Catalog"
slug: "/trino-connector/catalog-mysql"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

MySQL catalog 允许在外部 MySQL 实例中查询和创建表。
借此，可以在不同系统（如 MySQL 和 Hive）之间，或两个不同的 MySQL 实例之间关联数据。

## 要求

要连接到 MySQL，您需要：
- MySQL 5.7、8.0 或更高版本。
- 从 Trino 协调器和工作节点到 MySQL 的网络访问权限。默认端口为 3306。

## 创建表

目前，Apache Gravitino Trino 连接器仅支持基本的 MySQL 建表语句，涉及字段、是否允许为空、注释、主键、索引、默认值和自增。
Gravitino Trino 连接器支持 `CREATE TABLE AS SELECT`。

:::note
不支持 `CREATE OR REPLACE TABLE AS SELECT`。作为替代方案，请使用 `DROP TABLE` 然后再使用 `CREATE TABLE AS SELECT`。
:::

## 修改表

支持以下 alter table 操作：
- 重命名表
- 添加列
- 删除列
- 更改列类型
- 设置表属性

## 选择

Gravitino Trino 连接器支持大多数 SELECT 语句，能够成功执行查询。
它不支持某些查询优化，例如索引和下推。

## 更新

仅支持带有常量赋值和谓词的 `UPDATE` 语句。另请参阅 [UPDATE 限制](https://trino.io/docs/current/connector/mysql.html#update-limitation)。

## 删除

如果指定了 `WHERE` 子句，则仅删除匹配的行。否则，将删除表中的所有行。另请参见 [DELETE 限制](https://trino.io/docs/current/connector/mysql.html#delete-limitation)。

## 合并

不支持。

## 表和模式属性

MySQL 的模式不支持属性。

以下是支持的 MySQL 表属性：

| 属性名称         | 类型   | 默认值 | 描述                                                                                                                             | 必填 |
|-----------------------|--------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------|----------|
| engine                | string | InnoDB        | MySQL 表使用的引擎。                                                                                                       | 否       |
| auto_increment_offset | string | (none)        | 表的自动增量偏移量。                                                                                                | 否       |
| primary_key           | list   | (none)        | 表的主键，可以选择多列作为表的主键。所有键列必须定义为 `NOT NULL`。       | 否       |
| unique_key            | list   | (none)        | 表的唯一键，可以选择多列组成多个唯一键。每个唯一键应定义为 `keyName:col1,col2`。 | 否       |

以下是支持的 MySQL 列属性：

| 属性名称  | 类型    | 默认值 | 描述                   | 必填 |
|----------------|---------|---------------|-------------------------------|----------|
| auto_increment | boolean | false         | 自增列。    | 否       |
| default        | string  | (none)        | 列的默认值。 | 否       |

**注意：** 创建表仅支持常量默认值。不支持表达式默认值。 `SHOW CREATE TABLE` 也仅显示常量默认值。
以下是支持配置默认值的 Trino 类型：

| 类型名称 | 默认值示例                   |
|-----------|-----------------------------------------|
| TINYINT   | 1                                       |
| SMALLINT  | 1                                       | 
| INT       | 1                                       | 
| BIGINT    | 1                                       | 
| REAL      | 1.0                                     | 
| DOUBLE    | 1.0                                     | 
| DECIMAL   | 1.0                                     | 
| VARCHAR   | abc                                     | 
| CHAR      | abc                                     | 
| DATE      | 2025-08-07                              | 
| TIME      | 01:01:01                                | 
| TIMESTAMP | 2025-08-07 01:01:01 (CURRENT_TIMESTAMP) |

## 示例

完成以下步骤，然后才能通过 Gravitino 在 Trino 中使用 MySQL catalog：

- 在 Gravitino 中创建一个 metalake 和 catalog。假设 metalake 名称为 `test`，catalog 名称为 `mysql_test`，
那么你可以使用以下代码在 Gravitino 中创建它们：

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "test",
  "comment": "comment",
  "properties": {}
}' http://gravitino-host:8090/api/metalakes

curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "mysql_test",
  "type": "RELATIONAL",
  "comment": "comment",
  "provider": "jdbc-mysql",
  "properties": {
    "jdbc-url": "jdbc:mysql://mysql-host:3306?useSSL=false",
    "jdbc-user": "<username>",
    "jdbc-password": "<password>"
    "jdbc-driver": "com.mysql.cj.jdbc.Driver"
  }
}' http://gravitino-host:8090/api/metalakes/test/catalogs
```

有关 MySQL catalog 的更多信息，请参阅 [MySQL catalog](../jdbc-mysql-catalog.md)。

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
 mysql_test
(4 rows)

Query 20231017_082503_00018_6nt3n, FINISHED, 1 node
```

`gravitino` 目录是一个由 Trino 目录配置定义的目录。
`mysql_test` 目录是您在 Gravitino 中创建的目录。
其他目录是常规的用户配置的 Trino 目录。

### 创建表和模式

在 `test.mysql_test` catalog 中创建一个名为 `database_01` 的新 schema。

```sql
CREATE SCHEMA mysql_test.database_01;
```

在模式 `mysql_test.database_01` 中创建一个名为 `table_01` 的新表。

```sql
CREATE TABLE mysql_test.database_01.table_01
(
name varchar,
salary int
);
```

在模式 `mysql_test.database_01` 中创建一个名为 `table_index` 的新表，包含主键和索引。

```sql
CREATE TABLE mysql_test.database_01.table_index (
   key1 integer NOT NULL,
   key2 integer,
   key3 integer,
   key4 integer,
   key5 integer NOT NULL,
   col1 integer
)
COMMENT ''
WITH (
   engine = 'InnoDB',
   primary_key = ARRAY['key5','key1'],
   unique_key = ARRAY['unique_key1:key2','unique_key2:key4,key3']
);
```

在模式 `mysql_test.database_01` 中创建一个名为 `table_column_properties` 的新表，带有 auto_increment 和 default 属性。

```sql
CREATE TABLE mysql_test.database_01.table_column_properties(
    key1 INT NOT NULL WITH (auto_increment=true),
    f1 VARCHAR(200) WITH (default='VARCHAR'),
    f2 CHAR(20) WITH (default='CHAR') ,
    f4 DECIMAL(10, 3) WITH (default='0.3') ,
    f5 REAL WITH (default='0.3') ,
    f6 DOUBLE WITH (default='0.3') ,
    f8 TINYINT WITH (default='1') ,
    f9 SMALLINT WITH (default='1') ,
    f10 INT WITH (default='1') ,
    f11 INTEGER WITH (default='1') ,
    f12 BIGINT WITH (default='1'),
    f13 DATE WITH (default='2024-04-01'),
    f14 TIME WITH (default='08:00:00'),
    f15 TIMESTAMP WITH (default='2012-12-31 11:30:45'),
    f16 TIMESTAMP WITH TIME ZONE WITH (default='2012-12-31 11:30:45'),
    f17 TIMESTAMP WITH TIME ZONE WITH (default='CURRENT_TIMESTAMP')
)
WITH (
   primary_key = ARRAY['key1']
);
```

### 写入数据

向表 `table_01` 中插入数据：

```sql
INSERT INTO mysql_test.database_01.table_01 (name, salary) VALUES ('ice', 12);
```

从 select 将数据插入到表 `table_01` 中：

```sql
INSERT INTO mysql_test.database_01.table_01 (name, salary) SELECT * FROM "test.mysql_test".database_01.table_01;
```

将数据更新到表 `table_01` 中：

```sql
UPDATE mysql_test.database_01.table_01 SET name = 'ice_update' WHERE salary = 12;
```

从表 `table_01` 中删除数据：

```sql
DELETE FROM mysql_test.database_01.table_01 WHERE salary = 12;
DELETE FROM mysql_test.database_01.table_01;
```

### 查询数据

查询 `table_01` 表：

```sql
SELECT * FROM mysql_test.database_01.table_01;
```

### 修改表

向 `table_01` 表添加一个新列 `age`：

```sql
ALTER TABLE mysql_test.database_01.table_01 ADD COLUMN age int;
```

从 `table_01` 表中删除 `age` 列：

```sql
ALTER TABLE mysql_test.database_01.table_01 DROP COLUMN age;
```

将 `table_01` 表重命名为 `table_02`：

```sql
ALTER TABLE mysql_test.database_01.table_01 RENAME TO mysql_test.database_01.table_02;
```

### DROP

删除模式：

```sql
DROP SCHEMA mysql_test.database_01;
```

删除表：

```sql
DROP TABLE mysql_test.database_01.table_01;
```
