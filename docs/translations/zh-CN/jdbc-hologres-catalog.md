---
title: "Hologres Catalog"
slug: "/jdbc-hologres-catalog"
keywords:
- jdbc
- Hologres
- metadata
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 介绍

Apache Gravitino 提供管理 [Hologres](https://help.aliyun.com/zh/hologres) 元数据的能力。

Hologres是阿里云提供的实时数据仓库服务，专为高并发和低延迟的在线分析处理（OLAP）而设计。Hologres完全兼容PostgreSQL协议，并使用PostgreSQL JDBC Driver进行连接。

:::caution
Gravitino 会在 schema 和表注释中保存一些系统信息，例如 `(From Gravitino, DO NOT EDIT: gravitino.v1.uid1078334182909406185)`，请勿更改或删除此消息。
:::

## 目录

### 目录能力

- Gravitino catalog 对应于一个 Hologres 数据库实例。
- 支持 Hologres 的元数据管理。
- 支持 Hologres schema 和表的 DDL 操作。
- 支持表索引（CREATE TABLE 中的 PRIMARY KEY）。
- 支持[列默认值](./tables-and-views.md#table-column-default-value)。
- 支持 LIST 分区（物理分区表和逻辑分区表）。
- 支持通过 `WITH` 子句设置 Hologres 特有的表属性（orientation、clustering_key、distribution_key 等）。
- 不支持[自增](./tables-and-views.md#table-column-auto-increment)。

### 目录属性

通过添加 `gravitino.bypass.` 前缀作为 catalog 属性，将 Gravitino 未定义的任何属性传递给 Hologres 数据源。例如，catalog 属性 `gravitino.bypass.maxWaitMillis` 会将 `maxWaitMillis` 传递给数据源属性。

检查 [数据源属性](https://commons.apache.org/proper/commons-dbcp/configuration.html) 中的相关数据源配置

如果使用 JDBC catalog，必须在 catalog 属性中提供 `jdbc-url`、`jdbc-driver`、`jdbc-database`、`jdbc-user` 和 `jdbc-password`。
除了[通用 catalog 属性](./gravitino-server-config.md#catalog-properties-configuration)之外，Hologres catalog 还具有以下属性：

| 配置项   | 描述                                                                                                                   | 默认值 | 必填 |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `jdbc-url`           | 用于连接数据库的 JDBC URL。例如，`jdbc:postgresql://hgprecn-cn-xxx.hologres.aliyuncs.com:80/my_database` | (无)        | 是      |
| `jdbc-driver`        | JDBC 连接的驱动程序。必须为 `org.postgresql.Driver`。                                                           | (无)        | 是      |
| `jdbc-database`      | 数据库名称。对于 Hologres 这是必填项。                                                                            | (无)        | 是      |
| `jdbc-user`          | JDBC 用户名（AccessKey ID 或数据库用户名）。                                                                       | (无)        | 是      |
| `jdbc-password`      | JDBC 密码（AccessKey Secret 或数据库密码）。                                                                    | (无)        | 是      |
| `jdbc.pool.min-size` | 连接池中的最小连接数。默认为 `2`。                                                                | `2`           | 否       |
| `jdbc.pool.max-size` | 连接池中的最大连接数。默认为 `10`。                                                               | `10`          | 否       |

:::caution
Hologres 使用 PostgreSQL JDBC Driver（建议使用 42.3.2 或更高版本）。您需要下载 PostgreSQL JDBC Driver，并将其放置在 Gravitino 发行版下的 `catalogs/jdbc-hologres/libs` 目录中（例如，`distribution/package/catalogs/jdbc-hologres/libs` 或 `distribution/package-all/catalogs/jdbc-hologres/libs`）。
:::

### 目录操作

有关更多详细信息，请参阅[管理目录和模式](./manage-catalogs-and-schemas.md#catalog-operations)。

:::note
敏感的目录属性（例如 `jdbc-password`）在默认的加载目录响应中被隐藏（`jdbc-user` 以明文形式返回）。通过 `getSecrets` / `GET .../objects/{type}/{fullName}/secrets` 检索由 secret-manager 支持的属性（包括当作为 secret URN 存储时的 `jdbc-password`）。[凭据分发 API](security/credential-vending.md)（`getCredentials` / `JdbcCredential`）仍然可用于类型化凭据交付。
:::

## 模式

### 模式能力

- Gravitino 的 schema 概念对应于 Hologres (PostgreSQL) 的 schema。
- 支持创建带注释的 schema。
- 支持删除 schema。
- 系统 schema 会被自动过滤：`pg_toast`、`pg_catalog`、`information_schema`、`hologres`、`hg_internal`、`hg_recyclebin`、`hologres_object_table`、`hologres_sample`、`hologres_streaming_mv`、`hologres_statistic`。

### Schema 属性

- 不支持任何 schema 属性设置。

### Schema Operations

有关更多详细信息，请参阅[管理目录和架构](./manage-catalogs-and-schemas.md#schema-operations)。

## 表格

### 表格功能

- Gravitino 的表概念对应于 Hologres 表。
- 支持 Hologres 表的 DDL 操作。
- 支持 CREATE TABLE 中的 PRIMARY KEY 索引。
- 支持[列默认值](./tables-and-views.md#table-column-default-value)。
- 通过 DEFAULT 表达式支持表达式列（注意：Gravitino 将这些映射为列默认值，而不是 Hologres 意义上真正的生成/计算列）。
- 支持 LIST 分区（物理和逻辑）。
- 不支持[自增](./tables-and-views.md#table-column-auto-increment)。在 CREATE TABLE 和 ALTER TABLE 中创建自增列会被拒绝。

### 表格属性

Hologres特定的表属性在CREATE TABLE期间通过`WITH`子句设置，并从`hologres.hg_table_properties`系统表中读取。支持以下与用户相关的属性：

| 属性键                        | 描述                       | 示例值                  |
|-------------------------------------|-----------------------------------|--------------------------------|
| `orientation`                       | 存储格式                    | `column`, `row`, `row,column`  |
| `clustering_key`                    | 聚簇键列            | `id:asc`                       |
| `segment_key`                       | 事件时间列（分段键）   | `create_time`                  |
| `bitmap_columns`                    | 位图索引列              | `status,category`              |
| `dictionary_encoding_columns`       | 字典编码列       | `city,province`                |
| `time_to_live_in_seconds`           | 数据 TTL 设置                  | `2592000`                      |
| `table_group`                       | 表组名称                  | `my_table_group`               |
| `storage_format`                    | 内部存储格式           | `orc`, `sst`                   |
| `binlog_level`                      | Binlog 级别                      | `replica`, `none`              |
| `binlog_ttl`                        | Binlog TTL                        | `86400`                        |

:::info
- Gravitino 尚不支持通过 ALTER TABLE `SetProperty` / `RemoveProperty` 修改表属性（Hologres 原生支持通过 `CALL HG_UPDATE_TABLE_PROPERTY` 或重建命令修改属性，但此功能尚未在 Gravitino 中实现）。
- 属性 `distribution_key`、`is_logical_partitioned_table` 和 `primary_key` 通过其专用参数（Distribution、Partitioning、Indexes）进行管理，不应直接在表属性中设置。
:::

### 表格列类型

| Gravitino 类型              | Hologres 类型              | 备注                                              |
|-----------------------------|----------------------------|----------------------------------------------------|
| `Boolean`                   | `bool`                     |                                                    |
| `Short`                     | `int2` (SMALLINT)          |                                                    |
| `Integer`                   | `int4` (INTEGER)           |                                                    |
| `Long`                      | `int8` (BIGINT)            |                                                    |
| `Float`                     | `float4` (REAL)            |                                                    |
| `Double`                    | `float8` (DOUBLE PRECISION)|                                                    |
| `Decimal(p,s)`              | `numeric(p,s)`             |                                                    |
| `VarChar(n)`                | `varchar(n)`               | 不带长度的 `varchar` 映射为 `String`          |
| `FixedChar(n)`              | `bpchar(n)` (CHAR)         |                                                    |
| `String`                    | `text`                     |                                                    |
| `Binary`                    | `bytea`                    |                                                    |
| `Date`                      | `date`                     |                                                    |
| `Time`                      | `time`                     | 带可选精度                            |
| `Timestamp`                 | `timestamp`                | 始终不带精度后缀输出             |
| `Timestamp_tz`              | `timestamptz`              | 始终不带精度后缀输出             |
| `List(IntegerType, false)`  | `int4[]` (`_int4`)         | 通过 `_` 前缀表示数组类型                          |
| `List(LongType, false)`     | `int8[]` (`_int8`)         |                                                    |
| `List(FloatType, false)`    | `float4[]` (`_float4`)     |                                                    |
| `List(DoubleType, false)`   | `float8[]` (`_float8`)     |                                                    |
| `List(BooleanType, false)`  | `bool[]` (`_bool`)         |                                                    |
| `List(StringType, false)`   | `text[]` (`_text`)         |                                                    |

:::info
- Hologres 不支持 `TIMESTAMP`/`TIMESTAMPTZ` 的精度语法（例如，`timestamptz(6)` 是无效的），因此类型转换器总是输出不带精度的基本类型。
- 数组元素类型必须是非空的（Hologres 限制）。不支持多维数组。
- `json`、`jsonb`、`uuid`、`inet`、`money`、`roaringbitmap` 等类型映射到 Gravitino **[External Type](./tables-and-views.md#external-type)**，并保留原始类型名称。
:::

### 表分布

Hologres 支持通过 `WITH` 子句中的 `distribution_key` 属性进行 HASH 分布。

<Tabs groupId='language' queryString>
<TabItem value="json" label="JSON">

```json
{
  "distribution": {
    "strategy": "hash",
    "number": 0,
    "funcArgs": [
      {
        "type": "field",
        "fieldName": ["id"]
      }
    ]
  }
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Distribution distribution = Distributions.hash(0, NamedReference.field("id"));
```

</TabItem>
</Tabs>

### 表分区

Hologres 支持 LIST 分区，包含两种变体：

- **物理分区表**：`PARTITION BY LIST(column)` — 仅支持 1 个分区列。
- **逻辑分区表**（Hologres V3.1+）：`LOGICAL PARTITION BY LIST(col1[, col2])` — 支持 1-2 个分区列。通过将属性 `is_logical_partitioned_table` 设置为 `true` 来启用。

<Tabs groupId='language' queryString>
<TabItem value="json" label="JSON">

```json
{
  "partitioning": [
    {
      "strategy": "list",
      "fieldNames": [["ds"]]
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Transform[] partitioning = new Transform[] {
    Transforms.list(new String[][] {{"ds"}})
};
```

</TabItem>
</Tabs>

:::note
尚不支持通过 Gravitino 创建分区子表（例如，`CREATE TABLE child PARTITION OF parent FOR VALUES IN ('value')`）。
:::

### Table Indexes

- Supports PRIMARY_KEY in CREATE TABLE.
- Adding or deleting indexes via ALTER TABLE is not yet supported by Gravitino (Hologres natively supports index modification via rebuild commands, but this is not yet implemented in Gravitino).

<Tabs groupId='language' queryString>
<TabItem value="json" label="JSON">

```json
{
  "indexes": [
    {
      "indexType": "primary_key",
      "name": "pk_id",
      "fieldNames": [["id"]]
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Index[] indexes = new Index[] {
    Indexes.of(IndexType.PRIMARY_KEY, "pk_id", new String[][]{{"id"}}),
};
```

</TabItem>
</Tabs>

### Table Operations

Refer to [Manage Relational Metadata Using Gravitino](./manage-relational-metadata-using-gravitino.md#table-operations) for more details.

#### Alter Table Operations

Gravitino supports these table alteration operations for Hologres:

- `RenameTable`
- `UpdateComment`
- `AddColumn` (type and comment only; NOT NULL, default value, and auto-increment are not supported)
- `DeleteColumn`
- `RenameColumn`
- `UpdateColumnComment`

:::info
The following ALTER TABLE operations are **not supported** and will throw `IllegalArgumentException`:
- `UpdateColumnType`
- `UpdateColumnDefaultValue`
- `UpdateColumnNullability`
- `UpdateColumnPosition`
- `UpdateColumnAutoIncrement`
- `AddIndex`
- `DeleteIndex`
- `SetProperty`
- `RemoveProperty`
:::
