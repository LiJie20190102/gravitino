---
title: "Access Control"
slug: "/security/access-control"
keyword: "security"
license: "This software is licensed under the Apache License version 2."
---

## 概述

Apache Gravitino 将许多系统的 catalog 联合在一个单一的 metalake 下，因此权限是
在其中统一定义，而不是在每个系统中单独定义。当启用授权时，服务器
在操作运行之前检查每个请求，如果调用者没有相应的权限，则拒绝该请求。

两件事决定了答案：

- **所有权**伴随创建而产生。创建对象的人即拥有该对象，并且拥有它附带
修改它、删除它以及将其交给其他人的权利。所有权向下延伸，因此拥有
catalog 意味着对其内部的 schemas 和 tables 具有管理控制权。
- **权限**是具名权限，每个权限授权一种操作：`SELECT_TABLE` 读取
table，`CREATE_SCHEMA` 在 catalog 中创建 schema。权限永远不会直接
授予个人。权限被收集到一个角色中，并且该角色被授予给用户和组。

三条规则支配着它们的应用方式：

- **授权向下延伸。** 授权涵盖其授权对象下方的所有内容，包括
现在存在的以及以后创建的内容。对 schema 的 `SELECT_TABLE` 授权涵盖其中的所有表。
- **未授权则一切皆不允许。** 添加到 metalake 且未获得任何授权的用户只能看到
metalake，除此之外什么也看不到。
- **显式拒绝优先于一切。** 角色中的每个权限都带有 `ALLOW` 或 `DENY`
条件，并且 `DENY` 优先于在任何其他角色中以及任何其他
层级的 `ALLOW`。拒绝无法通过在其他地方授权来撤销，这使得 `DENY` 成为
从广泛授权中排除某个对象的方法。

## 快速开始

授权默认关闭。在 `${GRAVITINO_HOME}/conf/gravitino.conf` 中开启它，至少指定
一名服务管理员，并重启服务器：

```properties
gravitino.authorization.enable = true
gravitino.authorization.serviceAdmins = {admin_user}
```

服务管理员是唯一可以创建 metalakes 的用户，之后的所有操作都
通过 API 完成。[Walkthrough](#walkthrough) 运行了一个完整的端到端序列，从一个空服务器
到一个对某个 schema 具有读取权限的用户。[Server Configuration](#server-configuration) 涵盖了
剩余的设置，包括调用者的身份如何到达服务器。

## 授权模型

### 主体与对象

#### 用户和组

用户必须先添加到 metalake 中，才能在其中执行任何操作。组是用户的集合，而
授予组的角色适用于每个成员，这通常是团队管理访问权限的方式。

两者都带有一个可选的 `externalId`，用于将它们与外部身份提供商关联起来。用户还
具有一个 `enabled` 标志，该标志可在不删除用户的情况下暂停访问，并且在
使用 `externalId` 创建用户时默认为 `true`。

#### 服务管理员

服务管理员是一个普通用户，其名字出现在
`gravitino.authorization.serviceAdmins` 中。他们被添加到 metalakes 中，被授予角色，并成为所有者
就像其他任何人一样。该列表仅增加了一项能力，即创建 metalake，并且作为服务器
配置而不是角色，它不能通过 API 被授予或撤销。检查会读取
仅该列表，这正是允许在任何成员关系存在之前创建第一个 metalake 的原因。

#### 对象

Gravitino 管理的所有内容都是一个具有类型和名称的对象。名称是它的点分路径
位于 metalake 之下，因此一个表是 `{catalog}.{schema}.{table}`，并且请求通过
类型和名称来识别对象，因为相同的名称可以存在于多种类型中。

对对象的访问由通过角色授予的权限以及所有权控制。所有权
的行为类似于随对象附带的权限，而不是您授予的权限，并且它带有
没有任何权限名称涵盖的管理权限，即更改、删除和转移。

所有内容都位于 metalake 下，但只有数据对象嵌套在 catalog 下：

```
Metalake (top level)
├── Catalog (represents a data source)
│   └── Schema
│       ├── Table
│       ├── View
│       ├── Topic
│       ├── Fileset
│       ├── Model
│       └── Function
├── Tag
├── Policy
├── Job Template
├── Role
└── Job
```

关于那棵树，有三点值得注意：

- 角色和作业仅受所有权控制，因为没有特权绑定到它们，尽管
在创建它们的 metalake 网关上存在 `CREATE_ROLE` 和 `RUN_JOB`。
- 列完全不出现。它们通过其所属的表被访问，并且不带有自身的
控制，因此在此模型中没有列级别的授权。
- 用户和组不是对象。它们是特权和所有权被
分配给的主体。

### 资助

#### 权限

权限授权对对象执行特定操作，例如 `SELECT_TABLE` 或
`CREATE_SCHEMA`。权限被添加到角色中，角色再被授予给用户和组。权限
从不直接授予给用户。

#### 角色

角色是一组命名的权限，授予给用户和组。权限永远不会被授予
直接给用户。

角色包含对象，并且对于每个对象都有一个权限列表，每个权限都带有一个 `ALLOW` 或 `DENY`
条件。权限仅绑定到其支持的对象类型，因此 `CREATE_TABLE` 绑定到 metalake，
catalog 或 schema，绝不会绑定到 table。创建角色的人拥有它，并且可以修改或删除它。

#### 所有权

所有权可以由组或用户持有，在这种情况下，该组的每个成员都持有
它，并且可以随时转移。它适用于 metalakes、catalogs、schemas、表、视图、
topics、filesets、模型、函数、角色、标签、策略、作业模板和作业。

### Resolution

#### 评估请求

每个已授权的端点都声明了调用者可调用它的条件，并且检查
只要其中任何一个条件成立即通过。例如，在以下情况下加载表会成功：

- 调用者拥有 metalake 或 catalog。
- 调用者拥有 schema 并持有 `USE_CATALOG`。
- 调用者同时持有 `USE_CATALOG` 和 `USE_SCHEMA`，并且额外拥有表或持有
`SELECT_TABLE` 或 `MODIFY_TABLE`。

注意第三种情况。在模式上授予 `SELECT_TABLE` 权限涵盖了该模式下的每个表，但仅凭
其自身不授予任何权限，因为仍然缺少遍历权限。

失败的检查会返回 `403 Forbidden`。一些读取路径会改为返回 `404 Not Found`，以便让一个
调用者无法推断出他们无权查看的对象的存在。列表操作不会
失败；它们只返回调用者有权查看的条目。

#### 允许和拒绝

`DENY` 始终获胜。它会击败同一角色中的 `ALLOW`，用户持有的任何其他角色中的 `ALLOW`，
以及层次结构中任何其他级别的 `ALLOW`，无论在哪个方向：catalog 上的 `DENY`
优先于其 metalake 上的 `ALLOW`，而 metalake 上的 `DENY` 优先于其 catalog 上的 `ALLOW`。
因此，无法通过在其他地方授予某些权限来绕过拒绝。

同级权限彼此独立。`DENY MODIFY_TABLE` 会使 `ALLOW SELECT_TABLE`
保持不受影响，对于 `PRODUCE_TOPIC` 和 `CONSUME_TOPIC`，以及 `READ_FILESET` 和
`WRITE_FILESET` 也是如此。要同时拒绝读取和写入，请将两者都拒绝。

## 权限及其允许的操作

**Grantable On** 列出了权限可绑定到的对象类型，以及它所绑定的对象
设置授权的范围。将权限绑定到未为其列出的类型将被拒绝。

### 数据对象权限

| 权限            | 可授权对象                                                                | 允许的操作                                                       |
|----------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------|
| `CREATE_CATALOG`     | Metalake                                                                    | 创建目录                                                      |
| `USE_CATALOG`        | Metalake, Catalog                                                           | 使用范围内的任何目录，并访问其中的对象            |
| `CREATE_SCHEMA`      | Metalake, Catalog, Schema                                                   | 创建范围内的模式或嵌套模式                            |
| `USE_SCHEMA`         | Metalake, Catalog, Schema                                                   | 使用范围内的任何模式，并访问其中的对象             |
| `CREATE_TABLE`       | Metalake, Catalog, Schema                                                   | 在范围内的任何模式中创建表                                 |
| `PROBE_TABLE_LIKE`   | Metalake, Catalog, Schema, Table, View                                      | 探测类似表的对象是否存在，而不读取其数据    |
| `SELECT_TABLE`       | Metalake, Catalog, Schema, Table                                            | 读取范围内的任何表                                              |
| `MODIFY_TABLE`       | Metalake, Catalog, Schema, Table                                            | 读取、写入以及修改范围内任何表的结构       |
| `CREATE_VIEW`        | Metalake, Catalog, Schema                                                   | 在范围内的任何模式中创建视图                                  |
| `SELECT_VIEW`        | Metalake, Catalog, Schema, View                                             | 读取范围内的视图元数据                                          |
| `CREATE_TOPIC`       | Metalake, Catalog, Schema                                                   | 在范围内的任何模式中创建主题                                 |
| `CONSUME_TOPIC`      | Metalake, Catalog, Schema, Topic                                            | 消费范围内的任何主题                                      |
| `PRODUCE_TOPIC`      | Metalake, Catalog, Schema, Topic                                            | 消费、生产以及修改范围内的任何主题               |
| `CREATE_FILESET`     | Metalake, Catalog, Schema                                                   | 在范围内的任何模式中创建文件集                               |
| `READ_FILESET`       | Metalake, Catalog, Schema, Fileset                                          | 读取范围内的任何文件集                                            |
| `WRITE_FILESET`      | Metalake, Catalog, Schema, Fileset                                          | 读取、写入以及修改范围内的任何文件集                          |
| `REGISTER_MODEL`     | Metalake, Catalog, Schema                                                   | 在范围内的任何模式中注册模型                               |
| `LINK_MODEL_VERSION` | Metalake, Catalog, Schema, Model                                            | 将版本链接到范围内的任何模型                                  |
| `USE_MODEL`          | Metalake, Catalog, Schema, Model                                            | 读取范围内任何模型的元数据并下载其版本   |
| `USE_SECRET`         | Metalake, Catalog, Schema, Table, View, Topic, Fileset, Model, ModelVersion | 检索明文密钥并为范围内的对象提供凭证 |
| `REGISTER_FUNCTION`  | Metalake, Catalog, Schema                                                   | 在范围内的任何模式中注册函数                            |
| `EXECUTE_FUNCTION`   | Metalake, Catalog, Schema, Function                                         | 读取并执行范围内的任何函数             |
| `MODIFY_FUNCTION`    | Metalake, Catalog, Schema, Function                                         | 修改或删除范围内的任何函数                                  |

`SELECT_TABLE` 或 `MODIFY_TABLE` 足以加载表的元数据。主题和文件集
具有类似的读/写权限对。视图没有修改权限：`SELECT_VIEW` 读取
视图元数据，而更改或删除视图仅限所有者。

`CREATE_MODEL` 和 `CREATE_MODEL_VERSION` 是 `REGISTER_MODEL` 和
`LINK_MODEL_VERSION` 的已弃用别名。它们解析为相同的授权，因此现有的授权仍然有效，但
它们将在未来的版本中被移除。请在新的角色中使用当前的名称。

### 治理与管理权限

| 权限               | 可授予对象                                                            | 允许的操作                                     |
|-------------------------|-------------------------------------------------------------------------|----------------------------------------------------|
| `MANAGE_USERS`          | Metalake                                                                | 添加和删除用户                               |
| `MANAGE_GROUPS`         | Metalake                                                                | 添加和删除组                              |
| `CREATE_ROLE`           | Metalake                                                                | 创建角色                                       |
| `MANAGE_GRANTS`         | Metalake, Catalog, Schema, Table, View, Topic, Fileset, Model, Function | 授予和撤销范围内任何对象的权限 |
| `CREATE_TAG`            | Metalake                                                                | 创建标签                                        |
| `APPLY_TAG`             | Metalake, Tag                                                           | 将标签附加到元数据对象                    |
| `CREATE_POLICY`         | Metalake                                                                | 创建策略                                    |
| `APPLY_POLICY`          | Metalake, Policy                                                        | 将策略附加到元数据对象                |
| `VIEW_SECRET_PROVIDERS` | Metalake                                                                | 列出已配置的密钥提供者                  |
| `REGISTER_JOB_TEMPLATE` | Metalake                                                                | 注册作业模板                             |
| `USE_JOB_TEMPLATE`      | Metalake, JobTemplate                                                   | 从作业模板运行作业                       |
| `RUN_JOB`               | Metalake                                                                | 运行作业                                           |

`MANAGE_GRANTS` 绑定到 metalake 时，额外允许为用户和
该 metalake 范围内的组授予和撤销角色。绑定到其他任何对象时，它仅涵盖该
对象及其后代。

`APPLY_TAG`、`APPLY_POLICY` 和 `USE_JOB_TEMPLATE` 的作用范围与所有其他权限不同，在
本页上。它们绑定的对象是持有者可以使用的工具，而不是操作
所作用的对象。在策略 `pii_masking` 上授予 `APPLY_POLICY` 允许持有者附加该策略
且不能附加其他策略，而在 metalake 上授予该权限则允许他们附加 metalake 中的任何策略。

附加标签或策略会进行两次检查：持有者需要 `APPLY_TAG` 或 `APPLY_POLICY` 用于该
标签或策略，并且另外需要访问被标记的元数据对象。用户
无法标记他们原本无法访问的对象。

### 所需权限

三条规则贯穿始终，因此下文不再重复：

- 拥有该对象或其任何祖先对象，即可满足对其进行的任何检查。表格中的 **Owner** 表示
所有权是唯一的途径，因为没有任何权限授予该操作。
- 访问目录和架构内的对象还需要 `USE_CATALOG` 和 `USE_SCHEMA`。
- 无论权限是针对对象本身还是任何祖先对象，均有效。

列表操作首先需要访问其父级作用域。在该网关检查成功后，它们
仅返回调用者有权查看的条目，对于 metalake 所有者而言则是全部条目。

#### 数据对象

| 对象   | 创建              | 加载                                    | 修改             | 删除  |
|----------|---------------------|-----------------------------------------|-------------------|-------|
| 目录  | `CREATE_CATALOG`    | `USE_CATALOG`                           | 所有者             | 所有者 |
| 架构   | `CREATE_SCHEMA`     | `USE_SCHEMA`                            | 所有者             | 所有者 |
| 表    | `CREATE_TABLE`      | `SELECT_TABLE` 或 `MODIFY_TABLE`        | `MODIFY_TABLE`    | 所有者 |
| 视图     | `CREATE_VIEW`       | `SELECT_VIEW`                           | 所有者             | 所有者 |
| 主题    | `CREATE_TOPIC`      | `CONSUME_TOPIC` 或 `PRODUCE_TOPIC`      | `PRODUCE_TOPIC`   | 所有者 |
| 文件集  | `CREATE_FILESET`    | `READ_FILESET` 或 `WRITE_FILESET`       | `WRITE_FILESET`   | 所有者 |
| 模型    | `REGISTER_MODEL`    | `USE_MODEL`                             | 所有者             | 所有者 |
| 函数 | `REGISTER_FUNCTION` | `EXECUTE_FUNCTION` 或 `MODIFY_FUNCTION` | `MODIFY_FUNCTION` | 所有者 |

测试目录连接遵循目录行。在创建目录之前测试它需要
`CREATE_CATALOG`。使用其存储的配置测试现有目录需要 `USE_CATALOG`，与
加载它相同。使用未保存的建议更改测试现有目录需要
所有权，与修改它相同，因为调用者选择服务器连接的目标。

表统计信息遵循表本身：读取它们需要 `SELECT_TABLE` 或 `MODIFY_TABLE`，
写入它们需要 `MODIFY_TABLE`。模型版本遵循模型：读取需要 `USE_MODEL`，所有者来
修改或删除。获取明文密钥（`getSecrets`）或分发凭证（`getCredentials`）
需要拥有 metalake 或持有 `USE_SECRET` 权限。可以加载对象
但缺乏该访问权限的调用者会收到空结果，而不是禁止访问错误。

View 行适用于通过原生 Gravitino REST API 以及
Iceberg REST Catalog 进行的元数据操作（在启用授权时）。列出操作首先需要访问 schema，并且
然后根据所有权或 `SELECT_VIEW` 过滤单个视图。创建视图会使调用者成为其
所有者，这是用于后续 alter 和 drop 操作的路径。

这些检查仅授权 View 元数据操作。它们不授予对引用表的访问权限
或授权 SQL 执行。当前的 Iceberg 引擎路径使用调用者语义，因此调用者
仍然需要访问底层数据。View API 没有显式的 `INVOKER`/`DEFINER` 选项，
且 Gravitino 不实现 `DEFINER` 执行或新的引擎集成作为此
授权行为的一部分。

原生 View 重命名操作仅更改现有 schema 内的名称，并保持
仅限所有者；它不接受目标 schema。

#### Metalake 对象

| 对象           | 创建                  | 读取                                   | 修改或删除 | 使用                                             |
|------------------|-------------------------|----------------------------------------|-----------------|-------------------------------------------------|
| Metalake         | 服务管理员              | 成员资格                                | 所有者           |                                                 |
| User             | `MANAGE_USERS`          | `MANAGE_USERS`，或用户本人                | `MANAGE_USERS`  |                                                 |
| Group            | `MANAGE_GROUPS`         | `MANAGE_GROUPS`，或其成员                | `MANAGE_GROUPS` |                                                 |
| Role             | `CREATE_ROLE`           | `MANAGE_GRANTS`，或持有者或所有者         | 所有者           | 授予或撤销：`MANAGE_GRANTS`                      |
| Tag              | `CREATE_TAG`            | `APPLY_TAG`                            | 所有者           | 附加：`APPLY_TAG` 以及对对象的访问权限           |
| Policy           | `CREATE_POLICY`         | `APPLY_POLICY`                         | 所有者           | 附加：`APPLY_POLICY` 以及对对象的访问权限        |
| Job template     | `REGISTER_JOB_TEMPLATE` | `USE_JOB_TEMPLATE`                     | 所有者           | 运行作业：`RUN_JOB` 和 `USE_JOB_TEMPLATE`        |
| Job              |                         | 所有者                                  | 所有者           |                                                 |
| 密钥提供者       |                         | 所有者或 `VIEW_SECRET_PROVIDERS`        |                 |                                                 |

secrets-provider 注册表是进程全局服务器配置；metalake 路径仅限定
授权。列出提供者不会返回机密材料。

批量访问控制 API 使用与匹配的单实体操作相同的权限。大多数
批量操作在处理请求之前被授权一次。角色移除按每个
项目进行授权，因为每个角色可以由 metalake 所有者或该角色的所有者移除。批量
请求在 `errors` 中报告项目级失败。

| API                                                 | 所需权限                                 |
|-----------------------------------------------------|----------------------------------------------------|
| `POST /api/bulk/metalakes/{metalake}/users/add`     | metalake 的 `OWNER` 或 `MANAGE_USERS`          |
| `POST /api/bulk/metalakes/{metalake}/users/remove`  | metalake 的 `OWNER` 或 `MANAGE_USERS`          |
| `POST /api/bulk/metalakes/{metalake}/groups/add`    | metalake 的 `OWNER` 或 `MANAGE_GROUPS`         |
| `POST /api/bulk/metalakes/{metalake}/groups/remove` | metalake 的 `OWNER` 或 `MANAGE_GROUPS`         |
| `POST /api/bulk/metalakes/{metalake}/roles/add`     | metalake 的 `OWNER` 或 `CREATE_ROLE`           |
| `POST /api/bulk/metalakes/{metalake}/roles/remove`  | metalake 的 `OWNER`，或 role 的 `OWNER`    |
| `GET /api/metalakes/{metalake}/secrets/providers`   | metalake 的 `OWNER` 或 `VIEW_SECRET_PROVIDERS` |

例如，批量添加用户：

```shell
curl -X POST "http://localhost:8090/api/bulk/metalakes/{metalake}/users/add" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "users": [
    {"name": "analyst"},
    {"name": "developer", "externalId": "developer@example.com", "enabled": true}
  ]
}'
```

批量移除用户：

```shell
curl -X POST "http://localhost:8090/api/bulk/metalakes/{metalake}/users/remove" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "names": ["analyst", "developer"]
}'
```

例如，批量添加组：

```shell
curl -X POST "http://localhost:8090/api/bulk/metalakes/{metalake}/groups/add" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "groups": [
    {"name": "analysts"},
    {"name": "developers", "externalId": "developers@example.com"}
  ]
}'
```

批量移除组：

```shell
curl -X POST "http://localhost:8090/api/bulk/metalakes/{metalake}/groups/remove" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "names": ["analysts", "developers"]
}'
```

例如，批量添加角色：

```shell
curl -X POST "http://localhost:8090/api/bulk/metalakes/{metalake}/roles/add" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "roles": [
    {"name": "analyst", "properties": {}, "securableObjects": []},
    {"name": "developer", "properties": {}, "securableObjects": []}
  ]
}'
```

批量移除角色：

```shell
curl -X POST "http://localhost:8090/api/bulk/metalakes/{metalake}/roles/remove" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "names": ["analyst", "developer"]
}'
```

授予或撤销对象的权限需要该对象或其祖先对象上的 `MANAGE_GRANTS` 权限。
授予或撤销角色，以及覆盖角色的权限，需要该
metalake 上的 `MANAGE_GRANTS` 权限。设置所有者需要所有权。

## 使用 Active Roles 缩小访问范围

默认情况下，请求会根据调用者持有的每个角色进行评估。`X-Gravitino-Active-Roles`
头部会为携带它的请求缩小该集合，因此工作负载仅以它
需要的角色运行，而不是其用户被授予的所有角色。

```text
X-Gravitino-Active-Roles: analyst,reader
```

| 值               | 含义                                             |
|---------------------|-----------------------------------------------------|
| `analyst`           | 激活一个具名角色                             |
| `analyst,reader`    | 激活多个；访问权限仅为这些角色的并集 |
| `ALL`               | 激活调用者持有的所有角色                |
| `NONE`              | 不激活任何角色                                    |
| *(缺失或为空)* | 与 `ALL` 相同                                       |

角色名称精确匹配，并且 `ALL` 和 `NONE` 仅在全部大写时才被识别，因此 `all` 会
被读取为角色名称。周围的空白字符会被修剪，并且重复的名称会被合并。

### 收窄改变了什么

Narrowing only ever subtracts. The server validates the declaration against the roles the caller
actually holds, so the header can never widen access, and a caller that omits it is evaluated exactly
as before.

- **`DENY` 保持全局生效。** 调用者持有的任何角色所携带的拒绝仍然适用，即使该
角色未激活，因此无法利用收窄来逃避拒绝。
- **所有权不受影响。** 源于拥有某个对象的访问权限被直接授予给所有者
而非通过角色，因此所有者即使在 `NONE` 下也能保留它。
- **请求中的每个决策都被收窄**，而不仅仅是直接检查。列表结果会被过滤
以匹配活动集，凭证分发背后的特权也是如此：Iceberg 调用者
其活动角色不再携带 `MODIFY_TABLE` 的，将被分发一个只读存储凭证来代替
可写凭证。

### 错误

| 条件                                                          | 响应          |
|--------------------------------------------------------------------|-------------------|
| 空条目，例如 `analyst,` 中的尾随逗号           | `400 Bad Request` |
| `ALL` 或 `NONE` 与其他任何内容组合，例如 `ALL,analyst` | `400 Bad Request` |
| 格式正确的值，指定了调用者不具备的角色         | `403 Forbidden`   |

不存在的角色和调用者从未被授予的角色都会返回 `403`，因此响应
不能用于发现存在哪些角色名称。未持有的角色会被拒绝而不是被忽略，
这会立即暴露拼写错误，而不是静默地减少访问权限。

### 发送标头

Apache Spark 会将任何 `header.*` 目录属性转发到 Iceberg REST 目录：

```properties
spark.sql.catalog.{catalog}.header.X-Gravitino-Active-Roles = analyst
```

Trino 481 及更高版本会转发在 catalog 上配置的标头：

```properties
iceberg.rest-catalog.http-headers = X-Gravitino-Active-Roles: analyst
```

两者均为目录级且为静态，因此相同的值适用于使用它的每个用户和会话
目录。Java 客户端按客户端实例设置标头：

```java
GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withHeaders(ImmutableMap.of("X-Gravitino-Active-Roles", "analyst"))
    .build();
```

### 范围

收窄适用于 Gravitino 自行执行授权的地方：原生 REST API 和 Iceberg
REST catalog。将执行下推到外部系统的 Catalog 会根据映射的
用户和组进行评估，且永远不会看到声明，因此 header 在此无效。参见
[授权下推](authorization-pushdown.md)。

## 服务器配置

设置位于 `${GRAVITINO_HOME}/conf/gravitino.conf`。默认情况下授权是关闭的；该
[快速入门](#quick-start) 展示了开启它的两个设置。

| 设置 *                        | 描述                                                                                                 | 默认  |
|----------------------------------|-------------------------------------------------------------------------------------------------------------|----------|
| `enable`                         | 启用或禁用授权                                                                             | `false`  |
| `serviceAdmins`                  | 以逗号分隔的服务管理员用户名。当 `enable` 为 `true` 时必填                           | (无)   |
| `impl`                           | 元数据授权实现                                                                       | †        |
| `threadPoolSize`                 | 用于元数据授权请求的线程池大小                                                        | `10`     |
| `jcasbin.cacheExpirationSecs`    | 缓存条目保持有效的时间。降低该值可减少数据陈旧程度并增加后端读取次数               | `3600`   |
| `jcasbin.roleCacheSize`          | 每个角色相关缓存的最大大小。应用于三个缓存，因此实际内存使用量约为该值的 3 倍 | `10000`  |
| `jcasbin.ownerCacheSize`         | 所有者缓存的最大大小                                                                             | `100000` |
| `jcasbin.metadataIdCacheSize`    | 元数据名称到 ID 缓存的最大大小                                                               | `100000` |
| `jcasbin.changePollIntervalSecs` | 服务器轮询实体和所有者更改以使其缓存失效的频率。必须大于零 | `3`      |

\* 设置名称省略了前导 `gravitino.authorization.` 前缀。请在
配置文件中完整写出：

```properties
gravitino.authorization.jcasbin.roleCacheSize = 10000
```

† 默认为 `org.apache.gravitino.server.authorization.jcasbin.JcasbinAuthorizer`。

将 `gravitino.authorization.impl` 设置为
`org.apache.gravitino.server.authorization.PassThroughAuthorizer` 会在启用授权的情况下运行服务器，
但会绕过所有检查。直通模式是为迁移而存在的，不适用于
生产环境。请参阅[在现有 Metalakes 上启用授权](#enabling-authorization-on-existing-metalakes)。

默认授权器将角色和所有权信息保存在 Caffeine 缓存中，因此大多数授权
决策不需要读取后端。当通过 Gravitino API 更改权限或所有权时，
处理该更改的服务器会立即使受影响的条目失效。多节点部署中的其他节点
会在下次轮询时获取该更改，因此撤销操作最多可能需要
`jcasbin.changePollIntervalSecs` 才能在整个集群中生效。如果该时间窗口
对您的环境来说不可接受，请缩短该间隔。

### 身份验证

授权决定调用方可以做什么；身份验证确定调用方是谁。
`gravitino.authenticators` 选择该机制，并默认为 `simple`，它读取一个
未经验证的 HTTP Basic 标头，并且仅适用于本地评估。对于 OAuth：

```properties
gravitino.authenticators = oauth
gravitino.authenticator.oauth.jwksUri = {jwks_uri}
gravitino.authenticator.oauth.serviceAudience = {audience}

# The JWT claims that become the Gravitino user name and group memberships
gravitino.authenticator.oauth.principalFields = preferred_username
gravitino.authenticator.oauth.groupsFields = groups
```

其中两个设置将令牌连接到此页面：

- `principalFields` 指定了 JWT 声明，其值将成为 Gravitino 用户名，因此它必须
生成与你添加到 metalakes 并向其授予角色的相同字符串。它默认为 `sub`，这
通常是一个不透明的提供者 ID，而不是任何人会输入的名称。
- `groupsFields` 指定了提供组成员身份的声明，这就是授予组的角色如何
到达用户。

请参阅 [How to Authenticate](how-to-authenticate.md) 了解 Kerberos 及其他选项。

### 行为说明

- 在创建元数据对象之前，将用户添加到 metalake 中。
- 如果请求未携带用户身份，则操作将以 `anonymous` 用户身份运行。
- 当启用授权时，metalake 的创建者会自动作为用户被添加到其中。

### 在现有 Metalakes 上启用授权

在 `gravitino.authorization.enable` 为 `false` 时创建的 Metalake 没有所有者。一旦完全
启用授权，对无所有者的 metalake 的操作将会失败，因此请先分配所有者。

**步骤 1.** 在直通模式下启用授权，从而开启授权机制
同时绕过检查：

```properties
# Turn authorization on, but bypass every check while you assign owners
gravitino.authorization.enable = true
gravitino.authorization.serviceAdmins = {admin_user_1},{admin_user_2}
gravitino.authorization.impl = org.apache.gravitino.server.authorization.PassThroughAuthorizer
```

重启服务器。

**步骤 2.** 为每个现有的 metalake 设置所有者。

```shell
curl -X PUT \
  "$GRAVITINO/owners/metalake/{metalake}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "{admin_user_1}",
  "type": "USER"
}'
```

**步骤 3.** 删除 `gravitino.authorization.impl` 行，以便默认授权器接管：

```properties
# The same settings with the pass-through line gone, so checks now apply
gravitino.authorization.enable = true
gravitino.authorization.serviceAdmins = {admin_user_1},{admin_user_2}
```

**步骤 4.** 重启服务器。

在完成第 3 步之前，请确认每个 metalake 都有所有者。任何没有所有者的 metalake
在完全授权生效后将变得不可用。
## 演练

三个身份依次行动，从一个空服务器到一个读取单一 schema 的用户。该服务
管理员引导 metalake 并将其移交，`manager` 运行它，而 `staff` 构建并
共享数据。每个身份都出示其自己的 bearer token。

每次调用都会发送相同的两个标头，因此示例中使用了一个辅助函数：

```shell
GRAVITINO=http://localhost:8090/api/metalakes/{metalake}

gravitino() {
  curl -sS -H "Accept: application/vnd.gravitino.v1+json" \
       -H "Content-Type: application/json" "$@"
}
```

**1. 服务管理员创建 metalake 并将其移交。** 创建它会将创建者添加
为用户，并使其成为所有者，这正是授权接下来两次调用的原因。在移交之后，
`manager` 拥有 metalake，服务管理员不再参与其中。

```shell
gravitino -X POST "http://localhost:8090/api/metalakes" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"name": "{metalake}", "comment": "example metalake", "properties": {}}'

gravitino -X POST "$GRAVITINO/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"name": "manager"}'

gravitino -X PUT "$GRAVITINO/owners/metalake/{metalake}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"name": "manager", "type": "USER"}'
```

**2. `manager` 将 catalog 创建委托给 `staff`。** 拥有 metalake 让 `manager` 可以添加用户
并在无需任何授权的情况下创建角色。该角色在 metalake 上拥有 `CREATE_CATALOG` 权限，因此它涵盖了
`staff` 现在和将来创建的每一个 catalog。

```shell
gravitino -X POST "$GRAVITINO/users" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -d '{"name": "staff"}'

gravitino -X POST "$GRAVITINO/roles" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -d '{
  "name": "catalog_manager",
  "properties": {},
  "securableObjects": [
    {
      "fullName": "{metalake}",
      "type": "METALAKE",
      "privileges": [{"name": "CREATE_CATALOG", "condition": "ALLOW"}]
    }
  ]
}'

gravitino -X PUT "$GRAVITINO/permissions/users/staff/grant" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -d '{"roleNames": ["catalog_manager"]}'
```

**3. `staff` 构建出数据。** 创建 catalog 会使 `staff` 成为其所有者，并且该所有权
涵盖其中的所有内容，因此该 schema 不需要进一步的授权。该示例使用 Hive；任何
provider 均可工作，并带有其自身的属性。

```shell
gravitino -X POST "$GRAVITINO/catalogs" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
  "name": "{catalog}",
  "type": "RELATIONAL",
  "provider": "hive",
  "properties": {"metastore.uris": "thrift://{hive_host}:9083"}
}'

gravitino -X POST "$GRAVITINO/catalogs/{catalog}/schemas" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{"name": "{schema}"}'
```

**4. `staff` 授予 `analyst` 读取权限。** 读取一个 schema 需要三项权限：`USE_CATALOG`
和 `USE_SCHEMA` 来访问它，以及 `SELECT_TABLE` 来读取其中的内容。对象名称不会
被验证，因此拼写错误会产生一个不授予任何权限的角色。`analyst` 必须已经是
metalake 中的用户。

```shell
gravitino -X POST "$GRAVITINO/roles" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
  "name": "schema_reader",
  "properties": {},
  "securableObjects": [
    {
      "fullName": "{catalog}",
      "type": "CATALOG",
      "privileges": [{"name": "USE_CATALOG", "condition": "ALLOW"}]
    },
    {
      "fullName": "{catalog}.{schema}",
      "type": "SCHEMA",
      "privileges": [
        {"name": "USE_SCHEMA", "condition": "ALLOW"},
        {"name": "SELECT_TABLE", "condition": "ALLOW"}
      ]
    }
  ]
}'

gravitino -X PUT "$GRAVITINO/permissions/users/analyst/grant" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{"roleNames": ["schema_reader"]}'
```

`analyst` 现在可以读取 `{catalog}.{schema}` 中的每个表，包括之后在那里创建的表，并且
在 metalake 中的其他任何地方都无法执行任何操作。通过 Gravitino 连接器进行的查询将根据
控制上述元数据调用的相同所有权和权限进行授权。

## 端点

路径相对于 `http://localhost:8090/api/metalakes/{metalake}`。有关请求和响应
模式，请参阅 [Gravitino REST API](https://gravitino.apache.org/docs/latest/api/rest/gravitino-rest-api)。

用户、组和角色共享同一种结构。用 `users`、`groups` 或 `roles` 替换
`{collection}`，并用用户、组或角色名称替换 `{name}`：

| 操作 | 方法   | 路径                   |
|-----------|----------|------------------------|
| 创建    | `POST`   | `/{collection}`        |
| 列表      | `GET`    | `/{collection}`        |
| 获取       | `GET`    | `/{collection}/{name}` |
| 删除    | `DELETE` | `/{collection}/{name}` |

将 `?details=true` 添加到列表路径中，以获取完整对象而不是名称。

其余的都是独一无二的：

| 操作                         | 方法       | 路径                                                           |
|-----------------------------------|--------------|----------------------------------------------------------------|
| 向角色授予权限        | `PUT`        | `/permissions/roles/{role}/{object_type}/{object_name}/grant`  |
| 从角色撤销权限     | `PUT`        | `/permissions/roles/{role}/{object_type}/{object_name}/revoke` |
| 替换角色的权限       | `PUT`        | `/permissions/roles/{role}/`                                   |
| 向用户或组授予角色    | `PUT`        | `/permissions/{collection}/{name}/grant`                       |
| 从用户或组撤销角色 | `PUT`        | `/permissions/{collection}/{name}/revoke`                      |
| 列出绑定到对象的角色 | `GET`        | `/objects/{object_type}/{object_name}/roles`                   |
| 获取或设置对象的所有者      | `GET`, `PUT` | `/owners/{object_type}/{object_name}`                          |

替换角色的权限是破坏性的：此后，该角色将确切地持有请求体
包含的内容，且任何未包含在其中的对象都将被丢弃。

### Java 客户端

大多数调用直接映射到 `GravitinoClient` 方法，并由
[Java 文档](https://gravitino.apache.org/docs/latest/api/java/org/apache/gravitino/client/GravitinoClient.html)。
有三个调用接受的参数很难仅从签名推导出来。

角色的对象被构建为嵌套路径，而不是点分字符串：

```java
SecurableObject table =
    SecurableObjects.ofTable(
        SecurableObjects.ofSchema(
            SecurableObjects.ofCatalog("catalog1", Collections.emptyList()),
            "schema1",
            Collections.emptyList()),
        "table1",
        Lists.newArrayList(Privileges.SelectTable.allow()));

Role role = client.createRole("schema_reader", ImmutableMap.of(), Lists.newArrayList(table));
```

权限以 `Set` 的形式传递，且每个权限都带有其条件。这两个的 `List` 重载
方法已被弃用：

```java
MetadataObject schema =
    MetadataObjects.of(Lists.newArrayList("catalog1", "schema1"), MetadataObject.Type.SCHEMA);

client.grantPrivilegesToRole("schema_reader", schema, ImmutableSet.of(Privileges.SelectTable.allow()));
client.revokePrivilegesFromRole("schema_reader", schema, ImmutableSet.of(Privileges.SelectTable.deny()));
```

所有者是通过 `Owner.Type` 设置的，而不是字符串：

```java
client.setOwner(schema, "analyst", Owner.Type.USER);
```

## 相关

- [Gravitino REST API](https://gravitino.apache.org/docs/latest/api/rest/gravitino-rest-api)，用于
每个用户、组、角色、权限和所有者端点的请求和响应模式
- [Java 客户端](../how-to-use-gravitino-client.md) 和
[Python 客户端](../how-to-use-python-client.md)，用于从客户端库调用这些端点
- [`org.apache.gravitino.authorization`](https://gravitino.apache.org/docs/latest/api/java/org/apache/gravitino/authorization/package-summary.html)，
本页面背后的 Java 类：`Privilege`、`Privileges`、`SecurableObject` 和 `Owner`
- [授权下推](authorization-pushdown.md)，用于将执行下推到底层
数据源或外部系统（如 Apache Ranger）
- [如何进行身份验证](how-to-authenticate.md)，用于确定调用者身份
- [本地用户和组](local-users-and-groups.md)
