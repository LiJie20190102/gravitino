---
sidebar_label: Spark
title: 将 Spark 连接到 Iceberg REST
---
## 简介

Apache Gravitino 暴露了一个 [Iceberg REST catalog](../iceberg-rest-service.md) 端点，任何
兼容 Iceberg 的引擎均可直接连接该端点，无需安装特定于 Gravitino 的
连接器插件。本页介绍如何配置 Apache Spark 以使用 Gravitino 的 Iceberg REST
(IRC) 端点。

:::note
此集成使用标准的 Apache Iceberg REST catalog 规范。Gravitino 对所有
IRC 请求强制执行其完整的访问控制模型。从引擎传播用户身份已
计划在未来的版本中实现；当前请求使用在
Spark 配置中提供的凭据进行授权。
:::

## 前提条件

- 启用 Iceberg REST 服务运行的 Apache Gravitino。参见
  [Iceberg REST catalog service](../iceberg-rest-service.md) 了解设置说明。
- Spark 环境可访问 Gravitino IRC 端点。默认端口为 `9001`。
- Spark 环境中具备以下 JAR 文件：
  - `iceberg-spark-runtime-3.5_2.12-1.7.1.jar`
  - `hadoop-aws-3.3.4.jar`
  - `aws-bundle-2.29.38.jar`

本页使用 **Spark 3.5.3** 和 **Iceberg 1.7.1**。对于其他版本，请确保
Spark、Scala 和 Iceberg 运行时版本之间的兼容性。

## 配置

`spark-defaults.conf` 是 Spark 的持久化配置文件。此处设置的属性会
自动应用到每个 Spark 会话，无需命令行标志。该文件位于：

```
$SPARK_HOME/conf/spark-defaults.conf
```

如果文件尚不存在，请复制模板：

```bash
cp $SPARK_HOME/conf/spark-defaults.conf.template $SPARK_HOME/conf/spark-defaults.conf
```

### 简单认证

将以下内容添加到 `$SPARK_HOME/conf/spark-defaults.conf`：

```properties
# Iceberg extensions
spark.sql.extensions                                    org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

# Gravitino IRC catalog
spark.sql.catalog.gravitino_irc                         org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.gravitino_irc.type                    rest
spark.sql.catalog.gravitino_irc.uri                     http://<gravitino-host>:9001/iceberg

# S3 FileIO
spark.sql.catalog.gravitino_irc.io-impl                 org.apache.iceberg.aws.s3.S3FileIO
spark.sql.catalog.gravitino_irc.s3.region               us-east-1
spark.sql.catalog.gravitino_irc.s3.access-key-id        <access-key>
spark.sql.catalog.gravitino_irc.s3.secret-access-key    <secret-key>

# Hadoop S3A (for s3a:// paths)
spark.hadoop.fs.s3a.impl                                org.apache.hadoop.fs.s3a.S3AFileSystem

# Set as default catalog (optional)
spark.sql.defaultCatalog                                gravitino_irc
```

:::note
`gravitino_irc` 是 Spark 内部使用的 catalog 标识符。它映射到 Gravitino IRC 端点
通过 `uri` 属性。可以使用任何偏好的标识符。S3 凭据也可以通过
环境变量 (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) 或 IAM
实例配置文件提供，在此情况下可以省略显式凭据行。
:::

### 基本认证

如果 Gravitino 使用 [本地用户和组](../security/local-users-and-groups.md) 进行基本认证，
请将认证属性添加到 `$SPARK_HOME/conf/spark-defaults.conf`：

```properties
# Iceberg extensions
spark.sql.extensions                                      org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

# Gravitino IRC catalog
spark.sql.catalog.gravitino_irc                           org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.gravitino_irc.type                      rest
spark.sql.catalog.gravitino_irc.uri                       http://<gravitino-host>:9001/iceberg

# Basic authentication
spark.sql.catalog.gravitino_irc.rest.auth.type            basic
spark.sql.catalog.gravitino_irc.rest.auth.basic.username  <username>
spark.sql.catalog.gravitino_irc.rest.auth.basic.password  <password>

# S3 FileIO
spark.sql.catalog.gravitino_irc.io-impl                   org.apache.iceberg.aws.s3.S3FileIO
spark.sql.catalog.gravitino_irc.s3.region                 us-east-1
spark.sql.catalog.gravitino_irc.s3.access-key-id          <access-key>
spark.sql.catalog.gravitino_irc.s3.secret-access-key      <secret-key>

# Hadoop S3A (for s3a:// paths)
spark.hadoop.fs.s3a.impl                                  org.apache.hadoop.fs.s3a.S3AFileSystem

# Set as default catalog (optional)
spark.sql.defaultCatalog                                  gravitino_irc
```

### OAuth2 认证

如果 Gravitino 配置了 OAuth2，请将认证属性添加到同一个
`$SPARK_HOME/conf/spark-defaults.conf` 文件：

```properties
# Iceberg extensions
spark.sql.extensions                                    org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

# Gravitino IRC catalog
spark.sql.catalog.gravitino_irc                         org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.gravitino_irc.type                    rest
spark.sql.catalog.gravitino_irc.uri                     http://<gravitino-host>:9001/iceberg

# OAuth2 authentication
spark.sql.catalog.gravitino_irc.rest.auth.type          oauth2
spark.sql.catalog.gravitino_irc.rest.auth.oauth2.token  <your-token>

# S3 FileIO
spark.sql.catalog.gravitino_irc.io-impl                 org.apache.iceberg.aws.s3.S3FileIO
spark.sql.catalog.gravitino_irc.s3.region               us-east-1
spark.sql.catalog.gravitino_irc.s3.access-key-id        <access-key>
spark.sql.catalog.gravitino_irc.s3.secret-access-key    <secret-key>

# Hadoop S3A (for s3a:// paths)
spark.hadoop.fs.s3a.impl                                org.apache.hadoop.fs.s3a.S3AFileSystem

# Set as default catalog (optional)
spark.sql.defaultCatalog                                gravitino_irc
```

参见 [如何进行认证](../security/how-to-authenticate.md) 了解 Gravitino 认证
配置选项。

:::tip 本地开发
在本地开发中，可以使用 [MinIO](https://min.io) 作为兼容 S3 的存储后端。
将 S3 FileIO 部分替换为：

```properties
spark.sql.catalog.gravitino_irc.io-impl                 org.apache.iceberg.aws.s3.S3FileIO
spark.sql.catalog.gravitino_irc.s3.endpoint             http://<minio-host>:9000
spark.sql.catalog.gravitino_irc.s3.path-style-access    true
spark.sql.catalog.gravitino_irc.s3.access-key-id        <minio-access-key>
spark.sql.catalog.gravitino_irc.s3.secret-access-key    <minio-secret-key>
spark.hadoop.fs.s3a.impl                                org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.endpoint                            http://<minio-host>:9000
spark.hadoop.fs.s3a.path.style.access                   true
spark.hadoop.fs.s3a.connection.ssl.enabled              false
```

参见 [gravitino-irc-quickstart](https://github.com/markhoerth/gravitino-irc-quickstart) 获取
使用 MinIO 的完整本地开发环境。
:::

### 凭证分发

如果 Gravitino 配置了凭证分发，请添加以下内容以在客户端启用该功能：

```properties
spark.sql.catalog.gravitino_irc.header.X-Iceberg-Access-Delegation    vended-credentials
```

有关服务端配置，请参见 [凭证分发](../iceberg-rest-service.md#credential-vending)。

:::note
对于不由 Gravitino 管理的存储，属性不会自动从服务器
传输到客户端。传递自定义属性以显式初始化 FileIO：

```properties
spark.sql.catalog.gravitino_irc.<configuration-key>    <property-value>
```
:::

## 启动 Spark

一旦 `spark-defaults.conf` 配置就绪，即可正常启动 Spark 会话。Gravitino IRC
catalog 可立即使用，无需任何额外标志。

### Spark Shell (Scala)

```bash
$SPARK_HOME/bin/spark-shell
```

### Spark SQL

```bash
$SPARK_HOME/bin/spark-sql
```

### PySpark

```bash
$SPARK_HOME/bin/pyspark
```

## 示例

### 列出命名空间

```sql
SHOW NAMESPACES IN gravitino_irc;
```

### 列出表

```sql
SHOW TABLES IN gravitino_irc.<namespace>;
```

### 查询表

```sql
SELECT * FROM gravitino_irc.<namespace>.<table> LIMIT 10;
```

### 创建表

```sql
CREATE TABLE gravitino_irc.<namespace>.new_table (
  id INT,
  name STRING,
  created_at TIMESTAMP
) USING iceberg;
```

### 插入数据

```sql
INSERT INTO gravitino_irc.<namespace>.new_table VALUES (1, 'example', current_timestamp());
```

## Gravitino 连接器 vs. Iceberg REST

| 特性                       | Gravitino 引擎连接器            | Iceberg REST                 |
|:-------------------------|:----------------------------|:------------------------------|
| 需要引擎插件               | 是                          | 否                            |
| Gravitino 访问控制           | 是                          | 是                            |
| 支持的引擎                | Trino, Spark, Flink, Daft   | 任何兼容 Iceberg 的引擎             |
| 凭证分发                     | 不定                         | Yes (S3, GCS, OSS, ADLS)      |

## 相关

- [Iceberg REST catalog service](../iceberg-rest-service.md)
- [通过 Iceberg REST 连接 Trino](./trino.md)
- [通过 Iceberg REST 连接 Flink](./flink.md)
- [Spark Gravitino 连接器](../spark-connector/spark-connector.md)