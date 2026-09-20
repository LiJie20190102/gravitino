---
title: "Hive Catalog with Cloud Storage"
slug: "/hive-catalog"
date: 2024-9-24
keyword: "Hive catalog cloud storage S3 ADLS GCS"
license: "This software is licensed under the Apache License version 2."
---


## 简介

自 Hive 2.x 起，Hive 已支持将 S3 作为存储后端，使用户能够直接通过 Hive 在 Amazon S3 中存储和管理数据。Gravitino 通过支持带有 S3 的 Hive catalog 增强了这一能力，允许用户高效管理位于 S3 中的文件的存储位置。这种集成简化了数据操作，并支持从 Hive 查询中无缝访问 S3 数据。

对于 ADLS（即 Azure Blob Storage (ABS) 或 Azure Data Lake Storage (v2)）和 GCS (Google Cloud Storage)，其集成方式与 S3 类似。唯一的区别是 ADLS 和 GCS 的配置属性（见下文）。

以下部分将引导您完成配置 Hive catalog 以将 S3、ADLS 和 GCS 用作存储后端的必要步骤，包括配置详情以及创建数据库和表的示例。

## Hive Metastore 配置

以下内容将主要介绍如何配置 Hive metastore 以使用 S3 作为存储后端。只需对配置属性稍作修改，即可将相同的配置应用于 ADLS 和 GCS。

### 示例配置更改

以下是需要在 `hive-site.xml` 文件中添加或修改以支持 S3 的关键属性：

```xml

<property>
  <name>fs.s3a.access.key</name>
  <value>S3_ACCESS_KEY_ID</value>
</property>

<property>
  <name>fs.s3a.secret.key</name>
  <value>S3_SECRET_KEY_ID</value>
</property>

<property>
  <name>fs.s3a.endpoint</name>
  <value>S3_ENDPOINT_ID</value>
</property>

<!-- The following property is optional and can be replaced with the location property in the schema
definition and table definition, as shown in the examples below. After explicitly setting this
property, you can omit the location property in the schema and table definitions.

It's also applicable for Azure Blob Storage(ADLS) and GCS.
-->
<property>
  <name>hive.metastore.warehouse.dir</name>
  <value>S3_BUCKET_PATH</value>
</property>

<!-- The following two configurations are for Azure Blob Storage(ADLS) -->
<property>
  <name>fs.abfss.impl</name>
  <value>org.apache.hadoop.fs.azurebfs.SecureAzureBlobFileSystem</value>
</property>

<property>
  <name>fs.azure.account.key.ABS_ACCOUNT_NAME.dfs.core.windows.net</name>
  <value>ABS_ACCOUNT_KEY</value>
</property>

<!-- The following two configurations are only for Google Cloud Storage(gcs) -->
<property>
  <name>fs.gs.auth.service.account.enable</name>
  <value>true</value>
</property>

<!-- SERVICE_ACCOUNT_FILE should be a local file or remote file that can be access by hive server -->
<property>
  <name>fs.gs.auth.service.account.json.keyfile</name>
  <value>SERVICE_ACCOUNT_FILE</value>
</property>

```

### 添加所需的 JARs

更新 `hive-site.xml` 后，您需要确保 Hive classpath 中包含必要的与 S3 相关的 JAR 包。您可以通过执行以下命令来完成此操作：
```shell
cp ${HADOOP_HOME}/share/hadoop/tools/lib/*aws* ${HIVE_HOME}/lib

# For Azure Blob Storage(ADLS)
cp ${HADOOP_HOME}/share/hadoop/tools/lib/*azure* ${HIVE_HOME}/lib

# For Google Cloud Storage(GCS)
cp gcs-connector-hadoop3-2.2.22-shaded.jar ${HIVE_HOME}/lib
```

[`gcs-connector-hadoop3-2.2.22-shaded.jar`](https://github.com/GoogleCloudDataproc/hadoop-connectors/releases/download/v2.2.22/gcs-connector-hadoop2-2.2.22-shaded.jar) 是包含 Hadoop GCS connector 的捆绑 jar 包，你需要根据所使用的 Hadoop 版本选择相应的 gcs connector jar。

或者，你也可以从 Maven 仓库下载所需的 JARs，并将它们放入 Hive classpath 中。验证这些 JARs 与你正在使用的 Hadoop 版本是否兼容至关重要，以避免任何兼容性问题。

### 重启 Hive Metastore

正确设置所有配置后，重启 Hive 集群以应用更改。此步骤对于确保新配置生效以及 Hive 服务能够与 S3 通信至关重要。


## 使用 Gravitino 创建带 S3 存储的表或数据库

假设您已经使用 Gravitino 设置了 Hive catalog，您可以继续使用 S3 存储创建表或数据库。有关 catalog 操作的更多信息，请参阅 [Catalog operations](./manage-catalogs-and-schemas.md#catalog-operations)

### 示例：使用 S3 存储创建数据库

以下是使用 Gravitino 在 S3 中创建数据库的示例：

<Tabs groupId="language" queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "hive_schema",
  "comment": "comment",
  "properties": {
    "location": "s3a://bucket-name/path"
     
     # The following line is for Azure Blob Storage(ADLS)
     # "location": "abfss://container-name@user-account-name.dfs.core.windows.net/path"
     
     # The following line is for Google Cloud Storage(GCS)
     # "location": "gs://bucket-name/path"
  }
}' http://localhost:8090/api/metalakes/metalake/catalogs/catalog/schemas
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoClient gravitinoClient = GravitinoClient
    .builder("http://localhost:8090")
    .withMetalake("metalake")
    .build();

// Assuming you have just created a Hive catalog named `catalog`
Catalog catalog = gravitinoClient.loadCatalog("catalog");

SupportsSchemas supportsSchemas = catalog.asSchemas();

Map<String, String> schemaProperties = ImmutableMap.<String, String>builder()
    .put("location", "s3a://bucket-name/path")
    
    // The following line is for Azure Blob Storage(ADLS)
    // .put("location", "abfss://container-name@user-account-name.dfs.core.windows.net/path")
    
    // The following lines for Google Cloud Storage(GCS)
    // .put("location", "gs://bucket-name/path")
    
    .build();
Schema schema = supportsSchemas.createSchema("hive_schema",
    "This is a schema",
    schemaProperties
);
// ...
```

</TabItem>
</Tabs>

创建数据库后，您可以继续在此 schema 下使用 S3 存储创建表。有关表操作的更多详细信息，请参阅 [表操作](./manage-relational-metadata-using-gravitino.md#table-operations)。

## 通过 Hive CLI 访问使用 S3 存储的表

假设您已经在 [使用 Gravitino 创建具有 S3 存储的表或数据库](#create-tables-or-databases-with-s3-storage-using-gravitino) 章节中创建了一个表，假设该表名为 `hive_table`。您可以使用 Hive CLI 访问数据库/表并查看其详细信息，如下所示：


```shell
hive> show create database hive_schema;
OK
CREATE DATABASE `hive_schema`
COMMENT
  'comment'
LOCATION
  's3a://my-test-bucket/test-1727168792125'
WITH DBPROPERTIES (
  'gravitino.identifier'='gravitino.v1.uid2173913050348296645',
  'key1'='val1',
  'key2'='val2')
Time taken: 0.019 seconds, Fetched: 9 row(s)
hive> use hive_schema;
OK
Time taken: 0.019 seconds
hive> show create table cataloghiveit_table_fc7c7d16;
OK
CREATE TABLE `hive_table`(
  `hive_col_name1` tinyint COMMENT 'col_1_comment',
  `hive_col_name2` date COMMENT 'col_2_comment',
  `hive_col_name3` string COMMENT 'col_3_comment')
COMMENT 'table_comment'
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3a://my-test-bucket/test-1727168821335/hive_table'
TBLPROPERTIES (
  'EXTERNAL'='FALSE',
  'gravitino.identifier'='gravitino.v1.uid292928775813252841',
  'key1'='val1',
  'key2'='val2',
  'transient_lastDdlTime'='1727168821')
Time taken: 0.071 seconds, Fetched: 19 row(s)
> insert into hive_table values(1, '2022-11-12', 'hello');
Query ID = root_20240924091305_58ab83c7-7091-4cc7-a0d9-fa44945f45c6
Total jobs = 3
Launching Job 1 out of 3
Number of reduce tasks is set to 0 since there's no reduce operator
Job running in-process (local Hadoop)
2024-09-24 09:13:08,381 Stage-1 map = 100%,  reduce = 0%
Ended Job = job_local1096072998_0001
Stage-4 is selected by condition resolver.
Stage-3 is filtered out by condition resolver.
Stage-5 is filtered out by condition resolver.
Loading data to table hive_schema.hive_table
MapReduce Jobs Launched:
Stage-Stage-1:  HDFS Read: 0 HDFS Write: 0 SUCCESS
Total MapReduce CPU Time Spent: 0 msec
OK
Time taken: 2.843 seconds
hive> select * from hive_table;
OK
1	2022-11-12	hello
Time taken: 0.116 seconds, Fetched: 1 row(s)
```

此命令显示数据库 hive_schema 的创建详细信息，包括其在 S3 中的位置以及任何相关属性。

## 通过 Spark 访问使用 S3 存储的表

要使用 Spark 访问存储在 S3 中的表，您需要适当地配置 SparkSession。以下是如何使用必要的 S3 配置来设置 SparkSession 的示例：

```java
  SparkSession sparkSession =
        SparkSession.builder()
            .config("spark.plugins", "org.apache.gravitino.spark.connector.plugin.GravitinoSparkPlugin")
            .config("spark.sql.gravitino.uri", "http://localhost:8090")
            .config("spark.sql.gravitino.metalake", "xx")
            .config("spark.sql.catalog.{hive_catalog_name}.fs.s3a.access.key", accessKey)
            .config("spark.sql.catalog.{hive_catalog_name}.fs.s3a.secret.key", secretKey)
            .config("spark.sql.catalog.{hive_catalog_name}.fs.s3a.endpoint", getS3Endpoint)
            .config("spark.sql.catalog.{hive_catalog_name}.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

            // This two is for Azure Blob Storage(ADLS) only
            .config(
                String.format(
                    "spark.sql.catalog.{hive_catalog_name}.fs.azure.account.key.%s.dfs.core.windows.net",
                    ABS_USER_ACCOUNT_NAME),
                ABS_USER_ACCOUNT_KEY)
            .config("spark.sql.catalog.{hive_catalog_name}.fs.abfss.impl", "org.apache.hadoop.fs.azurebfs.SecureAzureBlobFileSystem")
  
            // This two is for Google Cloud Storage(GCS) only
            .config("spark.sql.catalog.{hive_catalog_name}.fs.gs.auth.service.account.enable", "true")
            .config("spark.sql.catalog.{hive_catalog_name}.fs.gs.auth.service.account.json.keyfile", "SERVICE_ACCOUNT_FILE")
            
            .config("spark.sql.catalog.{hive_catalog_name}.fs.s3a.path.style.access", "true")
            .config("spark.sql.catalog.{hive_catalog_name}.fs.s3a.connection.ssl.enabled", "false")
            .config(
                "spark.sql.catalog.{hive_catalog_name}.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
            .config("spark.sql.storeAssignmentPolicy", "LEGACY")
            .config("mapreduce.input.fileinputformat.input.dir.recursive", "true")
            .enableHiveSupport()
            .getOrCreate();

    sparkSession.sql("...");
```

:::note
请下载 [Hadoop AWS jar](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws) 和 [aws java sdk jar](https://mvnrepository.com/artifact/com.amazonaws/aws-java-sdk-bundle)，并将它们放置在 Spark 的 classpath 中。如果缺少这些 JAR 包，Spark 将无法访问 S3 存储。
Azure Blob Storage(ADLS) 需要将 [Hadoop Azure jar](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-azure) 和 [Azure cloud sdk jar](https://mvnrepository.com/artifact/com.azure/azure-storage-blob) 放置在 Spark 的 classpath 中。
对于 Google Cloud Storage(GCS)，您需要下载 [Hadoop GCS jar](https://github.com/GoogleCloudDataproc/hadoop-connectors/releases) 并将其放置在 Spark 的 classpath 中。
:::

按照这些说明，您可以通过 Hive CLI 和 Spark 有效地管理和访问您的 S3、ADLS 或 GCS 数据，并利用 Gravitino 的功能实现最佳的数据管理。
