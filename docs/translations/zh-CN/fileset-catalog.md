---
slug: /fileset-catalog
date: 2024-4-2
keyword: fileset catalog
license: This software is licensed under the Apache License version 2.
title: Fileset 目录
---
## 简介

Fileset catalog通过Hadoop兼容文件系统（Hadoop Compatible File
System，HCFS）管理fileset的存储位置。开箱即支持本地文件系统和HDFS，当匹配的bundle
jar位于classpath中时，还支持Amazon S3、Google Cloud
Storage、Azure Data Lake Storage、Alibaba Cloud OSS和Tencent Cloud COS。

本页面是共享参考：各种后端接受的属性、属性如何从Catalog继承到
Schema再到Fileset，以及如何接入自定义文件系统。示例中使用HDFS和本地
文件系统。有关云后端可运行的端到端示例，请参考
[带有云存储的Fileset Catalog](#实现自定义-hcfs-文件系统-fileset)下列出的相应后端页面。

注意，Gravitino使用Hadoop 3依赖构建Fileset catalog。理论上，它应
同时兼容Hadoop 2.x和3.x，因为Gravitino未使用
Hadoop 3的任何新特性。如果出现任何兼容性问题，请提交一个[issue](https://github.com/apache/gravitino/issues)。

## Catalog

### Catalog 属性

除了[通用Catalog属性](./gravitino-server-config.md#catalog-properties)，
Fileset catalog还具有以下属性：

| 属性名称                        | 描述                                                                                                                                                                                                                                                                                                                      | 默认值          | 是否必填 |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|----------|
| `location`                           | 由Fileset catalog管理的存储位置。其位置名称为`unknown`。该值应始终为目录（HDFS）或路径前缀（如S3、GCS等云存储），不支持单个文件。                                                                                                                       | (none)          | 否       |
| `location-`                          | 属性前缀。用户可以使用`location-{name}={path}`为Catalog设置多个不同名称的位置。                                                                                                                                                                                                       | (none)          | 否       |
| `default-filesystem-provider`        | （已废弃）如果用户未在URI中指定scheme，此Fileset catalog的默认文件系统提供者。候选值为'builtin-local'、'builtin-hdfs'、's3'、'gcs'、'abs'和'oss'。默认值为`builtin-local`。对于S3，如果将此值设置为's3'，则可以省略位置中的's3a://'前缀。 | `builtin-local` | 否       |
| `filesystem-providers`               | （已废弃）要添加的文件系统提供者。用户需要设置此配置以支持云存储或自定义HCFS。例如，将其设置为`s3`或包含`s3`的逗号分隔字符串（如`gs,s3`），以支持包含`s3`在内的多种Fileset。                                                       | (none)          | 否       |
| `credential-providers`               | 凭证提供者类型，以逗号分隔。                                                                                                                                                                                                                                                                               | (none)          | 否       |
| `filesystem-conn-timeout-secs`       | 使用Hadoop FileSystem客户端实例获取文件系统的超时时间。时间单位：秒。                                                                                                                                                                                                                              | 6               | 否       |
| `disable-filesystem-ops`             | 禁用服务端文件系统操作的配置。如果设置为true，当创建、删除Schema或Fileset时，服务端的Fileset catalog将不会创建或删除文件或文件夹。                                                                                                               | false           | 否       |
| `fileset-cache-eviction-interval-ms` | 驱逐Fileset缓存的间隔（毫秒），-1表示从不驱逐。                                                                                                                                                                                                                                                   | 3600000         | 否       |
| `fileset-cache-max-size`             | 缓存可能包含的最大Fileset数量，-1表示无限制。                                                                                                                                                                                                                                                     | 200000          | 否       |
| `config.resources`                   | 配置资源，以逗号分隔。例如，`hdfs-site.xml,core-site.xml`。                                                                                                                                                                                                                                     | (none)          | 否       |
| `fs.path.config.<name>`              | 定义一个逻辑位置条目。将`fs.path.config.<name>`设置为真实的基础URI（例如，`hdfs://cluster1/`）。任何以相同前缀开头的键（如`fs.path.config.<name>.config.resource`）都被视为位置范围的属性，并将转发给底层文件系统客户端。             | (none)          | 否       |

:::note
`default-filesystem-provider`和`filesystem-providers`已废弃。Fileset catalog会自动加载classpath上的文件系统提供者，包括内置文件系统提供者和存在相应bundle jar时的云提供者（例如，`gravitino-aws-bundle`、`gravitino-azure-bundle`、`gravitino-aliyun-bundle`、`gravitino-gcp-bundle`或`gravitino-tencent-bundle`）。
:::

有关凭证分发（Credential vending）的更多详情，请参阅[Credential vending](./security/credential-vending.md)。

默认的load catalog响应中会隐藏敏感的Catalog属性（如云访问
密钥）。通过
`getSecrets` / `GET .../objects/{type}/{fullName}/secrets`检索由secret manager支持的属性（包括存储为secret URN的密钥）。[凭证分发API](security/credential-vending.md) 仍可用于
类型化凭证
分发。

### HDFS Fileset

除了上述属性外，要访问如HDFS Fileset等Fileset，还需要配置以下额外
属性。

| 属性名称                                      | 描述                                                                                | 默认值 | 是否必填                                                    |
|----------------------------------------------------|--------------------------------------------------------------------------------------------|---------------|-------------------------------------------------------------|
| `authentication.impersonation-enable`              | 是否为Fileset catalog启用模拟（impersonation）。                                   | `false`       | 否                                                          |
| `authentication.type`                              | Fileset catalog的认证类型，仅支持`kerberos`、`simple`。      | `simple`      | 否                                                          |
| `authentication.kerberos.principal`                | Kerberos认证的principal                                               | (none)        | 如果`authentication.type`的值为Kerberos则必填。 |
| `authentication.kerberos.keytab-uri`               | Kerberos认证的keytab URI。                                     | (none)        | 如果`authentication.type`的值为Kerberos则必填。 |
| `authentication.kerberos.check-interval-sec`       | Fileset catalog的Kerberos凭证检查间隔。                             | 60            | 否                                                          |
| `authentication.kerberos.keytab-fetch-timeout-sec` | 从 `authentication.kerberos.keytab-uri` 获取 Kerberos keytab 的超时时间。 | 60            | 否                                                          |

`config.resources` 属性允许用户指定自定义配置文件。

Gravitino Fileset 在 `xxx-site.xml` 中扩展了以下属性：

| 属性名称                                     | 描述                                                             | 默认值 | 是否必填                                                    |
|---------------------------------------------------|-------------------------------------------------------------------------|---------------|-------------------------------------------------------------|
| hadoop.security.authentication.kerberos.principal | HDFS 客户端 Kerberos 认证的 principal。           | (none)        | 如果 `authentication.type` 的值为 Kerberos 则必填。 |
| hadoop.security.authentication.kerberos.keytab    | HDFS 客户端 Kerberos 认证的 keytab 文件路径。    | (none)        | 如果 `authentication.type` 的值为 Kerberos 则必填。 |
| hadoop.security.authentication.kerberos.krb5.conf | HDFS 客户端 Kerberos 认证的 krb5.conf 文件路径。 | (none)        | 否                                                          |

### 带云存储的 Fileset Catalog

对于基于 Java 和 Hadoop 的访问，Fileset 使用 Hadoop 兼容文件系统 (Hadoop Compatible File System, HCFS) 接口。
每个云后端提供各自的 Hadoop `FileSystem` 实现，例如用于 Amazon S3 的 S3A。
将匹配的 bundle jar 放置在 classpath 上，并为该后端设置凭证属性。
Python 客户端使用基于 fsspec 的实现，不需要这些 jar。每个后端有各自
的页面，其中包含可运行的端到端示例。

| 存储后端                                           | Bundle jar                 | 位置 scheme | 后端属性                                                         |
|-----------------------------------------------------------|----------------------------|-----------------|----------------------------------------------------------------------------|
| [Amazon S3](./fileset-catalog-with-s3.md)                 | `gravitino-aws-bundle`     | `s3a://`        | `s3-endpoint`, `s3-access-key-id`, `s3-secret-access-key`                  |
| [Google Cloud Storage](./fileset-catalog-with-gcs.md)     | `gravitino-gcp-bundle`     | `gs://`         | `gcs-service-account-file`                                                 |
| [Azure Data Lake Storage](./fileset-catalog-with-adls.md) | `gravitino-azure-bundle`   | `abfss://`      | `azure-storage-account-name`, `azure-storage-account-key`                  |
| [阿里云 OSS](./fileset-catalog-with-oss.md)        | `gravitino-aliyun-bundle`  | `oss://`        | `oss-endpoint`, `oss-access-key-id`, `oss-secret-access-key`               |
| [腾讯云 COS](./fileset-catalog-with-cos.md)        | `gravitino-tencent-bundle` | `cosn://`       | `cos-region`, `cos-access-key-id`, `cos-secret-access-key`, `cos-endpoint` |

一个 catalog 可以同时包含多个后端中的位置，前提是涉及的每个 bundle jar
都在 classpath 上。云后端也接受 `config.resources` 来向底层文件系统客户端传递自定义
配置文件。

### 实现自定义 HCFS 文件系统 Fileset

开发者和用户可以通过在以下 jar 中实现 `FileSystemProvider` 接口来自定义 HCFS 文件系统 fileset：
[gravitino-hadoop-common](https://repo1.maven.org/maven2/org/apache/gravitino/gravitino-hadoop-common/)。
`FileSystemProvider` 接口定义如下：

```java
  
  // 根据创建 catalog 时设置的属性创建 FileSystem 实例。
  FileSystem getFileSystem(@Nonnull Path path, @Nonnull Map<String, String> config)
      throws IOException;
  
  // 文件系统提供程序的 schema 名称。'file' 代表本地文件系统，
  // 'hdfs' 代表 HDFS，'s3a' 代表 AWS S3，'gs' 代表 GCS，'oss' 代表阿里云 OSS，'cosn' 代表腾讯云 COS。
  String scheme();

  // 文件系统提供程序的名称。'builtin-local' 代表本地文件系统，'builtin-hdfs' 代表 HDFS，
  // 's3' 代表 AWS S3，'gcs' 代表 GCS，'oss' 代表阿里云 OSS，'cos' 代表腾讯云 COS。
  String name();
```

同时，`FileSystemProvider` 使用 Java SPI 来加载自定义文件系统 provider。用户
需要在
jar 文件的 `META-INF/services` 目录下创建一个名为 `org.apache.gravitino.catalog.hadoop.fs.FileSystemProvider` 的文件。文件内容是
自定义文件系统 provider 的全限定类名。例如，`S3FileSystemProvider` 的内容如下：
![img.png](../../assets/fileset/custom-filesystem-provider.png)

实现 `FileSystemProvider` 接口后，需要将 jar 文件放入
`$GRAVITINO_HOME/catalogs/fileset/libs` 目录。然后即可使用自定义文件系统 provider。

### Fileset Catalog 认证

Fileset catalog 支持多级认证以控制访问，允许为
catalog、schema 和 fileset 设置不同的认证。认证设置的优先级如下：catalog < schema < fileset。
具体如下：

- **Catalog**：默认认证方式为 `simple`。
- **Schema**：如果未显式设置，则继承 catalog 的认证设置。有关
  schema 设置的更多信息，请参阅 [Schema 属性](#schema-操作)。
- **Fileset**：如果未显式设置，则继承 schema 的认证设置。有关
  fileset 设置的更多信息，请参阅 [Fileset 属性](#fileset-操作)。

`authentication.impersonation-enable` 的默认值为 false，对于 catalog，此
配置的默认值为 false，对于
schema 和 fileset，默认值继承自父级。用户设置的值将覆盖父级
值，优先级机制与认证相同。

### Catalog 操作

详情请参阅 [Catalog 操作](./manage-catalogs-and-schemas.md#catalog-operations)。

## Schema

### Schema 能力

Fileset catalog 支持创建、更新、删除和列出 schema。

### Schema 属性

所有 catalog 属性均由 schema 继承。此外，Fileset catalog schema 还具有以下
属性：

| 属性名                         | 描述                                                                                                               | 默认值             | 是否必填 |
|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------|----------|
| `location`                            | schema 管理的存储位置。其位置名称为 `unknown`。它也应该是一个目录或路径前缀。   | (none)                    | 否       |
| `location-`                           | 属性前缀。用户可以使用 `location-{name}={path}` 为 schema 设置多个具有不同名称的位置。 | (none)                    | 否       |
| `authentication.impersonation-enable` | 是否为此 Fileset catalog schema 启用模拟。                                                   | 父级值 (catalog) | 否       |
| `authentication.type`                 | 此 Fileset catalog schema 的认证类型，仅支持 `kerberos` 和 `simple`。                     | 父级值 (catalog) | 否       |
| `authentication.kerberos.principal`   | 此 schema 的 Kerberos 认证 principal。                                                             | 父级值 (catalog) | 否       |
| `authentication.kerberos.keytab-uri`  | 该 schema Kerberos 认证 keytab 的 URI。                                                    | 父级(catalog)值 | 否       |
| `credential-providers`                | 凭证提供器类型，以逗号分隔。                                                                                              | (none)                    | 否       |
| `config.resources`                    | 配置资源，以逗号分隔。例如，`hdfs-site.xml,core-site.xml`。                                | (none)                    | 否       |

### Schema 操作

详情请参阅 [Schema 操作](./manage-catalogs-and-schemas.md#schema-operations)。

:::note
在创建或删除 Schema 时，Gravitino 会自动创建或删除对应的文件系统目录
用于 Schema 路径。
在以下任一情况下，将跳过此行为：

1. 当 catalog 属性 `disable-filesystem-ops` 设置为 `true` 时
2. 当路径包含[占位符](./filesets.md#storage-locations)时
:::

## Fileset

### Fileset 能力

- Fileset catalog 支持创建、更新、删除和列出 fileset。

### Fileset 属性

所有 Schema 属性都会被 fileset 继承，包括从 catalog 继承的属性。
此外，Fileset catalog 的 fileset 还具有以下属性：

| 属性名称                               | 描述                                                                                                                    | 默认值                                                                                                         | 是否必填                                   | 是否不可变 |
|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|--------------------------------------------|-----------|
| `location`                            | 由 Schema 管理的存储路径。其路径名称为 `unknown`。该值应为目录或路径前缀。 | (none)                                                                                                         | 否                                         | 是       |
| `authentication.impersonation-enable` | 是否为 Fileset catalog 的 fileset 启用身份模拟。                                                                        | 父级（Schema）的值                                                                                              | 否                                         | 是       |
| `authentication.type`                 | Fileset catalog fileset 的认证类型，仅支持 `kerberos` 和 `simple`。                           | 父级（Schema）的值                                                                                              | 否                                         | 否        |
| `authentication.kerberos.principal`   | fileset 的 Kerberos 认证 principal。                                                           | 父级（Schema）的值                                                                                              | 否                                         | 否        |
| `authentication.kerberos.keytab-uri`  | fileset 的 Kerberos 认证 keytab 的 URI。                                                  | 父级（Schema）的值                                                                                              | 否                                         | 否        |
| `credential-providers`                | 凭证提供器类型，以逗号分隔。                                                                      | (none)                                                                                                         | 否                                         | 否        |
| `placeholder-`                        | 以 `placeholder-` 开头的属性用于替换路径中的占位符。                             | (none)                                                                                                         | 否                                         | 是       |
| `default-location-name`               | fileset 的默认路径名称，主要用于未指定路径名称时的 GVFS 操作。    | 当 fileset 只有一个路径时，其路径名称将被自动选为默认值。 | 是，当 fileset 有多个路径时 | 是       |
| `config.resources`                    | 配置资源，以逗号分隔。例如，`hdfs-site.xml,core-site.xml`。                            | (none)                                                                                                         | 否                                         | 否        |

部分属性为保留属性，用户不可设置：

| 属性名称             | 描述                           | 默认值               |
|-----------------------|---------------------------------------|-----------------------------|
| `placeholder-catalog` | catalog 名称的占位符。 | fileset 的 catalog 名称 |
| `placeholder-schema`  | schema 名称的占位符。  | fileset 的 schema 名称  |
| `placeholder-fileset` | fileset 名称的占位符。 | fileset 名称                |

凭证提供器可在以下多处位置指定。Gravitino 按以下优先级顺序检查 `credential-providers`
设置：

1. Fileset 属性
2. Schema 属性
3. Catalog 属性

### Fileset 操作

详情请参阅 [Fileset 操作](./manage-fileset-metadata-using-gravitino.md#fileset-operations)。

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免责声明**：
本文件由 AI 翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 翻译完成。尽管我们力求准确，但请注意，自动翻译可能包含错误或不准确之处。原始语言版文件应视为权威来源。对于重要信息，建议使用专业人工翻译。我们对因使用本翻译而产生的任何误解或误释不承担责任。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->