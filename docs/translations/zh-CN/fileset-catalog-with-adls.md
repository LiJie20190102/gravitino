---
slug: /fileset-catalog-with-adls
keyword: Fileset catalog ADLS Azure Blob Storage
license: This software is licensed under the Apache License version 2.
---
## 简介

本页介绍如何在 Azure Data Lake Storage 中存储 fileset 数据，同时由 Gravitino 管理元数据，
以及如何通过 Gravitino 虚拟文件系统 (GVFS) 读写该数据。

本页所有内容均针对 Azure Data Lake Storage。Fileset 模型本身、所有存储后端共享的属性，
以及属性从 catalog 继承到 schema 再到 fileset 的方式，
均在 [Fileset Catalog](./fileset-catalog.md) 中说明。

示例按顺序运行，并全程使用相同的名称：metalake `metalake`、catalog
`adls_catalog`、schema `adls_schema`、fileset `example_fileset`，以及 `http://localhost:8090` 作为
服务器 URL。将其替换为实际值。

## 前提条件

1. 下载 [`gravitino-azure-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-azure-bundle) 文件。
2. 将其放入 fileset catalog 类路径 `${GRAVITINO_HOME}/catalogs/fileset/libs/` 下。
3. 启动 Gravitino 服务器：

```bash
${GRAVITINO_HOME}/bin/gravitino-server.sh start
```

bundle jar 位于
类路径上后，catalog 会自动加载 Azure Data Lake Storage 文件系统提供器。已弃用的 `filesystem-providers` 和 `default-filesystem-provider` catalog
属性无需设置。

## Azure Data Lake Storage 属性

除了共享的
[catalog 属性](./fileset-catalog.md#catalog-properties) 外，还需要这些属性。GVFS 客户端
也需要相同的值，因此在此一并列出——注意 Python 客户端使用下划线拼写，
而 catalog 和 Java 客户端使用连字符。

| Catalog 和 Java 客户端        | Python 客户端                | 描述                                                                                                                                                                                                                                                                                                            | 必填     |
|------------------------------|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `azure-storage-account-name` | `azure_storage_account_name` | Azure Blob Storage 的账户名。                                                                                                                                                                                                                                                                                   | 是       |
| `azure-storage-account-key`  | `azure_storage_account_key`  | Azure Blob Storage 的账户密钥。                                                                                                                                                                                                                                                                                 | 是       |
| `credential-providers`       | (n/a)                        | 凭证提供器类型，以逗号分隔。可能的值为 `adls-token`、`azure-account-key`。设置此参数将启用凭证分发，因此客户端不再需要上述凭证。每个提供器所需的额外属性请参见 [凭证分发](./security/credential-vending.md#adls)。 | 否       |

:::note
Azure Data Lake Storage 也称为 Azure Blob Storage (ABS)。位置使用 `abfss://`
协议。
:::

Schema 和 fileset 属性记录在共享页面上：参见
[schema 属性](./fileset-catalog.md#schema-properties) 和
[fileset 属性](./fileset-catalog.md#fileset-properties)。

Fileset catalog 将其数据存储在 `location` 下，对于 Azure Data Lake Storage，其格式类似于
`abfss://container@account-name.dfs.core.windows.net/root`。

## 创建 Catalog、Schema 和 Fileset

### 步骤 1：创建 catalog

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "adls_catalog",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Azure Data Lake Storage",
  "properties": {
    "location": "abfss://container@account-name.dfs.core.windows.net/root",
    "azure-storage-account-name": "account_name",
    "azure-storage-account-key": "account_key"
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
    .put("location", "abfss://container@account-name.dfs.core.windows.net/root")
    .put("azure-storage-account-name", "account_name")
    .put("azure-storage-account-key", "account_key")
    .build();

Catalog catalog = gravitinoClient.createCatalog("adls_catalog",
    Catalog.Type.FILESET,
    "A fileset catalog backed by Azure Data Lake Storage",
    catalogProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
gravitino_client: GravitinoClient = GravitinoClient(
    uri="http://localhost:8090", metalake_name="metalake")

catalog_properties = {
    "location": "abfss://container@account-name.dfs.core.windows.net/root",
    "azure-storage-account-name": "account_name",
    "azure-storage-account-key": "account_key",
}

catalog = gravitino_client.create_catalog(name="adls_catalog",
                                          catalog_type=Catalog.Type.FILESET,
                                          provider=None,
                                          comment="A fileset catalog backed by Azure Data Lake Storage",
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
  "name": "adls_schema",
  "comment": "A schema in the Azure Data Lake Storage fileset catalog",
  "properties": {
    "location": "abfss://container@account-name.dfs.core.windows.net/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/adls_catalog/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("adls_catalog");
SupportsSchemas supportsSchemas = catalog.asSchemas();

Map<String, String> schemaProperties = ImmutableMap.<String, String>builder()
    .put("location", "abfss://container@account-name.dfs.core.windows.net/root/schema")
    .build();

Schema schema = supportsSchemas.createSchema("adls_schema",
    "A schema in the Azure Data Lake Storage fileset catalog",
    schemaProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="adls_catalog")
catalog.as_schemas().create_schema(name="adls_schema",
                                   comment="A schema in the Azure Data Lake Storage fileset catalog",
                                   properties={"location": "abfss://container@account-name.dfs.core.windows.net/root/schema"})
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
  "storageLocation": "abfss://container@account-name.dfs.core.windows.net/root/schema/example_fileset",
  "properties": {
    "k1": "v1"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/adls_catalog/schemas/adls_schema/filesets
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = gravitinoClient.loadCatalog("adls_catalog");
FilesetCatalog filesetCatalog = catalog.asFilesetCatalog();

Map<String, String> filesetProperties = ImmutableMap.<String, String>builder()
    .put("k1", "v1")
    .build();

filesetCatalog.createFileset(
    NameIdentifier.of("adls_schema", "example_fileset"),
    "This is an example fileset",
    Fileset.Type.MANAGED,
    "abfss://container@account-name.dfs.core.windows.net/root/schema/example_fileset",
    filesetProperties);
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog: Catalog = gravitino_client.load_catalog(name="adls_catalog")
catalog.as_fileset_catalog().create_fileset(
    ident=NameIdentifier.of("adls_schema", "example_fileset"),
    type=Fileset.Type.MANAGED,
    comment="This is an example fileset",
    storage_location="abfss://container@account-name.dfs.core.windows.net/root/schema/example_fileset",
    properties={"k1": "v1"})
```

</TabItem>
</Tabs>

该 fileset 现在可以通过以下地址访问：
`gvfs://fileset/adls_catalog/adls_schema/example_fileset`，可从任何 GVFS 客户端访问。

## 访问 Fileset

### Java 客户端 jar 包

每个 Java 或基于 Hadoop 的客户端都需要 `gravitino-filesystem-hadoop3-runtime`（发布于
Maven Central），以及 Azure Data Lake Storage 文件系统实现。只有后者
会因环境而异：

| 环境                   | 提供 Azure Data Lake Storage 文件系统的 Jar 包                                                                                                                                                             |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 未安装 Hadoop          | [`gravitino-azure-bundle`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-azure-bundle)，一个包含 Azure Data Lake Storage 文件系统实现及其依赖的 fat jar |
| 已安装 Hadoop          | `hadoop-azure-${hadoop-version}.jar`、`azure-storage-7.0.1.jar` 和 `wildfly-openssl-1.0.7.Final.jar`，随 Hadoop 一起发布于 `${HADOOP_HOME}/share/hadoop/tools/lib`                                          |

完整的构件如下：

- [`gravitino-azure-bundle-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-azure-bundle)：
  一个包含 `gravitino-azure` 功能及其所有所需依赖的“fat”jar，
  例如 `hadoop-azure` 及其访问 ADLS 所需的包。在环境没有预先配置 Hadoop 时使用。
- [`gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-filesystem-hadoop3-runtime)：
  一个打包了 Gravitino 虚拟文件系统客户端的“fat”jar，已包含
  `gravitino-azure` 功能。Java 和基于 Hadoop 的客户端需要它来访问 Gravitino
  fileset。
- `hadoop-azure-${hadoop-version}.jar`、`azure-storage-7.0.1.jar` 和
  `wildfly-openssl-1.0.7.Final.jar`：用于 Azure Data Lake Storage 访问的标准 Hadoop 依赖，
  随 Hadoop 发布于 `${HADOOP_HOME}/share/hadoop/tools/lib`。在现有 Hadoop 环境中运行时，
  需自行提供。
- [`gravitino-azure-${gravitino-version}.jar`](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-azure)：
  一个仅包含 Azure 集成代码的“thin”jar。它已包含在上述两个 jar 中，
  因此不需要作为直接依赖，除非更倾向于自行管理所有 Hadoop 和 Azure
  依赖。

```xml
<!-- No Hadoop environment -->
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-azure-bundle</artifactId>
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
  <artifactId>hadoop-azure</artifactId>
  <version>${HADOOP_VERSION}</version>
</dependency>
<dependency>
  <groupId>org.apache.gravitino</groupId>
  <artifactId>gravitino-filesystem-hadoop3-runtime</artifactId>
  <version>${GRAVITINO_VERSION}</version>
</dependency>
```

:::note
不需要 thin `gravitino-azure` jar。其功能已包含在
`gravitino-azure-bundle` 和 `gravitino-filesystem-hadoop3-runtime` 中。
:::

### GVFS Java 客户端

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration) 的基础上，设置上表中的 Azure Data Lake Storage
属性。

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
conf.set("azure-storage-account-name", "account_name");
conf.set("azure-storage-account-key", "account_key");

Path filesetPath = new Path("gvfs://fileset/adls_catalog/adls_schema/example_fileset/new_dir");
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
    "/path/to/hadoop-azure-3.3.4.jar,"
    "/path/to/azure-storage-7.0.1.jar,"
    "/path/to/wildfly-openssl-1.0.7.Final.jar "
    "--master local[1] pyspark-shell"
)

spark = (SparkSession.builder
    .appName("adls_fileset")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    .config("spark.hadoop.azure-storage-account-name", "account_name")
    .config("spark.hadoop.azure-storage-account-key", "account_key")
    .config("spark.driver.memory", "2g")
    .config("spark.driver.port", "2048")
    .getOrCreate())

data = [("Alice", 25), ("Bob", 30), ("Cathy", 45)]
spark_df = spark.createDataFrame(data, schema=["Name", "Age"])
gvfs_path = "gvfs://fileset/adls_catalog/adls_schema/example_fileset/people"

spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(gvfs_path)
```

如果 Spark 在没有 Hadoop 环境的情况下运行，只需更改 jar 列表：

```python
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/gravitino-azure-bundle-${gravitino-version}.jar,"
    "/path/to/gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar "
    "--master local[1] pyspark-shell"
)
```

:::note
某些 Spark 版本在 driver 中需要 Hadoop 环境，并且不会加载通过
`--jars` 传递的文件系统实现。如果发生这种情况，请直接将 jar 添加到 Spark 类路径中。
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
  <name>azure-storage-account-name</name>
  <value>account_name</value>
</property>
<property>
  <name>azure-storage-account-key</name>
  <value>account_key</value>
</property>
```

2. 将这些 jar 添加到 Hadoop 类路径：

   - `gravitino-filesystem-hadoop3-runtime-${gravitino-version}.jar`，来自 Maven Central。
   - `hadoop-azure-${hadoop-version}.jar`、`azure-storage-7.0.1.jar` 和 `wildfly-openssl-1.0.7.Final.jar`，随 Hadoop 一起发布于 `${HADOOP_HOME}/share/hadoop/tools/lib`。

3. 访问 fileset：

```shell
${HADOOP_HOME}/bin/hadoop fs -ls gvfs://fileset/adls_catalog/adls_schema/example_fileset
${HADOOP_HOME}/bin/hadoop fs -put /path/to/local/file gvfs://fileset/adls_catalog/adls_schema/example_fileset
```

### GVFS Python 客户端

```bash
pip install apache-gravitino==${GRAVITINO_VERSION}
```

在 [基础 GVFS 配置](./how-to-use-gvfs.md#configuration-1) 的基础上，通过 `options` 传递 Azure Data Lake Storage
属性，使用下划线拼写。

```python
from gravitino import gvfs

options = {
    "cache_size": 20,
    "cache_expired_time": 3600,
    "auth_type": "simple",
    "azure_storage_account_name": "account_name",
    "azure_storage_account_key": "account_key",
}

fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
fs.ls("gvfs://fileset/adls_catalog/adls_schema/example_fileset/")
```

### pandas

pandas 通过 `storage_options` 访问相同的路径。使用前一个 GVFS 示例中的 `fs` 实例
来发现生成的 Spark part 文件。

```python
import pandas as pd

storage_options = {
    "server_uri": "http://localhost:8090",
    "metalake_name": "metalake",
    "options": {
        "azure_storage_account_name": "account_name",
        "azure_storage_account_key": "account_key",
    }
}

csv_path = next(
    f"gvfs://{path}"
    for path in fs.ls(
        "gvfs://fileset/adls_catalog/adls_schema/example_fileset/people",
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

启用凭证分发后，catalog 将持有 Azure Data Lake Storage 凭证，Gravitino 服务器会
按请求分发凭证，因此客户端无需持有自己的云密钥。参见
[Credential Vending](./security/credential-vending.md) 了解通用机制，并参见
[ADLS credentials](./security/credential-vending.md#adls) 了解每个提供器
所需的属性。

支持的提供器包括 `adls-token`（分发短效令牌）和
`azure-account-key`（分发 catalog 上配置的静态账户密钥）。以下示例
使用 `adls-token`。

### 配置 catalog、schema 和 fileset

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "adls_catalog_with_vending",
  "type": "FILESET",
  "comment": "A fileset catalog backed by Azure Data Lake Storage with credential vending",
  "properties": {
    "location": "abfss://container@account-name.dfs.core.windows.net/root",
    "azure-storage-account-name": "account_name",
    "azure-storage-account-key": "account_key",
    "credential-providers": "adls-token",
    "azure-tenant-id": "The Azure tenant id",
    "azure-client-id": "The Azure client id",
    "azure-client-secret": "The Azure client secret key"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs
```

在启用凭证分发的 catalog 中创建 schema 和 fileset：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "adls_schema",
  "comment": "A schema in the Azure Data Lake Storage credential-vending catalog",
  "properties": {
    "location": "abfss://container@account-name.dfs.core.windows.net/root/schema"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/adls_catalog_with_vending/schemas

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "example_fileset",
  "comment": "This is an example fileset",
  "type": "MANAGED",
  "storageLocation": "abfss://container@account-name.dfs.core.windows.net/root/schema/example_fileset",
  "properties": {}
}' http://localhost:8090/api/metalakes/metalake/catalogs/adls_catalog_with_vending/schemas/adls_schema/filesets
```

`adls-token` 提供器还需要三个 catalog 属性。

| 属性名称              | 描述                    |
|-----------------------|-------------------------|
| `azure-tenant-id`     | Azure 租户 ID           |
| `azure-client-id`     | Azure 客户端 ID         |
| `azure-client-secret` | Azure 客户端密钥        |

### 无本地凭证访问

在客户端启用分发并移除凭证属性。

```java
Configuration conf = new Configuration();
conf.setBoolean("fs.gravitino.enableCredentialVending", true);
conf.set("fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri", "http://localhost:8090");
conf.set("fs.gravitino.client.metalake", "metalake");
// 无需设置 azure-storage-account-name 或 azure-storage-account-key

Path filesetPath = new Path(
    "gvfs://fileset/adls_catalog_with_vending/adls_schema/example_fileset/new_dir");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.mkdirs(filesetPath);
```

```python
spark = (SparkSession.builder
    .appName("adls_fileset")
    .config("spark.hadoop.fs.gravitino.enableCredentialVending", "true")
    .config("spark.hadoop.fs.AbstractFileSystem.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.Gvfs")
    .config("spark.hadoop.fs.gvfs.impl", "org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem")
    .config("spark.hadoop.fs.gravitino.server.uri", "http://localhost:8090")
    .config("spark.hadoop.fs.gravitino.client.metalake", "metalake")
    # 无需设置 azure-storage-account-name 或 azure-storage-account-key
    .getOrCreate())
```

```python
options = {
    "auth_type": "simple",
    "enable_credential_vending": True,
    # 无需设置 azure-storage-account-name 或 azure-storage-account-key
}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090",
                                     metalake_name="metalake",
                                     options=options)
```