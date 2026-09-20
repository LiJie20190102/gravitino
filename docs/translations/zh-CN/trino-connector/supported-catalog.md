---
title: "Trino Connector Catalog Support"
slug: "/trino-connector/supported-catalog"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino Trino 连接器当前支持的目录如下：

- [Hive](catalog-hive.md)
- [Iceberg](catalog-iceberg.md)
- [MySQL](catalog-mysql.md)
- [PostgreSQL](catalog-postgresql.md)
- [AWS Glue](catalog-glue.md)

## 创建目录

用户可以通过 Gravitino Trino 连接器创建目录，然后将它们加载到 Trino 中。
Gravitino Trino 连接器提供以下存储过程来创建、删除和修改目录。
用户还可以使用系统表 `catalog` 来描述所有目录。

创建目录：

```sql
create_catalog(CATALOG varchar, PROVIDER varchar, PROPERTIES MAP(VARCHAR, VARCHAR), IGNORE_EXIST boolean);
```

- CATALOG：要创建的 catalog 名称。
- PROVIDER：catalog 提供者。支持的值：`hive`、`lakehouse-iceberg`、`jdbc-mysql`、`jdbc-postgresql`、`glue`。
- PROPERTIES：catalog 的属性。
- IGNORE_EXIST：用于在 catalog 已存在时忽略错误的标志。它是可选的，默认值为 `false`。

The type of catalog properties reference:
- [Hive catalog](../apache-hive-catalog.md#catalog-properties)
- [Iceberg catalog](../lakehouse-iceberg-catalog.md#catalog-properties)
- [MySQL catalog](../jdbc-mysql-catalog.md#catalog-properties)
- [PostgreSQL catalog](../jdbc-postgresql-catalog.md#catalog-properties)
- [AWS Glue catalog](../aws-glue-catalog.md#catalog-properties)


删除目录：

```sql
drop_catalog(CATALOG varchar, IGNORE_NOT_EXIST boolean);
```

- CATALOG：要删除的目录名称。
- IGNORE_NOT_EXIST：如果目录不存在，用于忽略错误的标志。它是可选的，默认值为 `false`。


修改目录：

```sql
alter_catalog(CATALOG varchar, SET_PROPERTIES MAP(VARCHAR, VARCHAR), REMOVE_PROPERTIES ARRY[VARCHAR]);
```

- CATALOG: 要更改的目录名称。
- SET_PROPERTIES: 要设置的属性。
- REMOVE_PROPERTIES: 要移除的属性。

这些存储过程位于 `gravitino` 连接器和 `system` 模式下。
因此，你需要在 `trino-cli` 中使用以下 SQL 来调用它们：


描述目录：

系统表 `gravitino.system.catalog` 用于描述所有目录。

```sql
select * from gravitino.system.catalog;
```

结果如下：

```test
     name     | provider |                                                 properties
--------------+----------+-------------------------------------------------------------------------------------------------------------
 gt_hive      | hive     | {gravitino.bypass.hive.metastore.client.capability.check=false, metastore.uris=thrift://trino-ci-hive:9083}
```

检查目录注册状态：

`gravitino.system.catalog` 列出了 Gravitino 服务器已知的关系型目录，但不包括任何
匹配 `gravitino.trino.skip-catalog-patterns` 的目录。列在其中的目录不一定可用
在 Trino 中：注册它是一个可能失败的单独步骤。`gravitino.system.catalog_status` 涵盖了
连接器考虑过的每个目录，包括被 `catalog` 过滤掉的那些，并说明为什么每个
目录已注册或未注册。

```sql
select catalog_name, status, last_error from gravitino.system.catalog_status;
```

结果如下：

```test
 catalog_name | status     | last_error
--------------+------------+-------------------------------------------------
 gt_hive      | REGISTERED | NULL
 gt_iceberg   | FAILED     | Access Denied: Cannot create catalog gt_iceberg
 gt_files     | UNSUPPORTED| Only relational catalogs are supported, the catalog type is FILESET
```

| 列                   | 描述                                                                                                                            |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `metalake`           | 该目录所属的 metalake。                                                                                                   |
| `catalog_name`       | Gravitino 中目录的名称。                                                                                                  |
| `trino_catalog_name` | 目录在 Trino 中注册的名称，如 `SHOW CATALOGS` 中所示。                                                   |
| `provider`           | 目录提供者，例如 `hive` 或 `lakehouse-iceberg`。                                                                       |
| `status`             | `REGISTERED`、`FAILED`、`UNSUPPORTED` 或 `SKIPPED` 之一。见下表。                                                        |
| `last_error`         | 目录未注册的原因，如果已注册则为 `NULL`。                                                                           |
| `last_attempt_time`  | 目录最后一次被处理的时间，采用 ISO-8601 UTC 时间戳格式。                                                                     |
| `last_success_time`  | 目录最后一次成功注册的时间，如果从未成功注册则为 `NULL`。当目录后来失败或变得不受支持时，该值会保留。 |
| `failure_count`      | 连续失败的尝试次数，如果最后一次尝试成功则为 `0`。                                                        |

| 状态        | 含义                                                                                         |
|---------------|-------------------------------------------------------------------------------------------------|
| `REGISTERED`  | 目录已在 Trino 中注册，并出现在 `SHOW CATALOGS` 中。                              |
| `FAILED`      | 上次注册尝试失败，`last_error` 包含失败原因。每次刷新时重试。   |
| `UNSUPPORTED` | 目录不是关系型的，或者其提供者不受连接器支持。               |
| `SKIPPED`     | 目录匹配 `gravitino.trino.skip-catalog-patterns`，故意未注册。 |

在连接器列出任何目录之前就使其停止运行的故障，例如无法访问的
Gravitino 服务器，不会留下任何可供附加的行。`gravitino.system.load_status` 报告
循环本身的健康状况，并且始终只有一行。

```sql
select * from gravitino.system.load_status;
```

| 列                 | 描述                                                                                                                                                                   |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `trino_reachable`      | 加载循环上一次通过 JDBC 探测时 Trino 服务器是否响应。在其未响应时不会注册任何目录，并且 `last_error` 包含连接错误。 |
| `last_attempt_time`    | 循环上一次运行的时间，格式为 ISO-8601 UTC 时间戳。                                                                                                                         |
| `last_success_time`    | 循环上一次成功完成的时间，如果从未成功完成则为 `NULL`。                                                                                                            |
| `consecutive_failures` | 连续失败运行的次数，当上一次运行成功时为 `0`。                                                                                                       |
| `last_error`           | 上一次运行未能完成的原因，包括 Trino 服务器不可达的情况，成功时为 `NULL`。                                                             |
| `metalake_errors`      | metalake 名称到其上一次错误的 JSON 映射，当所有 metalake 均加载成功时为 `NULL`。在此处失败的 metalake 也会导致整个运行失败。                                   |

这两个表均由 coordinator 提供服务，并反映上次刷新，该刷新每
`gravitino.metadata.refresh-interval-seconds` 秒（默认为 10）运行一次。刚刚创建的 catalog
可能尚未被处理。

示例：
运行以下 SQL，使用 `jdbc-mysql` 提供程序创建一个名为 `mysql` 的目录。

```sql
-- Call stored procedures with position.
call gravitino.system.create_catalog(
    'mysql',
    'jdbc-mysql',
    Map(
        Array['jdbc-url', 'jdbc-user', 'jdbc-password', 'jdbc-driver'],
        Array['jdbc:mysql://192.168.164.4:3306?useSSL=false', 'trino', 'ds123', 'com.mysql.cj.jdbc.Driver']
    )
);
call gravitino.system.drop_datalog('mysql');

-- Call stored procedures with name.
call gravitino.system.create_catalog(
    catalog =>'mysql',
    provider => 'jdbc-mysql',
    properties => Map(
        Array['jdbc-url', 'jdbc-user', 'jdbc-password', 'jdbc-driver'],
        Array['jdbc:mysql://192.168.164.4:3306?useSSL=false', 'trino', 'ds123', 'com.mysql.cj.jdbc.Driver']
    ),
    ignore_exist => true
);

call gravitino.system.drop_datalog(
    catalog => 'mysql'
    ignore_not_exist => true
);

call gravitino.system.alter_catalog(
    catalog => 'mysql',
    set_properties=> Map(
        Array['jdbc-url'],
        Array['jdbc:mysql://127.0.0.1:3306?useSSL=false']
    ),
    remove_properties => Array['jdbc-driver']
);
```

如果您需要有关目录的更多信息，请参阅：
[创建目录](../manage-catalogs-and-schemas.md#create-a-catalog)。

## 传递 Trino 连接器配置

Gravitino catalog 由 Trino connector 实现，因此您可以将 Trino connector 配置传递给 Gravitino catalog。
例如，您想为 Hive catalog 设置 `hive.config.resources` 配置，您可以将该配置传递给
Gravitino catalog，如下所示：

```sql
call gravitino.system.create_catalog(
    'gt_hive',
    'hive',
    map(
        array['metastore.uris', 'trino.bypass.hive.config.resources'],
        array['thrift://trino-ci-hive:9083', '/tmp/hive-site.xml,/tmp/core-site.xml']
    )
);
```

配置键中带有 `trino.bypass.` 前缀，用于指示 Gravitino Trino 连接器在 Trino 运行时中将 Trino 连接器配置传递给 Gravitino catalog。

请注意，如果 Trino 连接器属性直接从 Gravitino catalog 继承值，则这些配置无法通过任何 `trino.bypass.*` 属性进行覆盖。
例如，Trino MySQL 连接器属性 `connection-url`、`connection-user` 和 `connection-password` 直接继承在 Gravitino MySQL catalog 中定义的 `jdbc-url`、`jdbc-user` 和 `jdbc-password` 值。
因此，定义 `trino.bypass.connection-url`、`trino.bypass.connection-user` 或 `trino.bypass.connection-password` 将被忽略且不生效。

更多 Trino 连接器配置可以参考：
- [Hive 目录](https://trino.io/docs/current/connector/hive.html#hive-general-configuration-properties)
- [Iceberg 目录](https://trino.io/docs/current/connector/iceberg.html#general-configuration)
- [MySQL 目录](https://trino.io/docs/current/connector/mysql.html#general-configuration-properties)
- [PostgreSQL 目录](https://trino.io/docs/current/connector/postgresql.html#general-configuration-properties)

## Trino 与 Apache Gravitino 之间的数据类型映射

Gravitino Trino 连接器目前支持 Trino 和 Gravitino 之间的以下数据类型转换。根据具体的 catalog，Gravitino 可能不支持该特定 catalog 的某些数据类型转换，例如，
Hive 不支持 `TIME` 数据类型。

| Gravitino 类型        | Trino 类型               |
|-----------------------|--------------------------|
| Boolean               | BOOLEAN                  |
| Byte                  | TINYINT                  |
| Short                 | SMALLINT                 |
| Integer               | INTEGER                  |
| Long                  | BIGINT                   |
| Float                 | REAL                     |
| Double                | DOUBLE                   |
| Decimal               | DECIMAL                  |
| String                | VARCHAR                  |
| Varchar               | VARCHAR                  |
| FixedChar             | CHAR                     |
| Binary                | VARBINARY                |
| Date                  | DATE                     |
| Time                  | TIME                     |
| Timestamp             | TIMESTAMP                |
| TimestampWithTimezone | TIMESTAMP WITH TIME ZONE |
| List                  | ARRAY                    |
| Map                   | MAP                      |
| Struct                | ROW                      |

有关 Trino 数据类型的更多信息，请参阅 [Trino 数据类型](https://trino.io/docs/current/language/types.html)；有关 Gravitino 数据类型，请参阅 [Gravitino 数据类型](../tables-and-views.md#table-column-type)。

## 故障排除

注册在后台进行，因此注册失败的目录根本不会出现在
`SHOW CATALOGS` 中。从 `gravitino.system.catalog_status` 开始，而不是 coordinator 日志。

| 症状                                                            | 可能原因                                                                                                      |
|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| 某个 catalog 未在 `SHOW CATALOGS` 中显示                            | 查询 `gravitino.system.catalog_status` 并读取 `status` 和 `last_error`，然后按照以下各行进行排查              |
| `status = FAILED`，`last_error` 提及 `Access Denied`             | `trino.jdbc.user` 缺少允许运行 `CREATE CATALOG` 的 Trino 系统角色                              |
| `status = FAILED`，`last_error` 提及某个配置属性    | 某个 `trino.bypass.` 属性未被底层 Trino connector 接受                                        |
| `status = UNSUPPORTED`                                               | 该 catalog 不是关系型的，或者其 provider 不在支持的列表中。`last_error` 列出了支持的 providers |
| `status = SKIPPED`                                                   | 该 catalog 匹配了 `gravitino.trino.skip-catalog-patterns`                                                         |
| 该 catalog 在 `catalog_status` 中完全没有对应行                    | 加载循环从未到达它。检查 `gravitino.system.load_status`                                                |
| `load_status.trino_reachable = false`                                  | connector 无法通过 JDBC 连接到 Trino。`last_error` 包含连接错误。检查 `discovery.uri`、`trino.jdbc.user` 和 `trino.jdbc.password` |
| `load_status.last_error` 提及连接被拒绝                 | Gravitino 服务器不可达。检查 `gravitino.uri`                                                          |
| `load_status.metalake_errors` 提及某个 metalake                       | 该 metalake 无法被列出，其他 metalake 不受影响                                               |
| 查询 `gravitino.system.catalog_status` 本身失败              | entry catalog 未初始化。该错误在创建 entry catalog 时报告，请检查启动时的 Trino 服务器日志 |
