---
slug: /gravitino-server-config
keywords:
- configuration
license: This software is licensed under the Apache License version 2.
---
## 简介

Apache Gravitino 服务器在启动时读取 `conf/gravitino.conf`。几乎每个属性都有一个
默认值，因此服务器可以以一个空文件启动，大多数部署只会更改其中少数几个
属性。例外是 `gravitino.authorization.serviceAdmins`，一旦你打开
授权，就必须设置它。

本页介绍服务器本身。Catalog 属性用于配置单个 catalog
而不是服务器，将在下文介绍。辅助服务的属性随
那些服务一起说明：参见 [Iceberg REST Catalog 服务](iceberg-rest-service.md) 和
[安全](security/how-to-authenticate.md)。

## 快速开始

### 开发

默认值已经适合本地开发。服务器监听 `0.0.0.0:8090`，并将其
元数据保存在嵌入式 H2 数据库中，因此无需任何配置：

```shell
${GRAVITINO_HOME}/bin/gravitino.sh start
```

仍有一个属性值得设置。默认情况下，H2 会将其数据库文件写入
`${GRAVITINO_HOME}/data/jdbc`，该路径位于解压后的发行版内。升级 Gravitino
意味着解压新的发行版，因此元数据正好位于你将要
替换或丢弃的目录中。请将其移动到升级不会触及的位置：

```text
# conf/gravitino.conf
gravitino.entity.store.relational.storagePath = /var/lib/gravitino/data/jdbc
```

这里没有任何身份验证。默认的 `simple` 认证器会接受客户端发送的任何
用户名，服务器使用纯 HTTP，且授权已关闭，因此每个调用者都可以执行
任何操作。再加上 Gravitino 对 H2 不作一致性或持久性保证，
这使得此配置除了本地开发外不适合任何用途。

### 生产环境

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

这里只有 `gravitino.cache.enableStats` 会改变行为；它会每五分钟记录命中次数、未命中次数和加载
失败次数，这正是让缓存问题在生产环境中可见的原因。其上方的三行
重申了默认值，并明确写出，以便缓存配置可以在一处
审查，而不是通过其缺失来推断。如果服务器负载足够高，以致缓存锁争用出现在性能分析中，
请将 `lockSegments` 提高到默认值以上。

此代码块依赖四件事：

**数据库 schema 不会为你创建。** 请初始化它，并将 JDBC 驱动 jar 放入
`${GRAVITINO_HOME}/libs/`，然后再进行首次启动。参见
[关系型后端存储](how-to-use-relational-backend-storage.md)。

**HTTPS 会取代 HTTP，而不是与它并存。** 设置了 `enableHttps` 的服务器不再提供
纯 HTTP，因此客户端和 Web UI 必须改用 `httpsPort`，其默认值为 `8433`。参见
[HTTPS](security/how-to-use-https.md)。

**认证器只有一行，但其提供程序不是。** 上面的代码块根据
JWKS 端点验证 JWT，这是外部身份提供程序的常见情况。静态签名密钥、
Kerberos，以及 Web UI 的 OIDC 登录流程各自需要不同的属性集。参见
[如何认证](security/how-to-authenticate.md)，或
[本地用户和组](security/local-users-and-groups.md)，以将用户和组保存在
Gravitino 自己的元数据存储中，而不是外部提供程序中。

**`gravitino.authorization.serviceAdmins` 没有默认值。** 这是这里唯一一个
Gravitino 不会为你填充的属性，并且在没有它的情况下启用授权会在启动时失败。
这些管理员和其他所有人之后可以做什么，是
[访问控制](security/access-control.md)的主题。

为 JVM 提供超过默认 1 GB 的内存：

```shell
export GRAVITINO_MEM="-Xms4g -Xmx4g -XX:MaxMetaspaceSize=1g"
```

### Docker

Gravitino 镜像并不是简单地根据你提供的配置文件运行服务器。在
启动时，入口点会重写 `conf/gravitino.conf`，将其自身的默认值应用于大约二
十几个属性，然后应用任何受支持的环境变量。请通过环境变量配置
容器：

```shell
docker run --rm -d \
  -p 8090:8090 \
  -e GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_URL="jdbc:postgresql://{db_host}:5432/{database}" \
  -e GRAVITINO_ENTITY_STORE_RELATIONAL_JDBC_DRIVER="org.postgresql.Driver" \
  apache/gravitino:{tag}
```

若要改为提供配置文件，例如来自 Kubernetes ConfigMap，请禁用
重写，使用 `SKIP_CONFIG_REWRITE=true`。参见
[容器配置](#容器配置)，了解重写会做什么以及识别哪些变量
。

### 运行多个服务器

负载均衡器后面的服务器共享实体存储，但保留本地缓存。每个服务器轮询
实体变更日志，并使另一个服务器已修改的条目失效。默认值是安全的：
三秒轮询间隔，并且无法保持缓存最新的服务器会退出，而不是提供
它已知过期的元数据。将负载均衡器的健康检查指向 `GET /health/ready`，这样
已丢失数据库连接的服务器就会停止接收流量。

## 服务器配置

本节中的每个属性都应放在 `${GRAVITINO_HOME}/conf/gravitino.conf` 中，每行一个
`property = value` 对。服务器在启动时读取该文件一次，因此更改
会在下次重启时生效。默认值为 `(empty)` 表示该属性存在，其值为
空字符串或空列表；`(none)` 表示它完全没有默认值。

### 处理请求

#### HTTP 服务器

| 配置项 | 描述 | 默认值 |
|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| `gravitino.server.webserver.host`                    | 服务器绑定的地址。                                                                                                                                                             | `0.0.0.0`                               |
| `gravitino.server.webserver.httpPort`                | 服务器监听的端口。                                                                                                                                                              | `8090`                                  |
| `gravitino.server.webserver.minThreads`              | Jetty 线程池中的最小线程数。低于 8 的值会提高到 8。                                                                                                                    | 处理器数量的两倍，8 到 100     |
| `gravitino.server.webserver.maxThreads`              | Jetty 线程池中的最大线程数。低于 8 的值会提高到 8，且该值必须至少为 `minThreads`。                                                                       | 处理器数量的四倍，最小 400 |
| `gravitino.server.webserver.threadPoolWorkQueueSize` | Jetty 线程池工作队列的大小。                                                                                                                                                    | `100`                                   |
| `gravitino.server.webserver.idleTimeout`             | 空闲连接的超时时间（毫秒）。                                                                                                                                                | `30000`                                 |
| `gravitino.server.webserver.stopTimeout`             | Jetty 等待优雅关闭的时间（毫秒）。参见 `org.eclipse.jetty.server.Server#setStopTimeout`。                                                                              | `30000`                                 |
| `gravitino.server.shutdown.timeout`                  | Gravitino 服务器自身优雅关闭的时间（毫秒）。                                                                                                                | `3000`                                  |
| `gravitino.server.webserver.requestHeaderSize`       | HTTP 请求头的最大大小（字节）。                                                                                                                                             | `131072`                                |
| `gravitino.server.webserver.responseHeaderSize`      | HTTP 响应头的最大大小（字节）。                                                                                                                                            | `131072`                                |
| `gravitino.server.webserver.customFilters`           | 要应用于 API 的 servlet 过滤器类名的逗号分隔列表。                                                                                                                      | (empty)                                 |
| `gravitino.server.rest.extensionPackages`            | 要扫描以查找额外 REST 资源的包的逗号分隔列表。                                                                                                                      | (empty)                                 |
| `gravitino.server.visibleConfigs`                    | 要在未认证的 `GET /configs` 端点上公开的额外属性的逗号分隔列表，在其始终返回的固定集合之上。该列表是累加的，因此每个条目都会扩大公开范围。 | (empty)                                 |
| `gravitino.server.bulk.maxItems`                     | 单个批量请求中允许的最大项目数。                                                                                                                                    | `100`                                   |
| `gravitino.server.webserver.includeErrorStackTrace`  | HTTP 错误响应是否包含服务器端堆栈跟踪。在新部署中将其设置为 `false`，因为响应可能会暴露内部实现细节。默认仍为 `true`，只是为了避免破坏期望 `stack` 字段的旧客户端。参见 [OWASP REST 安全：错误处理](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html#error-handling) 和 [CWE-209](https://cwe.mitre.org/data/definitions/209.html)。 | `true`                                  |

`customFilters` 中指定的过滤器必须是标准的 `javax.servlet` 过滤器。使用以下形式的属性向
过滤器传递参数，属性形式为
`gravitino.server.webserver.{filter_class_name}.param.{param_name} = {value}`。

`GET /configs` 为 Web UI 提供支持，因此它无需身份验证即可应答，并始终返回
`gravitino.authenticators`、`gravitino.authorization.enable` 和 `gravitino.schema.separator`。
当 `oauth` 是认证器之一时，它会添加 OAuth 客户端设置。请将你通过 `visibleConfigs` 添加的任何内容
视为公开内容，并且只添加客户端在能够进行身份验证之前需要的属性
。

另外两组 `gravitino.server.webserver.*` 属性记录在其他地方，因为
它们属于功能特性，而不是 Web 服务器本身。TLS、密钥库、信任库和
客户端证书认证位于 [HTTPS](security/how-to-use-https.md)。CORS 过滤器
及其允许的来源、方法和标头，在浏览器客户端运行于与服务器不同的
来源时需要这些配置，位于 [CORS](security/how-to-use-cors.md)。

#### Schema 名称

支持分层 schema 的 catalog 会在 API 边界处将层次结构公开为单个带分隔符的名称
。在内部，各层级使用 ASCII-1 作为物理分隔符存储，因此
配置的分隔符只是一种外部表示，它既不能为空，也不能为
`.`，也不能为 ASCII-1。

| 配置项 | 描述 | 默认值 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.schema.separator` | 在 API 边界处表示多级 schema 名称的分隔符，如 `A:B:C`。参见 [分层 schema](lakehouse-iceberg-catalog.md#hierarchical-schema)。 | `:`           |

#### 健康检查端点

Gravitino 按照
[MicroProfile Health](https://microprofile.io/project/eclipse/microprofile-health) 语义公开三个健康端点。所有
端点都免于身份验证，因此 Kubernetes 探针、负载均衡器和流量管理器
无需凭据即可访问它们。

| 端点 | 根别名 | 描述 | HTTP 状态 |
|-------------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| `GET /api/health/live`  | `GET /health/live`  | 存活检查。如果 HTTP 线程能够响应且未观察到 OOM，则返回 200；否则返回 503。用它来决定是否重启 pod。         | 200 或 503  |
| `GET /api/health/ready` | `GET /health/ready` | 就绪检查。当未观察到 OOM 且实体存储在探测超时内响应时，返回 200；否则返回 503。用它来路由流量。 | 200 或 503  |
| `GET /api/health`       | `GET /health`       | 聚合检查。当上述两项都通过时返回 200。也作为 `GET /health.html` 的别名。                                                             | 200 或 503  |

| 配置项 | 描述 | 默认值 |
|------------------------------------------------------|---------------------------------------------------------------------|---------------|
| `gravitino.server.health.entityStore.probeTimeoutMs` | `/ready` 背后实体存储探测的超时时间（毫秒）。 | `2000`        |

每个端点返回相同的 JSON 结构，但检查项不同。`code` 始终为 `0`，
`status` 为 `up` 或 `down`，`checks` 为每个探测的组件携带一个条目。`/live` 仅报告
`httpServer`，`/ready` 仅报告 `entityStore`，而聚合端点报告两者，
前提是未观察到 OOM：

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

失败的 `entityStore` 检查会报告 `timeout`、`interrupted`、`probe-rejected`、
`entity store not initialized`，或意外异常的简单类名。

在观察到 `OutOfMemoryError`（包括 Metaspace OOM）之后，所有三个端点及其根
别名都会返回 503，并带有单个 `jvm: down` 检查以及原因 `OutOfMemoryError; restart required`。
此状态会持续到进程重启；成功的请求不会重置它。参见
[内存不足故障](./health-and-readiness.md#out-of-memory-failures)了解检测范围。

#### JVM 内存

`GRAVITINO_MEM` 设置堆和元空间标志。启动脚本会将它追加到 `JAVA_OPTS`，并且
Iceberg REST 服务器和 Lance REST 服务器启动器会读取同一变量。请在
`conf/gravitino-env.sh` 中或启动服务器之前在环境中设置它。

默认值来自 `bin/common.sh`，为 `-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m`。请根据
catalog 数量、插件数量和查询并发量相应提高它：`-Xms4g -Xmx4g`
-XX:MaxMetaspaceSize=1g` 适合中等规模的生产服务器，而更大的部署则需要超过该值。

#### 指标

| 配置项 | 描述 | 默认值 |
|-------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.metrics.timeSlidingWindowSecs` | 已弃用，不再使用。持续时长计时器和直方图现在使用指数衰减蓄水池，而不是固定时间窗口，因此不常调用的操作会在长得多的时间内（大约半天）持续报告真实时长，而不是在 60 秒无活动后读数为零。空闲时间超过该时长的操作最终仍会报告持续时间为零。 | `60` |

### 存储元数据

#### 存储后端

Gravitino 通过 JDBC 存储元数据。H2 是默认值，因为它是嵌入式的，不需要任何
外部依赖，这使它适合本地开发，但不适合其他任何用途：Gravitino 对
存储在 H2 中的元数据不提供一致性或持久性保证。生产部署使用 MySQL 或
PostgreSQL，两者的设置过程见
[关系型后端存储](how-to-use-relational-backend-storage.md)。

只要 URL 不是 `jdbc:h2`，驱动、用户和密码属性就是必需的。

| 配置项 | 描述 | 默认值 |
|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| `gravitino.entity.store` | 实体存储实现。`relational` 是唯一支持的值。 | `relational` |
| `gravitino.entity.store.relational` | 关系型存储实现。`JDBCBackend` 是唯一支持的值，它涵盖 H2、MySQL 和 PostgreSQL。 | `JDBCBackend` |
| `gravitino.entity.store.relational.jdbcUrl` | 后端连接的数据库 URL。 | `jdbc:h2` |
| `gravitino.entity.store.relational.jdbcDriver` | 驱动类名。将驱动 jar 放在 `${GRAVITINO_HOME}/libs/` 中。 | `org.h2.Driver` |
| `gravitino.entity.store.relational.jdbcUser` | 数据库用户名。 | `gravitino` |
| `gravitino.entity.store.relational.jdbcPassword` | 数据库密码。 | `gravitino` |
| `gravitino.entity.store.relational.storagePath` | 嵌入式 H2 保存其文件的位置。相对值将相对于 `${GRAVITINO_HOME}` 解析。默认值位于部署目录内，因此替换该目录的升级会丢弃数据。请更改它。 | `${GRAVITINO_HOME}/data/jdbc` |
| `gravitino.entity.store.relational.maxConnections` | JDBC 连接池的最大大小。 | `100` |
| `gravitino.entity.store.relational.maxWaitMillis` | 从连接池获取连接的最大等待时间（毫秒）。 | `1000` |
| `gravitino.entity.store.maxTransactionSkewTimeMs` | 最大事务偏斜时间（毫秒）。 | `2000` |
| `gravitino.entity.store.deleteAfterTimeMs` | 已删除和被取代的行保留多长时间（毫秒）。接受 10 分钟到 30 天。 | `604800000`（7 天） |
| `gravitino.entity.store.versionRetentionCount` | 保留的实体版本数量，包括当前版本。接受 1 到 10。 | `1` |

#### 缓存

服务器将实体缓存在内存中，以避免每次请求都读取后端。缓存默认开启，
下面的属性用于调整它保存什么以及如何驱逐。

| 配置项 | 描述 | 默认值 |
|----------------------------------|-------------------------------------------------------------------------------------|--------------------|
| `gravitino.cache.enabled` | 是否缓存实体。 | `true` |
| `gravitino.cache.implementation` | 缓存实现。使用短名称，而不是完全限定类名。 | `caffeine` |
| `gravitino.cache.maxEntries` | 缓存条目的最大数量。当 `enableWeigher` 为 `true` 时忽略。 | `10000` |
| `gravitino.cache.expireTimeInMs` | 生存时间（毫秒），从条目创建时开始计算。 | `3600000`（1 小时） |
| `gravitino.cache.enableWeigher` | 是否按权重而不是按条目数量进行驱逐。 | `true` |
| `gravitino.cache.enableStats` | 是否每五分钟以 INFO 级别记录命中数、未命中数和加载失败数。 | `false` |
| `gravitino.cache.lockSegments` | 用于减少争用的锁分段数量。 | `16` |

两个驱逐限制会同时生效。生存时间始终生效：早于
`expireTimeInMs` 的条目会过期并被异步清理。除此之外，缓存会通过
条目数量或权重来限制其大小。禁用 `enableWeigher` 时，Caffeine 的 W-TinyLFU 策略会在达到
`maxEntries` 后驱逐最少使用的条目。启用 `enableWeigher` 时，每种实体类型
都带有一个权重，层级越高的实体权重越大，驱逐目标则改为总权重
预算；`maxEntries` 会被忽略，而单个条目若比整个预算还重，则永远不会
被缓存。

#### 变更日志传播

缓存是每个服务器本地的，因此在一个服务器上修改的 metalake 在其他服务器上会保持陈旧，
其相邻服务器也是如此。每个服务器都会将其变更写入实体变更日志表，并轮询该表
以使其他服务器已触及的内容失效。单独的清理器会修剪旧行。

| 配置项 | 描述 | 默认值 |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| `gravitino.entityChangeLog.pollIntervalSecs` | 轮询之间的间隔（秒）。必须为正数。 | `3` |
| `gravitino.entityChangeLog.retentionSecs` | 变更日志行保留多长时间（秒），按数据库时间计算。`0` 禁用清理；否则至少使用 `pollIntervalSecs` 的十倍。 | `2592000`（30 天） |
| `gravitino.entityChangeLog.cleanupIntervalSecs` | 清理器运行之间的间隔（秒）。必须为正数。 | `86400`（1 天） |

#### 树锁

Gravitino 使用内存中的树锁来串行化冲突的元数据操作。它是唯一
可用的锁实现，并且是每个服务器独立的。

| 配置项 | 描述 | 默认值 |
|--------------------------------------|------------------------------------------------------|---------------|
| `gravitino.lock.maxNodes` | 内存中保留的最大树锁节点数。 | `100000` |
| `gravitino.lock.minNodes` | 内存中保留的最小树锁节点数。 | `1000` |
| `gravitino.lock.cleanIntervalInSecs` | 回收陈旧锁节点的间隔（秒）。 | `60` |

### 加载 Catalog

这些属性控制服务器如何加载和隔离 Catalog。用于配置
单个 Catalog 的属性见 [Catalog 属性](#目录属性)。

下面的 `credential.backfillToProperties` 是供无法使用
发放凭证的连接器使用的变通方案；它选择退出的机制描述在
[凭证发放](security/credential-vending.md)。

| 配置项 | 描述 | 默认值 |
|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.catalog.cache.evictionIntervalMs` | 空闲 Catalog 从 Catalog 缓存中被驱逐之前的间隔（毫秒）。 | `3600000` |
| `gravitino.catalog.classloader.isolated` | 是否在隔离的类加载器中加载每个 Catalog 的库和配置，而不是使用应用程序类加载器。 | `true` |
| `gravitino.catalog.classloader.sharing.enabled` | 隔离相关属性匹配的 Catalog 是否可以共享同一个类加载器。共享会减少 Metaspace 使用量；禁用它会让每个 Catalog 都有自己的类加载器。 | `true` |
| `gravitino.catalog.credential.backfillToProperties` | 是否在 Catalog 属性响应中返回隐藏的 Catalog 凭证（例如 `jdbc-password`），以供无法使用发放凭证的连接器使用。任何能读取 Catalog 属性的人随后都能读取这些凭证。请在连接器升级后将其关闭。 | `false` |

### 敏感属性键匹配

Gravitino 会在 list/get 响应中屏蔽类似凭证的属性键，并可通过 `getSecrets` 恢复未声明的
内联值。默认情况下，当键名包含 `secret`、
`password`、`token`、`credential`、`access` 或 `account`（不区分大小写）时，该键即匹配。

`gravitino.secret.sensitiveKeyKeywords` <strong>替换</strong>该默认列表。用它来删除某个默认
会屏蔽无关属性的关键词（例如省略 `access` 和 `account`），添加拼写错误
或额外单词（例如 `passwrod` 或 `private`），或者将其设为空以禁用基于名称的
匹配。该值是一个逗号分隔列表。每一项都是属性键的不区分大小写的字面子字符串，
而不是正则表达式。请保持条目具体；像
`key` 这样过于宽泛的值可能会屏蔽无关属性。

| 配置项 | 描述 | 默认值 |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| `gravitino.secret.sensitiveKeyKeywords` | 用于类似凭证属性键的逗号分隔关键词。替换默认列表。每一项都是字面子字符串，而不是正则表达式。空值会禁用基于名称的匹配。 | `secret,password,token,credential,access,account` |

### 保护服务器安全

#### 身份验证

身份验证决定调用者是谁。它默认关闭：未配置的服务器会信任
客户端发送的任何用户名。

| 配置项 | 描述 | 默认值 |
|----------------------------|----------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.authenticators` | 要启用的逗号分隔身份验证器。有效值为 `simple`、`oauth`、`kerberos`、`basic` 和 `none`。 | `simple` |

命名一个身份验证器只需一行；配置它则不然。每个值都会读取自己的一组
`gravitino.authenticator.*` 属性，相关说明见
[如何认证](security/how-to-authenticate.md)。要将用户、密码哈希和组
成员关系保存在 Gravitino 自己的关系型存储中，而不是外部提供程序中，请参见
[本地用户和组](security/local-users-and-groups.md)。

单数形式的 `gravitino.authenticator` 是已弃用的拼写，但仍然可用。

#### 授权

授权决定已认证的调用者可以做什么。它也默认关闭，而启用
它需要命名服务管理员，因为该属性本身没有默认值。

| 配置项 | 描述 | 默认值 |
|------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `gravitino.authorization.enable` | 是否对元数据操作强制执行权限。 | `false` |
| `gravitino.authorization.serviceAdmins` | 管理服务的逗号分隔用户。创建 Metalake 仅限于这些用户。 | （无） |
| `gravitino.authorization.impl` | 授权器实现。 | `org.apache.gravitino.server.authorization.jcasbin.JcasbinAuthorizer` |
| `gravitino.authorization.threadPoolSize` | 用于处理授权检查的线程数。 | `100` |

这些属性所启用的权限模型、角色、授权、所有权，以及
默认授权器的 `gravitino.authorization.jcasbin.*` 调优，描述见
[访问控制](security/access-control.md)。要将强制执行下推到基础系统中，
通过 Apache Ranger 或原生权限模型，请参见
[授权下推](security/authorization-pushdown.md)。

#### 远程文件获取

服务器会在两种情况下按 URI 获取文件：暂存作业的文件，以及加载 Catalog 文件
（例如 Kerberos keytab）。两者都接受远程 URI，因此两者都是这样一条路径：能够
创建 Catalog 或提交作业的调用者可以让服务器自行发出请求。

| 配置项 | 描述 | 默认值 |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.fetchFile.blockUnsafeRemoteUri` | 是否拒绝解析为不安全地址的远程 URI。仅对需要它们的受信任 URI 禁用。 | `true` |

#### 审计日志

审计日志框架分为两部分。格式化器将 `Event` 转换为 `AuditLog`，而
写入器将 `AuditLog` 放到某处。两者都是接口，因此拥有自己的日志
管道的部署可以替换其中任意一个。

| 配置项 | 描述 | 默认值 |
|---------------------------------------|--------------------------------|---------------------------------------------------|
| `gravitino.audit.enabled` | 是否写入审计日志。 | `false` |
| `gravitino.audit.formatter.className` | 格式化器类名。          | `org.apache.gravitino.audit.v2.SimpleFormatterV2` |
| `gravitino.audit.writer.className`    | 写入器类名。             | `org.apache.gravitino.audit.FileAuditWriter`      |

`SimpleFormatterV2` 是默认格式化器。`JsonAuditFormatter` 可用于需要结构化
输出时：它每行输出一个 JSON 对象，序列化 `customInfo`，并将时间戳
写为 ISO 8601，具有毫秒精度和时区偏移。

`customInfo` 始终包含请求的查询参数，该参数会为每个
事件自动捕获——而不只是操作分发器显式报告的那些。例如，一个列表
端点的 `?details=true` 会出现在该请求的审计条目中，即使没有分发器
代码添加它。两个格式化器都会对 `customInfo` 值进行脱敏，将其替换为 `***`，当其键
完全匹配 `authorization`、`cookie`、`x-amz-security-token`、`s3.access-key-id`，或
`jdbc-password`，或（不区分大小写地）包含 `password`、`secret`、`token`、`credential`、
`apikey`、`accesskey`、`privatekey`、`auth` 或 `signature` 时——因此像调用方命名的参数
`?token=...` 或 `?myApiKey=...` 也会被掩蔽，即使其确切名称从未被枚举。一个简短的、
固定键列表，服务器自身始终使用（例如 `http.method`、`http.status`、`auth.method`）
不受该子字符串检查影响，否则 `auth.method` 会因为仅仅
包含 "auth" 而被掩蔽。

每个到达服务器的请求都会产生至少一条审计条目，即使其操作
没有专用的 `Event` 子类：`HttpAuditFilter` 会分派一个通用回退事件（方法、
URI、状态码以及同样自动捕获的查询参数），用于任何没有
操作层事件触发的请求。在会看到大量原本未审计调用发往
同一端点的服务器上——例如 Iceberg REST 目录的 `/v1/config`，一些客户端会
频繁轮询——这会显著增加审计日志量；请在
`conf/log4j2.properties`（如下）中相应调整日志轮转和保留策略。

`FileAuditWriter` 是默认写入器，它本身不管理文件。轮转、压缩和
保留被委托给名为 `gravitino.audit` 的 Log4j2 logger，由
`conf/log4j2.properties` 中的 `audit_file` appender 组配置。开箱即用时，它会写入
日志目录下的 `gravitino_audit.log`，并每天以及在达到 256 MB 时将其轮转为带编号的 gzip
归档。它会删除超过 30 天的归档，并按最旧优先删除总计超过 10 GB 的归档。
在那里更改保留策略或路径：

```properties
# conf/log4j2.properties
property.auditLogMaxTotalSize = 30GB
appender.audit_file.strategy.delete.ifFileName.ifAny.ifLastModified.age = 90d

appender.audit_file.fileName    = /var/log/gravitino/my_audit.log
appender.audit_file.filePattern = /var/log/gravitino/my_audit_%d{yyyyMMdd}.%i.log.gz
# Deletion must look in the new directory and match the new archive names.
appender.audit_file.strategy.delete.basePath = /var/log/gravitino
appender.audit_file.strategy.delete.ifFileName.glob = my_audit_*.log.gz
```

更早的版本使用以下配置设置审计保留：
`appender.audit_file.strategy.delete.ifAll.ifLastModified.age`。该键已不存在。Log4j2
会拒绝仍然设置它的配置文件，服务器随后不会写入任何日志文件。请参阅
[日志轮转和保留](./how-to-install.md#log-rotation-and-retention) 了解所有日志。

更早的版本通过 `gravitino.audit.writer.file.*` 直接配置写入器。这些
属性现在不起作用，如果 `FileAuditWriter` 在启动时发现其中任何一个，就会记录警告。

| 已移除的属性                                | 改为在 `conf/log4j2.properties` 中配置                     |
|-------------------------------------------------|-------------------------------------------------------------------|
| `gravitino.audit.writer.file.fileName`          | `appender.audit_file.fileName`                                    |
| `gravitino.audit.writer.file.append`            | `appender.audit_file.append`                                      |
| `gravitino.audit.writer.file.flushIntervalSecs` | 在 appender 上使用 `immediateFlush`，或将其包装在异步 appender 中 |

### 扩展服务器

#### 事件监听器

事件监听器接收 Gravitino 围绕元数据操作发出的事件，外部系统正是通过这种方式
在不轮询目录的情况下观察目录。要使用监听器，请实现
`EventListenerPlugin`，将 jar 放到服务器 classpath 上，并在 `gravitino.conf` 中命名它。

| 配置项                     | 描述                                                                            | 默认值 |
|----------------------------------------|----------------------------------------------------------------------------------------|---------------|
| `gravitino.eventListener.names`        | 以逗号分隔的监听器名称，例如 `audit,sync`。                                    | （空）       |
| `gravitino.eventListener.{name}.class` | 在 `{name}` 下注册的监听器的类名。                                  | （无）        |
| `gravitino.eventListener.{name}.{key}` | 监听器名称下的任何其他属性都会原样传递给该插件。 | （无）        |

`names` 中的每个名称都需要匹配的 `{name}.class`，否则服务器无法构建该监听器。

每个操作最多发出三个事件：运行前的前置事件、成功后的后置事件，
以及抛出异常后的失败事件。名称遵循操作，因此 `createTable`
产生 `CreateTablePreEvent`、`CreateTableEvent` 和 `CreateTableFailureEvent`。由
Gravitino IRC 端点服务的操作带有 `Iceberg` 前缀，例如 `IcebergCreateTableEvent`。
并非每个操作都定义全部三种。完整的类集合位于
[`org.apache.gravitino.listener.api.event`](https://github.com/apache/gravitino/tree/main/core/src/main/java/org/apache/gravitino/listener/api/event)
包中。

从预事件处理器抛出 `ForbiddenException` 会在操作运行前阻止它，这
使预事件成为否决点，而非通知。

每个事件上的 `customInfo()` 都包含请求的查询参数，而自定义监听器
接收到的它们是<strong>未脱敏的</strong>——上文“审计日志”中描述的掩蔽仅由
两个内置审计日志格式化器在格式化时应用，而不会应用于事件对象本身。监听器
如果将 `customInfo()` 转发到其他地方（日志、指标管道、下游服务），则
如果这对目标位置有影响，则需自行负责脱敏。

插件声明其事件如何被分派：

| 模式             | 行为                                                                                                                         |
|------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `SYNC`           | 内联处理，在操作结果到达客户端之前。慢监听器会拖慢请求。                           |
| `ASYNC_SHARED`   | 在与其他监听器共享的队列和分派器上处理。一个慢监听器会拖累其余监听器，并且事件可能被丢弃。 |
| `ASYNC_ISOLATED` | 在自有队列和分派器上处理。隔离性更好，代价是每个监听器一个队列和线程。                |

#### 辅助服务

辅助服务在 Gravitino 服务器进程内运行，并使用自己的端口。该属性
没有默认值，但发行版中随附的 `gravitino.conf` 将其设置为
`iceberg-rest,lance-rest`，因此除非你更改该行，否则两者都会启动。

| 配置项           | 描述                                                                                                                  | 默认值 |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.auxService.names` | 要启动的以逗号分隔的辅助服务。`iceberg-rest` 是 Gravitino IRC 服务器，`lance-rest` 是 Lance REST 服务器。 | （空）       |

IRC 配置的其余部分，以及 Lance REST 服务器的 `gravitino.lance-rest.*` 属性，
都在相应服务的文档中说明。请参阅
[Iceberg REST Catalog 服务](iceberg-rest-service.md)。

#### 作业

| 配置项                     | 描述                                                                                                | 默认值                 |
|----------------------------------------|------------------------------------------------------------------------------------------------------------|-------------------------------|
| `gravitino.job.executor`               | 运行作业的执行器。实现你自己的执行器并在此命名，以替换内置执行器。                  | `local`                       |
| `gravitino.job.stagingDir`             | 存放正在运行的作业的暂存文件的目录。                                                          | `/tmp/gravitino/jobs/staging` |
| `gravitino.job.stagingDirKeepTimeInMs` | 已完成的作业的暂存文件保留多长时间（毫秒）。在测试之外至少使用 10 分钟。 | `604800000`（7 天）          |
| `gravitino.job.statusPullIntervalInMs` | 作业状态轮询之间的间隔（毫秒）。在测试之外至少使用 1 分钟。                  | `300000`（5 分钟）          |

### 密钥管理

服务器会与你 `gravitino.conf` 中命名的 KMS 实例通信。每个名称都是一个已配置的
实例。要添加一个实例，请实现具有公共无参构造函数的 `KmsClientFactory`，将 jar 放到
服务器 classpath 上，并将 `gravitino.kms.provider.<name>.className` 设置为该类。
`create(provider, properties)` 为该名称构建 `KmsClient`。Gravitino 不附带 AWS 或
Azure 工厂。两个名称可以共享同一个类，这就是你运行多个同类型
保管库的方式。

该列表默认为空，此时服务器没有 KMS 客户端。命名一个没有
`className` 的提供者，或使用服务器无法构造为 `KmsClientFactory` 的类，会导致启动失败。
客户端构造仅验证本地配置；对提供者的第一次调用是后续的
密钥检查，而不是启动时。

| 配置项                         | 描述                                                                                                                                                          | 默认值 |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `gravitino.kms.providers`                  | 以逗号分隔的 KMS 实例名称，逗号后不能有空格。每个名称必须匹配 `[A-Za-z0-9][A-Za-z0-9_-]*`，且不能包含 `.`。重复项会导致启动失败。 | （空）       |
| `gravitino.kms.provider.<name>.className`  | 该实例所需的工厂类名。该类必须具有无参构造函数并实现 `KmsClientFactory`。                                          | （无）        |
| `gravitino.kms.provider.<name>.<key>`      | 该名称下的任何其他属性都会传递给该工厂。`<key>` 中允许嵌套点号，例如 `endpoint.region`。                                           | （无）        |

`providers` 中的每个名称都需要匹配的 `.className`。一个 `gravitino.kms.provider.<name>.*` 键
如果其名称不在列表中，或任何其他 `gravitino.kms.*` 键，都会导致启动失败。

调用方指定实例和密钥。它们不发送 `className`。服务器已经在启动时
为 `aws-prod` 构造了工厂。

```text
# conf/gravitino.conf
gravitino.kms.providers = aws-prod,aws-dr,azure-eu

gravitino.kms.provider.aws-prod.className = com.example.kms.AwsCustomKmsClientFactory
gravitino.kms.provider.aws-dr.className = com.example.kms.AwsCustomKmsClientFactory
gravitino.kms.provider.azure-eu.className = com.example.kms.AzureCustomKmsClientFactory
```

该配置构建三个客户端：一个自定义 AWS 工厂的两个实例，以及一个自定义
Azure 工厂。进一步的 `gravitino.kms.provider.<name>.*` 键是工厂属性，而不是封闭的
schema；每个工厂都会记录其接受的键。

## 目录属性

目录属性配置一个目录，而不是服务器。它们来自两个地方：一个
目录配置文件为该提供者的每个目录提供默认值，而
创建目录请求上的 `properties` 字段仅针对该目录提供值。请求
优先。两者都不影响 schema 或表属性。

目录属性有三种类型。有些由 Gravitino 自己定义，作为目录
工作所需的设置。任何以 `gravitino.bypass.` 为前缀的内容都会直接传递到底层
系统，且不做改动。其他任何内容 Gravitino 只是存储起来，供你随意使用。

通过 `gravitino.bypass.` 传递凭证、令牌或访问密钥会暴露它们：被绕过的
属性不受 Gravitino 管理，并可能从 REST API 以明文返回。当底层
系统别无选择时，请相应地限制对目录 API 的访问。

这些属性适用于每个目录：

| 配置项  | 描述                                                                                                                                            | 默认值 |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `package`           | 目录包的路径，Gravitino 从中加载目录的库和配置。它包含一个 `conf` 目录和一个 `libs` 目录。 | （无）        |
| `cloud.name`        | 目录运行所在的云。取值为 `aws`、`azure`、`gcp`、`on_premise` 或 `other` 之一。                                                                     | （无）        |
| `cloud.region-code` | 该云中的区域代码。                                                                                                                         | （无）        |

其他所有内容都因提供者而异。服务器会将下面每个配置目录添加到
classpath 中，这也是 `hdfs-site.xml` 等提供者特定文件所在的位置。

| 目录提供者    | 目录属性                                                                      | 配置文件路径                                  |
|---------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------|
| `hive`              | [Hive 目录属性](apache-hive-catalog.md#catalog-properties)                    | `catalogs/hive/conf/hive.conf`                           |
| `glue`              | [AWS Glue 目录属性](aws-glue-catalog.md#catalog-properties)                   | `catalogs/glue/conf/glue.conf`                           |
| `lakehouse-iceberg` | [Lakehouse Iceberg 目录属性](lakehouse-iceberg-catalog.md#catalog-properties) | `catalogs/lakehouse-iceberg/conf/lakehouse-iceberg.conf` |
| `lakehouse-paimon`  | [Lakehouse Paimon Catalog 属性](lakehouse-paimon-catalog.md#catalog-properties)   | `catalogs/lakehouse-paimon/conf/lakehouse-paimon.conf`   |
| `lakehouse-hudi`    | [Lakehouse Hudi Catalog 属性](lakehouse-hudi-catalog.md#catalog-properties)       | `catalogs/lakehouse-hudi/conf/lakehouse-hudi.conf`       |
| `lakehouse-generic` | [Lakehouse Generic Catalog 属性](lakehouse-generic-catalog.md#catalog-properties) | `catalogs/lakehouse-generic/conf/lakehouse-generic.conf` |
| `jdbc-mysql`        | [MySQL Catalog 属性](jdbc-mysql-catalog.md#catalog-properties)                    | `catalogs/jdbc-mysql/conf/jdbc-mysql.conf`               |
| `jdbc-postgresql`   | [PostgreSQL Catalog 属性](jdbc-postgresql-catalog.md#catalog-properties)          | `catalogs/jdbc-postgresql/conf/jdbc-postgresql.conf`     |
| `jdbc-doris`        | [Doris Catalog 属性](jdbc-doris-catalog.md#catalog-properties)                    | `catalogs/jdbc-doris/conf/jdbc-doris.conf`               |
| `jdbc-starrocks`    | [StarRocks Catalog 属性](jdbc-starrocks-catalog.md#catalog-properties)            | `catalogs/jdbc-starrocks/conf/jdbc-starrocks.conf`       |
| `jdbc-clickhouse` ‡ | [ClickHouse Catalog 属性](jdbc-clickhouse-catalog.md#catalog-properties)          | `catalogs/jdbc-clickhouse/conf/jdbc-clickhouse.conf`     |
| `jdbc-hologres` ‡   | [Hologres Catalog 属性](jdbc-hologres-catalog.md#catalog-properties)              | `catalogs/jdbc-hologres/conf/jdbc-hologres.conf`         |
| `jdbc-oceanbase` ‡  | [OceanBase Catalog 属性](jdbc-oceanbase-catalog.md#catalog-properties)            | `catalogs/jdbc-oceanbase/conf/jdbc-oceanbase.conf`       |
| `kafka`             | [Kafka Catalog 属性](kafka-catalog.md#catalog-properties)                         | `catalogs/kafka/conf/kafka.conf`                         |
| `fileset`           | [Fileset Catalog 属性](fileset-catalog.md#catalog-properties)                     | `catalogs/fileset/conf/fileset.conf`                     |
| `model`             | [Model Catalog 属性](model-catalog.md#catalog-properties)                         | `catalogs/model/conf/model.conf`                         |

‡ 贡献的 Catalog，仅在 `-all` 发行包中提供。标准包
不包含它们的目录。

## 容器配置

```shell
docker run --rm -d -p 8090:8090 apache/gravitino:{tag}
```

### 容器如何构建其配置

容器入口点在 JVM 启动之前重写 `conf/gravitino.conf`。它分两个
阶段。首先，它无条件地用自己的默认值覆盖它知道默认值的每个属性，
丢弃文件中原本的内容。然后，它应用每个受支持的、已
设置的环境变量。结果会写回原始文件。

有两个值得牢记的后果。你嵌入 `conf/gravitino.conf` 的属性只有在
容器没有为其提供默认值时才保留，因此挂载文件中的自定义 `httpPort` 之类的值会
被静默替换。而且容器的默认值不是服务器的默认值：容器将
`minThreads` 固定为 24，`maxThreads` 固定为 200，而在容器外启动的服务器会根据
处理器数量计算这两个值。

设置 `SKIP_CONFIG_REWRITE=true` 可禁用这两个阶段，并完全按照
写入的内容运行配置文件。当文件来自 Kubernetes ConfigMap 时使用此选项。

### 支持的环境变量

入口点识别以下变量，并忽略所有其他 `GRAVITINO_` 变量。
“容器默认值”列给出变量未设置时第一阶段写入的值；`(none)`
表示该属性保持不变。

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
| `GRAVITINO_ICEBERG_REST_URI`                             | `gravitino.iceberg-rest.uri`                         | (none)                                               |
| `GRAVITINO_ICEBERG_REST_CLASSPATH`                       | `gravitino.iceberg-rest.classpath`                   | `iceberg-rest-server/libs, iceberg-rest-server/conf` |
| `GRAVITINO_ICEBERG_REST_IO_IMPL`                         | `gravitino.iceberg-rest.io-impl`                     | (none)                                               |
| `GRAVITINO_ICEBERG_REST_CATALOG_BACKEND`                 | `gravitino.iceberg-rest.catalog-backend`             | `memory`                                             |
| `GRAVITINO_ICEBERG_REST_JDBC_DRIVER`                     | `gravitino.iceberg-rest.jdbc-driver`                 | (none)                                               |
| `GRAVITINO_ICEBERG_REST_JDBC_USER`                       | `gravitino.iceberg-rest.jdbc-user`                   | (none)                                               |
| `GRAVITINO_ICEBERG_REST_JDBC_PASSWORD`                   | `gravitino.iceberg-rest.jdbc-password`               | (none)                                               |
| `GRAVITINO_ICEBERG_REST_WAREHOUSE`                       | `gravitino.iceberg-rest.warehouse`                   | `/tmp/`                                              |
| `GRAVITINO_ICEBERG_REST_CREDENTIAL_PROVIDERS`            | `gravitino.iceberg-rest.credential-providers`        | (none)                                               |
| `GRAVITINO_ICEBERG_REST_GCS_SERVICE_ACCOUNT_FILE`        | `gravitino.iceberg-rest.gcs-service-account-file`    | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_ACCESS_KEY`                   | `gravitino.iceberg-rest.s3-access-key-id`            | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_SECRET_KEY`                   | `gravitino.iceberg-rest.s3-secret-access-key`        | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_ENDPOINT`                     | `gravitino.iceberg-rest.s3-endpoint`                 | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_REGION`                       | `gravitino.iceberg-rest.s3-region`                   | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_PATH_STYLE_ACCESS`            | `gravitino.iceberg-rest.s3-path-style-access`        | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_ROLE_ARN`                     | `gravitino.iceberg-rest.s3-role-arn`                 | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_EXTERNAL_ID`                  | `gravitino.iceberg-rest.s3-external-id`              | (none)                                               |
| `GRAVITINO_ICEBERG_REST_S3_TOKEN_SERVICE_ENDPOINT`       | `gravitino.iceberg-rest.s3-token-service-endpoint`   | (none)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_STORAGE_ACCOUNT_NAME`      | `gravitino.iceberg-rest.azure-storage-account-name`  | (none)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_STORAGE_ACCOUNT_KEY`       | `gravitino.iceberg-rest.azure-storage-account-key`   | (none)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_TENANT_ID`                 | `gravitino.iceberg-rest.azure-tenant-id`             | (none)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_CLIENT_ID`                 | `gravitino.iceberg-rest.azure-client-id`             | (none)                                               |
| `GRAVITINO_ICEBERG_REST_AZURE_CLIENT_SECRET`             | `gravitino.iceberg-rest.azure-client-secret`         | (none)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_ACCESS_KEY`                  | `gravitino.iceberg-rest.oss-access-key-id`           | (none)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_SECRET_KEY`                  | `gravitino.iceberg-rest.oss-secret-access-key`       | (none)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_ENDPOINT`                    | `gravitino.iceberg-rest.oss-endpoint`                | (none)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_REGION`                      | `gravitino.iceberg-rest.oss-region`                  | (none)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_ROLE_ARN`                    | `gravitino.iceberg-rest.oss-role-arn`                | (none)                                               |
| `GRAVITINO_ICEBERG_REST_OSS_EXTERNAL_ID`                 | `gravitino.iceberg-rest.oss-external-id`             | (none)                                               |

该镜像将 MySQL 和 PostgreSQL JDBC 驱动程序打包在 `jdbc-drivers/` 中，并将它们链接到 `libs/`
以及启动时的 `iceberg-rest-server/libs/`。对于云存储后端，将匹配的 Iceberg
bundle jar 包放入 `iceberg-bundles/`，它们会被链接到
`catalogs/lakehouse-iceberg/libs/` 和 `iceberg-rest-server/libs/`，方式相同。

### 检查容器做了什么

读回重写后的文件：

```shell
docker exec -it {container_id} cat /opt/gravitino/conf/gravitino.conf
```

然后确认服务器，以及你启动的辅助 IRC 服务（如果有）：

```shell
curl http://127.0.0.1:8090/health/ready
curl http://127.0.0.1:9001/iceberg/v1/config
```

## 访问 Apache Hadoop

Gravitino 以单个操作系统用户身份访问 Hadoop，因此该用户需要拥有 HDFS 和 YARN
权限，用于服务器将要接触的所有内容。没有这些权限，操作会失败并显示
`Permission denied`。要么向启动服务器的用户授予其所需的权限，要么设置
`HADOOP_USER_NAME` 为启动前已拥有这些权限的用户。对于本地部署，请将其设置
在 `conf/gravitino-env.sh` 中。

## 相关

- [关系型后端存储](how-to-use-relational-backend-storage.md)，用于将实体
  存储指向 MySQL 或 PostgreSQL，包括模式初始化和驱动程序安装
- [Iceberg REST Catalog 服务](iceberg-rest-service.md)，用于 `gravitino.iceberg-rest.*`
  由 `gravitino.auxService.names` 命名的辅助服务的属性
- [如何认证](security/how-to-authenticate.md)，用于 `gravitino.authenticator.*`
  `gravitino.authenticators` 的每个值背后的属性
- [本地用户和组](security/local-users-and-groups.md)，用于保存用户、密码
  哈希值以及 Gravitino 自有关系型存储中的组成员关系
- [访问控制](security/access-control.md)，用于说明授权器一旦
  `gravitino.authorization.enable` 被设置后强制执行的权限模型：角色、授权、所有权和 metalake 管理
- [授权下推](security/authorization-pushdown.md)，用于将这些权限传播
  到底层系统中，通过 Apache Ranger 或原生权限模型
- [凭证发放](security/credential-vending.md)，用于向
  引擎签发临时存储凭证，而不是分发长期有效的密钥
- [HTTPS](security/how-to-use-https.md)，用于 `gravitino.server.webserver.*` 密钥库、信任
  库和客户端证书属性
- [CORS](security/how-to-use-cors.md)，用于允许从另一个源提供的浏览器客户端调用
  API
- [安全](security/how-to-authenticate.md)