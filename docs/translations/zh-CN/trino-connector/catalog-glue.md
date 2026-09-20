---
title: "Apache Gravitino Trino connector - Glue catalog"
slug: /trino-connector/catalog-glue
keyword: gravitino connector trino glue aws
license: "This software is licensed under the Apache License version 2."
---

## 概述

Glue 目录允许 Trino 查询存储在 AWS Glue Data Catalog 中注册的表中的数据。
它支持 Amazon S3 上的 Hive 格式和 Iceberg 格式的表。

## 要求

- 从 Trino 协调器和工作节点到 AWS Glue API 和 Amazon S3 的网络访问。
- 具有必要的 Glue 和 S3 权限的 AWS IAM 凭证（访问密钥对或实例配置文件）。
有关所需策略，请参见 [AWS IAM 权限](../aws-glue-catalog.md#aws-iam-permissions)。
- 存储在 Amazon S3 上的数据文件。

## 模式操作

### 创建 Schema

```sql
CREATE SCHEMA glue_test.schema_name;
```

## 表操作

### 创建 Hive 格式的表

默认表格式为 Hive。以下示例创建了一个 ORC 格式的分区表：

```sql
CREATE TABLE glue_test.db01.orders
(
  order_id  bigint,
  customer  varchar,
  amount    decimal(10, 2),
  order_dt  date
)
WITH (
  format       = 'ORC',
  location     = 's3://my-bucket/warehouse/db01/orders',
  partitioned_by = ARRAY['order_dt']
);
```

要创建一个分桶且排序的表：

```sql
CREATE TABLE glue_test.db01.events
(
  event_id bigint,
  user_id  bigint,
  ts       timestamp
)
WITH (
  format       = 'PARQUET',
  location     = 's3://my-bucket/warehouse/db01/events',
  bucketed_by  = ARRAY['user_id'],
  bucket_count = 8,
  sorted_by    = ARRAY['ts DESC']
);
```

### 创建 Iceberg 格式的表

设置 `type = 'ICEBERG'` 以创建 Iceberg 表。Iceberg 表支持更丰富的分区转换。

```sql
CREATE TABLE glue_test.db01.logs
(
  log_id   bigint,
  message  varchar,
  event_ts timestamp(6) with time zone
)
WITH (
  type         = 'ICEBERG',
  location     = 's3://my-bucket/warehouse/db01/logs',
  partitioned_by = ARRAY['hour(event_ts)']
);
```

`partitioned_by` 中支持的 Iceberg 分区转换表达式：

| 表达式          | 描述              |
|---------------------|--------------------------|
| `column`            | 恒等分区       |
| `year(column)`      | 按年分区        |
| `month(column)`     | 按月分区       |
| `day(column)`       | 按天分区         |
| `hour(column)`      | 按小时分区        |
| `bucket(column, N)` | 哈希到 N 个桶      |
| `truncate(column, W)` | 截断到宽度 W    |

:::note
不支持 `CREATE OR REPLACE TABLE AS SELECT`。作为替代方案，请使用 `DROP TABLE` 然后再使用 `CREATE TABLE AS SELECT`。
:::

### 修改表

支持以下 alter table 操作：

- 添加列
- 删除列
- 重命名列
- 更改列类型
- 设置表属性

:::caution
不支持 Hive 格式表的重命名。AWS Glue 不提供表的原生重命名 API。
支持 Iceberg 格式表的重命名。
:::

### 选择

```sql
SELECT * FROM glue_test.db01.orders WHERE order_dt = DATE '2024-01-01';
```

### 插入

```sql
INSERT INTO glue_test.db01.orders (order_id, customer, amount, order_dt)
VALUES (1, 'alice', 99.99, DATE '2024-01-01');
```

### 更新

`UPDATE` 仅在 Iceberg 表（v2 规范或更高版本）中受支持。

```sql
UPDATE glue_test.db01.logs SET message = 'updated' WHERE log_id = 1;
```

### 删除

对于 Hive 格式的表，仅当 `WHERE` 子句匹配整个分区时才支持 `DELETE`。
对于 Iceberg 表，支持行级删除。

```sql
-- Hive table: delete an entire partition
DELETE FROM glue_test.db01.orders WHERE order_dt = DATE '2024-01-01';

-- Iceberg table: row-level delete
DELETE FROM glue_test.db01.logs WHERE log_id = 42;
```

### 丢弃

```sql
DROP TABLE glue_test.db01.orders;

DROP SCHEMA glue_test.db01;
```

## 模式和表属性

### 创建带有属性的 Schema

```sql
CREATE SCHEMA glue_test.db01
WITH (
  location = 's3://my-bucket/warehouse/db01'
);
```

| 属性   | 描述                | 默认值 | 必填 |
|------------|----------------------------|---------------|----------|
| `location` | schema 的 S3 位置 | (无)        | 否       |

### 创建具有属性的表

```sql
CREATE TABLE glue_test.db01.table_name
(
  name   varchar,
  salary integer
) WITH (
  type           = 'HIVE',
  format         = 'PARQUET',
  location       = 's3://my-bucket/warehouse/db01/table_name',
  partitioned_by = ARRAY['salary'],
  bucketed_by    = ARRAY['name'],
  bucket_count   = 4,
  sorted_by      = ARRAY['name']
);
```

| 属性         | 描述                                                                              | 默认值                      | 必填 |
|------------------|------------------------------------------------------------------------------------------|------------------------------------|----------|
| `type`           | 表格式：`HIVE` 或 `ICEBERG`                                                        | `HIVE`                             | 否       |
| `format`         | Hive 格式表的文件格式：`PARQUET`、`ORC`、`TEXTFILE` 等                   | `TEXTFILE`                         | 否       |
| `location`       | 表的 S3 存储位置                                                        | (派生自 catalog `warehouse`) | 否       |
| `partitioned_by` | 分区列或表达式。对于 Iceberg，使用转换语法，例如 `year(col)`。 | (无)                             | 否       |
| `bucketed_by`    | 分桶列（仅限 Hive 格式表）                                                 | (无)                             | 否       |
| `bucket_count`   | 分桶数量（设置 `bucketed_by` 时必填）                                   | (无)                             | 否       |
| `sorted_by`      | 排序列，例如 `ARRAY['col ASC NULLS LAST', 'col2 DESC']`                      | (无)                             | 否       |

## 示例

按照以下步骤通过 Gravitino 在 Trino 中使用 Glue 目录。

### 在 Gravitino 中创建目录

使用 Trino CLI 创建 catalog。假设 metalake 为 `test`，catalog 名称为 `glue_test`：

```sql
CALL gravitino.system.create_catalog(
  'glue_test',
  'glue',
  MAP(
    ARRAY['aws-region', 'aws-access-key-id', 'aws-secret-access-key', 'warehouse'],
    ARRAY['us-east-1', '<aws-access-key-id>', '<aws-secret-access-key>', 's3://my-bucket/warehouse']
  )
);
```

有关 Glue catalog 的更多信息，请参阅 [AWS Glue catalog](../aws-glue-catalog.md)。

### 连接并列出目录

将 `gravitino.metalake` 设置为 `test` 并启动 Trino 容器。然后列出 catalog：

```sql
SHOW CATALOGS;
```

结果类似于：

```text
    Catalog
----------------
 gravitino
 glue_test
 jmx
 system
(4 rows)
```

`glue_test` 目录对应于在 Gravitino 中创建的目录。

## 数据类型映射

Glue 连接器扩展了 Hive 数据类型映射，增加了对 Iceberg 类型的支持。

| Gravitino 类型               | Trino 类型                   | 备注                                        |
|------------------------------|------------------------------|----------------------------------------------|
| `boolean`                    | `BOOLEAN`                    |                                              |
| `byte`                       | `TINYINT`                    |                                              |
| `short`                      | `SMALLINT`                   |                                              |
| `integer`                    | `INTEGER`                    |                                              |
| `long`                       | `BIGINT`                     |                                              |
| `float`                      | `REAL`                       |                                              |
| `double`                     | `DOUBLE`                     |                                              |
| `decimal(p, s)`              | `DECIMAL(p, s)`              |                                              |
| `string`                     | `VARCHAR`                    |                                              |
| `varchar(n)`                 | `VARCHAR(n)`                 |                                              |
| `char(n)`                    | `CHAR(n)`                    |                                              |
| `binary`                     | `VARBINARY`                  |                                              |
| `date`                       | `DATE`                       |                                              |
| `time(6)`                    | `TIME(6)`                    | 仅限 Iceberg 表；微秒精度                     |
| `timestamp`                  | `TIMESTAMP(3)`               | Hive 格式表；毫秒精度                          |
| `timestamp(6)`               | `TIMESTAMP(6)`               | Iceberg 表；微秒精度                           |
| `timestamptz(6)`             | `TIMESTAMP(6) WITH TIME ZONE`| 仅限 Iceberg 表                               |
| `list`                       | `ARRAY`                      |                                              |
| `map`                        | `MAP`                        |                                              |
| `struct`                     | `ROW`                        |                                              |

:::note
`TIME` 和 `TIMESTAMP WITH TIME ZONE` 仅适用于 Iceberg 格式的表。Hive 格式的表使用不带时区的毫秒精度 `TIMESTAMP`。
:::

## Trino 连接器配置

Gravitino 将 catalog 属性传递给底层的 Trino Hive 连接器。使用 `trino.bypass.` 前缀提供额外的 Trino 连接器属性：

```sql
CALL gravitino.system.create_catalog(
  'glue_test',
  'glue',
  MAP(
    ARRAY['aws-region', 'aws-access-key-id', 'aws-secret-access-key', 'warehouse',
          'trino.bypass.hive.metastore.glue.max-connections'],
    ARRAY['us-east-1', '<aws-access-key-id>', '<aws-secret-access-key>', 's3://my-bucket/warehouse',
          '50']
  )
);
```

以下 Gravitino catalog 属性会自动转发至 Trino connector，且无法通过 `trino.bypass.*` 覆盖：

| Gravitino 属性      | Trino 连接器属性              |
|-------------------------|---------------------------------------|
| `aws-region`            | `hive.metastore.glue.region`          |
| `aws-glue-catalog-id`   | `hive.metastore.glue.catalogid`       |
| `aws-access-key-id`     | `hive.metastore.glue.aws-access-key`, `hive.s3.aws-access-key` |
| `aws-secret-access-key` | `hive.metastore.glue.aws-secret-key`, `hive.s3.aws-secret-key` |
| `aws-glue-endpoint`     | `hive.metastore.glue.endpoint-url`    |

有关 Trino Hive 连接器的更多配置选项，请参阅
[Trino Hive 连接器文档](https://trino.io/docs/current/connector/hive.html)。
