---
title: "Tables and Views"
slug: "/tables-and-views"
keyword: "table, view, column, relational metadata, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

表是关系目录持有的对象，而视图是对一个或多个
表的存储查询。两者都存在于模式中，并且无论由哪个系统存储，访问它们的方式都是相同的。

Gravitino 不保留任何一方的副本。通过 Hive、Iceberg、MySQL 或
Paimon catalog 注册的表保留在该系统中，而 Gravitino 保留引用以及附加在其上的任何内容。
通过 Gravitino 创建表会在源系统中创建它，列出表会向
请求时的源系统进行查询，因此直接在 Hive 中创建的表会在下次 Gravitino 被
询问时出现。

Gravitino 所增加的是跨越所有这些系统的统一形态。相同的调用描述了 Hive 表和
Iceberg 表，列承载相同的类型系统，并且标签、策略、所有权和统计信息
无论底层系统是什么，都以相同的方式附加。

## 快速开始

**1. 打开一个 catalog。** 表存在于关系型 catalog 内的 schema 中。参见
[Catalogs and Schemas](./catalogs-and-schemas.md) 了解如何连接一个。

**2. 浏览或创建。** 已连接的目录会显示其中已有的表。创建表
通过 Gravitino 会在源系统中创建它，并带有列、分区和属性
您指定的。

**3. 对重要内容进行分类。** 表及其列都带有标签和策略，这就是一次
分类设置如何到达读取 Gravitino 的每个引擎。

## 表格模型

### 列

列具有名称和类型，并且可以带有注释、可空性、自增标志以及一个
默认值。类型是 Gravitino 类型，而不是任何一个系统的类型，因此相同的定义适用
跨目录，并且每个提供者将它们映射到自己的类型。

如果提供程序无法表示某种类型，提供程序自己的页面会说明这一点。类型映射是最
常见的两个不同提供程序的目录产生差异的地方。

#### 表列类型

Gravitino 支持以下列类型。一个目录可能仅支持其中的一个子集；请参阅
提供商的页面以了解其类型映射。

| 类型                      | Java                                                                    | JSON                                                                                                                               |
|---------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| 布尔型                   | `Types.BooleanType.get()`                                               | `"boolean"`                                                                                                                        |
| 字节型                      | `Types.ByteType.get()`                                                  | `"byte"`                                                                                                                           |
| 无符号字节型             | `Types.ByteType.unsigned()`                                             | `"byte unsigned"`                                                                                                                  |
| 短整型                     | `Types.ShortType.get()`                                                 | `"short"`                                                                                                                          |
| 无符号短整型            | `Types.ShortType.unsigned()`                                            | `"short unsigned"`                                                                                                                 |
| 整型                   | `Types.IntegerType.get()`                                               | `"integer"`                                                                                                                        |
| 无符号整型          | `Types.IntegerType.unsigned()`                                          | `"integer unsigned"`                                                                                                               |
| 长整型                      | `Types.LongType.get()`                                                  | `"long"`                                                                                                                           |
| 无符号长整型             | `Types.LongType.unsigned()`                                             | `"long unsigned"`                                                                                                                  |
| 浮点型                     | `Types.FloatType.get()`                                                 | `"float"`                                                                                                                          |
| 双精度浮点型                    | `Types.DoubleType.get()`                                                | `"double"`                                                                                                                         |
| Decimal(precision, scale) | `Types.DecimalType.of(precision, scale)`                                | `"decimal(p,s)"`                                                                                                                   |
| 字符串                    | `Types.StringType.get()`                                                | `"string"`                                                                                                                         |
| FixedChar(length)         | `Types.FixedCharType.of(length)`                                        | `"char(l)"`                                                                                                                        |
| VarChar(length)           | `Types.VarCharType.of(length)`                                          | `"varchar(l)"`                                                                                                                     |
| 时间戳                 | `Types.TimestampType.withoutTimeZone()`                                 | `"timestamp"`                                                                                                                      |
| 时间戳(p)              | `Types.TimestampType.withoutTimeZone(p)`                                | `"timestamp(p)"`                                                                                                                   |
| 带时区时间戳     | `Types.TimestampType.withTimeZone()`                                    | `"timestamp_tz"`                                                                                                                   |
| 带时区时间戳(p)  | `Types.TimestampType.withTimeZone(p)`                                   | `"timestamp_tz(p)"`                                                                                                                |
| 日期                      | `Types.DateType.get()`                                                  | `"date"`                                                                                                                           |
| 时间                      | `Types.TimeType.get()`                                                  | `"time"`                                                                                                                           |
| 时间(p)                   | `Types.TimeType.of(p)`                                                  | `"time(p)"`                                                                                                                        |
| 年月间隔       | `Types.IntervalYearType.get()`                                          | `"interval_year"`                                                                                                                  |
| 日时间隔         | `Types.IntervalDayType.get()`                                           | `"interval_day"`                                                                                                                   |
| Fixed(length)             | `Types.FixedType.of(length)`                                            | `"fixed(l)"`                                                                                                                       |
| 二进制                    | `Types.BinaryType.get()`                                                | `"binary"`                                                                                                                         |
| 列表                      | `Types.ListType.of(Types.IntegerType.get(), true)`                       | `{"type":"list","containsNull":true,"elementType":"integer"}`                                                                |
| 映射                       | `Types.MapType.of(Types.StringType.get(), Types.IntegerType.get(), true)` | `{"type":"map","keyType":"string","valueType":"integer","valueContainsNull":true}`                                       |
| 结构体                    | `Types.StructType.of(Types.StructType.Field.of("id", Types.IntegerType.get(), false, null))` | `{"type":"struct","fields":[{"name":"id","type":"integer","nullable":false}]}`                            |
| 联合                     | `Types.UnionType.of(Types.IntegerType.get(), Types.StringType.get())`    | `{"type":"union","types":["integer","string"]}`                                                                              |
| UUID                      | `Types.UUIDType.get()`                                                  | `"uuid"`                                                                                                                           |
| 变体                   | `Types.VariantType.get()`                                               | `"variant"`                                                                                                                        |
| 空                      | `Types.NullType.get()`                                                  | `"null"`                                                                                                                           |
| 几何                  | `Types.GeometryType.crs84()`                                            | `"geometry"`                                                                                                                       |
| 地理                 | `Types.GeographyType.crs84()`                                           | `"geography"`                                                                                                                      |

Decimal 的精度在 1-38 范围内，标度在 0 到精度范围内。可选的
time 和 timestamp 类型的精度在 0-12 范围内。

##### Null 类型

null 类型表示一个只包含 null 值且其具体类型尚未
确定的列。它旨在通过模式演化提升为具体类型，在数据被
写入之前。支持情况特定于连接器。

##### 外部类型

外部类型表示不属于 Gravitino 类型系统的 catalog 类型。它保留了
外部 catalog 的类型字符串，以便客户端可以检查它而不会丢失信息。

```json
{
  "type": "external",
  "catalogString": "user-defined"
}
```

```java
String typeString = ((ExternalType) type).catalogString();
```

##### 未解析的类型

当客户端无法识别返回的类型时，未解析的类型保持了前向兼容
由服务器。客户端保留序列化后的值，而不是导致反序列化失败。

```json
{
  "type": "unparsed",
  "unparsedType": "unknown-type"
}
```

```java
String unparsedValue = ((UnparsedType) type).unparsedType();
```

#### 表列默认值

列的默认值可以是 [literal](./expression.md#literal) 或
[expression](./expression.md)。底层 catalog 将其应用于新行，并且支持情况取决于
catalog provider。

#### 表列自增

自增列要求底层目录为新行生成值。支持与
限制因提供程序而异，因此在启用前请检查提供程序的表功能。

### 表格属性

Properties are provider-specific and carry what the source system needs, such as the file format for
a Hive table or the write mode for an Iceberg table. Each catalog type's page documents its own set.

### 分区、分布与排序顺序

可以使用分区策略、分布、排序顺序和索引来创建表。
目录支持其中的哪些取决于提供者。参见
[表分区、分布、排序顺序和索引](./table-partitioning-distribution-sort-order-indexes.md)。

表被分区后，其分区本身就是独立的元数据对象。参见
[管理表分区](./manage-table-partition-using-gravitino.md)。

### 删除与清除对比

删除表会移除元数据，对于托管表，也会移除底层目录。对于
外部表，仅移除元数据，数据保留在原处。

清除操作会彻底删除数据，并跳过系统原本会使用的任何回收站。并非每个
目录都支持它，并且清除外部表会被拒绝，而不是被静默忽略。

这种区别在 Hive 上最为重要，因为外部表很常见，并且删除一个表会将
文件保留在原地。

## 视图

视图是一个存储的查询，Gravitino 将其视为一种独立的对象类型，而不是一种
表。视图受 Hive、Iceberg 和 Paimon 目录支持，而带有
不支持视图概念的提供者的关系型目录则根本没有视图。

视图携带查询文本、编写查询所用的方言，以及其自身的注释和
属性。Gravitino 存储该定义但不执行它，因此视图是否能解析是一个
读取它的引擎的问题。

视图可以携带标签，并与表一起出现在列表中。

## 在 UI 中使用表和视图

打开架构会列出其表和视图。选择一个表会显示其列及其类型，
其属性和标签。

标签从表行和单个列行附加，这是分类的最快方法
特定字段而不是整个表。策略在表级别附加。

## 权限

| 权限      | 可授权对象                        | 允许的操作                  |
|----------------|-------------------------------------|---------------------------------|
| `CREATE_TABLE` | Metalake、catalog 或 schema        | 创建表                 |
| `SELECT_TABLE` | Metalake、catalog、schema 或 table | 读取表元数据          |
| `MODIFY_TABLE` | Metalake、catalog、schema 或 table | 写入和修改表           |
| `CREATE_VIEW`  | Metalake、catalog 或 schema        | 创建视图                  |
| `SELECT_VIEW`  | Metalake、catalog、schema 或 view  | 读取视图元数据           |

在更大范围内授权会涵盖其下的所有内容。删除表是保留给
metalake 所有者和对象所有者，并且所有权沿层级向下解析，因此
catalog 的所有者拥有其中每个表的所有者路径。

当启用元数据授权时，列出视图首先需要访问架构，然后
仅返回调用者拥有的或可以使用 `SELECT_VIEW` 读取的视图。创建视图需要
作用域内的 `CREATE_VIEW`，并使调用者成为其所有者；修改和删除视图仅限所有者操作。

查看权限仅涵盖元数据操作。API 尚未定义 `INVOKER` 或
`DEFINER` 执行模式，因此对引用数据的访问仍受引擎的
授权。

## 使用 API

表和视图可以通过 REST 以及 Java 和
Python 客户端进行创建、列出、修改和删除。端点、负载结构和操作示例位于
[管理关系元数据](./manage-relational-metadata-using-gravitino.md) 和
[管理视图元数据](./manage-view-metadata-using-gravitino.md)。
