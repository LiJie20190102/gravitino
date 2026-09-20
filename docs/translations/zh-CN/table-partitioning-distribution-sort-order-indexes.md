---
title: "Table Structure"
slug: "/table-partitioning-distribution-sort-order-indexes"
date: 2023-12-25
keyword: "Table Partition Bucket Distribute Sort By"
license: "This software is licensed under the Apache License version 2."
last_update:
  date: 2024-02-02
  author: Clearvive
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

Gravitino 中的表具有四个可配置的结构属性，这些属性会影响数据的布局和访问方式：分区、分布、排序和索引。以下各节介绍了每种属性的语法，以及计算引擎在查询时如何使用它们。

## 表分区

要创建分区表，您应该提供以下两个组件来构建一个有效的分区表：

- 分区策略。它定义了 Gravitino 如何在各个分区之间分布表数据。Gravitino 支持以下分区策略。

:::note
下表中的 `score`、`createTime` 和 `city` 指的是表中的字段名。
:::

| 分区策略 | 描述                                                    | JSON 示例                                                                                            | Java 示例                                                                        | 等效 SQL 语义              |
|-----------------------|----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|---------------------------------------|
| `identity`            | 源值，未修改。                                      | `{"strategy":"identity","fieldName":["score"]}`                                                         | `Transforms.identity("score")`                                                      | `PARTITION BY score`                  |
| `hour`                | 提取时间戳的小时，作为距离 '1970-01-01 00:00:00' 的小时数。 | `{"strategy":"hour","fieldName":["createTime"]}`                                                        | `Transforms.hour("createTime")`                                                     | `PARTITION BY hour(createTime)`       |
| `day`                 | 提取日期或时间戳的天，作为距离 '1970-01-01' 的天数。    | `{"strategy":"day","fieldName":["createTime"]}`                                                         | `Transforms.day("createTime")`                                                      | `PARTITION BY day(createTime)`        |
| `month`               | 提取日期或时间戳的月份，作为距离 '1970-01-01' 的月数 | `{"strategy":"month","fieldName":["createTime"]}`                                                       | `Transforms.month("createTime")`                                                    | `PARTITION BY month(createTime)`      |
| `year`                | 提取日期或时间戳的年份，作为距离 1970 的年数。          | `{"strategy":"year","fieldName":["createTime"]}`                                                        | `Transforms.year("createTime")`                                                     | `PARTITION BY year(createTime)`       |
| `bucket[N]`           | 值的哈希，对 N 取模。                                          | `{"strategy":"bucket","numBuckets":10,"fieldNames":[["score"]]}`                                        | `Transforms.bucket(10, "score")`                                                    | `PARTITION BY bucket(10, score)`      |
| `truncate[W]`         | 值截断为宽度 W。                                    | `{"strategy":"truncate","width":20,"fieldName":["score"]}`                                              | `Transforms.truncate(20, "score")`                                                  | `PARTITION BY truncate(20, score)`    |
| `list`                | 按列表值对表进行分区。                           | `{"strategy":"list","fieldNames":[["createTime"],["city"]]}`                                            | `Transforms.list(new String[] {"createTime", "city"})`                              | `PARTITION BY list(createTime, city)` |
| `range`               | 按范围值对表进行分区。                          | `{"strategy":"range","fieldName":["createTime"]}`                                                       | `Transforms.range("createTime")`                                                    | `PARTITION BY range(createTime)`      |
| `function`            | 按函数表达式对表进行分区。                    | `{"strategy":"function","funcName":"toYYYYMM","funcArgs":[{"type":"field","fieldName":["VisitDate"]}]}` | `Transforms.apply("toYYYYMM", new Expression[]{NamedReference.field("VisitDate")})` | `PARTITION BY toYYYYMM(VisitDate)`    |

:::note
对于函数分区，您应提供函数名和函数参数。函数参数必须是一个[表达式](./expression.md)。
:::

- 字段名称：它定义了 Gravitino 使用哪些字段对表进行分区。

- 在某些情况下，您需要其他信息。例如，如果分区策略是 `bucket`，您应该提供桶的数量；如果分区策略是 `truncate`，您应该提供截断宽度。

创建分区表后，您可以[使用 Gravitino 管理其分区](./manage-table-partition-using-gravitino.md)。

## 表分布

要创建分布(分桶)表，您需要使用以下三个组件来构建一个有效的分桶表：

- 策略。它定义了 Gravitino 如何跨分区分布表数据。

| 分发策略 | 描述                                                                                                                     | JSON    | Java             |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------|---------|------------------|
| hash                  | 使用哈希的分布表。Gravitino 根据键的哈希值将表数据分布到桶中。                | `hash`  | `Strategy.HASH`  |
| range                 | 使用范围的分布表。Gravitino 根据指定的值范围或区间将表数据分布到桶中。 | `range` | `Strategy.RANGE` |
| even                  | 将表数据均匀分布到各个分区中。`even` 实现了 Doris 的 `random` 分布。                               | `even`  | `Strategy.EVEN`  |

- number。它定义了用于对表进行分桶的桶数量。
- funcArgs。它定义了策略的参数，该参数必须是一个[表达式](./expression.md)。

<Tabs groupId='language' queryString>
<TabItem value="Json" label="JSON">

```json
{
  "strategy": "hash",
  "number": 4,
  "funcArgs": [
    {
      "type": "field",
      "fieldName": ["score"]
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Distributions.of(Strategy.HASH, 4, NamedReference.field("score"));

// if you want to use auto distribution, you can use the following code, it will set the number is -1.
// Auto distribution with strategy and fields
Distributions.auto(Strategy.HASH, NamedReference.field("score"));
```
</TabItem>

</Tabs>

## 排序顺序

要定义一个排序顺序表，你应该使用以下三个组件来构建一个有效的排序顺序表：

- 方向。它定义了 Gravitino 对表进行排序的方向。默认值为 `ascending`。

| 方向  | 描述                                 | JSON   | Java                       |
|------------|---------------------------------------------|--------|----------------------------|
| 升序  | 按字段或函数升序排序。  | `asc`  | `SortDirection.ASCENDING`  |
| 降序 | 按字段或函数降序排序。 | `desc` | `SortDirection.DESCENDING` |

- 空值排序。它描述了在排序时如何处理空值

| 空值排序类型 | 描述                             | JSON          | Java                       |
|--------------------|-----------------------------------------|---------------|----------------------------|
| null_first         | 将空值放在第一位。 | `nulls_first` | `NullOrdering.NULLS_FIRST` |
| null_last          | 将空值放在最后一位。 | `nulls_last`  | `NullOrdering.NULLS_LAST`  |

注意：如果方向值为 `ascending`，则默认排序值为 `nulls_first`；如果方向值为 `descending`，则默认排序值为 `nulls_last`。

- sortTerm。它表示 Gravitino 用于对表进行排序的字段或函数，必须是一个 [expression](./expression.md)。

<Tabs groupId='language' queryString>
<TabItem value="Json" label="JSON">

```json
 {
  "direction": "asc",
  "nullOrder": "NULLS_LAST",
  "sortTerm":  {
    "type": "field",
    "fieldName": ["score"]
  }
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
SortOrders.of(NamedReference.field("score"), SortDirection.ASCENDING, NullOrdering.NULLS_LAST);
```

</TabItem>
</Tabs>


:::tip
**并非所有目录都支持这些功能**。有关更多详细信息，请参阅相关文档。
:::

以下是创建分区、分桶表和排序表的示例：

<Tabs groupId='language' queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "table",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "nullable": true,
      "comment": "Id of the user"
    },
    {
      "name": "name",
      "type": "varchar(2000)",
      "nullable": true,
      "comment": "Name of the user"
    },
    {
      "name": "age",
      "type": "short",
      "nullable": true,
      "comment": "Age of the user"
    },
    {
      "name": "score",
      "type": "double",
      "nullable": true,
      "comment": "Score of the user"
    }
  ],
  "comment": "Create a new Table",
  "properties": {
    "format": "ORC"
  },
  "partitioning": [
    {
      "strategy": "identity",
      "fieldName": ["score"]
    }
  ],
  "distribution": {
    "strategy": "hash",
    "number": 4,
    "funcArgs": [
      {
        "type": "field",
        "fieldName": ["score"]
      }
    ]
  },
  "sortOrders": [
    {
      "direction": "asc",
      "nullOrder": "NULLS_LAST",
      "sortTerm":  {
        "type": "field",
        "fieldName": ["name"]
      }
    }
  ]
}' http://localhost:8090/api/metalakes/metalake/catalogs/catalog/schemas/schema/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
tableCatalog.createTable(
    NameIdentifier.of("schema", "table"),
    new Column[] {
      Column.of("id", Types.IntegerType.get(), "Id of the user", true, false, null),
      Column.of("name", Types.VarCharType.of(2000), "Name of the user", true, false, null),
      Column.of("age", Types.ShortType.get(), "Age of the user", true, false, null),
      Column.of("score", Types.DoubleType.get(), "Score of the user", false, false, null)
    },
    "Create a new Table",
    tablePropertiesMap,
    new Transform[] {
    // Partition by id
      Transforms.identity("score")
    },
    // CLUSTERED BY id
    Distributions.of(Strategy.HASH, 4, NamedReference.field("id")),
    // SORTED BY name asc
    new SortOrder[] {
      SortOrders.of(
        NamedReference.field("age"), SortDirection.ASCENDING, NullOrdering.NULLS_LAST),
    });
```

</TabItem>
</Tabs>

## 索引

要定义一个索引表，您应该使用以下四个组件来构建一个有效的索引表：

- IndexType. 表示索引的类型，例如主键或唯一键。

| IndexType     | 描述                                                                                                                                                                                                                                                                                            | JSON            | Java                      |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|---------------------------|
| PRIMARY_KEY   | PRIMARY KEY 是用于唯一标识表中每一行的一列或多列。它强制唯一性，并确保指定列中没有两行具有相同的值。此外，PRIMARY KEY 约束会自动在指定列上创建唯一索引。 | `PRIMARY_KEY`   | `IndexType.PRIMARY_KEY`   |
| UNIQUE_KEY    | UNIQUE KEY 约束确保指定列或多列中的所有值在整个表中是唯一的。与 PRIMARY KEY 约束不同，一个表可以有多个 UNIQUE KEY 约束，从而允许在多个列或多列组合中具有唯一值。                  | `UNIQUE_KEY`    | `IndexType.UNIQUE_KEY`    |

- 名称。它定义了索引的名称。

- FieldNames。它定义了 Gravitino 使用哪些表字段来索引表。

- 属性（可选）。额外索引配置属性的映射（例如，ClickHouse 数据跳过索引的 `granularity`）。如果省略，则使用空映射。

<Tabs groupId='language' queryString>
<TabItem value="Json" label="JSON">

```json
 {
  "indexType": "PRIMARY_KEY",
  "name": "PRIMARY",
  "fieldNames": [["col_1"],["col_2"]],
  "properties": {}
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Indexes.of(IndexType.PRIMARY_KEY, "PRIMARY", new String[][]{{"col_1"}, {"col_2"}}, Map.of());
```

</TabItem>
</Tabs>

以下是创建索引表的示例：

<Tabs groupId='language' queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "table",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "nullable": true,
      "comment": "Id of the user"
    },
    {
      "name": "name",
      "type": "varchar(2000)",
      "nullable": true,
      "comment": "Name of the user"
    },
    {
      "name": "age",
      "type": "short",
      "nullable": true,
      "comment": "Age of the user"
    },
    {
      "name": "score",
      "type": "double",
      "nullable": true,
      "comment": "Score of the user"
    }
  ],
  "comment": "Create a new Table",
  "indexes": [
    {
      "indexType": "PRIMARY_KEY",
      "name": "PRIMARY",
      "fieldNames": [["id"]],
      "properties": {}
    },
    {
      "indexType": "UNIQUE_KEY",
      "name": "name_age_score_uk",
      "fieldNames": [["name"],["age"],["score"]],
      "properties": {}
    }
  ]
}' http://localhost:8090/api/metalakes/metalake/catalogs/catalog/schemas/schema/tables
```

</TabItem>
<TabItem value="java" label="Java">

```java
tableCatalog.createTable(
    NameIdentifier.of("schema", "table"),
    new Column[] {
      Column.of("id", Types.IntegerType.get(), "Id of the user", false, true, null),
      Column.of("name", Types.VarCharType.of(1000), "Name of the user", true, false, null),
      Column.of("age", Types.ShortType.get(), "Age of the user", true, false, null),
      Column.of("score", Types.DoubleType.get(), "Score of the user", true, false, null)
    },
    "Create a new Table",
    tablePropertiesMap,
    Transforms.EMPTY_TRANSFORM,
    Distributions.NONE,
    new SortOrder[0],
    new Index[] {
      Indexes.of(IndexType.PRIMARY_KEY, "PRIMARY", new String[][]{{"id"}}, Map.of()),
      Indexes.of(IndexType.UNIQUE_KEY, "name_age_score_uk", new String[][]{{"name"}, {"age"}, {"score"}}, Map.of())
    });
```

</TabItem>
</Tabs>
