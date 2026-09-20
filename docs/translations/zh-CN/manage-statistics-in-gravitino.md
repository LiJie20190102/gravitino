---
title: "Manage Statistics"
slug: "/manage-statistics-in-gravitino"
keyword: "statistics management, statistics, partition statistics, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

This page covers the Gravitino API for statistics. For what a statistic is, the difference between
reserved and custom, and how partition statistics relate to partitions, see
[Statistics](./statistics.md).

统计信息附加到表上。自定义名称必须以 `custom.` 开头，以避开 Gravitino
日后可能保留的名称。

## 表统计信息

### 更新统计信息

更新会创建不存在的统计信息，并覆盖已存在的统计信息。保留的统计信息
由系统维护的不可修改，并且请求会被拒绝。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": {
    "custom.last_reviewed": "2026-08-02",
    "custom.owner_team": "risk"
  }
}' http://localhost:8090/api/metalakes/example/objects/table/sales.public.orders/statistics
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table orders = ...
Map<String, StatisticValue<?>> updates = Maps.newHashMap();
updates.put("custom.last_reviewed", StatisticValues.stringValue("2026-08-02"));
updates.put("custom.owner_team", StatisticValues.stringValue("risk"));

orders.supportsStatistics().updateStatistics(updates);
```

</TabItem>
</Tabs>

### 列表统计

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/objects/table/sales.public.orders/statistics
```

</TabItem>
<TabItem value="java" label="Java">

```java
List<Statistic> statistics = orders.supportsStatistics().listStatistics();
```

</TabItem>
</Tabs>

### 掉落统计

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "names": ["custom.owner_team"]
}' http://localhost:8090/api/metalakes/example/objects/table/sales.public.orders/statistics
```

</TabItem>
<TabItem value="java" label="Java">

```java
orders.supportsStatistics().dropStatistics(ImmutableList.of("custom.owner_team"));
```

</TabItem>
</Tabs>

## 分区统计

分区统计信息由 Gravitino 而不是 catalog 持有，因此它们适用于任何表
包括那些不暴露分区对象的 catalog。分区名称由调用者提供，并且
在一次请求中读取或写入多个分区。

### 更新分区统计信息

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {
      "partitionName": "dt=2026-08-02",
      "statistics": {"custom.row_estimate": "18000"}
    }
  ]
}' http://localhost:8090/api/metalakes/example/objects/table/sales.public.orders/statistics/partitions
```

</TabItem>
<TabItem value="java" label="Java">

```java
Map<String, StatisticValue<?>> stats = Maps.newHashMap();
stats.put("custom.row_estimate", StatisticValues.longValue(18000L));

orders.supportsPartitionStatistics().updatePartitionStatistics(
    ImmutableList.of(PartitionStatisticsModification.update("dt=2026-08-02", stats)));
```

</TabItem>
</Tabs>

### 列表分区统计信息

列出接受分区范围，而不是单个名称。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/example/objects/table/sales.public.orders/statistics/partitions?from=dt=2026-08-01&to=dt=2026-08-31"
```

</TabItem>
<TabItem value="java" label="Java">

```java
List<PartitionStatistics> statistics = orders.supportsPartitionStatistics().listPartitionStatistics(
    PartitionRange.between(
        "dt=2026-08-01", PartitionRange.BoundType.CLOSED,
        "dt=2026-08-31", PartitionRange.BoundType.CLOSED));
```

</TabItem>
</Tabs>

### 删除分区统计信息

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "drops": [
    {
      "partitionName": "dt=2026-08-02",
      "statisticNames": ["custom.row_estimate"]
    }
  ]
}' http://localhost:8090/api/metalakes/example/objects/table/sales.public.orders/statistics/partitions
```

</TabItem>
<TabItem value="java" label="Java">

```java
orders.supportsPartitionStatistics().dropPartitionStatistics(
    ImmutableList.of(
        PartitionStatisticsModification.drop(
            "dt=2026-08-02", ImmutableList.of("custom.row_estimate"))));
```

</TabItem>
</Tabs>

## 存储配置

分区统计使用可插拔的存储后端，在服务器上进行配置。参见
下文的[服务器配置](#server-configuration)。编写自定义后端的内容包含在
[自定义分区存储](./development/custom-partition-storage.md)。

### 服务器配置

| 配置项                              | 描述                                                                                                                                                                                                                          | 默认值                                                             | 必填 |
|-------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|----------|
| `gravitino.stats.partition.storageFactoryClass` | 分区统计信息的存储工厂类，用于在不同的存储中存储分区统计信息。`org.apache.gravitino.stats.storage.MemoryPartitionStatsStorageFactory` 只能用于测试。 | `org.apache.gravitino.stats.storage.JdbcPartitionStatisticStorageFactory` | 否       |


#### JDBC 存储（默认）

从 1.2.0 版本开始，Gravitino 使用基于 JDBC 的存储作为默认的分区统计存储后端。
这提供了一个可靠的、生产就绪的解决方案，支持多种数据库后端：

- **MySQL** (推荐用于生产环境)
- **PostgreSQL**
- **H2** (适合测试和开发)

要使用 JDBC 存储，请通过添加前缀 `gravitino.stats.partition.storageOption.` 来配置以下选项：

| 配置项                                            | 描述                                                       | 默认值              | 必填 |
|---------------------------------------------------------------|-------------------------------------------------------------------|----------------------------|----------|
| `gravitino.stats.partition.storageOption.jdbcUrl`             | JDBC 连接 URL（例如，jdbc:mysql://localhost:3306/gravitino） | 无                       | 是      |
| `gravitino.stats.partition.storageOption.jdbcUser`            | 数据库用户名                                                 | 无                       | 是      |
| `gravitino.stats.partition.storageOption.jdbcPassword`        | 数据库密码                                                 | 无                       | 是      |
| `gravitino.stats.partition.storageOption.jdbcDriver`          | JDBC 驱动类名                                            | `com.mysql.cj.jdbc.Driver` | 否       |
| `gravitino.stats.partition.storageOption.poolMaxSize`         | 最大连接池大小                                      | `10`                       | 否       |
| `gravitino.stats.partition.storageOption.poolMinIdle`         | 连接池中最小空闲连接数                                  | `2`                        | 否       |
| `gravitino.stats.partition.storageOption.connectionTimeoutMs` | 连接超时时间（毫秒）                                | `30000`                    | 否       |
| `gravitino.stats.partition.storageOption.testOnBorrow`        | 使用前测试连接                                       | `true`                     | 否       |

**示例 MySQL 配置：**

```properties
gravitino.stats.partition.storageFactoryClass = org.apache.gravitino.stats.storage.JdbcPartitionStatisticStorageFactory
gravitino.stats.partition.storageOption.jdbcUrl = jdbc:mysql://localhost:3306/gravitino
gravitino.stats.partition.storageOption.jdbcUser = gravitino
gravitino.stats.partition.storageOption.jdbcPassword = gravitino123
gravitino.stats.partition.storageOption.poolMaxSize = 20
```

**PostgreSQL 配置示例：**

```properties
gravitino.stats.partition.storageFactoryClass = org.apache.gravitino.stats.storage.JdbcPartitionStatisticStorageFactory
gravitino.stats.partition.storageOption.jdbcUrl = jdbc:postgresql://localhost:5432/gravitino
gravitino.stats.partition.storageOption.jdbcUser = gravitino
gravitino.stats.partition.storageOption.jdbcPassword = gravitino123
gravitino.stats.partition.storageOption.jdbcDriver = org.postgresql.Driver
```

**数据库模式设置：**

在使用 JDBC 存储之前，您需要创建数据库 schema。为所有支持的数据库均提供了 schema 文件：

- MySQL: `scripts/mysql/schema-${GRAVITINO_VERSION}-mysql.sql`
- PostgreSQL: `scripts/postgresql/schema-${GRAVITINO_VERSION}-postgresql.sql`
- H2: `scripts/h2/schema-${GRAVITINO_VERSION}-h2.sql`

对于 MySQL：
```bash
mysql -u root -p < scripts/mysql/schema-${GRAVITINO_VERSION}-mysql.sql
```

对于 PostgreSQL：
```bash
psql -U postgres -d gravitino -f scripts/postgresql/schema-${GRAVITINO_VERSION}-postgresql.sql
```

#### Lance 存储（备选）

如果您使用 [Lance](https://lancedb.github.io/lance/) 作为分区统计存储，您可以设置以下选项，如果您有其他 lance 存储选项，可以通过添加前缀 `gravitino.stats.partition.storageOption.` 来传递它。
例如，如果您为 Lance 存储选项设置了额外属性 `foo` 为 `bar`，您可以添加一个配置项 `gravitino.stats.partition.storageOption.foo`，其值为 `bar`。

关于 Lance 远程存储，您可以参考[这里](https://lancedb.github.io/lance/usage/storage/)的文档。


| 配置项                                                   | 描述                                               | 默认值                        | 必填 |
|----------------------------------------------------------------------|-----------------------------------------------------------|--------------------------------------|----------|
| `gravitino.stats.partition.storageOption.location`                   | Lance 文件的位置                               | `${GRAVITINO_HOME}/data/lance`       | 否       |
| `gravitino.stats.partition.storageOption.maxRowsPerFile`             | 每个文件的最大行数                                 | `1000000`                            | 否       |
| `gravitino.stats.partition.storageOption.maxBytesPerFile`            | 每个文件的最大字节数                                | `104857600`                          | 否       |
| `gravitino.stats.partition.storageOption.maxRowsPerGroup`            | 每个组的最大行数                                | `1000000`                            | 否       |
| `gravitino.stats.partition.storageOption.readBatchSize`              | 读取时的批量记录数                      | `10000`                              | 否       |
| `gravitino.stats.partition.storageOption.datasetCacheSize`           | Lance 的数据集缓存大小                           | `0`，表示不使用缓存 | 否       |
| `gravitino.stats.partition.storageOption.metadataFileCacheSizeBytes` | Lance 的元数据文件缓存大小                      | `102400`                             | 否       |
| `gravitino.stats.partition.storageOption.indexCacheSizeBytes`        | Lance 的索引缓存大小                              | `102400`                             | 否       |
| `gravitino.stats.partition.storageOption.maxStatisticsPerUpdate`     | 每次更新操作允许的最大统计信息数量 | `100`                                | 否       |

如果有大量分区数较少的表，则应设置较小的 metadataFileCacheSizeBytes 和 indexCacheSizeBytes。

**要使用 Lance 存储，请配置：**

```properties
gravitino.stats.partition.storageFactoryClass = org.apache.gravitino.stats.storage.LancePartitionStatisticStorageFactory
gravitino.stats.partition.storageOption.location = /data/lance
```
