---
title: "Manage Relational Metadata"
slug: "/manage-relational-metadata-using-gravitino"
keyword: "table management, table, column, relational metadata, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页面介绍了表的 Gravitino API。关于表是什么、列和属性如何工作，
drop 与 purge 的区别，以及如何在 UI 中操作表，请参见[表和
视图](./tables-and-views.md)。要创建表所在的 catalog 和 schema，请参见[管理
Catalog 和 Schema](./manage-catalogs-and-schemas.md)。视图有其专属页面，[管理视图
元数据](./manage-view-metadata-using-gravitino.md)。

以下示例使用 Hive catalog。列类型、表属性和支持的操作因
提供者而异，每种 catalog 类型都有其各自的文档：[Apache Hive](./apache-hive-catalog.md)、
[MySQL](./jdbc-mysql-catalog.md)、[PostgreSQL](./jdbc-postgresql-catalog.md)、[Apache
Doris](./jdbc-doris-catalog.md)、[StarRocks](./jdbc-starrocks-catalog.md)、
[OceanBase](./jdbc-oceanbase-catalog.md)、[Hologres](./jdbc-hologres-catalog.md)、
[ClickHouse](./jdbc-clickhouse-catalog.md)、[Apache Iceberg](./lakehouse-iceberg-catalog.md)、
[Apache Paimon](./lakehouse-paimon-catalog.md)、[Apache Hudi](./lakehouse-hudi-catalog.md)，以及
[Lakehouse generic](./lakehouse-generic-catalog.md)。

## 表操作

### 创建表格

表需要一个名称及其列。分区、分布、排序顺序、索引以及
属性都是可选的，并且 catalog 接受其中的哪些取决于 provider。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "customers",
  "comment": "Customer records",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "comment": "Primary key",
      "nullable": false,
      "autoIncrement": true
    },
    {
      "name": "name",
      "type": "varchar(500)",
      "comment": "Customer name",
      "nullable": true
    },
    {
      "name": "created_at",
      "type": "timestamp",
      "nullable": false,
      "defaultValue": {
        "type": "function",
        "funcName": "current_timestamp",
        "funcArgs": []
      }
    }
  ],
  "properties": {"format": "ORC"}
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("sales");

Column[] columns = new Column[] {
    Column.of("id", Types.IntegerType.get(), "Primary key", false, true, null),
    Column.of("name", Types.VarCharType.of(500), "Customer name"),
    Column.of("created_at", Types.TimestampType.withoutTimeZone(), null, false, false,
        FunctionExpression.of("current_timestamp"))
};

Table table = catalog.asTableCatalog().createTable(
    NameIdentifier.of("public", "customers"),
    columns,
    "Customer records",
    ImmutableMap.of("format", "ORC"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog = client.load_catalog("sales")

columns = [
    Column.of("id", Types.IntegerType.get(), "Primary key", False, True, None),
    Column.of("name", Types.VarCharType.of(500), "Customer name"),
    Column.of("created_at", Types.TimestampType.without_time_zone(), None, False),
]

table = catalog.as_table_catalog().create_table(
    ident=NameIdentifier.of("public", "customers"),
    columns=columns,
    comment="Customer records",
    properties={"format": "ORC"})
```

</TabItem>
</Tabs>

有关分区、分布、排序顺序和索引，请参阅[表分区、分布、排序
顺序和索引](./table-partitioning-distribution-sort-order-indexes.md)。

### 加载表

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/customers
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table table = catalog.asTableCatalog().loadTable(
    NameIdentifier.of("public", "customers"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
table = catalog.as_table_catalog().load_table(
    NameIdentifier.of("public", "customers"))
```

</TabItem>
</Tabs>

### 修改表

更改在一个请求中以列表形式应用，并涵盖表本身、其属性以及其
列。

| 更改                        | JSON                                                                                            | Java                                          |
|-------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 重命名表              | `{"@type":"rename","newName":"table_renamed"}`                                                  | `TableChange.rename(...)`                     |
| 移动到另一个模式        | `{"@type":"rename","newName":"table_renamed","newSchemaName":"new_schema"}`                     | `TableChange.rename(...)`                     |
| 更新注释            | `{"@type":"updateComment","newComment":"new_comment"}`                                          | `TableChange.updateComment(...)`              |
| 设置属性                | `{"@type":"setProperty","property":"key1","value":"value1"}`                                    | `TableChange.setProperty(...)`                |
| 移除属性             | `{"@type":"removeProperty","property":"key1"}`                                                  | `TableChange.removeProperty(...)`             |
| 添加列                  | `{"@type":"addColumn","fieldName":["position"],"type":"varchar(20)","position":"FIRST"}`        | `TableChange.addColumn(...)`                  |
| 删除列               | `{"@type":"deleteColumn","fieldName":["name"],"ifExists":true}`                                 | `TableChange.deleteColumn(...)`               |
| 重命名列               | `{"@type":"renameColumn","oldFieldName":["name_old"],"newFieldName":"name_new"}`                | `TableChange.renameColumn(...)`               |
| 更新列注释       | `{"@type":"updateColumnComment","fieldName":["name"],"newComment":"new comment"}`               | `TableChange.updateColumnComment(...)`        |
| 更新列类型          | `{"@type":"updateColumnType","fieldName":["name"],"newType":"varchar(100)"}`                    | `TableChange.updateColumnType(...)`           |
| 更新列的可空性 | `{"@type":"updateColumnNullability","fieldName":["name"],"nullable":true}`                      | `TableChange.updateColumnNullability(...)`    |
| 更新列位置      | `{"@type":"updateColumnPosition","fieldName":["name"],"newPosition":"default"}`                 | `TableChange.updateColumnPosition(...)`       |
| 更新列默认值 | `{"@type":"updateColumnDefaultValue","fieldName":["name"],"newDefaultValue":{...}}`             | `TableChange.updateColumnDefaultValue(...)`   |

并非每个提供商都接受每一项更改。如果不接受，请求会被拒绝，而不是
被静默忽略。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "updateComment", "newComment": "Customer records, curated"},
    {"@type": "addColumn", "fieldName": ["email"], "type": "varchar(320)", "nullable": true}
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/customers
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table table = catalog.asTableCatalog().alterTable(
    NameIdentifier.of("public", "customers"),
    TableChange.updateComment("Customer records, curated"),
    TableChange.addColumn(new String[] {"email"}, Types.VarCharType.of(320)));
```

</TabItem>
<TabItem value="python" label="Python">

```python
table = catalog.as_table_catalog().alter_table(
    NameIdentifier.of("public", "customers"),
    TableChange.update_comment("Customer records, curated"),
    TableChange.add_column(["email"], Types.VarCharType.of(320)))
```

</TabItem>
</Tabs>

### 删除或清除表

删除会移除元数据，对于托管表也会移除底层目录。对于
外部表则仅移除元数据。清除会彻底移除数据并跳过回收站，该操作
在外部表上会被拒绝，并且并非所有 catalog 都支持。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/customers?purge=false"
```

</TabItem>
<TabItem value="java" label="Java">

```java
boolean dropped = catalog.asTableCatalog().dropTable(
    NameIdentifier.of("public", "customers"));

boolean purged = catalog.asTableCatalog().purgeTable(
    NameIdentifier.of("public", "customers"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
dropped = catalog.as_table_catalog().drop_table(
    NameIdentifier.of("public", "customers"))

purged = catalog.as_table_catalog().purge_table(
    NameIdentifier.of("public", "customers"))
```

</TabItem>
</Tabs>

### 列出表

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
NameIdentifier[] identifiers = catalog.asTableCatalog().listTables(
    Namespace.of("public"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
identifiers = catalog.as_table_catalog().list_tables(Namespace.of("public"))
```

</TabItem>
</Tabs>
