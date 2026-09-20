---
title: "Authorization Pushdown"
slug: "/security/authorization-pushdown"
keywords:
  - security
  - authorization
  - ranger
license: "This software is licensed under the Apache License version 2."
---

## 概述

授权下推将在 Gravitino 中进行的授权应用到 Apache Ranger，因此权限会在数据所在处强制执行，而不是仅在 Gravitino 内部执行。直接读取表的引擎仍然受其约束。

下推通过 `authorization-provider` 属性针对每个 catalog 进行配置。当 catalog 的权限存在于单个 Ranger 服务中时，将其设置为 `ranger`，或者当一个 catalog 需要将其授权应用于多个时，将其设置为 `chain`。没有该属性的 catalog 仅在 Gravitino 中管理访问权限。

Gravitino 解析哪个 catalog 持有被授权的对象，将操作交给该 catalog 的插件，插件将 Gravitino 权限映射到 Ranger 的模型上，并通过 Ranger admin REST API 进行写入。插件接口并非特定于 Ranger，因此可以添加其他权限系统，而目前随产品发布的是 Ranger。

配置目录后，通过常规的[授权 REST API](https://gravitino.apache.org/docs/latest/api/rest/grant-role-to-user)进行授权。不存在单独的下推调用。

## Ranger

Ranger 提供程序涵盖两种 Ranger 服务类型。`HadoopSQL` 管理 Hive、Iceberg 和 Paimon 目录的模式、表和列。`HDFS` 管理路径，这正是文件集目录所需要的。目录通过 `authorization.ranger.service.type` 选择其中之一。

Spark reaches these catalogs through the Kyuubi authorization plugin. That plugin cannot push updates or deletes for a Paimon catalog.

### 配置

| 属性名称                                         | 描述                                                                                                    | 默认值                     |
|-------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|-----------------------------------|
| `authorization-provider`                              | 设置为 `ranger` 以将授权推送到 Apache Ranger                                                              | (none)                            |
| `authorization.ranger.admin.url`                      | Ranger 管理 Web URI                                                                                       | (none)                            |
| `authorization.ranger.service.type`                   | `HadoopSQL` 或 `HDFS`                                                                                          | (none)                            |
| `authorization.ranger.service.name`                   | 要将策略写入的 Ranger 服务                                                                      | (none)                            |
| `authorization.ranger.auth.type`                      | `simple` 或 `kerberos`                                                                                         | `simple`                          |
| `authorization.ranger.username`                       | Ranger 管理员登录用户名，或 Kerberos principal。需要 Ranger 管理员权限               | (none)                            |
| `authorization.ranger.password`                       | Ranger 管理员登录密码，或 keytab 文件的路径                                                    | (none)                            |
| `authorization.ranger.service.create-if-absent`       | 当 Ranger 服务不存在时创建该服务                                                      | `false`                           |

其余属性仅在 `create-if-absent` 为 `true` 时适用，因为它们描述了 Gravitino 创建的服务。

| 属性名称                                         | 描述                                                              | 默认值                     |
|-------------------------------------------------------|--------------------------------------------------------------------------|-----------------------------------|
| `authorization.ranger.jdbc.driverClassName`           | 新 HadoopSQL 服务的驱动类                                 | `org.apache.hive.jdbc.HiveDriver` |
| `authorization.ranger.jdbc.url`                       | 新 HadoopSQL 服务的 JDBC URL                                     | `jdbc:hive2://127.0.0.1:8081`     |
| `authorization.ranger.hadoop.security.authentication` | 新 HDFS 服务的 Hadoop 安全认证                    | `simple`                          |
| `authorization.ranger.hadoop.security.authorization`  | 新 HDFS 服务的 Hadoop 安全授权                     | (无)                            |
| `authorization.ranger.hadoop.rpc.protection`          | 新 HDFS 服务的 Hadoop RPC 保护                             | `authentication`                  |
| `authorization.ranger.fs.default.name`                | 新 HDFS 服务的默认文件系统                                | `hdfs://127.0.0.1:8090`           |

### 示例

一个 Hive 服务已经由名为 `hiveRepo` 的 Ranger 服务管理，并且可以通过 `172.0.0.100:6080` 访问 Ranger。将该 Hive 服务作为启用了 pushdown 的 Hive catalog 添加到 Gravitino 中，需要以下 catalog 属性。

```properties
authorization-provider=ranger
authorization.ranger.admin.url=172.0.0.100:6080
authorization.ranger.auth.type=simple
authorization.ranger.username={ranger_admin_user}
authorization.ranger.password={ranger_admin_password}
authorization.ranger.service.type=HadoopSQL
authorization.ranger.service.name=hiveRepo
```

### Gravitino 创建的角色

Gravitino 在 Ranger 中创建以下托管角色并自行管理其成员资格，因此请将它们视为 Gravitino 所拥有，而不是在 Ranger UI 中编辑它们。

| 角色                            | 目的                                                                                          |
|---------------------------------|---------------------------------------------------------------------------------------------------|
| `GRAVITINO_METALAKE_OWNER_ROLE_<metalake_id>` | 包含拥有所标识 metalake 的用户或组，在 Ranger 策略中拥有所有者权限 |
| `GRAVITINO_CATALOG_OWNER_ROLE_<catalog_id>` | 包含拥有所标识 catalog 的用户或组，在 Ranger 策略中拥有所有者权限 |
| `GRAVITINO_OWNER_ROLE`          | 标记涵盖 schema 和 table 所有者权限的策略项，且不包含任何成员          |

### 将所有者角色从 1.x 迁移至 2.0

Gravitino 1.x 使用了共享的 Ranger 角色 `GRAVITINO_METALAKE_OWNER_ROLE` 和
`GRAVITINO_CATALOG_OWNER_ROLE`。如果多个 catalog 写入同一个 Ranger 服务，成员资格
在任一共享角色中可能会赋予所有者对其所拥有对象之外的访问权限。Gravitino 2.0 使用
上表中带有 ID 后缀的角色，但现有的 Ranger 状态不会被
自动迁移。

升级 Gravitino 服务器后，协调每个现有的 metalake 和启用 Ranger 的 catalog
通过重新设置其当前所有者来实现。设置相同的所有者是安全且幂等的。它会创建
带有 ID 后缀的角色，将该角色授予当前所有者，并替换匹配的 Ranger 策略中的
旧共享角色。在发送 `PUT` 请求之前获取当前所有者；不要从
旧共享角色的成员身份中推断它，因为该角色可能包含多个 catalog 的所有者。

以下示例协调 metalake `prod` 中目录 `sales` 的所有者：

```shell
curl -s \
  -H "Accept: application/vnd.gravitino.v1+json" \
  "http://<gravitino-host>:8090/api/metalakes/prod/owners/CATALOG/sales"

curl -X PUT \
  -H "Content-Type: application/json" \
  -d '{"name":"<current-owner-name>","type":"<USER-or-GROUP>"}' \
  "http://<gravitino-host>:8090/api/metalakes/prod/owners/CATALOG/sales"
```

对每个启用了 Ranger 授权的 catalog 重复相同的过程。还要协调每个
metalake，使用 `METALAKE/<metalake-name>` 代替 `CATALOG/<catalog-name>`。metalake 的
所有者更新将通过该 metalake 中每个启用授权的 catalog 应用。

保留这两个旧版共享角色，直到所有对象均已协调完毕。然后使用 Ranger Admin 来：

1. 验证没有策略引用确切的角色名称 `GRAVITINO_METALAKE_OWNER_ROLE` 或
`GRAVITINO_CATALOG_OWNER_ROLE`。
2. 验证每个 `GRAVITINO_METALAKE_OWNER_ROLE_<metalake_id>` 和
`GRAVITINO_CATALOG_OWNER_ROLE_<catalog_id>` 包含预期的所有者，并测试两个
共享同一个 Ranger 服务的目录的访问权限。
3. 删除这两个旧版共享角色。不要删除带 ID 后缀的角色或
`GRAVITINO_OWNER_ROLE`。

## 链式调用插件

一个 catalog 通常需要在多个位置应用权限。将其数据存储在 HDFS 上的 Hive catalog 既需要 HadoopSQL 服务中的表授权，也需要 HDFS 服务中相应路径的授权，否则直接读取文件的引擎会绕过表权限。

`chain` 提供程序负责处理此操作。将 `authorization.chain.plugins` 设置为您选择的以逗号分隔的名称列表，然后以 `authorization.chain.{plugin_name}` 作为属性前缀来配置每个命名的插件。链中的每个插件都会应用于每次授权操作。

| 属性名称                                            | 描述                                                    |
|----------------------------------------------------------|-----------------------------------------------------------------|
| `authorization-provider`                                 | 设置为 `chain` 以将多个插件应用到此目录         |
| `authorization.chain.plugins`                            | 逗号分隔的插件名称，每个名称指定下文的一个前缀        |
| `authorization.chain.{plugin_name}.ranger.admin.url`     | 该插件的管理 URI                                   |
| `authorization.chain.{plugin_name}.ranger.service.type`  | 该插件的 `HadoopSQL` 或 `HDFS`                           |
| `authorization.chain.{plugin_name}.ranger.service.name`  | 该插件的 Ranger 服务                              |
| `authorization.chain.{plugin_name}.ranger.username`      | 该插件的 Ranger 管理员登录用户名                 |
| `authorization.chain.{plugin_name}.ranger.password`      | 该插件的 Ranger 管理员登录密码                 |

`authorization.chain.plugins` 中的名称是标签而非插件类型，因此只要与其属性使用的前缀相匹配，任何名称均可。链中的每个插件都是 Ranger 插件，因为 Ranger 是唯一可用于链式调用的提供者。

### 示例

Hive 服务由 Ranger 服务 `hiveRepo` 管理，其底层 HDFS 存储由 `hdfsRepo` 管理。将两者链接起来可使表授权与路径授权保持同步。

```properties
authorization-provider=chain
authorization.chain.plugins=hive,hdfs
authorization.chain.hive.ranger.admin.url=http://ranger-service:6080
authorization.chain.hive.ranger.service.type=HadoopSQL
authorization.chain.hive.ranger.service.name=hiveRepo
authorization.chain.hive.ranger.auth.type=simple
authorization.chain.hive.ranger.username={ranger_admin_user}
authorization.chain.hive.ranger.password={ranger_admin_password}
authorization.chain.hdfs.ranger.admin.url=http://ranger-service:6080
authorization.chain.hdfs.ranger.service.type=HDFS
authorization.chain.hdfs.ranger.service.name=hdfsRepo
authorization.chain.hdfs.ranger.auth.type=simple
authorization.chain.hdfs.ranger.username={ranger_admin_user}
authorization.chain.hdfs.ranger.password={ranger_admin_password}
```

## 延伸阅读

- [访问控制](access-control.md) 用于下推转换所基于的 Gravitino 权限模型
- [授权 REST API](https://gravitino.apache.org/docs/latest/api/rest/grant-role-to-user) 用于授予权限
