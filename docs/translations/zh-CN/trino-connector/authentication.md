---
title: "Trino Connector Authentication"
slug: "/trino-connector/authentication"
keyword: "gravitino connector trino authentication"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Gravitino Trino 连接器支持使用与 Gravitino Java 客户端相同的身份验证机制向 Gravitino 服务器进行身份验证：Simple、Basic、OAuth2 和 Kerberos。身份验证通过 Trino 连接器属性文件并使用 `gravitino.client.*` 前缀进行配置。

如果未设置 `gravitino.client.authType`，连接器将以无认证模式运行，并在不提供任何凭据的情况下连接到 Gravitino 服务器。

## 认证类型

### 简单身份验证

简单认证使用用户名向 Gravitino 服务器进行认证。

**`etc/catalog/gravitino.properties` 中的配置：**

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

# Simple authentication with username
gravitino.client.authType=simple
gravitino.user=admin
```

**配置属性：**

| 属性                    | 描述                                                     | 默认值 | 必填                               |
|-----------------------------|-----------------------------------------------------------------|---------------|----------------------------------------|
| `gravitino.client.authType` | 认证类型：`simple`、`basic`、`oauth2` 或 `kerberos` | (无)        | 否                                     |
| `gravitino.user`            | 简单认证的用户名                              | (无)        | 否（如果未指定，则使用系统用户） |

### 基本认证

基本认证使用 HTTP Basic 凭据针对 Gravitino 本地用户存储进行验证。Gravitino
服务器必须启用基本认证。请参阅
[如何认证](../security/how-to-authenticate.md#basic-mode) 了解服务器端设置。

**`etc/catalog/gravitino.properties` 中的配置：**

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

# Basic authentication with local user store
gravitino.client.authType=basic
gravitino.client.basic.username=admin
gravitino.client.basic.password=YourSecureGravitinoPassword
```

**配置属性：**

| 属性                          | 描述                                                     | 默认值 | 必填                   |
|-----------------------------------|-----------------------------------------------------------------|---------------|----------------------------|
| `gravitino.client.authType`       | 认证类型：`simple`、`basic`、`oauth2` 或 `kerberos` | (none)        | 是（用于启用 Basic）      |
| `gravitino.client.basic.username` | 本地用户存储用户名                                       | (none)        | 如果 authType 为 `basic` 则为是 |
| `gravitino.client.basic.password` | 本地用户存储密码                                       | (none)        | 如果 authType 为 `basic` 则为是 |

### OAuth2 认证

OAuth2 身份验证使用 OAuth 2.0 令牌向 Gravitino 服务器进行身份验证。

**`etc/catalog/gravitino.properties` 中的配置：**

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

# OAuth2 authentication
gravitino.client.authType=oauth2
gravitino.client.oauth2.serverUri=http://oauth-server:8080
gravitino.client.oauth2.credential=client_id:client_secret
gravitino.client.oauth2.path=oauth2/token
gravitino.client.oauth2.scope=gravitino
```

**配置属性：**

| 属性                             | 描述                                                     | 默认值 | 必填                    |
|--------------------------------------|-----------------------------------------------------------------|---------------|-----------------------------|
| `gravitino.client.authType`          | 认证类型：`simple`、`basic`、`oauth2` 或 `kerberos` | (无)        | 是（以启用 OAuth2）      |
| `gravitino.client.oauth2.serverUri`  | OAuth2 服务器 URI                                               | (无)        | 是（如果 authType 为 `oauth2`） |
| `gravitino.client.oauth2.credential` | OAuth2 凭证，格式为 `client_id:client_secret`          | (无)        | 是（如果 authType 为 `oauth2`） |
| `gravitino.client.oauth2.path`       | OAuth2 令牌端点路径                                      | (无)        | 是（如果 authType 为 `oauth2`） |
| `gravitino.client.oauth2.scope`      | OAuth2 作用域                                                    | (无)        | 是（如果 authType 为 `oauth2`） |

### 示例：连接到受 OAuth 保护的 Gravitino Server

本示例展示了如何配置 Trino 连接器以连接到受 OAuth 身份验证保护的 Gravitino 服务器。

**1. 使用 OAuth 配置 Gravitino 服务器**（在 `conf/gravitino.conf` 中）：

```properties
gravitino.authenticators=oauth
gravitino.authenticator.oauth.serviceAudience=gravitino
gravitino.authenticator.oauth.defaultSignKey=<your-signing-key>
gravitino.authenticator.oauth.tokenPath=/oauth2/token
gravitino.authenticator.oauth.serverUri=http://localhost:8177
```

**2. 配置 Trino 连接器** (在 `etc/catalog/gravitino.properties` 中)：

```properties
connector.name=gravitino
gravitino.metalake=my_metalake
gravitino.uri=http://localhost:8090

# OAuth2 authentication
gravitino.client.authType=oauth2
gravitino.client.oauth2.serverUri=http://localhost:8177
gravitino.client.oauth2.credential=test:test
gravitino.client.oauth2.path=oauth2/token
gravitino.client.oauth2.scope=test
```

**3. 验证连接：**

```sql
SHOW CATALOGS;
```

### Kerberos 身份验证

Kerberos 认证使用 Kerberos 票据向 Gravitino 服务器进行认证。

**`etc/catalog/gravitino.properties` 中的配置：**

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

# Kerberos authentication with keytab
gravitino.client.authType=kerberos
gravitino.client.kerberos.principal=user@REALM
gravitino.client.kerberos.keytabFilePath=/path/to/user.keytab
```

**配置属性：**

| 属性                                     | 描述                                                         | 默认值   | 必填                                  | 起始版本   |
|----------------------------------------------|---------------------------------------------------------------------|-----------------|-------------------------------------------|-----------------|
| `gravitino.client.authType`                  | 认证类型：`simple`、`basic`、`oauth2` 或 `kerberos`     | (无)          | 是（用于启用 Kerberos）                  | 1.3.0           |
| `gravitino.client.kerberos.principal`        | Kerberos principal                                                  | (无)          | 是，如果 authType 为 `kerberos`             | 1.3.0           |
| `gravitino.client.kerberos.keytabFilePath`   | keytab 文件路径                                                 | (无)          | 否（如果未指定，则使用 ticket cache）   | 1.3.0           |

## 会话凭证转发

设置 `gravitino.client.session.forwardUser=true` 会为每个 Trino 会话用户创建一个专属的 Gravitino 客户端，因此每个用户都会在 Gravitino 审计日志中可见，而不是共享的 `gravitino.user` 或服务身份。它在 `authType=simple` 和 `authType=oauth2` 下受支持。对于没有转发令牌的 OAuth2 会话，连接器会改为重用共享的服务元数据。

**配置 (`authType=simple`):**

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

gravitino.client.authType=simple
gravitino.client.session.forwardUser=true
```

使用 `authType=simple` 时，Trino 会话用户名将作为 simple-auth 身份转发给 Gravitino。

**配置 (`authType=oauth2`):**

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

gravitino.client.authType=oauth2
gravitino.client.oauth2.serverUri=http://oauth-server:8080
gravitino.client.oauth2.credential=client_id:client_secret
gravitino.client.oauth2.path=oauth2/token
gravitino.client.oauth2.scope=gravitino
gravitino.client.session.forwardUser=true
```

使用 `authType=oauth2` 时，当 Trino 协调器在 `token` 键（或配置的 `gravitino.client.session.userTokenCredentialKey`）下用调用者的访问令牌填充会话的 extra-credentials 时，终端用户的 IdP 访问令牌将直接提供给 Gravitino。如果该凭据不存在、为空或仅包含空白字符，连接器将重用共享的服务元数据。这允许经过密码验证的会话（包括内部目录管理 JDBC 会话）使用配置的服务身份及其权限来访问 Gravitino 元数据。使用提供的令牌时遇到的错误仍会传播；它们不会触发此回退。下游目录身份验证（包括 IRC 身份验证）是单独配置的，不会因这种元数据回退而改变。

coordinator 是否能够填充此 extra-credential 取决于 Trino 发行版：

- **Starburst Enterprise** 通过 `http-server.authentication.type=DELEGATED-OAUTH2` 支持此功能 — 参见 [OAuth 2.0 令牌传递](https://docs.starburst.io/latest/security/oauth2-passthrough.html)。
- **开源 Trino 尚不支持此功能。** 目前没有等效的协调器端机制将调用者的 OAuth2 令牌转发到连接器会话中；参见在上游跟踪此功能请求的 [trinodb/trino discussion #24403](https://github.com/trinodb/trino/discussions/24403) 和 [issue #27917](https://github.com/trinodb/trino/issues/27917)。

上面的 `gravitino.client.oauth2.*` 属性仍然配置用于目录发现的共享 bootstrap/admin 客户端 —— 它们与按用户转发的令牌无关。

对于通过 Gravitino Iceberg REST 服务器 (IRC) 访问的 Iceberg catalog —— 每个
`lakehouse-iceberg` catalog，只要 Gravitino 服务器报告其正在运行 IRC；参见 [Iceberg
catalog](./catalog-iceberg.md#how-trino-reaches-the-catalog) —— IRC 自身的认证是
每个 Trino 集群配置一次，使用 `gravitino.iceberg.rest-catalog.` 前缀，并且
`iceberg.rest-catalog.session=USER` 会在 `forwardUser=true` 且 IRC 配置了
`gravitino.iceberg.rest-catalog.security=OAUTH2` 时自动设置（如下所示）：

```properties
gravitino.iceberg.rest-catalog.security=OAUTH2
gravitino.iceberg.rest-catalog.oauth2.credential=service-account-id:service-account-secret
gravitino.iceberg.rest-catalog.oauth2.server-uri=http://your-idp/realms/gravitino/protocol/openid-connect/token
gravitino.iceberg.rest-catalog.oauth2.scope=email
```

这是一个与连接器针对主 Gravitino 所使用的凭据完全独立的凭据
服务器；它不会被自动复用。

对于带有 `catalog-backend=rest` 的 Iceberg catalog（指向其自身的 Iceberg REST Catalog，
连接器不会重新路由该 catalog），连接器不会自行设置 `iceberg.rest-catalog.security`/`iceberg.rest-catalog.session` —— 该 catalog 自身的 `gravitino.client.*` 配置与其底层 Iceberg REST catalog 的身份验证方式无关。要将最终用户的 token 也转发给 REST catalog 本身，请在该 catalog 的属性中显式设置 `trino.bypass.iceberg.rest-catalog.security=OAUTH2` 和 `trino.bypass.iceberg.rest-catalog.session=USER`，并连同其引导的 `trino.bypass.iceberg.rest-catalog.oauth2.*` 凭证一起设置；请参阅下方的操作示例。

**配置属性：**

| 属性                                                  | 描述                                                                                                                                                                            | 默认值 | 必填 | 起始版本 |
|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|---------------|
| `gravitino.client.session.forwardUser`                    | 当为 `true` 且 `authType=simple` 或 `authType=oauth2` 时，按查询将 Trino 会话用户/令牌转发给 Gravitino；没有令牌的 OAuth2 会话使用共享服务元数据 | `false`       | 否       | 1.3.0         |
| `gravitino.client.session.cache.maxSize`                  | 缓存中保留的每个用户的最大会话数                                                                                                                               | `500`         | 否       | 1.3.0         |
| `gravitino.client.session.cache.expireAfterAccessSeconds` | 空闲的每个用户会话从缓存中清除之前的秒数                                                                                                                      | `3600`        | 否       | 1.3.0         |

### 示例：OAuth2 按用户令牌转发

本示例演示了一个完整的配置，其中每个 Trino 用户自己的 OAuth2 访问令牌会被
转发到 Gravitino 和 Iceberg REST catalog (IRC)，而不是单个共享服务
身份。

**1. Trino coordinator：将登录用户的 token 转发给 connectors。** 这是
使得 `authType=oauth2` 转发成为可能的前提条件 —— coordinator 必须
在 `token` 键下，使用调用者的 access token 填充会话的 extra-credentials。

- **Starburst Enterprise**：在 `etc/config.properties` 中设置以下内容：

  ```properties
  http-server.authentication.type=DELEGATED-OAUTH2
  ```

请参阅 [OAuth 2.0 token pass-through](https://docs.starburst.io/latest/security/oauth2-passthrough.html)
获取详情，包括其限制：透传令牌不会被刷新，且必须
比查询生命周期更长。

- **开源 Trino**：目前没有等效的 coordinator 设置。跟踪
[trinodb/trino discussion #24403](https://github.com/trinodb/trino/discussions/24403) 和
[issue #27917](https://github.com/trinodb/trino/issues/27917) 以了解此功能请求。直到
它在上游落地，转发 OAuth2 用户令牌需要一种 Trino 发行版，该发行版
自身提供此 extra-credential。没有它的会话使用共享的服务元数据。

**2. Gravitino 服务器：启用 OAuth2**（在 `conf/gravitino.conf` 中）：

```properties
gravitino.authenticators=oauth
gravitino.authenticator.oauth.serviceAudience=account
gravitino.authenticator.oauth.jwksUri=http://your-idp/realms/gravitino/protocol/openid-connect/certs
gravitino.authenticator.oauth.tokenValidatorClass=org.apache.gravitino.server.authentication.JwksTokenValidator
gravitino.authenticator.oauth.principalFields=preferred_username,email,sub
```

**3. Trino 连接器：启用 OAuth2 转发** (在 `etc/catalog/gravitino.properties` 中)：

```properties
connector.name=gravitino
gravitino.metalake=my_metalake
gravitino.uri=http://localhost:8090

gravitino.client.authType=oauth2
gravitino.client.oauth2.serverUri=http://your-idp
gravitino.client.oauth2.credential=service-account-id:service-account-secret
gravitino.client.oauth2.path=realms/gravitino/protocol/openid-connect/token
gravitino.client.oauth2.scope=email
gravitino.client.session.forwardUser=true
```

`gravitino.client.oauth2.*` 属性配置用于 catalog
发现以及没有转发令牌的会话进行的元数据访问的共享服务身份。使用
`forwardUser=true`，携带来自步骤 1 的令牌的会话验证元数据请求，使用
该令牌来代替。

**4. 创建 metalake 和 catalog。** 首先创建 metalake `my_metalake`（通过
Gravitino REST API、SDK 或 CLI — 参见
[管理 metalakes](../manage-metalake-using-gravitino.md#create-a-metalake)），然后创建一个
在其下的基于 REST 的 Iceberg catalog，在 Trino CLI 中使用
`gravitino.system.create_catalog` 存储过程。为了同时将终端用户的 token 转发给 Iceberg
REST catalog (IRC) 本身，设置 `trino.bypass.iceberg.rest-catalog.security=OAUTH2` 和
`trino.bypass.iceberg.rest-catalog.session=USER` 在 catalog 上，以及其引导
`trino.bypass.iceberg.rest-catalog.oauth2.*` 凭据：

```sql
call gravitino.system.create_catalog(
    'my_catalog',
    'lakehouse-iceberg',
    map(
        array['uri', 'catalog-backend', 'warehouse',
          'trino.bypass.iceberg.rest-catalog.security', 'trino.bypass.iceberg.rest-catalog.session',
          'trino.bypass.iceberg.rest-catalog.oauth2.credential', 'trino.bypass.iceberg.rest-catalog.oauth2.scope',
          'trino.bypass.iceberg.rest-catalog.oauth2.server-uri'
        ],
        array['http://irc-host:9001/iceberg', 'rest', 'my_catalog',
          'OAUTH2', 'USER',
          'service-account-id:service-account-secret', 'email',
          'http://your-idp/realms/gravitino/protocol/openid-connect/token'
        ]
    )
);
```

该过程使用连接器的共享服务客户端在 Gravitino 中创建目录。
目录注册也可以调用连接器的元数据入口点；一个内部的
密码认证的 JDBC 会话（无转发令牌）使用共享服务元数据
在那里。`create_catalog` 既在 Gravitino 中创建目录，又将其加载
到 Trino 中作为其自身的顶级目录——而不是作为模式嵌套在单个 `gravitino`
目录下。如果省略了上述两个 `trino.bypass.iceberg.rest-catalog.*` 属性，REST
目录会保留其自身的默认安全设置，独立于
`gravitino.client.session.forwardUser`，并且最终用户的令牌永远不会到达 IRC。

**5. 以特定用户身份查询。** 在真实的 OIDC 登录流程中，Trino 会填充转发的令牌
在用户登录后自动进行 —— 这种自动填充正是需要
Starburst 的 DELEGATED-OAUTH2（步骤 1）的部分。对于在任何 Trino 发行版（包括
开源 Trino）上进行手动测试，可以直接在 CLI 上设置相同的 extra-credential，而独立于
协调器的配置方式：

```shell
trino --server http://localhost:8080 \
  --user alice \
  --extra-credential token=<alice-idp-access-token> \
  --execute "SHOW SCHEMAS IN my_catalog"
```

Gravitino 将此请求视为 `alice`，而不是共享的服务身份 —— `alice` 自己的
权限生效，并且带有缺失或无效令牌的请求在到达
目录之前被拒绝。因为 `my_catalog` 是使用 `trino.bypass.iceberg.rest-catalog.session=USER` 创建的
在第 4 步中，同一个转发的令牌也会直接到达 IRC，因此基于用户的授权
无论 Trino 是与 Gravitino 的原生 API 通信还是直接与 IRC 通信，都能一致地生效。

## 备注

- 必须配置 Gravitino 服务器并启用相应的身份验证机制。
- 对于 OAuth2 身份验证，请确保可以从 Trino 协调器和工作节点访问 OAuth2 服务器。
- 对于 Kerberos 身份验证，请确保在所有 Trino 节点上正确设置了 Kerberos 配置。
- 身份验证配置通过 `gravitino.client.*` 前缀传递给底层的 Gravitino Java 客户端。

## 另请参阅

- [Gravitino 服务器认证配置](../security/how-to-authenticate.md)
- [本地用户和组](../security/local-users-and-groups.md)
- [Trino 连接器配置](./configuration.md)
