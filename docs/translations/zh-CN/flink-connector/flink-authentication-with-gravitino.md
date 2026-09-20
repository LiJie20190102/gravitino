---
slug: /flink-connector/flink-authentication
keyword: flink connector authentication basic oauth2 kerberos
license: This software is licensed under the Apache License version 2.
---
## 概述

Flink 连接器在访问 Gravitino 服务器时支持 `simple`、`basic`、`oauth2` 和 `kerberos` 身份验证。

| 属性                                                 | 类型   | 默认值 | 描述                                                   | 是否必填 |
|----------------------------------------------------------|--------|---------------|---------------------------------------------------------------|----------|
| table.catalog-store.gravitino.gravitino.client.auth.type | string | (none)        | 当显式设置时，仅支持 `oauth2` 和 `basic`。 | 否       |

## Simple 模式

在 simple 模式下，用户名来源于 Flink。解析顺序为：
1. `HADOOP_USER_NAME` 环境变量
2. 当前登录的操作系统用户

## Basic 模式

在 Basic 模式下，Flink 连接器使用 HTTP Basic 凭证向 Gravitino 服务器进行身份验证，
验证对象为本地用户存储。Gravitino 服务器必须启用 Basic 身份验证。参见
[如何进行身份验证](../security/how-to-authenticate.md#basic-mode) 以了解服务器端配置。

| 属性                                                      | 类型   | 默认值 | 描述                                    | 是否必填            |
|---------------------------------------------------------------|--------|---------------|------------------------------------------------|---------------------|
| table.catalog-store.gravitino.gravitino.client.auth.type      | string | (none)        | 设置为 `basic` 以启用 Basic 身份验证。 | 是，适用于 Basic 模式 |
| table.catalog-store.gravitino.gravitino.client.basic.username | string | (none)        | 本地用户存储中的用户名。                     | 是，适用于 Basic 模式 |
| table.catalog-store.gravitino.gravitino.client.basic.password | string | (none)        | 该用户的密码。                     | 是，适用于 Basic 模式 |

### Basic 配置示例

```yaml
table.catalog-store.kind: gravitino
table.catalog-store.gravitino.gravitino.uri: http://localhost:8090
table.catalog-store.gravitino.gravitino.metalake: my_metalake
table.catalog-store.gravitino.gravitino.client.auth.type: basic
table.catalog-store.gravitino.gravitino.client.basic.username: admin
table.catalog-store.gravitino.gravitino.client.basic.password: YourSecureGravitinoPassword
```

## OAuth2 模式

在 OAuth2 模式下，配置以下设置以获取 OAuth2 令牌来访问 Gravitino 服务器：

| 属性                                                         | 类型   | 默认值 | 描述                                      | 是否必填             |
|------------------------------------------------------------------|--------|---------------|--------------------------------------------------|----------------------|
| table.catalog-store.gravitino.gravitino.client.oauth2.serverUri  | string | (none)        | OAuth2 服务器 URI。                           | 是，适用于 OAuth2 模式 |
| table.catalog-store.gravitino.gravitino.client.oauth2.tokenPath  | string | (none)        | OAuth2 服务器上的令牌端点路径。    | 是，适用于 OAuth2 模式 |
| table.catalog-store.gravitino.gravitino.client.oauth2.credential | string | (none)        | 用于请求 OAuth2 令牌的凭证。 | 是，适用于 OAuth2 模式 |
| table.catalog-store.gravitino.gravitino.client.oauth2.scope      | string | (none)        | 用于请求 OAuth2 令牌的作用域。      | 是，适用于 OAuth2 模式 |

### OAuth2 配置示例

```yaml
table.catalog-store.kind: gravitino
table.catalog-store.gravitino.gravitino.uri: http://localhost:8090
table.catalog-store.gravitino.gravitino.metalake: my_metalake
table.catalog-store.gravitino.gravitino.client.auth.type: oauth2
table.catalog-store.gravitino.gravitino.client.oauth2.serverUri: https://oauth-server.example.com
table.catalog-store.gravitino.gravitino.client.oauth2.tokenPath: /oauth/token
table.catalog-store.gravitino.gravitino.client.oauth2.credential: client-id:client-secret
table.catalog-store.gravitino.gravitino.client.oauth2.scope: your-scope
```

## Kerberos 模式

在 Kerberos 模式下，使用 Flink 安全配置获取用于访问 Gravitino 服务器的 Kerberos 票据。配置 `security.kerberos.login.principal` 和 `security.kerberos.login.keytab` 以指定 Kerberos 主体和 keytab。

Gravitino 服务器主体遵循 `HTTP/$host@$realm` 格式；确保 `$host` 与 Gravitino 服务器 URI 中指定的主机匹配。确保 `krb5.conf` 对 Flink 可用，例如通过 Flink JVM 选项中的 `-Djava.security.krb5.conf=/path/to/krb5.conf` 进行设置。