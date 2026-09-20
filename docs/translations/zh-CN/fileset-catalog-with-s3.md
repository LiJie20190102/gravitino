---
slug: /fileset-catalog-with-s3
keyword: Fileset catalog S3
license: This software is licensed under the Apache License version 2.
title: 使用 S3 的文件集 (Fileset) 目录 (Catalog)
---
## 简介

本页介绍如何在 Amazon S3 中存储 fileset 数据，同时由 Gravitino 管理元数据，
以及如何通过 Gravitino Virtual File System (GVFS) 读写该数据。

本页所有内容均针对 Amazon S3。Fileset 模型本身、所有存储后端共享的属性，
以及属性从 catalog 到 schema 再到 fileset 的继承方式，
均在 [Fileset Catalog](./fileset-catalog.md) 中说明。

示例按顺序运行，且全程使用相同名称：metalake `metalake`、catalog
`s3_catalog`、schema `s3_schema`、fileset `example_fileset`，以及 `http://localhost:8090` 作为
服务器 URL。请将这些值替换为实际使用的值。

## 前提条件

1. 下载 [`gravitino-aws-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aws-bundle) 文件。
2. 将其放入 fileset catalog 类路径 `${GRAVITINO_HOME}/catalogs/fileset/libs/` 下。
3. 启动 Gravitino 服务器：

```bash
${GRAVITINO_HOME}/bin/gravitino-server.sh start
```

当 bundle jar 加入
类路径后，catalog 会自动加载 Amazon S3 filesystem provider。已废弃的 `filesystem-providers` 和 `default-filesystem-provider` catalog
属性无需设置。

## Amazon S3 属性

除共享的
[catalog 属性](./fileset-catalog.md#catalog-properties) 外，还需要以下属性。GVFS 客户端
也需要相同的值，因此在此一并列出——注意 Python 客户端使用下划线，
而 catalog 和 Java 客户端使用连字符。

| Catalog 和 Java 客户端 | Python 客户端          | 描述                                                                                                                                                                                                                                                                                                         | 必填                                         |
|-------------------------|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| `s3-endpoint`           | `s3_endpoint`          | S3 服务的 Endpoint。MinIO 等 S3 兼容存储始终需要此项。                                                                                                                                                                                                                                    | 是，Python 客户端访问 AWS S3 时除外 |
| `s3-access-key-id`      | `s3_access_key_id`     | S3 服务的 Access key。                                                                                                                                                                                                                                                                                       | 是                                              |
| `s3-secret-access-key`  | `s3_secret_access_key` | S3 服务的 Secret key。                                                                                                                                                                                                                                                                                       | 是                                              |
| `credential-providers`  | (不适用)                  | 凭证 provider 类型，以逗号分隔。可能的值为 `s3-token`、`s3-secret-key`、`aws-irsa`。设置此项将启用凭证分发，客户端不再需要上述凭证。各 provider 所需的额外属性请参见 [凭证分发](./security/credential-vending.md#s3)。 | 否                                               |

:::note
- Location 必须以 `s3a://` 开头，而不是 `s3://`。`hadoop-aws` 库不支持
  `s3://` scheme。
- 对于 MinIO 及其他 S3 兼容服务，将 `s3-endpoint` 设置为该服务。如果需要
  path-style 访问，将 `gravitino.bypass.fs.s3a.path.style.access=true` 添加到
  `${GRAVITINO_HOME}/catalogs/fileset/conf/fileset.conf` 用于服务端操作。同时在
  GVFS Java 客户端上设置 `s3-path-style-access=true`，或在
  Spark 中设置 `spark.hadoop.s3-path-style-access=true`。对于 Python GVFS 客户端，将
  `config_kwargs={"s3": {"addressing_style": "path"}}` 传递给
  `GravitinoVirtualFileSystem`；对于 pandas，在
  `storage_options` 的顶层添加相同的 `config_kwargs` 条目。
:::

Schema 和 fileset 属性记录在共享页面上：参见
[schema 属性](./fileset-catalog.md#schema-properties) 和
[fileset 属性](./fileset-catalog.md#fileset-properties)。

Fileset catalog 将数据存储在 `location` 下，对于 Amazon S3，格式类似于
`s3a://bucket/root`。

## 创建 Catalog、Schema 和 Fileset

### 步骤 1：创建 catalog

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "s3_catalog",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Amazon S3",
  "properties": {
    "location": "s3a://bucket/root",
    "s3-endpoint": "http://s3.ap-northeast-1.amazonaws.com",
    "s3-access-key-id": "access_key",
    "s3-secret-access-key": "secret_key"
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
    .put("location", "s3a://bucket/root")
    .put("s3-endpoint", "http://s3.ap-northeast-1.amazonaws.com")
    .put("s3-access-key-id", "access_key")
    .put("s3-secret-access-key", "secret_key")
    .build();

Catalog catalog = gravitinoClient.createCatalog("s3_catalog",
    Catalog.Type.FILESET,
    "A fileset catalog backed by Amazon S3",
    catalogProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
gravitino_client: GravitinoClient = GravitinoClient(
    uri="http://localhost:8090", metalake_name="metalake")

catalog_properties = {
    "location": "s3a://bucket/root",
    "s3-endpoint": "http://s3.ap-northeast-1.amazonaws.com",
    "s3-access-key-id": "access_key",
    "s3-secret-access-key": "secret_key",
}

catalog = gravitino_client.create_catalog(name="s3_catalog",
                                          catalog_type=Catalog.Type.FILESET,
                                          provider=None,
                                          comment="A fileset catalog backed by Amazon S3",
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
  "name": "s3_schema",
  "comment": "A schema in the Amazon S3 fileset catalog",
  "properties": {
    "location": "s3a://bucket/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/s3_catalog/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("s3_catalog");
SupportsSchemas supportsSchemas = catalog.asSchemas();

Map<String, String> schemaProperties = ImmutableMap.<String, String>builder()
    .put("location", "s3a://bucket/root/schema")
    .build();

Schema schema = supportsSchemas.createSchema("s3_schema",
    "A schema in the Amazon S3 fileset catalog",
    schemaProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="s3_catalog")
catalog.as_schemas().create_schema(name="s3_schema",
                                   comment="A schema in the Amazon S3 fileset catalog",
                                   properties={"location": "s3a://bucket/root/schema"})
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
  "storageLocation": "s3a://bucket/root/schema/example_fileset",
  "properties": {
    "k1": "v1"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/s3_catalog/schemas/s3_schema/filesets
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("s3_catalog");
FilesetCatalog filesetCatalog = catalog.asFilesetCatalog();

Map<String, String> filesetProperties = ImmutableMap.<String, String>builder()
    .put("k1", "v1")
    .build();

filesetCatalog.createFileset(
    NameIdentifier.of("s3_schema", "example_fileset"),
    "This is an example fileset",
    Fileset.Type.MANAGED,
    "s3a://bucket/root/schema/example_fileset",
    filesetProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="s3_catalog")
catalog.as_fileset_catalog().create_fileset(
    ident=NameIdentifier.of("s3_schema", "example_fileset"),
    type=Fileset.Type.MANAGED,
    comment="This is an example fileset",
    storage_location="s3a://bucket/root/schema/example_fileset",
    properties={"k1": "v1"})
```

</TabItem>
</Tabs>

该 fileset 现在可通过以下地址从任何 GVFS 客户端访问：
`gvfs://fileset/s3_catalog/s3_schema/example_fileset`。

## 访问 Fileset

### Java 客户端 jar 包

每个 Java 或基于 Hadoop 的客户端都需要 `gravitino-filesystem-hadoop3-runtime`，它发布在
Maven Central 上，以及 Amazon S3 filesystem 实现。只有后者会因
环境而异：

| 环境            | 提供 Amazon S3 filesystem 的 jar 包                                                                                                                                             |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 未安装 Hadoop    | [`gravitino-aws-bundle`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aws-bundle)，一个打包了 Amazon S3 filesystem 实现和 AWS SDK 的 fat jar |
| 已有 Hadoop      | `hadoop-aws-${hadoop-version}.jar` 和 `aws-java-sdk-bundle-1.12.262.jar`，随 Hadoop 一起发布，位于 `${HADOOP_HOME}/share/hadoop/tools/lib` 下                                       |

完整的构件列表：

- [`gravitino-aws-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aws-bundle):
  一个“fat”jar，包含 `gravitino-aws` 功能及其所需的所有依赖项，
  如 `hadoop-aws` 和 AWS SDK。在环境没有预装 Hadoop 时使用。
- [`gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-filesystem-hadoop3-runtime):
  一个“fat”jar，打包了 Gravitino 虚拟文件系统客户端，并已包含
  `gravitino-aws` 功能。Java 和基于 Hadoop 的客户端需要它来访问 Gravitino
  fileset。
- `hadoop-aws-${hadoop-version}.jar` 和 `aws-java-sdk-bundle-1.12.262.jar`：标准的 Hadoop
  Amazon S3 访问依赖项，随 Hadoop 一起发布，位于
  `${HADOOP_HOME}/share/hadoop/tools/lib` 下。在已有
  Hadoop 环境中运行时需自行提供。
- [`gravitino-aws-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aws):
  一个只包含 AWS 集成代码的“thin”jar。上述两个 jar 中已包含它，
  因此无需作为直接依赖项，除非倾向于自行管理所有 Hadoop 和 AWS
  依赖项。

```xml
<!-- No Hadoop environment -->
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-aws-bundle</artifactId>
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
<dependency>
  <groupId>org.apache.hadoop</groupId>
  <artifactId>hadoop-aws</artifactId>
  <version>${HADOOP_VERSION}</version>
</dependency>
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-filesystem-hadoop3-runtime</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
```

:::note
不需要 thin `gravitino-aws` jar。其功能已包含在
`gravitino-aws-bundle` 和 `gravitino-filesystem-hadoop3-runtime` 中。
:::

### GVFS Java 客户端

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration) 之上，设置上表中的
Amazon S3 属性。

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
conf.set("s3-endpoint", "http://s3.ap-northeast-1.amazonaws.com");
conf.set("s3-access-key-id", "access_key");
conf.set("s3-secret-access-key", "secret_key");

Path filesetPath = new Path("gvfs://fileset/s3_catalog/s3_schema/example_fileset/new_dir");
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
    "/path/to/hadoop-aws-3.3.4.jar,"
    "/path/to/aws-java-sdk-bundle-1.12.262.jar "
    "--master local[1] pyspark-shell"
)

spark = (SparkSession.builder
    .appName("s3_fileset")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    .config("spark.hadoop.s3-endpoint", "http://s3.ap-northeast-1.amazonaws.com")
    .config("spark.hadoop.s3-access-key-id", "access_key")
    .config("spark.hadoop.s3-secret-access-key", "secret_key")
    .config("spark.driver.memory", "2g")
    .config("spark.driver.port", "2048")
    .getOrCreate())

data = [("Alice", 25), ("Bob", 30), ("Cathy", 45)]
spark_df = spark.createDataFrame(data, schema=["Name", "Age"])
gvfs_path = "gvfs://fileset/s3_catalog/s3_schema/example_fileset/people"

spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(gvfs_path)
```

如果 Spark 在没有 Hadoop 环境的情况下运行，只需更改 jar 列表：

```python
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/gravitino-aws-bundle-${gravitino-version}.jar,"
    "/path/to/gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar "
    "--master local[1] pyspark-shell"
)
```

:::note
某些 Spark 版本在 driver 中需要 Hadoop 环境，并且不会加载通过
`--jars` 传递的 filesystem 实现。如果发生这种情况，请直接将 jar 添加到 Spark classpath 中。
:::

### Hadoop fs 命令

1. 将以下内容添加到 `${HADOOP_HOME}/etc/hadoop/core-site.xml`：

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
  <name>s3-endpoint</name>
  <value>http://s3.ap-northeast-1.amazonaws.com</value>
</property>
<property>
  <name>s3-access-key-id</name>
  <value>access_key</value>
</property>
<property>
  <name>s3-secret-access-key</name>
  <value>secret_key</value>
</property>
```

2. 将以下 jar 添加到 Hadoop classpath：

   - `gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`，来自 Maven Central。
   - `hadoop-aws-${hadoop-version}.jar` 和 `aws-java-sdk-bundle-1.12.262.jar`，随 Hadoop 一起发布，位于 `${HADOOP_HOME}/share/hadoop/tools/lib` 下。

3. 访问 fileset：

```shell
${HADOOP_HOME}/bin/hadoop fs -ls gvfs://fileset/s3_catalog/s3_schema/example_fileset
${HADOOP_HOME}/bin/hadoop fs -put /path/to/local/file gvfs://fileset/s3_catalog/s3_schema/example_fileset
```

### GVFS Python 客户端

```bash
pip install apache-gravitino==${GRAVITINO_VERSION}
```

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration-1) 之上，在 `options` 中传递
Amazon S3 属性，使用下划线拼写。

```python
from gravitino import gvfs

options = {
    "cache_size": 20,
    "cache_expired_time": 3600,
    "auth_type": "simple",
    "s3_endpoint": "http://s3.ap-northeast-1.amazonaws.com",
    "s3_access_key_id": "access_key",
    "s3_secret_access_key": "secret_key",
}

fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
fs.ls("gvfs://fileset/s3_catalog/s3_schema/example_fileset/")
```

### pandas

pandas 通过 `storage_options` 访问相同路径。使用前面
GVFS 示例中的 `fs` 实例来发现生成的 Spark part 文件。

```python
import pandas as pd

storage_options = {
    "server_uri": "http://localhost:8090",
    "metalake_name": "metalake",
    "options": {
        "s3_endpoint": "http://s3.ap-northeast-1.amazonaws.com",
        "s3_access_key_id": "access_key",
        "s3_secret_access_key": "secret_key",
    }
}

csv_path = next(
    f"gvfs://{path}"
    for path in fs.ls(
        "gvfs://fileset/s3_catalog/s3_schema/example_fileset/people",
        detail=False,
    )
    if (
        path.rsplit("/", 1)[-1].startswith("part-")
        and path.endswith(".csv")
    )
)
ds = pd.read_csv(csv_path, storage_options=storage_options)
ds.head()
```

更多用例，请参见 [Gravitino Virtual File System](./how-to-use-gvfs.md)。

## 凭证分发

通过凭证分发，catalog 持有 Amazon S3 凭证，Gravitino 服务器按
请求分发凭证，因此客户端无需持有自己的云密钥。
通用机制请参见 [凭证分发](./security/credential-vending.md)，
各 provider 所需属性请参见 [S3 凭证](./security/credential-vending.md#s3)
的说明。

支持的 provider 包括：`s3-token`，分发短期的 STS token；
`s3-secret-key`，分发 catalog 上配置的静态 access key；以及 `aws-irsa`，
从 IAM role for service accounts 分发凭证，目前从文件中读取
web identity token。以下示例使用 `s3-token`。

### 配置 catalog、schema 和 fileset

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "s3_catalog_with_vending",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Amazon S3 with credential vending",
  "properties": {
    "location": "s3a://bucket/root",
    "s3-endpoint": "http://s3.ap-northeast-1.amazonaws.com",
    "s3-access-key-id": "access_key",
    "s3-secret-access-key": "secret_key",
    "credential-providers": "s3-token",
    "s3-region": "ap-northeast-1",
    "s3-role-arn": "arn:aws:iam::123456789012:role/gravitino-fileset"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

在启用凭证分发的 catalog 中创建 schema 和 fileset：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "s3_schema",
  "comment": "A schema in the Amazon S3 credential-vending catalog",
  "properties": {
    "location": "s3a://bucket/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/s3_catalog_with_vending/schemas

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "example_fileset",
  "comment": "This is an example fileset",
  "type": "MANAGED",
  "storageLocation": "s3a://bucket/root/schema/example_fileset",
  "properties": {}
}' http://localhost:8090/api/metalakes/metalake/catalogs/s3_catalog_with_vending/schemas/s3_schema/filesets
```

`s3-token` provider 需要另外两个 catalog 属性。

| 属性名 | 描述                                        |
|---------------|----------------------------------------------------|
| `s3-region`   | Bucket 所在区域，例如 `ap-northeast-1` |
| `s3-role-arn` | 授予数据访问权限的 role ARN     |

### 无本地凭证访问

在客户端启用分发并移除凭证属性。

```java
Configuration conf = new Configuration();
conf.setBoolean("fs.gravitino.enableCredentialVending", true);
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
// 无需设置 s3-access-key-id 或 s3-secret-access-key

Path filesetPath = new Path(
    "gvfs://fileset/s3_catalog_with_vending/s3_schema/example_fileset/new_dir");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.mkdirs(filesetPath);
```

```python
spark = (SparkSession.builder
    .appName("s3_fileset")
    .config("spark.hadoop.fs.gravitino.enableCredentialVending", "true")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    # 无需设置 s3-access-key-id 或 s3-secret-access-key
    .getOrCreate())
```

```python
options = {
    "auth_type": "simple",
    "enable_credential_vending": True,
    # 无需设置 s3-access-key-id 或 s3-secret-access-key
}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
```