---
title: "Gravitino Server Configuration"
slug: "/gravitino-server-config"
keywords:
  - configuration
license: "This software is licensed under the Apache License version 2."
---

## 介绍

Apache Gravitino 服务器在启动时会读取 `conf/gravitino.conf`。几乎每个属性都有一个
默认值，因此服务器可以使用空文件启动，并且大多数部署只需更改其中少数几个
属性。例外是 `gravitino.authorization.serviceAdmins`，一旦你开启
授权，就必须设置它。

本页涵盖服务器本身。Catalog 属性用于配置单个 catalog，
而非服务器，将在下文介绍。辅助服务的属性位于
这些服务中：参见 [Iceberg REST Catalog Service](iceberg-rest-service.md) 和
[Security](security/how-to-authenticate.md)。

## 快速开始

### 开发

默认设置已经适合本地工作。服务器监听 `0.0.0.0:8090` 并将其
元数据保存在嵌入式 H2 数据库中，因此无需配置：

```shell
${GRAVITINO_HOME}/bin/gravitino.sh start
```

仍有一个属性值得设置。默认情况下，H2 将其数据库文件写入
`${GRAVITINO_HOME}/data/jdbc`，该目录位于解压后的发行版内。升级 Gravitino
意味着解压新的发行版，因此元数据就存放在你即将
替换或放弃的目录中。将其移动到升级不会触及的地方：

```text
# conf/gravitino.conf
gravitino.entity.store.relational.storagePath = /var/lib/gravitino/data/jdbc
```

这里的一切都未经过身份验证。默认的 `simple` 身份验证器接受客户端发送的任何
用户名，服务器使用纯 HTTP 通信，并且授权已关闭，因此每个调用者都可以做
任何事情。再加上 H2，Gravitino 对其不提供一致性或持久性保证，
这使得该配置除了本地工作外不适用于任何其他用途。

### 生产

生产服务器将元数据保存在 MySQL 或 PostgreSQL 中，对其调用者进行身份验证，强制执行
授权，并写入审计日志：

```text
# conf/gravitino.conf
# Entity store
gravitino.entity.store.relational.jdbcUrl      = jdbc:mysql://{db_host}:3306/{database}
gravitino.entity.store.relational.jdbcDriver   = com.mysql.cj.jdbc.Driver
gravitino.entity.store.relational.jdbcUser     = {username}
gravitino.entity.store.relational.jdbcPassword = {password}

# Transport
gravitino.server.webserver.enableHttps      = true
gravitino.server.webserver.keyStorePath     = /etc/gravitino/tls/server.jks
gravitino.server.webserver.keyStorePassword = {keystore_password}
gravitino.server.webserver.managerPassword  = {manager_password}

# Authentication
gravitino.authenticators                            = oauth
gravitino.authenticator.oauth.jwksUri               = {jwks_uri}
gravitino.authenticator.oauth.tokenValidatorClass   = org.apache.gravitino.server.authentication.JwksTokenValidator
gravitino.authenticator.oauth.serviceAudience       = {audience}
gravitino.authenticator.oauth.principalFields       = preferred_username,email,sub

# Authorization
gravitino.authorization.enable        = true
gravitino.authorization.serviceAdmins = {admin_user}

# Audit log
gravitino.audit.enabled = true

# Entity cache
gravitino.cache.enabled        = true
gravitino.cache.implementation = caffeine
gravitino.cache.lockSegments   = 16
gravitino.cache.enableStats    = true
```

只有 `gravitino.cache.enableStats` 会改变此处的行为；它会记录命中数、未命中数和加载
失败数，每五分钟一次，这使得缓存问题在生产环境中可见。这三
行重申了默认值，并将其详细列出，以便缓存配置可以在
一个地方进行审查，而不是从其缺失中推断。将 `lockSegments` 提高到默认值以上，如果
服务器负载足够高，以至于缓存锁竞争出现在性能分析中。

此区块依赖的四件事：

**数据库模式不会为您自动创建。** 请初始化它，并将 JDBC 驱动 jar 包放入
`${GRAVITINO_HOME}/libs/` 中，在首次启动前完成。参见
[关系型后端存储](how-to-use-relational-backend-storage.md)。

**HTTPS 替代 HTTP，而不是与其并存。** 设置了 `enableHttps` 的服务器不再提供
纯 HTTP，因此客户端和 Web UI 必须迁移到 `httpsPort`，默认为 `8433`。参见
[HTTPS](security/how-to-use-https.md)。

**验证器只有一行，但其提供者并非如此。** 上面的代码块针对一个
JWKS 端点验证 JWT，这是外部身份提供者的常见情况。静态签名密钥、
Kerberos 和 Web UI 的 OIDC 登录流程各自需要一组不同的属性。请参阅
[如何进行身份验证](security/how-to-authenticate.md)，或
[本地用户和组](security/local-users-and-groups.md) 以将用户和组保留在
Gravitino 自己的元数据存储中，而不是外部提供者中。

**`gravitino.authorization.serviceAdmins` 没有默认值。** 它是这里唯一一个
Gravitino 不会为你自动填充的属性，在没有它的情况下启用授权会在启动时失败。至于
那些管理员和其他所有人接下来可以做的事情，则是
[访问控制](security/access-control.md) 的主题。

给 JVM 分配超过其默认占用的 1 GB：

```shell
export GRAVITINO_MEM="-Xms4g -Xmx4g -XX:MaxMetaspaceSize=1g"
```

### Docker

Gravitino 镜像并非只是根据你提供的配置文件来运行服务器。在
启动时，入口点会重写 `conf/gravitino.conf`，将其自身的默认值应用于大约二十多个
属性，然后再应用任何受支持的环境变量。配置容器
通过环境变量：

```shell
docker run --rm -d \
  -p 8090:8090 \
  -e GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_URL="jdbc:postgresql://{db_host}:5432/{database}" \
  -e GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_DRIVER="org.postgresql.Driver" \
  apache/gravitino:{tag}
```

要改为提供配置文件，例如从 Kubernetes ConfigMap，请禁用
重写（使用 `SKIP_CONFIG_REWRITE=true`）。请参阅
[容器配置](#container-configuration) 了解重写的作用以及它识别哪些
变量。

### 运行多个服务器

负载均衡器后面的服务器共享实体存储，但保留本地缓存。每台服务器轮询
实体变更日志，并使其他服务器已修改的条目失效。默认设置是安全的：
三秒轮询一次，并且无法保持其缓存最新的服务器会选择退出，而不是提供
它知道已过期的元数据。将负载均衡器的健康检查指向 `GET /health/ready`，这样一台
丢失了数据库的服务器就会停止接收流量。

## 服务器配置

本节中的每个属性都应位于 `${GRAVITINO_HOME}/conf/gravitino.conf` 中，每行一个
`property = value` 对。服务器在启动时读取该文件一次，因此更改
将在下次重启时生效。默认值为 `(empty)` 表示该属性存在一个
空字符串或列表；`(none)` 表示它完全没有默认值。

### 服务请求

#### HTTP 服务器

| 配置项                                   | 描述                                                                                                                                                                                  | 默认值                           |
|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| `gravitino.server.webserver.host`                    | 服务器绑定的地址。                                                                                                                                                             | `0.0.0.0`                               |
| `gravitino.server.webserver.httpPort`                | 服务器监听的端口。                                                                                                                                                              | `8090`                                  |
| `gravitino.server.webserver.minThreads`              | Jetty 线程池中的最小线程数。低于 8 的值会被提升到 8。                                                                                                                    | 处理器数量的两倍，8 到 100     |
| `gravitino.server.webserver.maxThreads`              | Jetty 线程池中的最大线程数。低于 8 的值会被提升到 8，且该值必须至少为 `minThreads`。                                                                       | 处理器数量的四倍，最小 400 |
| `gravitino.server.webserver.threadPoolWorkQueueSize` | Jetty 线程池工作队列的大小。                                                                                                                                                    | `100`                                   |
| `gravitino.server.webserver.idleTimeout`             | 空闲连接的超时时间（毫秒）。                                                                                                                                                | `30000`                                 |
| `gravitino.server.webserver.stopTimeout`             | Jetty 等待优雅关闭的时间（毫秒）。参见 `org.eclipse.jetty.server.Server#setStopTimeout`。                                                                              | `30000`                                 |
| `gravitino.server.shutdown.timeout`                  | Gravitino 服务器自身优雅关闭的时间（毫秒）。                                                                                                                | `3000`                                  |
| `gravitino.server.webserver.requestHeaderSize`       | HTTP 请求头的最大大小（字节）。                                                                                                                                             | `131072`                                |
| `gravitino.server.webserver.responseHeaderSize`      | HTTP 响应头的最大大小（字节）。                                                                                                                                            | `131072`                                |
| `gravitino.server.webserver.customFilters`           | 应用于 API 的 servlet 过滤器类名的逗号分隔列表。                                                                                                                      | (空)                                 |
| `gravitino.server.rest.extensionPackages`            | 要扫描以查找额外 REST 资源的包的逗号分隔列表。                                                                                                                      | (空)                                 |
| `gravitino.server.visibleConfigs`                    | 在未经身份验证的 `GET /configs` 端点上暴露的额外属性的逗号分隔列表，叠加在它始终返回的固定集合之上。是累加的，因此每个条目都会扩大公开的范围。 | (空)                                 |
| `gravitino.server.bulk.maxItems`                     | 单个批量请求中允许的最大项目数。                                                                                                                                    | `100`                                   |
| `gravitino.server.webserver.includeErrorStackTrace`  | HTTP 错误响应是否包含服务器端堆栈跟踪。在新的部署中将此设置为 `false`，因为响应可能会暴露内部实现细节。默认保持为 `true` 只是为了避免破坏期望 `stack` 字段的旧客户端。参见 [OWASP REST 安全：错误处理](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html#error-handling) 和 [CWE-209](https://cwe.mitre.org/data/definitions/209.html)。 | `true`                                  |

Filters named in `customFilters` must be standard `javax.servlet` filters. Pass parameters to a
filter with properties of the form
`gravitino.server.webserver.{filter_class_name}.param.{param_name} = {value}`.

`GET /configs` 为 Web UI 提供支持，因此它无需身份验证即可响应，并且总是返回
`gravitino.authenticators`、`gravitino.authorization.enable` 和 `gravitino.schema.separator`。
当 `oauth` 包含在身份验证器中时，它会添加 OAuth 客户端设置。将您添加的任何内容
通过 `visibleConfigs` 视为公开，并且仅添加客户端在能够
进行身份验证之前所需的属性。

另外两组 `gravitino.server.webserver.*` 属性在别处有文档说明，因为
它们属于功能特性而非 Web 服务器本身。TLS、密钥库、信任库以及
客户端证书身份验证在 [HTTPS](security/how-to-use-https.md) 中。CORS 过滤器
及其允许的来源、方法和标头，当浏览器客户端运行在与服务器不同的
来源时需要，详见 [CORS](security/how-to-use-cors.md)。

#### 模式名称

支持分层 schema 的目录将层级结构作为单个带分隔符的名称公开在
API 边界。在内部，各级别使用 ASCII-1 作为物理分隔符进行存储，因此
配置的分隔符仅作为外部表示，并且它既不能是空白，也不能是
`.`, 也不能是 ASCII-1。

| 配置项           | 描述                                                                                                                                                       | 默认值 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.schema.separator` | Separator representing a multi-level schema name at the API boundary, as in `A:B:C`. See [Hierarchical schema](lakehouse-iceberg-catalog.md#hierarchical-schema). | `:`           |

#### 健康检查端点

Gravitino 暴露了三个健康端点，遵循
[MicroProfile Health](https://microprofile.io/project/eclipse/microprofile-health) 语义。所有
这些端点均免于身份验证，因此 Kubernetes 探针、负载均衡器和流量管理器
无需凭据即可访问它们。

| 端点                | 根别名          | 描述                                                                                                                                         | HTTP 状态码 |
|-------------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| `GET /api/health/live`  | `GET /health/live`  | 存活。如果 HTTP 线程可以响应且未观察到 OOM，则返回 200；否则返回 503。使用它来决定是否重启 pod。         | 200 or 503  |
| `GET /api/health/ready` | `GET /health/ready` | 就绪。当未观察到 OOM 且实体存储在探针超时时间内响应时，返回 200；否则返回 503。使用它来路由流量。 | 200 or 503  |
| `GET /api/health`       | `GET /health`       | 聚合。当上述两项都通过时返回 200。别名为 `GET /health.html`。                                                             | 200 or 503  |

| 配置项                                   | 描述                                                         | 默认值 |
|------------------------------------------------------|---------------------------------------------------------------------|---------------|
| `gravitino.server.health.entityStore.probeTimeoutMs` | 位于 `/ready` 之后的实体存储探测的超时时间（毫秒）。 | `2000`        |

每个端点返回相同的 JSON 结构，但检查项不同。`code` 始终为 `0`，
`status` 为 `up` 或 `down`，并且 `checks` 包含每个被探测组件的一个条目。`/live` 报告
仅 `httpServer`，`/ready` 仅报告 `entityStore`，而聚合端点报告两者
在未观察到 OOM 时：

```json
{
  "code": 0,
  "status": "down",
  "checks": [
    { "name": "httpServer", "status": "up", "details": {} },
    { "name": "entityStore", "status": "down", "details": { "reason": "timeout" } }
  ]
}
```

失败的 `entityStore` 检查会报告 `timeout`、`interrupted`、`probe-rejected`，
`entity store not initialized`，或者意外异常的简单类名。

在观察到 `OutOfMemoryError`（包括 Metaspace OOM）后，所有三个端点及其根
别名将返回 503，并带有一个 `jvm: down` 检查和原因 `OutOfMemoryError; restart required`。
此状态将持续到进程重启；成功的请求不会重置它。参见
[Out-of-memory failures](./health-and-readiness.md#out-of-memory-failures) 以了解检测范围。

#### JVM 内存

`GRAVITINO_MEM` 设置堆和元空间标志。启动脚本将其附加到 `JAVA_OPTS` 中，并且
Iceberg REST 服务器和 Lance REST 服务器的启动器会读取相同的变量。请将其设置在
`conf/gravitino-env.sh` 或在启动服务器之前的环境中。

The default, from `bin/common.sh`, is `-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m`. Raise it in
line with catalog count, plugin count, and query concurrency: `-Xms4g -Xmx4g
-XX:MaxMetaspaceSize=1g` suits a moderate production server, and larger deployments go beyond that.

#### 指标

| 配置项                        | 描述                                                                                                                                                                                                                                                                                                                                                                                    | 默认值 |
|-------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.metrics.timeSlidingWindowSecs` | 已弃用，不再使用。持续时间计时器和直方图现在使用指数衰减蓄水池而不是固定时间窗口，因此不常调用的操作会在更长的时间内（大约半天）持续报告真实的持续时间，而不是在 60 秒不活动后读取为零。空闲时间超过此值的操作最终仍会报告持续时间为零。 | `60`          |

### 存储元数据

#### 存储后端

Gravitino 通过 JDBC 存储元数据。H2 是默认选项，因为它是嵌入式的，不需要任何
外部依赖，这使得它适合本地开发，但不适合其他任何场景：Gravitino 不对
存储在 H2 中的元数据提供一致性或持久性保证。生产部署使用 MySQL 或
PostgreSQL，两者的设置步骤请参见
[关系型后端存储](how-to-use-relational-backend-storage.md)。

只要 URL 不是 `jdbc:h2`，driver、user 和 password 属性就是必需的。

| 配置项                                 | 描述                                                                                                                                                                                                          | 默认值                 |
|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| `gravitino.entity.store`                           | 实体存储实现。`relational` 是唯一支持的值。                                                                                                                                             | `relational`                  |
| `gravitino.entity.store.relational`                | 关系型存储实现。`JDBCBackend` 是唯一支持的值，它涵盖 H2、MySQL 和 PostgreSQL。                                                                                               | `JDBCBackend`                 |
| `gravitino.entity.store.relational.jdbcUrl`        | 后端连接的数据库 URL。                                                                                                                                                                                | `jdbc:h2`                     |
| `gravitino.entity.store.relational.jdbcDriver`     | 驱动类名。将驱动 jar 包放在 `${GRAVITINO_HOME}/libs/` 目录下。                                                                                                                                                | `org.h2.Driver`               |
| `gravitino.entity.store.relational.jdbcUser`       | 数据库用户名。                                                                                                                                                                                                   | `gravitino`                   |
| `gravitino.entity.store.relational.jdbcPassword`   | 数据库密码。                                                                                                                                                                                                   | `gravitino`                   |
| `gravitino.entity.store.relational.storagePath`    | 内嵌 H2 存放文件的位置。相对值会基于 `${GRAVITINO_HOME}` 进行解析。默认值位于部署目录内，因此替换该目录的升级操作会丢弃数据。请更改此设置。 | `${GRAVITINO_HOME}/data/jdbc` |
| `gravitino.entity.store.relational.maxConnections` | JDBC 连接池的最大大小。                                                                                                                                                                            | `100`                         |
| `gravitino.entity.store.relational.maxWaitMillis`  | 从连接池获取连接的最大等待时间（毫秒）。                                                                                                                                                         | `1000`                        |
| `gravitino.entity.store.maxTransactionSkewTimeMs`  | 最大事务偏差时间（毫秒）。                                                                                                                                                                            | `2000`                        |
| `gravitino.entity.store.deleteAfterTimeMs`         | 已删除和被取代的行保留的时间（毫秒）。接受 10 分钟到 30 天。                                                                                                                        | `604800000` (7 天)          |
| `gravitino.entity.store.versionRetentionCount`     | 保留的实体版本数量，包括当前版本。接受 1 到 10。                                                                                                                                          | `1`                           |

#### 缓存

服务器在内存中缓存实体，以避免在每次请求时读取后端。缓存开启
默认开启，并且以下属性用于调整其保留的内容以及如何进行驱逐。

| 配置项               | 描述                                                                         | 默认值      |
|----------------------------------|-------------------------------------------------------------------------------------|--------------------|
| `gravitino.cache.enabled`        | 是否缓存实体。                                                   | `true`             |
| `gravitino.cache.implementation` | 缓存实现。使用短名称，而不是完全限定的类名。         | `caffeine`         |
| `gravitino.cache.maxEntries`     | 缓存条目的最大数量。当 `enableWeigher` 为 `true` 时忽略。           | `10000`            |
| `gravitino.cache.expireTimeInMs` | 存活时间（以毫秒为单位），从条目创建时开始计算。                         | `3600000` (1 小时) |
| `gravitino.cache.enableWeigher`  | 是否按权重而不是按条目数进行淘汰。                              | `true`             |
| `gravitino.cache.enableStats`    | 是否每五分钟以 INFO 级别记录命中数、未命中数和加载失败数。 | `false`            |
| `gravitino.cache.lockSegments`   | 用于减少争用的锁段数量。                                  | `16`               |

两个驱逐限制同时适用。存活时间始终适用：一个早于
`expireTimeInMs` 的条目会过期并被异步清理。与此同时，缓存限制其大小
按数量或按权重。在禁用 `enableWeigher` 时，Caffeine 的 W-TinyLFU 策略会驱逐
最少使用的条目，一旦达到 `maxEntries`。在启用 `enableWeigher` 时，每个实体类型
具有相应的权重，层级较高的实体权重更大，并且驱逐以总权重
预算为目标；`maxEntries` 会被忽略，并且重于整个预算的单个条目永远不会被
缓存。

#### 变更日志传播

缓存是每个服务器本地的，因此在一个服务器上修改的 metalake 否则会在
它的相邻服务器上保持过期状态。每个服务器将其更改写入实体变更日志表并轮询该表
以使其他服务器触及的内容失效。一个单独的清理器会修剪旧行。

| 配置项                              | 描述                                                                                                                                         | 默认值       |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| `gravitino.entityChangeLog.pollIntervalSecs`    | 轮询之间的间隔时间（以秒为单位）。必须为正数。                                                                                                | `3`                 |
| `gravitino.entityChangeLog.retentionSecs`       | 变更日志行的保留时间（以秒为单位），以数据库时间衡量。`0` 禁用清理；否则至少使用 `pollIntervalSecs` 的十倍。 | `2592000`（30天） |
| `gravitino.entityChangeLog.cleanupIntervalSecs` | 清理器运行之间的间隔时间（以秒为单位）。必须为正数。                                                                                         | `86400`（1天）     |

#### 树锁

Gravitino 使用内存树锁串行化冲突的元数据操作。它是唯一的
可用的锁实现，并且它是每个服务器独立的。

| 配置项                               | 描述                                                 | 默认值         |
|--------------------------------------|------------------------------------------------------|---------------|
| `gravitino.lock.maxNodes`            | 内存中保留的最大树锁节点数。              | `100000`      |
| `gravitino.lock.minNodes`            | 内存中保留的最小树锁节点数。              | `1000`        |
| `gravitino.lock.cleanIntervalInSecs` | 回收过期锁节点的时间间隔（秒）。 | `60`          |

### 加载目录

这些属性控制服务器如何加载和隔离 catalog。配置
单个 catalog 的属性在 [Catalog Properties](#catalog-properties) 中介绍。

下方的 `credential.backfillToProperties` 是针对无法使用
分发凭据的连接器的逃生舱；它所退出的机制在
[凭据分发](security/credential-vending.md) 中有描述。

| 配置项                                  | 描述                                                                                                                                                                                                                                                                                            | 默认值 |
|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.catalog.cache.evictionIntervalMs`        | 空闲 catalog 从 catalog 缓存中被驱逐前的时间间隔（以毫秒为单位）。                                                                                                                                                                                                                     | `3600000`     |
| `gravitino.catalog.classloader.isolated`            | 是否在隔离的 classloader 中加载每个 catalog 的库和配置，而不是在应用程序 classloader 中加载。                                                                                                                                                                         | `true`        |
| `gravitino.catalog.classloader.sharing.enabled`     | 隔离相关属性匹配的 catalog 是否可以共享同一个 classloader。共享可以减少 Metaspace 的使用；禁用此选项会使每个 catalog 都拥有独立的 classloader。                                                                                                                                       | `true`        |
| `gravitino.catalog.credential.backfillToProperties` | 对于无法使用 vended credentials 的连接器，是否在 catalog 属性响应中返回隐藏的 catalog 凭证（如 `jdbc-password`）。任何能够读取 catalog 属性的人都可以读取这些凭证。一旦你的连接器升级，请将其关闭。                 | `false`       |

### 保护服务器

#### 身份验证

身份验证决定调用者是谁。默认情况下它是关闭的：未配置的服务器会信任
客户端发送的任何用户名。

| 配置项         | 描述                                                                                                    | 默认值 |
|----------------------------|----------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.authenticators` | 以逗号分隔的要启用的认证器。有效值为 `simple`、`oauth`、`kerberos`、`basic` 和 `none`。 | `simple`      |

命名认证器只需一行；配置它则不然。每个值都会读取其自身的
`gravitino.authenticator.*` 属性族，详见
[如何认证](security/how-to-authenticate.md)。若要将用户、密码哈希和组
成员资格保存在 Gravitino 自身的关系存储中，而不是外部提供者中，请参阅
[本地用户和组](security/local-users-and-groups.md)。

`gravitino.authenticator`（单数形式）是一个已弃用的拼写，但仍然有效。

#### 授权

授权决定经过身份验证的调用方可以做什么。它默认也是关闭的，并且开启
它需要指定服务管理员，因为该属性本身没有默认值。

| 配置项                       | 描述                                                                                | 默认值                                                         |
|------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `gravitino.authorization.enable`         | 是否对元数据操作强制执行权限。                                      | `false`                                                               |
| `gravitino.authorization.serviceAdmins`  | 以逗号分隔的管理该服务的用户。Metalake 的创建仅限这些用户。 | (none)                                                                |
| `gravitino.authorization.impl`           | 授权器实现。                                                                 | `org.apache.gravitino.server.authorization.jcasbin.JcasbinAuthorizer` |
| `gravitino.authorization.threadPoolSize` | 用于授权检查的线程。                                                      | `100`                                                                 |

这些属性开启的权限模型、角色、授权、所有权，以及
默认授权器的 `gravitino.authorization.jcasbin.*` 调优，描述于
[Access Control](security/access-control.md)。要将强制执行下推到底层系统中
通过 Apache Ranger 或原生权限模型，请参见
[Authorization Pushdown](security/authorization-pushdown.md)。

#### 远程文件获取

服务器在两种情况下通过 URI 获取文件：暂存作业文件，以及加载目录文件
例如 Kerberos keytab。两者都接受远程 URI，因此两者都是一条路径，使得能够
创建目录或提交作业的调用者可以让服务器自行发出请求。

| 配置项                         | 描述                                                                                                   | 默认值 |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.fetchFile.blockUnsafeRemoteUri` | 是否拒绝解析为不安全地址的远程 URI。仅对需要它们的受信任 URI 禁用。 | `true`        |

#### 审计日志

审计日志框架分为两部分。格式化器将 `Event` 转换为 `AuditLog`，而
写入器将该 `AuditLog` 放置到某处。两者都是接口，因此具有自身日志
管线的部署可以替换其中任意一个。

| 配置项                    | 描述                    | 默认值                                     |
|---------------------------------------|--------------------------------|---------------------------------------------------|
| `gravitino.audit.enabled`             | 是否写入审计日志。 | `false`                                           |
| `gravitino.audit.formatter.className` | 格式化器类名。          | `org.apache.gravitino.audit.v2.SimpleFormatterV2` |
| `gravitino.audit.writer.className`    | 写入器类名。             | `org.apache.gravitino.audit.FileAuditWriter`      |

`SimpleFormatterV2` 是默认的格式化器。`JsonAuditFormatter` 可用于需要结构化
输出的场景：它每行输出一个 JSON 对象，序列化 `customInfo`，并写入时间戳
格式为 ISO 8601，具有毫秒精度和时区偏移。

`customInfo` always includes the request's query parameters, captured automatically for every
event — not just the ones an operation dispatcher explicitly reports. For example, a listing
endpoint's `?details=true` shows up in the audit entry for that request even though no dispatcher
code added it. Both formatters redact a `customInfo` value, replacing it with `***`, when its key
either exactly matches `authorization`, `cookie`, `x-amz-security-token`, `s3.access-key-id`, or
`jdbc-password`, or contains (case-insensitively) `password`, `secret`, `token`, `credential`,
`apikey`, `accesskey`, `privatekey`, `auth`, or `signature` — so a caller-named parameter like
`?token=...` or `?myApiKey=...` is masked even though its exact name was never enumerated. A short,
fixed list of keys the server itself always uses (e.g. `http.method`, `http.status`, `auth.method`)
is exempt from that substring check, since otherwise `auth.method` would be masked for merely
containing "auth".

每个到达服务器的请求都会产生至少一个审计条目，即使是其操作
没有专用 `Event` 子类的请求：`HttpAuditFilter` 会分发一个通用的回退事件（方法，
URI、状态码，以及相同的自动捕获的查询参数），用于任何没有
触发操作层事件的请求。在一个收到大量原本未审计的调用发往
相同端点的服务器上——例如 Iceberg REST 目录的 `/v1/config`，一些客户端会轮询
频繁——这会显著增加审计日志的量；请相应地在
`conf/log4j2.properties`（下文）中调整日志轮转和保留的大小。

`FileAuditWriter` 是默认的写入器，它本身不管理任何文件。轮转、压缩和
保留策略通过名为 `gravitino.audit` 的记录器委托给 Log4j2，该记录器由
`conf/log4j2.properties` 中的 `audit_file` appender 组进行配置。开箱即用时，它会将
内容写入日志目录下的 `gravitino_audit.log`，每天以及在达到 256 MB 时进行轮转，对轮转的文件进行 gzip 压缩，
并删除 30 天前的任何内容。请在此处更改路径或保留策略：

```properties
# conf/log4j2.properties
appender.audit_file.fileName    = /var/log/gravitino/my_audit.log
appender.audit_file.filePattern = /var/log/gravitino/my_audit_%d{yyyyMMdd}.%i.log.gz

appender.audit_file.strategy.delete.ifAll.ifLastModified.age = 90d
```

早期版本直接通过 `gravitino.audit.writer.file.*` 配置写入器。这些
属性现在不起作用，并且 `FileAuditWriter` 在启动时如果发现其中任何一个，会记录一条警告。

| 已移除的属性                                | 改为在 `conf/log4j2.properties` 中配置                     |
|-------------------------------------------------|-------------------------------------------------------------------|
| `gravitino.audit.writer.file.fileName`          | `appender.audit_file.fileName`                                    |
| `gravitino.audit.writer.file.append`            | `appender.audit_file.append`                                      |
| `gravitino.audit.writer.file.flushIntervalSecs` | `immediateFlush` 在 appender 上，或将其包装在异步 appender 中 |

### 扩展服务器

#### 事件监听器

事件监听器接收 Gravitino 发出的关于元数据操作的事件，这就是
外部系统无需轮询即可观察目录的方式。要使用它，请实现
`EventListenerPlugin`，将 jar 包放在服务器 classpath 上，并在 `gravitino.conf` 中为其命名。

| 配置项                     | 描述                                                                            | 默认值 |
|----------------------------------------|----------------------------------------------------------------------------------------|---------------|
| `gravitino.eventListener.names`        | 逗号分隔的监听器名称，例如 `audit,sync`。                                    | (空)       |
| `gravitino.eventListener.{name}.class` | 在 `{name}` 下注册的监听器的类名。                                  | (无)        |
| `gravitino.eventListener.{name}.{key}` | 监听器名称下的任何其他属性都将原样传递给该插件。 | (无)        |

`names` 中的每个名称都需要一个匹配的 `{name}.class`，否则服务器将无法构建该监听器。

Each operation emits up to three events: a pre-event before it runs, a post-event after it
succeeds, and a failure event after it throws. The names follow the operation, so `createTable`
produces `CreateTablePreEvent`, `CreateTableEvent`, and `CreateTableFailureEvent`. Operations
served by the Gravitino IRC endpoint carry an `Iceberg` prefix, as in `IcebergCreateTableEvent`.
Not every operation defines all three. The full set of classes lives in the
[`org.apache.gravitino.listener.api.event`](https://github.com/apache/gravitino/tree/main/core/src/main/java/org/apache/gravitino/listener/api/event)
package.

从预事件处理器中抛出 `ForbiddenException` 会在操作运行之前将其停止，这
使得预事件成为否决点而非通知。

每个事件上的 `customInfo()` 包含请求的查询参数，并且自定义监听器
接收它们时是**未脱敏的** —— 上面 "Audit Logging" 下描述的掩码仅由
两个内置的审计日志格式化程序在格式化时应用，而不是应用于事件对象本身。一个
将 `customInfo()` 转发到其他地方（日志、指标管道、下游服务）的监听器，如果
这对其目标位置很重要，则负责其自身的脱敏。

插件声明其事件是如何分发的：

| 模式             | 行为                                                                                                                         |
|------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `SYNC`           | 内联处理，在操作结果到达客户端之前。慢速监听器会拖慢请求。                           |
| `ASYNC_SHARED`   | 在与其他监听器共享的队列和调度器上处理。一个慢速监听器会拖累其余监听器，并且事件可能会被丢弃。 |
| `ASYNC_ISOLATED` | 在其专属的队列和调度器上处理。隔离性更好，代价是每个监听器需要一个队列和线程。                |

#### 辅助服务

辅助服务在 Gravitino 服务器进程内运行，使用其自己的端口。该属性没有
默认值，但发行版中附带的 `gravitino.conf` 将其设置为
`iceberg-rest,lance-rest`，因此除非您更改该行，否则两者都会启动。

| 配置项           | 描述                                                                                                                  | 默认值 |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.auxService.names` | 要启动的逗号分隔的辅助服务。`iceberg-rest` 是 Gravitino IRC 服务器，`lance-rest` 是 Lance REST 服务器。 | (empty)       |

其余的 IRC 配置，以及 Lance REST 的 `gravitino.lance-rest.*` 属性
服务器，均在这些服务中进行了文档说明。请参见
[Iceberg REST 目录服务](iceberg-rest-service.md).

#### 作业

| 配置项                     | 描述                                                                                                | 默认值                 |
|----------------------------------------|------------------------------------------------------------------------------------------------------------|-------------------------------|
| `gravitino.job.executor`               | 运行作业的执行器。实现你自己的执行器并在此命名，以替换内置执行器。                  | `local`                       |
| `gravitino.job.stagingDir`             | 存放用于运行作业的暂存文件的目录。                                                          | `/tmp/gravitino/jobs/staging` |
| `gravitino.job.stagingDirKeepTimeInMs` | 已完成作业的暂存文件保留的时长（以毫秒为单位）。在非测试环境下至少使用 10 分钟。 | `604800000` (7 days)          |
| `gravitino.job.statusPullIntervalInMs` | 轮询作业状态的时间间隔（以毫秒为单位）。在非测试环境下至少使用 1 分钟。                  | `300000` (5 minutes)          |

### 密钥管理

服务器与您在 `gravitino.conf` 中命名的 KMS 实例进行通信。每个名称都是一个已配置的
实例。要添加一个实例，请实现带有公共无参构造函数的 `KmsClientFactory`，将该 jar 放在
服务器 classpath 上，并将 `gravitino.kms.provider.<name>.className` 设置为该类。
`create(provider, properties)` 构建该名称的 `KmsClient`。Gravitino 不附带 AWS 或
Azure 工厂。两个名称可以共享一个类，这就是您运行多个同一类型的 vault 的
方式。

默认情况下该列表为空，此时服务器没有 KMS 客户端。命名一个没有
`className`，或者服务器无法将其构造为 `KmsClientFactory` 的类，会导致启动失败。
客户端构造仅验证本地配置；对提供程序的第一次调用是稍后的
密钥检查，而不是启动。

| 配置项                         | 描述                                                                                                                                                          | 默认值 |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.kms.providers`                  | 逗号分隔的 KMS 实例名称，逗号后无空格。每个名称必须匹配 `[A-Za-z0-9][A-Za-z0-9_-]*` 且不能包含 `.`。重复项会导致启动失败。 | (空)       |
| `gravitino.kms.provider.<name>.className`  | 该实例所需的工厂类名。该类必须具有无参构造函数并实现 `KmsClientFactory`。                                          | (无)        |
| `gravitino.kms.provider.<name>.<key>`      | 该名称下的任何其他属性都将传递给该工厂。`<key>` 中允许嵌套点，例如 `endpoint.region`。                                           | (无)        |

`providers` 中的每个名称都需要一个匹配的 `.className`。一个 `gravitino.kms.provider.<name>.*` 键
针对不在列表中的名称，或任何其他 `gravitino.kms.*` 键，会导致启动失败。

调用者为实例和键命名。他们不发送 `className`。服务器已经构建了
启动时用于 `aws-prod` 的工厂。

```text
# conf/gravitino.conf
gravitino.kms.providers = aws-prod,aws-dr,azure-eu

gravitino.kms.provider.aws-prod.className = com.example.kms.AwsCustomKmsClientFactory
gravitino.kms.provider.aws-dr.className = com.example.kms.AwsCustomKmsClientFactory
gravitino.kms.provider.azure-eu.className = com.example.kms.AzureCustomKmsClientFactory
```

该配置构建了三个客户端：一个自定义 AWS 工厂的两个实例以及一个自定义
Azure 工厂。此外，`gravitino.kms.provider.<name>.*` 键是工厂属性，而不是一个封闭的
模式；每个工厂都记录了其接受的键。

## 目录属性

Catalog 属性配置单个 catalog 而不是服务器。它们来自两个地方：一个
catalog 配置文件为该提供程序的每个 catalog 提供默认值，以及
创建 catalog 请求上的 `properties` 字段仅为该 catalog 提供值。该请求
胜出。两者都不影响 schema 或表属性。

catalog 属性是三种类型之一。Gravitino 自身定义了一些，作为 catalog 的设置
正常工作所需的。任何以 `gravitino.bypass.` 为前缀的内容都会直接传递给底层
系统且保持不变。其他任何内容，Gravitino 只是简单地为您存储，供您随意使用。

通过 `gravitino.bypass.` 传递凭证、令牌或访问密钥会将其暴露：被绕过的
属性不受 Gravitino 管理，并且可能会从 REST API 以明文形式返回。如果
底层系统没有其他选择，请相应地限制对 catalog API 的访问。

这些属性适用于每个目录：

| 配置项  | 描述                                                                                                                                            | 默认值 |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `package`           | catalog 包的路径，Gravitino 从中加载 catalog 的库和配置。它包含一个 `conf` 目录和一个 `libs` 目录。 | (none)        |
| `cloud.name`        | catalog 运行所在的云。`aws`、`azure`、`gcp`、`on_premise` 或 `other` 之一。                                                                     | (none)        |
| `cloud.region-code` | 该云内的区域代码。                                                                                                                         | (none)        |

其他一切都取决于提供程序。服务器会将下面的每个配置目录添加到
classpath 中，这也是放置 `hdfs-site.xml` 等特定于提供程序的文件的地方。

| 目录提供者    | 目录属性                                                                      | 配置文件路径                                  |
|---------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------|
| `hive`              | [Hive 目录属性](apache-hive-catalog.md#catalog-properties)                    | `catalogs/hive/conf/hive.conf`                           |
| `glue`              | [AWS Glue 目录属性](aws-glue-catalog.md#catalog-properties)                   | `catalogs/glue/conf/glue.conf`                           |
| `lakehouse-iceberg` | [Lakehouse Iceberg 目录属性](lakehouse-iceberg-catalog.md#catalog-properties) | `catalogs/lakehouse-iceberg/conf/lakehouse-iceberg.conf` |
| `lakehouse-paimon`  | [Lakehouse Paimon 目录属性](lakehouse-paimon-catalog.md#catalog-properties)   | `catalogs/lakehouse-paimon/conf/lakehouse-paimon.conf`   |
| `lakehouse-hudi`    | [Lakehouse Hudi 目录属性](lakehouse-hudi-catalog.md#catalog-properties)       | `catalogs/lakehouse-hudi/conf/lakehouse-hudi.conf`       |
| `lakehouse-generic` | [Lakehouse Generic 目录属性](lakehouse-generic-catalog.md#catalog-properties) | `catalogs/lakehouse-generic/conf/lakehouse-generic.conf` |
| `jdbc-mysql`        | [MySQL 目录属性](jdbc-mysql-catalog.md#catalog-properties)                    | `catalogs/jdbc-mysql/conf/jdbc-mysql.conf`               |
| `jdbc-postgresql`   | [PostgreSQL 目录属性](jdbc-postgresql-catalog.md#catalog-properties)          | `catalogs/jdbc-postgresql/conf/jdbc-postgresql.conf`     |
| `jdbc-doris`        | [Doris 目录属性](jdbc-doris-catalog.md#catalog-properties)                    | `catalogs/jdbc-doris/conf/jdbc-doris.conf`               |
| `jdbc-starrocks`    | [StarRocks 目录属性](jdbc-starrocks-catalog.md#catalog-properties)            | `catalogs/jdbc-starrocks/conf/jdbc-starrocks.conf`       |
| `jdbc-clickhouse` ‡ | [ClickHouse 目录属性](jdbc-clickhouse-catalog.md#catalog-properties)          | `catalogs/jdbc-clickhouse/conf/jdbc-clickhouse.conf`     |
| `jdbc-hologres` ‡   | [Hologres 目录属性](jdbc-hologres-catalog.md#catalog-properties)              | `catalogs/jdbc-hologres/conf/jdbc-hologres.conf`         |
| `jdbc-oceanbase` ‡  | [OceanBase 目录属性](jdbc-oceanbase-catalog.md#catalog-properties)            | `catalogs/jdbc-oceanbase/conf/jdbc-oceanbase.conf`       |
| `kafka`             | [Kafka 目录属性](kafka-catalog.md#catalog-properties)                         | `catalogs/kafka/conf/kafka.conf`                         |
| `fileset`           | [Fileset 目录属性](fileset-catalog.md#catalog-properties)                     | `catalogs/fileset/conf/fileset.conf`                     |
| `model`             | [Model 目录属性](model-catalog.md#catalog-properties)                         | `catalogs/model/conf/model.conf`                         |

‡ 贡献的目录，仅在 `-all` 发行包中提供。标准包
不包含它们的目录。

## 容器配置

```shell
docker run --rm -d -p 8090:8090 apache/gravitino:{tag}
```

### 容器如何构建其配置

容器入口点在 JVM 启动之前重写 `conf/gravitino.conf`。它分两
步执行。首先，它会无条件地将其自身的默认值覆盖到它知道默认值的每个属性上，
丢弃文件中原有的任何内容。然后，它会应用每个受支持的、已设置的
环境变量。结果将被写回并覆盖原始文件。

值得牢记的两个后果。你写入 `conf/gravitino.conf` 的属性只有在
容器没有为其设置默认值时才能保留，因此像挂载文件中自定义的 `httpPort` 这样的值会被
静默替换。而且容器的默认值并非服务器的默认值：容器将
`minThreads` 固定为 24，`maxThreads` 固定为 200，而在容器外启动的服务器会基于
处理器数量计算这两个值。

设置 `SKIP_CONFIG_REWRITE=true` 以禁用两轮处理，并完全按照
所写的内容运行配置文件。当文件来自 Kubernetes ConfigMap 时，请使用此设置。

### 支持的环境变量

入口点识别以下变量并忽略所有其他 `GRAVITINO_` 变量。该
Container Default 列给出了当变量未设置时首次处理写入的值；`(none)`
表示该属性保持原样。

| 环境变量                                     | 配置键                                    | 容器默认值                                    |
|----------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| `GRAVITINO_SERVER_SHUTDOWN_TIMEOUT`                      | `gravitino.server.shutdown.timeout`                  | `3000`                                               |
| `GRAVITINO_SERVER_WEBSERVER_HOST`                        | `gravitino.server.webserver.host`                    | `0.0.0.0`                                            |
| `GRAVITINO_SERVER_WEBSERVER_HTTP_PORT`                   | `gravitino.server.webserver.httpPort`                | `8090`                                               |
| `GRAVITINO_SERVER_WEBSERVER_MIN_THREADS`                 | `gravitino.server.webserver.minThreads`              | `24`                                                 |
| `GRAVITINO_SERVER_WEBSERVER_MAX_THREADS`                 | `gravitino.server.webserver.maxThreads`              | `200`                                                |
| `GRAVITINO_SERVER_WEBSERVER_STOP_TIMEOUT`                | `gravitino.server.webserver.stopTimeout`             | `30000`                                              |
| `GRAVITINO_SERVER_WEBSERVER_IDLE_TIMEOUT`                | `gravitino.server.webserver.idleTimeout`             | `30000`                                              |
| `GRAVITINO_SERVER_WEBSERVER_THREAD_POOL_WORK_QUEUE_SIZE` | `gravitino.server.webserver.threadPoolWorkQueueSize` | `100`                                                |
| `GRAVITINO_SERVER_WEBSERVER_REQUEST_HEADER_SIZE`         | `gravitino.server.webserver.requestHeaderSize`       | `131072`                                             |
| `GRAVITINO_SERVER_WEBSERVER_RESPONSE_HEADER_SIZE`        | `gravitino.server.webserver.responseHeaderSize`      | `131072`                                             |
| `GRAVITINO_SERVER_BULK_MAX_ITEMS`                        | `gravitino.server.bulk.maxItems`                     | `100`                                                |
| `GRAVITINO_SERVER_WEBSERVER_INCLUDE_ERROR_STACK_TRACE`    | `gravitino.server.webserver.includeErrorStackTrace`  | `true`                                               |
| `GRAVITINO_ENTITY_STORE`                                 | `gravitino.entity.store`                             | `relational`                                         |
| `GRAVITINO_ENTITY_STORE_RELATIONAL`                      | `gravitino.entity.store.relational`                  | `JDBCBackend`                                        |
| `GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_URL`             | `gravitino.entity.store.relational.jdbcUrl`          | `jdbc:h2`                                            |
| `GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_DRIVER`          | `gravitino.entity.store.relational.jdbcDriver`       | `org.h2.Driver`                                      |
| `GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_USER`            | `gravitino.entity.store.relational.jdbcUser`         | `gravitino`                                          |
| `GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_PASSWORD`        | `gravitino.entity.store.relational.jdbcPassword`     | `gravitino`                                          |
| `GRAVITINO_CATALOG_CACHE_EVICTION_INTERVAL_MS`           | `gravitino.catalog.cache.evictionIntervalMs`         | `3600000`                                            |
| `GRAVITINO_AUTHORIZATION_ENABLE`                         | `gravitino.authorization.enable`                     | `false`                                              |
| `GRAVITINO_AUTHORIZATION_SERVICE_ADMINS`                 | `gravitino.authorization.serviceAdmins`              | `anonymous`                                          |
| `GRAVITINO_AUX_SERVICE_NAMES`                            | `gravitino.auxService.names`                         | `iceberg-rest`                                       |
| `GRAVITINO_ICEBERG_REST_HOST`                            | `gravitino.iceberg-rest.host`                        | `0.0.0.0`                                            |
| `GRAVITINO_ICEBERG_REST_HTTP_PORT`                       | `gravitino.iceberg-rest.httpPort`                    | `9001`                                               |
| `GRAVITINO_ICEBERG_REST_URI`                             | `gravitino.iceberg-rest.uri`                         | (无)                                               |
| `GRAVITINO_ICEBERG_REST_CLASSPATH`                       | `gravitino.iceberg-rest.classpath`                   | `iceberg-rest-server/libs, iceberg-rest-server/conf` |
| `GRAVITINO_ICEBERG_REST_IO_IMPL`                         | `gravitino.iceberg-rest.io-impl`                     | (无)                                               |
| `GRAVITINO_ICEBERG_REST_CATALOG_BACKEND`                 | `gravitino.iceberg-rest.catalog-backend`             | `memory`                                             |
| `GRAVITINO_ICEBERG_REST_JDBC_DRIVER`                     | `gravitino.iceberg-rest.jdbc-driver`                 | (无)                                               |
| `GRAVITINO_ICEBERG_REST_JDBC_USER`                       | `gravitino.iceberg-rest.jdbc-user`                   | (无)                                               |
| `GRAVITINO_ICEBERG_REST_JDBC_PASSWORD`                   | `gravitino.iceberg-rest.jdbc-password`               | (无)                                               |
| `GRAVITINO_ICEBERG_REST_WAREHOUSE`                       | `gravitino.iceberg-rest.warehouse`                   | `/tmp/`                                              |
| `GRAVITINO_ICEBERG_REST_CREDENTIAL_PROVIDERS`            | `gravitino.iceberg-rest.credential-providers`        | (无)                                               |
| `GRAVITINO_ICEBERG_REST_GCS_SERVICE_ACCOUNT_FILE`        | `gravitino.iceberg-rest.gcs-service-account-file`    | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_ACCESS_KEY`                   | `gravitino.iceberg-rest.s3-access-key-id`            | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_SECRET_KEY`                   | `gravitino.iceberg-rest.s3-secret-access-key`        | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_ENDPOINT`                     | `gravitino.iceberg-rest.s3-endpoint`                 | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_REGION`                       | `gravitino.iceberg-rest.s3-region`                   | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_PATH_STYLE_ACCESS`            | `gravitino.iceberg-rest.s3-path-style-access`        | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_ROLE_ARN`                     | `gravitino.iceberg-rest.s3-role-arn`                 | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_EXTERNAL_ID`                  | `gravitino.iceberg-rest.s3-external-id`              | (无)                                               |
| `GRAVITINO_ICEBERG_REST_S3_TOKEN_SERVICE_ENDPOINT`       | `gravitino.iceberg-rest.s3-token-service-endpoint`   | (无)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_STORAGE_ACCOUNT_NAME`      | `gravitino.iceberg-rest.azure-storage-account-name`  | (无)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_STORAGE_ACCOUNT_KEY`       | `gravitino.iceberg-rest.azure-storage-account-key`   | (无)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_TENANT_ID`                 | `gravitino.iceberg-rest.azure-tenant-id`             | (无)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_CLIENT_ID`                 | `gravitino.iceberg-rest.azure-client-id`             | (无)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_CLIENT_SECRET`             | `gravitino.iceberg-rest.azure-client-secret`         | (无)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_ACCESS_KEY`                  | `gravitino.iceberg-rest.oss-access-key-id`           | (无)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_SECRET_KEY`                  | `gravitino.iceberg-rest.oss-secret-access-key`       | (无)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_ENDPOINT`                    | `gravitino.iceberg-rest.oss-endpoint`                | (无)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_REGION`                      | `gravitino.iceberg-rest.oss-region`                  | (无)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_ROLE_ARN`                    | `gravitino.iceberg-rest.oss-role-arn`                | (无)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_EXTERNAL_ID`                 | `gravitino.iceberg-rest.oss-external-id`             | (无)                                               |

镜像将 MySQL 和 PostgreSQL JDBC 驱动打包在 `jdbc-drivers/` 中，并将它们链接到 `libs/`
和 `iceberg-rest-server/libs/` 中（在启动时）。对于云存储后端，请将匹配的 Iceberg
bundle jars 放入 `iceberg-bundles/` 中，它们将被链接到
`catalogs/lakehouse-iceberg/libs/` 和 `iceberg-rest-server/libs/` 中，方式相同。

### 检查容器做了什么

读回重写后的文件：

```shell
docker exec -it {container_id} cat /opt/gravitino/conf/gravitino.conf
```

然后确认服务器，以及辅助 IRC 服务（如果您启动了的话）：

```shell
curl http://127.0.0.1:8090/health/ready
curl http://127.0.0.1:9001/iceberg/v1/config
```

## 访问 Apache Hadoop

Gravitino 以单一操作系统用户身份访问 Hadoop，因此该用户需要 HDFS 和 YARN
的权限，以涵盖服务器将涉及的所有内容。如果没有这些权限，操作将失败并报
`Permission denied`。要么授予启动服务器的用户所需的权限，要么设置
`HADOOP_USER_NAME` 为一个已经拥有这些权限的用户，在启动前完成此操作。对于本地部署，将其设置
在 `conf/gravitino-env.sh` 中。

## 相关

- [关系型后端存储](how-to-use-relational-backend-storage.md)，用于将实体
存储指向 MySQL 或 PostgreSQL，包括 schema 初始化和驱动安装
- [Iceberg REST Catalog 服务](iceberg-rest-service.md)，用于 `gravitino.iceberg-rest.*`
属性，该属性属于由 `gravitino.auxService.names` 命名的辅助服务
- [如何进行身份验证](security/how-to-authenticate.md)，用于 `gravitino.authenticator.*`
属性，该属性对应于 `gravitino.authenticators` 的每个值
- [本地用户和组](security/local-users-and-groups.md)，用于在 Gravitino 自身的关系型存储中保存用户、密码
哈希和组成员身份
- [访问控制](security/access-control.md)，用于授权器在设置
`gravitino.authorization.enable` 后强制执行的权限模型：角色、授权、所有权和 metalake 管理
- [授权下推](security/authorization-pushdown.md)，用于通过 Apache Ranger 或原生权限模型将这些权限
传播到底层系统中
- [凭证分发](security/credential-vending.md)，用于向引擎颁发临时存储凭证，
而不是分发长期有效的密钥
- [HTTPS](security/how-to-use-https.md)，用于 `gravitino.server.webserver.*` 密钥库、信任
库和客户端证书属性
- [CORS](security/how-to-use-cors.md)，用于允许来自其他源的浏览器客户端调用
API
- [安全](security/how-to-authenticate.md)
