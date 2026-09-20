---
title: "Gravitino Virtual File System"
slug: "/how-to-use-gvfs"
license: "This software is licensed under the Apache License version 2."
---

## 简介

`Fileset` 是 Apache Gravitino 引入的一个概念，它是文件和
目录的逻辑集合，使用 `fileset` 你可以通过 Gravitino 管理非表格数据。有关
详情，你可以阅读[如何使用 Gravitino 管理 fileset 元数据](./manage-fileset-metadata-using-gravitino.md)。

要使用由 Gravitino 管理的 `fileset`，Gravitino 提供了一个虚拟文件系统层，称为
Gravitino 虚拟文件系统（GVFS）：
* 在 Java 中，它构建于 Hadoop 兼容文件系统（HCFS）接口之上。
* 在 Python 中，它构建于 [fsspec](https://filesystem-spec.readthedocs.io/en/stable/index.html)
接口之上。

GVFS 是一个虚拟层，它管理文件集中的文件和目录，通过一个虚拟
路径，而无需了解文件集的具体存储细节。您可以访问
如下所示的文件或文件夹：

```text
gvfs://fileset/${catalog_name}/${schema_name}/${fileset_name}/sub_dir/
```

在 python GVFS 中，您也可以访问文件或文件夹，如下所示：

```text
fileset/${catalog_name}/${schema_name}/${fileset_name}/sub_dir/
```

这里 `gvfs` 是 GVFS 的 scheme，`fileset` 是 GVFS 的根目录，无法被
修改，且 `${catalog_name}/${schema_name}/${fileset_name}` 是 fileset 的虚拟路径。
通过将文件或文件夹
名称拼接到该虚拟路径，以访问此虚拟路径下的文件和文件夹。

GVFS 的使用模式与 HDFS 或 S3 相同。GVFS 内部管理
路径映射并自动转换。

## 使用 Java GVFS 管理文件

### 先决条件

- GVFS 需要 Hadoop 3.3.1 或更高版本。

### 配置

| 配置项                                    | 描述                                                                                                                                                                                                                                                                                                                                                            | 默认值                                                  | 必填                            |
|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|-------------------------------------|
| `fs.AbstractFileSystem.gvfs.impl`                     | Gravitino 虚拟文件系统抽象类，将其设置为 `org.apache.gravitino.filesystem.hadoop.Gvfs`。                                                                                                                                                                                                                                                             | (无)                                                         | 是                                 |
| `fs.gvfs.impl`                                        | Gravitino 虚拟文件系统实现类，将其设置为 `org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem`。                                                                                                                                                                                                                                 | (无)                                                         | 是                                 |
| `fs.gvfs.impl.disable.cache`                          | 在 Hadoop 环境中禁用 Gravitino 虚拟文件系统缓存。如果需要代理多用户操作，请将此值设置为 `true` 并为每个用户创建单独的文件系统。                                                                                                                                                                       | `false`                                                        | 否                                  |
| `fs.gravitino.server.uri`                             | GVFS 加载 fileset 元数据所需的 Gravitino 服务器 URI。                                                                                                                                                                                                                                                                                                | (无)                                                         | 是                                 |
| `fs.gravitino.client.metalake`                        | fileset 所属的 metalake。                                                                                                                                                                                                                                                                                                                             | (无)                                                         | 是                                 |
| `fs.gravitino.client.authType`                        | Gravitino 客户端在 Gravitino 虚拟文件系统中使用的认证类型。支持 `simple`、`oauth2` 和 `kerberos`。                                                                                                                                                                                                                                           | `simple`                                                       | 否                                  |
| `fs.gravitino.client.oauth2.serverUri`                | 在 Gravitino 虚拟文件系统中使用 `oauth2` 认证类型时，Gravitino 客户端的认证服务器 URI。                                                                                                                                                                                                                                                     | (无)                                                         | 如果使用 `oauth2` 认证类型则为是   |
| `fs.gravitino.client.oauth2.credential`               | 在 Gravitino 虚拟文件系统中使用 `oauth2` 认证类型时，Gravitino 客户端的认证凭据。                                                                                                                                                                                                                                                       | (无)                                                         | 如果使用 `oauth2` 认证类型则为是   |
| `fs.gravitino.client.oauth2.path`                     | 在 Gravitino 虚拟文件系统中使用 `oauth2` 认证类型时，Gravitino 客户端的认证服务器路径。请移除路径中的第一个斜杠 `/`，例如 `oauth/token`。                                                                                                                                                                        | (无)                                                         | 如果使用 `oauth2` 认证类型则为是   |
| `fs.gravitino.client.oauth2.scope`                    | 在 Gravitino 虚拟文件系统中使用 `oauth2` 认证类型时，Gravitino 客户端的认证范围。                                                                                                                                                                                                                                                          | (无)                                                         | 如果使用 `oauth2` 认证类型则为是   |
| `fs.gravitino.client.kerberos.principal`              | 在 Gravitino 虚拟文件系统中使用 `kerberos` 认证类型时，Gravitino 客户端的认证主体。                                                                                                                                                                                                                                                    | (无)                                                         | 如果使用 `kerberos` 认证类型则为是 |
| `fs.gravitino.client.kerberos.keytabFilePath`         | 在 Gravitino 虚拟文件系统中使用 `kerberos` 认证类型时，Gravitino 客户端的认证 keytab 文件路径。                                                                                                                                                                                                                                               | (none)                                                         | 否                                  |
| `fs.gravitino.fileset.cache.maxCapacity`              | Gravitino 虚拟文件系统的缓存容量。                                                                                                                                                                                                                                                                                                               | `20`                                                           | 否                                  |
| `fs.gravitino.fileset.cache.evictionMillsAfterAccess` | 在 Gravitino 虚拟文件系统中，缓存在访问后过期的时间值。该值以 `milliseconds` 为单位。                                                                                                                                                                                                                                         | `3600000`                                                      | 否                                  |
| `fs.gravitino.fileset.cache.closeOnEviction`          | 是否在缓存驱逐时立即关闭底层 FileSystem。默认为 `false`：关闭操作会推迟到 GVFS 关闭时执行，以避免破坏长生命周期的流。设置为 `true` 可回退到传统行为（驱逐时立即关闭）。                                                                                                           | `false`                                                        | 否                                  |
| `fs.gravitino.current.location.name`                  | 用于选择 fileset 位置的配置。如果未设置此配置，将检查由 `fs.gravitino.current.location.name.env.var` 配置的环境变量的值。如果两者均未设置，将使用 fileset 属性 `default-location-name` 的值作为位置名称。                                              | fileset 属性 `default-location-name` 的值          | 否                                  |
| `fs.gravitino.current.location.name.env.var`          | 用于获取当前位置名称的环境变量名称。                                                                                                                                                                                                                                                                                                        | `CURRENT_LOCATION_NAME`                                        | 否                                  |
| `fs.gravitino.operations.class`                       | 为 Gravitino 虚拟文件系统提供 FS 操作的操作类。用户可以扩展 `BaseGVFSOperations` 来实现自己的操作，并在此配置中配置类名以使用自定义的 FS 操作。                                                                                                                               | `org.apache.gravitino.filesystem.hadoop.DefaultGVFSOperations` | 否                                  |
| `fs.gravitino.hook.class`                             | 要注入到 <br/>Gravitino 虚拟文件系统中的 hook 类。用户可以实现自己的 `GravitinoVirtualFileSystemHook`，并在此配置中配置类名以注入自定义代码。                                                                                                                                                                  | `org.apache.gravitino.filesystem.hadoop.NoOpHook`              | 否                                  |
| `fs.gravitino.client.request.header.`                 | Gravitino 客户端请求头的配置键前缀。您可以为 Gravitino 客户端设置请求头。                                                                                                                                                                                                                                         | (none)                                                         | 否                                  |
| `fs.gravitino.enableCredentialVending`                | 是否为 Gravitino 虚拟文件系统启用凭据分发。                                                                                                                                                                                                                                                                                            | `false`                                                        | 否                                  |
| `fs.gravitino.client.`                                | Gravitino 客户端配置的配置键前缀。                                                                                                                                                                                                                                                                                                          | (none)                                                         | 否                                  |
| `fs.gravitino.filesetMetadataCache.enable`            | 是否在 Gravitino 虚拟文件系统中缓存 fileset、fileset schema 或 fileset catalog 元数据。请注意，此缓存会产生副作用：如果您修改了 fileset 或 fileset catalog 元数据，客户端将无法看到最新的更改。                                                                                                             | `false`                                                        | 否                                  |
| `fs.gravitino.autoCreateLocation`                     | 当服务端文件系统操作被禁用且位置不存在时，是否启用自动创建 fileset 位置的配置键。                                                                                                                                                                                                        | `true`                                                         | 否                                  |
| `fs.path.config.<name>`                               | 定义一个逻辑位置条目。将 `fs.path.config.<name>` 设置为真实的基础 URI（例如，`hdfs://cluster1/`）。任何以相同前缀开头的键（例如 `fs.path.config.<name>.config.resource`）都将被视为位置范围的属性，并被转发到底层文件系统客户端。注意：位置名称不能包含（`.`，`_`）。 | (none)                                                         | 否                                  |

要配置 Gravitino 客户端，请使用以 `fs.gravitino.client.` 为前缀的属性。这些属性在移除 `fs.` 前缀后将被传递给 Gravitino 客户端。

:::note
当用户使用多集群文件集目录时，他们可以为基础路径配置单独的属性集
针对不同集群，使用上述 `fs.path.config.<name>` 属性。

例如，一个复杂的目录结构可能如下所示：

```text
catalog1 -> hdfs://cluster1/catalog1
    schema1 -> hdfs://cluster1/catalog1/schema1
        fileset1 -> hdfs://cluster1/catalog1/schema1/fileset1
        fileset2 -> hdfs://cluster1/catalog1/schema1/fileset2
    schema2 -> hdfs://cluster2/tmp/schema2
        fileset3 -> hdfs://cluster2/tmp/schema2/fsd
        fileset4 -> hdfs://cluster3/customers
```

在这种情况下，用户可以为每个基础路径配置不同的客户端属性：

```text
fs.path.config.cluster1 = hdfs://cluster1/
fs.path.config.cluster1.config.resource= /etc/core-site.xml,/etc/hdfs-site.xml

fs.path.config.cluster2 = hdfs://cluster2/
fs.path.config.cluster2.config.resource= /etc/fs2/core-site.xml,/etc/fs2/hdfs-site.xml

fs.path.config.cluster3 = hdfs://cluster3/
fs.path.config.cluster3.config.resource=/etc/fs3/core-site.xml,/etc/fs3/hdfs-site.xml
```

简单的 `fs.path.config.<name>` 条目指定文件系统的基础路径。同一前缀下的任何附加键（`fs.path.config.<name>.<config_key>`）都会被视为位置范围的配置（例如，HDFS 的 `config.resource`），并直接转发给底层文件系统客户端。
:::

**示例：** 设置 `fs.gravitino.client.socketTimeoutMs` 等同于为 Gravitino 客户端设置 `gravitino.client.socketTimeoutMs`。

**注意：** 无效的配置属性会导致异常。请参阅 [Gravitino Java 客户端配置](./how-to-use-gravitino-client.md#java-client-configuration) 以获取更多支持的客户端配置。

由云存储支持的文件集需要该后端的凭证属性，以及
上述属性，并且 classpath 中需要相应的 bundle jar。参见
[Amazon S3](./fileset-catalog-with-s3.md#amazon-s3-properties)，
[Google Cloud Storage](./fileset-catalog-with-gcs.md#google-cloud-storage-properties)，
[Azure Data Lake Storage](./fileset-catalog-with-adls.md#azure-data-lake-storage-properties)，
[Alibaba Cloud OSS](./fileset-catalog-with-oss.md#alibaba-cloud-oss-properties) 和
[Tencent Cloud COS](./fileset-catalog-with-cos.md#tencent-cloud-cos-properties) 以查看属性
名称和每个后端的可运行示例。

#### 自定义文件集

用户可以定义自己的 fileset 类型并配置相应的
属性，更多信息请参考 [自定义 Fileset](./fileset-catalog.md#implement-a-custom-hcfs-file-system-fileset)。
因此，如果你想通过 GVFS 访问自定义的 fileset，你需要配置相应的属性。

| 配置项       | 描述                                                                                             | 默认值 | 必填 |
|--------------------------|---------------------------------------------------------------------------------------------------------|---------------|----------|
| `your-custom-properties` | 这些属性将用于在 `CustomFileSystemProvider#getFileSystem` 中创建一个 FileSystem 实例 | (none)        | 否       |

通过两种方式配置这些属性：

1. 在代码中获取 `FileSystem` 之前，构造一个 `Configuration` 对象并设置其属性：

    ```java
    Configuration conf = new Configuration();
    conf.set("fs.AbstractFileSystem.gvfs.impl","org.apache.gravitino.filesystem.hadoop.Gvfs");
    conf.set("fs.gvfs.impl","org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
    conf.set("fs.gravitino.server.uri","http://localhost:8090");
    conf.set("fs.gravitino.client.metalake","test_metalake");
    Path filesetPath = new Path("gvfs://fileset/test_catalog/test_schema/test_fileset_1");
    FileSystem fs = filesetPath.getFileSystem(conf);
    ```

2. 在 Hadoop 环境的 `core-site.xml` 文件中配置属性：

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
        <value>test_metalake</value>
      </property>
    ```

### 示例

首先确保获取 Gravitino Virtual File System 运行时 jar 包，你可以通过
两种方式：

1. 从 Maven 中央仓库下载。您可以下载名为
`gravitino-filesystem-hadoop3-runtime-{version}.jar` 的 runtime jar，从 [Maven repository](https://mvnrepository.com/) 下载。

2. 从源代码编译：

下载或克隆 [Gravitino 源代码](https://github.com/apache/gravitino)，并进行编译
在 Gravitino 源代码目录中，使用以下命令在本地进行：

    ```shell
       ./gradlew :clients:filesystem-hadoop3-runtime:build -x test
    ```

:::note
对于具有多个位置的文件集，您可以使用以下方法之一（按优先级顺序）指定要访问的位置：
1. 设置 `fs.gravitino.current.location.name` 配置属性
2. 导出环境变量 `CURRENT_LOCATION_NAME`
3. 如果两者均未指定，系统将使用文件集属性中的 `default-location-name` 值
:::

#### 通过 Hadoop Shell 命令

使用 Hadoop shell 命令对 fileset 存储执行操作。例如：

```shell
# 1. Configure the hadoop `core-site.xml` configuration
# You should put the required properties into this file

# set the location name if you want to access a specific location
# export CURRENT_LOCATION_NAME=${the_fileset_location_name}
vi ${HADOOP_HOME}/etc/hadoop/core-site.xml

# 2. Place the GVFS runtime jar into your Hadoop environment
cp gravitino-filesystem-hadoop3-runtime-{version}.jar ${HADOOP_HOME}/share/hadoop/common/lib/

# 3. Complete the Kerberos authentication setup of the Hadoop environment (if necessary).
# You need to ensure that the Kerberos has permission on the HDFS directory.
kinit -kt your_kerberos.keytab your_kerberos@xxx.com

# 4. Try to list the fileset
./${HADOOP_HOME}/bin/hadoop dfs -ls gvfs://fileset/test_catalog/test_schema/test_fileset_1
```

#### 通过 Java 代码

通过 Java 代码对由 fileset 管理的文件或目录执行操作。
确保你的代码使用了正确的 Hadoop 环境，并且你的环境
包含 `gravitino-filesystem-hadoop3-runtime-{version}.jar` 依赖。

例如：

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl","org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl","org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri","http://localhost:8090");
conf.set("fs.gravitino.client.metalake","test_metalake");
// set the location name if you want to access a specific location
// conf.set("fs.gravitino.current.location.name","test_location_name");
Path filesetPath = new Path("gvfs://fileset/test_catalog/test_schema/test_fileset_1");
FileSystem fs = filesetPath.getFileSystem(conf);
fs.getFileStatus(filesetPath);
```

#### 通过 Apache Spark

1. 将 GVFS 运行时 jar 包添加到 Spark 环境中。

你可以在 Spark submit shell 中使用 `--packages` 或 `--jars` 来包含 Gravitino 虚拟
文件系统运行时 jar，如下所示：

    ```shell
    ./${SPARK_HOME}/bin/spark-submit --packages org.apache.gravitino:gravitino-filesystem-hadoop3-runtime:${version}
    ```

如果你想在 Spark 安装中包含 Gravitino Virtual File System 运行时 jar 包，请将其添加到 `${SPARK_HOME}/jars/` 文件夹中。

2. 提交作业时配置 Hadoop 配置。

你可以按以下方式在 shell 命令中进行配置：

    ```shell
    --conf spark.hadoop.fs.AbstractFileSystem.gvfs.impl=org.apache.gravitino.filesystem.hadoop.Gvfs
    --conf spark.hadoop.fs.gvfs.impl=org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem
    --conf spark.hadoop.fs.gravitino.server.uri=${your_gravitino_server_uri}
    --conf spark.hadoop.fs.gravitino.client.metalake=${your_gravitino_metalake}
    # set the location name if you want to access a specific location
    # --conf spark.hadoop.fs.gravitino.current.location.name=${the_fileset_location_name}
    ```

3. 在您的代码中对 fileset 存储执行操作。

最后，您可以在 Spark 程序中访问 fileset 存储：

    ```scala
    // Scala code
    val spark = SparkSession.builder()
          .appName("Gvfs Example")
          .getOrCreate()

    val rdd = spark.sparkContext.textFile("gvfs://fileset/test_catalog/test_schema/test_fileset_1")

    rdd.foreach(println)
    ```

#### 通过 TensorFlow

要让 Tensorflow 支持 GVFS，你需要重新编译 [tensorflow-io](https://github.com/tensorflow/io) 模块。

1. 首先，添加一个补丁并重新编译 tensorflow-io。

你需要添加一个 [patch](https://github.com/tensorflow/io/pull/1970) 来支持 GVFS 在
tensorflow-io 上。然后你可以按照 [tutorial](https://github.com/tensorflow/io/blob/master/docs/development.md)
来重新编译你的代码并发布 tensorflow-io 模块。

2. 然后你需要配置 Hadoop 配置。

你需要配置 Hadoop 配置并添加 `gravitino-filesystem-hadoop3-runtime-{version}.jar`，
并根据 [通过 Hadoop shell 命令使用 GVFS](#via-hadoop-shell-command) 章节设置 Kerberos 环境。

然后你需要将你的环境设置如下：

   ```shell
   export HADOOP_HOME=${your_hadoop_home}
   export HADOOP_CONF_DIR=${your_hadoop_conf_home}
   # set the location name if you want to access a specific location
   # export CURRENT_LOCATION_NAME=${the_fileset_location_name}
   export PATH=$PATH:$HADOOP_HOME/libexec/hadoop-config.sh
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$JAVA_HOME/jre/lib/amd64/server
   export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
   export CLASSPATH="$(hadoop classpath --glob)"
   ```

3. 导入 tensorflow-io 并进行测试。

   ```python
   import tensorflow as tf
   import tensorflow_io as tfio

   ## read a file
   print(tf.io.read_file('gvfs://fileset/test_catalog/test_schema/test_fileset_1/test.txt'))

   ## list directory
   print(tf.io.gfile.listdir('gvfs://fileset/test_catalog/test_schema/test_fileset_1/'))
   ```

### 身份验证

Gravitino 虚拟文件系统支持两种访问 Gravitino 服务器的认证类型：`simple` 和 `oauth2`。

`simple` 类型是 Gravitino 虚拟文件系统的默认认证类型。

#### `simple` 身份验证

首先，确保您的 Gravitino 服务器也配置为使用 `simple` 身份验证模式。

然后，您可以像这样配置 Hadoop：

```java
// Simple type uses the environment variable `GRAVITINO_USER` as the client user.
// If the environment variable `GRAVITINO_USER` isn't set,
// the client uses the user of the machine that sends requests.
System.setProperty("GRAVITINO_USER", "test");

Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl","org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl","org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri","http://localhost:8090");
conf.set("fs.gravitino.client.metalake","test_metalake");
// Configure the auth type to simple,
// or do not configure this configuration, gvfs will use simple type as default.
conf.set("fs.gravitino.client.authType", "simple");
Path filesetPath = new Path("gvfs://fileset/test_catalog/test_schema/test_fileset_1");
FileSystem fs = filesetPath.getFileSystem(conf);
```

#### `OAuth` 认证

如果您想在 Gravitino 虚拟文件系统中为 Gravitino 客户端使用 `oauth2` 认证，
请参阅此文档以完成 Gravitino 服务器和 OAuth 服务器的配置：[Security](security/how-to-authenticate.md)。

然后，您可以像这样配置 Hadoop：

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl","org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl","org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri","http://localhost:8090");
conf.set("fs.gravitino.client.metalake","test_metalake");
// Configure the auth type to oauth2.
conf.set("fs.gravitino.client.authType", "oauth2");
// Configure the OAuth configuration.
conf.set("fs.gravitino.client.oauth2.serverUri", "${your_oauth_server_uri}");
conf.set("fs.gravitino.client.oauth2.credential", "${your_client_credential}");
conf.set("fs.gravitino.client.oauth2.path", "${your_oauth_server_path}");
conf.set("fs.gravitino.client.oauth2.scope", "${your_client_scope}");
Path filesetPath = new Path("gvfs://fileset/test_catalog/test_schema/test_fileset_1");
FileSystem fs = filesetPath.getFileSystem(conf);
```

#### `Kerberos` 身份验证

如果您想在 Gravitino 虚拟文件系统中为 Gravitino 客户端使用 `kerberos` 认证，
请参阅此文档以完成 Gravitino 服务器的配置：[Security](security/how-to-authenticate.md)。

然后，您可以像这样配置 Hadoop：

```java
Configuration conf = new Configuration();
conf.set("fs.AbstractFileSystem.gvfs.impl","org.apache.gravitino.filesystem.hadoop.Gvfs");
conf.set("fs.gvfs.impl","org.apache.gravitino.filesystem.hadoop.GravitinoVirtualFileSystem");
conf.set("fs.gravitino.server.uri","http://localhost:8090");
conf.set("fs.gravitino.client.metalake","test_metalake");
// Configure the auth type to kerberos.
conf.set("fs.gravitino.client.authType", "kerberos");
// Configure the Kerberos configuration.
conf.set("fs.gravitino.client.kerberos.principal", "${your_kerberos_principal}");
// Optional. You don't need to set the keytab if you use kerberos ticket cache.
conf.set("fs.gravitino.client.kerberos.keytabFilePath", "${your_kerberos_keytab}");
Path filesetPath = new Path("gvfs://fileset/test_catalog/test_schema/test_fileset_1");
FileSystem fs = filesetPath.getFileSystem(conf);
```

## 使用 Python GVFS 管理文件

### 先决条件

+ 包含 HDFS 或其他 Hadoop 兼容文件系统 (HCFS) 实现（例如 S3 或 GCS）的 Hadoop 环境。GVFS 需要 Hadoop 3.3.1 或更高版本。
+ Python 3.12 或更高版本。

注意：如果您使用的是 macOS 或 Windows 操作系统，您需要按照
[Hadoop 官方构建文档](https://github.com/apache/hadoop/blob/trunk/BUILDING.txt)（需要与您的 Hadoop 版本匹配）
中的步骤重新编译 `libhdfs` 等本地库，并完全替换 `${HADOOP_HOME}/lib/native` 中的文件。

### 配置

| 配置项              | 描述                                                                                                                                                                                                                                                                                                                                                            | 默认值                                                        | 必填                          |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|-----------------------------------|
| `server_uri`                    | Gravitino 服务器 uri，例如 `http://localhost:8090`。                                                                                                                                                                                                                                                                                                                | (无)                                                               | 是                               |
| `metalake_name`                 | 文件集所属的 metalake 名称。                                                                                                                                                                                                                                                                                                                        | (无)                                                               | 是                               |
| `cache_size`                    | Gravitino 虚拟文件系统的缓存容量。                                                                                                                                                                                                                                                                                                               | `20`                                                                 | 否                                |
| `cache_expired_time`            | 在 Gravitino 虚拟文件系统中，缓存访问后过期的时间值。该值以 `seconds` 为单位。                                                                                                                                                                                                                                              | `3600`                                                               | 否                                |
| `auth_type`                     | Gravitino 客户端在 Gravitino 虚拟文件系统中使用的认证类型。支持 `simple`、`basic` 和 `oauth2`。                                                                                                                                                                                                                                              | `simple`                                                             | 否                                |
| `basic_username`                | 当使用 `basic` 认证类型和本地用户存储时，Gravitino 客户端的用户名。                                                                                                                                                                                                                                                                          | (无)                                                               | 如果使用 `basic` 认证类型则为是  |
| `basic_password`                | 当使用 `basic` 认证类型和本地用户存储时，Gravitino 客户端的密码。                                                                                                                                                                                                                                                                          | (无)                                                               | 如果使用 `basic` 认证类型则为是  |
| `oauth2_server_uri`             | 当使用 `oauth2` 认证类型时，Gravitino 客户端的认证服务器 URI。                                                                                                                                                                                                                                                                                            | (无)                                                               | 如果使用 `oauth2` 认证类型则为是 |
| `oauth2_credential`             | 当使用 `oauth2` 认证类型时，Gravitino 客户端的认证凭据。                                                                                                                                                                                                                                                                                            | (无)                                                               | 如果使用 `oauth2` 认证类型则为是 |
| `oauth2_path`                   | 当使用 `oauth2` 认证类型时，Gravitino 客户端的认证服务器路径。请移除路径中的第一个斜杠 `/`，例如 `oauth/token`。                                                                                                                                                                                                               | (无)                                                               | 如果使用 `oauth2` 认证类型则为是 |
| `oauth2_scope`                  | 当使用 `oauth2` 认证类型和 Gravitino 虚拟文件系统时，Gravitino 客户端的认证范围。                                                                                                                                                                                                                                                          | (无)                                                               | 如果使用 `oauth2` 认证类型则为是 |
| `credential_expiration_ratio`   | 来自 Gravitino 的凭证过期时间比例。这用于 Gravitino Fileset 目录启用了凭证分发的情况。如果从 Gravitino 获取的凭证过期时间为 1 小时，GVFS 客户端将尝试在 1 * 0.9 = 0.5 小时内刷新凭证。                                                                    | 0.5                                                                  | No                                |
| `current_location_name`         | 用于选择 fileset 位置的配置。如果未设置此配置，将检查由 `current_location_name_env_var` 配置的环境变量的值。如果两者均未设置，则将使用 fileset 属性 `default-location-name` 的值作为位置名称。                                                           | the value of fileset property `default-location-name`                | No                                |
| `current_location_name_env_var` | 用于获取当前位置名称的环境变量名称。                                                                                                                                                                                                                                                                                                        | `CURRENT_LOCATION_NAME`                                              | No                                |
| `operations_class`              | 为 Gravitino 虚拟文件系统提供 FS 操作的操作类。用户可以继承 `BaseGVFSOperations` 来实现自己的操作，并在此配置中配置类名以使用自定义的 FS 操作。                                                                                                                               | `gravitino.filesystem.gvfs_default_operations.DefaultGVFSOperations` | No                                |
| `hook_class`                    | 要注入到 Gravitino 虚拟文件系统中的钩子类。用户可以实现自己的 `GravitinoVirtualFileSystemHook`，并在此配置中配置类名以注入自定义代码。                                                                                                                                                                       | `gravitino.filesystem.gvfs_hook.NoOpHook`                            | No                                |
| `client_request_header_`        | Gravitino 客户端请求头的配置键前缀。您可以为 Gravitino 客户端设置请求头。                                                                                                                                                                                                                                         | (none)                                                               | No                                |
| `enable_credential_vending`     | 是否为 Gravitino 虚拟文件系统启用凭证分发。                                                                                                                                                                                                                                                                                            | `false`                                                              | No                                |
| `gvfs_gravitino_client_`        | Gravitino 客户端的配置键前缀。您可以为 Gravitino 客户端设置配置。                                                                                                                                                                                                                                                                | (none)                                                               | No                                |
| `enable_fileset_metadata_cache` | 是否在 Gravitino 虚拟文件系统中缓存 fileset 或 fileset 目录元数据。请注意，此缓存会导致副作用：如果您修改 fileset 或 fileset 目录元数据，客户端将无法看到最新更改。                                                                                                                             | `false`                                                              | No                                |
| `auto_create_location`          | 用于在禁用服务器端文件系统操作且位置不存在时，是否启用自动创建 fileset 位置的配置键。                                                                                                                                                                                                        | `true`                                                               | No                                |
| `fs_path_config_<name>`         | 定义一个逻辑位置条目。将 `fs_path_config_<name>` 设置为真实的基础 URI（例如，`hdfs://cluster1/`）。任何以相同前缀开头的键（例如 `fs_path_config_<name>_config.resource`）都将被视为位置范围的属性，并转发给底层文件系统客户端。注意：位置名称不能包含（`.`，`_`）。 | (none)                                                               | No                                |

要配置 Gravitino 客户端，请使用以 `gvfs_gravitino_client_` 为前缀的属性。这些属性在移除 `gvfs_` 前缀后将传递给 Gravitino 客户端。

**示例：** 设置 `gvfs_gravitino_client_request_timeout` 相当于为 Gravitino 客户端设置 `gravitino_client_request_timeout`。

**注意：** 无效的配置属性将导致异常。有关更多支持的客户端配置，请参阅 [Gravitino Python 客户端配置](./how-to-use-gravitino-client.md#python-client-configuration)。

:::note
当用户使用多集群文件集目录时，他们可以为基本路径配置单独的属性集
针对不同集群，使用上述 `fs_path_config_<name>` 属性。

例如，一个复杂的目录结构可能如下所示：

```text
catalog1 -> hdfs://cluster1/catalog1
    schema1 -> hdfs://cluster1/catalog1/schema1
        fileset1 -> hdfs://cluster1/catalog1/schema1/fileset1
        fileset2 -> hdfs://cluster1/catalog1/schema1/fileset2
    schema2 -> hdfs://cluster2/tmp/schema2
        fileset3 -> hdfs://cluster2/tmp/schema2/fsd
        fileset4 -> hdfs://cluster3/customers
```

在这种情况下，用户可以为每个基础路径配置不同的客户端属性：

```python
options = {
    "server_uri": "http://localhost:8090",
    "metalake_name": "test",
    "fs_path_config_cluster1": "hdfs://cluster1/",
    "fs_path_config_cluster1_config.resource": "/etc/core-site.xml,/etc/hdfs-site.xml",
    "fs_path_config_cluster2": "hdfs://cluster2/",
    "fs_path_config_cluster2_config.resource": "/etc/fs2/core-site.xml,/etc/fs2/hdfs-site.xml",
    "fs_path_config_cluster3": "hdfs://cluster3/",
    "fs_path_config_cluster3_config.resource": "/etc/fs3/core-site.xml,/etc/fs3/hdfs-site.xml",
}
```

普通的 `fs_path_config_<name>` 条目指定了文件系统的基础路径。相同前缀（`fs_path_config_<name>_<config_key>`）下的任何附加键都被视为基于位置的配置（例如，HDFS 的 `config.resource`），并直接转发给底层文件系统客户端。
:::

#### 云存储文件集的配置

由云存储支持的文件集需要该后端的凭证属性，拼写时使用
下划线而不是连字符。参见
[Amazon S3](./fileset-catalog-with-s3.md#amazon-s3-properties)，
[Google Cloud Storage](./fileset-catalog-with-gcs.md#google-cloud-storage-properties)，
[Azure Data Lake Storage](./fileset-catalog-with-adls.md#azure-data-lake-storage-properties)，
[Alibaba Cloud OSS](./fileset-catalog-with-oss.md#alibaba-cloud-oss-properties) 和
[Tencent Cloud COS](./fileset-catalog-with-cos.md#tencent-cloud-cos-properties) 以获取属性
名称以及每个后端的可运行示例。

:::note
由于 `fsspec` 库的限制，Gravitino Python 客户端不支持用户定义的[自定义文件系统](fileset-catalog.md#implement-a-custom-hcfs-file-system-fileset)。
:::

### 示例

:::note
对于具有多个位置的文件集，您可以使用以下方法之一（按优先级顺序）指定要访问的位置：
1. 设置 `current_location_name` 配置属性
2. 导出环境变量 `CURRENT_LOCATION_NAME`
3. 如果两者均未指定，系统将使用文件集属性中的 `default-location-name` 值
:::

1. 确保获取 Gravitino 库。
你可以通过 [pip](https://pip.pypa.io/en/stable/installation/) 获取它：

    ```shell
    pip install apache-gravitino
    ```

2. 配置 Hadoop 环境。
您应确保 Python 客户端具有 Kerberos 认证信息，并且
在系统环境中配置 Hadoop 环境：

    ```shell
    # kinit kerberos
    kinit -kt /tmp/xxx.keytab xxx@HADOOP.COM
    # Or you can configure kerberos information in the Hadoop `core-site.xml` file
    <property>
      <name>hadoop.security.authentication</name>
      <value>kerberos</value>
    </property>

    <property>
      <name>hadoop.client.kerberos.principal</name>
      <value>xxx@HADOOP.COM</value>
    </property>

    <property>
      <name>hadoop.client.keytab.file</name>
      <value>/tmp/xxx.keytab</value>
    </property>

   <!-- Optional, if you want to access a specific location -->
   <property>
      <name>fs.gravitino.current.location.name</name>
      <value>location-name</value>
   </property>

    # Configure Hadoop env in Linux
    export HADOOP_HOME=${YOUR_HADOOP_PATH}
    export HADOOP_CONF_DIR=${YOUR_HADOOP_PATH}/etc/hadoop
    export CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`
    ```

#### 通过 Fsspec 风格的接口

使用 fsspec 风格的接口对 fileset 文件执行操作。

例如：

```python
from gravitino import gvfs

# init the gvfs
fs = gvfs.GravitinoVirtualFileSystem(
   server_uri="http://localhost:8090",
   metalake_name="test_metalake",
   # set the location name if you want to access a specific location
   options={"current_location_name": "the_location_name"})

# list file infos under the fileset
fs.ls(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir")

# get file info under the fileset
fs.info(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test.parquet")

# check a file or a directory whether exists
fs.exists(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir")

# write something into a file
with fs.open(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test.txt", mode="wb") as output_stream:
    output_stream.write(b"hello world")

# append something into a file
with fs.open(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test.txt", mode="ab") as append_stream:
    append_stream.write(b"hello world")

# read something from a file
with fs.open(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test.txt", mode="rb") as input_stream:
    input_stream.read()

# copy a file
fs.cp_file(path1="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test.txt",
           path2="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test-1.txt")

# delete a file
fs.rm_file(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/ttt/test-1.txt")

# two methods to create a directory
fs.makedirs(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir_2")

fs.mkdir(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir_3")

# delete a file or a directory recursively
fs.rm(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir_2", recursive=True)

# delete a directory
fs.rmdir(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir_2")

# move a file or a directory
fs.mv(path1="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test-1.txt",
      path2="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/sub_dir/test-2.txt")

# get the content of a file
fs.cat_file(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test-1.txt")

# copy a remote file to local
fs.get_file(rpath="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test-1.txt",
            lpath="/tmp/local-file-1.txt")
```

#### 与第三方 Python 库集成

对 fileset 管理的文件或目录执行操作
与一些支持 fsspec 兼容文件系统的第三方 Python 库集成。

例如：
1. 与 [Pandas](https://pandas.pydata.org/docs/reference/io.html)(2.0.3) 集成。

```python
from gravitino import gvfs
import pandas as pd

data = pd.DataFrame({'Name': ['A', 'B', 'C', 'D'], 'ID': [20, 21, 19, 18]})
storage_options = {'server_uri': 'http://localhost:8090', 'metalake_name': 'test_metalake'}
# save data to a parquet file under the fileset
data.to_parquet('gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.parquet', storage_options=storage_options)

# read data from a parquet file under the fileset
ds = pd.read_parquet(path="gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.parquet",
                     storage_options=storage_options)
print(ds)

# save data to a csv file under the fileset
data.to_csv('gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.csv', storage_options=storage_options)

# save data from a csv file under the fileset
df = pd.read_csv('gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.csv', storage_options=storage_options)
print(df)
```

2. 与 [PyArrow](https://arrow.apache.org/docs/python/filesystems.html)(15.0.2) 集成。

```python
from gravitino import gvfs
import pyarrow.dataset as dt
import pyarrow.parquet as pq

fs = gvfs.GravitinoVirtualFileSystem(
    server_uri="http://localhost:8090",
    metalake_name="test_metalake",
    # set the location name if you want to access a specific location
    options={"current_location_name": "the_location_name"}
)

# read a parquet file as arrow dataset
arrow_dataset = dt.dataset("gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.parquet", filesystem=fs)

# read a parquet file as arrow parquet table
arrow_table = pq.read_table("gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.parquet", filesystem=fs)
```

3. 与 [Ray](https://docs.ray.io/en/latest/data/loading-data.html#loading-data)(2.10.0) 集成。

```python
from gravitino import gvfs
import ray

fs = gvfs.GravitinoVirtualFileSystem(
    server_uri="http://localhost:8090",
    metalake_name="test_metalake",
    # set the location name if you want to access a specific location
    options={"current_location_name": "the_location_name"},
)

# read a parquet file as ray dataset
ds = ray.data.read_parquet("gvfs://fileset/fileset_catalog/tmp/tmp_fileset/test.parquet",fs)
```

4. 与 [LlamaIndex](https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader/#support-for-external-filesystems)(0.10.40) 集成。

```python
from gravitino import gvfs
from llama_index.core import SimpleDirectoryReader

fs = gvfs.GravitinoVirtualFileSystem(
   server_uri=server_uri,
   metalake_name=metalake_name,
   # set the location name if you want to access a specific location
   options={"current_location_name": "the_location_name"},
)

# read all document files like csv files under the fileset sub dir
reader = SimpleDirectoryReader(
    input_dir='fileset/fileset_catalog/tmp/tmp_fileset/sub_dir',
    fs=fs,
    recursive=True,  # recursively searches all subdirectories
)
documents = reader.load_data()
print(documents)
```

### 身份验证

Python 中的 Gravitino 虚拟文件系统支持三种访问 Gravitino 服务器的认证类型：`simple`、`basic` 和 `oauth2`。

`simple` 类型是 Python 中 Gravitino 虚拟文件系统的默认认证类型。

#### `simple` 身份验证

首先，确保您的 Gravitino 服务器也配置为使用 `simple` 身份验证模式。

然后，您可以像这样配置身份验证：

```python
from gravitino import gvfs

options = {"auth_type": "simple"}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090", metalake_name="test_metalake", options=options)
print(fs.ls("gvfs://fileset/fileset_catalog/tmp/test_fileset"))
```

#### `basic` 认证

首先，请确保您的 Gravitino 服务器也配置为使用 `basic` 身份验证模式。
有关服务器端设置，请参阅[如何进行身份验证](security/how-to-authenticate.md#basic-mode)。

然后，您可以像这样配置身份验证：

```python
from gravitino import gvfs
from gravitino.filesystem.gvfs_config import GVFSConfig

options = {
    GVFSConfig.AUTH_TYPE: GVFSConfig.BASIC_AUTH_TYPE,
    GVFSConfig.BASIC_USERNAME: "admin",
    GVFSConfig.BASIC_PASSWORD: "YourSecureGravitinoPassword",
}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090", metalake_name="test_metalake", options=options)
print(fs.ls("gvfs://fileset/fileset_catalog/tmp/test_fileset"))
```

#### `OAuth` 认证

首先，确保你的 Gravitino 服务器也配置为使用 `oauth2` 身份验证模式，
并且你有一个用于获取令牌的 OAuth 服务器：[Security](security/how-to-authenticate.md)。

然后，您可以像这样配置身份验证：

```python
from gravitino import gvfs

options = {
    GVFSConfig.AUTH_TYPE: GVFSConfig.OAUTH2_AUTH_TYPE,
    GVFSConfig.OAUTH2_SERVER_URI: "http://127.0.0.1:1082",
    GVFSConfig.OAUTH2_CREDENTIAL: "xx:xx",
    GVFSConfig.OAUTH2_SCOPE: "test",
    GVFSConfig.OAUTH2_PATH: "token/test",
}
fs = gvfs.GravitinoVirtualFileSystem(server_uri="http://localhost:8090", metalake_name="test_metalake", options=options)
print(fs.ls("gvfs://fileset/fileset_catalog/tmp/test_fileset"))
```
