---
title: "Authentication"
slug: "/security/how-to-authenticate"
keyword: "security authentication oauth kerberos"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino 支持四种身份验证机制：simple、Basic、OAuth 和 Kerberos。
如果您没有为客户端和服务器显式启用身份验证，将使用 `anonymous` 用户访问服务器。

### 简单模式

在简单模式下，客户端使用 `GRAVITINO_USER` 环境变量的值作为用户名。
如果客户端未设置 `GRAVITINO_USER` 环境变量，则客户端默认使用发送请求的机器上登录用户的用户名。

对于客户端，用户可以通过以下代码启用 `simple` 模式：

```java
GravitinoClient client = GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withSimpleAuth()
    .build();
```

此外，用户名可以直接作为参数来创建客户端。

```java
GravitinoClient client = GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withSimpleAuth("test_user_name")
    .build();
```

使用 curl 或其他 HTTP 客户端时，使用 `Authorization` 标头进行身份验证：

```shell
curl -v -X GET \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:' | base64)" \
  http://localhost:8090/api/version
```

### 基础模式

在 Basic 模式下，Gravitino 会根据本地用户元数据验证 HTTP Basic 凭证，这些元数据存储
在关系实体存储中。

要启用基本模式：

- 将 `gravitino.authenticators` 设置为 `basic`。
- 将 `gravitino.server.rest.extensionPackages` 设置为 `org.apache.gravitino.idp.web.rest.feature`。
- 将 `gravitino.authorization.serviceAdmins` 设置为应存在于
本地用户存储中的服务管理员用户名。

本地用户存储与 `simple` 认证器（默认）**不兼容**，
`gravitino.authenticators` 必须包含 `basic` 且不能包含 `simple`。
- 在首次启动时，如果任何已配置的服务管理员尚未拥有密码，请将
`GRAVITINO_INITIAL_ADMIN_PASSWORD` 环境变量设置为初始密码（12 到 64
个字符），然后再启动 Gravitino。相同的密码将应用于每个已配置的服务
管理员，前提是其在本地用户存储中尚不存在。

对于客户端，使用以下代码启用 Basic 模式：

```java
GravitinoClient client = GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withBasicAuth("admin", "YourSecureGravitinoPassword")
    .build();
```

```python
from gravitino.auth.basic_auth_provider import BasicAuthProvider
from gravitino.client.gravitino_client import GravitinoClient

client = GravitinoClient(
    uri="http://localhost:8090",
    metalake_name="metalake",
    auth_data_provider=BasicAuthProvider("admin", "YourSecureGravitinoPassword"),
)
```

```shell
curl -v -X GET \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:YourSecureGravitinoPassword' | base64)" \
  http://localhost:8090/api/version
```

Web UI 使用 `/configs` 中 `gravitino.authenticators` 的第一个条目。当其为 `basic` 时，
登录页面会显示由本地用户元数据支持的用户名和密码表单。请参阅
[本地用户和组](local-users-and-groups.md)。

### OAuth 模式

Gravitino 支持外部 OAuth 2.0 服务器，并提供两种令牌验证方法：

1. **静态签名密钥验证** - 使用预配置的签名密钥来验证JWT令牌
2. **基于JWKS的验证** - 从OAuth提供程序的JWKS端点动态获取公钥（支持像Azure AD这样的OIDC提供程序，以及其他兼容JWKS的提供程序）

要启用 OAuth 模式：

- 首先，确保外部 OAuth 2.0 服务器支持 Bearer JWT 令牌。
- 对于**静态密钥验证**：配置 `gravitino.authenticator.oauth.defaultSignKey`、`gravitino.authenticator.oauth.serverUri` 和 `gravitino.authenticator.oauth.tokenPath`。
- 对于 **JWKS 验证**：配置 `gravitino.authenticator.oauth.jwksUri` 和 `gravitino.authenticator.oauth.tokenValidatorClass=org.apache.gravitino.server.authentication.JwksTokenValidator`。根据是否需要 Web UI OIDC 登录流程，你可以使用 `gravitino.authenticator.oauth.provider=default` 或 `gravitino.authenticator.oauth.provider=oidc`。
- 对于 **Web UI OIDC 身份验证**：设置 `gravitino.authenticator.oauth.provider=oidc` 并配置 `gravitino.authenticator.oauth.clientId`、`gravitino.authenticator.oauth.authority` 和 `gravitino.authenticator.oauth.scope`。这些设置通过 `/configs` 端点暴露给 Web UI，以启用 OAuth 登录流程。使用回调重定向 URI 配置你的 OAuth 提供商：`https://your-gravitino-server/ui/oauth/callback`。

  :::note
Web UI 的 OIDC 登录使用带 PKCE 的授权码流程，这依赖于浏览器
[Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)。浏览器仅
在[安全上下文](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)中暴露此 API，
也就是说，当 Web UI 通过 HTTPS 或从 `localhost` 提供服务时。如果您通过纯
HTTP 在非 `localhost` 主机上打开 Web UI，登录将失败，因为 PKCE 所需的加密原语
不可用。请通过 HTTPS 提供 Web UI（或通过 `localhost` 访问它）以使 OIDC 登录正常工作。
  :::
- 接下来，对于客户端，用户可以通过以下代码启用 `OAuth` 模式：

```java
DefaultOAuth2TokenProvider authDataProvider = DefaultOAuth2TokenProvider.builder()
    .withUri("oauth server uri")
    .withCredential("yy:xx")
    .withPath("oauth/token")
    .withScope("test")
    .build();

GravitinoClient client = GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withOAuth(authDataProvider)
    .build();
```

### Kerberos 模式

要启用 Kerberos 模式，用户必须确保服务器和客户端具有正确的 Kerberos 配置。在服务器端，用户应将 `gravitino.authenticators` 设置为 `kerberos`，并为
`gravitino.authenticator.kerberos.principal` 和 `gravitino.authenticator.kerberos.keytab` 提供合适的值。在客户端，用户可以通过以下代码启用 `kerberos` 模式：

```java
// Use keytab to create KerberosTokenProvider
KerberosTokenProvider provider = KerberosTokenProvider.builder()
        .withClientPrincipal(clientPrincipal)
        .withKeyTabFile(new File(keytabFile))
        .build();

// Use ticketCache to create KerberosTokenProvider
KerberosTokenProvider provider = KerberosTokenProvider.builder()
        .withClientPrincipal(clientPrincipal)
        .build();        

GravitinoClient client = GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withKerberosAuth(provider)
    .build();
```

:::info
Iceberg REST 服务不支持 Kerberos 认证。
URI 必须是服务器的主机名，而不是其 IP 地址。
:::

### 自定义模式

Gravitino 也支持自定义认证实现。
对于服务端，你可以实现 `Authenticator` 接口并指定 `gravitino.authenciators`。
对于客户端，你可以扩展抽象类 `CustomTokenProvider` 并指定 token provider。

```java
GravitinoClient client = GravitinoClient.builder(uri)
    .withMetalake("metalake")
    .withCustomProvider(provider)
    .build();
```

### 主体映射

Gravitino 支持主体映射，将已认证的主体（来自 OAuth 或 Kerberos）转换为用于授权的用户身份。默认情况下，Gravitino 使用基于正则表达式的映射。

### 组映射

Gravitino 支持组映射，将已认证的组（来自 OAuth）转换为 Gravitino 组以进行授权。默认情况下，Gravitino 使用基于正则表达式的映射。

#### OAuth 用户组映射

对于 OAuth 认证，组从 JWT claims 中提取（通过 `gravitino.authenticator.oauth.groupsFields` 配置）。自定义这些组的映射方式：

```text
# Use default regex mapper that extracts everything (passes through unchanged)
gravitino.authenticator.oauth.groupMapper = regex
gravitino.authenticator.oauth.groupMapper.regex.pattern = ^(.*)$

# Extract group from a complex string (e.g., /group -> group)
gravitino.authenticator.oauth.groupMapper = regex
gravitino.authenticator.oauth.groupMapper.regex.pattern = ^/(.*)


# Use custom group mapper implementation
gravitino.authenticator.oauth.groupMapper = com.example.MyCustomGroupMapper
```

#### 自定义组映射器

对于高级用例，实现 `GroupMapper` 接口：

```java
package com.example;

import org.apache.gravitino.UserGroup;
import org.apache.gravitino.auth.GroupMapper;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class MyCustomGroupMapper implements GroupMapper {
  @Override
  public List<UserGroup> map(List<Object> groups) {
    if (groups == null) {
      return Collections.emptyList();
    }
    return groups.stream()
        .map(g -> new UserGroup(Optional.empty(), "mapped_" + g.toString()))
        .collect(Collectors.toList());
  }
}
```

配置 Gravitino 使用您的自定义 mapper：

```text
gravitino.authenticator.oauth.groupMapper = com.example.MyCustomGroupMapper
```

#### OAuth 主体映射

对于 OAuth 认证，主体从 JWT 声明中提取（通过 `gravitino.authenticator.oauth.principalFields` 配置）。自定义这些主体的映射方式：

```text
# Use default regex mapper that extracts everything (passes through unchanged)
gravitino.authenticator.oauth.principalMapper = regex
gravitino.authenticator.oauth.principalMapper.regex.pattern = ^(.*)$

# Extract username from email (e.g., user@example.com -> user)
gravitino.authenticator.oauth.principalMapper = regex
gravitino.authenticator.oauth.principalMapper.regex.pattern = ([^@]+)@.*

# Use custom mapper implementation
gravitino.authenticator.oauth.principalMapper = com.example.MyCustomPrincipalMapper
```

#### 自定义 Principal Mapper

对于高级用例，实现 `PrincipalMapper` 接口：

```java
package com.example;

import org.apache.gravitino.auth.PrincipalMapper;
import java.security.Principal;

public class MyCustomPrincipalMapper implements PrincipalMapper {
  @Override
  public Principal map(String principal) {
    return () -> "mapped_" + principal;
  }
}
```

配置 Gravitino 使用您的自定义 mapper：

```text
gravitino.authenticator.oauth.principalMapper = com.example.MyCustomPrincipalMapper
```

#### Kerberos 主体映射

对于 Kerberos 认证，主体遵循 `primary[/instance][@REALM]` 格式。默认映射器提取 primary 组件（`@` 之前的用户名）：

```text
# Default: Extract primary component (user@REALM -> user, HTTP/server@REALM -> HTTP)
gravitino.authenticator.kerberos.principalMapper = regex
gravitino.authenticator.kerberos.principalMapper.regex.pattern = ([^@]+).*

# Extract only the first part before '/' (HTTP/server@REALM -> HTTP)
gravitino.authenticator.kerberos.principalMapper = regex
gravitino.authenticator.kerberos.principalMapper.regex.pattern = ([^/@]+).*
```

#### 自定义 Kerberos Principal 映射器

对于高级用例，实现 `PrincipalMapper` 接口：

```java
package com.example;

import org.apache.gravitino.auth.KerberosPrincipal;
import org.apache.gravitino.auth.KerberosPrincipalMapper;
import org.apache.gravitino.auth.PrincipalMapper;

import java.security.Principal;

public class RealmBasedMapper implements PrincipalMapper {
  private final KerberosPrincipalMapper parser = new KerberosPrincipalMapper();

  @Override
  public Principal map(String principal) {
    // Parse Kerberos principal components
    KerberosPrincipal krbPrincipal = (KerberosPrincipal) parser.map(principal);
    
    // Route based on realm
    if ("DEV.EXAMPLE.COM".equals(krbPrincipal.getRealm().orElse(null))) {
      return () -> "dev_" + krbPrincipal.getName();
    } else if ("PROD.EXAMPLE.COM".equals(krbPrincipal.getRealm().orElse(null))) {
      return () -> "prod_" + krbPrincipal.getName();
    }
    
    // Default: use primary with instance (e.g., "HTTP/server")
    return () -> krbPrincipal.getPrimaryWithInstance();
  }
}
```

配置 Gravitino 使用您的自定义 mapper：

```text
gravitino.authenticator.kerberos.principalMapper = com.example.RealmBasedMapper
```

### 服务器配置

Gravitino server 和 Gravitino Iceberg REST server 共享相同的配置项，您无需为 Gravitino Iceberg REST server 添加 `gravitino.iceberg-rest` 前缀。

| 配置项                                               | 描述                                                                                                                                                                                                                                                             | 默认值                                                       | 是否必填                                                                                        |
|------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `gravitino.authenticator`                                        | 已废弃。请改用 `gravitino.authenticators`。                                                                                                                                                                                                        | `simple`                                                            | 否                                                                                              |
| `gravitino.authenticators`                                       | Gravitino 使用的认证器，设置为 `simple`、`basic`、`oauth` 或 `kerberos`。多个认证器以逗号分隔。如果一个请求同时被多个认证器支持，默认将使用第一个认证器。    | `simple`                                                            | 否                                                                                              |
| `gravitino.authenticator.oauth.serviceAudience`                  | 当 Gravitino 使用 OAuth 作为认证器时的受众名称。                                                                                                                                                                                                       | `GravitinoServer`                                                   | 否                                                                                              |
| `gravitino.authenticator.oauth.allowSkewSecs`                    | 当 Gravitino 使用 OAuth 作为认证器时，JWT 允许的偏移秒数。                                                                                                                                                                                             | `0`                                                                 | 否                                                                                              |
| `gravitino.authenticator.oauth.defaultSignKey`                   | 当 Gravitino 使用 OAuth 作为认证器时，JWT 的签名密钥。                                                                                                                                                                                                  | (无)                                                              | 如果使用 `oauth` 作为认证器则为是                                                         |
| `gravitino.authenticator.oauth.signAlgorithmType`                | 当 Gravitino 使用 OAuth 作为认证器时的签名算法。                                                                                                                                                                                                 | `RS256`                                                             | 否                                                                                              |
| `gravitino.authenticator.oauth.serverUri`                        | 默认 OAuth 服务器的 URI。使用 StaticSignKeyValidator 时必需，基于 JWKS 的验证器不需要。                                                                                                                                                | (无)                                                              | 如果使用 `StaticSignKeyValidator` 则为是                                                           |
| `gravitino.authenticator.oauth.tokenPath`                        | 默认 OAuth 服务器的 token 路径。使用 StaticSignKeyValidator 时必需，基于 JWKS 的验证器不需要。                                                                                                                                     | (无)                                                              | 如果使用 `StaticSignKeyValidator` 则为是                                                           |
| `gravitino.authenticator.oauth.provider`                         | OAuth 提供者类型（default、oidc）。决定 Web UI 认证流程。Web UI OIDC 登录使用 'oidc'，旧版登录或仅 API 认证使用 'default'。                                                                                                | `default`                                                           | 否                                                                                              |
| `gravitino.authenticator.oauth.clientId`                         | 用于 Web UI 认证的 OAuth 客户端 ID。                                                                                                                                                                                                                              | (无)                                                              | 如果 provider 为 `oidc` 则为是                                                                       |
| `gravitino.authenticator.oauth.authority`                        | 用于 Web UI 认证的 OIDC 提供者的 OAuth authority/issuer URL。（例如，Azure AD 租户 URL）。                                                                                                                                                                   | (无)                                                              | 如果 provider 为 `oidc` 则为是                                                                       |
| `gravitino.authenticator.oauth.scope`                            | 用于 Web UI 认证的 OAuth 作用域（空格分隔）。                                                                                                                                                                                                               | (无)                                                              | 如果 provider 为 `oidc` 则为是                                                                       |
| `gravitino.authenticator.oauth.jwksUri`                          | 用于服务端 OAuth 令牌验证的 JWKS URI。使用基于 JWKS 的验证时必填。                                                                                                                                                                             | (无)                                                              | 如果 `tokenValidatorClass` 为 `org.apache.gravitino.server.authentication.JwksTokenValidator` 则为是 |
| `gravitino.authenticator.oauth.principalFields`                  | 用作 principal 身份的 JWT claim 字段。逗号分隔的列表，用于按顺序回退（例如，'preferred_username,email,sub'）。                                                                                                                                                                                                     | `sub`                                                               | 否                                                                                              |
| `gravitino.authenticator.oauth.groupsFields`                     | 用作组成员身份的 JWT claim 字段。逗号分隔的列表，用于按顺序回退（例如，'groups,roles'）。                                                                                                                                                       | `groups`                                                            | 否                                                                                              |
| `gravitino.authenticator.oauth.tokenValidatorClass`              | OAuth 令牌验证器实现的完全限定类名。使用 `org.apache.gravitino.server.authentication.JwksTokenValidator` 进行基于 JWKS 的验证，或使用 `org.apache.gravitino.server.authentication.StaticSignKeyValidator` 进行静态密钥验证。 | `org.apache.gravitino.server.authentication.StaticSignKeyValidator` | 否                                                                                              |
| `gravitino.authenticator.oauth.principalMapper`                  | OAuth 的 Principal mapper 类型。使用 'regex' 进行基于正则表达式的映射，或提供实现 `org.apache.gravitino.auth.PrincipalMapper` 的完全限定类名。                                                                                                 | `regex`                                                             | 否                                                                                              |
| `gravitino.authenticator.oauth.principalMapper.regex.pattern`    | 用于 OAuth principal 映射的正则表达式模式。第一个捕获组成为映射后的 principal。仅在 principalMapper 为 'regex' 时使用。                                                                                                                                 | `^(.*)$`                                                            | 否                                                                                              |
| `gravitino.authenticator.oauth.groupMapper`                      | OAuth 的 Group mapper 类型。使用 'regex' 进行基于正则表达式的映射，或提供实现 `org.apache.gravitino.auth.GroupMapper` 的完全限定类名。                                                                                                         | `regex`                                                             | 否                                                                                              |
| `gravitino.authenticator.oauth.groupMapper.regex.pattern`        | 用于 OAuth group 映射的正则表达式模式。第一个捕获组成为映射后的 group。仅在 groupMapper 为 'regex' 时使用。                                                                                                                                             | `^(.*)$`                                                            | 否                                                                                              |
| `gravitino.authenticator.kerberos.principal`                     | 指示用于 HTTP 端点的 Kerberos principal。Principal 应以 `HTTP/` 开头。                                                                                                                                                                     | (无)                                                              | 如果使用 `kerberos` 作为认证器则为是                                                      |
| `gravitino.authenticator.kerberos.keytab`                        | 包含 principal 凭据的 keytab 文件的位置。                                                                                                                                                                                                     | (无)                                                              | 如果使用 `kerberos` 作为认证器则为是                                                      |
| `gravitino.authenticator.kerberos.principalMapper`               | Kerberos 的 Principal 映射器类型。使用 'regex' 进行基于正则表达式的映射，或者提供一个实现了 `org.apache.gravitino.auth.PrincipalMapper` 的全限定类名。                                                                                              | `regex`                                                             | 否                                                                                              |
| `gravitino.authenticator.kerberos.principalMapper.regex.pattern` | Kerberos Principal 映射的正则表达式模式。第一个捕获组将成为映射后的 Principal。仅在 principalMapper 为 'regex' 时使用。                                                                                                                              | `([^@]+).*`                                                         | 否                                                                                              |

Gravitino 支持的签名算法如下：

| 名称  | 描述                                    |
|-------|------------------------------------------------|
| HS256 | 使用 SHA-25A 的 HMAC                             |
| HS384 | 使用 SHA-384 的 HMAC                             |
| HS512 | 使用 SHA-51 的 HMAC                              |
| RS256 | 使用 SHA-256 的 RSASSA-PKCS-v1_5                 |
| RS384 | 使用 SHA-384 的 RSASSA-PKCS-v1_5                 |
| RS512 | 使用 SHA-512 的 RSASSA-PKCS-v1_5                 |
| ES256 | 使用 P-256 和 SHA-256 的 ECDSA                  |
| ES384 | 使用 P-384 和 SHA-384 的 ECDSA                  |
| ES512 | 使用 P-521 和 SHA-512 的 ECDSA                  |
| PS256 | 使用 SHA-256 和 MGF1（基于 SHA-256）的 RSASSA-PSS |
| PS384 | 使用 SHA-384 和 MGF1（基于 SHA-384）的 RSASSA-PSS |
| PS512 | 使用 SHA-512 和 MGF1（基于 SHA-512）的 RSASSA-PSS |

### 示例：基本认证

此示例展示如何启用内置的 Basic 认证。

**前提条件：**

- Gravitino 分发包（包含服务器 classpath 上的 idp-basic 插件）

本地用户存储与 `simple` 认证器（默认）**不兼容**，
`gravitino.authenticators` 必须包含 `basic` 且不能包含 `simple`。

**配置：**

将以下内容追加到 `conf/gravitino.conf`：

```text
gravitino.authenticators = basic
gravitino.server.rest.extensionPackages = org.apache.gravitino.idp.web.rest.feature
gravitino.authorization.serviceAdmins = admin
```

首次启动时，如果 `admin` 服务管理员在存储中还没有密码，
在启动服务器之前设置初始密码：

```bash
export GRAVITINO_INITIAL_ADMIN_PASSWORD='YourSecureGravitinoPassword'
./bin/start-gravitino.sh
```

**用法：**

```shell
curl -v -X GET \
  -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'admin:YourSecureGravitinoPassword' | base64)" \
  http://localhost:8090/api/version
```

If the service admin already has a password, you do not need to set
`GRAVITINO_INITIAL_ADMIN_PASSWORD` on restart. Gravitino does not change existing passwords
when the server starts again.

### 示例：Azure AD 作为带有 JWKS 验证的 OIDC 提供商

本示例展示了如何使用 Azure AD 配置 Gravitino，并使用基于 JWKS 的令牌验证。

**前提条件：**
- 带有应用注册（单页应用）的 Azure AD 租户
- 应用配置包含：
- 客户端 ID（应用 ID）
- 平台配置：单页应用（SPA）
- 重定向 URI：`https://your-gravitino-server/ui/oauth/callback`
- 所需的 API 权限/范围（通常为 `openid`、`profile`、`email`）

**配置：**

```text
# Enable OAuth authentication
gravitino.authenticators = oauth

# OIDC Provider Configuration for Web UI
gravitino.authenticator.oauth.provider = oidc
gravitino.authenticator.oauth.clientId = <your-azure-app-client-id>
gravitino.authenticator.oauth.authority = https://login.microsoftonline.com/<your-tenant-id>/v2.0
gravitino.authenticator.oauth.scope = openid profile email

# JWKS-based Token Validation
gravitino.authenticator.oauth.jwksUri = https://login.microsoftonline.com/<your-tenant-id>/discovery/v2.0/keys
gravitino.authenticator.oauth.tokenValidatorClass = org.apache.gravitino.server.authentication.JwksTokenValidator
gravitino.authenticator.oauth.serviceAudience = <your-azure-app-client-id-or-api-identifier>
gravitino.authenticator.oauth.principalFields = preferred_username,email,sub
```

**用法：**
- **Web UI**：导航至 Gravitino Web UI，它将重定向到 Azure AD 进行身份验证
- **API 访问**：在 `Authorization: Bearer <token>` 标头中使用 Azure AD 令牌

**Azure AD v2.0 端点（推荐）：**
`authority` 必须使用 v2.0 端点（`/v2.0` 后缀）以匹配 v2.0 JWKS URI。这确保了在 OIDC 发现期间颁发的令牌使用与您的 JWKS 配置相匹配的正确令牌格式和颁发者声明。

**替代方案：Azure AD v1.0 端点：**
对于需要 v1.0 令牌的旧版应用程序或组织策略，请使用：
```text
gravitino.authenticator.oauth.authority = https://sts.windows.net/<your-tenant-id>/
gravitino.authenticator.oauth.jwksUri = https://login.microsoftonline.com/<your-tenant-id>/discovery/v2.0/keys
```
Azure AD 对 v1.0 和 v2.0 使用相同的签名密钥，因此 v2.0 JWKS 可以验证 v1.0 令牌。

**重要：** 当使用 v2.0 JWKS 时，请勿使用 `https://login.microsoftonline.com/<tenant-id>/`（不带 `/v2.0`）作为颁发机构。这会导致颁发者不匹配：令牌将包含 `iss: "https://sts.windows.net/..."`，但服务器期望的是 `iss: "https://login.microsoftonline.com/..."`。

**服务受众：**
`serviceAudience` 应与 Azure AD 令牌中的 `aud` 声明相匹配。这通常是你的 Azure AD 应用程序的客户端 ID，但如果你配置了自定义 API 作用域（例如，`api://<client-id>`），则它可能是自定义 API 标识符。

**主体字段：**
`principalFields` 支持多个回退选项。Gravitino 将按顺序尝试每个字段（例如，先是 `preferred_username`，然后是 `email`，最后是 `sub`），直到找到一个非空值来用作用户身份。

使用 JWKS 验证时，您无需配置 `defaultSignKey`、`serverUri` 或 `tokenPath`，因为验证器会从 Azure AD 的 JWKS 端点动态获取公钥。
:::

### 示例：静态密钥 OAuth 提供程序

为了兼容不支持 JWKS 的现有 OAuth 服务器：

```text
gravitino.authenticators = oauth
gravitino.authenticator.oauth.provider = default
gravitino.authenticator.oauth.clientId = test
gravitino.authenticator.oauth.scope = test
gravitino.authenticator.oauth.serviceAudience = test
gravitino.authenticator.oauth.tokenValidatorClass = org.apache.gravitino.server.authentication.StaticSignKeyValidator
gravitino.authenticator.oauth.serverUri = http://your-oauth-server
gravitino.authenticator.oauth.tokenPath = /oauth2/token
gravitino.authenticator.oauth.defaultSignKey = <your-static-signing-key>
```

### 示例：使用默认提供程序进行 JWKS 验证

对于无 Web UI OIDC 工作流的基于 JWKS 的令牌验证：

```text
gravitino.authenticators = oauth
gravitino.authenticator.oauth.provider = default
gravitino.authenticator.oauth.serviceAudience = <your-audience>
gravitino.authenticator.oauth.tokenValidatorClass = org.apache.gravitino.server.authentication.JwksTokenValidator
gravitino.authenticator.oauth.jwksUri = https://your-oauth-provider/.well-known/jwks.json
```

### 示例

按照以下步骤设置 OAuth 模式的 Gravitino 服务器：

1. 前置条件

你需要安装 JDK8 和 Docker。

2. 设置一个外部 OAuth 2.0 服务器

有一个基于 [spring-authorization-server](https://github.com/spring-projects/spring-authorization-server/tree/1.0.3) 的 sample-authorization-server。镜像在外部 OAuth 2.0 服务器中注册了客户端信息
其 clientId 为 `test`，secret 为 `test`，scope 为 `test`。

```shell
 docker run -p 8177:8177 --name sample-auth-server -d datastrato/sample-authorization-server:0.3.0
```

3. 在浏览器中打开[授权服务器的 JWK URL](http://localhost:8177/oauth2/jwks)，即可获取 JWK。

![jks_response_image](../assets/jks.png)

4. 将 JWK 转换为 PEM。你可以使用[在线工具](https://8gwifi.org/jwkconvertfunctions.jsp#google_vignette)或其他工具。

![pem_convert_result_image](../assets/pem.png)

5. 复制公钥并删除字符 `\n`，即可获得 Gravitino 服务器的默认签名密钥。

6. 参考[配置](../gravitino-server-config.md)并将配置追加到 conf/gravitino.conf。

```text
gravitino.authenticators = oauth
gravitino.authenticator.oauth.serviceAudience = test
gravitino.authenticator.oauth.defaultSignKey = <the default signing key>
gravitino.authenticator.oauth.tokenPath = /oauth2/token
gravitino.authenticator.oauth.serverUri = http://localhost:8177
```

7. 打开 [Gravitino 服务器的 URL](http://localhost:8090)，并使用 clientId `test`、clientSecret `test` 和 scope `test` 登录。

![oauth_login_image](../assets/oauth.png)

8. 使用 curl 命令访问 Gravitino。

获取访问令牌

```shell
curl --location --request POST 'http://127.0.0.1:8177/oauth2/token?grant_type=client_credentials&client_id=test&client_secret=test&scope=test'
```

使用访问令牌请求 Gravitino

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" http://localhost:8090/api/version
```

### 将 Keycloak 配置为 OAuth 提供者

1. 搭建一个外部 Keycloak 服务器，您可以参考 [Keycloak 文档](https://www.keycloak.org/getting-started/getting-started-docker)

```shell
docker run -dti -p 8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.2.5 start-dev
```

2. 前往 [Keycloak 管理控制台](http://localhost:8080/)，使用初始管理员用户登录，用户名为 `admin`，密码为 `admin`

3. 为 Gravitino 创建一个 realm
* 在左侧菜单中点击 *Manage realms*。
* 点击 *Create realm* 按钮

![create-realm.png](../assets/security/create-realm.png)

4. 获取 `gravitinorealm` 公钥，即 gravitino.conf 中的 `<the default signing key>`
在浏览器中访问 `http://localhost:8080/realms/gravitinorealm`

![realm-public-key.png](../assets/security/realm-public-key.png)

5. 添加用户

最初，realm 中没有用户。请按照以下步骤创建用户：
* 确认您仍处于 gravitinorealm realm 中，它紧邻 *Current realm*。
* 点击左侧菜单中的 Users。
* 点击 *Create new user*。
* 使用以下值填写表单：  
*Username*: usera, *First name*: 任意名, *Last name*: 任意姓, *Email*: 任意邮箱
* 点击 *credentials*，在 *Set password form* 中填入密码。
* 将 Temporary 切换为 Off，以便用户在首次登录时无需更新此密码。

您现在可以登录[账户控制台(gravitinorealm)](http://localhost:8080/realms/gravitinorealm/account)以验证此用户是否已正确配置。

6. 在 Keycloak 中注册 Gravitino

* 点击 *Current realm* 旁边的 *gravitinorealm*。
*  点击 *Clients*。
*  点击 *Create client*
*  填写 *Client type*：`OpenID Connect`，*Client ID*：`gravitino-client`
*  点击 *Next*
*  确认已启用 `Client authentication`、`Standard flow`、`Direct access grants` 和 `Service accounts roles`。
*  点击 *Next*
*  将 *Valid redirect URIs* 设置为 `http://localhost:8090/*`
*  将 *Web origins* 设置为 `http://localhost:8090`
*  点击 *Save*。
*  点击 *Credentials* 选项卡页面，获取 `Client Secret`。

![create-client.png](../assets/security/create-client.png)

7. 参考[配置](../gravitino-server-config.md)并将配置追加到 conf/gravitino.conf。

```text
gravitino.authenticators = oauth
gravitino.authenticator.oauth.serviceAudience = account
gravitino.authenticator.oauth.defaultSignKey = <the default signing key>
gravitino.authenticator.oauth.tokenPath = /realms/gravitinorealm/protocol/openid-connect/token
gravitino.authenticator.oauth.serverUri = http://localhost:8080
```

8. 使用客户端凭据进行身份验证。`access token` 绑定到服务账号。

获取访问令牌

```shell
curl \
  -d "client_id=gravitino-client" \
  -d "client_secret=FL20ezBgQAOlDQeNifzwliQ56wohhqNo" \
  -d "grant_type=client_credentials" \
  "http://localhost:8080/realms/gravitinorealm/protocol/openid-connect/token"
```

使用访问令牌请求 Gravitino

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" http://localhost:8090/api/version
```

9. 使用密码对用户进行身份验证。openid scope 返回一个包含用户信息的 `id_token`，该信息可用于未来文章中的消费者映射和组映射。

获取访问令牌

```shell
curl \
  -d "client_id=gravitino-client" \
  -d "client_secret=FL20ezBgQAOlDQeNifzwliQ56wohhqNo" \
  -d "username=usera" \
  -d "password=Admin@123" \
  -d "grant_type=password" \
  -d "scope=openid" \
  "http://localhost:8080/realms/gravitinorealm/protocol/openid-connect/token"
```

使用访问令牌向 Gravitino 服务器发起请求：

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" http://localhost:8090/api/version
```

对于 Gravitino Iceberg REST 服务，不需要 'Accept: application/vnd.gravitino.v1+json' 请求头，你可以使用以下命令：

```shell
curl -v -X GET -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" http://127.0.0.1:9001/iceberg/v1/config
```

### 使用 Keycloak 启用 Web UI OIDC 登录

上面注册的 `gravitino-client` 是一个用于机器到机器流程的机密客户端
（客户端凭证和密码授权）。浏览器 Web UI 无法使用机密客户端，因为
它无法保存客户端密钥，因此 Web UI OIDC 登录需要一个单独的公共客户端。一个典型的
Keycloak 部署因此会使用两个客户端：

| 客户端             | 类型         | 使用方                                                       | Keycloak 设置                                                                   |
|--------------------|--------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `gravitino-client` | 机密 | 引擎和机器流程（CLI、连接器、服务账户） | *客户端身份验证*开启，*标准流程*和*服务账户角色*已启用    |
| `gravitino-ui`     | 公开       | 浏览器 Web UI OIDC 登录                                     | *客户端身份验证*关闭，*标准流程*已启用                                |

为 Web UI 注册公共客户端：

* 在 `gravitinorealm` 域中点击 *客户端*，然后 *创建客户端*。
* 填写 *客户端类型*：`OpenID Connect`，*客户端 ID*：`gravitino-ui`，然后点击 *下一步*。
* 将 *客户端认证* **关闭**（这会使其成为公共客户端）并启用 *标准流程*。点击 *下一步*。
* 将 *有效的重定向 URI* 设置为 `https://your-gravitino-server/ui/oauth/callback`。
* 将 *有效的注销后重定向 URI* 设置为 `https://your-gravitino-server/*`，以便注销后可以重定向回 Web UI。
* 将 *Web 来源* 设置为 `https://your-gravitino-server`。
* 点击 *保存*。

然后在 `conf/gravitino.conf` 中将 Web UI OIDC 设置指向此公共客户端：

```text
gravitino.authenticators = oauth
gravitino.authenticator.oauth.provider = oidc
gravitino.authenticator.oauth.clientId = gravitino-ui
gravitino.authenticator.oauth.authority = http://localhost:8080/realms/gravitinorealm
gravitino.authenticator.oauth.scope = openid profile email
gravitino.authenticator.oauth.jwksUri = http://localhost:8080/realms/gravitinorealm/protocol/openid-connect/certs
gravitino.authenticator.oauth.tokenValidatorClass = org.apache.gravitino.server.authentication.JwksTokenValidator
gravitino.authenticator.oauth.serviceAudience = account
gravitino.authenticator.oauth.principalFields = preferred_username,email,sub
```

本示例使用基于 JWKS 的验证，服务器从
`jwksUri` 自动获取 Keycloak 的公钥。因此，它不需要静态密钥设置
（`gravitino.authenticator.oauth.defaultSignKey`、`gravitino.authenticator.oauth.serverUri` 和
`gravitino.authenticator.oauth.tokenPath`），如上面的机器流程示例所示。JWKS 验证
是 Keycloak 推荐的做法；只有当您有意使用
`tokenValidatorClass=org.apache.gravitino.server.authentication.StaticSignKeyValidator` 作为替代时，才设置静态密钥。这
相同的服务器配置可以验证来自 Web UI 和机器客户端的令牌，因此您无需
为每个客户端单独设置验证器。

:::note
Web UI OIDC 登录需要一个[安全上下文](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)：
通过 HTTPS 提供 Web UI 或通过 `localhost` 访问它。请参阅
[OAuth Mode](#oauth-mode) 部分中的 secure-context 注释以了解详情。
:::

#### 统一拆分主机名部署的令牌颁发者

Keycloak 令牌中的 `iss`（issuer）声明是根据获取令牌的主机名构建
的。当浏览器和 Gravitino 服务器通过不同的主机名访问 Keycloak 时（例如，
浏览器使用公共 URL，而服务器使用内部 Docker 或集群主机名），
浏览器签发的令牌中的 `iss` 声明将与服务器期望的 `authority` 不匹配，并且
验证将失败并出现诸如 `JWT iss claim value rejected` 的错误。

为了保持 issuer 一致，无论使用哪个主机名访问 Keycloak，请设置一个统一的
领域上的 **前端 URL**：

* 打开 `gravitinorealm` 域，转到 *域设置* > *常规*。
* 将 *前端 URL* 设置为规范的、可从外部访问的 Keycloak 基础 URL（例如，
`https://keycloak.example.com`）。
* 保存，然后在 `gravitino.authenticator.oauth.authority`（以及匹配的
`jwksUri`）中使用相同的基础 URL。

设置了 Frontend URL 后，Keycloak 会在每个令牌上标记相同的 `iss` 声明，无论
请求到达的主机名是什么，因此浏览器签发和服务器验证的令牌保持一致。
