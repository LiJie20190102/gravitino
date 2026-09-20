---
title: "Partitions"
slug: "/partitions"
keyword: "partition, partition management, partition pruning, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

## 介绍

分区是表数据的一个命名切片，在 Gravitino 中它是一个元数据对象，你可以
列出、检查、添加和删除。

大多数情况下，分区会自行管理。目录会在数据到达时创建它们，而
引擎在查询时无需任何人要求即可对它们进行剪枝。手动管理它们在少数
特定情况下很重要：按分区而不是按行使数据过期，记录每个分区的统计信息，以便
规划器可以基于它们进行剪枝，以及在将要填充它的数据到达之前添加分区。

分区属于分区表。当表在创建时带有
分区策略时，表即成为分区表，这与分区本身是分开的。参见
[表分区、分布、排序和索引](./table-partitioning-distribution-sort-order-indexes.md)。

## 快速开始

**1. 从分区表开始。** 没有分区策略的表没有分区可以
管理。请参阅[表和视图](./tables-and-views.md)。

**2. 选择您的 catalog 使用的路径。** 在 Hive、Glue 和 Doris 上，分区是您管理的对象
通过 Gravitino API。在 Iceberg 上，分区是通过 Iceberg 兼容引擎更改的
指向 Iceberg REST catalog 服务，该服务默认监听 9001 端口。

**3. 列出、添加或删除。** 两种路径都通过 API 进行。UI 显示表的分区情况，但
不列出、添加或删除单个分区。

## 分区模型

### 分区类型

| 类型       | 描述                                                        |
|------------|------------------------------------------------------------------|
| `IDENTITY` | 每个分区列一个值，例如 `dt=2026-08-02`       |
| `RANGE`    | 上限和下限，例如日期范围                   |
| `LIST`     | 一组明确的值组合                            |

类型取决于表的分区方式，而不是按分区选择。

### 分区管理在何处生效

通过 Gravitino API 进行分区管理适用于 Hive、Glue 和 Doris 目录。每个
下面的操作均可在上述三者上使用，且不适用于其他。

Iceberg、Paimon 和 Hudi 自行管理分区，并且除 Doris 外的 JDBC catalog 具有
没有分区操作，因此对其中任何一个的调用都会失败，而不是返回空列表。
对于这些 catalog，Gravitino 并未缺失任何内容，并且以下章节说明了替代做法。

### Iceberg 表

Iceberg 的分区方式有所不同，这种差异是刻意为之，而不是一种缺陷。

一个 Iceberg 表声明一个分区规范，即一组对其列的转换，例如
`day(event_time)` 或 `bucket(16, customer_id)`。然后分区会在数据
到达时从数据中派生，Iceberg 将此称为隐藏分区。没有可以添加、获取或删除的分区对象，
这就是为什么 Iceberg 不在上面的列表中。

Gravitino 在创建表时设置 spec。Identity、bucket、truncate、year、month、day 和
hour 转换全部转换为 Iceberg spec，其中 bucket 限制为单个字段。List 和 range
分区在 Iceberg 中没有对应项，会被拒绝。

创建后，分区的更改是通过引擎而不是通过 Gravitino API 进行的。
将 Spark、Trino 或其他 Iceberg 客户端指向 Iceberg REST catalog 服务，该服务监听
默认端口 9001，并使用引擎自身的语法：

```sql
ALTER TABLE sales.public.orders ADD PARTITION FIELD day(event_time);
ALTER TABLE sales.public.orders DROP PARTITION FIELD country;
```

Iceberg REST catalog 服务处理生成的 `AddPartitionSpec` 和
`SetDefaultPartitionSpec` 更新，因此分区演化的行为与针对任何
Iceberg catalog 的行为完全相同。现有数据不会被重写，新的 spec 适用于之后写入的
数据。

参见 [Iceberg REST 目录服务](./iceberg-rest-service.md)。

### 分区与统计信息

统计信息附加到分区以及整个表上，这使得针对每个分区的
度量值可供规划器使用。参见 [统计信息](./statistics.md)。

## 在 UI 中使用分区

表页面显示了表的分区策略、创建时使用的转换，以及一个
其分区字段数量的计数。按 `dt` 和 `country` 分区的表显示两个。
不会列出各个分区，添加或删除分区需通过 API 进行。

显示内容来自表本身，因此它适用于包括 Iceberg 在内的每个关系型目录。
按 `day(event_time)` 分区的 Iceberg 表像任何其他表一样显示该转换，因为
分区规范被读回并以相同的形式呈现。计数为零通常意味着
表未声明分区，而不是无法读取分区。一个例外是
ClickHouse：一个其 `PARTITION BY` 使用了 Gravitino 无法结构化的原生表达式的表
显示零个分区字段，而规范表达式作为替代保留在只读的 `partition-key`
属性中。

## 权限

分区遵循其所属的表。列出它们需要读取该表的权限，
而添加或删除需要修改该表的权限。参见
[表和视图](./tables-and-views.md)。

## 使用 API

在 Hive、Glue 和 Doris 上，分区的列出、添加、检查和删除是通过 REST 以及
Java 和 Python 客户端进行的。端点、负载结构和操作示例位于
[管理表分区](./manage-table-partition-using-gravitino.md)。

在 Iceberg 上，分区更改是通过兼容 Iceberg 的引擎指向
[Iceberg REST catalog service](./iceberg-rest-service.md) 而不是通过这些端点。

分区统计是一个独立的路径，适用于任何表，包括 Iceberg。它们由
Gravitino 而不是 catalog 持有，因此即使在 catalog 未暴露
可列出的分区对象的情况下，分区也可以携带统计信息。分区名称由调用者提供，而不是
被发现的，并且统计信息是在一个范围内读取和写入的，而不是一次一个。参见
[Statistics](./statistics.md) 和 [Manage Statistics](./manage-statistics-in-gravitino.md)。
