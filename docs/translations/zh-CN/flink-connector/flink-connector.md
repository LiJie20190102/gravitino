---
slug: /flink-connector/flink-connector
keyword: flink connector federation query
license: This software is licensed under the Apache License version 2.
title: Flink 连接器
---
## 概述

Apache Gravitino Flink 连接器实现了 [Catalog Store](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/table/catalogs/#catalog-store) 来管理 Gravitino 下的 Catalog。
该功能支持执行联邦查询，通过统一的接口和一致的访问控制访问来自各种 Catalog 的数据。

该连接器针对每个支持的 Flink 次要版本发布为特定版本的运行时 JAR。在内部，Gravitino 使用共享的连接器逻辑以及特定版本的 Catalog 和工厂入口点，以便每个运行时构件与其运行的 Flink API 匹配。

## 功能特性

1. 支持 [Hive catalog](flink-catalog-hive.md)
2. 支持 [Iceberg catalog](flink-catalog-iceberg.md)
3. 支持 [Paimon catalog](flink-catalog-paimon.md)
4. 支持 [Jdbc catalog](flink-catalog-jdbc.md)
5. 支持大多数 DDL 和 DML SQL。

## 前提条件

* Scala 2.12
* Flink 1.18、1.19 或 1.20
* JDK 8、11 或 17

## 使用方式

1. [构建](../how-to-build.md)或下载与 Flink 次要版本匹配的 Gravitino Flink 连接器运行时 JAR，并将其放置在 Flink 的 classpath 中。

| Flink 版本 | 运行时构件 |
|---------------|------------------|
| 1.18          | `gravitino-flink-connector-runtime-1.18_2.12-${gravitino-version}.jar` |
| 1.19          | `gravitino-flink-connector-runtime-1.19_2.12-${gravitino-version}.jar` |
| 1.20          | `gravitino-flink-connector-runtime-1.20_2.12-${gravitino-version}.jar` |

不要在同一 Flink 部署中混合使用来自不同 Flink 次要版本的运行时 JAR。

2. 配置 Flink 配置以使用 Gravitino Flink 连接器。

| 属性                                                            | 类型    | 默认值     | 描述                                                                           | 必填 |
|---------------------------------------------------------------------|---------|-------------------|---------------------------------------------------------------------------------------|----------|
| table.catalog-store.kind                                            | string  | generic_in_memory | Catalog Store 名称，应设置为 `gravitino`。                                 | 是      |
| table.catalog-store.gravitino.gravitino.metalake                    | string  | (none)            | Flink 连接器用于向 Gravitino 发起请求的 metalake 名称。                  | 是      |
| table.catalog-store.gravitino.gravitino.uri                         | string  | (none)            | Gravitino 服务器地址的 URI。                                                  | 是      |
| table.catalog-store.gravitino.gravitino.enableSessionCatalogSupport | boolean | false             | 是否在 Gravitino Catalog Store 中启用对 Flink session catalog 的支持。 | 否       |
| table.catalog-store.gravitino.gravitino.client.                     | string  | (none)            | Gravitino 客户端配置的配置键前缀。                         | 否       |

当 `table.catalog-store.gravitino.gravitino.enableSessionCatalogSupport` 设置为 `true` 时，Gravitino 使用 `GravitinoSessionCatalogStore`，它将 `GravitinoCatalogStore`（由 Gravitino 服务器支持）与内存存储结合，以支持 Flink 的 session catalog。当设置为 `false`（默认值）时，仅使用 `GravitinoCatalogStore`。

启用 session catalog 支持时，适用以下行为：

- **CREATE CATALOG**：Gravitino 管理的 Catalog（例如 `gravitino-hive`、`gravitino-iceberg`）会持久化到 Gravitino 服务器；非 Gravitino 管理的 Catalog（例如 `hive`、`jdbc` 或任何自定义连接器类型）仅存储在内存存储中。
- **GET / USE CATALOG**：首先检查内存存储。如果未在其中找到该 Catalog，则从 Gravitino 服务器检索。
- **DROP CATALOG**：首先检查内存存储。如果该 Catalog 在其中存在，则从内存中移除；否则从 Gravitino 服务器移除。
- **SHOW / LIST CATALOGS**：返回内存存储和 Gravitino 服务器中 Catalog 的合并集合。
- **Session scope**：仅在内存中存储的 Catalog 是 session 范围内的，在 Flink 重启后将不复存在。
- **Name conflict**：如果两个存储中存在同名 Catalog，则内存中的条目优先。

要配置 Gravitino 客户端，请使用以 `table.catalog-store.gravitino.gravitino.client.` 为前缀的属性。这些属性在移除 `table.catalog-store.gravitino.` 前缀后将传递给 Gravitino 客户端。

**示例：** 设置 `table.catalog-store.gravitino.gravitino.client.socketTimeoutMs` 等同于为 Gravitino 客户端设置 `gravitino.client.socketTimeoutMs`。

**注意：** 无效的配置属性将导致异常。有关更多支持的客户端配置，请参阅 [Gravitino Java 客户端配置](../how-to-use-gravitino-client.md#java-client-configuration)。

在 flink-conf.yaml 中设置 Flink 配置。
```yaml
table.catalog-store.kind: gravitino
table.catalog-store.gravitino.gravitino.metalake: metalake_demo
table.catalog-store.gravitino.gravitino.uri: http://localhost:8090
table.catalog-store.gravitino.gravitino.enableSessionCatalogSupport: true
table.catalog-store.gravitino.gravitino.client.socketTimeoutMs: 60000
table.catalog-store.gravitino.gravitino.client.connectionTimeoutMs: 60000
```
或者在 `TableEnvironment` 中设置 Flink 配置。
```java
final Configuration configuration = new Configuration();
configuration.setString("table.catalog-store.kind", "gravitino");
configuration.setString("table.catalog-store.gravitino.gravitino.metalake", "metalake_demo");
configuration.setString("table.catalog-store.gravitino.gravitino.uri", "http://localhost:8090");
configuration.setBoolean("table.catalog-store.gravitino.gravitino.enableSessionCatalogSupport", true);
configuration.setString("table.catalog-store.gravitino.gravitino.client.socketTimeoutMs", "60000");
configuration.setString("table.catalog-store.gravitino.gravitino.client.connectionTimeoutMs", "60000");
EnvironmentSettings.Builder builder = EnvironmentSettings.newInstance().withConfiguration(configuration);
TableEnvironment tableEnv = TableEnvironment.create(builder.inBatchMode().build());
```

3. 将必要的 jar 文件添加到 Flink 的 classpath 中。

要使用 Gravitino 连接器运行 Flink 并访问如 Hive 等数据源，可能需要将额外的 jar 包放入 Flink 的 classpath 中。有关更多信息，请参阅 [Flink 文档](https://nightlies.apache.org/flink/flink-docs-master/docs/connectors/table/hive/overview/#dependencies)。

4. 执行 Flink SQL 查询。

假设在 metalake `metalake_demo` 中只有一个名为 `catalog_hive` 的 Hive catalog。

```sql
// use hive catalog
USE CATALOG catalog_hive;
CREATE DATABASE db;
USE db;
SET 'execution.runtime-mode' = 'batch';
SET 'sql-client.execution.result-mode' = 'tableau';
CREATE TABLE hive_students (id INT, name STRING);
INSERT INTO hive_students VALUES (1, 'Alice'), (2, 'Bob');
SELECT * FROM hive_students;
```

## Catalog 命名限制

:::caution
创建将与 Flink 连接器一起使用的 Catalog 时，Catalog 名称<strong>不能以数字开头</strong>。这是 Flink 的限制。例如：
- ✅ 有效：`catalog_hive`、`hive_catalog`、`my_catalog_1`
- ❌ 无效：`1_catalog`、`123catalog`、`2hive`

如果创建以数字开头的 Catalog，则无法从 Flink 访问该 Catalog。
:::

## 数据类型映射

Gravitino Flink 连接器支持 Flink 和 Gravitino 之间的以下数据类型映射。

| Flink 类型                       | Gravitino 类型                |
|----------------------------------|-------------------------------|
| `array`                          | `list`                        |
| `bigint`                         | `long`                        |
| `binary`                         | `fixed`                       |
| `boolean`                        | `boolean`                     |
| `char`                           | `char`                        |
| `date`                           | `date`                        |
| `decimal`                        | `decimal`                     |
| `double`                         | `double`                      |
| `float`                          | `float`                       |
| `integer`                        | `integer`                     |
| `map`                            | `map`                         |
| `null`                           | `null`                        |
| `row`                            | `struct`                      |
| `smallint`                       | `short`                       |
| `time`                           | `time`                        |
| `timestamp`                      | `timestamp without time zone` |
| `timestamp without time zone`    | `timestamp without time zone` |
| `timestamp with time zone`       | `timestamp with time zone`    |
| `timestamp with local time zone` | `timestamp with time zone`    |
| `timestamp_ltz`                  | `timestamp with time zone`    |
| `tinyint`                        | `byte`                        |
| `varbinary`                      | `binary`                      |
| `varchar`                        | `string`                      |