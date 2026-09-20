---
title: "Trino Connector: Hive Catalog"
slug: "/trino-connector/catalog-hive"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Hive catalog 允许 Trino 查询存储在 Apache Hive 数据仓库中的数据。

## 要求

Hive 连接器需要 Hive metastore 服务 (HMS)，或兼容的 Hive metastore 实现，例如
AWS Glue。

支持 Apache Hadoop HDFS 2.x。

许多分布式存储系统，包括 HDFS、Amazon S3 或 S3 兼容系统，
Google Cloud Storage、Azure Storage 和 IBM Cloud Object Storage 都可以通过 Hive 连接器进行查询。

协调器和所有工作节点必须能够通过网络访问 Hive metastore 和存储系统。

通过 Thrift 协议访问 Hive metastore 默认使用 9083 端口。

数据文件必须是受支持的文件格式。某些文件格式可以使用文件格式配置进行配置
属性
每个目录：

- ORC
- PARQUET
- AVRO
- RCFILE
- SEQUENCEFILE
- JSON
- CSV
- TEXTFILE


## 模式操作

### 创建 Schema

用户可以通过 Apache Gravitino Trino 连接器创建带有属性的 schema，如下所示：

```SQL
CREATE SCHEMA catalog.schema_name 
```

## 表操作

### 创建表

Gravitino Trino 连接器支持基本的 Hive 建表语句，例如定义字段，
允许空值，以及添加注释。Gravitino Trino 连接器支持 `CREATE TABLE AS SELECT`。

:::note
不支持 `CREATE OR REPLACE TABLE AS SELECT`。作为替代方案，请使用 `DROP TABLE` 然后再使用 `CREATE TABLE AS SELECT`。
:::

以下示例展示了如何在 Hive catalog 中创建表：

```shell
CREATE TABLE catalog.schema_name.table_name
(
  name varchar,
  salary int
)
```


### 修改表

支持以下 alter table 操作：

- 重命名表
- 添加列
- 删除列
- 重命名列
- 更改列类型
- 设置表属性

### 选择

Gravitino Trino 连接器支持大多数 SELECT 语句，允许成功执行查询。
它不支持某些查询优化，例如下推和裁剪功能。

### 更新

`UPDATE` 仅支持格式为 ORC 的事务性 Hive 表。不支持对分区列或分桶列进行 `UPDATE`。

### 删除

应用于非事务表的 `DELETE` 仅在表已分区且 `WHERE` 子句匹配整个分区时才受支持。
采用 ORC 格式的事务性 Hive 表支持“逐行”删除，其中 `WHERE` 子句可以匹配任意行集合。

### 合并

`MERGE` 仅支持 ACID 表。

另请参阅 [更多限制](https://trino.io/docs/current/connector/hive.html#data-management)。

## 模式和表属性

在 Hive 目录中，使用 "WITH" 关键字在 "CREATE"
语句中为表和模式设置附加属性。


### 创建带有属性的 Schema

用户可以使用以下示例来创建带有属性的 schema：

```sql
CREATE SCHEMA catalog.dbname
WITH (
  location = 'hdfs://hdfs-host:9000/user/hive/warehouse/dbname'
);
```

以下表格是 Hive schema 支持的属性：

| 属性 | 描述                     | 默认值 | 必填 | 保留 |
|----------|---------------------------------|---------------|----------|----------|
| location | 用于表存储的 HDFS 位置 | (无)        | 否       | 否       |

保留属性：保留属性是用户无法设置但可以读取的属性。


### 创建具有属性的表

用户可以使用以下示例来创建带有属性的表：

```sql
CREATE TABLE catalog.dbname.tablename
(
  name varchar,
  salary int
) WITH (
  format = 'TEXTFILE',
  KEY = 'VALUE',
  ...      
);
```

以下表格为 Hive 表支持的属性：

| 属性       | 描述                           | 默认值                                              | 必填 | 保留 |
|----------------|---------------------------------------|------------------------------------------------------------|----------|----------|
| format         | 表的 Hive 存储格式     | TEXTFILE                                                   | 否       | 否       |
| location       | 表存储的 HDFS 路径       | (none)                                                     | 否       | 否       |
| input_format   | 表的输入格式类  | org.apache.hadoop.mapred.TextInputFormat                   | 否       | 否       |
| output_format  | 表的输出格式类 | org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat | 否       | 否       |
| serde_lib      | 表的 serde 库类 | org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe         | 否       | 否       |
| serde_name     | serde 的名称                     | 默认为表名                                      | 否       | 否       |
| partitioned_by | 表的分区列       | (none)                                                     | 否       | 否       |
| bucketed_by    | 表的分桶列          | (none)                                                     | 否       | 否       |
| bucket_count   | 表的分桶数量       | (none)                                                     | 否       | 否       |
| sorted_by      | 表的排序列          | (none)                                                     | 否       | 否       |

以下属性会被自动添加并作为保留属性进行管理。不允许用户设置这些属性。

| 属性   | 描述                             |
|------------|-----------------------------------------|
| total_size | 表的总大小                 |
| num_files  | 文件数量                         |
| external   | 指示是否为外部表 |
| table_type | Hive表的类型                  |

## 示例

在通过 Gravitino 在 Trino 中使用 Hive catalog 之前，请完成以下步骤：

- 在 Gravitino 中创建一个 metalake 和 catalog。假设 metalake 名称为 `test`，catalog 名称为 `hive_test`，
那么你可以使用以下代码在 Gravitino 中创建它们：

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "test",
  "comment": "comment",
  "properties": {}
}' http://gravitino-host:8090/api/metalakes

curl -X POST \
-H "Content-Type: application/json" \
-d '{
  "name": "hive_test",
  "type": "RELATIONAL",
  "comment": "comment",
  "provider": "hive",
  "properties": {
    "metastore.uris": "thrift://hive-host:9083"
  }
}' http://gravitino-host:8090/api/metalakes/test/catalogs
```

有关 Hive catalog 的更多信息，请参阅 [Hive catalog](../apache-hive-catalog.md)。

- 将配置 `gravitino.metalake` 的值设置为您创建的名为 'test' 的 metalake，并启动 Trino 容器。

使用 Trino CLI 连接到 Trino 容器并运行查询。

列出所有 Gravitino 管理的目录：

```sql 
SHOW CATALOGS;
```

结果类似于：

```text
    Catalog
----------------
 gravitino
 jmx
 system
 hive_test
(4 rows)

Query 20231017_082503_00018_6nt3n, FINISHED, 1 node
```

`gravitino` 目录是一个由 Trino 目录配置定义的目录。
`hive_test` 目录是您在 Gravitino 中创建的目录。
其他目录是常规的用户配置的 Trino 目录。

### 创建表和模式

在 `hive_test` 目录中创建一个名为 `database_01` 的新模式。

```sql
CREATE SCHEMA hive_test.database_01;
```

使用 HDFS 位置创建一个新的 schema：

```sql
CREATE SCHEMA hive_test.database_01 WITH (
  location = 'hdfs://hdfs-host:9000/user/hive/warehouse/database_01'
);
```

在 schema `hive_test.database_01` 中创建一个名为 `table_01` 的新表，并以 TEXTFILE 格式存储，按 `salary` 分区，按 `name` 分桶并按 `salary` 排序。

```sql
CREATE TABLE  hive_test.database_01.table_01
(
name varchar,
salary int,
month int    
)
WITH (
  format = 'TEXTFILE',
  partitioned_by = ARRAY['month'],
  bucketed_by = ARRAY['name'],
  bucket_count = 2,
  sorted_by = ARRAY['salary']  
);
```

### 写入数据

向表 `table_01` 中插入数据：

```sql
INSERT INTO hive_test.database_01.table_01 (name, salary, month) VALUES ('ice', 12, 22);
```

从 select 将数据插入到表 `table_01` 中：

```sql
INSERT INTO hive_test.database_01.table_01 (name, salary, month) SELECT * FROM hive_test.database_01.table_01;
```

删除表 `table_01` 中整个分区的数据：

```sql
DELETE FROM hive_test.database_01.table_01 WHERE month=22;
```

如果在模式 `hive_test.database_01` 中定义了一个 ACID 表，如下：

```sql
CREATE TABLE database_01.test_acid
(
    id INT,
    name STRING,
    salary INT
)
CLUSTERED BY (id) INTO 4 BUCKETS
STORED AS ORC
TBLPROPERTIES ('transactional'='true');
```

将数据更新到表 `test_acid` 中：

```sql
UPDATE hive_test.database_01.test_acid SET name='bob' WHERE id=1;
```

从表 `test_acid` 中删除数据：

```sql
DELETE FROM hive_test.database_01.test_acid WHERE id=1;
```

将数据合并到表 `test_acid` 中：

```sql
MERGE INTO hive_test.database_01.test_acid t USING hive_test.database_01.table_01 s
    ON (t.name = s.name)
    WHEN MATCHED AND s.name = 'bob'
        THEN DELETE
    WHEN MATCHED
        THEN UPDATE
            SET salary = s.salary + t.salary
    WHEN NOT MATCHED
        THEN INSERT (id, name, salary)
              VALUES (3, s.name, s.salary);
```

### 查询数据

查询 `table_01` 表：

```sql
SELECT * FROM hive_test.database_01.table_01;
```

### 修改表

向 `table_01` 表添加一个新列 `age`：

```sql
ALTER TABLE hive_test.database_01.table_01 ADD COLUMN age int;
```

从 `table_01` 表中删除 `age` 列：

```sql
ALTER TABLE hive_test.database_01.table_01 DROP COLUMN age;
```

将 `table_01` 表重命名为 `table_02`：

```sql
ALTER TABLE hive_test.database_01.table_01 RENAME TO hive_test.database_01.table_02;
```

### DROP

删除模式：

```sql
DROP SCHEMA hive_test.database_01;
```

删除表：

```sql
DROP TABLE hive_test.database_01.table_01;
```

## HDFS 配置与权限

对于基本设置，Apache Gravitino Trino 连接器配置 HDFS 客户端
使用 catalog 配置。它支持使用 `hdfs-site.xml` 配置 HDFS 客户端
和 `core-site.xml` 文件，通过 catalog 配置中的 `trino.bypass.hive.config.resources` 设置。

在 Trino 中为 Hive 表运行任何 `Insert` 语句之前，
你必须检查 Trino 用于访问 HDFS 的用户是否有权访问 Hive 仓库目录。
通过在 Trino JVM 配置中设置 HADOOP_USER_NAME 系统属性来覆盖此用户名，
将 hdfs_user 替换为适当的用户名：

```text
-DHADOOP_USER_NAME=hdfs_user
```

## S3

当在 Hive catalog 中使用 AWS S3 时，用户需要配置 Trino Hive 连接器的
AWS S3 相关属性，配置在 catalog 的属性中。请参考
[Hive connector with Amazon S3](https://trino.io/docs/current/connector/hive-s3.html) 的文档。

要在 Trino CLI 中创建带有 AWS S3 配置的 Hive catalog，请使用以下命令：

```sql
call gravitino.system.create_catalog(
  'gt_hive',
  'hive',
  map(
    array['metastore.uris',
        'trino.bypass.hive.s3.aws-access-key', 'trino.bypass.hive.s3.aws-secret-key', 'trino.bypass.hive.s3.region'
    ],
    array['thrift://hive:9083', '<aws-access-key>', '<aws-secret-key>', '<region>']
  )
);
```

- `trino.bypass.hive.s3.aws-access-key`、`trino.bypass.hive.s3.aws-secret-key` 和 `trino.bypass.hive.s3.region` 的设置
是 Apache Gravitino Trino 连接器所必需的。

成功创建 Hive catalog 后，用户可以按如下方式创建 schema 和表：

```sql
CREATE SCHEMA gt_hive.gt_db02
WITH (location = 's3a://trino-test/dw/gt_db02');

CREATE TABLE gt_hive.gt_db02.tb01 (
    name varchar,
    salary int
);
```

`location` 指定 AWS S3 存储路径。

运行该命令后，这些表即可用于在 AWS S3 上进行数据读写操作。

:::note
确保 Hive catalog 使用的 Hive Metastore 服务支持 AWS S3。
:::
