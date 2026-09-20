---
slug: /fileset-catalog-with-gcs
keyword: Fileset catalog GCS
license: This software is licensed under the Apache License version 2.
---
## 简介

本页说明如何将 Fileset 数据存储在 Google Cloud Storage 中，同时由 Gravitino 管理元数据，
以及如何通过 Gravitino 虚拟文件系统（GVFS）读写该数据。

本页所有内容均特定于 Google Cloud Storage。Fileset 模型本身、所有存储后端共享的属性，以及
属性从 catalog 到 schema 再到 fileset 的继承方式，均在
[Fileset Catalog](./fileset-catalog.md) 中描述。

示例按顺序运行，并全程使用相同的名称：metalake `metalake`、catalog
`gcs_catalog`、schema `gcs_schema`、fileset `example_fileset`，并以 `http://localhost:8090` 作为
服务器 URL。将其替换为实际使用的值。

## 前提条件

1. 下载 [`gravitino-gcp-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-gcp-bundle) 文件。
2. 将其放入 fileset catalog 的类路径 `${GRAVITINO_HOME}/catalogs/fileset/libs/` 中。
3. 启动 Gravitino 服务器：

```bash
${GRAVITINO_HOME}/bin/gravitino-server.sh start
```

一旦 bundle jar 位于类路径上，catalog 会自动加载 Google Cloud Storage 文件系统提供程序。已废弃的
`filesystem-providers` 和 `default-filesystem-provider` catalog
属性无需设置。

## Google Cloud Storage 属性

除了共享的
[catalog 属性](./fileset-catalog.md#catalog-properties) 外，还需要这些属性。GVFS 客户端也需要相同的值，因此在此一并列出 —
注意 Python 客户端使用下划线拼写，而 catalog 和 Java 客户端
使用连字符。

| Catalog 和 Java 客户端    | Python 客户端              | 描述                                                                                                                                                                                                                                                                              | 是否必需 |
|----------------------------|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `gcs-service-account-file` | `gcs_service_account_file` | GCS 服务账号 JSON 文件的路径。                                                                                                                                                                                                                                               | 是      |
| `credential-providers`     | (n/a)                      | 凭证提供程序类型，以逗号分隔。可能的值为 `gcs-token`。设置此项会启用凭证分发 (credential vending)，因此客户端不再需要上述凭证。每个提供程序所需的额外属性请参见 [凭证分发](./security/credential-vending.md#gcs)。 | 否       |

:::note
服务账号文件必须对 catalog 的 Gravitino 服务器进程可读，且对
GVFS 的每个客户端进程可读。
:::

Schema 和 fileset 属性记录在共享页面上：参见
[schema 属性](./fileset-catalog.md#schema-properties) 和
[fileset 属性](./fileset-catalog.md#fileset-properties)。

Fileset catalog 将其数据存储在 `location` 下，对于 Google Cloud Storage，该位置类似于
`gs://bucket/root`。

## 创建 Catalog、Schema 和 Fileset

### 步骤 1：创建 catalog

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "gcs_catalog",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Google Cloud Storage",
  "properties": {
    "location": "gs://bucket/root",
    "gcs-service-account-file": "/path/to/service-account.json"
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
    .put("location", "gs://bucket/root")
    .put("gcs-service-account-file", "/path/to/service-account.json")
    .build();

Catalog catalog = gravitinoClient.createCatalog("gcs_catalog",
    Catalog.Type.FILESET,
    "A fileset catalog backed by Google Cloud Storage",
    catalogProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
gravitino_client: GravitinoClient = GravitinoClient(
    uri="http://localhost:8090", metalake_name="metalake")

catalog_properties = {
    "location": "gs://bucket/root",
    "gcs-service-account-file": "/path/to/service-account.json",
}

catalog = gravitino_client.create_catalog(name="gcs_catalog",
                                          catalog_type=Catalog.Type.FILESET,
                                          provider=None,
                                          comment="A fileset catalog backed by Google Cloud Storage",
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
  "name": "gcs_schema",
  "comment": "A schema in the Google Cloud Storage fileset catalog",
  "properties": {
    "location": "gs://bucket/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/gcs_catalog/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("gcs_catalog");
SupportsSchemas supportsSchemas = catalog.asSchemas();

Map<String, String> schemaProperties = ImmutableMap.<String, String>builder()
    .put("location", "gs://bucket/root/schema")
    .build();

Schema schema = supportsSchemas.createSchema("gcs_schema",
    "A schema in the Google Cloud Storage fileset catalog",
    schemaProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="gcs_catalog")
catalog.as_schemas().create_schema(name="gcs_schema",
                                   comment="A schema in the Google Cloud Storage fileset catalog",
                                   properties={"location": "gs://bucket/root/schema"})
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
  "storageLocation": "gs://bucket/root/schema/example_fileset",
  "properties": {
    "k1": "v1"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/gcs_catalog/schemas/gcs_schema/filesets
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("gcs_catalog");
FilesetCatalog filesetCatalog = catalog.asFilesetCatalog();

Map<String, String> filesetProperties = ImmutableMap.<String, String>builder()
    .put("k1", "v1")
    .build();

filesetCatalog.createFileset(
    NameIdentifier.of("gcs_schema", "example_fileset"),
    "This is an example fileset",
    Fileset.Type.MANAGED,
    "gs://bucket/root/schema/example_fileset",
    filesetProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="gcs_catalog")
catalog.as_fileset_catalog().create_fileset(
    ident=NameIdentifier.of("gcs_schema", "example_fileset"),
    type=Fileset.Type.MANAGED,
    comment="This is an example fileset",
    storage_location="gs://bucket/root/schema/example_fileset",
    properties={"k1": "v1"})
```

</TabItem>
</Tabs>

该 fileset 现在可由任何 GVFS 客户端通过以下地址访问：
`gvfs://fileset/gcs_catalog/gcs_schema/example_fileset`。

## 访问 Fileset

### Java 客户端 jar 包

每个 Java 或基于 Hadoop 的客户端都需要 `gravitino-filesystem-hadoop3-runtime`，它发布在
Maven Central 上，以及 Google Cloud Storage 文件系统实现。只有后者因环境
而异：

| 环境            | 提供 Google Cloud Storage 文件系统的 Jar 包                                                                                                                                                                                           |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 未安装 Hadoop    | [`gravitino-gcp-bundle`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-gcp-bundle)，一个包含 Google Cloud Storage 文件系统实现及其依赖项的 fat jar                                          |
| 已存在 Hadoop | [`gcs-connector-hadoop3-2.2.22-shaded.jar`](https://github.com/GoogleCloudDataproc/hadoop-connectors/releases/download/v2.2.22/gcs-connector-hadoop3-2.2.22-shaded.jar)，由 Google 发布，不属于 Apache Hadoop 发行版 |

完整的构件：

- [`gravitino-gcp-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-gcp-bundle):
  一个包含 `gravitino-gcp` 功能及其所有所需依赖项的 "fat" jar，
  例如 `gcs-connector`。当环境中没有预先存在的 Hadoop 配置时使用。
- [`gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-filesystem-hadoop3-runtime):
  一个捆绑了 Gravitino 虚拟文件系统客户端的 "fat" jar，并且已包含
  `gravitino-gcp` 功能。Java 和基于 Hadoop 的客户端需要它来访问 Gravitino
  fileset。
- [`gcs-connector-hadoop3-2.2.22-shaded.jar`](https://github.com/GoogleCloudDataproc/hadoop-connectors/releases/download/v2.2.22/gcs-connector-hadoop3-2.2.22-shaded.jar):
  用于访问 Google Cloud Storage 的标准 Hadoop 依赖项，由 Google 发布，不属于
  Apache Hadoop 发行版。在现有 Hadoop 环境中运行时，需自行提供这些
  依赖项。
- [`gravitino-gcp-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-gcp):
  仅包含 GCP 集成代码的 "thin" jar。它已包含在上述两个 jar 中，
  因此除非倾向于自行管理所有 Hadoop 和 GCP
  依赖项，否则不需要将其作为直接依赖。

```xml
<!-- No Hadoop environment -->
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-gcp-bundle</artifactId>
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
  <groupId>com.google.cloud.bigdataoss</groupId>
  <artifactId>gcs-connector</artifactId>
  <version>hadoop3-2.2.22</version>
</dependency>
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-filesystem-hadoop3-runtime</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
```

:::note
不需要 thin `gravitino-gcp` jar。其功能已包含在上述两个
`gravitino-gcp-bundle` 和 `gravitino-filesystem-hadoop3-runtime`。
:::

### GVFS Java 客户端

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration) 基础上，设置 Google Cloud Storage
上表中的属性。

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
conf.set("gcs-service-account-file", "/path/to/service-account.json");

Path filesetPath = new Path("gvfs://fileset/gcs_catalog/gcs_schema/example_fileset/new_dir");
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
    "/path/to/gcs-connector-hadoop3-2.2.22-shaded.jar "
    "--master local[1] pyspark-shell"
)

spark = (SparkSession.builder
    .appName("gcs_fileset")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    .config("spark.hadoop.gcs-service-account-file", "/path/to/service-account.json")
    .config("spark.driver.memory", "2g")
    .config("spark.driver.port", "2048")
    .getOrCreate())

data = [("Alice", 25), ("Bob", 30), ("Cathy", 45)]
spark_df = spark.createDataFrame(data, schema=["Name", "Age"])
gvfs_path = "gvfs://fileset/gcs_catalog/gcs_schema/example_fileset/people"

spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(gvfs_path)
```

如果 Spark 运行在没有 Hadoop 环境的情况下，仅需更改 jar 列表：

```python
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/gravitino-gcp-bundle-${gravitino-version}.jar,"
    "/path/to/gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar "
    "--master local[1] pyspark-shell"
)
```

:::note
部分 Spark 版本在 driver 中需要 Hadoop 环境，且无法加载通过 `--jars` 传递的文件系统
实现。如果发生这种情况，请直接将 jar 添加到 Spark classpath 中。
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
  <name>gcs-service-account-file</name>
  <value>/path/to/service-account.json</value>
</property>
```

2. 将这些 jar 添加到 Hadoop classpath 中：

   - `gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`，来自 Maven Central。
   - [`gcs-connector-hadoop3-2.2.22-shaded.jar`](https://github.com/GoogleCloudDataproc/hadoop-connectors/releases/download/v2.2.22/gcs-connector-hadoop3-2.2.22-shaded.jar)，由 Google 发布，不属于 Apache Hadoop 发行版。

3. 访问 fileset：

```shell
${HADOOP_HOME}/bin/hadoop fs -ls gvfs://fileset/gcs_catalog/gcs_schema/example_fileset
${HADOOP_HOME}/bin/hadoop fs -put /path/to/local/file gvfs://fileset/gcs_catalog/gcs_schema/example_fileset
```

### GVFS Python 客户端

```bash
pip install apache-gravitino==${GRAVITINO_VERSION}
```

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration-1) 基础上，在 `options` 中传递 Google Cloud Storage
属性，属性名使用下划线拼写。

```python
from gravitino import gvfs

options = {
    "cache_size": 20,
    "cache_expired_time": 3600,
    "auth_type": "simple",
    "gcs_service_account_file": "/path/to/service-account.json",
}

fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
fs.ls("gvfs://fileset/gcs_catalog/gcs_schema/example_fileset/")
```

### pandas

pandas 通过 `storage_options` 访问相同的路径。使用前述
GVFS 示例中的 `fs` 实例来查看生成的 Spark part 文件。

```python
import pandas as pd

storage_options = {
    "server_uri": "http://localhost:8090",
    "metalake_name": "metalake",
    "options": {
        "gcs_service_account_file": "/path/to/service-account.json",
    }
}

csv_path = next(
    f"gvfs://{path}"
    for path in fs.ls(
        "gvfs://fileset/gcs_catalog/gcs_schema/example_fileset/people",
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

了解更多用例，请参见 [Gravitino Virtual File System](./how-to-use-gvfs.md)。

## 凭证分发

通过凭证分发，catalog 持有 Google Cloud Storage 凭证，Gravitino 服务器在
每次请求时分发一个凭证，因此客户端无需持有自己的云密钥。通用机制请参见
[Credential Vending](./security/credential-vending.md)，各提供者所需的属性请参见
[GCS credentials](./security/credential-vending.md#gcs) 了解各提供者
所需的属性。

支持的提供者为 `gcs-token`，分发短期 token。

### 配置 catalog、schema 和 fileset

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "gcs_catalog_with_vending",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Google Cloud Storage with credential vending",
  "properties": {
    "location": "gs://bucket/root",
    "gcs-service-account-file": "/path/to/service-account.json",
    "credential-providers": "gcs-token"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

在启用凭证分发的 catalog 中创建 schema 和 fileset：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "gcs_schema",
  "comment": "A schema in the Google Cloud Storage credential-vending catalog",
  "properties": {
    "location": "gs://bucket/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/gcs_catalog_with_vending/schemas

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "example_fileset",
  "comment": "This is an example fileset",
  "type": "MANAGED",
  "storageLocation": "gs://bucket/root/schema/example_fileset",
  "properties": {}
}' http://localhost:8090/api/metalakes/metalake/catalogs/gcs_catalog_with_vending/schemas/gcs_schema/filesets
```

### 无本地凭证访问

在客户端启用分发功能并移除凭证属性。

```java
Configuration conf = new Configuration();
conf.setBoolean("fs.gravitino.enableCredentialVending", true);
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
// 无需设置 gcs-service-account-file

Path filesetPath = new Path(
    "gvfs://fileset/gcs_catalog_with_vending/gcs_schema/example_fileset/new_dir");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.mkdirs(filesetPath);
```

```python
spark = (SparkSession.builder
    .appName("gcs_fileset")
    .config("spark.hadoop.fs.gravitino.enableCredentialVending", "true")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    # 无需设置 gcs-service-account-file
    .getOrCreate())
```

```python
options = {
    "auth_type": "simple",
    "enable_credential_vending": True,
    # 无需设置 gcs-service-account-file
}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
```