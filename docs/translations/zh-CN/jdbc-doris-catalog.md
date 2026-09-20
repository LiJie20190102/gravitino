---
title: "Doris Catalog"
slug: "/jdbc-doris-catalog"
keywords:
- jdbc
- Apache Doris
- metadata
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 介绍

Apache Gravitino 提供了通过 JDBC 连接管理 [Apache Doris](https://doris.apache.org/) 元数据的能力。

:::caution
Gravitino 在 schema 和表的注释中保存了一些系统信息，例如
`(From Gravitino, DO NOT EDIT: gravitino.v1.uid1078334182909406185)`，请勿更改或删除此消息。
:::

## 目录

### 目录能力

- Gravitino catalog 对应 Doris 实例。
- 支持 Doris (1.2.x, 3.0.x, 4.0.x) 的元数据管理。
- 支持表索引（PRIMARY_KEY, UNIQUE_KEY, INVERTED, BITMAP (旧版), ANN/VECTOR）。
- 支持[列默认值](./tables-and-views.md#table-column-default-value)。

### 目录属性

将 Gravitino 未定义的任何属性传递给 Doris 数据源，可通过添加
`gravitino.bypass.` 前缀作为 catalog 属性。例如，catalog 属性
`gravitino.bypass.maxWaitMillis` 会将 `maxWaitMillis` 传递给数据源属性。

Check the relevant data source configuration in
[data source properties](https://commons.apache.org/proper/commons-dbcp/configuration.html) for
more details.

除了[通用 catalog 属性](./gravitino-server-config.md#catalog-properties-configuration)之外，Doris catalog 还具有以下属性：

| 配置项      | 描述                                                                                       | 默认值 | 必填 |
|-------------------------|---------------------------------------------------------------------------------------------------|---------------|----------|
| `jdbc-url`              | 用于连接数据库的 JDBC URL。例如，`jdbc:mysql://localhost:9030`               | (无)        | 是      |
| `jdbc-driver`           | JDBC 连接的驱动程序。例如，`com.mysql.jdbc.Driver`。                          | (无)        | 是      |
| `jdbc-user`             | JDBC 用户名。                                                                               | (无)        | 是      |
| `jdbc-password`         | JDBC 密码。                                                                                | (无)        | 是      |
| `jdbc.pool.min-size`    | 连接池中的最小连接数。默认为 `2`。                                    | `2`           | 否       |
| `jdbc.pool.max-size`    | 连接池中的最大连接数。默认为 `10`。                                   | `10`          | 否       |
| `jdbc.pool.max-wait-ms` | 连接池等待连接返回的最大持续时间。默认为 `30000`。 | `30000`       | 否       |

在使用 Doris Catalog 之前，您必须将相应的 JDBC 驱动程序下载到 `catalogs/jdbc-doris/libs` 目录中。
由于许可问题，Gravitino 不打包 Doris 的 JDBC 驱动程序。

### 驱动程序版本兼容性

Doris catalog 包含用于 datetime 精度计算的驱动版本兼容性检查：

- **MySQL Connector/J 版本 >= 8.0.16**：完全支持日期时间精度计算
- **MySQL Connector/J 版本 < 8.0.16**：有限支持 - 日期时间精度计算返回 `null` 并附带警告日志

此限制影响以下日期时间类型：
- `DATETIME(p)` - 日期时间精度

当使用不受支持的驱动程序版本时，系统将：
1. 继续以默认精度 (0) 正常工作
2. 记录一条警告信息，指出驱动程序版本的限制
3. 在精度计算时返回 `null` 以避免错误结果

**示例警告日志：**
```
WARN: MySQL driver version mysql-connector-java-8.0.11 is below 8.0.16, 
columnSize may not be accurate for precision calculation. 
Returning null for DATETIME type precision. Driver version: mysql-connector-java-8.0.11
```

**推荐的驱动版本：**
- `mysql-connector-java-8.0.16` 或更高版本

### 目录操作

有关更多详细信息，请参阅[管理目录和模式](./manage-catalogs-and-schemas.md#catalog-operations)。

:::note
敏感的目录属性（例如 `jdbc-password`）在默认的加载目录响应中被隐藏（`jdbc-user` 以明文形式返回）。通过 `getSecrets` / `GET .../objects/{type}/{fullName}/secrets` 检索由 secret-manager 支持的属性（包括当作为 secret URN 存储时的 `jdbc-password`）。[凭据分发 API](security/credential-vending.md)（`getCredentials` / `JdbcCredential`）仍然可用于类型化凭据交付。
:::

## 模式

### 模式能力

- Gravitino 的 schema 概念对应于 Doris 数据库。
- 支持创建 schema。
- 支持删除 schema。

### Schema 属性

- 支持 schema 属性，包括 Doris 数据库属性和用户自定义属性。

### Schema Operations

请参阅
[管理目录和架构](./manage-catalogs-and-schemas.md#schema-operations) 以获取更多详细信息。

## 表格

### 表格功能

- Gravitino 的表概念对应于 Doris 表。
- 支持索引。
- 支持[列默认值](./tables-and-views.md#table-column-default-value)。

#### 表格列类型

| Gravitino 类型             | Doris 类型           |
|----------------------------|----------------------|
| `Boolean`                  | `Boolean`            |
| `Byte`                     | `TinyInt`            |
| `Short`                    | `SmallInt`           |
| `Integer`                  | `Int`                |
| `Long`                     | `BigInt`             |
| `Float`                    | `Float`              |
| `Double`                   | `Double`             |
| `Decimal`                  | `Decimal`            |
| `Date`                     | `Date`/`DateV2`      |
| `Timestamp[(p)]`           | `Datetime[(p)]`      |
| `VarChar`                  | `VarChar`            |
| `FixedChar`                | `Char`               |
| `String`                   | `String`             |
| `Binary`                   | `Binary`/`VarBinary` |
| `ExternalType("json")`     | `JSON`               |
| `ExternalType("variant")`  | `Variant`            |
| `ExternalType("ipv4")`     | `IPv4`               |
| `ExternalType("ipv6")`     | `IPv6`               |
| `ExternalType("largeint")` | `LargeInt`           |
| `ExternalType("bitmap")`   | `Bitmap`             |
| `ExternalType("hll")`      | `HLL`                |

Doris 不支持 Gravitino 的 `Fixed` `Timestamp_tz` `IntervalDay` `IntervalYear` `Union` `UUID` 类型。
上述列表之外的数据类型将映射为 Gravitino 的 **[Unparsed Type](./tables-and-views.md#unparsed-type)**，表示无法解析的数据类型。

:::note
Doris 的 `array`、`map` 和 `struct` 类型作为 `ExternalType` 加载，并保留完整的类型字符串（例如 `array<int(11)>`）。它们不会被解析为 Gravitino 原生复合类型（`ListType`、`MapType`、`StructType`）。`ExternalType` 中的类型标识符始终为小写（例如 `"json"`，而不是 `"JSON"`），这与 Doris JDBC 元数据行为相匹配。
:::

:::tip Version Compatibility
- `DateV2` 类型：Doris 1.2+（在 4.0.x 版本中当 `disable_datev1=true` 时必需）
- `Binary` / `VarBinary` 类型：Doris 4.0+（在 3.x 版本中不可用）
- `Auto-Increment` 列：Doris 2.1+
- `INVERTED` 索引：Doris 3.0+
- `ANN` / `VECTOR` 索引：Doris 4.0.6+
:::


### 表列自增

Doris 2.1+ 支持自增列。Gravitino 在创建表时会验证 Doris 版本，并在较旧版本上拒绝使用自增列。

Doris 强制执行以下约束（违反约束会被 Doris 服务器拒绝）：

- 表必须使用 `UNIQUE KEY` 或 `DUPLICATE KEY` 模型。
- 自增列必须是 `BIGINT NOT NULL` 且没有 `DEFAULT` 值。
- 每个表最多只能有一个自增列。

:::note
Gravitino 目前支持通过 `UNIQUE_KEY` 索引类型创建 `UNIQUE KEY` 表。要创建 `DUPLICATE KEY` 表，请在表定义中省略键索引 —— 当未指定键时，Doris 默认使用 DUPLICATE 模型。
:::

<Tabs groupId='language' queryString>
<TabItem value="json" label="JSON">

```json
{
  "columns": [
    {
      "name": "id",
      "type": "long",
      "nullable": false,
      "autoIncrement": true
    }
  ],
  "indexes": [
    {
      "indexType": "unique_key",
      "name": "id_key",
      "fieldNames": [["id"]]
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Column column = Column.of("id", Types.LongType.get(), "", false, true, null);
Index[] indexes = new Index[] {
    Indexes.of(Index.IndexType.UNIQUE_KEY, "id_key", new String[][]{{"id"}}, Map.of())
};
```

</TabItem>
</Tabs>

### 表格属性

Doris 表属性可以在创建表时设置。
仅支持 Doris 内置表属性；不支持用户自定义属性。

| 属性名称                      | 描述                                                                                                                                                                                 | 默认值 | 必填 | 保留 | 不可变 |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|----------|-----------|
| `replication_num`                  | 表的副本数。如果未指定且后端服务器数量少于 3，则默认值为 1；如果 BE ≥ 3，将使用服务端默认值（3）。 | `1` 或 `3`    | 否       | 否       | 否        |
| `replication_allocation`           | 表的副本分配策略。不能与 `replication_num` 同时设置。                                                                                          | (无)        | 否       | 否       | 否        |
| `compression`                      | 表的压缩类型。支持的值：`ZSTD`、`LZ4`、`LZ4F`、`ZLIB`。在 Doris 4.0+ 中已弃用作为表级属性。建表后无法更改。            | (无)        | 否       | 否       | 是       |
| `bloom_filter_columns`             | 用于创建布隆过滤器索引的列的逗号分隔列表。                                                                                                                 | (无)        | 否       | 否       | 否        |
| `storage_policy`                   | 冷热分离的存储策略名称。                                                                                                                                     | (无)        | 否       | 否       | 否        |
| `light_schema_change`              | 表是否启用 light schema change。可以通过 ALTER TABLE SET 修改。                                                                                                  | `true`        | 否       | 否       | 否        |
| `enable_unique_key_merge_on_write` | Unique Key 表是否启用 merge-on-write。必须在 CREATE TABLE 时设置；创建后无法更改。                                                                | `true`        | 否       | 否       | 是       |

:::note
**不可变**属性可以在 CREATE TABLE 时设置，但不能通过 ALTER TABLE 更改。
**保留**属性（目前没有）是只读的，不能由用户设置。
:::

### 表索引

Doris catalog 支持以下索引类型。每个索引适用于单列。

| Gravitino 索引类型 | Doris DDL                                                              | Doris 版本 |
|----------------------|------------------------------------------------------------------------|---------------|
| `PRIMARY_KEY`        | `` INDEX `PRIMARY` (col) `` (在 INDEX 子句中，无 USING)            | 1.2+          |
| `UNIQUE_KEY`         | `UNIQUE KEY(col)` (在表模型部分，非 INDEX 子句)       | 1.2+          |
| `INVERTED`           | `INDEX name (col) USING INVERTED [PROPERTIES(...)]`                    | 3.0+          |
| `BITMAP`             | `INDEX name (col)` (裸形式，无 USING 子句；只写，见下方说明) | 1.2+          |
| `VECTOR`             | `INDEX name (col) USING ANN`                                           | 4.0.6+        |

:::note
- `PRIMARY_KEY` 作为裸索引保留在 INDEX 子句中（例如 `` INDEX `PRIMARY` (`id`) ``），没有 USING 子句。
- `UNIQUE_KEY` 作为表模型声明输出（例如 `` UNIQUE KEY(`id`) ``），位于 INDEX 子句之外。
- `INVERTED` 属性可以通过 `Index.properties()`（用于 CREATE TABLE）或 `TableChange.AddIndex.getProperties()`（用于 ALTER TABLE）提供。加载的原生和 Gravitino 创建的 INVERTED 索引通过 `Index.properties()` 暴露有效的 Doris 属性。支持的键、值和服务器添加的默认值取决于 Doris 版本，并由 Doris 验证。
- `SHOW INDEX` 不会转义属性键或值中嵌入的双引号。因此，Gravitino 不保证它们的往返一致性，并拒绝超出支持的扁平引号对格式的元数据。
- 索引注释目前不由 Gravitino `Index` API 表示，并且在往返过程中不会被保留。
- `BITMAP` 是一种只写的遗留类型，用于与 Doris 1.2.x 向后兼容。写入路径生成裸 `INDEX`（没有 USING 子句），但读取路径将其映射回 `INVERTED`，因为 Doris 4.0.6 从语法中移除了 BITMAP。创建 BITMAP 索引并读回时将显示 `INVERTED`。
:::

**主键示例：**

<Tabs groupId='language' queryString>
<TabItem value="json" label="JSON">

```json
{
  "indexes": [
    {
      "indexType": "primary_key",
      "name": "PRIMARY",
      "fieldNames": [["id"]]
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Index[] indexes = new Index[] {
    Indexes.of(IndexType.PRIMARY_KEY, "PRIMARY", new String[][]{{"id"}}, Map.of())
};
```

</TabItem>
</Tabs>

**倒排索引示例（Doris 3.0+）：**

<Tabs groupId='language' queryString>
<TabItem value="json" label="JSON">

```json
{
  "indexes": [
    {
      "indexType": "inverted",
      "name": "idx_name",
      "fieldNames": [["name"]],
      "properties": {
        "parser": "english",
        "support_phrase": "true"
      }
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Index[] indexes = new Index[] {
    Indexes.of(
        IndexType.INVERTED,
        "idx_name",
        new String[][]{{"name"}},
        Map.of("parser", "english", "support_phrase", "true"))
};
```

</TabItem>
</Tabs>

### 表分区

Doris catalog 支持分区表。
用户可以在 Doris catalog 中使用特定的分区属性创建分区表。在创建 Doris 表时，也支持预分配分区。
请注意，尽管 Gravitino 支持多种分区策略，但 Apache Doris 本身仅支持以下两种分区策略：

- `RANGE`
- `LIST`

:::caution
分区属性中指定的 `fieldName` 必须是表中定义的列的名称。
:::

### 表分布

用户也可以在 Doris catalog 中创建表时指定分布策略。Doris catalog 支持以下分布策略：
- `HASH`
- `RANDOM`

对于 `RANDOM` 分布策略，Gravitino 使用 `EVEN` 来表示它。关于 Gravitino 中定义的分布策略的更多信息可以在[这里](./table-partitioning-distribution-sort-order-indexes.md#table-distribution)找到。


### 表格操作

请参阅[使用 Gravitino 管理关系元数据](./manage-relational-metadata-using-gravitino.md#table-operations)以获取更多详细信息。

#### 修改表操作

Gravitino 支持这些表变更操作：

- `RenameTable`
- `UpdateComment`
- `AddColumn`
- `DeleteColumn`
- `UpdateColumnType`
- `UpdateColumnPosition`
- `UpdateColumnComment`
- `SetProperty`

请注意：

- 并非所有的表修改操作都可以批量处理。
- Schema 变更，例如添加/修改/删除列，可以批量处理。
- 支持同时修改多个列注释。
- 不支持同时修改列类型和列注释。
- Doris 中的 schema 变更是异步的。你可能会获取到过时的 schema，如果你
在变更后立即执行 schema 查询。在变更后短暂
暂停。Gravitino 将在
即将发布的版本中，在 schema 信息中展示 schema 变更状态以解决此问题。
