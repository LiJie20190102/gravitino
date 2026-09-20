---
slug: /aws-glue-catalog
keywords:
- glue
- aws
- metadata
license: This software is licensed under the Apache License version 2.
---
## 介绍

Apache Gravitino 使用 [AWS Glue Data Catalog](https://aws.amazon.com/glue/) 作为元数据目录。

### 要求

* Glue catalog 需要能够访问 AWS Glue API 的网络权限。
* Gravitino 使用 AWS SDK v2 与 Glue 通信。

:::note
Glue catalog 的 schema 和 table 名称大小写不敏感。AWS Glue 在存储时会将数据库名和表名转换为小写。
:::

## Catalog

### Catalog 能力

Glue catalog 支持在 AWS Glue Data Catalog 中创建、更新和删除数据库和表。

- 默认支持存储在 Glue 中的所有表类型（Hive、Iceberg、Delta、Parquet 等）。
- 支持 Hive 格式表的分区、分桶和排序。
- 不支持视图。Glue 视图（带有 `TableType=VIRTUAL_VIEW` 的表）会被过滤掉。

### Catalog 属性

除了[通用 Catalog 属性](./gravitino-server-config.md#catalog-properties-configuration)外，Glue catalog 还具有以下属性：

| 属性名                    | 描述                                                                                                                                                                                                | 默认值        | 是否必填 | 是否不可变 |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|-----------|
| `aws-region`            | Glue Data Catalog 所在的 AWS 区域（例如 `us-east-1`）。                                                                                                                                            | (无)          | 是       | 是        |
| `aws-glue-catalog-id`   | 拥有 Glue catalog 的 12 位 AWS 账户 ID。如果省略，则默认为调用者的 AWS 账户 ID。                                                                                                                     | (无)          | 否       | 是        |
| `aws-access-key-id`     | 用于静态凭证认证的 AWS 访问密钥 ID。如果省略，则使用默认凭证链。                                                                                                                                   | (无)          | 否       | 否        |
| `aws-secret-access-key` | 与 `aws-access-key-id` 配对的 AWS 秘密访问密钥。如果省略，则使用默认凭证链。                                                                                                                         | (无)          | 否       | 否        |
| `aws-glue-endpoint`     | 用于 VPC 端点或 LocalStack 测试的自定义 Glue 端点 URL（例如 `http://localhost:4566`）。                                                                                                            | (无)          | 否       | 否        |
| `warehouse`             | 当创建表时未指定明确的 `location` 且 Glue 数据库未声明 `LocationUri` 时，作为数据仓库的基础存储路径（例如 `s3://my-bucket/warehouse`）。然后，表位置将派生为 `warehouse/database/table`。                      | (无)          | 是       | 否        |
| `default-table-format`  | 通过 Gravitino 的 `createTable()` API 创建的表的默认格式。接受值：`iceberg`、`hive`。                                                                                                              | `hive`        | 否       | 否        |
| `table-format-filter`   | 由 `listTables()` 和 `loadTable()` 公开的表格式的逗号分隔列表。接受值：`all`、`hive`、`iceberg`、`delta`、`parquet`。用于限制可见的表类型。                                                          | `all`         | 否       | 否        |

:::note
<strong>认证优先级</strong>：静态凭证（`aws-access-key-id` + `aws-secret-access-key`）优先于默认凭证链（环境变量、实例配置文件、容器凭证）。
:::

### Catalog 操作

有关更多详细信息，请参阅[管理 Catalog 和 Schema](./manage-catalogs-and-schemas.md#catalog-operations)。

:::note
敏感 Catalog 属性（如凭证分发密钥）在默认的加载 Catalog 响应中被隐藏。通过 `getSecrets` / `GET .../objects/{type}/{fullName}/secrets` 检索由 secret manager 支持的属性（包括与凭证分发重叠的密钥）。[凭证分发 API](security/credential-vending.md) 仍然可用于类型化凭证交付。
:::

## Schema

### Schema 能力

Glue catalog 支持在 AWS Glue Data Catalog 中创建、更新和删除数据库。

### Schema 属性

除了 `comment` 之外，Glue catalog 未定义其他预定义 schema 属性。其他键值属性将传递到底层 Glue 数据库。

### Schema 操作

参见[管理 Catalog 和 Schema](./manage-catalogs-and-schemas.md#schema-operations)。

## Table

### Table 能力

- Glue catalog 支持在 AWS Glue Data Catalog 中创建、更新和删除表。
- Glue `Table.parameters()` 中的所有条目都将原样传递给 Gravitino，因此下游工具可以正确识别表格式。
- 不支持列默认值。
- 不支持列上的 NOT NULL 约束。
- 不支持表索引。

### Table 分区

Glue catalog 支持[分区表](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-PartitionedTables)。通过指定分区属性在 Glue catalog 中创建分区表。

支持的分区策略取决于表格式：

- **Hive 格式表**：仅支持 `Identity` 分区，因为原生 Glue 分区模型是 Hive 风格的 key=value。
- **Iceberg 格式表**：支持所有 Iceberg 分区转换：`identity`、`year`、`month`、`day`、`hour`、`bucket` 和 `truncate`。

:::caution
在分区属性中指定的 `fieldName` 必须是表中定义的列名。
:::

### Table 排序顺序和分布

Glue catalog 支持[分桶排序表](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-BucketedSortedTables)。通过设置 `distribution` 和 `sortOrders` 属性创建分桶排序表。
尽管 Gravitino 支持多种分布策略，但 AWS Glue 本质上仅支持单一分布策略（按列聚簇）。因此，Glue catalog 仅支持 `Hash` 分布。

:::caution
在 `distribution` 和 `sortOrders` 属性中指定的 `fieldName` 必须是表中定义的列名。
:::

### Table 列类型

Glue catalog 支持 [Hive Language Manual](https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types) 中定义的所有数据类型。
下表列出了从 Glue catalog 映射到 Gravitino 的数据类型。

| Glue 数据类型          | Gravitino 数据类型  |
|-----------------------|---------------------|
| `boolean`             | `boolean`           |
| `tinyint`             | `byte`              |
| `smallint`            | `short`             |
| `int` / `integer`     | `integer`           |
| `bigint`              | `long`              |
| `float`               | `float`             |
| `double`              | `double`            |
| `decimal`             | `decimal`           |
| `string`              | `string`            |
| `char`                | `char`              |
| `varchar`             | `varchar`           |
| `timestamp`           | `timestamp`         |
| `date`                | `date`              |
| `interval_year_month` | `interval_year`     |
| `interval_day_time`   | `interval_day`      |
| `binary`              | `binary`            |
| `array`               | `list`              |
| `map`                 | `map`               |
| `struct`              | `struct`            |
| `uniontype`           | `union`             |

:::info
上述未列出的数据类型映射到 Gravitino **[External Type](./tables-and-views.md#external-type)**，表示来自 Glue catalog 的无法解析的数据类型。
:::

### 表属性

下表列出了 Glue 表的预定义属性。额外的键值属性将直接传递到底层 Glue 数据库。

:::note
<strong>保留</strong>：不能传递到 Gravitino 服务器的字段。

<strong>不可变</strong>：一旦设置便无法修改的字段。
:::

| 属性名称             | 描述                                                                                                                                                                                                          | 默认值                                                       | 必需     | 保留     | 不可变    |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|----------|----------|-----------|
| `location`          | 表的存储位置，例如 `s3://bucket/prefix/test_table`。未指定时，从 Glue 数据库的 `LocationUri` 派生为 `database-location/table`；当数据库未声明位置时，回退为 `warehouse/database/table`。                                                                         | (从数据库位置或 warehouse 派生)                                | 否       | 否       | 否        |
| `format`            | 表文件格式（`parquet`、`orc`、`textfile` 等）。设置后，`input-format`、`output-format` 和 `serde-lib` 将自动派生。主要用于通过 Trino 创建 Hive 格式表。 | (无)                                                         | 否       | 否       | 是        |
| `input-format`      | 表的输入格式类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcInputFormat`。                                                                                                                                     | `org.apache.hadoop.mapred.TextInputFormat`                   | 否       | 否       | 是        |
| `output-format`     | 表的输出格式类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat`。                                                                                                                                   | `org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat` | 否       | 否       | 是        |
| `serde-lib`         | 表的 serde 库类，例如 `org.apache.hadoop.hive.ql.io.orc.OrcSerde`。                                                                                                                                          | `org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe`         | 否       | 否       | 是        |
| `serde-name`        | serde 的名称。                                                                                                                                                                                               | (无)                                                         | 否       | 否       | 否        |
| `serde.parameter.`  | serde 参数的前缀，例如 `"serde.parameter.orc.create.index" = "true"`，指示 ORC serde 库创建行索引。                                                                                                            | (无)                                                         | 否       | 否       | 否        |
| `table-format`      | 存储在 Glue `Table.parameters()` 中的表格式。使用 `ICEBERG` 创建 Iceberg 表。常见值：`ICEBERG`、`HIVE`。                                                                                                      | (无)                                                         | 否       | 否       | 否        |
| `metadata_location` | 存储在 Glue `Table.parameters()` 中的 Iceberg 表元数据文件位置。在 `createTable()` 期间设置时，注册已有的 Iceberg 表而非创建新表。                                                                              | (无)                                                         | 否       | 否       | 否        |
| `comment`           | 用于存储表注释。                                                                                                                                                                                             | (无)                                                         | 否       | 是       | 否        |

:::note
Glue `Table.parameters()` 中的所有条目原封不动地通过 Gravitino 的 API 层。此透传机制确保 `table_type=ICEBERG`、`metadata_location=s3://...`、`spark.sql.sources.provider=delta` 及任何其他格式标识符能够保留在 Gravitino 的元数据代理层中。
:::

### 表操作

有关更多详情，请参阅[使用 Gravitino 管理关系型元数据](./manage-relational-metadata-using-gravitino.md#table-operations)。

#### 修改操作

Gravitino 定义了一套统一的[元数据操作接口](./manage-relational-metadata-using-gravitino.md#alter-a-table)。下表将 Glue 修改操作映射到 Gravitino 表更新请求。

##### 修改表

| Glue 修改操作            | Gravitino 表更新请求            |
|--------------------------|--------------------------------|
| `Alter Table Properties` | `Set a table property`         |
| `Alter Table Comment`    | `Update comment`               |
| `Remove Properties`      | `Remove a table property`      |

:::caution
不支持 Hive 格式表重命名。AWS Glue 不提供原生的表重命名 API；重命名需要重建表。
支持 Iceberg 格式表重命名。
:::

##### 修改列

| Glue 修改操作            | Gravitino 表更新请求               |
|--------------------------|-----------------------------------|
| `Change Column Name`     | `Rename a column`                 |
| `Change Column Type`     | `Update the type of a column`     |
| `Change Column Position` | `Update the position of a column` |
| `Change Column Comment`  | `Update the column comment`       |

##### 修改分区

Glue catalog 通过 `SupportsPartitions` 支持 Hive 格式恒等分区表的分区操作：

- `listPartitions()` / `listPartitionNames()`
- `getPartition(partitionName)`
- `addPartition(partition)`
- `dropPartition(partitionName)`

:::caution
仅支持 `IdentityPartition`，因为 Glue 分区模型采用 Hive 风格的 key=value 格式。
:::

## Iceberg 表

Glue catalog 通过 Apache Iceberg SDK 的 `GlueCatalog` 支持创建和管理 Iceberg 格式表。创建 Iceberg 表时，Gravitino 将 `metadata.json` 文件写入 S3，并以正确的 `metadata_location` 参数在 Glue 中注册该表，使其可被 Trino（Lakehouse connector）、Spark 及其他 Iceberg 原生查询引擎使用。

### 创建 Iceberg 表

在表属性中设置 `table-format=ICEBERG`，或在 catalog 上配置 `default-table-format=iceberg`，使所有表默认为 Iceberg 格式。

`warehouse` catalog 属性是必需的，但仅在没有指定显式 `location` 且 Glue 数据库未声明 `LocationUri` 时作为后备使用。如果没有显式 `location`，当数据库声明了 `LocationUri` 时，表位置派生为 `database-location/table`，否则派生为 `warehouse/database/table`。

### 注册已存在的 Iceberg 表

要注册已存在于 S3 中的 Iceberg 表，在 `createTable()` 时将 `metadata_location` 设置为已有 `metadata.json` 文件的路径。在此模式下，Gravitino 在 Glue 中注册表而不创建新的元数据。

### Iceberg 列类型

Iceberg 表使用 Iceberg 类型系统，与 Hive 类型不同。下表列出了 Iceberg 表支持的 Gravitino 类型及其到 Iceberg 类型的映射关系：

| Gravitino 数据类型       | Iceberg 数据类型      | 说明                                                |
|--------------------------|-----------------------|-----------------------------------------------------|
| `boolean`                | `boolean`             |                                                     |
| `byte`                   | `int`                 | 扩展为 32 位整数                                    |
| `short`                  | `int`                 | 扩展为 32 位整数                                    |
| `integer`                | `int`                 |                                                     |
| `long`                   | `long`                |                                                     |
| `float`                  | `float`               |                                                     |
| `double`                 | `double`              |                                                     |
| `decimal(p, s)`          | `decimal(p, s)`       |                                                     |
| `string`                 | `string`              |                                                     |
| `varchar`                | `string`              | Iceberg 没有可变长度字符类型                        |
| `char`                   | `string`              | Iceberg 没有可变长度字符类型                        |
| `date`                   | `date`                |                                                     |
| `time(6)`                | `time`                | 仅支持微秒精度 (6)                                  |
| `timestamp(6)`           | `timestamp`           | 仅支持微秒精度 (6)                                  |
| `timestamptz(6)`         | `timestamptz`         | 仅支持微秒精度 (6)                                  |
| `binary`                 | `binary`              |                                                     |
| `fixed(n)`               | `binary`              | 映射为可变长度二进制                                |
| `uuid`                   | `uuid`                |                                                     |
| `list`                   | `list`                |                                                     |
| `map`                    | `map`                 |                                                     |
| `struct`                 | `struct`              |                                                     |

### Iceberg 表变更操作

对于 Iceberg 表，支持以下变更操作：

| 操作                           | Gravitino 表更新请求              |
|---------------------------------|-----------------------------------|
| 添加列                          | `Add a column`                    |
| 删除列                          | `Delete a column`                 |
| 重命名列                        | `Rename a column`                 |
| 更新列类型                      | `Update the type of a column`     |
| 更新列注释                      | `Update the column comment`       |
| 更新列可空性                    | `Update column nullability`       |
| 设置表属性                      | `Set a table property`            |
| 删除表属性                      | `Remove a table property`         |

:::caution
Schema 变更和属性变更在两个独立的 Iceberg 事务中提交。如果 schema 提交成功但属性提交失败，表将处于部分变更的状态。
:::

:::caution
通过此 catalog 不支持对 Iceberg 表的嵌套列操作（添加、删除、重命名、类型更新）。
:::

## 安全性

### AWS IAM 权限

Glue catalog 使用的凭证所附加的 IAM 策略必须同时覆盖 Glue 元数据访问和 S3 数据访问：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GlueMetadataAccess",
      "Effect": "Allow",
      "Action": [
        "glue:GetCatalog",
        "glue:GetDatabase", "glue:GetDatabases",
        "glue:CreateDatabase", "glue:UpdateDatabase", "glue:DeleteDatabase",
        "glue:GetTable", "glue:GetTables",
        "glue:CreateTable", "glue:UpdateTable", "glue:DeleteTable",
        "glue:GetPartition", "glue:GetPartitions",
        "glue:CreatePartition", "glue:DeletePartition"
      ],
      "Resource": [
        "arn:aws:glue:<region>:<account-id>:catalog",
        "arn:aws:glue:<region>:<account-id>:database/*",
        "arn:aws:glue:<region>:<account-id>:table/*/*"
      ]
    },
    {
      "Sid": "S3DataAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<warehouse-bucket>",
        "arn:aws:s3:::<warehouse-bucket>/*"
      ]
    }
  ]
}
```