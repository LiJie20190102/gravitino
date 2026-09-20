---
slug: /expression
date: 2024-02-02
keyword: expression function field literal reference
license: This software is licensed under the Apache License version 2.
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页介绍 Apache Gravitino 的表达式系统。表达式是元数据定义的重要组成部分，通过表达式，可以为列定义[默认值](./tables-and-views.md#table-column-default-value)、为[函数分区](./table-partitioning-distribution-sort-order-indexes.md#table-partitioning)和[分桶](./table-partitioning-distribution-sort-order-indexes.md#table-distribution)指定函数参数，以及为表中的[排序](./table-partitioning-distribution-sort-order-indexes.md#sort-ordering)指定排序项。
Gravitino 表达式系统将表达式分为三个基本部分：字段引用、字面量和函数。函数表达式可以包含字段引用、字面量及其他函数表达式。

## 字段引用

字段引用是对表中字段的引用。
以下为创建字段引用表达式的示例，演示如何为 `student` 字段创建引用。

<Tabs groupId='language' queryString>
  <TabItem value="Json" label="JSON">

```json
[
  {
    "type": "field",
    "fieldName": [
      "student"
    ]
  }
]
```

  </TabItem>
  <TabItem value="java" label="Java">

```java
NamedReference field = NamedReference.field("student");
```

  </TabItem>
</Tabs>

## 字面量

字面量是常量值。
以下为创建字面量表达式的示例，演示如何创建 `NULL` 字面量以及值为 `1024` 的三种不同数据类型的字面量表达式。

<Tabs groupId='language' queryString>
  <TabItem value="Json" label="JSON">

```json
[
  {
    "type": "literal",
    "dataType": "null",
    "value": "null"
  },
  {
    "type": "literal",
    "dataType": "integer",
    "value": "1024"
  },
  {
    "type": "literal",
    "dataType": "string",
    "value": "1024"
  },
  {
    "type": "literal",
    "dataType": "decimal(10,2)",
    "value": "1024"
  }
]
```

  </TabItem>
  <TabItem value="java" label="Java">

```java
Literal<?>[] literals =
    new Literal[] {
    Literals.NULL,
    Literals.integerLiteral(1024),
    Literals.stringLiteral("1024"),
    Literals.decimalLiteral(Decimal.of("1024", 10, 2))
    };
```

  </TabItem>
</Tabs>

## 函数表达式

函数表达式表示带参数或不带参数的函数调用。参数可以是字段引用、字面量或其他函数表达式。
以下为创建函数表达式的示例，演示如何为 `rand()` 和 `date_trunc('year', birthday)` 创建函数表达式。

<Tabs groupId='language' queryString>
  <TabItem value="Json" label="JSON">

```json
[
  {
    "type": "function",
    "funcName": "rand",
    "funcArgs": []
  },
  {
    "type": "function",
    "funcName": "date_trunc",
    "funcArgs": [
      {
        "type": "literal",
        "dataType": "string",
        "value": "year"
      },
      {
        "type": "field",
        "fieldName": [
          "birthday"
        ]
      }
    ]
  }
]
```

  </TabItem>
  <TabItem value="java" label="Java">

```java
FunctionExpression[] functionExpressions =
        new FunctionExpression[] {
          FunctionExpression.of("rand"),
          FunctionExpression.of("date_trunc", Literals.stringLiteral("year"), NamedReference.field("birthday"))
        };
```

  </TabItem>
</Tabs>

## 未解析表达式

未解析表达式是一种特殊类型的表达式，专门用于在列的默认值无法解析时呈现该默认值。
以下展示未解析表达式在 JSON 和 Java 中的数据结构，便于获取其值。

<Tabs groupId='language' queryString>
  <TabItem value="Json" label="JSON">

```json
{
  "type": "unparsed",
  "unparsedExpression": "(curdate() + interval 1 year)"
}
```

  </TabItem>
  <TabItem value="java" label="Java">

```java
// 以下表达式的结果是一个字符串 "(curdate() + interval 1 year)"
String unparsedValue = ((UnparsedExpression) expressino).unparsedExpression();
```

  </TabItem>
</Tabs>