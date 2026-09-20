---
title: "Manage Table Partitions"
slug: "/manage-table-partition-using-gravitino"
keyword: "partition management, partition, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页面涵盖了用于分区的 Gravitino API。关于什么是分区、分区类型，以及
哪些 catalog 支持管理它们，请参见 [Partitions](./partitions.md)。

分区管理适用于 Hive 和 Doris 目录。Iceberg、MySQL 和 PostgreSQL 目录
自行管理分区，不在此处暴露。

## 分区操作

### 添加分区

分区类型必须与表的分区策略相匹配。三种形状如下。

<Tabs groupId="partitions">
<TabItem value="identity" label="身份">

```json
{
  "type": "identity",
  "name": "dt=2026-08-02/country=us",
  "fieldNames": [["dt"], ["country"]],
  "values": [
    {"type": "literal", "dataType": "date", "value": "2026-08-02"},
    {"type": "literal", "dataType": "string", "value": "us"}
  ]
}
```

`values` 必须与 `fieldNames` 的顺序相同。在 Hive 表上，分区名称会被忽略，
因为 Hive 会根据字段名和值推导出它。

</TabItem>
<TabItem value="range" label="Range">

```json
{
  "type": "range",
  "name": "p20260802",
  "upper": {"type": "literal", "dataType": "date", "value": "2026-08-02"},
  "lower": {"type": "literal", "dataType": "date", "value": "2026-08-01"}
}
```

</TabItem>
<TabItem value="list" label="列表">

```json
{
  "type": "list",
  "name": "p_north_america",
  "lists": [
    [{"type": "literal", "dataType": "string", "value": "us"}],
    [{"type": "literal", "dataType": "string", "value": "ca"}]
  ]
}
```

</TabItem>
</Tabs>

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "partitions": [
    {
      "type": "identity",
      "name": "dt=2026-08-02/country=us",
      "fieldNames": [["dt"], ["country"]],
      "values": [
        {"type": "literal", "dataType": "date", "value": "2026-08-02"},
        {"type": "literal", "dataType": "string", "value": "us"}
      ]
    }
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/orders/partitions
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table orders = catalog.asTableCatalog().loadTable(
    NameIdentifier.of("public", "orders"));

Partition partition = Partitions.identity(
    new String[][] {{"dt"}, {"country"}},
    new Literal[] {
        Literals.dateLiteral(LocalDate.of(2026, 8, 2)),
        Literals.stringLiteral("us")
    });

orders.supportPartitions().addPartition(partition);
```

</TabItem>
</Tabs>

### 获取分区

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/orders/partitions/dt=2026-08-02%2Fcountry=us"
```

</TabItem>
<TabItem value="java" label="Java">

```java
Partition partition = orders.supportPartitions().getPartition(
    "dt=2026-08-02/country=us");
```

</TabItem>
</Tabs>

### 列出分区

列表返回名称，或在设置了 `details=true` 时返回完整的分区对象。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/orders/partitions

curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/orders/partitions?details=true"
```

</TabItem>
<TabItem value="java" label="Java">

```java
String[] names = orders.supportPartitions().listPartitionNames();
Partition[] partitions = orders.supportPartitions().listPartitions();
```

</TabItem>
</Tabs>

### 删除分区

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/tables/orders/partitions/dt=2026-08-02%2Fcountry=us"
```

</TabItem>
<TabItem value="java" label="Java">

```java
boolean dropped = orders.supportPartitions().dropPartition(
    "dt=2026-08-02/country=us");

boolean purged = orders.supportPartitions().purgePartition(
    "dt=2026-08-02/country=us");
```

</TabItem>
</Tabs>

删除会移除分区元数据。清除也会移除其数据，并且并非
所有目录都支持。
