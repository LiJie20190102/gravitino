---
title: "Spark Connector"
slug: "/spark-connector/spark-connector"
keyword: "spark connector federation query"
license: "This software is licensed under the Apache License version 2."
---

## 概述

Apache Gravitino Spark 连接器利用 Spark DataSourceV2 接口来促进对 Gravitino 下多种 catalog 的管理。这一能力允许用户执行联邦查询，通过统一接口和一致的访问控制访问来自不同 catalog 的数据。

## 能力

1. 支持 [Hive catalog](spark-catalog-hive.md)、[Iceberg catalog](spark-catalog-iceberg.md)、[Paimon catalog](spark-catalog-paimon.md)、[Jdbc catalog](spark-catalog-jdbc.md) 和 [AWS Glue catalog](spark-catalog-glue.md)。
2. 支持联邦查询。
3. 支持大多数 DDL 和 DML SQL。

## 需求

* Spark 3.5 或 4.0
* Spark 3.5 上的 Scala 2.12 或 2.13；Spark 4 仅支持 Scala 2.13
* Spark 3.5 上的 JDK 8、11 或 17；Spark 4 需要 JDK 17

## 用法

1. [构建](../how-to-build.md) 或下载与您的 Spark 次要版本和 Scala 版本相匹配的包 ([gravitino-spark-connector-runtime-3.5_2.12](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-spark-connector-runtime-3.5_2.12), [gravitino-spark-connector-runtime-3.5_2.13](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-spark-connector-runtime-3.5_2.13), [gravitino-spark-connector-runtime-4.0_2.13](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-spark-connector-runtime-4.0_2.13))，并将其放置到 Spark 的 classpath 中。
2. 配置 Spark 会话以使用 Gravitino spark connector。

| 属性                                         | 类型    | 默认值 | 描述                                                                                                                                                              | 必填 |
|--------------------------------------------------|---------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| spark.plugins                                    | string  | (none)        | Gravitino spark 插件名称，`org.apache.gravitino.spark.connector.plugin.GravitinoSparkPlugin`                                                                          | 是      |
| spark.sql.gravitino.metalake                     | string  | (none)        | spark connector 用于请求 Gravitino 的 metalake 名称。                                                                                                     | 是      |
| spark.sql.gravitino.uri                          | string  | (none)        | Gravitino 服务器地址的 uri。                                                                                                                                     | 是      |
| spark.sql.gravitino.enableIcebergSupport         | string  | `false`       | 设置为 `true` 以使用 Iceberg catalog。                                                                                                                                    | 否       |
| spark.sql.gravitino.enablePaimonSupport          | string  | `false`       | 设置为 `true` 以使用 Paimon catalog。                                                                                                                                     | 否       |
| spark.sql.gravitino.client.                      | string  | (none)        | Gravitino 客户端配置的配置键前缀。                                                                                                            | 否       |
| spark.sql.gravitino.authType                     | string  | `simple`      | 认证类型，为 `simple`、`basic`、`oauth2`、`kerberos`、`token` 之一。                                                                                        | 否       |
| spark.sql.gravitino.token.value                  | string  | (none)        | 提交给 Gravitino 的 bearer token，在 `authType` 为 `token` 时使用。                                                                                               | 否       |
| spark.sql.gravitino.token.file                   | string  | (none)        | 包含 bearer token 的文件路径。优先级高于 `token.value`，并且每次请求时都会重新读取。                                                                 | 否       |
| spark.sql.gravitino.token.principalFields        | string  | `sub`         | 逗号分隔、有序的 JWT claim 名称，用于在 `token` 模式下识别调用者。                                                                                    | 否       |
| spark.sql.gravitino.clientCacheMaxSize           | int     | `100`         | 缓存的 Gravitino 客户端最大数量，每个身份一个。                                                                                                        | 否       |
| spark.sql.gravitino.clientCacheTtlSec            | long    | `3600`        | 在缓存的 Gravitino 客户端最后一次使用后的这么多秒后将其逐出。                                                                                               | 否       |
| spark.sql.gravitino.catalogCacheTtlSec           | long    | `300`         | 在缓存的 catalog 加载后的这么多秒后将其逐出。                                                                                                           | 否       |
| spark.sql.gravitino.iceberg.rest-routing-enabled | boolean | `true`        | 由 `hive` 和 `jdbc` 支持的 Iceberg catalog 是否必须通过 Gravitino Iceberg REST 服务器路由。设置为 `false` 以保留旧版原生后端转换。  | 否       |
| spark.sql.gravitino.iceberg.rest-uri             | string  | (none)        | 覆盖自动发现的 Gravitino Iceberg REST 服务器端点。参见 [Iceberg catalog](spark-catalog-iceberg.md#routing-through-the-gravitino-iceberg-rest-server)。 | 否       |
| spark.sql.gravitino.iceberg.reuseOAuth2          | boolean | `true`        | 为路由的 Iceberg REST catalog 重用 Gravitino OAuth2 客户端配置。显式的 IRC OAuth2 属性会覆盖各个重用的值。                     | 否       |
| spark.sql.gravitino.iceberg.rest.                | string  | (none)        | Iceberg REST 客户端配置的配置键前缀（例如 `rest.auth.type`），在 catalog 通过 Gravitino Iceberg REST 服务器路由时应用。     | 否       |

要配置 Gravitino 客户端，请使用以 `spark.sql.gravitino.client.` 为前缀的属性。这些属性在移除 `spark.sql.` 前缀后将传递给 Gravitino 客户端。

**示例：** 设置 `spark.sql.gravitino.client.socketTimeoutMs` 相当于为 Gravitino 客户端设置 `gravitino.client.socketTimeoutMs`。

**注意：** 无效的配置属性将导致异常。请参阅 [Gravitino Java 客户端配置](../how-to-use-gravitino-client.md#java-client-configuration) 以获取更多支持的客户端配置。

### `token` 模式下的每用户身份

当 `spark.sql.gravitino.authType` 为 `token` 时，连接器会提供在
`spark.sql.gravitino.token.file` 中找到的 bearer token，若没有则使用 `spark.sql.gravitino.token.value`，并在
每次请求时重新解析它，并优先读取活动 Spark 会话的配置，而不是
应用程序的配置。调用者的身份取自
`spark.sql.gravitino.token.principalFields` 指定的 JWT claim，该字段应设置为与服务器的
`gravitino.authenticator.oauth.principalFields` 相匹配，以便连接器和服务器就谁在
发起请求达成一致。该 claim 在不验证签名的情况下读取，因为验证 token 仍然是
服务器的工作；该值仅用于对连接器的缓存进行分区。不透明的、
非 JWT token 则通过 token 的哈希值进行分区。

Gravitino 客户端及其加载的目录元数据按身份进行缓存，因此共享
一个 Spark driver 的两个用户永远不会看到彼此缓存的元数据。所有其他身份验证类型保持
单一应用级身份，不受上述任何情况的影响。

有两个限制值得明确指出：

* 在驱动程序启动时向 Spark 注册的目录列表使用应用程序的
身份进行解析，因此用户可能会看到随后不允许其打开的目录名称。
* 这仅控制元数据解析。数据由执行器使用
构建底层目录时所用的凭据来读取，而不是最终用户的令牌。

```shell
./bin/spark-sql -v \
--conf spark.plugins="org.apache.gravitino.spark.connector.plugin.GravitinoSparkPlugin" \
--conf spark.sql.gravitino.uri=http://127.0.0.1:8090 \
--conf spark.sql.gravitino.metalake=test \
--conf spark.sql.gravitino.enableIcebergSupport=true \
--conf spark.sql.gravitino.client.socketTimeoutMs=60000 \
--conf spark.sql.gravitino.client.connectionTimeoutMs=60000 \
--conf spark.sql.warehouse.dir=hdfs://127.0.0.1:9000/user/hive/warehouse-hive
```

3. [下载](https://iceberg.apache.org/releases/) 对应的运行时 jar 包，如果使用 Iceberg catalog，则将其放置到 Spark 的 classpath 中。

4. 执行 Spark SQL 查询。

假设在 metalake `test` 中有两个 catalog，`hive` 用于 Hive catalog，`iceberg` 用于 Iceberg catalog。

```sql
// use hive catalog
USE hive;
CREATE DATABASE db;
USE db;
CREATE TABLE hive_students (id INT, name STRING);
INSERT INTO hive_students VALUES (1, 'Alice'), (2, 'Bob');

// use Iceberg catalog
USE iceberg;
USE db;
CREATE TABLE IF NOT EXISTS iceberg_scores (id INT, score INT) USING iceberg;
INSERT INTO iceberg_scores VALUES (1, 95), (2, 88);

// execute federation query between hive table and iceberg table
SELECT hs.name, is.score FROM hive.db.hive_students hs JOIN iceberg_scores is ON hs.id = is.id;
```

:::info
由于 Spark catalog 管理器的限制，命令 `SHOW CATALOGS` 将仅显示名为 spark_catalog 的 Spark 默认 catalog。它不会列出 metalake 中存在的 catalog。但是，在显式使用带有特定 catalog 名称的 `USE` 命令后，该 catalog 名称便会显示在 `SHOW CATALOGS` 的输出中。
:::

## 数据类型映射

Gravitino Spark 连接器支持 Spark 和 Gravitino 之间的以下数据类型映射。

| Spark 数据类型                   | Gravitino 数据类型           |
|-----------------------------------|-------------------------------|
| `BooleanType`                     | `boolean`                     |
| `ByteType`                        | `byte`                        |
| `ShortType`                       | `short`                       |
| `IntegerType`                     | `integer`                     |
| `LongType`                        | `long`                        |
| `FloatType`                       | `float`                       |
| `DoubleType`                      | `double`                      |
| `DecimalType`                     | `decimal`                     |
| `StringType`                      | `string`                      |
| `CharType`                        | `char`                        |
| `VarcharType`                     | `varchar`                     |
| `TimestampType`                   | `timestamp with time zone`    |
| `TimestampNTZType`                | `timestamp without time zone` |
| `DateType`                        | `date`                        |
| `BinaryType`                      | `binary`                      |
| `ArrayType`                       | `array`                       |
| `MapType`                         | `map`                         |
| `StructType`                      | `struct`                      |

:::note
对于 Gravitino `UUID` 类型，Spark connector 将其表示为 `StringType`，因为 Spark 没有原生的 UUID 类型。
此行为与 Spark 内置的 PostgreSQL JDBC 映射（`uuid` -> `StringType`）一致。
:::
