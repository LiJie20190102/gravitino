---
title: "Spark Connector: Iceberg Catalog"
slug: "/spark-connector/spark-catalog-iceberg"
keyword: "spark connector iceberg catalog"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino Spark 连接器提供读写 Iceberg 表的能力，其中元数据由 Gravitino 服务器管理。

## 准备工作

1. 在 Spark 配置中将 `spark.sql.gravitino.enableIcebergSupport` 设置为 `true`。
2. 下载与您的 Spark 次要版本和 Scala 版本相匹配的 Iceberg Spark 运行时 JAR 和 Gravitino Spark 连接器运行时 JAR，并将它们放置在 Spark classpath 中。

Spark 客户端使用的 Iceberg 版本与 Gravitino 服务器 (1.11.0) 不同。请使用下表为您的 Spark 版本选择正确的 JARs。

| Spark 版本 | Scala          | Iceberg 版本 | Iceberg 客户端运行时构件                         | Gravitino 连接器运行时构件                                                |
|---------------|----------------|-----------------|---------------------------------------------------------|-----------------------------------------------------------------------------------|
| 3.5           | 2.12 或 2.13   | 1.11.0          | `iceberg-spark-runtime-3.5_${scala-version}-1.11.0.jar` | `gravitino-spark-connector-runtime-3.5_${scala-version}-${gravitino-version}.jar` |
| 4.0           | 2.13           | 1.11.0          | `iceberg-spark-runtime-4.0_2.13-1.11.0.jar`             | `gravitino-spark-connector-runtime-4.0_2.13-${gravitino-version}.jar`             |

将 `${scala-version}` 替换为 `2.12` 或 `2.13`，并将 `${gravitino-version}` 替换为你的 Gravitino 发行版本。

:::caution
仅使用匹配表格行中的 JARs。在客户端 classpath 上混合使用不同版本的 Iceberg JARs 是不兼容的，可能会导致运行时错误。
:::

## 能力

### DML 和 DDL 操作

- `CREATE TABLE`

不支持分布和排序顺序。

- `DROP TABLE`
- `ALTER TABLE`
- `INSERT INTO&OVERWRITE`
- `SELECT`
- `MERGE INTO`
- `DELETE FROM`
- `UPDATE`
- `CALL`
- `TIME TRAVEL QUERY`
- `DESCRIBE TABLE`

### 不支持的操作

- 视图操作。
- 元数据表，例如：
- `{iceberg_catalog}.{iceberg_database}.{iceberg_table}.snapshots`
- 其他 Iceberg 扩展 SQL，例如：
- `ALTER TABLE prod.db.sample ADD PARTITION FIELD xx`
- `ALTER TABLE ... WRITE ORDERED BY`
- `ALTER TABLE prod.db.sample CREATE BRANCH branchName`
- `ALTER TABLE prod.db.sample CREATE TAG tagName`
- AtomicCreateTableAsSelect&AtomicReplaceTableAsSelect

## SQL 示例

```sql
-- Suppose iceberg_a is the Iceberg catalog name managed by Gravitino
USE iceberg_a;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

CREATE TABLE IF NOT EXISTS employee (
  id bigint,
  name string,
  department string,
  hire_date timestamp
) USING iceberg
PARTITIONED BY (days(hire_date));
DESC TABLE EXTENDED employee;

INSERT INTO employee
VALUES
(1, 'Alice', 'Engineering', TIMESTAMP '2021-01-01 09:00:00'),
(2, 'Bob', 'Marketing', TIMESTAMP '2021-02-01 10:30:00'),
(3, 'Charlie', 'Sales', TIMESTAMP '2021-03-01 08:45:00');

SELECT * FROM employee WHERE date(hire_date) = '2021-01-01';

UPDATE employee SET department = 'Jenny' WHERE id = 1;

DELETE FROM employee WHERE id < 2;

MERGE INTO employee
USING (SELECT 4 as id, 'David' as name, 'Engineering' as department, TIMESTAMP '2021-04-01 09:00:00' as hire_date) as new_employee
ON employee.id = new_employee.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

MERGE INTO employee
USING (SELECT 4 as id, 'David' as name, 'Engineering' as department, TIMESTAMP '2021-04-01 09:00:00' as hire_date) as new_employee
ON employee.id = new_employee.id
WHEN MATCHED THEN DELETE
WHEN NOT MATCHED THEN INSERT *;

-- Suppose that the first snapshotId of employee is 1L and the second snapshotId is 2L
-- Rollback the snapshot for iceberg_a.mydatabase.employee to 1L
CALL iceberg_a.system.rollback_to_snapshot('iceberg_a.mydatabase.employee', 1);
-- Set the snapshot for iceberg_a.mydatabase.employee to 2L
CALL iceberg_a.system.set_current_snapshot('iceberg_a.mydatabase.employee', 2);

-- Suppose that the commit timestamp of the first snapshot is older than '2024-05-27 01:01:00'
-- Time travel to '2024-05-27 01:01:00'
SELECT * FROM employee TIMESTAMP AS OF '2024-05-27 01:01:00';
SELECT * FROM employee FOR SYSTEM_TIME AS OF '2024-05-27 01:01:00';

-- Show the details of employee, such as schema and reserved properties(like location, current-snapshot-id, provider, format, format-version, etc)
DESC EXTENDED employee;
```

有关 `CALL` 的更多详细信息，请参阅 Iceberg 官方文档中的 [Spark Procedures 说明](https://iceberg.apache.org/docs/1.5.2/spark-procedures/#spark-procedures)。

## 目录属性

Gravitino spark 连接器会将 catalog 属性中定义的以下属性名称转换为 Spark Iceberg 连接器配置。

| Gravitino catalog 属性名称 | Spark Iceberg 连接器配置 | 描述                                                                                                                                                                                                         |
|---------------------------------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `catalog-backend`               | `type`                                | Catalog 后端类型。支持 `hive` 或 `jdbc` 或 `rest` 或 `custom`                                                                                                                                                |
| `catalog-backend-impl`          | `catalog-impl`                        | 自定义 catalog 实现的完全限定类名，仅在 `catalog-backend` 为 `custom` 时生效                                                                                                     |
| `uri`                           | `uri`                                 | Catalog 后端 uri                                                                                                                                                                                                 |
| `warehouse`                     | `warehouse`                           | Catalog 后端 warehouse                                                                                                                                                                                           |
| `jdbc-user`                     | `jdbc.user`                           | JDBC 用户名                                                                                                                                                                                                      |
| `jdbc-password`                 | `jdbc.password`                       | JDBC 密码                                                                                                                                                                                                       |
| `io-impl`                       | `io-impl`                             | Iceberg 中 `FileIO` 的 io 实现。                                                                                                                                                                      |
| `s3-endpoint`                   | `s3.endpoint`                         | S3 服务的备用端点。可用于具有不同端点的任何兼容 s3 的对象存储服务的 S3FileIO，或访问虚拟私有云中的私有 S3 端点。 |
| `s3-region`                     | `client.region`                       | S3 服务的区域，例如 `us-west-2`。                                                                                                                                                                     |
| `s3-access-key-id`              | `s3.access-key-id`                    | 用于访问 S3 数据的静态访问密钥 ID。                                                                                                                                                                    |
| `s3-secret-access-key`          | `s3.secret-access-key`                | 用于访问 S3 数据的静态秘密访问密钥。                                                                                                                                                                |
| `s3-path-style-access`          | `s3.path-style-access`                | 是否为 S3 使用路径风格访问。                                                                                                                                                                            |
| `oss-endpoint`                  | `oss.endpoint`                        | 阿里云 OSS 服务的端点。                                                                                                                                                                                 |
| `oss-access-key-id`             | `client.access-key-id`                | 用于访问 OSS 数据的静态访问密钥 ID。                                                                                                                                                                   |
| `oss-secret-access-key`         | `client.access-key-secret`            | 用于访问 OSS 数据的静态秘密访问密钥。                                                                                                                                                               |
| `azure-storage-account-name`    | `adls.auth.shared-key.account.name`   | 用于访问 ADLS 数据的静态存储账户名。                                                                                                                                                           |
| `azure-storage-account-key`     | `adls.auth.shared-key.account.key`    | 用于访问 ADLS 数据的静态存储账户密钥。                                                                                                                                                           |

带有 `spark.bypass.` 前缀的 Gravitino catalog 属性名称会传递给 Spark Iceberg connector。例如，使用 `spark.bypass.clients` 将 `clients` 传递给 Spark Iceberg connector。

:::info
Iceberg catalog 属性 `cache-enabled` 在内部被设置为 `false`，且不允许更改。
:::

## 通过 Gravitino Iceberg REST 服务器进行路由

If the Gravitino server exposes an [Iceberg REST catalog](../iceberg-rest-service.md) (IRC) endpoint for the
current metalake, the Spark connector automatically routes `hive` and `jdbc` backed Iceberg catalogs through
that endpoint instead of talking to the Hive metastore or JDBC database directly. This has no effect on
catalogs whose `catalog-backend` is already `rest` or `custom`.

通过 IRC 服务器进行路由是接收短期、针对每个表的 **vended credentials** 的唯一方式
由 Iceberg 的原生 REST 协议自动刷新。非 REST 路径仍然可以注入单个
在目录初始化时获取一次的 vended credential（参见
[Credential vending](../security/credential-vending.md)），但它不会在每次表访问时刷新。

REST 路由默认启用。端点在每个 Spark 应用程序中发现一次——在
Gravitino Spark 插件的生命周期内，而非每个 `SparkSession`——并且之后不再重新检查。

- 如果未找到可发现的端点（例如，`iceberg-rest` 辅助服务被禁用或
未配置 `catalog-config-provider=dynamic-config-provider`），目录初始化将失败
并提示可操作的错误。设置 `spark.sql.gravitino.iceberg.rest-routing-enabled=false` 以保留
原生的 Hive/JDBC 后端。
- 如果目录的仓库使用带有原生 Iceberg FileIO 的方案（`s3://`、`gs://`、`abfs://` 等）
则必须配置[凭证分发](../security/credential-vending.md)（`credential-providers`）
才能进行路由：路由会将该 FileIO 的任何静态存储凭证替换为分发的
凭证，如果没有凭证分发，目录将失去存储访问权限。目录初始化
如果未进行此配置，将失败并提示可操作的错误。为该目录设置 `rest-routing-enabled=false`
以继续使用旧版的 Hive/JDBC 后端。

要强制使用特定端点而不是依赖自动发现，请设置：

```properties
spark.sql.gravitino.iceberg.rest-uri    http://<gravitino-host>:9001/iceberg
```

要保留旧版 Hive/JDBC 转换并跳过端点发现，请显式禁用路由：

```properties
spark.sql.gravitino.iceberg.rest-routing-enabled    false
```

如果 Gravitino 在 IRC 端点上需要认证，请传递 Iceberg REST 客户端自身的认证
属性，请使用 `spark.sql.gravitino.iceberg.rest.` 前缀。例如，对于 Basic 认证：

```properties
spark.sql.gravitino.iceberg.rest.rest.auth.type            basic
spark.sql.gravitino.iceberg.rest.rest.auth.basic.username  <username>
spark.sql.gravitino.iceberg.rest.rest.auth.basic.password  <password>
```

See [Connect Spark to Iceberg REST](../iceberg-rest-engine/spark.md) for the full set of supported
`rest.auth.*` properties and how to configure them when connecting directly to the IRC endpoint.

当 Gravitino 客户端使用 OAuth2 时，连接器会将其 OAuth2 客户端配置重用于 IRC，在
默认情况下。这避免了在两个端点接受相同客户端身份时重复配置。等效的
显式设置是：

```properties
spark.sql.gravitino.iceberg.reuseOAuth2    true
```

即使 IRC 作为 Gravitino 辅助服务运行，Gravitino 和 IRC 也可能使用不同的 OAuth2 客户端。
使用 IRC 专属的 Iceberg REST 属性覆盖任何复用的值；未指定的值将继续来自
Gravitino 客户端配置：

```properties
# Gravitino metadata API client
spark.sql.gravitino.authType                  oauth2
spark.sql.gravitino.oauth2.serverUri           https://identity.example.com
spark.sql.gravitino.oauth2.tokenPath           /oauth/token
spark.sql.gravitino.oauth2.credential          <gravitino-client-id>:<gravitino-client-secret>
spark.sql.gravitino.oauth2.scope               gravitino

# IRC data-plane client override
spark.sql.gravitino.iceberg.rest.credential   <irc-client-id>:<irc-client-secret>
spark.sql.gravitino.iceberg.rest.scope        iceberg
```

IRC 属性按字段优先。当重用 Gravitino
配置且默认完全没有 IRC 特定的覆盖时，此验证也适用：如果重用的配置本身
不完整，目录初始化将失败并识别出缺失的属性。设置
`spark.sql.gravitino.iceberg.reuseOAuth2=false` 当提供完整的、独立的 IRC 认证
配置时，或者当 IRC 不需要 OAuth2 时。

:::caution
Spark 的 UI 会对属性名称匹配 `secret|password|token` 的环境变量值进行脱敏处理，但这不
匹配 `credential`。`spark.sql.gravitino.oauth2.credential` 和 `spark.sql.gravitino.iceberg.rest.credential` 都
在 Spark UI 的环境页面上以明文显示；请设置 `spark.redaction.regex` 来同时匹配
`credential`，如果担心此问题。
:::

由于代售凭据仅由 Iceberg 的原生 `FileIO` 实现所使用，请确保
下面 [Storage](#storage) 中列出的仓库存储 jar 包位于 Spark 类路径上；连接器
会从仓库位置的 scheme（`s3`/`s3a`/`s3n`、`gs`、
`abfs`/`abfss`/`wasb`/`wasbs`、`oss`）自动推导出 `io-impl`，除非已在 catalog 上显式设置了 `io-impl`。

## 存储

Spark connector 可以自动将 Gravitino catalog 中的存储属性转换为 Spark Iceberg connector，对于 `S3`、`ADLS`、`OSS`、`GCS` 无需额外配置。

### S3

下载与 Iceberg 运行时版本相匹配的 [Iceberg AWS bundle](https://mvnrepository.com/artifact/org.apache.iceberg/iceberg-aws-bundle)
并将其放置在 Spark driver 和 executor 的 classpaths 中。这是
`S3FileIO` 所必需的，即使 Spark 镜像已经包含了 Hadoop S3A 使用的 AWS SDK v1；
`S3FileIO` 使用来自 `iceberg-aws-bundle` 的 AWS SDK v2。如果缺少该 bundle，初始化可能会失败并抛出
`NoClassDefFoundError`，该错误不会直接指出缺少的 bundle。

### OSS

请下载 [Aliyun OSS SDK](https://gosspublic.alicdn.com/sdks/java/aliyun_java_sdk_3.10.2.zip) 并将 `aliyun-sdk-oss-3.10.2.jar`、`hamcrest-core-1.1.jar`、`jdom2-2.0.6.jar` 复制到 Spark 的 classpath 中。

### GCS

请确保 Spark 可以访问凭证文件，例如使用 `export GOOGLE_APPLICATION_CREDENTIALS=/xx/application_default_credentials.json`，并下载 [Iceberg GCP bundle](https://mvnrepository.com/artifact/org.apache.iceberg/iceberg-gcp-bundle) 并将其放置在 Spark 的 classpath 中。

### ADLS

请下载 [Iceberg Azure bundle](https://mvnrepository.com/artifact/org.apache.iceberg/iceberg-azure-bundle) 并将其放置在 Spark 的 classpath 中。

### 其他存储

添加格式为 `spark.sql.catalog.${iceberg_catalog_name}.{configuration_key}` 的自定义配置。此外，请将实现 `FileIO` 的相应 jar 包放置在 Spark 的 classpath 中。
