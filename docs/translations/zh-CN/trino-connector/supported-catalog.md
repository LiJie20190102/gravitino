---
slug: /trino-connector/supported-catalog
keyword: gravitino connector trino
license: This software is licensed under the Apache License version 2.
title: Trino 连接器目录支持
---
## 简介

Apache Gravitino Trino 连接器当前支持的目录如下：

- [Hive](catalog-hive.md)
- [Iceberg](catalog-iceberg.md)
- [MySQL](catalog-mysql.md)
- [PostgreSQL](catalog-postgresql.md)
- [AWS Glue](catalog-glue.md)

## 创建目录

用户可以通过 Gravitino Trino 连接器创建目录，然后将其加载到 Trino 中。
Gravitino Trino 连接器提供以下存储过程来创建、删除和修改目录。
用户还可以使用系统表 `catalog` 来描述所有目录。

创建目录：

```sql
create_catalog(CATALOG varchar, PROVIDER varchar, PROPERTIES MAP(VARCHAR, VARCHAR), IGNORE_EXIST boolean, METALAKE varchar);
```

- CATALOG：要创建的目录名称。
- PROVIDER：目录提供者。支持的值：`hive`、`lakehouse-iceberg`、`jdbc-mysql`、`jdbc-postgresql`、`glue`。
- PROPERTIES：目录的属性。
- IGNORE_EXIST：如果目录已存在，是否忽略错误。它是可选的，默认值为 `false`。
- METALAKE：要在其中创建目录的 metalake。它是可选的，默认值为已配置的 `gravitino.metalake`；当 `gravitino.metalake` 未设置时，此项为必填。

目录属性类型参考：
- [Hive 目录](../apache-hive-catalog.md#catalog-properties)
- [Iceberg 目录](../lakehouse-iceberg-catalog.md#catalog-properties)
- [MySQL 目录](../jdbc-mysql-catalog.md#catalog-properties)
- [PostgreSQL 目录](../jdbc-postgresql-catalog.md#catalog-properties)
- [AWS Glue 目录](../aws-glue-catalog.md#catalog-properties)


删除目录：

```sql
drop_catalog(CATALOG varchar, IGNORE_NOT_EXIST boolean, METALAKE varchar);
```

- CATALOG：要删除的目录名称。
- IGNORE_NOT_EXIST：如果目录不存在，是否忽略错误。它是可选的，默认值为 `false`。
- METALAKE：目录所属的 metalake。它是可选的，默认值为已配置的 `gravitino.metalake`；当 `gravitino.metalake` 未设置时，此项为必填。


修改目录：

```sql
alter_catalog(CATALOG varchar, SET_PROPERTIES MAP(VARCHAR, VARCHAR), REMOVE_PROPERTIES ARRY[VARCHAR], METALAKE varchar);
```

- CATALOG：要修改的目录名称。
- SET_PROPERTIES：要设置的属性。
- REMOVE_PROPERTIES：要移除的属性。
- METALAKE：目录所属的 metalake。它是可选的，默认值为已配置的 `gravitino.metalake`；当 `gravitino.metalake` 未设置时，此项为必填。

只有当所有 metalake 都已加载时，才能以配置的 metalake 之外的 metalake 为目标
（`gravitino.metalake` 未设置或 `gravitino.catalog-name-with-metalake=true`）。对于未限定的
目录名称，这些存储过程会按名称和 metalake 查找目录，因此另一个
metalake 中具有相同 Trino 目录名称的目录不会受到影响。

这些存储过程位于 `gravitino` 连接器和 `system` schema 下。
因此，你需要在 `trino-cli` 中使用以下 SQL 来调用它们，按名称传递 metalake，
当 `gravitino.metalake` 未设置时：

```sql
call gravitino.system.create_catalog(
    catalog => 'gt_hive',
    provider => 'hive',
    properties => map(array['metastore.uris'], array['thrift://trino-ci-hive:9083']),
    metalake => 'test'
);
```

描述目录：

系统表 `gravitino.system.catalog` 用于描述已配置的
metalake 的所有目录，或者当 `gravitino.metalake` 未设置时描述每个 metalake 的所有目录。

```sql
select * from gravitino.system.catalog;
```

结果类似于：

```test
     name     | provider |                                                 properties                                                  | metalake
--------------+----------+-------------------------------------------------------------------------------------------------------------+----------
 gt_hive      | hive     | {gravitino.bypass.hive.metastore.client.capability.check=false, metastore.uris=thrift://trino-ci-hive:9083} | test
```

`metalake` 列可以区分不同 metalake 中共享名称的目录，
当 `gravitino.metalake` 未设置时。

检查目录注册状态：

`gravitino.system.catalog` 列出 Gravitino 服务器已知的关系型目录，但不包括任何
匹配 `gravitino.trino.skip-catalog-patterns` 的目录。其中列出的目录不一定可在
Trino 中使用：注册它是一个可能失败的单独步骤。`gravitino.system.catalog_status` 涵盖
连接器考虑过的每个目录，包括被 `catalog` 过滤掉的目录，并说明每个目录
为什么已注册或未注册。

```sql
select catalog_name, status, last_error from gravitino.system.catalog_status;
```

结果类似于：

```test
 catalog_name | status     | last_error
--------------+------------+-------------------------------------------------
 gt_hive      | REGISTERED | NULL
 gt_iceberg   | FAILED     | Access Denied: Cannot create catalog gt_iceberg
 gt_files     | UNSUPPORTED| Only relational catalogs are supported, the catalog type is FILESET
```

| 列               | 描述                                                                                                                            |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `metalake`           | 目录所属的 metalake。                                                                                                   |
| `catalog_name`       | Gravitino 中目录的名称。                                                                                                  |
| `trino_catalog_name` | 目录在 Trino 中注册时使用的名称，与 `SHOW CATALOGS` 中显示的一致。                                                   |
| `provider`           | 目录提供者，例如 `hive` 或 `lakehouse-iceberg`。                                                                       |
| `status`             | 取值为 `REGISTERED`、`FAILED`、`UNSUPPORTED` 或 `SKIPPED` 之一。见下表。                                                        |
| `last_error`         | 目录未注册的原因；当目录已注册时为 `NULL`。                                                                           |
| `last_attempt_time`  | 目录上次被处理的时间，采用 ISO-8601 UTC 时间戳。                                                                     |
| `last_success_time`  | 目录上次成功注册的时间；如果从未成功注册则为 `NULL`。当目录之后失败或变为不支持时仍会保留。 |
| `failure_count`      | 连续失败尝试的次数；上次尝试成功时为 `0`。                                                        |

| 状态        | 含义                                                                                         |
|---------------|-------------------------------------------------------------------------------------------------|
| `REGISTERED`  | 目录已在 Trino 中注册，并出现在 `SHOW CATALOGS` 中。                              |
| `FAILED`      | 上次注册尝试失败，`last_error` 包含原因。每次刷新都会重试。   |
| `UNSUPPORTED` | 目录不是关系型的，或者其提供者不受连接器支持。               |
| `SKIPPED`     | 目录匹配 `gravitino.trino.skip-catalog-patterns`，被有意不注册。 |

如果在连接器能够列出目录之前就发生失败，例如无法访问
Gravitino 服务器，则没有行可用于关联该失败。`gravitino.system.load_status` 报告
循环本身的健康状况，并且始终恰好有一行。

```sql
select * from gravitino.system.load_status;
```

| 列                 | 描述                                                                                                                                                                   |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `trino_reachable`      | 上一次负载循环通过 JDBC 探测 Trino 服务器时，Trino 服务器是否响应。当其不响应时，不会注册任何目录，`last_error` 包含连接错误。 |
| `last_attempt_time`    | 循环上次运行的时间，采用 ISO-8601 UTC 时间戳。                                                                                                                         |
| `last_success_time`    | 循环上次成功完成的时间；如果从未成功完成，则为 `NULL`。                                                                                                            |
| `consecutive_failures` | 连续失败运行的次数；上次运行成功时为 `0`。                                                                                                       |
| `last_error`           | 上次运行未完成的原因，包括 Trino 服务器不可达；成功时为 `NULL`。                                                             |
| `metalake_errors`      | 从 metalake 名称到其上次错误的 JSON 映射；每个 metalake 都加载成功时为 `NULL`。在此处失败的 metalake 也会导致整个运行失败。                                   |

这两个表都由协调器提供，并反映上次刷新；刷新每
`gravitino.metadata.refresh-interval-seconds` 秒（默认 10 秒）运行一次。刚刚创建的目录
可能尚未被处理。

示例：
运行以下 SQL，以使用 `jdbc-mysql` 提供者创建名为 `mysql` 的目录。

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

如果需要有关目录的更多信息，请参阅：
[创建目录](../manage-catalogs-and-schemas.md#create-a-catalog)。

## 传递 Trino 连接器配置

Gravitino 目录由 Trino 连接器实现，因此你可以将 Trino 连接器配置传递给 Gravitino 目录。
例如，你想为 Hive 目录设置 `hive.config.resources` 配置，可以将该配置传递给
Gravitino 目录，如下所示：

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

配置键中带有 `trino.bypass.` 前缀，用于指示 Gravitino Trino 连接器在 Trino 运行时将 Trino 连接器配置传递给 Gravitino 目录。

请注意，如果 Trino 连接器属性直接从 Gravitino 目录继承值，则无法通过任何 `trino.bypass.*` 属性覆盖这些配置。
例如，Trino MySQL 连接器属性 `connection-url`、`connection-user` 和 `connection-password` 直接继承 Gravitino MySQL 目录中定义的 `jdbc-url`、`jdbc-user` 和 `jdbc-password` 值。
因此，定义 `trino.bypass.connection-url`、`trino.bypass.connection-user` 或 `trino.bypass.connection-password` 将被忽略，不会生效。

更多 Trino 连接器配置可参阅：
- [Hive 目录](https://trino.io/docs/current/connector/hive.html#hive-general-configuration-properties)
- [Iceberg 目录](https://trino.io/docs/current/connector/iceberg.html#general-configuration)
- [MySQL 目录](https://trino.io/docs/current/connector/mysql.html#general-configuration-properties)
- [PostgreSQL 目录](https://trino.io/docs/current/connector/postgresql.html#general-configuration-properties)

## Trino 与 Apache Gravitino 之间的数据类型映射

Gravitino Trino 连接器目前支持以下 Trino 与 Gravitino 之间的数据类型转换。根据具体目录，Gravitino 可能不支持该特定目录的某些数据类型转换，例如，
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

有关 Trino 数据类型的更多信息，请参阅 [Trino 数据类型](https://trino.io/docs/current/language/types.html)；有关 Gravitino 数据类型的更多信息，请参阅 [Gravitino 数据类型](../tables-and-views.md#table-column-type)。

## 故障排查

注册在后台进行，因此注册失败的目录根本不会出现在
`SHOW CATALOGS` 中。应从 `gravitino.system.catalog_status` 开始排查，而不是协调器日志。

| 症状                                                            | 可能原因                                                                                                      |
|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| 某个目录从 `SHOW CATALOGS` 中缺失                            | 查询 `gravitino.system.catalog_status`，读取 `status` 和 `last_error`，然后参照下面的行              |
| `status = FAILED`，`last_error` 提到 `Access Denied`             | `trino.jdbc.user` 缺少可运行 `CREATE CATALOG` 的 Trino 系统角色                              |
| `status = FAILED`，`last_error` 提到配置属性    | 底层 Trino 连接器不接受某个 `trino.bypass.` 属性                                        |
| `status = FAILED`，`last_error` 提到 `already registered by metalake` | 另一个 metalake 拥有相同的 Trino 目录名称。重命名该目录或设置 `gravitino.catalog-name-with-metalake=true` |
| `status = UNSUPPORTED`                                               | 该目录不是关系型的，或者其提供者不在支持列表中。`last_error` 会列出支持的提供者 |
| `status = SKIPPED`                                                   | 该目录匹配 `gravitino.trino.skip-catalog-patterns`                                                         |
| 该目录在 `catalog_status` 中完全没有行                    | 负载循环从未处理到它。检查 `gravitino.system.load_status`                                                |
| `load_status.trino_reachable = false`                                  | 连接器无法通过 JDBC 访问 Trino。`last_error` 包含连接错误。检查 `discovery.uri`、`trino.jdbc.user` 和 `trino.jdbc.password` |
| `load_status.last_error` 提到连接被拒绝                 | Gravitino 服务器不可达。检查 `gravitino.uri`                                                          |
| `load_status.metalake_errors` 指定了某个 metalake                       | 无法列出该 metalake，其他 metalake 不受影响                                               |
| 查询 `gravitino.system.catalog_status` 本身失败              | 入口目录未初始化。创建入口目录时会报告该错误，请在启动时检查 Trino 服务器日志 |