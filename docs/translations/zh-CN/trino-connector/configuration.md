---
title: "Trino Connector Configuration"
slug: "/trino-connector/configuration"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

| 属性                                    | 类型    | 默认值         | 描述                                                                                                                                                                                                                                                                                                                                      | 必填 |
|---------------------------------------------|---------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| connector.name                              | string  | (none)                | `connector.name` 定义了 Trino 连接器的类型，该值始终为 'gravitino'。                                                                                                                                                                                                                                                      | Yes      |
| gravitino.metalake                          | string  | (none)                | `gravitino.metalake` 定义了 Trino 连接器使用 Gravitino 服务器中的哪个 metalake。Trino 连接器应在启动时设置它，`gravitino.metalake` 的值需要是一个有效的名称，Trino 连接器可以检测并加载已创建的包含目录、模式和表的 metalake，并保持同步。                              | Yes      |
| gravitino.uri                               | string  | http://localhost:8090 | `gravitino.uri` 定义了 Gravitino 服务器的连接 URL，默认值为 `http://localhost:8090`。Trino 连接器可以在 Gravitino 服务器准备就绪后检测并连接到它，无需事先启动 Gravitino 服务器。                                                                                                 | No       |
| trino.jdbc.user                             | string  | admin                 | 当前 Trino 的 jdbc 用户名。                                                                                                                                                                                                                                                                                                             | NO       |
| trino.jdbc.password                         | string  | (none)                | 当前 Trino 的 jdbc 密码。                                                                                                                                                                                                                                                                                                              | NO       |
| trino.jdbc.ssl.enabled                      | boolean | (derived)             | 到 Trino coordinator 的内部 JDBC 连接是否使用 TLS。如果未设置，则从 Trino `discovery.uri` 的协议推导得出，因此 `discovery.uri` 为 `https://...` 的 coordinator 不需要显式设置。                                                                                                               | No       |
| trino.jdbc.ssl.truststore.path              | string  | (none)                | 包含 Trino coordinator 证书的 truststore 路径。如果省略，则使用默认的 JVM truststore。需要 TLS，TLS 在 `discovery.uri` 为 HTTPS 时自动启用，或通过 `trino.jdbc.ssl.enabled=true` 显式启用，并且 `trino.jdbc.ssl.verification` 不为 `NONE`。                                             | No       |
| trino.jdbc.ssl.truststore.password          | string  | (none)                | 由 `trino.jdbc.ssl.truststore.path` 配置的 truststore 密码。需要 TLS 和 `trino.jdbc.ssl.truststore.path`，否则连接器将无法启动。                                                                                                                                                                            | No       |
| trino.jdbc.ssl.truststore.type              | string  | (none)                | truststore 的类型，例如 `JKS` 或 `PKCS12`。如果省略，则使用默认的 JVM truststore 类型。需要 TLS 和 `trino.jdbc.ssl.truststore.path`，否则连接器将无法启动。                                                                                                                                           | No       |
| trino.jdbc.ssl.keystore.path                | string  | (none)                | 包含提供给 coordinator 的客户端证书的 keystore 路径，适用于需要双向 TLS 的 coordinator。需要 TLS，TLS 在 `discovery.uri` 为 HTTPS 时自动启用，或通过 `trino.jdbc.ssl.enabled=true` 显式启用，并且 `trino.jdbc.ssl.verification` 不为 `NONE`。请参阅下面关于双向 TLS 的说明。 | No       |
| trino.jdbc.ssl.keystore.password            | string  | (none)                | 由 `trino.jdbc.ssl.keystore.path` 配置的 keystore 密码。需要 TLS 和 `trino.jdbc.ssl.keystore.path`，否则连接器将无法启动。                                                                                                                                                                                  | No       |
| trino.jdbc.ssl.keystore.type                | string  | (none)                | keystore 的类型，例如 `JKS` 或 `PKCS12`。如果省略，则使用默认的 JVM keystore 类型。需要 TLS 和 `trino.jdbc.ssl.keystore.path`，否则连接器将无法启动。                                                                                                                                                 | No       |
| trino.jdbc.ssl.verification                 | string  | FULL                  | 内部 JDBC 连接的证书验证模式：`FULL`、`CA` 或 `NONE`。任何非 `FULL` 的值都需要 TLS，这可以从 HTTPS `discovery.uri` 推导得出。`NONE` 完全禁用证书验证，应仅用于故障排除。                                                              | No       |
| trino.jdbc.roles                            | string  | (none)                | 应用于内部 JDBC 连接的会话角色，例如 `system:sysadmin`。仅允许使用特权角色执行 `CREATE CATALOG` 的部署需要此项。                                                                                                                                                                           | No       |
| trino.jdbc.properties.                      | string  | (none)                | 原始 Trino JDBC 驱动程序属性的配置键前缀，请参阅[连接到启用 TLS 的协调器](#connecting-to-a-tls-enabled-coordinator)。                                                                                                                                                                                      | No       |
| gravitino.metadata.refresh-interval-seconds | integer | 10                    | `gravitino.metadata.refresh-interval-seconds` 定义了从 Gravitino 服务器刷新元数据的间隔时间（以秒为单位），默认值为 10 秒。                                                                                                                                                                                    | No       |
| gravitino.trino.skip-version-validation     | boolean | false                 | `gravitino.trino.skip-version-validation` 定义是否跳过 Trino 版本验证。Gravitino 支持 440 到 478 之间的 Trino 版本。如果此选项为 `true`，仍然可以使用不受支持的 Trino 版本，但不保证兼容性。                                                                              | No       |
| gravitino.client.                           | string  | (none)                | Gravitino 客户端配置的配置键前缀。                                                                                                                                                                                                                                                                                    | No       |
| gravitino.trino.skip-catalog-patterns       | string  | (none)                | `gravitino.trino.skip-catalog-patterns` 定义了一个以逗号分隔的目录名正则表达式模式列表，这些模式应从加载中排除。例如，`test_.*, .*_tmp` 会排除所有以 `test_` 开头或以 `_tmp` 结尾的目录。                                                                                                | No       |
| gravitino.use-single-metalake               | boolean | true                  | 如果为 `true`，则仅使用一个 metalake，并且目录由 `<catalog_name>` 标识。如果为 `false`，则启用多 metalake 模式，并且目录由 `<metalake_name>.<catalog_name>` 标识。                                                                                                                                                | No       |
| gravitino.iceberg.rest-routing-enabled      | boolean | true                  | 非 REST `lakehouse-iceberg` 目录是否必须通过 Gravitino Iceberg REST 服务器进行路由。启用后，在发现成功或配置了 `gravitino.iceberg.rest-uri` 之前，不会注册目录。将此项设置为 `false` 可保留旧版 `catalog-backend` 转换并跳过发现。 | No       |
| gravitino.iceberg.rest-uri                  | string  | (none)                | Gravitino Iceberg REST 服务器 (IRC) 的端点。它是从此连接器的 metalake 的 Gravitino 服务器中自动发现的；仅设置为覆盖发现的值。当可用时，符合条件的 `lakehouse-iceberg` 目录将通过 IRC 加载，从而启用凭证分发。                                               | No       |
| gravitino.iceberg.rest-catalog.             | string  | (none)                | 传递给内部 Trino Iceberg REST 目录的属性前缀。该前缀会被重写为 `iceberg.rest-catalog.`。`uri`、`warehouse` 和 `prefix` 键是保留的，并由连接器派生。                                                                                                                               | No       |

要配置 Gravitino 客户端，请使用以 `gravitino.client.` 为前缀的属性。这些属性将直接传递给 Gravitino 客户端。

**注意：** 无效的配置属性将导致异常。请参阅 [Gravitino Java 客户端配置](../how-to-use-gravitino-client.md#java-client-configuration) 以获取更多支持的客户端配置。

升级不提供 Iceberg REST 端点的部署时，要么配置
`gravitino.iceberg.rest-uri`，或者设置 `gravitino.iceberg.rest-routing-enabled=false` 以保留
旧的 `catalog-backend` 转换。否则，非 REST 的 `lakehouse-iceberg` 目录将保持
未注册状态，直到发现成功。参见
[Iceberg 目录](./catalog-iceberg.md#how-trino-reaches-the-catalog)。

多 metalake 模式 (`gravitino.use-single-metalake=false`) 在 Trino 连接器版本 440-445 和 469-478 中受支持。在版本 446-468 上，会记录一条警告并且连接器会初始化，但该模式并未得到完全支持，某些操作可能会失败。

**注意：** 在多 metalake 模式下，`gravitino.iceberg.rest-uri` 仅在限定于某个
metalake 时才会生效，即 `gravitino.iceberg.rest-uri.<metalake_name>` —— 未限定作用域的形式将被忽略，因为单个
Iceberg REST 服务器仅服务于一个 metalake，将其应用到每个 metalake 会
导致其他 metalake 路由错误。未限定作用域的形式在单 metalake 模式下仍然有效。

## 连接到启用 TLS 的协调器

Gravitino Trino 连接器注册 catalog 的方式是回连到 Trino coordinator，经由
JDBC 并运行 `CREATE CATALOG` / `DROP CATALOG`。此连接在
连接器启动时建立，并被元数据刷新循环重用，因此必须为
coordinator 自身的 TLS 和授权设置进行配置。

```properties
connector.name=gravitino
gravitino.metalake=metalake
gravitino.uri=http://localhost:8090

# The internal JDBC connection to the coordinator.
trino.jdbc.user=admin
trino.jdbc.password=YourSecureTrinoPassword
trino.jdbc.ssl.truststore.path=/etc/trino/truststore.jks
trino.jdbc.ssl.truststore.password=YourSecureTruststorePassword
# Required when the deployment only allows CREATE CATALOG with a privileged role.
trino.jdbc.roles=system:sysadmin
```

`trino.jdbc.ssl.enabled` may be omitted when the Trino `discovery.uri` uses the `https` scheme, as
it is derived from that scheme by default. When `discovery.uri` omits the port, the default port of
its scheme is used, that is `443` for `https` and `80` for `http`.

`trino.jdbc.ssl.*` 配置仅在启用 TLS 的连接上有意义。设置任何
在禁用 TLS 时设置它们会导致连接器在启动时失败，而不是被静默忽略，因此
配置错误的 truststore 永远不会降级为明文连接。同样地，truststore
密码和类型需要 truststore 路径，而 keystore 密码和类型需要 keystore
路径：如果没有该路径，驱动程序将回退到其默认值，而它们将不适用于该默认值。

如果协调器证书由 JVM 不信任的 CA 签名，请将其导入到
信任库，并将 `trino.jdbc.ssl.truststore.path` 指向它：

```shell
# Export the coordinator certificate, then import it into a dedicated truststore.
openssl s_client -showcerts -connect coordinator.example.com:8443 </dev/null \
  | openssl x509 -outform PEM > coordinator.pem
keytool -importcert -noprompt -alias trino-coordinator -file coordinator.pem \
  -keystore /etc/trino/truststore.jks -storepass YourSecureTruststorePassword
```

:::caution
`trino.jdbc.ssl.verification=NONE` 会完全禁用证书验证，并使
连接暴露于中间人攻击。仅将其用于故障排除；改为将协调器
证书导入信任库。
:::

`trino.jdbc.*` 属性仅供 coordinator 使用。它们永远不会被复制到
connector 创建的 catalog 中，因此它们持有的凭证不会到达生成的
`CREATE CATALOG` 语句或 Trino catalog 属性文件中。

### 双向 TLS 与证书认证

需要双向 TLS 的协调器也需要客户端证书。将
`trino.jdbc.ssl.keystore.path` 指向保存它的密钥库：

```properties
trino.jdbc.ssl.keystore.path=/etc/trino/client.p12
trino.jdbc.ssl.keystore.password=YourSecureKeystorePassword
```

:::note
双向 TLS 配置是为完整性而提供的，并且尚未针对
需要客户端证书的协调器进行验证。
:::

Trino 也可以配置为使用 `http-server.authentication.type=CERTIFICATE`，其中客户端
证书本身即作为登录凭证，协调器从证书的
主体中提取用户名。该连接器目前不支持这种身份验证类型：它始终使用
`trino.jdbc.user` 进行身份验证，因此以这种方式配置的协调器会拒绝内部 JDBC 连接。

### 传递任意 JDBC 驱动属性

任何没有专用配置的 Trino JDBC 驱动程序属性都可以通过
`trino.jdbc.properties.` 前缀传递。该前缀会被去除，剩余部分将交给驱动程序
原样处理，覆盖从专用 `trino.jdbc.*` 配置派生的值：

```properties
trino.jdbc.properties.KerberosRemoteServiceName=trino
trino.jdbc.properties.SSLKeyStorePath=/etc/trino/client.p12
trino.jdbc.properties.SSLKeyStorePassword=YourSecureKeystorePassword
```

通过此前缀传递的属性会直接交给驱动程序而不经验证，这与
专用的 `trino.jdbc.*` 配置不同。因此，未知名称或无效值会表现为
建立连接时的驱动程序错误，而不是配置错误。

请参阅 [Trino JDBC 驱动程序文档](https://trino.io/docs/current/client/jdbc.html) 以获取
受支持的属性名称的完整列表。

## 身份验证

Gravitino Trino 连接器支持使用 Simple、Basic、OAuth 和 Kerberos 身份验证向 Gravitino 服务器进行身份验证。有关详细的身份验证配置，请参阅 [Trino Connector Authentication](./authentication.md)。
