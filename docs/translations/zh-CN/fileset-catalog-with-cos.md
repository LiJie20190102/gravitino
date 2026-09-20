---
slug: /fileset-catalog-with-cos
keyword: Fileset catalog COS
license: This software is licensed under the Apache License version 2.
title: 使用 COS 的 Fileset Catalog
---
## 简介

本页介绍如何将 fileset 数据存储在腾讯云 COS 中，同时由 Gravitino 管理元数据，
以及如何通过 Gravitino 虚拟文件系统（GVFS）读写该数据。

本页所有内容均针对腾讯云 COS。fileset 模型本身、各存储后端共享的属性，以及属性
从 catalog 到 schema 再到 fileset 的继承方式，已在
[Fileset Catalog](./fileset-catalog.md) 中说明。

示例按顺序执行，全文使用相同的名称：metalake `metalake`、catalog
`cos_catalog`、schema `cos_schema`、fileset `example_fileset`，服务器 URL 为
`http://localhost:8090`。请替换为实际值。

## 前置条件

1. 下载 [`gravitino-tencent-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-tencent-bundle) 文件。
2. 将其放置在 fileset catalog 的 classpath 下：`${GRAVITINO_HOME}/catalogs/fileset/libs/`。
3. 启动 Gravitino 服务器：

```bash
${GRAVITINO_HOME}/bin/gravitino-server.sh start
```

bundle jar 加入 classpath 后，catalog 会自动加载腾讯云 COS 文件系统提供者。
已弃用的 `filesystem-providers` 和 `default-filesystem-provider` catalog
属性无需再设置。

## 腾讯云 COS 属性

以下属性是在共享的 [catalog 属性](./fileset-catalog.md#catalog-properties) 之外需要设置的。
GVFS 客户端也需要相同的值，因此在此一并列出——注意 Python 客户端使用
下划线拼写，而 catalog 和 Java 客户端使用连字符。


| Catalog 和 Java 客户端    | Python 客户端              | 描述                                                                                                                                                                                                                                                                                                                                                                                       | 必需     |
|----------------------------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `cos-region`               | `cos_region`               | COS 存储桶所在地域，例如 `ap-guangzhou` 或 `ap-shanghai`。                                                                                                                                                                                                                                                                                                                            | 是       |
| `cos-endpoint`             | `cos_endpoint`             | COS 服务的端点<em>后缀</em>，映射到 `fs.cosn.bucket.endpoint_suffix`。它是主机后缀，而非 URL——`cos.ap-guangzhou.myqcloud.com`，不是 `https://cos.ap-guangzhou.myqcloud.com`。未设置时，hadoop-cos 会根据 `cos-region` 推导。仅在需要访问非公开端点（如 VPC 端点）时设置。                                                                          | 否       |
| `cos-access-key-id`        | `cos_access_key_id`        | 静态访问密钥 ID，即腾讯云的 `SecretId`。                                                                                                                                                                                                                                                                                                                                               | 是       |
| `cos-secret-access-key`    | `cos_secret_access_key`    | 静态秘密访问密钥，即腾讯云的 `SecretKey`。                                                                                                                                                                                                                                                                                                                                          | 是       |
| `credential-providers`     | (不适用)                      | 凭证提供者类型，以逗号分隔。支持的值为 `cos-secret-key`（由服务器分发的静态 AK/SK）和 `cos-token`（通过 CAM `AssumeRole` 签发的短期 STS 令牌）。设置后即启用凭证分发，客户端不再需要上述凭证。各提供者所需的额外属性参见 [凭证分发](./security/credential-vending.md)。| 否       |
| `cos-role-arn`             | `cos_role_arn`             | Gravitino 服务器在签发 STS 临时凭证时扮演的 CAM 角色 ARN，例如 `qcs::cam::uin/100012345678:roleName/GravitinoCOSAccess`。仅在 `credential-providers` 包含 `cos-token` 时需要。                                                                                                                                                                         | 否       |
| `cos-app-id`               | `cos_app_id`               | 存储桶所有者的腾讯云数字 AppId（存储桶名称的末尾段，例如 `1250000000`）。仅在 `credential-providers` 包含 `cos-token` 时需要，用于在 STS 会话策略中构建资源 ARN。                                                                                                                                                       | 否       |
| `cos-external-id`          | `cos_external_id`          | 可选的 `ExternalId`，传递给 STS `AssumeRole` 调用，用于将角色信任策略锁定到 Gravitino。仅在 `credential-providers` 包含 `cos-token` 时有意义。                                                                                                                                                                                                                     | 否       |
| `cos-token-expire-in-secs` | `cos_token_expire_in_secs` | COS STS 令牌过期时间（秒）。不得超过角色的最大会话时长。仅在 `credential-providers` 包含 `cos-token` 时有意义。默认为 `3600`。                                                                                                                                                                                                                  | 否       |

:::note
`default-filesystem-provider` 和 `filesystem-providers` 已弃用。fileset catalog
会自动加载 classpath 上发现的文件系统提供者，包括内置提供者以及 bundle jar（如
`gravitino-tencent-bundle`）携带的云存储提供者。
:::

:::note
`cos-region` 对 hadoop-cos 是必填项：签名请求、构建默认端点以及
选择正确的 CAM 范围都需要地域信息。即使已设置 `cos-endpoint`，也需保持该项设置。
:::

schema 和 fileset 属性记录在共享页面中：参见
[schema 属性](./fileset-catalog.md#schema-properties) 和
[fileset 属性](./fileset-catalog.md#fileset-properties)。

fileset catalog 将其数据存储在 `location` 下，对于腾讯云 COS，格式类似于
`cosn://my-bucket-1250000000/root`。

## 创建 Catalog、Schema 和 Fileset

### 步骤 1：创建 catalog

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "cos_catalog",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Tencent Cloud COS",
  "properties": {
    "location": "cosn://my-bucket-1250000000/root",
    "cos-region": "ap-guangzhou",
    "cos-endpoint": "cos.ap-guangzhou.myqcloud.com",
    "cos-access-key-id": "access_key",
    "cos-secret-access-key": "secret_key"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoClient gravitinoClient = GravitinoClient
    .builder("http://localhost:8090")
    .withMetalake("metalake")
    .build();

Map<String, String> catalogProperties = ImmutableMap.<String, String>builder()
    .put("location", "cosn://my-bucket-1250000000/root")
    .put("cos-region", "ap-guangzhou")
    .put("cos-endpoint", "cos.ap-guangzhou.myqcloud.com")
    .put("cos-access-key-id", "access_key")
    .put("cos-secret-access-key", "secret_key")
    .build();

Catalog catalog = gravitinoClient.createCatalog("cos_catalog",
    Catalog.Type.FILESET,
    "A fileset catalog backed by Tencent Cloud COS",
    catalogProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
gravitino_client: GravitinoClient = GravitinoClient(
    uri="http://localhost:8090", metalake_name="metalake")

catalog_properties = {
    "location": "cosn://my-bucket-1250000000/root",
    "cos-region": "ap-guangzhou",
    "cos-endpoint": "cos.ap-guangzhou.myqcloud.com",
    "cos-access-key-id": "access_key",
    "cos-secret-access-key": "secret_key",
}

catalog = gravitino_client.create_catalog(name="cos_catalog",
                                          catalog_type=Catalog.Type.FILESET,
                                          provider=None,
                                          comment="A fileset catalog backed by Tencent Cloud COS",
                                          properties=catalog_properties)
```

</TabItem>
</Tabs>

### 步骤 2：创建 schema

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "cos_schema",
  "comment": "A schema in the Tencent Cloud COS fileset catalog",
  "properties": {
    "location": "cosn://my-bucket-1250000000/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/cos_catalog/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("cos_catalog");
SupportsSchemas supportsSchemas = catalog.asSchemas();

Map<String, String> schemaProperties = ImmutableMap.<String, String>builder()
    .put("location", "cosn://my-bucket-1250000000/root/schema")
    .build();

Schema schema = supportsSchemas.createSchema("cos_schema",
    "A schema in the Tencent Cloud COS fileset catalog",
    schemaProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="cos_catalog")
catalog.as_schemas().create_schema(name="cos_schema",
                                   comment="A schema in the Tencent Cloud COS fileset catalog",
                                   properties={"location": "cosn://my-bucket-1250000000/root/schema"})
```

</TabItem>
</Tabs>

### 步骤 3：创建 fileset

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "example_fileset",
  "comment": "This is an example fileset",
  "type": "MANAGED",
  "storageLocation": "cosn://my-bucket-1250000000/root/schema/example_fileset",
  "properties": {
    "k1": "v1"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/cos_catalog/schemas/cos_schema/filesets
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("cos_catalog");
FilesetCatalog filesetCatalog = catalog.asFilesetCatalog();

Map<String, String> filesetProperties = ImmutableMap.<String, String>builder()
    .put("k1", "v1")
    .build();

filesetCatalog.createFileset(
    NameIdentifier.of("cos_schema", "example_fileset"),
    "This is an example fileset",
    Fileset.Type.MANAGED,
    "cosn://my-bucket-1250000000/root/schema/example_fileset",
    filesetProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="cos_catalog")
catalog.as_fileset_catalog().create_fileset(
    ident=NameIdentifier.of("cos_schema", "example_fileset"),
    type=Fileset.Type.MANAGED,
    comment="This is an example fileset",
    storage_location="cosn://my-bucket-1250000000/root/schema/example_fileset",
    properties={"k1": "v1"})
```

</TabItem>
</Tabs>

此时该 fileset 可从任意 GVFS 客户端通过以下地址访问：
`gvfs://fileset/cos_catalog/cos_schema/example_fileset`。

## 访问 Fileset

### Java 客户端 jar 包

每个基于 Java 或 Hadoop 的客户端都需要发布在 Maven Central 上的
`gravitino-filesystem-hadoop3-runtime`，以及腾讯云 COS 文件系统实现。仅后者因
环境而异：

| 环境            | 提供腾讯云 COS 文件系统的 jar 包                                                                                                                                                      |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 未安装 Hadoop    | [`gravitino-tencent-bundle`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-tencent-bundle)，一个打包了 `hadoop-cos` 和腾讯云 COS Java SDK 的 fat jar                  |
| 已有 Hadoop | `hadoop-cos-3.3.0-8.3.23.jar` 和 `cos_api-bundle-5.6.227.jar`，由腾讯云发布在 Maven Central 上，与 `hadoop-aws` 或 `hadoop-aliyun` 不同，不属于 Apache Hadoop 发行版 |

完整的构件列表：

- [`gravitino-tencent-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-tencent-bundle)：
  一个 "fat" jar，包含 `gravitino-tencent` 功能及其所有依赖项，
  如 `hadoop-cos` 和腾讯云 COS Java SDK。在环境中没有预装 Hadoop 时使用。
- [`gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-filesystem-hadoop3-runtime)：
  一个 "fat" jar，打包了 Gravitino 虚拟文件系统客户端，并已包含
  `gravitino-tencent` 功能。Java 和基于 Hadoop 的客户端需要它来访问 Gravitino
  fileset。
- `hadoop-cos-3.3.0-8.3.23.jar` 和 `cos_api-bundle-5.6.227.jar`：腾讯云 COS 访问的
  标准 Hadoop 依赖项，由腾讯云发布在 Maven Central 上，与 `hadoop-aws`
  或 `hadoop-aliyun` 不同，不属于 Apache Hadoop 发行版。在已有 Hadoop
  环境中运行时需自行提供。

```xml
<!-- No Hadoop environment -->
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-tencent-bundle</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-filesystem-hadoop3-runtime</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
```

```xml
<!-- Existing Hadoop environment -->
<dependency>
  <groupId>org.apache.hadoop</groupId>
  <artifactId>hadoop-common</artifactId>
  <version>${HADOOP_VERSION}</version>
</dependency>
<!-- hadoop-cos is published by Tencent Cloud, not by Apache Hadoop. -->
<dependency>
  <groupId>com.qcloud.cos</groupId>
  <artifactId>hadoop-cos</artifactId>
  <version>3.3.0-8.3.23</version>
</dependency>
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-filesystem-hadoop3-runtime</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
```

:::note
不需要瘦包 `gravitino-tencent` jar。其功能已包含在
`gravitino-tencent-bundle` 和 `gravitino-filesystem-hadoop3-runtime` 中。
:::

### GVFS Java 客户端

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration) 之上，设置上表中的
腾讯云 COS 属性。

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
conf.set("cos-region", "ap-guangzhou");
conf.set("cos-endpoint", "cos.ap-guangzhou.myqcloud.com");
conf.set("cos-access-key-id", "access_key");
conf.set("cos-secret-access-key", "secret_key");

Path filesetPath = new Path("gvfs://fileset/cos_catalog/cos_schema/example_fileset/new_dir");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.mkdirs(filesetPath);
```

### Apache Spark

以下示例在已安装 Hadoop 3.3.4 的环境中使用 PySpark 3.5.0。

```bash
pip install pyspark==3.5.0
pip install apache-gravitino==${GRAVITINO_VERSION}
```

```python
import os
from pyspark.sql import SparkSession

# 在 JDK 17 上，还需要添加：
#   --conf "spark.driver.extraJavaOptions=--add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
#   --conf "spark.executor.extraJavaOptions=--add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar,"
    "/path/to/hadoop-cos-3.3.0-8.3.23.jar,"
    "/path/to/cos_api-bundle-5.6.227.jar "
    "--master local[1] pyspark-shell"
)

spark = (SparkSession.builder
    .appName("cos_fileset")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    .config("spark.hadoop.cos-region", "ap-guangzhou")
    .config("spark.hadoop.cos-endpoint", "cos.ap-guangzhou.myqcloud.com")
    .config("spark.hadoop.cos-access-key-id", "access_key")
    .config("spark.hadoop.cos-secret-access-key", "secret_key")
    .config("spark.driver.memory", "2g")
    .config("spark.driver.port", "2048")
    .getOrCreate())

data = [("Alice", 25), ("Bob", 30), ("Cathy", 45)]
spark_df = spark.createDataFrame(data, schema=["Name", "Age"])
gvfs_path = "gvfs://fileset/cos_catalog/cos_schema/example_fileset/people"

spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(gvfs_path)
```

如果 Spark 运行在没有 Hadoop 环境的条件下，仅 jar 列表不同：

```python
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/gravitino-tencent-bundle-${gravitino-version}.jar,"
    "/path/to/gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar "
    "--master local[1] pyspark-shell"
)
```

:::note
某些 Spark 版本在 driver 中需要 Hadoop 环境，且不会加载通过
`--jars` 传入的文件系统实现。如果出现此情况，请将 jar 直接加入 Spark classpath。
:::

### Hadoop fs 命令

1. 在 `${HADOOP_HOME}/etc/hadoop/core-site.xml` 中添加以下内容：

```xml
<property>
  <name>fs.AbstractFileSystem.gvfs.impl</name>
  <value>org.apache.gravitino.filesystem.hadoop.Gvfs</value>
</property>
<property>
  <name>fs.gvfs.impl</name>
  <value>org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem</value>
</property>
<property>
  <name>fs.gravitino.server.uri</name>
  <value>http://localhost:8090</value>
</property>
<property>
  <name>fs.gravitino.client.metalake</name>
  <value>metalake</value>
</property>
<property>
  <name>cos-region</name>
  <value>ap-guangzhou</value>
</property>
<property>
  <name>cos-endpoint</name>
  <value>cos.ap-guangzhou.myqcloud.com</value>
</property>
<property>
  <name>cos-access-key-id</name>
  <value>access_key</value>
</property>
<property>
  <name>cos-secret-access-key</name>
  <value>secret_key</value>
</property>
```

2. 将以下 jar 包加入 Hadoop classpath：

   - `gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`，来自 Maven Central。
   - `hadoop-cos-3.3.0-8.3.23.jar` 和 `cos_api-bundle-5.6.227.jar`，由腾讯云发布在 Maven Central 上，与 `hadoop-aws` 或 `hadoop-aliyun` 不同，不属于 Apache Hadoop 发行版。

3. 访问 fileset：

```shell
${HADOOP_HOME}/bin/hadoop fs -ls gvfs://fileset/cos_catalog/cos_schema/example_fileset
${HADOOP_HOME}/bin/hadoop fs -put /path/to/local/file gvfs://fileset/cos_catalog/cos_schema/example_fileset
```

### GVFS Python 客户端与 pandas

:::note
GVFS Python 客户端尚未提供 COS 存储处理器。无法通过 `gvfs.GravitinoVirtualFileSystem` 或 pandas
`read_csv("gvfs://...")` 读写
COS 支持的 fileset。请使用 GVFS Java 客户端、Spark 或 `hadoop fs` 访问 COS 数据。

此限制不影响 Python `GravitinoClient` 元数据 API。它仍可创建、
查看、更新和删除 COS catalog、schema 和 fileset，如
[创建 Catalog、Schema 和 Fileset](#步骤-1：创建-catalog) 所示。
:::

更多 Java 客户端使用场景，参见
[Gravitino Virtual File System](./how-to-use-gvfs.md)。

## 凭证分发

通过凭证分发，catalog 持有腾讯云 COS 凭证，Gravitino
服务器按请求分发凭证，客户端无需自行持有云密钥。通用机制参见
[Credential Vending](./security/credential-vending.md)。

当前支持的凭证提供者如下：

| 凭证提供者 | 描述                                                                                                                                                                                                                                                                                                                                                                                        | 分发的凭证类型 |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------|
| `cos-secret-key`    | Gravitino 服务器分发 catalog 上配置的静态 `cos-access-key-id` / `cos-secret-access-key`。用于在服务器端集中管理凭证。                                                                                                                                                                                                                         | 静态 AK/SK           |
| `cos-token`         | Gravitino 服务器调用腾讯云 CAM `AssumeRole`，分发短期 STS 三元组（`TmpSecretId` / `TmpSecretKey` / `SessionToken`），范围限定为客户端请求的 fileset 路径。要求 catalog 上配置 `cos-role-arn` 和 `cos-app-id`，且配置在 catalog 上的 AK/SK 所属账户拥有 CAM 权限（`sts:AssumeRole` / `cam:GetFederationToken`）。 | 短期 STS 令牌  |

### 配置 catalog、schema 和 fileset

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "cos_catalog_with_vending",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Tencent Cloud COS with credential vending",
  "properties": {
    "location": "cosn://my-bucket-1250000000/root",
    "cos-region": "ap-guangzhou",
    "cos-endpoint": "cos.ap-guangzhou.myqcloud.com",
    "cos-access-key-id": "access_key",
    "cos-secret-access-key": "secret_key",
    "credential-providers": "cos-secret-key"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

若要改为启用基于 STS 的凭证分发（建议在生产环境中使用，因为 catalog 上的 AK/SK 永远不会离开服务器），请将 `credential-providers` 切换为 `cos-token` 并添加 CAM 角色配置。下方的 AK/SK 是用于调用 `sts:AssumeRole` 的<em>服务端</em>账号；被分发的客户端仅能看到为请求的 fileset 路径签发的短期会话令牌：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "cos-catalog-with-sts-vending",
  "type": "FILESET",
  "comment": "This is a COS fileset catalog with STS credential vending",
  "properties": {
    "location": "cosn://my-bucket-1250000000/root",
    "cos-region": "ap-guangzhou",
    "cos-access-key-id": "server_access_key",
    "cos-secret-access-key": "server_secret_key",
    "credential-providers": "cos-token",
    "cos-role-arn": "qcs::cam::uin/100012345678:roleName/GravitinoCOSAccess",
    "cos-app-id": "1250000000",
    "cos-token-expire-in-secs": "1800"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

:::note
使用 `cos-token` 时，`cos-role-arn` 引用的 CAM 角色 (1) 必须信任 Gravitino 服务器主体（或使用 `cos-external-id` 进行更严格的匹配），并且 (2) 对计划暴露的 bucket 路径拥有 COS 读写权限。Gravitino 通过会话策略进一步缩小分发令牌的权限范围，仅允许访问 fileset 自身的读写位置，因此该角色的权限可以设置为组织策略所允许的最宽范围——实际有效权限是两者的交集。
:::

在凭证分发 catalog 中创建 schema 和 fileset：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "cos_schema",
  "comment": "A schema in the Tencent Cloud COS credential-vending catalog",
  "properties": {
    "location": "cosn://my-bucket-1250000000/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/cos_catalog_with_vending/schemas

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "example_fileset",
  "comment": "This is an example fileset",
  "type": "MANAGED",
  "storageLocation": "cosn://my-bucket-1250000000/root/schema/example_fileset",
  "properties": {}
}' http://localhost:8090/api/metalakes/metalake/catalogs/cos_catalog_with_vending/schemas/cos_schema/filesets
```

### 无需本地凭证访问

在客户端启用分发并移除凭证属性。

```java
Configuration conf = new Configuration();
conf.setBoolean("fs.gravitino.enableCredentialVending", true);
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
// 无需设置 cos-access-key-id 或 cos-secret-access-key

Path filesetPath = new Path(
    "gvfs://fileset/cos_catalog_with_vending/cos_schema/example_fileset/new_dir");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.mkdirs(filesetPath);
```

```python
spark = (SparkSession.builder
    .appName("cos_fileset")
    .config("spark.hadoop.fs.gravitino.enableCredentialVending", "true")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    # 无需设置 cos-access-key-id 或 cos-secret-access-key
    .getOrCreate())
```

GVFS Python 客户端无法访问以 COS 为后端的 fileset；参见
[GVFS Python 客户端与 pandas](#凭证分发).