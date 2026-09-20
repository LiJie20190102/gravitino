---
title: "ClickHouse Catalog"
slug: "/jdbc-clickhouse-catalog"
keywords:
- jdbc
- clickhouse
- metadata
license: "This software is licensed under the Apache License version 2.0."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 介绍

Apache Gravitino 可以通过 JDBC catalog 管理 ClickHouse 元数据。本文档描述了 ClickHouse catalog 的功能和限制，以及 catalog、schema 和 table 支持的操作和属性。

:::caution
由于 ClickHouse JDBC 驱动程序体积较大以及潜在的许可问题，标准的 Gravitino 服务器发行版中未包含 ClickHouse catalog。要使用 ClickHouse catalog，您可以从源代码构建，并参考文档 [how-to-build](./how-to-build.md) 获取更多详细信息。
:::

## 目录

### 目录能力

| 项目              | 描述                                                                                                                                                                                                   |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Scope             | 一个 catalog 映射到一个 ClickHouse 实例                                                                                                                                                                   |
| Metadata/DDL      | 支持基于 JDBC 的元数据管理和 DDL                                                                                                                                                               |
| Column defaults   | 支持列默认值                                                                                                                                                                                |
| Drivers           | 需要在 `${GRAVITINO_HOME}/catalogs/jdbc-clickhouse/libs` 中提供用户自备的 ClickHouse JDBC 驱动，从 [链接](https://repo1.maven.org/maven2/com/clickhouse/clickhouse-jdbc/0.7.1/) 下载 jar 包        |
| Supported version | 所有代码均通过 ClickHouse `24.8.14` 测试，较新版本如 `25.x` 可能也能正常工作，但我们未进行彻底测试。如果出现不符合预期的运行情况，请向社区报告。             |

### ClickHouse Server 与 JDBC Driver 兼容性矩阵

| ClickHouse 版本             | 支持的 ClickHouse JDBC 驱动版本 |
|--------------------------------|-------------------------------------------|
| `24.8.x` (包括 `24.8.14`) | `0.7.1 ~ 0.8.4`                           |

:::tip
对于其他 ClickHouse 版本（非 24.8.x），所需的 JDBC 驱动程序版本可能会有所不同。
请将您的预发布环境验证结果和官方 ClickHouse 文档作为最终参考。
:::

### 目录属性

通过添加 `gravitino.bypass.` 前缀来传递 Gravitino 未定义的任何 JDBC 连接池属性（例如 `gravitino.bypass.maxWaitMillis`）。详情请参见 [commons-dbcp 配置](https://commons.apache.org/proper/commons-dbcp/configuration.html)。

使用 JDBC catalog 时，必须提供 `jdbc-url`、`jdbc-driver`、`jdbc-user` 和 `jdbc-password`。常规 catalog 属性列在[此处](./gravitino-server-config.md#catalog-properties-configuration)；ClickHouse 未添加额外的 catalog 作用域键。

| 配置项      | 描述                                                           | 默认值 | 必填 |
|-------------------------|-----------------------------------------------------------------------|---------------|----------|
| `jdbc-url`              | JDBC URL，例如 `jdbc:clickhouse://localhost:8123`              | (无)        | 是      |
| `jdbc-driver`           | JDBC 驱动类，例如 `com.clickhouse.jdbc.ClickHouseDriver` | (无)        | 是      |
| `jdbc-user`             | JDBC 用户名                                                        | (无)        | 是      |
| `jdbc-password`         | JDBC 密码                                                         | (无)        | 是      |
| `jdbc.pool.min-size`    | 最小连接池大小                                                     | `2`           | 否       |
| `jdbc.pool.max-size`    | 最大连接池大小                                                     | `10`          | 否       |
| `jdbc.pool.max-wait-ms` | 连接的最大等待时间                                        | `30000`       | 否       |

### 创建 ClickHouse Catalog

以下示例使用所需的 JDBC 属性和可选的连接池设置创建了一个 ClickHouse catalog。请注意，`jdbc-driver` 类必须在 Gravitino classpath 中可用（例如，将 ClickHouse JDBC 驱动程序的 JAR 包放置在 `${GRAVITINO_HOME}/catalogs/jdbc-clickhouse/libs` 中）。
关于部分属性的说明：
- provider：必须为 `jdbc-clickhouse`，以便 Gravitino 将该 catalog 识别为 ClickHouse；
- type：必须为 `RELATIONAL`，因为 ClickHouse 是一个关系型数据库；


<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "ck",
  "type": "RELATIONAL",
  "comment": "ClickHouse catalog",
  "provider": "jdbc-clickhouse",
  "properties": {
    "jdbc-url": "jdbc:clickhouse://localhost:8123",
    "jdbc-driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "jdbc-user": "default",
    "jdbc-password": "password"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoClient client = GravitinoClient.builder("http://localhost:8090")
    .withMetalake("metalake")
    .build();

Map<String, String> ckProps = ImmutableMap.<String, String>builder()
    .put("jdbc-url", "jdbc:clickhouse://localhost:8123")
    .put("jdbc-driver", "com.clickhouse.jdbc.ClickHouseDriver")
    .put("jdbc-user", "default")
    .put("jdbc-password", "password")
    .build();

Catalog catalog =
    client.createCatalog("ck", Catalog.Type.RELATIONAL, "jdbc-clickhouse", "ClickHouse catalog", ckProps);
```

</TabItem>
</Tabs>

有关其他目录操作，请参阅[管理目录和模式](./manage-catalogs-and-schemas.md#catalog-operations)。

## 模式

### 模式能力

| 项目         | 描述                                                        |
|--------------|--------------------------------------------------------------------|
| 映射      | Gravitino schema 映射到 ClickHouse 数据库                     |
| 操作   | 创建 / 删除 / 加载 / 列出 (ClickHouse 支持级联删除)     |
| 注释     | 支持 Schema 注释                                          |
| 集群模式 | 提供 `cluster-name` 时，创建可选 `ON CLUSTER` |

### Schema 属性

| 属性名称  | 描述                                                                        | 默认值 | 必填 | 不可变 |
|----------------|------------------------------------------------------------------------------------|---------------|----------|-----------|
| `on-cluster`   | 创建数据库时使用 `ON CLUSTER`                                        | `false`       | 否       | 否        |
| `cluster-name` | 与 `ON CLUSTER` 一起使用的集群名称（必须与表级集群设置一致） | (无)        | 否       | 否        |

:::warning
**集群属性仅反映由 Gravitino 管理的模式。** Gravitino 在创建时将集群名称嵌入到模式的 `COMMENT` 字段中（因为对于标准的 Atomic 数据库，`SHOW CREATE DATABASE` 不包含 `ON CLUSTER`）。在 Gravitino 之外创建的模式将不会具有此元数据，因此在加载时 `on-cluster` 和 `cluster-name` 将缺失，并且 `DROP SCHEMA` 不会将 `ON CLUSTER` 传播到其他集群节点。
:::

### 创建 Schema

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "sales",
  "comment": "Sales database",
  "properties": {
    "on-cluster": "true",
    "cluster-name": "ck_cluster"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/ck/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("ck");
Schema schema = catalog.asTableCatalog()
    .createSchema("sales", "Sales database",
        ImmutableMap.of("on-cluster", "true", "cluster-name", "ck_cluster"));
```

</TabItem>
</Tabs>

有关更多模式操作，请参阅[管理目录和模式](./manage-catalogs-and-schemas.md#schema-operations)。

## 表格

### 表格功能

| 区域                | 详情                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 映射             | Gravitino 表映射到 ClickHouse 表                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 引擎             | **MergeTree 系列** (`MergeTree` 默认, `ReplacingMergeTree`, `SummingMergeTree`, `AggregatingMergeTree`, `CollapsingMergeTree`, `VersionedCollapsingMergeTree`, `GraphiteMergeTree`): 完全支持，数据在重启后持久化。**Log 系列** (`TinyLog`, `StripeLog`, `Log`): 支持，数据和表定义在重启后持久化。**`Null`**: 支持，表持久化，数据按设计总是被丢弃。**`Set`**: 支持，表定义持久化。**`Memory`**: ⚠️ 表定义持久化，但数据在 ClickHouse 重启后丢失（易失性）。**Distributed**: 具有远程数据库/表和分片键的集群模式。**无法通过 Gravitino 直接创建** (`Join`, `Buffer`, `View`, `KeeperMap`, `File`): 需要 CREATE TABLE API 不支持的参数化 ENGINE 子句或外部依赖。 |
| 排序/分区  | MergeTree 系列要求恰好一个 `ORDER BY` 列；MergeTree 引擎仅支持单列标识 `PARTITION BY`。其他引擎拒绝 `ORDER BY`/`PARTITION BY`。                                                                                                                                                                                                                                                                                    |
| 索引             | 主键；数据跳过索引 `DATA_SKIPPING_MINMAX`、`DATA_SKIPPING_BLOOM_FILTER`、`DATA_SKIPPING_SET`、`DATA_SKIPPING_NGRAMBFV1` 和 `DATA_SKIPPING_TOKENBFV1`（可通过 `Index.properties()` 配置粒度）。                                                                                                                                                                                                                                                                                                                                   |
| 分布        | Gravitino 强制使用 `Distributions.NONE`；无自定义分布策略。                                                                                                                                                                                                                                                                                                                                                                                               |
| 列默认值     | 支持。                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 不支持         | 创建后更改引擎；移除表属性；自增列。                                                                                                                                                                                                                                                                                                                                                                                          |

### 表格列类型

| Gravitino 类型      | ClickHouse 类型                        |
|---------------------|----------------------------------------|
| `Byte`              | `Int8`                                 |
| `Unsigned Byte`     | `UInt8`                                |
| `Short`             | `Int16`                                |
| `Unsigned Short`    | `UInt16`                               |
| `Integer`           | `Int32`                                |
| `Unsigned Integer`  | `UInt32`                               |
| `Long`              | `Int64`                                 |
| `Unsigned Long`     | `UInt64`                               |
| `Float`             | `Float32`                              |
| `Double`            | `Float64`                              |
| `Decimal(p,s)`      | `Decimal(p,s)`                         |
| `String`/`VarChar`  | `String`                               |
| `FixedChar(n)`      | `FixedString(n)`                       |
| `Date`              | `Date`                                 |
| `Timestamp[(p)]`    | `DateTime` (精度默认为 `0`) |
| `BOOLEAN`           | `Bool`                                 |
| `UUID`              | `UUID`                                 |

其他 ClickHouse 类型暴露为 [外部类型](./tables-and-views.md#external-type)。

### 表格属性

:::note
- `settings.*` 键被原样传递给 ClickHouse 的 `SETTINGS` 子句。
- `engine` 值在创建后是不可变的。
:::

:::warning
**集群属性仅反映由 Gravitino 管理的对象。**
对于非 Replicated 对象，ClickHouse 不会在 `SHOW CREATE TABLE` 或 `SHOW CREATE DATABASE` 的输出中持久化 `ON CLUSTER` 信息。Gravitino 通过在创建时将集群名称嵌入对象的 `COMMENT` 字段中，并在加载/删除时将其读回，从而解决了这一问题。

这意味着：
- **由 Gravitino 创建的数据库和表**：`on-cluster` 和 `cluster-name` 属性是准确的。
- **在 Gravitino 之外创建的数据库或表**（例如，通过 ClickHouse 客户端、迁移脚本或其他工具）：无论对象是否实际上是在 `ON CLUSTER` 上创建的，`on-cluster` 都将为 `false`，且 `cluster-name` 将不存在。随后通过 Gravitino 执行的 `DROP DATABASE` / `DROP TABLE` 操作将**不**包含 `ON CLUSTER`，这可能会在非协调集群节点上留下孤立对象。

如果你需要 Gravitino 管理现有的集群数据库或表，请通过 Gravitino API 重新创建它，以便正确嵌入集群元数据。
:::

:::warning
**Memory 引擎数据易失性**：使用 `engine=Memory` 创建的表仅将数据存储在 RAM 中。ClickHouse 服务器重启后，表定义会保留（Gravitino 的 `loadTable` 会成功），但所有数据将永久丢失。Gravitino 元数据和 ClickHouse 在 schema 级别保持一致，但用户需负责在重启后重新填充数据。如果需要数据持久性，请考虑使用 `TinyLog`、`StripeLog` 或 MergeTree 系列引擎。
:::

| 属性名称             | 描述                                                                                              | 默认值 | 必填   | 保留 | 不可变 |
|---------------------------|----------------------------------------------------------------------------------------------------------|---------------|------------|----------|-----------|
| `engine`                  | 表引擎（例如 `MergeTree`、`ReplacingMergeTree`、`Distributed`、`Memory` 等）              | `MergeTree`   | 否         | 否       | 是       |
| `graphite.config`         | `GraphiteMergeTree` 使用的 `<graphite_rollup>` 配置元素的名称                        | (无)        | 否\*\*\*   | 否       | 否        |
| `engine_parameters`       | 支持的参数化 MergeTree 引擎的参数                                                 | (无)        | 否         | 否       | 否        |
| `cluster-name`            | 与 `ON CLUSTER` 和 Distributed 引擎一起使用的集群名称                                               | (无)        | 否\*       | 否       | 否        |
| `on-cluster`              | 创建表时使用 `ON CLUSTER`                                                                 | (无)        | 否         | 否       | 否        |
| `cluster-remote-database` | `Distributed` 引擎的远程数据库                                                                 | (无)        | 否\*\*     | 否       | 否        |
| `cluster-remote-table`    | `Distributed` 引擎的远程表                                                                    | (无)        | 否\*\*     | 否       | 否        |
| `cluster-sharding-key`    | `Distributed` 引擎的分片键（允许使用表达式；引用的列必须是非空整数） | (无)        | 否\*\*     | 否       | 否        |
| `settings.<name>`         | 作为 `SETTINGS <name>=<value>` 转发的 ClickHouse 引擎设置                                         | (无)        | 否         | 否       | 否        |
| `partition-key`           | ClickHouse 的规范原生分区表达式（来自 `system.tables.partition_key`）。只读；加载时始终存在，空字符串表示未分区。 | `""`          | 否         | 是      | 是       |

\* 当 `on-cluster=true` 或 `engine=Distributed` 时必填。  
\*\* 当 `engine=Distributed` 时必填。
\*\*\* 当 `engine=GraphiteMergeTree` 时必填。

`engine_parameters` 属性适用于 `ReplacingMergeTree`、`SummingMergeTree`、`CollapsingMergeTree` 和 `VersionedCollapsingMergeTree`。在加载这些表时会恢复这些值，并且提供时必须不带外层括号。对于 `GraphiteMergeTree`，请改用 `graphite.config`。

### 表索引

- `PRIMARY_KEY`
- 数据跳过索引：
- `DATA_SKIPPING_MINMAX`（默认 `GRANULARITY 1`）
- `DATA_SKIPPING_BLOOM_FILTER`（默认 `GRANULARITY 1`）
- `DATA_SKIPPING_SET`（默认 `GRANULARITY 1`，加上可配置的 `set(N)` 最大值）
- `DATA_SKIPPING_NGRAMBFV1`（`GRANULARITY` 可通过 `Index.properties()` 自定义，默认为 1；需要在 `Index.properties()` 中提供 `ngram_size`、`bloom_filter_size`、`hash_functions`、`random_seed`）
- `DATA_SKIPPING_TOKENBFV1`（`GRANULARITY` 可通过 `Index.properties()` 自定义，默认为 1；需要在 `Index.properties()` 中提供 `bloom_filter_size`、`hash_functions`、`random_seed`）

可以通过 `Index.properties()` API 指定自定义 `GRANULARITY`（键 `granularity`，值必须为正整数）。对于 `DATA_SKIPPING_SET`，可以通过 `set_max_values` 配置最大唯一值数量（非负整数）。如果未指定，则适用上述默认值。

在没有 `system.data_skipping_indices.type_full` 的 ClickHouse 版本上，Gravitino 会回退到传统的元数据查询。如果传统的 `type` 值不包含 bloom-filter 参数，索引类型和字段会被保留，但无法重建所需的参数属性；在重新创建表之前，请显式提供这些属性。

字段表达式无法表示为 Gravitino 字段名称的 ClickHouse 数据跳过索引（例如 `lower(name)` 或 `name + 1`），在加载表时会被跳过并发出警告，且不会被重新创建。仍然支持直接列引用和仅包含列引用的元组。

### 分区、排序与分布

- `ORDER BY`: MergeTree 系列引擎必需，且仅支持列标识；
- 接受的格式：`id`、`(id, name)`、`(func(id), name)`、`func(id)`；
- 拒绝的格式：`(id + 1)`、`(func(id) + 1)` 等。

- `PARTITION BY`：仅支持单列标识和部分函数，且仅适用于 MergeTree 系列引擎。例如，支持 `PARTITION BY created_at` 或 `PARTITION BY toYYYYMM(created_at)`，但不支持 `PARTITION BY (created_at + 1)`。
总的来说，支持以下分区表达式：
- 标识：`PARTITION BY column_name`
- 函数：`PARTITION BY toDate(column_name)`、`PARTITION BY toYear(column_name)`、`PARTITION BY toYYYYMM(column_name)`。不支持其他函数。
- 不支持：`PARTITION BY (column_name + 1)`、`PARTITION BY (toYear(column_name) + 1)` 等。（注意：ClickHouse 本身确实支持任意分区表达式，但 Gravitino 仅支持上述分区模式）。

创建表时适用上述模式。加载表时，Gravitino 会在只读的 `partition-key` 属性中保留 ClickHouse 的规范原生分区表达式（由 `system.tables.partition_key` 返回）。因此，在加载时，即使无法将其映射到受支持的某个 `Transform`，任意的原生表达式也会被保留；在这种情况下，`Table.partitioning()` 为空，并且完整的表达式会通过 `partition-key` 暴露。

- 分布：固定为 `Distributions.NONE`。对于 `Distributed` 引擎表，您可以通过表属性指定分片键和远程数据库/表来满足相同的使用场景。如果后续有需求，我们将考虑添加更灵活的分布策略。

### 创建一个表格

以下示例创建了一个 `MergeTree` 表，包含 `ORDER BY`、分区、索引、注释以及包括 `ON CLUSTER` 在内的属性。请注意，MergeTree 系列表需要 `engine` 属性，并且如果 `on-cluster=true`，集群属性必须与 schema 级别的集群设置保持一致。

这是一个将在 ClickHouse 中执行的建表语句，用于创建相应的表：
```sql
CREATE TABLE sales.orders ON CLUSTER ck_cluster (
  order_id Int32,
  user_id Int32,
  amount Decimal(18,2),
  created_at DateTime,
  primary key (order_id),
) ENGINE = MergeTree order BY order_id PARTITION BY created_at;

```

可以通过 API 创建相同的表，如下所示：

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "orders",
  "comment": "Orders table",
  "columns": [
    {"name": "order_id", "type": "int", "nullable": false},
    {"name": "user_id", "type": "int", "nullable": false},
    {"name": "amount", "type": "decimal(18,2)", "nullable": false},
    {"name": "created_at", "type": "timestamp", "nullable": false}
  ],
  "properties": {
    "engine": "MergeTree",
    "on-cluster": "true",
    "cluster-name": "ck_cluster"
  },
  "sortOrders": [
    {"expression": "order_id", "direction": "ASCENDING"}
  ],
  "partitioning": ["created_at"],
  "indexes": [
    {"indexType": "primary_key", "name": "pk_order", "fieldNames": [["order_id"]]}
  ]
}' http://localhost:8090/api/metalakes/metalake/catalogs/ck/schemas/sales/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
TableCatalog tableCatalog = client.loadCatalog("ck").asTableCatalog();

Column[] columns = new Column[] {
    Column.of("order_id", Types.IntegerType.get(), "Order ID", false),
    Column.of("user_id", Types.IntegerType.get(), "User ID", false),
    Column.of("amount", Types.DecimalType.of(18, 2), "Amount", false),
    Column.of("created_at", Types.TimestampType.withoutTimeZone(), "Created time", false)
};

Index[] indexes =
    new Index[] {Indexes.of(Index.IndexType.PRIMARY_KEY, "pk_order", new String[][] {{"order_id"}})};

SortOrder[] sortOrders =
    new SortOrder[] {SortOrder.builder("order_id").withDirection(SortDirection.ASCENDING).build()};

Transform[] partitions = new Transform[] {Transforms.identity("created_at")};

tableCatalog.createTable(
    NameIdentifier.of("sales", "orders"),
    columns,
    "Orders table",
    ImmutableMap.of("engine", "MergeTree", "on-cluster", "true", "cluster-name", "ck_cluster"),
    partitions,
    Distributions.NONE,
    indexes,
    sortOrders);
```

</TabItem>
</Tabs>

### 表格操作

支持：
- 创建带有引擎、`ORDER BY`、可选分区、索引、注释、默认值和 `SETTINGS` 的表。
- 添加列（包含可空标志、默认值、注释、位置）。
- 重命名列。
- 更新列类型/注释/默认值/位置/可空性。
- 删除列（支持 `IF EXISTS`）。
- 添加和删除数据跳过索引；通过 `Index.properties()` 配置自定义 `GRANULARITY`、`set(N)` 以及 `ngrambf_v1`/`tokenbf_v1` 布隆过滤器参数。不支持添加/删除主键。
- 更新表注释。

不支持：
- 创建后更改引擎。
- 删除表属性或任意的 `ALTER TABLE ... SETTINGS`。
- 自增列。

有关常见 JDBC 语义，请参见[使用 Gravitino 管理关系型元数据](./manage-relational-metadata-using-gravitino.md#table-operations)。
