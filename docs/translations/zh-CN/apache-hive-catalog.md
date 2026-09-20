---
slug: /apache-hive-catalog
date: 2023-12-10
keyword: hive catalog
license: This software is licensed under the Apache License version 2.
---
## 简介

Apache Gravitino 提供了使用 [Apache Hive](https://hive.apache.org) 作为目录进行元数据管理的能力。

### 要求与限制

* Hive 目录需要一个 Hive Metastore 服务 (HMS)，或者 HMS 的兼容实现，例如 AWS Glue。
* Gravitino 必须能够使用 Thrift 协议通过网络访问 Hive metastore 服务。

:::note
Hive 目录支持 HMS 2.x 版本。它可以自动检测 HMS 版本。
:::

## 目录

### 目录功能

Hive 目录支持在 HMS 中创建、更新和删除数据库和表。

### 目录属性

除了[通用目录属性](./gravitino-server-config.md#catalog-properties-configuration)外，Hive 目录还具有以下属性：

| 属性名称                            | 描述                                                                                                                                                                                                                                         | 默认值 | 是否必需                     |
|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|------------------------------|
| `metastore.uris`                         | Hive metastore 服务 URI，多个地址用逗号分隔。例如 `thrift://127.0.0.1:9083`                                                                                                                                         | (无)        | 是                          |
| `client.pool-size`                       | Gravitino 池中 Hive metastore 客户端的最大数量。                                                                                                                                                                             | 1             | 否                           |
| `gravitino.bypass.`                      | 使用此前缀的属性名称将传递给底层 HMS 客户端使用。例如 `gravitino.bypass.hive.metastore.failure.retries = 3` 表示 Thrift metastore 调用失败时重试 3 次                                   | (无)        | 否                           |
| `client.pool-cache.eviction-interval-ms` | 缓存池逐出间隔。                                                                                                                                                                                                                   | 300000        | 否                           |
| `impersonation-enable`                   | 为 Hive 目录启用用户模拟。                                                                                                                                                                                                         | false         | 否                           |
| `kerberos.principal`                     | 目录的 Kerberos 主体。如果要使用 Kerberos，您应配置 `gravitino.bypass.hadoop.security.authentication`、`gravitino.bypass.hive.metastore.kerberos.principal` 和 `gravitino.bypass.hive.metastore.sasl.enabled`。 | (无)        | 如果使用 kerberos 则需要 |
| `kerberos.keytab-uri`                    | 目录的 keytab URI。目前支持的协议有 `https`、`http`、`ftp`、`file`。                                                                                                                                                     | (无)        | 如果使用 kerberos 则需要 |
| `kerberos.check-interval-sec`            | 检查主体有效性的间隔                                                                                                                                                                                                     | 60            | 否                           |
| `kerberos.keytab-fetch-timeout-sec`      | 获取 keytab 的超时时间                                                                                                                                                                                                                        | 60            | 否                           |
| `list-all-tables`                        | 是否列出数据库中的所有表，包括非 Hive 表，如 Iceberg、Paimon 和 Hudi。当为 false 时，会尽最大努力过滤掉非 Hive 表；有关已知限制，请参阅下面的注释。                               | false         | 否                           |
| `default.catalog`                        | Hive3 metastore 后端的默认目录名称；使用 Hive2 metastore 时忽略此配置。                                                                                                                               | hive          | 否                           |

:::note
当 `list-all-tables=false` 时，Hive 目录会尽最大努力移除以下内容：
- Iceberg 表（表属性 `table_type=ICEBERG`）
- Paimon 表（表属性 `table_type=PAIMON`）
- Hudi 表（表属性 `provider=hudi`），以及它们的 `_ro` 兄弟表

**已知限制。** 过滤是通过 Hive Metastore 在服务端执行的，它仅
支持对无点属性键进行精确键查找。由 Spark 直接注册的 Hudi 表
（例如通过 `saveAsTable`）通常仅设置 `spark.sql.sources.provider=hudi`，而不会同时
设置 `provider=hudi`，因此无法将它们过滤掉，它们会出现在列表中。

**解决方法。** 向此类表添加无点的 `provider=hudi` 属性，以便服务端
过滤器可以匹配它们。可以在创建后：

```sql
ALTER TABLE <db>.<table> SET TBLPROPERTIES ('provider'='hudi');
```

或者在写入时通过 Hudi 的 Hive 同步选项：

```scala
df.write.format("hudi")
  .option("hoodie.datasource.hive_sync.table_properties", "provider=hudi")
  .saveAsTable("<db>.<table>")
```

相应的 `_ro` / `_rt` 兄弟表会根据基表名称自动移除。
:::

当将 Gravitino 与 Trino 一起使用时，使用 `trino.bypass.` 前缀传递 Trino Hive 连接器配置。例如，使用 `trino.bypass.hive.config.resources` 将 `hive.config.resources` 传递给 Trino 运行时中的 Gravitino Hive 目录。

当将 Gravitino 与 Spark 一起使用时，使用 `spark.bypass.` 前缀传递 Spark Hive 连接器配置。例如，使用 `spark.bypass.hive.exec.dynamic.partition.mode` 将 `hive.exec.dynamic.partition.mode` 传递给 Spark 运行时中的 Spark Hive 连接器。

当将 Gravitino 授权用于 Hive 与 Apache Ranger 时，请参阅[使用 Ranger 属性授权 Hive](security/authorization-pushdown.md#configure-the-ranger-hadoop-sql-plugin)

### 目录操作

有关更多详细信息，请参阅[管理目录和模式](./manage-catalogs-and-schemas.md#catalog-operations)。

:::note
敏感的目录属性（如凭证分发密钥）会从默认的加载目录响应中隐藏。通过 `getSecrets` / `GET .../objects/{type}/{fullName}/secrets` 检索由秘密管理器支持的属性（包括与凭证分发重叠的密钥）。[凭证分发 API](security/credential-vending.md) 仍可用于类型化凭证传递。
:::

## 模式

### 模式功能

Hive 目录支持在 HMS 中创建、更新和删除数据库。

### 模式属性

模式属性为底层 Hive 数据库提供或设置元数据。
下表列出了 Hive 数据库的预定义模式属性。此外，您可以定义自己的键值对属性，并将其传递给底层 Hive 数据库。

| 属性名称 | 描述                                                              | 默认值                                                                           | 是否必需 |
|---------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------|
| `location`    | Hive 数据库存储的目录，例如 `/user/hive/warehouse`。 | HMS 默认使用 `hive-site.xml` 中的 `hive.metastore.warehouse.dir` 值。 | 否       |

### 模式操作

请参阅[管理目录和模式](./manage-catalogs-and-schemas.md#schema-operations)。

## 表

### 表功能

- Hive 目录支持在 HMS 中创建、更新和删除表。
- 不支持列默认值。

### 表分区

Hive 目录支持[分区表](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-PartitionedTables)。用户可以在 Hive 目录中使用特定的分区属性创建分区表。
尽管 Gravitino 支持多种分区策略，但 Apache Hive 本身仅支持单一分区策略（按列分区）。因此，Hive 目录仅支持 `Identity` 分区。

:::caution
分区属性中指定的 `fieldName` 必须是表中定义的列名。
:::

### 表排序和分布

Hive 目录支持[分桶排序表](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-BucketedSortedTables)。用户可以在 Hive 目录中使用特定的 `distribution` 和 `sortOrders` 属性创建分桶排序表。
尽管 Gravitino 支持多种分布策略，但 Apache Hive 本身仅支持单一分布策略（按列聚集）。因此 Hive 目录仅支持 `Hash` 分布。

:::caution
`distribution` 和 `sortOrders` 属性中指定的 `fieldName` 必须是表中定义的列名。
:::

### 表列类型

Hive 目录支持 [Hive Language Manual](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types) 中定义的所有数据类型。
下表列出了从 Hive 目录映射到 Gravitino 的数据类型。

| Hive 数据类型              | Gravitino 数据类型 |
|-----------------------------|---------------------|
| `boolean`                   | `boolean`           |
| `tinyint`                   | `byte`              |
| `smallint`                  | `short`             |
| `int`/`integer`             | `integer`           |
| `bigint`                    | `long`              |
| `float`                     | `float`             |
| `double`/`double precision` | `double`            |
| `decimal`                   | `decimal`           |
| `string`                    | `string`            |
| `char`                      | `char`              |
| `varchar`                   | `varchar`           |
| `timestamp`                 | `timestamp`         |
| `date`                      | `date`              |
| `interval_year_month`       | `interval_year`     |
| `interval_day_time`         | `interval_day`      |
| `binary`                    | `binary`            |
| `array`                     | `list`              |
| `map`                       | `map`               |
| `struct`                    | `struct`            |
| `uniontype`                 | `union`             |

:::info
1. 除上面列出的数据类型外，其他数据类型映射到 Gravitino **[外部类型](./tables-and-views.md#external-type)**，表示从 Hive 目录无法解析的数据类型。
2. 对 Hive 表使用带字段注释的 `struct` 数据类型会抛出错误，因为它不适用于 Hive 表（请参阅 [HIVE-26593](https://issues.apache.org/jira/browse/HIVE-26593)）。
:::

### 表属性

表属性为底层 Hive 表提供或设置元数据。
下表列出了 Hive 表的预定义表属性。此外，您可以定义自己的键值对属性，并将其传递给底层 Hive 数据库。

:::note
<strong>保留</strong>：无法传递给 Gravitino 服务器的字段。

<strong>不可变</strong>：一旦设置就无法修改的字段。
:::

| 属性名称           | 描述                                                                                                                                | 默认值                                                                                                                                       | 是否必需 | 是否保留 | 是否不可变 |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|----------|----------|-----------|
| `location`              | 表存储的位置，例如 `/user/hive/warehouse/test_table`。                                                                 | HMS 默认使用数据库位置作为父目录。                                                                                  | 否       | 否       | 是       |
| `table-type`            | 表的类型。有效值包括 `MANAGED_TABLE` 和 `EXTERNAL_TABLE`。                                                              | `MANAGED_TABLE`                                                                                                                                     | 否       | 否       | 是       |
| `format`                | 表文件格式。有效值包括 `TEXTFILE`、`SEQUENCEFILE`、`RCFILE`、`ORC`、`PARQUET`、`AVRO`、`JSON`、`CSV` 和 `REGEX`。    | `TEXTFILE`                                                                                                                                          | 否       | 否       | 是       |
| `input-format`          | 表的输入格式类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcInputFormat`。                                           | 属性 `format` 设置默认值 `org.apache.hadoop.mapred.TextInputFormat`，并可将其更改为其他默认值。                   | 否       | 否       | 是       |
| `output-format`         | 表的输出格式类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat`。                                         | 属性 `format` 设置默认值 `org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat`，并可将其更改为其他默认值。 | 否       | 否       | 是       |
| `serde-lib`             | 表的 serde 库类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcSerde`。                                                | 属性 `format` 设置默认值 `org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe`，并可将其更改为其他默认值。         | 否       | 否       | 是       |
| `serde.parameter.`      | serde 参数的前缀，例如 `"serde.parameter.orc.create.index" = "true"`，表示 `ORC` serde 库创建行索引 | (无)                                                                                                                                              | 否       | 否       | 是       |
| `serde-name`            | serde 的名称                                                                                                                      | 默认使用表名。                                                                                                                              | 否       | 否       | 是       |
| `comment`               | 用于存储表注释。                                                                                                             | (无)                                                                                                                                              | 否       | 是      | 否        |
| `numFiles`              | 用于存储表中的文件数量。                                                                                            | (无)                                                                                                                                              | 否       | 是      | 否        |
| `totalSize`             | 用于存储表的总大小。                                                                                                 | (无)                                                                                                                                              | 否       | 是      | 否        |
| `EXTERNAL`              | 指示表是否为外部表。                                                                                                   | (无)                                                                                                                                              | 否       | 是      | 否        |
| `transient_lastDdlTime` | 用于存储表的最后 DDL 时间。                                                                                              | (无)                                                                                                                                              | 否       | 是      | 否        |

### 表索引

- 不支持表索引。

### 表操作

有关更多详细信息，请参阅[使用 Gravitino 管理关系元数据](./manage-relational-metadata-using-gravitino.md#table-operations)。

#### 修改操作

Gravitino 已经定义了一套统一的[元数据操作接口](./manage-relational-metadata-using-gravitino.md#alter-a-table)，并且几乎所有 [Hive Alter 操作](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-AlterTable/Partition/Column) 都有对应的表更新请求，使你能够更改现有表的结构。
下表列出了 Hive Alter 操作与 Gravitino 表更新请求之间的映射关系。

##### 修改表

| Hive Alter 操作                          | Gravitino 表更新请求 |
|-----------------------------------------------|--------------------------------|
| `Rename Table`                                | `Rename table`                 |
| `Alter Table Properties`                      | `Set a table property`         |
| `Alter Table Comment`                         | `Update comment`               |
| `Alter SerDe Properties`                      | `Set a table property`         |
| `Remove SerDe Properties`                     | `Remove a table property`      |
| `Alter Table Storage Properties`              | 不支持                    |
| `Alter Table Skewed or Stored as Directories` | 不支持                    |
| `Alter Table Constraints`                     | 不支持                    |

:::note
由于 Gravitino 有单独的接口用于更新表的注释，Hive catalog 将 `comment` 设置为表的保留属性，从而阻止用户设置 comment 属性。Apache Hive 可以修改表的 comment 属性。
:::

##### 修改列

| Hive Alter 操作     | Gravitino 表更新请求    |
|--------------------------|-----------------------------------|
| `Change Column Name`     | `Rename a column`                 |
| `Change Column Type`     | `Update the type of a column`     |
| `Change Column Position` | `Update the position of a column` |
| `Change Column Comment`  | `Update the column comment`       |

##### 修改分区

:::note
对修改分区的支持正在开发中。
:::

## 视图

### 视图功能

- 支持对以 `VIRTUAL_VIEW` 形式存储在 Hive Metastore Service 中的视图执行列出、创建、加载、修改和删除操作。
- 每个视图必须恰好包含一个 SQL 表示。
- 支持使用 `hive`、`trino`、`flink` 或 `spark` 方言创建视图。
- 加载现有 HMS 视图时，Gravitino 会自动检测该视图使用的是 `hive`、`trino`、`flink` 还是 `spark` 方言。
- 对于 `hive` 和 `flink` 方言，`defaultCatalog` 和 `defaultSchema` 必须为 `null`。
- 对于 `trino` 方言，设置 `defaultSchema` 时要求也必须设置 `defaultCatalog`（没有 catalog 的 schema 无法表示）。
- `trino` 方言要求至少有一个输出列，并使用 Trino 自有的原生 “Presto View” Hive Metastore 编码进行存储，因此通过 Gravitino 创建的视图可与指向同一 Hive Metastore 的原生 Trino/Presto Hive 连接器互操作，反之亦然。其依赖的 HMS `presto_view` 属性是保留属性，会根据视图的方言在内部进行管理；不能直接设置或移除该属性。Gravitino 的视图模型无法表示原生 Trino 视图的所有者、`runAsInvoker` 或 SQL 路径，因此如果要替换的现有原生视图对其中的任一属性使用了非默认值，操作会被拒绝，而不是静默丢弃该值。
- `flink` 方言要求至少设置一个带有 `flink.` 前缀的视图属性。Flink 连接器会自动设置 `flink.schema.num-columns`；直接使用 REST API 时，请显式设置至少一个 `flink.*` 属性。
- `spark` 方言要求设置视图属性 `spark.sql.create.version`；否则视图在重新加载时会按 `hive` 方言往返转换。

### 视图操作

有关更多详细信息，请参阅[使用 Gravitino 管理视图元数据](./manage-view-metadata-using-gravitino.md)。

## 使用 S3 存储的 Hive Catalog

要创建使用 S3 存储的 Hive catalog，可以参考 [使用 S3 的 Hive catalog](./hive-catalog-with-cloud-storage.md) 文档。Hive catalog 与 S3 存储配合使用时不需要特殊配置。
唯一的区别是文件的存储位置位于 S3。使用 `location` 为数据库或表指定 S3 路径。