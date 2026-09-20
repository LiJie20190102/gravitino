---
slug: /fileset-catalog-with-oss
keyword: Fileset catalog OSS
license: This software is licensed under the Apache License version 2.
---
## 简介

本页介绍如何在阿里云 OSS 中存储 Fileset 数据，同时由 Gravitino 管理元数据，
以及如何通过 Gravitino 虚拟文件系统（GVFS）读写该数据。

本页所有内容均针对阿里云 OSS。Fileset 模型本身、各存储后端共享的属性，
以及属性从 Catalog 到 Schema 再到 Fileset 的继承方式，
在 [Fileset Catalog](./fileset-catalog.md) 中有详细说明。

示例按顺序执行，全文使用相同的名称：metalake `metalake`、catalog
`oss_catalog`、schema `oss_schema`、fileset `example_fileset`，以及 `http://localhost:8090` 作为
服务器 URL。请替换为实际值。

## 前提条件

1. 下载 [`gravitino-aliyun-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aliyun-bundle) 文件。
2. 将其放入 fileset catalog 的类路径 `${GRAVITINO_HOME}/catalogs/fileset/libs/` 下。
3. 启动 Gravitino 服务器：

```bash
${GRAVITINO_HOME}/bin/gravitino-server.sh start
```

bundle jar 位于类路径后，catalog 会自动加载阿里云 OSS 文件系统提供者。已弃用的
`filesystem-providers` 和 `default-filesystem-provider` catalog
属性无需设置。

## 阿里云 OSS 属性

除共享的
[catalog 属性](./fileset-catalog.md#catalog-properties) 外，还需要以下属性。GVFS 客户端也需要相同的值，因此在此一并列出——注意
Python 客户端使用下划线拼写，
而 catalog 和 Java 客户端使用连字符。

| Catalog 和 Java 客户端 | Python 客户端           | 描述                                                                                                                                                                                                                                                                                                | 是否必填 |
|-------------------------|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `oss-endpoint`          | `oss_endpoint`          | 阿里云 OSS 服务的 Endpoint。                                                                                                                                                                                                                                                                        | 是      |
| `oss-access-key-id`     | `oss_access_key_id`     | 阿里云 OSS 服务的 Access Key ID。                                                                                                                                                                                                                                                                      | 是      |
| `oss-secret-access-key` | `oss_secret_access_key` | 阿里云 OSS 服务的 Secret Access Key。                                                                                                                                                                                                                                                                      | 是      |
| `credential-providers`  | (n/a)                   | 凭证提供者类型，以逗号分隔。可选值为 `oss-token`、`oss-secret-key`。设置后启用凭证分发，客户端无需再使用上述凭证。各提供者所需的其他属性请参见[凭证分发](./security/credential-vending.md#oss)。 | 否       |

Schema 和 Fileset 属性在共享页面中有文档说明：参见
[Schema 属性](./fileset-catalog.md#schema-properties) 和
[Fileset 属性](./fileset-catalog.md#fileset-properties)。

Fileset catalog 将数据存储在 `location` 下，对于阿里云 OSS，格式类似于
`oss://bucket/root`。

## 创建 Catalog、Schema 和 Fileset

### 步骤 1：创建 catalog

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "oss_catalog",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Alibaba Cloud OSS",
  "properties": {
    "location": "oss://bucket/root",
    "oss-endpoint": "http://oss-cn-hangzhou.aliyuncs.com",
    "oss-access-key-id": "access_key",
    "oss-secret-access-key": "secret_key"
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
    .put("location", "oss://bucket/root")
    .put("oss-endpoint", "http://oss-cn-hangzhou.aliyuncs.com")
    .put("oss-access-key-id", "access_key")
    .put("oss-secret-access-key", "secret_key")
    .build();

Catalog catalog = gravitinoClient.createCatalog("oss_catalog",
    Catalog.Type.FILESET,
    "A fileset catalog backed by Alibaba Cloud OSS",
    catalogProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
gravitino_client: GravitinoClient = GravitinoClient(
    uri="http://localhost:8090", metalake_name="metalake")

catalog_properties = {
    "location": "oss://bucket/root",
    "oss-endpoint": "http://oss-cn-hangzhou.aliyuncs.com",
    "oss-access-key-id": "access_key",
    "oss-secret-access-key": "secret_key",
}

catalog = gravitino_client.create_catalog(name="oss_catalog",
                                          catalog_type=Catalog.Type.FILESET,
                                          provider=None,
                                          comment="A fileset catalog backed by Alibaba Cloud OSS",
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
  "name": "oss_schema",
  "comment": "A schema in the Alibaba Cloud OSS fileset catalog",
  "properties": {
    "location": "oss://bucket/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/oss_catalog/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("oss_catalog");
SupportsSchemas supportsSchemas = catalog.asSchemas();

Map<String, String> schemaProperties = ImmutableMap.<String, String>builder()
    .put("location", "oss://bucket/root/schema")
    .build();

Schema schema = supportsSchemas.createSchema("oss_schema",
    "A schema in the Alibaba Cloud OSS fileset catalog",
    schemaProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="oss_catalog")
catalog.as_schemas().create_schema(name="oss_schema",
                                   comment="A schema in the Alibaba Cloud OSS fileset catalog",
                                   properties={"location": "oss://bucket/root/schema"})
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
  "storageLocation": "oss://bucket/root/schema/example_fileset",
  "properties": {
    "k1": "v1"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/oss_catalog/schemas/oss_schema/filesets
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("oss_catalog");
FilesetCatalog filesetCatalog = catalog.asFilesetCatalog();

Map<String, String> filesetProperties = ImmutableMap.<String, String>builder()
    .put("k1", "v1")
    .build();

filesetCatalog.createFileset(
    NameIdentifier.of("oss_schema", "example_fileset"),
    "This is an example fileset",
    Fileset.Type.MANAGED,
    "oss://bucket/root/schema/example_fileset",
    filesetProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="oss_catalog")
catalog.as_fileset_catalog().create_fileset(
    ident=NameIdentifier.of("oss_schema", "example_fileset"),
    type=Fileset.Type.MANAGED,
    comment="This is an example fileset",
    storage_location="oss://bucket/root/schema/example_fileset",
    properties={"k1": "v1"})
```

</TabItem>
</Tabs>

该 fileset 现在可以通过以下地址访问：
`gvfs://fileset/oss_catalog/oss_schema/example_fileset`，适用于任何 GVFS 客户端。

## 访问 Fileset

### Java 客户端 jar 包

每个 Java 或基于 Hadoop 的客户端都需要 `gravitino-filesystem-hadoop3-runtime`（发布于
Maven Central），以及阿里云 OSS 文件系统实现。仅后者因
环境而异：

| 环境            | 提供阿里云 OSS 文件系统的 Jar                                                                                                                                                        |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 未安装 Hadoop    | [`gravitino-aliyun-bundle`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aliyun-bundle)，包含阿里云 OSS 文件系统实现及其依赖的 fat jar |
| 已有 Hadoop | `hadoop-aliyun-${hadoop-version}.jar`、`aliyun-sdk-oss-3.13.0.jar` 和 `jdom2-2.0.6.jar`，随 Hadoop 一起发布，位于 `${HADOOP_HOME}/share/hadoop/tools/lib`                                           |

完整构件列表：

- [`gravitino-aliyun-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aliyun-bundle)：
  一个包含 `gravitino-aliyun` 功能及其所有依赖的 "fat" jar，
  如 `hadoop-aliyun` 和 `aliyun-sdk-oss`。在环境中没有预装 Hadoop 时使用。
- [`gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-filesystem-hadoop3-runtime)：
  一个打包了 Gravitino 虚拟文件系统客户端的 "fat" jar，已包含
  `gravitino-aliyun` 功能。Java 和基于 Hadoop 的客户端需要它来访问 Gravitino
  fileset。
- `hadoop-aliyun-${hadoop-version}.jar`、`aliyun-sdk-oss-3.13.0.jar` 和 `jdom2-2.0.6.jar`：
  用于访问阿里云 OSS 的标准 Hadoop 依赖，随 Hadoop 一起发布，位于
  `${HADOOP_HOME}/share/hadoop/tools/lib`。在已有的
  Hadoop 环境中运行时需自行提供。
- [`gravitino-aliyun-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aliyun)：
  一个仅包含阿里云集成代码的 "thin" jar。它已包含在上面两个
  jar 中，因此无需作为直接依赖，除非希望自行管理所有 Hadoop 和
  阿里云依赖。

```xml
<!-- No Hadoop environment -->
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-aliyun-bundle</artifactId>
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
  <artifactId>hadoop-aliyun</artifactId>
  <version>${HADOOP_VERSION}</version>
</dependency>
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-filesystem-hadoop3-runtime</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
```

:::note
`gravitino-aliyun` thin jar 不是必需的。其功能已包含在
`gravitino-aliyun-bundle` 和 `gravitino-filesystem-hadoop3-runtime` 中。
:::

### GVFS Java 客户端

在 [GVFS 基础配置](./how-to-use-gvfs.md#configuration) 之上，设置上表中的阿里云 OSS
属性。

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
conf.set("oss-endpoint", "http://oss-cn-hangzhou.aliyuncs.com");
conf.set("oss-access-key-id", "access_key");
conf.set("oss-secret-access-key", "secret_key");

Path filesetPath = new Path("gvfs://fileset/oss_catalog/oss_schema/example_fileset/new_dir");
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
    "/path/to/hadoop-aliyun-3.3.4.jar,"
    "/path/to/aliyun-sdk-oss-3.13.0.jar,"
    "/path/to/jdom2-2.0.6.jar "
    "--master local[1] pyspark-shell"
)

spark = (SparkSession.builder
    .appName("oss_fileset")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    .config("spark.hadoop.oss-endpoint", "http://oss-cn-hangzhou.aliyuncs.com")
    .config("spark.hadoop.oss-access-key-id", "access_key")
    .config("spark.hadoop.oss-secret-access-key", "secret_key")
    .config("spark.driver.memory", "2g")
    .config("spark.driver.port", "2048")
    .getOrCreate())

data = [("Alice", 25), ("Bob", 30), ("Cathy", 45)]
spark_df = spark.createDataFrame(data, schema=["Name", "Age"])
gvfs_path = "gvfs://fileset/oss_catalog/oss_schema/example_fileset/people"

spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(gvfs_path)
```

如果 Spark 在没有 Hadoop 环境的情况下运行，只需更改 jar 列表：

```python
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/gravitino-aliyun-bundle-${gravitino-version}.jar,"
    "/path/to/gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar "
    "--master local[1] pyspark-shell"
)
```

:::note
某些 Spark 版本在 driver 中需要 Hadoop 环境，且不会加载通过
`--jars` 传递的文件系统实现。如果出现此情况，请将 jar 直接添加到 Spark 类路径中。
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
  <name>oss-endpoint</name>
  <value>http://oss-cn-hangzhou.aliyuncs.com</value>
</property>
<property>
  <name>oss-access-key-id</name>
  <value>access_key</value>
</property>
<property>
  <name>oss-secret-access-key</name>
  <value>secret_key</value>
</property>
```

2. 将以下 jar 添加到 Hadoop 类路径中：

   - `gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`，来自 Maven Central。
   - `hadoop-aliyun-${hadoop-version}.jar`、`aliyun-sdk-oss-3.13.0.jar` 和 `jdom2-2.0.6.jar`，随 Hadoop 一起发布，位于 `${HADOOP_HOME}/share/hadoop/tools/lib`。

3. 访问 fileset：

```shell
${HADOOP_HOME}/bin/hadoop fs -ls gvfs://fileset/oss_catalog/oss_schema/example_fileset
${HADOOP_HOME}/bin/hadoop fs -put /path/to/local/file gvfs://fileset/oss_catalog/oss_schema/example_fileset
```

### GVFS Python 客户端

```bash
pip install apache-gravitino==${GRAVITINO_VERSION}
```

在 [GVFS 基础配置](./how-to-use-gvfs.md#configuration-1) 之上，在 `options` 中传入阿里云 OSS
属性，使用下划线拼写。

```python
from gravitino import gvfs

options = {
    "cache_size": 20,
    "cache_expired_time": 3600,
    "auth_type": "simple",
    "oss_endpoint": "http://oss-cn-hangzhou.aliyuncs.com",
    "oss_access_key_id": "access_key",
    "oss_secret_access_key": "secret_key",
}

fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
fs.ls("gvfs://fileset/oss_catalog/oss_schema/example_fileset/")
```

### pandas

pandas 通过 `storage_options` 访问相同的路径。使用前面 GVFS 示例中的 `fs` 实例
来发现生成的 Spark part 文件。

```python
import pandas as pd

storage_options = {
    "server_uri": "http://localhost:8090",
    "metalake_name": "metalake",
    "options": {
        "oss_endpoint": "http://oss-cn-hangzhou.aliyuncs.com",
        "oss_access_key_id": "access_key",
        "oss_secret_access_key": "secret_key",
    }
}

csv_path = next(
    f"gvfs://{path}"
    for path in fs.ls(
        "gvfs://fileset/oss_catalog/oss_schema/example_fileset/people",
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

更多用例请参见 [Gravitino 虚拟文件系统](./how-to-use-gvfs.md)。

## 凭证分发

启用凭证分发后，catalog 持有阿里云 OSS 凭证，Gravitino 服务器按请求
分发凭证，因此客户端无需持有自身的云密钥。通用机制请参见
[凭证分发](./security/credential-vending.md)，各提供者所需属性
请参见 [OSS 凭证](./security/credential-vending.md#oss)
。

支持的提供者为 `oss-token`（分发短期 STS 令牌）和
`oss-secret-key`（分发 catalog 上配置的静态 Access Key）。以下示例使用
`oss-token`。

### 配置 catalog、schema 和 fileset

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "oss_catalog_with_vending",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Alibaba Cloud OSS with credential vending",
  "properties": {
    "location": "oss://bucket/root",
    "oss-endpoint": "http://oss-cn-hangzhou.aliyuncs.com",
    "oss-access-key-id": "access_key",
    "oss-secret-access-key": "secret_key",
    "credential-providers": "oss-token",
    "oss-region": "oss-cn-hangzhou",
    "oss-role-arn": "The ARN of the role that grants access to the OSS data"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

在启用凭证分发的 catalog 中创建 schema 和 fileset：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "oss_schema",
  "comment": "A schema in the Alibaba Cloud OSS credential-vending catalog",
  "properties": {
    "location": "oss://bucket/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/oss_catalog_with_vending/schemas

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "example_fileset",
  "comment": "This is an example fileset",
  "type": "MANAGED",
  "storageLocation": "oss://bucket/root/schema/example_fileset",
  "properties": {}
}' http://localhost:8090/api/metalakes/metalake/catalogs/oss_catalog_with_vending/schemas/oss_schema/filesets
```

`oss-token` 提供者还需要两个额外的 catalog 属性。

| 属性名  | 描述                                         |
|----------------|-----------------------------------------------------|
| `oss-region`   | Bucket 所在的 Region，例如 `oss-cn-hangzhou` |
| `oss-role-arn` | 授予数据访问权限的角色的 ARN      |

### 无本地凭证访问

在客户端启用凭证分发，并移除凭证属性。

```java
Configuration conf = new Configuration();
conf.setBoolean("fs.gravitino.enableCredentialVending", true);
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
// 无需设置 oss-access-key-id 或 oss-secret-access-key

Path filesetPath = new Path(
    "gvfs://fileset/oss_catalog_with_vending/oss_schema/example_fileset/new_dir");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.mkdirs(filesetPath);
```

```python
spark = (SparkSession.builder
    .appName("oss_fileset")
    .config("spark.hadoop.fs.gravitino.enableCredentialVending", "true")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    # 无需设置 oss-access-key-id 或 oss-secret-access-key
    .getOrCreate())
```

```python
options = {
    "auth_type": "simple",
    "enable_credential_vending": True,
    # 无需设置 oss-access-key-id 或 oss-secret-access-key
}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
```