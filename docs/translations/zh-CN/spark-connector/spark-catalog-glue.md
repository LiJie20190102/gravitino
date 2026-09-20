---
title: "Spark Connector: Glue Catalog"
slug: "/spark-connector/spark-catalog-glue"
keyword: "spark connector glue catalog aws"
license: "This software is licensed under the Apache License version 2."
---

## 概述

借助 Apache Gravitino Spark 连接器，访问 AWS Glue Data Catalog 中的数据或管理元数据变得十分简单，从而实现跨 Glue 目录的无缝联邦查询。

## 能力

支持 SparkSQL 中的大多数 DDL 和 DML 操作，但不包括以下操作：

- 函数操作（支持 Gravitino UDF，参见 [Spark 连接器 - 用户定义函数](spark-connector-udf.md)）
- 分区操作
- 视图操作
- `LOAD` 子句
- `CREATE TABLE LIKE` 子句
- `TRUNCATE TABLE` 子句

## 表格格式支持

Glue 目录支持在单个数据库中使用混合表格式：

- **Hive 格式的表** (PARQUET、ORC、TEXTFILE 等)：使用 AWS Glue Data Catalog Hive 客户端路由到 HiveTableCatalog
- **Iceberg 格式的表**：路由到 Iceberg 的 SparkCatalog (GlueCatalog) 以进行 I/O

表路由基于 Glue 表参数中的 `table-format` 属性。带有 `table-format=ICEBERG` 的表将被委派给 Iceberg 后端。

## 要求

- 对 AWS Glue API 和 Amazon S3 的网络访问
- 具有必要的 Glue 和 S3 权限的 AWS IAM 凭证。
有关所需策略，请参见 [AWS IAM 权限](../aws-glue-catalog.md#aws-iam-permissions)
- Apache Spark 3.5
- 已打补丁的 Hive 和 AWS Glue 客户端 JAR 包（参见 [设置](#setup)；在 Amazon EMR 上预装）
- Spark classpath 上的 `iceberg-spark-runtime` 和 `iceberg-aws-bundle` JAR 包，用于 Iceberg 表支持（在 Amazon EMR 上不需要）

:::note
该连接器在 Spark 4 上也能解析 Glue 目录类，但是该目录所需的打过补丁的 Hive JAR 包
仅为 Spark 3 发布，因此 Glue 仅在 Spark 3.5 上进行了验证。
:::

## 设置

Spark 自带的 Hive 2.3.9 不包含 `HiveMetaStoreClientFactory` 接口
（由 [HIVE-12679](https://issues.apache.org/jira/browse/HIVE-12679) 添加）AWS Glue 客户端
需要的。将自带的 Hive JAR 包替换为与
Glue 客户端打包在一起的修补版本。

:::note
在 AWS 托管的 Spark 环境（例如 Amazon EMR）中，Hive 库已经过修补，且
AWS Glue Data Catalog 客户端已预安装。跳过下面的步骤 1 和 2。
有关 Amazon EMR 的完整演练，请参阅[在 Amazon EMR 上部署](#deploy-on-amazon-emr)。
:::

对于非 EMR 环境下的 Iceberg 表支持，还需将以下 JAR 包放入 Spark classpath 中：

- `iceberg-spark-runtime` — 请参阅 [Iceberg catalog](spark-catalog-iceberg.md#preparation) 以获取与您的 Spark 版本相匹配的版本
- `iceberg-aws-bundle` — 匹配相同的 Iceberg 版本，提供 `GlueCatalog` 所需的 AWS SDK v2 依赖项

```bash
# Example for Spark 3.5 with Iceberg 1.6.1
curl -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.6.1/iceberg-spark-runtime-3.5_2.12-1.6.1.jar
curl -O https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/1.6.1/iceberg-aws-bundle-1.6.1.jar
```

:::note
在 Amazon EMR 上，集群中已预装 AWS SDK v2。不需要 `iceberg-aws-bundle`。
有关特定于 EMR 的 JAR 设置，请参阅[在 Amazon EMR 上部署](#deploy-on-amazon-emr)。
:::

[spark-hive-glue-libs](https://github.com/datastrato/spark-hive-glue-libs) 提供了预构建的 JARs
其中包含已打补丁的 Hive 2.3.10 以及适用于 Spark 的 AWS Glue Data Catalog 客户端。

### 步骤 1：下载 JARs

从 `spark3/glue-3.4.0` 目录下载所有 JAR 文件，该目录属于
[spark-hive-glue-libs](https://github.com/datastrato/spark-hive-glue-libs)。
目录名称指的是 Glue 客户端版本 (3.4.0)，而不是 Spark 版本；
这些 JAR 文件与 Spark 3.5 兼容。

```bash
mkdir -p /opt/glue-hive-jars
curl -fsSL "https://api.github.com/repos/datastrato/spark-hive-glue-libs/contents/spark3/glue-3.4.0" \
  | jq -r '.[] | select(.name | endswith(".jar")) | .download_url' \
  | while read -r url; do
      curl -fL "$url" -o "/opt/glue-hive-jars/$(basename "$url")"
    done
```

或者，直接从
[spark-hive-glue-libs 仓库](https://github.com/datastrato/spark-hive-glue-libs/tree/main/spark3/glue-3.4.0) 下载 JARs

### 步骤 2：配置 Spark

在启动 Spark 时添加以下配置：

```bash
spark-submit \
  --conf spark.sql.hive.metastore.version=2.3.10 \
  --conf spark.sql.hive.metastore.jars=path \
  --conf spark.sql.hive.metastore.jars.path=/opt/glue-hive-jars/* \
  --conf spark.sql.hive.metastore.sharedPrefixes=com.amazonaws,org.apache.thrift,org.slf4j,com.google.common \
  ...
```

:::note
`spark.sql.hive.metastore.jars=path` 配置指示 Spark 加载 Hive metastore
客户端从指定目录加载，而不是其内置的 Hive JAR 包。
该目录中的 AWS SDK JAR 包在 Spark 的 `IsolatedClientLoader` 中加载，以防止版本
与 `hadoop-aws` 发生冲突。
:::

## 在 Amazon EMR 上部署

Amazon EMR 7.x 预装了修补后的 Hive 库和 AWS Glue Data Catalog 客户端，
因此无需 [设置](#setup) 中所述的手动 JAR 设置。

### 先决条件

- AWS CLI 已配置具有 `AmazonEMRFullAccessPolicy_v2` 和 EC2 权限的 IAM 用户或角色
- 具备 Glue 读取和 S3 读写权限的 EC2 实例配置文件（`EMR_EC2_DefaultRole`）
- 用于表存储的 S3 存储桶（例如 `s3://my-bucket/warehouse`）
- 可从 EMR 集群访问的 Gravitino 服务器

### 步骤 1：创建 EMR 集群

```bash
aws emr create-cluster \
  --name "gravitino-glue" \
  --release-label emr-7.2.0 \
  --applications Name=Spark \
  --instance-type m5.xlarge \
  --instance-count 1 \
  --use-default-roles \
  --region <your-region> \
  --tags 'for-use-with-amazon-emr-managed-policies=true' \
  --configurations '[{"Classification":"spark-hive-site","Properties":{"hive.metastore.client.factory.class":"com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"}}]' \
  --ec2-attributes KeyName=<your-key-pair>
```

`spark-hive-site` 配置将 Spark 的 Hive 元存储客户端路由到 AWS Glue 数据
目录。`for-use-with-amazon-emr-managed-policies=true` 标签是
`AmazonEMRFullAccessPolicy_v2` 所必需的。

### 步骤 2：将 JAR 添加到 Spark classpath

按照 [Spark connector setup](spark-connector.md#usage) 获取
`gravitino-spark-connector-runtime-3.5` JAR 包。在 EMR 上，请将其放在 `/usr/lib/spark/jars/` 中，而不是
自定义路径中——该目录会自动加入 Spark 的系统 classpath 中。使用 `--jars` 或
`--driver-class-path` 是不够的，因为 Gravitino 插件 classloader 必须在
Spark 启动时找到该 JAR 包。

为了支持 Iceberg 表，还需将 Iceberg Spark 运行时 JAR 添加到 `/usr/lib/spark/jars/`：

- [iceberg-spark-runtime-3.5_2.12](https://mvnrepository.com/artifact/org.apache.iceberg/iceberg-spark-runtime-3.5_2.12) 版本 **1.10.1**

:::warning
使用 `iceberg-spark-runtime` 版本 **1.10.1**，而不是 1.11.0。EMR 7.2.0 自带 AWS SDK v2
2.23.18，其中不包含 `RetryMode.ADAPTIVE_V2`。Iceberg 1.11.0 引用了此字段
在运行时，并抛出 `NoSuchFieldError: ADAPTIVE_V2`。
:::

### 步骤 3：创建 Glue 目录

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "name": "glue_catalog",
    "type": "RELATIONAL",
    "provider": "glue",
    "properties": {
      "aws-region": "<your-region>",
      "warehouse": "s3://<your-bucket>/warehouse"
    }
  }' http://<gravitino-host>:8090/api/metalakes/<metalake>/catalogs
```

当在 EMR 上使用 EC2 实例角色运行时，AWS 凭证会被自动获取 —
不需要静态的 `aws-access-key-id` 或 `aws-secret-access-key`。

### 步骤 4：提交 Spark 作业

:::warning
使用 `spark-submit`，而不是 `spark-sql`。`spark-sql` CLI 不会以正确的顺序初始化 Gravitino
插件类加载器，因此已注册的 catalog 将不会出现在 `SHOW CATALOGS` 中。
:::

通过 `spark-submit` 传递 Gravitino 插件配置：

```bash
spark-submit --master yarn \
  --conf spark.plugins=org.apache.gravitino.spark.connector.plugin.GravitinoSparkPlugin \
  --conf spark.sql.gravitino.uri=http://<gravitino-host>:8090 \
  --conf spark.sql.gravitino.metalake=<metalake> \
  --conf spark.sql.gravitino.enableIcebergSupport=true \
  --conf spark.sql.catalogImplementation=hive \
  --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  --conf spark.hadoop.fs.s3.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  your_job.py
```

以下 PySpark 代码片段展示了如何在 Glue 目录中查询 Hive 格式和 Iceberg 表：

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

spark.sql("USE glue_catalog.mydb")

# Query a Hive-format table
spark.sql("SELECT * FROM employees WHERE department = 'Engineering'").show()

# Query an Iceberg table
spark.sql("SELECT * FROM orders WHERE order_ts >= DATE '2024-01-01'").show()

spark.stop()
```

## 创建目录

使用 Gravitino REST API 或 Gravitino CLI 创建 Glue catalog：

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "glue_catalog",
  "type": "RELATIONAL",
  "provider": "glue",
  "properties": {
    "aws-region": "us-east-1",
    "aws-access-key-id": "<your-access-key-id>",
    "aws-secret-access-key": "<your-secret-access-key>",
    "warehouse": "s3://my-bucket/warehouse"
  }
}' http://gravitino-host:8090/api/metalakes/{metalake}/catalogs
```

有关 Glue catalog 属性的更多信息，请参阅 [AWS Glue catalog](../aws-glue-catalog.md)。

## SQL 示例

```sql
-- Suppose glue_catalog is the Glue catalog name managed by Gravitino
USE glue_catalog;

CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

-- Create a Hive-format Parquet table
CREATE TABLE IF NOT EXISTS employees (
    id INT,
    name STRING,
    age INT
)
PARTITIONED BY (department STRING)
STORED AS PARQUET;

DESC TABLE EXTENDED employees;

INSERT OVERWRITE TABLE employees PARTITION(department='Engineering')
VALUES (1, 'John Doe', 30), (2, 'Jane Smith', 28);

SELECT * FROM employees WHERE department = 'Engineering';

-- Create an Iceberg table partitioned by day
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT,
    customer STRING,
    amount DECIMAL(10, 2),
    order_ts TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(order_ts));

INSERT INTO orders VALUES (1, 'alice', 99.99, TIMESTAMP '2024-01-01 00:00:00');

SELECT * FROM orders WHERE order_ts >= DATE '2024-01-01';
```


## 目录属性

Gravitino Spark 连接器将以下 catalog 属性名称映射到 Spark Hive/Iceberg 连接器配置。

| Gravitino 目录属性中的属性名称 | Spark Hive 连接器配置 | 描述                                 |
|-----------------------------------------------|------------------------------------|---------------------------------------------|
| `aws-region`                                  | `aws.region`                       | Glue Data Catalog 的 AWS 区域            |
| `aws-glue-catalog-id`                         | `aws.glue.catalog.id`              | 拥有 Glue catalog 的 12 位 AWS 账户 ID |
| `aws-glue-endpoint`                           | `aws.glue.endpoint`                | 自定义 Glue endpoint URL                    |
| `warehouse`                                   | (Iceberg) `warehouse`              | Iceberg 表的基础存储路径        |

对于 Iceberg 表，Gravitino 属性映射到 Iceberg GlueCatalog 配置：

| Gravitino 属性      | Iceberg GlueCatalog 属性          | 描述                               |
|-------------------------|---------------------------------------|-------------------------------------------|
| `aws-region`            | `client.region`                       | AWS 区域                                |
| `aws-glue-catalog-id`   | `glue.id`                             | Glue 目录 ID                           |
| `aws-glue-endpoint`     | `glue.endpoint`                       | Glue 端点 URL                         |
| `aws-access-key-id`     | `client.credentials-provider.*`      | AWS 访问密钥（通过自定义提供程序）      |
| `aws-secret-access-key` | `client.credentials-provider.*`      | AWS 秘密密钥（通过自定义提供程序）      |

带有 `spark.bypass.` 前缀的 Gravitino catalog 属性名称将直接传递给 Spark Hive connector。例如，使用 `spark.bypass.hive.exec.dynamic.partition.mode` 将 `hive.exec.dynamic.partition.mode` 传递给 Spark Hive connector。

## S3 存储

使用 AWS S3 时，通过 Spark 配置将 S3 凭证配置为全局 Hadoop 属性：

```bash
spark-submit \
  --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  --conf spark.hadoop.fs.s3a.access.key=<your-access-key> \
  --conf spark.hadoop.fs.s3a.secret.key=<your-secret-key> \
  --conf spark.hadoop.fs.s3a.endpoint.region=<your-region> \
  --conf spark.hadoop.fs.s3.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  --conf spark.hadoop.fs.s3.access.key=<your-access-key> \
  --conf spark.hadoop.fs.s3.secret.key=<your-secret-key> \
  ...
```

:::note
必须配置 `fs.s3a.*` 和 `fs.s3.*`。AWS Glue Data Catalog Hive 客户端存储表
位置时使用 `s3://` 方案，而 Spark 使用 `s3a://` 进行 S3 访问。将这两种方案映射到
`S3AFileSystem` 可确保 Hive 格式的表是可读的。
:::

或者，在 catalog 属性中使用 `spark.bypass.` 前缀来传递 S3 配置：

```json
{
  "properties": {
    "aws-region": "us-east-1",
    "warehouse": "s3a://my-bucket/warehouse",
    "spark.bypass.fs.s3a.access.key": "<your-access-key>",
    "spark.bypass.fs.s3a.secret.key": "<your-secret-key>"
  }
}
```

:::note
使用 S3 存储时，请确保你的 Spark classpath 中包含 AWS Java SDK 和 Hadoop AWS JARs。
:::
