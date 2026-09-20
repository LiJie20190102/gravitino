---
slug: /apache-hive-catalog
date: 2023-12-10
keyword: hive catalog
license: This software is licensed under the Apache License version 2.
---
## 简介

Apache Gravitino 支持将 [Apache Hive](https://hive.apache.org) 作为元数据管理的 Catalog。

### 要求与限制

* Hive Catalog 需要 Hive Metastore Service (HMS) 或 HMS 的兼容实现，如 AWS Glue。
* Gravitino 必须能够通过 Thrift 协议访问 Hive metastore 服务。

:::note
Hive Catalog 支持 HMS 2.x 和 3.x 版本，能够自动检测 HMS 版本。
:::

## Catalog

### Catalog 能力

Hive Catalog 支持在 HMS 中创建、更新和删除数据库及表。

### Catalog 属性

除了[通用 Catalog 属性](./gravitino-server-config.md#catalog-properties-configuration)外，Hive Catalog 还具有以下属性：

| 属性名称                                  | 描述                                                                                                                                                                                                                                                | 默认值        | 是否必填                    |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|------------------------------|
| `metastore.uris`                         | Hive metastore 服务 URI，多个地址以逗号分隔。例如 `thrift://127.0.0.1:9083`                                                                                                                                                                            | (无)          | 是                          |
| `client.pool-size`                       | Gravitino 的 Hive metastore 客户端连接池最大数量。                                                                                                                                                                                                    | 1             | 否                           |
| `gravitino.bypass.`                      | 带有此前缀的属性名将传递给底层 HMS 客户端使用。例如 `gravitino.bypass.hive.metastore.failure.retries = 3` 表示 Thrift metastore 调用失败时重试 3 次                                                                                                        | (无)          | 否                           |
| `client.pool-cache.eviction-interval-ms` | 缓存池驱逐间隔。                                                                                                                                                                                                                                      | 300000        | 否                           |
| `impersonation-enable`                   | 为 Hive Catalog 启用用户模拟（impersonation）。                                                                                                                                                                                                       | false         | 否                           |
| `kerberos.principal`                     | Catalog 的 Kerberos principal。如果使用 Kerberos，需要配置 `gravitino.bypass.hadoop.security.authentication`、`gravitino.bypass.hive.metastore.kerberos.principal` 和 `gravitino.bypass.hive.metastore.sasl.enabled`。                                | (无)          | 使用 Kerberos 时必填         |
| `kerberos.keytab-uri`                    | Catalog 的 keytab URI。当前支持的协议包括 `https`、`http`、`ftp`、`file`。                                                                                                                                                                             | (无)          | 使用 Kerberos 时必填         |
| `kerberos.check-interval-sec`            | 检查 principal 有效性的间隔。                                                                                                                                                                                                                         | 60            | 否                           |
| `kerberos.keytab-fetch-timeout-sec`      | 获取 keytab 的超时时间。                                                                                                                                                                                                                              | 60            | 否                           |
| `list-all-tables`                        | 是否列出数据库中的所有表，包括 Iceberg、Paimon 和 Hudi 等非 Hive 表。设为 false 时，会尽力过滤非 Hive 表；已知限制见下方说明。                                                                                                                            | false         | 否                           |
| `default.catalog`                        | Hive3 metastore 后端的默认 Catalog 名称；使用 Hive2 metastore 时忽略此配置。                                                                                                                                                                              | hive          | 否                           |

:::note
当 `list-all-tables=false` 时，Hive Catalog 会尽力过滤以下内容：
- Iceberg 表（表属性 `table_type=ICEBERG`）
- Paimon 表（表属性 `table_type=PAIMON`）
- Hudi 表（表属性 `provider=hudi`），包括其 `_ro` 和 `_rt` 变体

**已知限制。** 过滤操作通过 Hive Metastore 在服务端执行，仅
支持对不含点号的属性键进行精确查找。由 Spark 直接注册的 Hudi 表
（例如通过 `saveAsTable`）通常只设置 `spark.sql.sources.provider=hudi`，而未同时
设置 `provider=hudi`，因此无法被过滤，仍会出现在列表中。

**变通方案。** 为此类表添加不含点号的 `provider=hudi` 属性，使服务端
过滤器能匹配到它们。可在创建后添加：

```sql
ALTER TABLE <db>.<table> SET TBLPROPERTIES ('provider'='hudi');
```

或在写入时通过 Hudi 的 Hive 同步选项设置：

```scala
df.write.format("hudi")
  .option("hoodie.datasource.hive_sync.table_properties", "provider=hudi")
  .saveAsTable("<db>.<table>")
```

相应的 `_ro` / `_rt` 变体会基于基础表名自动过滤。
:::

当 Gravitino 与 Trino 配合使用时，通过 `trino.bypass.` 前缀传递 Trino Hive 连接器配置。例如，使用 `trino.bypass.hive.config.resources` 将 `hive.config.resources` 传递给 Trino 运行时中的 Gravitino Hive Catalog。

当 Gravitino 与 Spark 配合使用时，通过 `spark.bypass.` 前缀传递 Spark Hive 连接器配置。例如，使用 `spark.bypass.hive.exec.dynamic.partition.mode` 将 `hive.exec.dynamic.partition.mode` 传递给 Spark 运行时中的 Spark Hive 连接器。

当使用 Apache Ranger 为 Hive 进行 Gravitino 授权时，参见 [Ranger 授权 Hive 属性](security/authorization-pushdown.md#configure-the-ranger-hadoop-sql-plugin)

### Catalog 操作

详情参见[管理 Catalog 和 Schema](./manage-catalogs-and-schemas.md#catalog-operations)。

:::note
敏感 Catalog 属性（如凭证分发密钥）在默认的加载 Catalog 响应中被隐藏。通过 `getSecrets` / `GET .../objects/{type}/{fullName}/secrets` 获取由 secret manager 支持的属性（包括与凭证分发重叠的密钥）。[凭证分发 API](security/credential-vending.md) 仍可用于类型化凭证传递。
:::

## Schema

### Schema 能力

Hive Catalog 支持在 HMS 中创建、更新和删除数据库。

### Schema 属性

Schema 属性用于提供或设置底层 Hive 数据库的元数据。
下表列出了 Hive 数据库的预定义 Schema 属性。此外，可以自定义键值对属性并传递给底层 Hive 数据库。

| 属性名称       | 描述                                                                     | 默认值                                                                                  | 是否必填 |
|---------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------|
| `location`    | Hive 数据库存储目录，例如 `/user/hive/warehouse`。                          | HMS 默认使用 `hive-site.xml` 中 `hive.metastore.warehouse.dir` 的值。                       | 否       |

### Schema 操作

参见[管理 Catalog 和 Schema](./manage-catalogs-and-schemas.md#schema-operations)。

## Table

### Table 能力

- Hive Catalog 支持在 HMS 中创建、更新和删除表。
- 不支持列默认值。

### Table 分区

Hive Catalog 支持[分区表](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-PartitionedTables)。可以通过指定分区属性在 Hive Catalog 中创建分区表。
尽管 Gravitino 支持多种分区策略，Apache Hive 本质上仅支持单一分区策略（按列分区）。因此，Hive Catalog 仅支持 `Identity` 分区。

:::caution
分区属性中指定的 `fieldName` 必须是表中已定义的列名。
:::

### Table 排序与分布

Hive Catalog 支持[分桶排序表](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-BucketedSortedTables)。可以通过指定 `distribution` 和 `sortOrders` 属性在 Hive Catalog 中创建分桶排序表。
尽管 Gravitino 支持多种分布策略，Apache Hive 本质上仅支持单一分布策略（按列聚簇）。因此，Hive Catalog 仅支持 `Hash` 分布。

:::caution
`distribution` 和 `sortOrders` 属性中指定的 `fieldName` 必须是表中已定义的列名。
:::

### Table 列类型

Hive Catalog 支持 [Hive 语言手册](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types) 中定义的所有数据类型。
下表列出了从 Hive Catalog 到 Gravitino 的数据类型映射。

| Hive 数据类型                | Gravitino 数据类型  |
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
1. 上述列表之外的数据类型映射为 Gravitino **[External Type](./tables-and-views.md#external-type)**，表示来自 Hive Catalog 的无法解析的数据类型。
2. 使用 `struct` 数据类型并附带字段注释会抛出错误，因为该功能不适用于 Hive 表（参见 [HIVE-26593](https://issues.apache.org/jira/browse/HIVE-26593)）。
:::

### Table 属性

Table 属性用于提供或设置底层 Hive 表的元数据。
下表列出了 Hive 表的预定义 Table 属性。此外，可以自定义键值对属性并传递给底层 Hive 数据库。

:::note
**保留（Reserved）**：无法传递给 Gravitino 服务端的字段。

**不可变（Immutable）**：一旦设置便无法修改的字段。
:::

| 属性名称                   | 描述                                                                                                                                      | 默认值                                                                                                                                              | 是否必填 | 保留     | 不可变    |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|----------|----------|-----------|
| `location`              | 表存储位置，例如 `/user/hive/warehouse/test_table`。                                                                                          | HMS 默认使用数据库位置作为父目录。                                                                                                                       | 否       | 否       | 是        |
| `table-type`            | 表类型。有效值包括 `MANAGED_TABLE` 和 `EXTERNAL_TABLE`。                                                                                       | `MANAGED_TABLE`                                                                                                                                     | 否       | 否       | 是        |
| `format`                | 表文件格式。有效值包括 `TEXTFILE`、`SEQUENCEFILE`、`RCFILE`、`ORC`、`PARQUET`、`AVRO`、`JSON`、`CSV` 和 `REGEX`。                                  | `TEXTFILE`                                                                                                                                          | 否       | 否       | 是        |
| `input-format`          | 表的输入格式类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcInputFormat`。                                                                     | `format` 属性设置默认值 `org.apache.hadoop.mapred.TextInputFormat`，可更改为其他默认值。                                                                  | 否       | 否       | 是        |
| `output-format`         | 表的输出格式类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat`。                                                                   | `format` 属性设置默认值 `org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat`，可更改为其他默认值。                                                  | 否       | 否       | 是        |
| `serde-lib`             | 表的 SerDe 库类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcSerde`。                                                                         | `format` 属性设置默认值 `org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe`，可更改为其他默认值。                                                          | 否       | 否       | 是        |
| `serde.parameter.`      | SerDe 参数前缀，例如 `"serde.parameter.orc.create.index" = "true"`，指示 `ORC` SerDe 库创建行索引                                                | (无)                                                                                                                                                | 否       | 否       | 是        |
| `serde-name`            | SerDe 名称。                                                                                                                                | 默认为表名。                                                                                                                                         | 否       | 否       | 是        |
| `comment`               | 用于存储表注释。                                                                                                                            | (无)                                                                                                                                                | 否       | 是       | 否        |
| `numFiles`              | 用于存储表中的文件数量。                                                                                                                    | (无)                                                                                                                                                | 否       | 是       | 否        |
| `totalSize`             | 用于存储表的总大小。                                                                                                                        | (无)                                                                                                                                                | 否       | 是       | 否        |
| `EXTERNAL`              | 指示表是否为外部表。                                                                                                                        | (无)                                                                                                                                                | 否       | 是       | 否        |
| `transient_lastDdlTime` | 用于存储表的最后 DDL 时间。                                                                                                                 | (无)                                                                                                                                                | 否       | 是       | 否        |

### Table 索引

- 不支持表索引。

### Table 操作

更多详情请参考[使用 Gravitino 管理关系型元数据](./manage-relational-metadata-using-gravitino.md#table-operations)。

#### 修改操作

Gravitino 已定义了一套统一的[元数据操作接口](./manage-relational-metadata-using-gravitino.md#alter-a-table)，几乎所有[Hive Alter 操作](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-AlterTable/Partition/Column)都有对应的表更新请求，可用于修改已有表的结构。
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
由于 Gravitino 提供了单独的接口用于更新表注释，Hive catalog 将 `comment` 设为表的保留属性，防止用户设置 comment 属性。Apache Hive 可以修改表的 comment 属性。
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
修改分区功能正在开发中。
:::

## 视图

### 视图能力

- 支持对存储在 Hive Metastore Service 中作为 `VIRTUAL_VIEW` 的视图进行列出、创建、加载、修改和删除操作。
- 每个视图必须包含且仅包含一个 SQL 表示。
- 支持使用 `hive`、`trino`、`flink` 或 `spark` 方言创建视图。
- 加载已有的 HMS 视图时，Gravitino 自动检测视图使用的是 `hive`、`trino`、`flink` 还是 `spark` 方言。
- 对于 `hive` 和 `flink` 方言，`defaultCatalog` 和 `defaultSchema` 必须为 `null`。
- 对于 `trino` 方言，`defaultSchema` 要求同时设置 `defaultCatalog`（没有 catalog 的 schema 无法表示）。
- `trino` 方言要求至少一个输出列，并使用 Trino 自有的原生 "Presto View" Hive Metastore 编码进行存储，因此通过 Gravitino 创建的视图与指向同一 Hive Metastore 的原生 Trino/Presto Hive 连接器互通，反之亦然。该功能依赖的 HMS `presto_view` 属性为保留属性，根据视图方言在内部管理，无法直接设置或移除。Gravitino 的视图模型无法表示原生 Trino 视图的 owner、`runAsInvoker` 或 SQL path，因此替换已有原生视图时，如果这些属性中有任何非默认值，操作将被拒绝而非静默丢弃。
- `flink` 方言要求至少设置一个以 `flink.` 为前缀的视图属性。Flink 连接器会自动设置 `flink.schema.num-columns`；直接使用 REST API 时，需显式设置至少一个 `flink.*` 属性。
- `spark` 方言要求设置视图属性 `spark.sql.create.version`；否则重新加载时视图会以 `hive` 方言进行往返。

### 视图操作

更多详情请参考[使用 Gravitino 管理视图元数据](./manage-view-metadata-using-gravitino.md)。

## 带有 S3 存储的 Hive Catalog

创建带有 S3 存储的 Hive catalog，可参考[Hive catalog with S3](./hive-catalog-with-cloud-storage.md)文档。Hive catalog 配合 S3 存储使用无需特殊配置。
唯一的区别是文件的存储位置位于 S3。使用 `location` 指定数据库或表的 S3 路径。