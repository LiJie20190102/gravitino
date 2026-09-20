---
sidebar_label: Flink
title: 将 Flink 连接到 Iceberg REST
---
## 简介

Apache Gravitino 暴露了一个 [Iceberg REST catalog](../iceberg-rest-service.md) 端点，任何
兼容 Iceberg 的引擎都可以直接连接——无需安装 Gravitino 专用的
连接器插件。本页介绍如何配置 Apache Flink 使用 Gravitino 的 Iceberg REST
(IRC) 端点。

:::note
此集成使用标准的 Apache Iceberg REST catalog 规范。Gravitino 对所有
IRC 请求实施完整的访问控制模型。
:::

## 前置条件

- Apache Gravitino 已启动并启用 Iceberg REST 服务。参见
  [Iceberg REST catalog service](../iceberg-rest-service.md) 了解配置说明。
- Flink 环境可访问 Gravitino IRC 端点。默认端口为 `9001`。
- Flink classpath 中需包含以下 JAR 文件：
  - `iceberg-flink-runtime-1.18-1.7.1.jar`（Flink 1.19 使用 `iceberg-flink-runtime-1.19-1.7.1.jar`）
  - `iceberg-aws-bundle-1.7.1.jar`
  - `flink-shaded-hadoop-2-uber.jar`

本页使用 **Flink 1.18** 和 **Iceberg 1.7.1**。

:::note
与 Spark 和 Trino 不同，Flink 要求在 catalog
定义中指定 S3 连接属性，而非在单独的配置文件中指定。
:::

## 配置

Flink 使用集群配置文件 (`flink-conf.yaml`) 进行通用设置。Iceberg
catalog 通过 `CREATE CATALOG` SQL 语句按会话注册。

### flink-conf.yaml

在 `$FLINK_HOME/conf/flink-conf.yaml` 中设置批执行模式和结果显示方式：

```yaml
execution.runtime-mode: batch
sql-client.execution.result-mode: tableau
```

:::tip
`tableau` 模式在终端中内联打印查询结果。若不设置，Flink SQL Client 会
以全屏分页器方式打开结果。
:::

### 启动 Flink SQL Client

```bash
$FLINK_HOME/bin/sql-client.sh
```

## 注册 Catalog

在 Flink SQL Client 提示符下，运行以下 `CREATE CATALOG` 语句。将
`<gravitino-host>` 替换为 Gravitino 服务器地址，并提供 S3 凭证。

### 无认证

```sql
CREATE CATALOG gravitino_irc WITH (
  'type'                 = 'iceberg',
  'catalog-type'         = 'rest',
  'uri'                  = 'http://<gravitino-host>:9001/iceberg',
  'io-impl'              = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.region'            = 'us-east-1',
  's3.access-key-id'     = '<access-key>',
  's3.secret-access-key' = '<secret-key>'
);
```

### Basic 认证

如果 Gravitino 使用 [本地用户和组](../security/local-users-and-groups.md) 进行 Basic
认证，请在 catalog 上设置认证属性：

```sql
CREATE CATALOG gravitino_irc WITH (
  'type'                     = 'iceberg',
  'catalog-type'             = 'rest',
  'uri'                      = 'http://<gravitino-host>:9001/iceberg',
  'rest.auth.type'           = 'basic',
  'rest.auth.basic.username' = '<username>',
  'rest.auth.basic.password' = '<password>',
  'io-impl'                  = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.region'                = 'us-east-1',
  's3.access-key-id'         = '<access-key>',
  's3.secret-access-key'     = '<secret-key>'
);
```

### OAuth2 认证

```sql
CREATE CATALOG gravitino_irc WITH (
  'type'                 = 'iceberg',
  'catalog-type'         = 'rest',
  'uri'                  = 'http://<gravitino-host>:9001/iceberg',
  'rest.auth.type'       = 'oauth2',
  'rest.auth.oauth2.token' = '<your-token>',
  'io-impl'              = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.region'            = 'us-east-1',
  's3.access-key-id'     = '<access-key>',
  's3.secret-access-key' = '<secret-key>'
);
```

参见 [如何认证](../security/how-to-authenticate.md) 了解 Gravitino 认证
配置选项。

:::note
catalog 注册在 SQL Client 会话期间持续有效。每次启动新会话时必须重新
运行 `CREATE CATALOG`。
:::

:::tip 本地开发
使用 MinIO 进行本地开发时，将以下 S3 属性添加到 catalog 定义中：

```sql
  's3.endpoint'          = 'http://<minio-host>:9000',
  's3.path-style-access' = 'true',
```

参见 [gravitino-irc-quickstart](https://github.com/markhoerth/gravitino-irc-quickstart) 了解使用 MinIO 的
完整本地开发环境。
:::

## 示例

### 使用 Catalog

```sql
USE CATALOG gravitino_irc;
```

### 列出数据库

```sql
SHOW DATABASES;
```

### 列出表

```sql
SHOW TABLES IN <namespace>;
```

### 查询表

```sql
SELECT * FROM <namespace>.<table>;
```

### 创建表

```sql
CREATE TABLE gravitino_irc.<namespace>.new_table (
  id INT,
  name STRING,
  created_at TIMESTAMP
);
```

### 插入数据

```sql
INSERT INTO gravitino_irc.<namespace>.new_table VALUES (1, 'example', CURRENT_TIMESTAMP);
```

## Gravitino 连接器 vs. Iceberg REST

| 特性                      | Gravitino 引擎连接器        | Iceberg REST                  |
|:-------------------------|:----------------------------|:------------------------------|
| 需要引擎插件             | 是                          | 否                            |
| Gravitino 访问控制       | 是                          | 是                            |
| 支持的引擎              | Trino、Spark、Flink、Daft   | 任何兼容 Iceberg 的引擎       |
| 凭证分发 (credential vending) | 视情况而定            | 是 (S3、GCS、OSS、ADLS)       |

## 相关内容

- [Iceberg REST catalog service](../iceberg-rest-service.md)
- [通过 Iceberg REST 连接 Spark](./spark.md)
- [通过 Iceberg REST 连接 Trino](./trino.md)
- [Flink Gravitino 连接器](../flink-connector/flink-connector.md)