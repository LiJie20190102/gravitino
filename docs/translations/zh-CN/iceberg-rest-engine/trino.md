---
sidebar_label: Trino
title: 将 Trino 连接到 Iceberg REST Catalog
---
## 简介

Apache Gravitino 暴露了一个 Iceberg REST Catalog (IRC) 端点，任何兼容 Iceberg 的引擎都可以
直接连接到该端点，无需安装 Gravitino 专用的连接器插件。以下各节
描述了如何配置 Trino 以使用该端点。

大部分配置在 Trino 端，此处予以介绍。存储凭证设置
位于 Gravitino catalog 上，在[凭证
分发](../security/credential-vending.md)中有所介绍，本页在适用的
各处均会链接到该文档。

## 快速开始

在 Trino 的 `etc/catalog/` 目录中创建一个 catalog 属性文件。文件名决定了
Trino 中的 catalog 名称，因此 `gravitino_irc.properties` 会创建一个名为 `gravitino_irc` 的 catalog。某些
发行版将该目录放在 `etc/trino/catalog/`。无论哪种方式，这些都是
每个 catalog 的属性，不属于 `config.properties`。

下面的文件是完整的，使用分发的凭证和 OAuth2 认证。将其放入
`etc/catalog/` 并重启 Trino。每个注释组在下方都有匹配的章节，介绍
属性的作用以及可替代的选项。

```properties
# Connection properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://{gravitino_host}:9001/iceberg
iceberg.rest-catalog.prefix={catalog}

# Storage access
iceberg.rest-catalog.vended-credentials-enabled=true
fs.s3.enabled=true
s3.region={region_name}

# Authentication
iceberg.rest-catalog.security=OAUTH2
iceberg.rest-catalog.oauth2.credential={client_id}:{client_secret}
iceberg.rest-catalog.oauth2.server-uri={token_endpoint_uri}
iceberg.rest-catalog.oauth2.scope={scope}

# Table defaults
iceberg.file-format=PARQUET
iceberg.compression-codec=ZSTD
```

在 Trino 480 及更早版本中，`fs.s3.enabled` 命名为 `fs.native-s3.enabled`。请参阅[存储
访问](#凭证分发的工作原理)。

## 前提条件

在 Gravitino 端：

- Gravitino 运行时已启用 Iceberg REST 服务。请参阅 [Iceberg REST catalog
服务](../iceberg-rest-service.md) 进行设置。
- Trino coordinator 和所有 worker 均可访问的 IRC 端点。默认端口为 `9001`。
- 对于分发的凭证，需要进行三项 catalog 端设置，均在[凭证
分发](../security/credential-vending.md)中有所介绍：
  - 在 catalog 上配置凭证提供者及其承担的角色。请参阅
[`s3-token`](../security/credential-vending.md#s3-token)。
  - IRC classpath 上的云 bundle jar 包。请参阅
[部署](../security/credential-vending.md#deployment)。
  - AWS IAM 中分发角色上的信任策略和权限策略。

在凭证分发所需的一切配置中，只有 [存储访问](#凭证分发的工作原理) 中的 Trino 属性
是在本页上配置的。如果缺少上述任何一项，一个本身正确的 Trino catalog 文件
无法分发任何凭证，并且产生的失败会在 Trino 而非 Gravitino 中暴露出来。
请参阅 [故障排除](#gravitino-连接器与-irc-对比) 了解每项缺失产生的症状。

在 Trino 端，发布要求因功能而异：

| 功能                                                       | 最低 Trino 版本 |
|:-----------------------------------------------------------------|:----------------------|
| 原生 S3 文件系统，消费分发凭证         | 419                   |
| 在每个 catalog 文件中显式激活文件系统             | 458                   |
| Azure 的分发凭证                                     | 481                   |
| S3、GCS 和 Azure 的可刷新分发凭证            | 481                   |
| 通过 `iceberg.rest-catalog.http-headers` 进行基本认证 | 481                   |
| 支持 OAuth2 和嵌套命名空间的 `SHOW SCHEMAS`                 | 482                   |

已通过 AWS S3 针对 Gravitino 1.3.0 和 Trino 478 进行验证。Trino 481 及更高版本中的
属性名称和行为来自 Trino 文档和发行说明，而不是来自该运行。

## 哪些 Gravitino Catalog 可访问

`conf/gravitino.conf` 中的两个设置决定了 Trino catalog 文件可以访问的内容：

```properties
gravitino.iceberg-rest.catalog-config-provider = dynamic-config-provider
gravitino.iceberg-rest.gravitino-metalake = {metalake}
```

metalake 在启动时固定。`gravitino-metalake` 恰好指定一个 metalake，并且 IRC 仅
为该 metalake 中的 catalog 提供服务。通过 Gravitino REST API 创建另一个 metalake
并不会使其在该端点上可访问。将 IRC 指向不同的 metalake 意味着
编辑 `gravitino.conf` 并重启，而同时为两个 metalake 提供服务意味着运行两个 Iceberg REST
服务。服务器启动时 metalake 不必存在，因此先在配置中命名它，
然后再创建它是可行的。

Catalog 不是固定的。动态配置提供者会轮询 Gravitino 服务器以获取该
metalake 中的 catalog，因此通过 REST catalog API 创建的 catalog 无需重启
即可访问。在 Trino 中使用 `iceberg.rest-catalog.prefix` 选择一个 catalog，这在[连接
属性](#存储访问)中有所介绍。设置 `gravitino.iceberg-rest.default-catalog-name` 决定了
当客户端完全不发送前缀时由哪个 catalog 响应。

相反，静态配置提供者为直接在 `gravitino.conf` 中定义的 catalog 提供服务，使用
以 `gravitino.iceberg-rest.` 为前缀的键，在服务器启动时加载一次。以这种方式定义的
catalog 不会在 metalake 中注册，因此无法授予其权限。大多数已发布的
示例使用静态形式，因此请注意不要混淆两者。

通过 IRC 进行 Gravitino 访问控制需要同时满足三个条件，而不仅仅是动态提供者：

- 作为 Gravitino 服务器内的辅助服务运行的 Iceberg REST 服务。独立的
  Iceberg REST 部署不支持访问控制。请参阅[部署
  模式](../iceberg-rest-service.md#deployment-modes)，其中的模式表带有访问
  控制列，以及[访问控制](../iceberg-rest-service.md#access-control)。
- Gravitino 服务器上的 `gravitino.authorization.enable = true`。请参阅[访问
  控制](../security/access-control.md)。
- 动态配置提供者。请参阅[动态 catalog 配置
  提供者](../iceberg-rest-service.md#dynamic-catalog-configuration-provider)。

有关启用这三者然后对通过 IRC 访问的 catalog 授予权限的端到端操作指南，
请参阅[访问控制教程](../iceberg-rest-service.md#access-control-tutorial)。

请参阅[设置属性](../security/credential-vending.md#setting-properties) 了解凭证
属性在这两个提供者之间的区别，以及 [Iceberg REST catalog
服务](../iceberg-rest-service.md) 了解完整的提供者配置。

## 连接属性

```properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://{gravitino_host}:9001/iceberg
iceberg.rest-catalog.prefix={catalog}
```

| 属性                     | 用途                                | 必需 |
|:-----------------------------|:---------------------------------------|:---------|
| `connector.name`             | 在此路径下始终为 `iceberg`         | 是      |
| `iceberg.catalog.type`       | 在此路径下始终为 `rest`            | 是      |
| `iceberg.rest-catalog.uri`   | Gravitino IRC 端点             | 是      |
| `iceberg.rest-catalog.prefix`| 选择要使用的 Gravitino catalog | 是      |

Trino 在 [Iceberg REST catalog 配置
属性](https://trino.io/docs/current/object-storage/metastores.html#rest-catalog) 中记录了完整集合。

`iceberg.rest-catalog.prefix` 必须与 Gravitino 中的 catalog 名称匹配。向服务器
确认预期值：

```bash
curl -s "http://{gravitino_host}:9001/iceberg/v1/config?warehouse={catalog}"
```

Gravitino 在 `defaults` 下返回前缀，因此在 Trino 中显式设置它是匹配而不是
覆盖它。

存储访问和认证是独立的选择。从下面两个
章节中各选择一个选项。

## 存储访问

Trino 需要凭证来读写底层对象存储。选择分发凭证
或静态凭证。请勿同时配置两者。

无论选择哪种，都必须启用原生 S3 文件系统。它为
S3 访问执行请求签名，如果没有它，元数据操作会成功，而数据读取会失败并提示
`ICEBERG_FILESYSTEM_ERROR`。

```properties
fs.s3.enabled=true
```

Trino 481 移除了旧版对象存储支持，仅保留 `fs.hadoop.enabled` 用于 HDFS，并且
原生文件系统属性同时去掉了 `native-` 段。480 及更早版本的
文档记录了 `fs.native-s3.enabled`，481 及更高版本的文档记录了 `fs.s3.enabled`。请使用所运行版本
对应的文档中记录的名称。

### 凭证分发的工作原理

1. Trino 调用 Gravitino IRC 端点上的 `loadTable`。当设置
   `iceberg.rest-catalog.vended-credentials-enabled=true` 时，Trino 会自动
   发送 `X-Iceberg-Access-Delegation: vended-credentials` 标头。
2. Gravitino 针对 catalog 上配置的 IAM 角色调用 STS `AssumeRole`。
3. Gravitino 在 `loadTable` 响应中返回 `storage-credentials` 块，其中包含范围限定为
   该表 S3 前缀的临时凭证。
4. Trino 将这些凭证用于该查询中的 S3 读写。

该设计的一个特点值得明确说明，因为人们通常会有相反的假设。
分发的凭证范围限定为表路径，而不是调用用户。Gravitino
通过承担 catalog 上配置的固定角色来生成凭证，因此每个能访问特定表的调用者
都会获得具有相同存储权限的凭证。基于用户的限制来自于 Gravitino
访问控制决定谁能访问该表，而不是来自凭证本身。

### 分发凭证

在上文的快速开始中使用。Gravitino 在查询时生成短期的、路径限定的凭证，
因此 Trino 配置中不存在长期存储密钥。

```properties
iceberg.rest-catalog.vended-credentials-enabled=true
fs.s3.enabled=true
s3.region={region_name}
```

这所需的 catalog 端配置，包括凭证提供者及其承担的角色，
以及其背后的 IAM 策略，在[凭证
分发](../security/credential-vending.md)中有所介绍。这些都不是从 Trino catalog 文件设置的。

如果文件中还设置了 `s3.aws-access-key` 和 `s3.aws-secret-key`，Trino 会请求分发
凭证，接收凭证，然后仍然使用静态密钥进行签名。不会出现警告，并且每个
查询都能正常工作，因此该文件看起来像是在使用分发，但实际并非如此。检查两者是否
存在，并参阅[验证](#确认服务器分发凭证) 了解如何确认实际上哪些凭证
到达了 S3。

后端覆盖范围因 Trino 版本而异。S3 一直受支持。Trino 481 添加了 Azure
（[trinodb/trino#23238](https://github.com/trinodb/trino/issues/23238)）和可刷新的分发
凭证，其发行说明描述为涵盖 S3、GCS 和 Azure
（[trinodb/trino#28998](https://github.com/trinodb/trino/issues/28998)）。在依赖 GCS 或 Azure 之前，请查阅所运行版本对应的发行说明，
并在分发尚不可用时使用静态
凭证。

### 静态凭证

在 Trino 中直接配置存储密钥。设置更简单，但密钥是长期的，未
限定于表路径，并且在 Gravitino 之外管理。

相对于快速开始，移除 `iceberg.rest-catalog.vended-credentials-enabled` 并配置
密钥：

```properties
fs.s3.enabled=true
s3.region={region_name}
s3.aws-access-key={access_key_id}
s3.aws-secret-key={secret_access_key}
```

将 `iceberg.rest-catalog.vended-credentials-enabled=true` 与密钥一起保留在原位不是
错误，也不会产生警告。Trino 会请求分发凭证，然后仍然使用静态密钥
进行签名，原因如[分发凭证](#静态凭证)中所述。

对于针对 MinIO 的本地开发。同样的优先级适用，因此在此也
移除 `iceberg.rest-catalog.vended-credentials-enabled`：

```properties
fs.s3.enabled=true
s3.endpoint=http://{minio_host}:9000
s3.path-style-access=true
s3.aws-access-key={minio_access_key}
s3.aws-secret-key={minio_secret_key}
s3.region=us-east-1
```

## 认证

Trino 如何向 Gravitino 标识自己。独立于上文的存储凭证选择。如果
Gravitino 要求身份标识，Trino 必须在此处提供一个，否则请求会在任何
分发发生之前被拒绝。请参阅[如何认证](../security/how-to-authenticate.md) 了解 Gravitino 端的内容。

### 无认证

完全省略认证块。相对于快速开始，这意味着删除这四
行：

```properties
iceberg.rest-catalog.security=OAUTH2
iceberg.rest-catalog.oauth2.credential={client_id}:{client_secret}
iceberg.rest-catalog.oauth2.server-uri={token_endpoint_uri}
iceberg.rest-catalog.oauth2.scope={scope}
```

如果它们均未被设置，`iceberg.rest-catalog.security` 将保持其默认值 `NONE`，并且 Trino
不会向 IRC 发送凭证。请参阅 [Iceberg REST catalog 配置
属性](https://trino.io/docs/current/object-storage/metastores.html#rest-catalog) 了解该
属性及其其他值。

仅将其用于本地开发和隔离的测试环境。由于请求上没有身份标识，
Gravitino 无需授权，因此在 catalog 上授予的权限对
通过 IRC 到达的查询没有影响，并且每个能访问该端口的调用者都具有相同的访问权限。添加
分发凭证会将这种影响扩展到元数据之外。由于 IRC 会为任何请求的调用者
生成凭证，如[凭证分发的工作原理](#分发凭证)中所述，任何
能访问该端点的人都可以获得数据仓库的有效存储凭证。

如果服务器确实要求身份标识而 Trino 未提供，请求会在到达分发
之前被拒绝，这表现为 403 错误而不是存储错误。

### 基本认证

需要 Trino 481 或更高版本。

`iceberg.rest-catalog.security` 没有 Basic 值，因此无法配置 Trino 通过
用户名和密码向 REST catalog 进行认证。Gravitino 的 IRC 确实接受针对
[本地用户和组](../security/local-users-and-groups.md)的 HTTP Basic 认证，因此
解决方法是自行构造标头并让 Trino 将其附加到每个 REST catalog 请求上。
Trino 481 新增了 `iceberg.rest-catalog.http-headers`
（[trinodb/trino#24236](https://github.com/trinodb/trino/issues/24236)）用于发送任意 header，
Basic 认证只是该功能的一个用途，而非独立的功能。

对凭证进行编码：

```bash
echo -n '{username}:{password}' | base64
```

然后设置 header：

```properties
iceberg.rest-catalog.http-headers=Authorization: Basic {base64_credentials}
```

在 481 之前的版本中无法发送 header，因此只能选择 OAuth2 或无
认证。

Trino 将该值视为不透明 header 而非凭证，因此不会对其进行续期或轮换，
每次请求时原样发送。Base64 是编码而非加密，任何能够
读取 catalog 文件的人都可以恢复密码。Trino 文档也将该属性描述为携带
额外的非敏感 header，因此将凭证放入其中虽然可行，但与其声明的
用途相悖。在 Gravitino 服务器支持的情况下，优先使用 OAuth2。

### OAuth2 认证

两种方式，区别在于由谁获取 token。两者在网络传输中使用相同的 `Authorization: Bearer` header，
因此 Gravitino 端的配置对两者都是相同的。

#### 客户端凭证流

上文快速入门中使用的就是该方式。Trino 持有 client ID 和 secret，自行请求 token，
并在当前 token 过期时获取新的 token。推荐使用此方式。

```properties
iceberg.rest-catalog.security=OAUTH2
iceberg.rest-catalog.oauth2.credential={client_id}:{client_secret}
iceberg.rest-catalog.oauth2.server-uri={token_endpoint_uri}
iceberg.rest-catalog.oauth2.scope={scope}
```

`iceberg.rest-catalog.oauth2.server-uri` 是 Trino 定位身份提供者的方式。该参数接受
提供者的 token endpoint，而非 issuer 或 realm URL。在 Keycloak 中即：

```
https://{keycloak_host}/realms/{realm}/protocol/openid-connect/token
```

随后 Trino 将接收到的 token 作为 bearer token，通过 HTTP header 在每次
Iceberg REST 请求中发送给 Gravitino：

```
Authorization: Bearer {access_token}
```

#### 预签发 Token

Trino 在每次对 IRC 的请求中发送一个固定 token，该 token 从身份提供者通过带外方式获取。
没有任何机制对其进行续期，因此当 token 过期后，每个请求都会返回 401 错误，直到有人
修改 catalog 文件并重启 Trino。

```properties
iceberg.rest-catalog.security=OAUTH2
iceberg.rest-catalog.oauth2.token={token}
```

在 Trino 无法访问 OAuth2 服务器时，或进行短期测试时使用此方式。注意，
token 以明文形式存储在 catalog 文件中，任何能够读取该文件的人都可以
直接对 IRC 重放该 token，而 client secret 则不会如此。

#### Token 交换

在 Trino 479 及更高版本中，为上述两种方式都添加以下配置，以避免可能导致
重复 token 请求的 token 交换行为：

```properties
iceberg.rest-catalog.session=NONE
iceberg.rest-catalog.oauth2.token-exchange-enabled=false
```

`iceberg.rest-catalog.session=NONE` 已是默认值，可以省略。

## 表默认值

可选配置，与本页其他内容相互独立。这些配置设置了 Trino 通过 IRC
创建表时使用的默认值：

```properties
iceberg.file-format=PARQUET
iceberg.compression-codec=ZSTD
```

## 启动 Trino

Trino 是一个服务器进程，catalog 在 Trino 启动时加载。将
`gravitino_irc.properties` 放入 `etc/catalog/` 后，重启 Trino：

```bash
$TRINO_HOME/bin/launcher restart
```

Trino 重启后大约需要 20 秒才能接受查询，这段时间足以在脚本化运行中
产生误导性的连接错误。

Trino 运行后，使用 Trino CLI 连接：

```bash
trino --server http://{trino_host}:8080 --catalog gravitino_irc
```

或者不使用默认 catalog 连接，并在查询中使用完全限定名：

```bash
trino --server http://{trino_host}:8080
```

## 验证

### 确认服务器分发凭证

在假设 Trino 正在使用分发的凭证之前，先检查服务器。`loadTable` 响应中的
`storage-credentials` 块是直接证据：

```bash
curl -s -H "X-Iceberg-Access-Delegation: vended-credentials" \
  -H "Authorization: Bearer {token}" \
  http://{gravitino_host}:9001/iceberg/v1/{catalog}/namespaces/{namespace}/tables/{table} \
  | python3 -m json.tool | grep -A8 storage-credentials
```

预期输出：

```json
"storage-credentials": [
  {
    "prefix": "s3://{bucket_name}/{warehouse_path}/{namespace}/{table}",
    "config": {
      "s3.access-key-id": "ASIA...",
      "s3.secret-access-key": "...",
      "s3.session-token": "...",
      "s3.session-token-expires-at-ms": "..."
    }
  }
]
```

三个标志可用于区分真正的凭证分发与透传的静态凭证：访问密钥以
`ASIA` 而非 `AKIA` 开头，存在 session token，且前缀的作用域限定在
表路径而非整个 bucket。

### 确认引擎路径

```bash
trino --execute "SELECT * FROM {catalog}.{namespace}.{table}"
```

仅凭查询成功并不能证明正在使用凭证分发，因为静态密钥或实例配置文件
也能满足相同的读取操作。要在 AWS 层进行独立确认，CloudTrail 会显示
针对分发角色的 `AssumeRole` 调用，随后的 S3 操作归属于 assumed-role
会话而非基础 IAM 用户。在 EC2 实例配置文件可能满足 S3 读取操作的环境中，
CloudTrail 是权威的检查手段。

## 已知问题

### 长查询期间分发的凭证不会刷新

适用于 481 之前的 Trino 版本。

**原因：** Gravitino 在 `loadTable` 响应中声明了一个刷新端点，即
`client.refresh-credentials-endpoint`，但 Trino 在分发的凭证于查询过程中过期时不会调用该端点
（[trinodb/trino#25827](https://github.com/trinodb/trino/issues/25827)）。运行时间超过
STS 会话有效期的扫描将会失败。该差距是客户端的问题，而非 catalog 的限制。

**解决方案：** 升级到 Trino 481 或更高版本，该版本新增了可刷新的分发凭证功能
（[trinodb/trino#28998](https://github.com/trinodb/trino/issues/28998)）。在更早的版本中，调高
Gravitino catalog 上的 [`s3-token-expire-in-secs`](../security/credential-vending.md#s3-token)，
同时调高 IAM 角色的最大会话时长，或者将单个查询的运行时间控制在
会话有效期之内。

### 存储凭证在查询 JSON 中暴露

**原因：** Trino 将存储凭证序列化到写入和表维护操作的查询 JSON 中，任何具有写入权限的用户
都可以通过 Trino UI 或查询 API 读取这些凭证
（[GHSA-x27p-5f68-m644](https://github.com/trinodb/trino/security/advisories/GHSA-x27p-5f68-m644)）。
该暴露问题对静态凭证和分发凭证均适用。

**解决方案：** 对照已部署的 Trino 版本审查当前安全公告状态。较短的
`s3-token-expire-in-secs` 值可以限制暴露的分发凭证可用的
时间窗口，这是静态密钥无法提供的。

### Trino 返回有效凭证但未使用

**原因：** 至少有一份报告描述了某个 Trino 版本从服务器接收到正确的 `storage-credentials`
块但在 S3 访问时失败，而相同的端点从 Spark 可以正常工作
（[trinodb/trino#27416](https://github.com/trinodb/trino/issues/27416)，在 Trino 474 上报告）。

**解决方案：** 如果验证 curl 显示有效的凭证块但 Trino 仍然失败，在重新检查配置之前，
应将 Trino 版本视为可疑因素。

### 使用 OAuth2 和嵌套命名空间时 `SHOW SCHEMAS` 失败

**原因：** 当 `iceberg.rest-catalog.security=OAUTH2`、
`iceberg.rest-catalog.nested-namespace-enabled=true` 且 `iceberg.rest-catalog.session=NONE`（即
默认值）时，`SHOW SCHEMAS` 会递归调用 Iceberg REST 的 `listNamespaces`。在 482 之前的 Trino
版本中，每次递归调用都会创建一个独立的 OAuth 会话，这可能触发过量的 token
请求并导致 `Connection pool shut down` 或 `StackOverflowError` 等错误。

**解决方案：** 升级到 Trino 482 或更高版本。

### `TIMESTAMP WITH TIME ZONE` 值不会根据客户端会话时区进行调整

**原因：** Trino 不会根据客户端会话时区调整 `TIMESTAMP WITH TIME ZONE` 结果。与 Spark 和 Flink 不同，Trino
会基于存储的 timestamp-with-time-zone 值来显示这些
值。

**解决方案：** 使用 `at_timezone` 和 `current_timezone()` 进行转换：

```sql
SELECT
  id,
  at_timezone(timestamp_with_timezone_column, current_timezone())
FROM {catalog}.{namespace}.{table};
```

### Trino 标识符不区分大小写

**原因：** Trino 标识符不区分大小写，因此仅大小写不同的元数据名称无法被
区分。参见 [Trino 标识符
文档](https://trino.io/docs/current/language/reserved.html#language-identifiers)。该
限制源自 Trino 自身，并非 Gravitino 特有。

**解决方案：** 使用小写元数据名称，避免创建仅大小写不同的
对象。当 Gravitino 中已存在大小写混合的名称时，
`iceberg.rest-catalog.case-insensitive-name-matching=true`（默认关闭）可让 Trino 解析这些名称。
该配置并不能使仅大小写不同的名称变得可区分。

## 故障排查

此路径中的故障往往在远离根因处显现。下表将症状映射回产生这些症状的
配置。

| 症状                                                          | 可能原因                                                                                               |
|:-----------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|
| `SHOW CATALOGS` 中不可见 catalog                           | Trino 未重启，或 catalog 文件中存在解析错误。检查 Trino 服务器日志                      |
| `Failed to list namespaces`                                      | `iceberg.rest-catalog.prefix` 与 Gravitino catalog 名称不匹配，或身份被拒绝        |
| 403 `ForbiddenException`，principal 不在 metalake 中              | 身份在到达凭证分发之前被拒绝。Token principal 必须是 metalake 的成员            |
| `loadTable` 响应中缺少 `storage-credentials`       | catalog 上未设置 `credential-providers`，或 IRC classpath 中缺少 cloud bundle jar      |
| 数据读取时出现 `ICEBERG_FILESYSTEM_ERROR`，元数据正常          | 未启用原生 S3 文件系统，该版本的属性名错误，或静态密钥覆盖          |
| 尽管 `storage-credentials` 块有效但 S3 返回 `AccessDenied`    | 分发角色的权限策略，或 Trino catalog 文件中静态密钥优先          |
| `AssumeRole` 时 STS 返回 `AccessDenied`                               | 信任策略不允许 `s3-access-key-id` principal 担任分发角色                    |
| 响应中的访问密钥以 `AKIA` 开头                    | catalog 使用的是 `s3-secret-key` 而非 `s3-token`，因此静态密钥被原样分发           |
| 长查询在大约一小时后失败                            | STS 会话过期且无客户端刷新。参见已知问题                                           |
| 验证 curl 显示有效凭证但 Trino 在 S3 上失败  | 可能是特定版本的消费 bug。参见已知问题                                                |

Catalog 侧的原因在 [凭证
分发](../security/credential-vending.md) 中有描述。

## Gravitino 连接器与 IRC 对比

| 特性                  | Gravitino 引擎连接器 | IRC                           |
|:-------------------------|:---------------------------|:------------------------------|
| 是否需要引擎插件   | 是                        | 否                            |
| Gravitino 访问控制 | 是                        | 是，适用于 API 创建的 catalog |
| 支持的引擎        | Trino、Spark、Flink、Daft  | 任何 Iceberg 兼容引擎 |
| 凭证分发       | 因情况而异                     | 是，参见 Trino 发行说明  |

通过 Gravitino REST catalog API 创建的 catalog 会注册到 metalake 中，因此可以
对其授予权限，且 Gravitino 访问控制适用于通过 IRC 到达这些 catalog 的查询。
而在 Iceberg REST 服务配置文件中定义的 catalog 不会注册到
metalake 中，因此无法对其授予权限。

## 相关内容

- [凭证分发](../security/credential-vending.md)
- [Iceberg REST catalog 服务](../iceberg-rest-service.md)
- [连接 Spark 到 Iceberg REST](./spark.md)
- [连接 Flink 到 Iceberg REST](./flink.md)
- [Trino Gravitino 连接器](../trino-connector/trino-connector.md)

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免责声明**：
本文件由 AI 翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 翻译完成。尽管我们力求准确，但请注意，自动翻译可能包含错误或不准确之处。原始语言版文件应视为权威来源。对于重要信息，建议使用专业人工翻译。我们对因使用本翻译而产生的任何误解或误释不承担责任。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->