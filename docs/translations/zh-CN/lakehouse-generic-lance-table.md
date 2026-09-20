---
slug: /lance-table-support
keywords:
- lakehouse
- lance
- metadata
- generic catalog
license: This software is licensed under the Apache License version 2.
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


## 概述

本文档介绍如何使用 Apache Gravitino 通过 Lance 作为底层表格式来管理通用湖仓目录。


## 表管理

### 支持的操作

对于通用湖仓目录中的 Lance 表，下表总结了支持的操作：

| 操作 | 支持状态  |
|-----------|-----------------|
| 列出      | ✅ 完全支持          |
| 加载      | ✅ 完全支持          |
| 修改     | 目前不支持 |
| 创建    | ✅ 完全支持          |
| 注册  | ✅ 完全支持          |
| 删除      | ✅ 完全支持          |
| 清除     | ✅ 完全支持          |

:::note 功能限制
- **分区：** 不支持
- **排序顺序：** 不支持
- **分布：** 不支持
- **索引：** 不支持
:::

### 数据类型映射

Lance 使用 Apache Arrow 作为表模式。下表显示了 Gravitino 与 Arrow 之间的类型映射：

| Gravitino 类型                   | Arrow 类型                              |
|----------------------------------|-----------------------------------------|
| `Struct`                         | `Struct`                                |
| `Map`                            | Lance 不支持                  |
| `List`                           | `Array`                                 |
| `Boolean`                        | `Boolean`                               |
| `Byte`                           | `Int8`                                  |
| `Short`                          | `Int16`                                 |
| `Integer`                        | `Int32`                                 |
| `Long`                           | `Int64`                                 |
| `Float`                          | `Float`                                 |
| `Double`                         | `Double`                                |
| `String`                         | `Utf8`                                  |
| `Binary`                         | `Binary`                                |
| `Decimal(p, s)`                  | `Decimal(p, s)`（128 位）               |
| `Date`                           | `Date`                                  |
| `Timestamp`/`Timestamp(6)`       | `TimestampType withoutZone`             |
| `Timestamp(0)`                   | `TimestampType Second withoutZone`      |
| `Timestamp(3)`                   | `TimestampType Millisecond withoutZone` |
| `Timestamp(9)`                   | `TimestampType Nanosecond withoutZone`  |
| `Timestamp_tz`/`Timestamp_tz(6)` | `TimestampType Microsecond withUtc`     |
| `Timestamp_tz(0)`                | `TimestampType Second withUtc`          |
| `Timestamp_tz(3)`                | `TimestampType Millisecond withUtc`     |
| `Timestamp_tz(9)`                | `TimestampType Nanosecond withUtc`      |
| `Time`/`Time(9)`                 | `Time Nanosecond`                       |
| `Null`                           | `Null`                                  |
| `Fixed(n)`                       | `Fixed-Size Binary(n)`                  |
| `Interval_year`                  | Lance 不支持                  |
| `Interval_day`                   | `Duration(Microsecond)`                 |
| `External(arrow_field_json_str)` | 任意 Arrow 字段                         |

### 外部类型

对于 Gravitino 中未原生映射的 Arrow 类型，请使用 `External(arrow_field_json_str)` 类型，它接受 Arrow `Field` 的 JSON 字符串表示。

**要求：**
- JSON 必须符合 Apache Arrow [Field 规范](https://github.com/apache/arrow-java/blob/ed81e5981a2bee40584b3a411ed755cb4cc5b91f/vector/src/main/java/org/apache/arrow/vector/types/pojo/Field.java#L80C1-L86C68)
- `name` 属性必须与列名完全匹配
- `nullable` 属性必须与列的可空性匹配
- `children` 数组：
  - 对于原始类型为空
  - 对于复杂类型（Struct、List）包含子字段定义

**示例：**

| Arrow 类型        | 外部类型定义                                                                                                                                                                                                                            |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Large Utf8`      | `External("{\"name\":\"col_name\",\"nullable\":true,\"type\":{\"name\":\"largeutf8\"},\"children\":[]}")`                                                                                                                                           |
| `Large Binary`    | `External("{\"name\":\"col_name\",\"nullable\":true,\"type\":{\"name\":\"largebinary\"},\"children\":[]}")`                                                                                                                                         |
| `Large List`      | `External("{\"name\":\"col_name\",\"nullable\":true,\"type\":{\"name\":\"largelist\"},\"children\":[{\"name\":\"element\",\"nullable\":true,\"type\":{\"name\":\"int\",\"bitWidth\":32,\"isSigned\":true},\"children\":[]}]}")`                     |
| `Fixed-Size List` | `External("{\"name\":\"col_name\",\"nullable\":true,\"type\":{\"name\":\"fixedsizelist\",\"listSize\":10},\"children\":[{\"name\":\"element\",\"nullable\":true,\"type\":{\"name\":\"int\",\"bitWidth\":32,\"isSigned\":true},\"children\":[]}]}")` |

### 表属性

通用湖仓目录中表的必需和可选属性：

| 属性              | 描述                                                                                                                                                                                                                                                                                                                              | 默认值  | 是否必需     |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|--------------|
| `format`              | 表格式：`lance`，仅完全支持 `lance`。                                                                                                                                                                                                                                                                                  | （无）   | 是          |
| `location`            | 表元数据和数据的存储路径，Lance 支持：S3、GCS、OSS、AZ、File、Memory 和 file-object-store。                                                                                                                                                                                                                          | （无）   | 有条件* |
| `external`            | 数据目录是否为外部位置。如果为 `true`，删除表只会移除 Gravitino 中的元数据，不会删除数据目录，而清除表会删除两者。对于非外部表，删除会同时删除两者。                                                                                 | false    | 否           |
| `lance.creation-mode` | 创建模式：对于创建表，它可以是 `CREATE`、`EXIST_OK` 或 `OVERWRITE`。对于注册表，它应为 `CREATE` 或 `OVERWRITE`                                                                                                                                                                                            | `CREATE` | 否           |
| `lance.register`      | 是否为注册表操作。如果为 `true`，此 API 实际上不会创建数据目录，创建和管理数据目录是用户的责任。如果为 `false`，它会实际创建表。                                                                                                          | false    | 否           |
| `lance.storage.xxxx`  | Lance 格式所需的任何额外存储特定属性（例如，S3 凭证、HDFS 配置）。将 `xxxx` 替换为实际属性名。例如，我们可以在使用 S3 位置时使用 `lance.storage.aws_access_key_id` 设置 S3 aws_access_key_id，详情请参阅 https://lancedb.com/docs/storage/integrations/ | （无）   | 否           |

- `CREATE`：创建新表，如果表已存在则失败。
- `EXIST_OK`：如果表不存在则创建新表，否则不执行任何操作。
- `OVERWRITE`：创建新表，如果表已存在则覆盖；如果表不是注册表，它会先删除现有数据目录，然后创建新表。

### 格式边界

通用目录对其通用表 API 与格式无关，但 Lance 表操作必须
目标实体的 `format` 属性为 `lance`（不区分大小写）。Lance REST 直接
操作（如 describe、drop、deregister 和 alter）会拒绝已知的非 Lance 实体，并返回
HTTP `400 INVALID_INPUT`；`tableExists` 将其呈现为不存在。这些检查保留现有
元数据和位置。

对于分派到 Lance 表委托器的创建请求，现有的非 Lance 实体仍然
是 `CREATE` (`409`) 的普通名称冲突。`EXIST_OK`、创建 `OVERWRITE` 和注册
`OVERWRITE` 会被直接 Gravitino API 以 `IllegalArgumentException` 拒绝，该异常
由 Lance REST 服务返回为 HTTP `400`。特别是，覆盖验证发生在
元数据移除或 Lance 数据集删除之前。通用目录 `ListTables` 行为
不变；它继续列出所有格式。特定格式的列出是一个单独的后续
事项。

**位置要求：** 必须在目录、模式或表级别指定。请参阅[位置解析](./lakehouse-generic-catalog.md#key-property-location)。

同时设置特定于你的湖仓格式或自定义要求的其他属性。

### 模式刷新

对于 Lance 表，Gravitino 将表列存储在其元数据存储中。某些 Lance 写入器也可以
在 Lance 位置直接更新数据集。为了使 Gravitino 元数据保持同步，通用
湖仓目录支持目录级模式刷新模式：

| 模式                 | 行为                                                                                                                                                                                                                                                                         |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `DECLARED_AND_EMPTY` | 默认。在两种情况下从 Lance 数据集刷新模式：(1) 已声明表（`lance.declared=true`）的模式尚未写入 Gravitino；(2) Gravitino 列列表为空的表，例如在其模式被捕获之前注册的表。 |
| `VERSION_CHECK`      | 在每次 `loadTable` 时打开 Lance 数据集，将数据集版本与 `lance.version` 比较，并在版本发生变化时刷新列。 |

仅当表可能通过 Lance 路径在 Gravitino 外部直接修改时，才使用 `VERSION_CHECK`
。它会为每次 `loadTable` 调用添加数据集版本检查。

:::note 零列 Lance 数据集
如果 Lance 数据集确实没有列，`DECLARED_AND_EMPTY` 模式会记录所检查的数据集
版本（`lance.version`）在第一次 `loadTable` 调用时。后续加载会跳过打开数据集
只要存储的版本未更改。在记录新版本之前，Lance 表
修改会重新检查空的存储模式，如果无法加载则中止，因此不完整的列
元数据不会与最新数据集版本关联。
:::

### 表操作

表操作遵循标准关系目录模式。请参阅[表操作](./manage-relational-metadata-using-gravitino.md#table-operations)获取完整文档。

以下部分提供使用 Lance 表的示例和重要细节。

#### 创建 Lance 表

<Tabs groupId='language' queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "lance_table",
  "comment": "Example Lance table",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "comment": "Primary identifier",
      "nullable": false
    }
  ],
  "properties": {
    "format": "lance",
    "location": "/tmp/lance_catalog/schema/lance_table"
  }
}' http://localhost:8090/api/metalakes/test/catalogs/generic_lakehouse_lance_catalog/schemas/schema/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("generic_lakehouse_lance_catalog");
TableCatalog tableCatalog = catalog.asTableCatalog();

Map<String, String> tableProperties = ImmutableMap.<String, String>builder()
    .put("format", "lance")
    .put("location", "/tmp/lance_catalog/schema/example_table")
    .build();

tableCatalog.createTable(
    NameIdentifier.of("schema", "lance_table"),
    new Column[] {
        Column.of("id", Types.IntegerType.get(), "Primary identifier", 
                  true, false, null)
    },
    "Example Lance table",
    tableProperties,
    null,  // 分区
    null,  // 分布
    null,  // 排序顺序
    null   // 索引
);
```

</TabItem>
</Tabs>

#### 注册外部表

注册现有 Lance 表，而无需移动或复制数据：

<Tabs groupId='language' queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "register_lance_table",
  "comment": "Registered existing Lance table",
  "columns": [],
  "properties": {
    "format": "lance",
    "lance.register": "true",
    "location": "/tmp/lance_catalog/schema/existing_lance_table"
  }
}' http://localhost:8090/api/metalakes/test/catalogs/generic_lakehouse_lance_catalog/schemas/schema/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("generic_lakehouse_lance_catalog");
TableCatalog tableCatalog = catalog.asTableCatalog();

Map<String, String> registerProperties = ImmutableMap.<String, String>builder()
    .put("format", "lance")
    .put("lance.register", "true")
    .put("location", "/tmp/lance_catalog/schema/existing_lance_table")
    .build();

tableCatalog.createTable(
    NameIdentifier.of("schema", "register_lance_table"),
    new Column[] {},  // 架构已从现有表自动检测
    "Registered existing Lance table",
    registerProperties,
    null, null, null, null
);
```

</TabItem>
</Tabs>

:::tip 注册与创建
- <strong>注册</strong>（`lance.register: true`）：
  - 链接到现有 Lance 数据集或路径占位符
  - 从 Lance 元数据自动检测模式
  - 用于导入现有数据集

- <strong>创建</strong>（默认）：
  - 从零开始创建新的 Lance 表
  - 需要列模式定义
  - 初始化新的 Lance 数据集文件
:::

## 高级主题

### 故障排查

#### 常见问题

**问题："未指定位置"错误**
```
Solution: Ensure at least one level (catalog/schema/table) specifies the location property
```

**问题：权限被拒绝错误**
```
Solution: Check file system permissions and credentials for the storage backend
```

**问题：注册后找不到表**
```
Solution: Verify the location path points to a valid Lance dataset directory
```

### 迁移指南

#### 迁移现有 Lance 表

1. <strong>清点</strong>：列出所有现有 Lance 表位置
2. <strong>创建目录</strong>：创建指向根位置的通用湖仓目录
3. <strong>注册表</strong>：为每个表使用注册操作
4. <strong>验证</strong>：确认所有表都可通过 Gravitino 访问
5. <strong>更新客户端</strong>：让应用程序指向 Gravitino 元数据，而不是直接访问 Lance

**示例迁移脚本：**

```shell
# 要注册的现有 Lance 表列表
tables_to_migrate=(
    "sales orders /data/sales/orders"
    "sales customers /data/sales/customers"
    "inventory products /data/inventory/products"
)

# 注册每个表
for entry in "${tables_to_migrate[@]}"; do
    read -r schema table location <<< "$entry"
    echo ${schema}
    echo ${table}

    curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
      -H "Content-Type: application/json" -d "{
      \"name\": \"${table}\",
      \"comment\": \"Registered existing Lance table\",
      \"columns\": [],
      \"properties\": {
        \"format\": \"lance\",
        \"lance.register\": \"true\",
        \"location\": \"${location}\"
      }
    }" http://localhost:8090/api/metalakes/test/catalogs/generic_lakehouse_lance_catalog/schemas/$schema/tables

    echo "Registered ${schema}.${table}"
done
```

其他表操作（load、alter、drop、truncate）遵循标准关系目录模式。请参阅[表操作](./manage-relational-metadata-using-gravitino.md#table-operations)了解详情。

### 使用 MinIO 的 Lance 表

要使用存储在 MinIO 中的 Lance 表配合 Gravitino，请在 Lance 目录上一次性配置 MinIO 存储后端。然后 Gravitino 会将这些存储选项返回给 Lance 客户端，Spark 无需重复配置它们。

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "lance_catalog",
  "type": "RELATIONAL",
  "provider": "lakehouse-generic",
  "comment": "catalog for Lance tables on MinIO",
  "properties": {
    "location": "s3://bucket1/lance",
    "lance.storage.endpoint": "http://minio:9000",
    "lance.storage.access_key_id": "ak",
    "lance.storage.secret_access_key": "sk",
    "lance.storage.allow_http": "true",
    "lance.storage.region": "us-east-1"
  }
}' http://localhost:8090/api/metalakes/test/catalogs

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "lance_orders",
  "comment": "Order table stored in MinIO",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "comment": "Primary identifier",
      "nullable": false
    }
  ],
  "properties": {
    "format": "lance",
    "location": "s3://bucket1/lance_orders"
  }
}' http://localhost:8090/api/metalakes/test/catalogs/lance_catalog/schemas/sales/tables

```

如果你需要在单个表上覆盖存储，仍然支持 `lance.storage.*` 表属性。