---
title: "Manage View Metadata"
slug: "/manage-view-metadata-using-gravitino"
keyword: "view management, view, SQL view, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页面介绍了视图的 Gravitino API。有关什么是视图、哪些目录支持它们，以及
它们与表的关系，请参见[表和视图](./tables-and-views.md)。有关创建目录
和视图所在的模式，请参见[管理目录和模式](./manage-catalogs-and-schemas.md)。

视图由 Hive、Iceberg 和 Paimon 目录支持。

## 视图操作

### 创建视图

视图包含其列以及一个或多个表示，每个表示持有一个查询及其
所使用的方言。SQL 是目前唯一的表示类型。可以设置默认的 catalog 和 schema，以便
查询中的非限定名称得以解析。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "active_customers",
  "comment": "Customers with orders in the last year",
  "query": "SELECT * FROM customers WHERE last_order_at > current_date - interval 365 day",
  "dialect": "spark",
  "columns": [
    {"name": "id", "type": "integer", "nullable": false},
    {"name": "name", "type": "varchar(500)", "nullable": true}
  ],
  "properties": {}
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/views
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("sales");
ViewCatalog views = catalog.asViewCatalog();

Column[] columns = new Column[] {
    Column.of("id", Types.IntegerType.get(), null, false, false, null),
    Column.of("name", Types.VarCharType.of(500))
};

Representation[] representations = new Representation[] {
    SQLRepresentation.builder()
        .withDialect("spark")
        .withSql("SELECT * FROM customers "
            + "WHERE last_order_at > current_date - interval 365 day")
        .build()
};

View view = views.createView(
    NameIdentifier.of("public", "active_customers"),
    "Customers with orders in the last year",
    columns,
    representations,
    "sales",
    "public",
    ImmutableMap.of());
```

</TabItem>
</Tabs>

Gravitino 存储定义但不执行它，因此查询是否能解析是一个问题
对于读取视图的引擎来说。

### 加载视图

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/views/active_customers
```

</TabItem>
<TabItem value="java" label="Java">

```java
View view = views.loadView(NameIdentifier.of("public", "active_customers"));
```

</TabItem>
</Tabs>

### 修改视图

| 更改             | JSON                                                         | Java                                       |
|--------------------|--------------------------------------------------------------|--------------------------------------------|
| Rename             | `{"@type":"rename","newName":"view_renamed"}`                | `ViewChange.rename("view_renamed")`        |
| Update the comment | `{"@type":"updateComment","newComment":"new_comment"}`       | `ViewChange.updateComment("new_comment")`  |
| Set a property     | `{"@type":"setProperty","property":"key1","value":"value1"}` | `ViewChange.setProperty("key1", "value1")` |
| Remove a property  | `{"@type":"removeProperty","property":"key1"}`               | `ViewChange.removeProperty("key1")`        |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "updateComment", "newComment": "Customers active in the last year"}
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/views/active_customers
```

</TabItem>
<TabItem value="java" label="Java">

```java
View view = views.alterView(
    NameIdentifier.of("public", "active_customers"),
    ViewChange.updateComment("Customers active in the last year"));
```

</TabItem>
</Tabs>

### 删除视图

删除视图会移除其定义。它所读取的表不受影响。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/views/active_customers
```

</TabItem>
<TabItem value="java" label="Java">

```java
boolean dropped = views.dropView(NameIdentifier.of("public", "active_customers"));
```

</TabItem>
</Tabs>

### 列表视图

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/views
```

</TabItem>
<TabItem value="java" label="Java">

```java
NameIdentifier[] identifiers = views.listViews(Namespace.of("public"));
```

</TabItem>
</Tabs>
