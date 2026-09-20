---
title: "Local Users and Groups"
slug: "/security/local-users-and-groups"
keywords:
  - security
  - authentication
  - basic authentication
license: "This software is licensed under the Apache License version 2."
---

## 概述

Apache Gravitino 可以通过 `idp-basic` 插件在其自身的关系型元数据存储中存储登录身份。用户名、密码哈希和组成员身份与服务器的其余元数据存放在一起，客户端使用 HTTP Basic 凭据进行身份验证。无需 Gravitino 之外的任何组件。

本地用户存储对 Gravitino 的调用者进行身份验证。它不颁发供其他服务使用的令牌或断言，因此它不是单点登录系统，也不能替代 Okta、Microsoft Entra ID 或 Keycloak。将其用于概念验证、离线安装以及可接受独立身份存储的隔离部署。对于其他情况，请参阅 [如何进行身份验证](how-to-authenticate.md)。

凭据在每次请求时通过 HTTP 标头传输，因此只要网络不完全可信，就请在 [HTTPS](how-to-use-https.md) 后运行服务器。

管理端点位于 `/api/idp/` 下，这反映的是插件的原始名称，而非功能的范围。有关请求和响应架构，请参见 [OpenAPI 定义](../open-api/idp/openapi.yaml)。

## 快速开始

**1. 配置服务器。** 将以下内容添加到 `gravitino.conf` 中。这两个属性都是必需的，因为如果未注册 REST 扩展包，`basic` 认证器将拒绝启动。

```properties
gravitino.authenticators = basic
gravitino.server.rest.extensionPackages = org.apache.gravitino.idp.web.rest.feature
gravitino.authorization.serviceAdmins = admin
```

**2. 设置初始管理员密码。** `gravitino.authorization.serviceAdmins` 中的每个用户名都需要一个已存储的密码，然后才能调用管理端点。在首次启动前设置此项。

```shell
export GRAVITINO_INITIAL_ADMIN_PASSWORD='{admin_password}'
```

**3. 启动 Gravitino 并确认管理员正常工作。**

```shell
curl -s -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Authorization: Basic $(echo -n 'admin:{admin_password}' | base64)" \
  http://localhost:8090/api/version
```

**4. 创建用户。**

```shell
curl -s -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:{admin_password}' | base64)" \
  -d '{"user":"alice","password":"{user_password}"}' \
  http://localhost:8090/api/idp/users
```

## 配置

| 配置项                        | 描述                                                          | 示例                                     |
|-------------------------------------------|----------------------------------------------------------------------|---------------------------------------------|
| `gravitino.authenticators`                | 必须为 `basic`，且不能包含 `simple`                       | `basic`                                     |
| `gravitino.server.rest.extensionPackages` | 注册用户和组管理端点                    | `org.apache.gravitino.idp.web.rest.feature` |
| `gravitino.authorization.serviceAdmins`   | 以逗号分隔的用户名，允许管理所有 IdP 用户和组 | `admin`                                     |

本地用户存储与 `simple` 认证器不兼容，该认证器是服务器默认设置，接受客户端提供的用户名而不检查密码。两个认证器都声明相同的 `Basic` 授权头，服务器会使用列表中第一个声明该头的认证器，因此将 `simple` 列在 `basic` 之前意味着永远不会检查密码。请替换 `simple`，而不是在其基础上添加。

Web UI 从服务器读取 `gravitino.authenticators`，并在 `basic` 为当前启用的认证器时显示用户名和密码表单。

### 密码和用户名规则

这些规则同样适用于用户创建、密码修改以及 `GRAVITINO_INITIAL_ADMIN_PASSWORD`。

| 规则            | 值                                  |
|-----------------|----------------------------------------|
| 用户名        | 必填，且不能包含冒号 |
| 密码长度 | 12 到 64 个字符（含两端）          |

密码可由服务管理员重置，或由用户为自己的账户更改。
该请求仅携带新密码，不包含当前密码；调用者使用其当前凭据通过
HTTP Basic 进行身份验证。

## 管理用户和组

所有管理端点均位于 `http://{host}:{port}/api/idp` 下，并需要 Basic 认证。
大多数操作需要服务管理员。已认证用户也可以 `GET` 或 `PUT`
`/api/idp/users/{user}` 以操作其自身的用户名（仅限读取个人资料 / 修改密码）。
在每个请求中发送 `Accept: application/vnd.gravitino.v1+json`，并且
在带有请求体的请求中发送 `Content-Type: application/json`。

### 用户操作

| 操作     | 方法 | 路径                    | 请求体                                                       |
|---------------|--------|-------------------------|------------------------------------------------------------|
| 获取用户    | GET    | `/api/idp/users/{user}` | 无                                                       |
| 添加用户    | POST   | `/api/idp/users`        | `{"user":"alice","password":"{password}"}`                 |
| 更新用户 | PUT    | `/api/idp/users/{user}` | `{"password":"{new_password}"}` 和/或 `{"enabled":false}` |
| 删除用户 | DELETE | `/api/idp/users/{user}` | 无                                                       |

添加用户的请求体使用字段名 `user` 而不是 `name`。`enabled` 在创建时是可选的，并且默认为 `true`。被禁用的用户无法进行身份验证。`PUT /api/idp/users/{user}` 接受 `password` 和/或 `enabled`；至少需要提供一个。在 `gravitino.authorization.serviceAdmins` 中列出的用户不能被禁用。非管理员调用者只能获取或更新其自身的用户信息，并且在更新时只能更改其密码（不能更改 `enabled` 或其他用户）。

```shell
curl -s -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'alice:{user_password}' | base64)" \
  -d '{"password":"{new_password}"}' \
  http://localhost:8090/api/idp/users/alice
```

```shell
curl -s -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:{admin_password}' | base64)" \
  -d '{"user":"alice","password":"{user_password}"}' \
  http://localhost:8090/api/idp/users
```

### 组操作

| 操作               | 方法 | 路径                                         | 请求体                                                       |
|-------------------------|--------|----------------------------------------------|------------------------------------------------------------|
| 获取组             | GET    | `/api/idp/groups/{group}`                    | 无                                                       |
| 添加组             | POST   | `/api/idp/groups`                            | `{"group":"engineering","comment":"Platform engineering"}` |
| 删除组          | DELETE | `/api/idp/groups/{group}?force={true false}` | 无                                                       |
| 修改组成员 | PUT    | `/api/idp/groups/{group}/users`              | `{"usersToAdd":["alice"],"usersToRemove":["carol"]}`       |

add-group 请求体使用字段名 `group` 而不是 `name`。`comment` 在创建时是可选的（最多 1024 个字符，utf8mb4），并作为组描述存储。除非 `force=true`，否则移除仍包含成员的组会失败。成员变更至少需要 `usersToAdd` 或 `usersToRemove` 中的一个，并且接受在单个请求中同时包含两者。

```shell
curl -s -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:{admin_password}' | base64)" \
  -d '{"usersToAdd":["alice","bob"],"usersToRemove":["carol"]}' \
  http://localhost:8090/api/idp/groups/engineering/users
```

## 授予元数据访问权限

本地用户一旦存在即可进行身份验证，但只有在 metalake 中注册并在其中被授予权限后，才能访问元数据。这两个是独立的步骤，并且用户名必须匹配。

```shell
curl -s -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:{admin_password}' | base64)" \
  -d '{"name":"alice"}' \
  http://localhost:8090/api/metalakes/{metalake}/users
```

当 `gravitino.authorization.enable` 设置为 `true` 时，只有服务管理员才能创建 metalakes。有关角色、权限和所有权，请参见 [访问控制](access-control.md)；有关 metalake 创建，请参见 [管理 Metalakes](../manage-metalake-using-gravitino.md#create-a-metalake)。

## 连接引擎

引擎通过两条路径之一连接到 Gravitino，并且每条路径都使用其各自的 Basic 凭证。

### 通过 Gravitino 连接器

为每个引擎配置连接器，然后添加下方的凭据。有关连接器设置的其余部分，请参见 [Spark 认证](../spark-connector/spark-authentication-with-gravitino.md)、[Flink 认证](../flink-connector/flink-authentication-with-gravitino.md) 和 [Trino 认证](../trino-connector/authentication.md)。

```properties
# Spark
spark.sql.gravitino.authType=basic
spark.sql.gravitino.basic.username={username}
spark.sql.gravitino.basic.password={password}
```

```yaml
# Flink
table.catalog-store.gravitino.gravitino.client.auth.type: basic
table.catalog-store.gravitino.gravitino.client.basic.username: {username}
table.catalog-store.gravitino.gravitino.client.basic.password: {password}
```

```properties
# Trino, in etc/catalog/gravitino.properties
gravitino.client.authType=basic
gravitino.client.basic.username={username}
gravitino.client.basic.password={password}
```

Trino 还需要在 `etc/config.properties` 中配置 `catalog.management=dynamic` 并重启，目录才会出现。

### 通过 Iceberg REST 端点

引擎可以直接连接到 `http://{host}:9001/iceberg/` 的 Iceberg REST 服务，无需 Gravitino 连接器插件。有关其余的设置，请参阅[通过 Iceberg REST 连接 Spark](../iceberg-rest-engine/spark.md)、[通过 Iceberg REST 连接 Flink](../iceberg-rest-engine/flink.md)和[通过 Iceberg REST 连接 Trino](../iceberg-rest-engine/trino.md)。

```properties
# Spark
spark.sql.catalog.{catalog}.rest.auth.type=basic
spark.sql.catalog.{catalog}.rest.auth.basic.username={username}
spark.sql.catalog.{catalog}.rest.auth.basic.password={password}
```

```sql
-- Flink
'rest.auth.type' = 'basic',
'rest.auth.basic.username' = '{username}',
'rest.auth.basic.password' = '{password}'
```

Trino 没有针对 Iceberg REST 的原生 Basic 模式，并且需要 Trino 481 或更高版本，因此直接设置请求头。使用 `echo -n '{username}:{password}' | base64` 生成编码后的凭据，然后设置：

```properties
# Trino, in etc/catalog/{catalog}.properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://localhost:9001/iceberg
iceberg.rest-catalog.http-headers=Authorization: Basic {base64_credentials}
```

## 延伸阅读

- [OpenAPI 定义](../open-api/idp/openapi.yaml) 用于完整的请求和响应模式
- [如何使用 HTTPS](how-to-use-https.md) 用于在传输过程中保护凭据
- [访问控制](access-control.md) 关于已认证用户被允许执行的操作
