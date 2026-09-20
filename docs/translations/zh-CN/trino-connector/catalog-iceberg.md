---
title: "Trino Connector: Iceberg Catalog"
slug: "/trino-connector/catalog-iceberg"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Iceberg 是一种用于海量分析数据集的开放表格式。 
Iceberg 目录允许 Trino 查询以 Iceberg 格式写入的文件中存储的数据，
如 Iceberg 表规范中所定义。该目录支持 Apache Iceberg 表规范版本 1 和 2。

## 要求

要使用 Iceberg，您需要：
- Trino 协调器和工作节点到分布式对象存储的网络访问权限。
- 访问 Hive metastore 服务 (HMS)、AWS Glue 目录、JDBC 目录、REST 目录或 Nessie 服务器的权限。
- 以受支持的文件格式存储的数据文件。可以使用每个目录的文件格式配置属性对其进行配置：
- ORC
- Parquet（默认）

## Trino 如何访问目录

Gravitino Trino 连接器通过 Gravitino Iceberg 加载每个 `lakehouse-iceberg` 目录
REST 服务器 (IRC)，无论目录的 `catalog-backend` 如何。`catalog-backend` 描述了
Gravitino 如何存储目录的元数据；它不决定查询引擎如何访问数据。

这就是 [credential vending](../security/credential-vending.md) 能够工作的原因。Trino 仅消费
其 `rest` Iceberg catalog 类型中的 vended credentials —— `jdbc` 和 `hive_metastore` 类型没有
存放 STS 临时凭证的会话令牌的地方 —— 因此，带有
`credential-providers=s3-token` 的 catalog 在这些路径上不会生成任何可用的凭证。通过
IRC 进行路由意味着每次表访问都会通过 Iceberg REST
协议获得新颁发的临时凭证。

The connector already connects to the Gravitino server (it is how catalogs are discovered in the
first place), so it also asks that server whether it has an Iceberg REST server running as an
[auxiliary service](../iceberg-rest-service.md) for the connector's metalake. By default, a
non-REST `lakehouse-iceberg` catalog is not registered until an endpoint is discovered or configured
explicitly. It is retried during every metadata refresh rather than silently falling back and
disabling credential vending. To retain the behavior from older connector versions, set
`gravitino.iceberg.rest-routing-enabled=false`; this skips discovery and translates the catalog's
`catalog-backend` into the corresponding native Trino Iceberg configuration.

只有协调器轮询 Gravitino 服务器，因此当
catalog 注册或刷新时，协调器会解析端点，并将其分发给每个节点（包括协调器和 workers）
作为该 catalog 自身定义的一部分——这与 Trino 复制任何其他 catalog 属性
集群范围内的方式相同。在 IRC 启动之前无法注册的 catalog
会在后续发现轮询成功后自动注册；无需重启 Trino。

Gravitino 服务器从 IRC 的监听器配置中推导出发现的端点，因此
在反向代理后面，它可能会报告一个客户端无法访问的端点。在这种情况下，请将
Gravitino 服务器上的 `gravitino.iceberg-rest.advertised-uri` 设置为公共端点（见
[Iceberg REST 服务](../iceberg-rest-service.md#http-server)）；发现机制随后将报告该 URI
作为替代。

设置 `gravitino.iceberg.rest-uri` 以覆盖发现的端点，并且它是必需的——不仅仅是
覆盖——对于独立的 IRC（它自己的进程，而不是 Gravitino 服务器的辅助服务）：
Gravitino 服务器无法知道独立的 IRC 是否存在，因此发现机制永远找不到它。参见
[限制](#limitations)。

```properties
connector.name=gravitino
gravitino.metalake=test
gravitino.uri=http://gravitino-host:8090

gravitino.iceberg.rest-uri=http://gravitino-host:9001/iceberg
```

连接器从 catalog 本身派生出其他所有内容。Gravitino catalog 名称被传递
作为 `iceberg.rest-catalog.warehouse` 和 `iceberg.rest-catalog.prefix` —— Iceberg 客户端
两次选择该 catalog，首先作为 `GET /v1_config` 调用的查询参数，该调用
发现它，然后作为之后每个请求的路径段。

Trino 原生文件系统派生自 catalog 的 `warehouse` 方案，因为 vended
凭证仅由 Trino 的原生文件系统使用：

| 仓库方案                               | 派生属性                                                                                                                                                 |
|:------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `s3://`, `s3a://`, `s3n://`                    | `fs.native-s3.enabled`，加上 `s3.region`、`s3.endpoint` 和 `s3.path-style-access`，其中 catalog 定义了 `s3-region`、`s3-endpoint` 和 `s3-path-style-access` |
| `gs://`                                        | `fs.native-gcs.enabled`                                                                                                                                            |
| `abfs://`, `abfss://`, `wasb://`, `wasbs://`   | `fs.native-azure.enabled`                                                                                                                                          |
| 其他任何内容 (`hdfs://`, `file://`, `oss://`) | 无 — 仅 `fs.hadoop.enabled`                                                                                                                                    |

最后一行的方案没有 Trino 原生文件系统，因此为其提供凭证的 catalog
无法应用它们；当 connector 检测到该组合时，会记录一条警告。

在 Gravitino 端，IRC 必须与动态配置提供程序一起运行，以便它能够提供 catalog
在 Gravitino 中定义的：

```properties
gravitino.auxService.names = iceberg-rest
gravitino.iceberg-rest.catalog-config-provider = dynamic-config-provider
gravitino.iceberg-rest.gravitino-metalake = test
```

### 向 Iceberg REST 服务器进行身份验证

如果 IRC 启用了身份验证，连接器构建的内部 Iceberg REST catalog
必须自行对其进行身份验证。这是一组与连接器使用的凭据相独立的凭据，
针对主 Gravitino 服务器，并且不会被自动重用。任何带有前缀
`gravitino.iceberg.rest-catalog.` 的属性都会传递给内部 catalog，并将其前缀
重写为 `iceberg.rest-catalog.`：

```properties
gravitino.iceberg.rest-catalog.security=OAUTH2
gravitino.iceberg.rest-catalog.oauth2.credential=client_id:client_secret
gravitino.iceberg.rest-catalog.oauth2.server-uri=http://your-idp/token
gravitino.iceberg.rest-catalog.oauth2.scope=email
```

省略此代码块在已认证的 IRC 上会表现为身份验证错误，而不是
配置缺失错误，这很容易被误判。

有四个键被保留：`iceberg.rest-catalog.uri`、`.warehouse`、`.prefix` 和
`iceberg.catalog.type`。连接器总是会自行派生这些键，因此通过
`gravitino.iceberg.rest-catalog.` 或目录的 `trino.bypass.` 设置它们均无效——连接器会记录
当它忽略某个键时。

当两者都成立时，连接器会自动设置 `iceberg.rest-catalog.session=USER`：

- `gravitino.client.session.forwardUser=true`
- IRC 通过以下任意一种方式使用 OAuth2 进行身份验证：
- `gravitino.client.authType=oauth2`
- `gravitino.iceberg.rest-catalog.security=OAUTH2`
- `trino.bypass.iceberg.rest-catalog.security=OAUTH2`，在具有独立 REST 后端的 catalog 上

然后每个查询将最终用户的身份传递给 IRC，保持按用户分发凭证和
按用户授权不变。否则会故意关闭会话模式：转发的
令牌无法被交换，因此它不会向 IRC 携带任何身份。设置
`gravitino.iceberg.rest-catalog.session` 以显式覆盖任一方式。参见
[Authentication](./authentication.md) 了解完整设置。

### 局限性

- 一个 IRC 仅服务于一个 metalake，在启动时由
`gravitino.iceberg-rest.gravitino-metalake` 固定。Gravitino 服务器仅报告该 IRC 的端点
用于该 metalake。在多 metalake 模式下（`gravitino.use-single-metalake=false`），非 REST
另一个 metalake 中的 Iceberg catalog 因此需要 metalake 范围的手动 URI，或者保持
在启用 REST 路由时未注册。
- 使用 `catalog-backend=rest` 创建的 catalog 继续指向其自身配置的 `uri`，并且
不会被重新路由，因为它已经直接到达 Iceberg REST catalog。
- 不运行 IRC 的部署必须设置
`gravitino.iceberg.rest-routing-enabled=false`，以将非 REST 的 `lakehouse-iceberg` catalog 转换
为 Trino 的 `jdbc` 或 `hive_metastore` catalog 类型，如同以前一样。
- 发现功能仅适用于作为 Gravitino 辅助服务运行的 IRC
（`gravitino.auxService.names=iceberg-rest`），嵌入在与 Gravitino 服务器相同的进程中。
独立的 IRC —— 其自身进程，使用 `GravitinoIcebergRESTServer` 启动并拥有其自己的
`gravitino-iceberg-rest-server.conf` —— 从不向 Gravitino 服务器注册，因此服务器
无法知道它的存在；Gravitino 服务器不会报告任何端点，即使独立的 IRC
正在运行。在这种情况下，请手动设置 `gravitino.iceberg.rest-uri`。

## 模式操作

### 创建 Schema

用户可以通过 Apache Gravitino Trino 连接器创建 schema，如下所示：

```SQL
CREATE SCHEMA catalog.schema_name
```

## 表操作

### 创建表

Apache Gravitino Trino 连接器支持基本的 Iceberg 表创建语句，例如定义字段，
允许空值，以及添加注释。Apache Gravitino Trino 连接器支持 `CREATE TABLE AS SELECT`。

:::note
不支持 `CREATE OR REPLACE TABLE AS SELECT`。Iceberg 连接器会缓存表的 UUID
在查询计划阶段；在同一事务内删除并重新创建表会导致
随后的插入阶段检测到 UUID 不匹配并失败。请使用 `DROP TABLE`，然后使用
`CREATE TABLE AS SELECT` 作为替代方案。
:::

以下示例展示了如何在 Iceberg 目录中创建表：

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

Apache Gravitino Trino 连接器支持大多数 SELECT 语句，能够成功执行查询。
它不支持某些查询优化，例如下推和剪枝功能。

### 更新

`UPDATE` 仅支持使用 Iceberg 规范 v2 或更高版本的表。

### 删除

支持对使用 Iceberg 规范 v2 或更高版本的表删除整个分区和单行。
另请参阅 [删除限制](https://trino.io/docs/current/connector/iceberg.html#data-management)。

### 合并

`MERGE` 仅支持使用 Iceberg 规范 v2 或更高版本的表。

### 表过程

Apache Gravitino Trino 连接器将 Iceberg 表维护过程委托
给底层的 Iceberg 连接器，因此可以通过
在由 Gravitino 管理的 Iceberg 表上使用 `ALTER TABLE ... EXECUTE` 来调用它们。支持以下
过程：

| Procedure            | Description                                                                                          |
|----------------------|------------------------------------------------------------------------------------------------------|
| `expire_snapshots`   | 删除旧快照及其关联的元数据/数据文件以回收存储空间。                    |
| `remove_orphan_files`| 删除表的数据目录中未被任何快照引用的文件。                  |
| `optimize`           | 将小数据文件重写为更少、更大的文件，以提高读取性能（即 `rewrite_data_files`）。 |
| `rewrite_manifests`  | 重写表的清单文件以优化元数据扫描。                                       |

示例用法：

```sql
-- Expire snapshots older than the default retention threshold
ALTER TABLE iceberg_test.database_01.table_01 EXECUTE expire_snapshots;

-- Expire snapshots older than 7 days (requires the minimum retention override
-- to be less than or equal to the requested threshold)
ALTER TABLE iceberg_test.database_01.table_01
  EXECUTE expire_snapshots(retention_threshold => '7d');

-- Remove orphan files
ALTER TABLE iceberg_test.database_01.table_01 EXECUTE remove_orphan_files;

-- Compact small data files
ALTER TABLE iceberg_test.database_01.table_01 EXECUTE optimize;

-- Compact small data files whose size is under a threshold
ALTER TABLE iceberg_test.database_01.table_01
  EXECUTE optimize(file_size_threshold => '128MB');

-- Rewrite manifests for faster metadata scans
ALTER TABLE iceberg_test.database_01.table_01 EXECUTE rewrite_manifests;
```

有关每个过程接受的参数的完整列表，请参见
[Trino Iceberg 连接器文档](https://trino.io/docs/current/connector/iceberg.html#alter-table-execute).

## 表和模式属性

### 创建带有属性的 Schema

Iceberg 模式不支持属性。

### 创建具有属性的表

用户可以使用以下示例来创建带有属性的表：

```sql
CREATE TABLE catalog.dbname.tablename
(
  name varchar,
  salary int
) WITH (
  KEY = 'VALUE',
  ...      
);
```

以下表格是 Iceberg 表支持的属性：

| 属性 | 描述 | 默认值 | 必填 | 保留 |
|--------------|---------------------------------|---------------|----------|----------|
| partitioning | 表的分区列 | (无)        | 否       | 否       |
| sorted_by    | 表的排序列    | (无)        | 否       | 否       |

保留属性：保留属性是用户无法设置但可以读取的属性。

## 示例

在通过 Apache Gravitino 在 Trino 中使用 Iceberg catalog 之前，请完成以下步骤：

- 在 Apache Gravitino 中创建一个 metalake 和 catalog。假设 metalake 名称为 `test`，catalog 名称为 `iceberg_test`，
那么你可以使用以下代码在 Apache Gravitino 中创建它们：

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "test",
  "comment": "comment",
  "properties": {}
}' http://gravitino-host:8090/api/metalakes

curl -X POST -H "Content-Type: application/json" \
-d '{
  "name": "iceberg_test",
  "type": "RELATIONAL",
  "comment": "comment",
  "provider": "lakehouse-iceberg",
  "properties": {
    "uri": "thrift://hive-host:9083",
    "catalog-backend": "hive",
    "warehouse": "hdfs://hdfs-host:9000/user/iceberg/warehouse"
  }
}' http://gravitino-host:8090/api/metalakes/test/catalogs
```

有关 Iceberg catalog 的更多信息，请参阅 [Iceberg catalog](../lakehouse-iceberg-catalog.md)。

- 将配置 `gravitino.metalake` 的值设置为您创建的名为 'test' 的 metalake，并启动 Trino 容器。

使用 Trino CLI 连接到 Trino 容器并运行查询。

列出所有 Apache Gravitino 管理的目录：

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
 iceberg_test
(4 rows)

Query 20231017_082503_00018_6nt3n, FINISHED, 1 node
```

`gravitino` 目录是由 Trino 目录配置定义的目录。
`iceberg_test` 目录是您在 Apache Gravitino 中创建的目录。
其他目录是常规的用户配置的 Trino 目录。

### 创建表和模式

在 `test.iceberg_test` 目录中创建一个名为 `database_01` 的新模式。

```sql
CREATE SCHEMA iceberg_test.database_01;
```

在模式 `iceberg_test.database_01` 中创建一个名为 `table_01` 的新表。

```sql
CREATE TABLE iceberg_test.database_01.table_01
(
name varchar,
salary int
) with (
  partitioning = ARRAY['salary'],
  sorted_by = ARRAY['name']
);
```

### 写入数据

向表 `table_01` 中插入数据：

```sql
INSERT INTO iceberg_test.database_01.table_01 (name, salary) VALUES ('ice', 12);
```

从 select 将数据插入到表 `table_01` 中：

```sql
INSERT INTO iceberg_test.database_01.table_01 (name, salary) SELECT * FROM iceberg_test.database_01.table_01;
```

将数据更新到表 `table_01` 中：

```sql
UPDATE iceberg_test.database_01.table_01 SET name='ice_update' WHERE salary=12;
```

删除表 `table_01` 中的数据：

```sql
DELETE FROM iceberg_test.database_01.table_01 WHERE name='ice';
```

将数据合并到表 `table_01` 中：

```sql
MERGE INTO iceberg_test.database_01.table_01 t USING iceberg_test.database_01.table_02 s
    ON (t.name = s.name)
    WHEN MATCHED AND s.name = 'bob'
        THEN DELETE
    WHEN MATCHED
        THEN UPDATE
            SET salary = s.salary + t.salary
    WHEN NOT MATCHED
        THEN INSERT (name, salary)
              VALUES (s.name, s.salary);
```

### 查询数据

查询 `table_01` 表：

```sql
SELECT * FROM iceberg_test.database_01.table_01;
```

### 修改表

向 `table_01` 表添加一个新列 `age`：

```sql
ALTER TABLE iceberg_test.database_01.table_01 ADD COLUMN age int;
```

从 `table_01` 表中删除 `age` 列：

```sql
ALTER TABLE iceberg_test.database_01.table_01 DROP COLUMN age;
```

将 `table_01` 表重命名为 `table_02`：

```sql
ALTER TABLE iceberg_test.database_01.table_01 RENAME TO iceberg_test.database_01.table_02;
```

### 丢弃

删除模式：

```sql
DROP SCHEMA iceberg_test.database_01;
```

删除表：

```sql
DROP TABLE iceberg_test.database_01.table_01;
```

## HDFS 用户名和权限

在 Trino 中为 Iceberg 表运行任何 `Insert` 语句之前，
你必须检查 Trino 用于访问 HDFS 的用户是否拥有仓库目录的访问权限。
通过在 Trino JVM 配置中设置 HADOOP_USER_NAME 系统属性来覆盖此用户名，
将 hdfs_user 替换为适当的用户名：

```text
-DHADOOP_USER_NAME=hdfs_user
```

## S3

在 Iceberg catalog 中使用 AWS S3 时，用户需要配置 Trino Iceberg 连接器的
AWS S3 相关属性，这些属性需在 catalog 的属性中进行配置。请参考
[Hive 连接器与 Amazon S3](https://trino.io/docs/current/connector/hive-s3.html) 的文档。
这些配置必须在 Iceberg catalog 的属性中使用 `trino.bypass.` 前缀才能生效。

要在 Trino CLI 中创建带有 AWS S3 配置的 Iceberg 目录，请使用以下命令：

```sql
call gravitino.system.create_catalog(
    'gt_iceberg',
    'lakehouse-iceberg',
    map(
        array['uri', 'catalog-backend', 'warehouse',
          'trino.bypass.hive.s3.aws-access-key', 'trino.bypass.hive.s3.aws-secret-key', 'trino.bypass.hive.s3.region',
          's3-access-key-id', 's3-secret-access-key', 's3-region', 'io-impl'
        ],
        array['thrift://hive:9083', 'hive', 's3a://trino-test-ice/dw2',
        '<aws-access-key>', '<aws-secret-key>', '<region>',
        '<aws-access-key>', '<aws-secret-key>', '<region>', 'org.apache.iceberg.aws.s3.S3FileIO']
    )
);
```

- `trino.bypass.hive.s3.aws-access-key`、`trino.bypass.hive.s3.aws-secret-key`、`trino.bypass.hive.s3.region` 的配置
是 Apache Gravitino Trino 连接器的必需配置。
- `s3-access-key-id`、`s3-secret-access-key`、`io-impl` 和 `s3-region` 的配置。
是 [Apache Gravitino Iceberg catalog](../lakehouse-iceberg-catalog.md#s3) 的必需配置。
- `location` 指定 AWS S3 上的存储路径。在继续操作之前，请确保 AWS S3 上存在指定的目录。

成功创建 Iceberg catalog 后，用户可以按如下方式创建 schemas 和 tables：

```sql
CREATE SCHEMA gt_iceberg.gt_db03;

CREATE TABLE gt_iceberg.gt_db03.tb01 (
    name varchar,
    salary int
);
```

运行该命令后，这些表即可用于在 AWS S3 上进行数据读写操作。

:::note
Apache Gravitino 服务器中的 Iceberg catalog 模块应该添加 AWS S3 支持。
参见 [Apache Gravitino Iceberg catalog](../lakehouse-iceberg-catalog.md#s3)。
:::
