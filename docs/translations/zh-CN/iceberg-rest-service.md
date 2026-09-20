---
title: "Iceberg REST Catalog Service"
slug: "/iceberg-rest-service"
keywords:
  - Iceberg REST catalog
license: "This software is licensed under the Apache License version 2."
---

## 概述

Apache Gravitino Iceberg REST 服务器实现了 [Apache Iceberg REST API 规范](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)。
通过 `http://$ip:$port/iceberg/` 访问 Iceberg REST 端点。

Iceberg REST 服务器和主 Gravitino 服务器暴露不同的接口，并管理不同的表类型：

| 项目               | Gravitino Iceberg REST 服务器                                                                            | Gravitino 服务器                                                                                     |
|--------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| 接口         | [Iceberg REST API 规范](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml) | [Gravitino 统一接口](https://gravitino.apache.org/docs/latest/api/rest/gravitino-rest-api) |
| 托管表类型 | 仅限 Iceberg 表                                                                                       | JDBC、Hive、Iceberg、Hudi、Paimon 等                                                               |

### 能力

Iceberg REST 服务器提供：

- Apache Iceberg 1.11 REST API 支持大多数命名空间、表和视图操作。
- 分层命名空间。
- Hive、JDBC 和 REST 目录后端。
- 为 S3、GCS、OSS 和 ADLS 提供凭据分发。
- 支持 S3、HDFS、OSS、GCS、ADLS 和自定义存储。
- 事件监听器和审计日志。
- OAuth2 和 HTTPS。
- 辅助模式下的访问控制。
- 可插拔的指标存储。
- 表元数据和扫描计划缓存。

以下 Iceberg REST API 功能未实现：

- 多表事务。
- 视图注册。

## 部署

### 部署模式

选择以下部署模式之一：

| 模式              | 包                               | 类路径                  | 访问控制 |
|-------------------|---------------------------------------|----------------------------|----------------|
| 独立服务器 | Gravitino Iceberg REST 服务器包 | `libs`                     | 否             |
| 独立服务器 | Gravitino 服务器包              | `iceberg-rest-server/libs` | 否             |
| 辅助服务 | Gravitino 服务器包              | `iceberg-rest-server/libs` | 是            |

### 软件包构建

有关构建和安装 Gravitino 服务器包的说明，请参阅 [构建 Gravitino](./how-to-build.md) 和 [安装 Gravitino](./how-to-install.md)。

构建独立的 Iceberg REST 服务器包：

```shell
./gradlew compileIcebergRESTServer -x test
```

在分发目录中创建压缩包：

```shell
./gradlew assembleIcebergRESTServer -x test
```

### 包布局

独立的 Iceberg REST 服务器包具有以下布局：

```text
|── ...
└── distribution/gravitino-iceberg-rest-server
    |── bin/
    |   └── gravitino-iceberg-rest-server.sh    # Gravitino Iceberg REST server Launching scripts.
    |── conf/                                   # All configurations for Gravitino Iceberg REST server.
    |   ├── gravitino-iceberg-rest-server.conf  # Gravitino Iceberg REST server configuration.
    |   ├── gravitino-env.sh                    # Environment variables, etc., JAVA_HOME, GRAVITINO_HOME, and more.
    |   └── log4j2.properties                   # log4j configuration for the Gravitino Iceberg REST server.
    |   └── hdfs-site.xml & core-site.xml       # HDFS configuration files.
    |── libs/                                   # Gravitino Iceberg REST server dependencies libraries.
    |── logs/                                   # Gravitino Iceberg REST server logs. Automatically created after the server starts.
```

## 配置

独立部署和辅助部署使用不同的配置文件：

- 独立服务器：`gravitino-iceberg-rest-server.conf`。
- 辅助服务：`gravitino.conf`。

两个文件都使用相同的 Iceberg REST 配置项。
`gravitino.auxService.iceberg-rest.` 前缀已弃用。
如果 `gravitino.auxService.iceberg-rest.key` 和 `gravitino.iceberg-rest.key` 同时存在，则 `gravitino.iceberg-rest.key` 优先。
以下部分使用 `gravitino.iceberg-rest.` 前缀。

服务器级别的 `gravitino.fetchFile.blockUnsafeRemoteUri` 配置控制诸如 Kerberos keytabs 等远程文件是否可能解析为不安全的地址。其默认值为 `true`。对于独立模式，请在 `gravitino-iceberg-rest-server.conf` 中配置它；对于辅助模式，请在 `gravitino.conf` 中配置它。

### 服务配置

#### 辅助服务

| 配置项                 | 描述                                                                                                                                                                                                                            | 默认值 | 必填 |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.auxService.names`       | Gravitino Iceberg REST 目录服务的辅助服务名称。使用 **`iceberg-rest`**。                                                                                                                                      | (无)        | 是      |
| `gravitino.iceberg-rest.classpath` | Gravitino Iceberg REST 目录服务的类路径；包含存放 jars 和配置的目录。支持绝对路径和相对路径，例如，`iceberg-rest-server/libs, iceberg-rest-server/conf` | (无)        | 是      |

这些设置仅适用于 `gravitino.conf`。
请勿将它们添加到独立服务器配置中。

#### HTTP 服务器

| 配置项                               | 描述                                                                                                                                                                                   | 默认值                                                                | 必填 |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|----------|
| `gravitino.iceberg-rest.host`                    | Gravitino Iceberg REST 目录服务的主机。                                                                                                                                       | `0.0.0.0`                                                                    | 否       |
| `gravitino.iceberg-rest.httpPort`                | Gravitino Iceberg REST 目录服务的端口。                                                                                                                                       | `9001`                                                                       | 否       |
| `gravitino.iceberg-rest.minThreads`              | Jetty Web 服务器使用的线程池中的最小线程数。如果该值小于 8，则 `minThreads` 为 8。                                                                 | `Math.max(Math.min(Runtime.getRuntime().availableProcessors() * 2, 100), 8)` | 否       |
| `gravitino.iceberg-rest.maxThreads`              | Jetty Web 服务器使用的线程池中的最大线程数。如果该值小于 8，则 `maxThreads` 为 8，并且 `maxThreads` 必须大于或等于 `minThreads`。 | `Math.max(Runtime.getRuntime().availableProcessors() * 4, 400)`              | 否       |
| `gravitino.iceberg-rest.threadPoolWorkQueueSize` | Gravitino Iceberg REST 目录服务使用的线程池中的队列大小。                                                                                                      | `100`                                                                        | 否       |
| `gravitino.iceberg-rest.stopTimeout`             | Gravitino Iceberg REST 目录服务优雅停止的时间（以毫秒为单位）。更多信息请参见 `org.eclipse.jetty.server.Server#setStopTimeout`。                       | `30000`                                                                      | 否       |
| `gravitino.iceberg-rest.idleTimeout`             | 空闲连接的超时时间（以毫秒为单位）。                                                                                                                                                        | `30000`                                                                      | 否       |
| `gravitino.iceberg-rest.requestHeaderSize`       | HTTP 请求的最大大小。                                                                                                                                                          | `131072`                                                                     | 否       |
| `gravitino.iceberg-rest.responseHeaderSize`      | HTTP 响应的最大大小。                                                                                                                                                         | `131072`                                                                     | 否       |
| `gravitino.iceberg-rest.includeErrorStackTrace`  | 错误响应是否包含服务器端堆栈跟踪。在新的部署中将其设置为 `false`，因为响应可能会暴露内部实现细节。 | `true`                                                                       | 否       |
| `gravitino.iceberg-rest.customFilters`           | 要应用于 API 的以逗号分隔的过滤器类名列表。                                                                                                                              | (none)                                                                       | 否       |
| `gravitino.iceberg-rest.advertised-uri`          | 报告给通过 Gravitino 服务器发现该服务的客户端的公共端点。必须是带有主机且没有查询或片段的绝对 `http`/`https` URI。                  | (none)                                                                       | 否       |

`customFilters` 中的过滤器应该是一个标准的 javax servlet 过滤器。
通过设置格式为 `gravitino.iceberg-rest.<class name of filter>.param.<param name>=<value>` 的配置项来指定过滤器参数。

当诸如 Trino 连接器之类的客户端通过反向代理访问服务，且该代理的协议、主机、端口或路径与监听器的不一致时，请设置 `gravitino.iceberg-rest.advertised-uri`，例如 `https://iceberg.example.com/iceberg/`。
显式指定的端口必须在 1-65535 范围内；无效值将导致发现请求失败，而不是对外发布一个不可达的端点。
它仅影响对外发布的端点，不影响监听器；未设置时，端点将由 `host`、`httpPort`/`httpsPort` 和 `enableHttps` 推导得出。
此设置仅适用于辅助服务。

#### 异步表清除

默认情况下，删除带有 `purgeRequested=true` 的表是同步的：目录条目和表文件会在 `DELETE` 返回之前被移除。

当 Iceberg REST 服务在 Gravitino 内部运行（作为辅助服务）时，客户端可以通过在 `DELETE ...?purgeRequested=true` 中添加请求头 `X-Gravitino-Async-Purge: true` 来请求异步清除。随后，一旦表从 catalog 中移除，drop 操作就会返回 `204 No Content`，并且文件将在后台被删除。该表会立即从 `LIST` 中消失，但在文件清理完成之前，重新创建它（使用相同名称的 `createTable` / `registerTable`）将返回 `409 Conflict`。

标头名称不区分大小写（根据 HTTP 标准），但其值必须完全为 `true`。任何其他值，或者没有标头，都会使用同步默认值，因此标准 Iceberg 客户端不受影响。异步清理仅在辅助模式下可用；在独立模式下标头会被忽略。

以下设置用于调整后台工作进程，并且是可选的。

| 配置项                                            | 描述                                                                                          | 默认值 | 是否必填 |
|---------------------------------------------------------------|------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.async-cleanup.worker-threads`         | 每个服务器的工作线程池大小。每个工作线程从共享的后端表中认领并运行清理作业。 | `2`           | 否       |
| `gravitino.iceberg-rest.async-cleanup.delete-threads`         | 清理作业共享的服务器级文件删除池大小。                                            | `4`           | 否       |
| `gravitino.iceberg-rest.async-cleanup.delete-batch-size`      | 每个批量删除批次的文件数量。                                                               | `1000`        | 否       |
| `gravitino.iceberg-rest.async-cleanup.poll-interval-secs`     | 工作线程轮询间隔（以秒为单位）。这也控制了待处理作业的重试节奏。                | `5`           | 否       |
| `gravitino.iceberg-rest.async-cleanup.heartbeat-timeout-secs` | 运行中的作业在没有新心跳的情况下经过此秒数后，可以被其他工作线程回收。 | `300`         | 否       |
| `gravitino.iceberg-rest.async-cleanup.max-attempts`           | 清理作业被标记为 `FAILED` 之前的失败尝试次数。                                   | `5`           | 否       |
| `gravitino.iceberg-rest.async-cleanup.retention-hours`        | 终态 `SUCCEEDED` 或 `FAILED` 清理行在清除前的保留时间。                     | `720`         | 否       |

### 目录后端配置

:::info
Gravitino Iceberg REST 目录服务默认使用内存目录后端。在生产环境中，请指定 Hive、JDBC 或 REST 目录后端。
:::

#### Hive 后端配置

| 配置项                            | 描述                                                                                                                                  | 默认值                                                                 | 必填 |
|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|----------|
| `gravitino.iceberg-rest.catalog-backend`      | Gravitino Iceberg REST catalog 服务的 Catalog 后端。对于 Hive catalog 后端，请使用值 **`hive`**。                    | `memory`                                                                      | 是      |
| `gravitino.iceberg-rest.uri`                  | Hive 元数据地址，例如 `thrift://127.0.0.1:9083`。                                                                                | (none)                                                                        | 是      |
| `gravitino.iceberg-rest.warehouse`            | Hive catalog 的 warehouse 目录，例如 `/user/hive/warehouse-hive/`。                                                           | (none)                                                                        | 是      |
| `gravitino.iceberg-rest.catalog-backend-name` | 传递给底层 Iceberg catalog 后端的 catalog 后端名称。JDBC 后端中的 Catalog 名称用于隔离命名空间和表。 | `hive` 用于 Hive 后端，`jdbc` 用于 JDBC 后端，`memory` 用于 memory 后端 | 否       |

对于受 Kerberos 保护的 Hive Metastore 和 HDFS，请参阅[后端身份验证](#backend-authentication)。

#### JDBC 后端配置

| 配置项                            | 描述                                                                                                                                                                                                                                                                                | 默认值           | 必填 |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|----------|
| `gravitino.iceberg-rest.catalog-backend`      | Gravitino Iceberg REST catalog 服务的 Catalog 后端。对于 JDBC catalog 后端，使用值 **`jdbc`**。                                                                                                                                                                                  | `memory`                | Yes      |
| `gravitino.iceberg-rest.uri`                  | JDBC 连接地址，例如 Postgres 的 `jdbc:postgresql://127.0.0.1:5432`，或 mysql 的 `jdbc:mysql://127.0.0.1:3306/`。                                                                                                                                                                         | (none)                  | Yes      |
| `gravitino.iceberg-rest.warehouse`            | JDBC catalog 的 warehouse 目录。如果使用 HDFS，请设置 HDFS 前缀，例如 `hdfs://127.0.0.1:9000/user/hive/warehouse-jdbc`                                                                                                                                                                       | (none)                  | Yes      |
| `gravitino.iceberg-rest.catalog-backend-name` | 传递给底层 Iceberg catalog 后端的 catalog 名称。JDBC 后端中的 catalog 名称用于隔离命名空间和表。                                                                                                                                                                       | `jdbc` 用于 JDBC 后端 | No       |
| `gravitino.iceberg-rest.jdbc-user`            | JDBC 连接的用户名。                                                                                                                                                                                                                                                                       | (none)                  | No       |
| `gravitino.iceberg-rest.jdbc-password`        | JDBC 连接的密码。                                                                                                                                                                                                                                                                       | (none)                  | No       |
| `gravitino.iceberg-rest.jdbc-initialize`      | 创建 JDBC catalog 时是否初始化元数据表。                                                                                                                                                                                                                                      | `true`                  | No       |
| `gravitino.iceberg-rest.jdbc-driver`          | MySQL 使用 `com.mysql.jdbc.Driver` 或 `com.mysql.cj.jdbc.Driver`，PostgreSQL 使用 `org.postgresql.Driver`。                                                                                                                                                                                                   | (none)                  | Yes      |
| `gravitino.iceberg-rest.jdbc-schema-version`  | JDBC catalog 的 schema 版本。默认为 `V1` 以启用视图支持。仅在需要禁用视图支持时设置为 `V0`。一旦底层数据库迁移到 V1，在后续重启时不再需要此属性。                                                      | `V1`                    | No       |
| `gravitino.iceberg-rest.jdbc.strict-mode`     | JDBC catalog 是否以严格模式运行。默认为 `true`，以便在不存在的命名空间中创建表或视图时会失败并返回 `NoSuchNamespace` (HTTP 404)，这与 Iceberg REST 规范相匹配。设置为 `false` 可恢复隐式创建命名空间的旧行为。 | `true`                  | No       |

如果您之前已有 JDBC Iceberg 目录，则必须设置 `catalog-backend-name` 使其与您的 Jdbc Iceberg 目录名称保持一致，以操作之前的命名空间和表。

使用 `gravitino.iceberg-rest.jdbc-user` 和 `gravitino.iceberg-rest.jdbc-password` 来认证 JDBC catalog 元数据存储。当仓库位于受 Kerberos 保护的 HDFS 上时，将 `gravitino.iceberg-rest.authentication.type` 设置为 `kerberos`，并在 [后端认证](#backend-authentication) 中配置 Kerberos 属性以访问仓库路径。

:::caution
将相应的 JDBC 驱动下载到 `iceberg-rest-server/libs` 目录中。
如果您使用多个 JDBC catalog 后端，将 `jdbc-initialize` 设置为 true 对于像 `Mysql` 这样的 RDBMS 可能不会生效，您应该显式创建 Iceberg 元表。
:::

#### REST 后端配置

使用 REST 后端代理另一个 Iceberg REST catalog server (IRC2)。Gravitino Iceberg REST 服务充当 IRC1，并将 catalog 操作转发给 IRC2。

默认情况下，当后端 catalog 是 REST catalog 时，IRC1 会跳过授权并作为代理运行。IRC2 负责处理授权。如果您希望 IRC1 保留授权检查，请设置 `gravitino.iceberg-rest.disable-rest-authz=false`。

| 配置项                                         | 描述                                                                                                                                                      | 默认值 | 必填 |
|------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.catalog-backend`                   | Gravitino Iceberg REST catalog 服务的 Catalog 后端。对于 REST catalog 后端，使用值 **`rest`**。                                        | `memory`      | Yes      |
| `gravitino.iceberg-rest.uri`                               | Iceberg REST catalog URI (IRC2)，例如 `http://127.0.0.1:9001/iceberg`。                                                                                    | (none)        | Yes      |
| `gravitino.iceberg-rest.warehouse`                         | Iceberg REST 规范中的 catalog 名称。设置为特定的 catalog 名称，或留空以使用 IRC2 上的默认 catalog。                                    | (none)        | No       |
| `gravitino.iceberg-rest.rest-client-connection-timeout-ms` | IRC1 请求 REST catalog 后端的 HTTP 连接超时时间（以毫秒为单位）。                                                                       | `10000`       | No       |
| `gravitino.iceberg-rest.rest-client-socket-timeout-ms`     | IRC1 请求 REST catalog 后端的 HTTP socket 超时时间（以毫秒为单位）。                                                                           | `60000`       | No       |
| `gravitino.iceberg-rest.data-access`                       | 通过 `/v1/config` 暴露给 Iceberg REST 客户端的数据访问模式。支持的值：`vended-credentials`、`remote-signing`。                                     | (none)        | No       |
| `gravitino.iceberg-rest.disable-rest-authz`                | 当目标后端 catalog 是 REST catalog 时，IRC1 是否禁用授权。如果希望 IRC1 在代理前执行授权，请设置为 `false`。 | `true`        | No       |

如果 IRC2 使用 HDFS 存储时的 IRC1 配置示例：

```text
gravitino.iceberg-rest.catalog-backend = rest
gravitino.iceberg-rest.uri = http://127.0.0.1:9001/iceberg
```

如果 IRC2 使用 S3 存储，IRC1 配置示例：

```text
gravitino.iceberg-rest.catalog-backend = rest
gravitino.iceberg-rest.uri = http://127.0.0.1:9001/iceberg
gravitino.iceberg-rest.s3-access-key-id = xx
gravitino.iceberg-rest.s3-secret-access-key = xx
gravitino.iceberg-rest.s3-region = xx
gravitino.iceberg-rest.credential-providers = s3-secret-key
gravitino.iceberg-rest.header.X-Iceberg-Access-Delegation = vended-credentials
```

如果客户端请求凭证分发，IRC1 也必须配置 S3 配置。

:::caution
如果 IRC2 不强制授权，保持 `gravitino.iceberg-rest.disable-rest-authz=true` 会导致操作处于无保护状态。将其设置为 `false` 以在 IRC1 中强制授权。
:::

`data-access` 在 REST 客户端的 `/v1/config` 默认值中返回：

- `vended-credentials`：客户端应请求凭证分发（`X-Iceberg-Access-Delegation: vended-credentials`）。
- `remote-signing`：Gravitino 尚不支持此模式。

#### 自定义后端配置

| 配置项                            | 描述                                                                                                                   | 默认值 | 必填 |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.catalog-backend`      | Gravitino Iceberg REST 目录服务的目录后端。对于自定义目录后端，请使用值 **`custom`**。 | `memory`      | 是      |
| `gravitino.iceberg-rest.catalog-backend-impl` | 自定义目录实现的全限定类名，仅在 `catalog-backend` 为 `custom` 时生效。              | (无)        | 否       |

如果你想使用自定义的 Iceberg Catalog 作为 `catalog-backend`，你可以将相应的 jar 文件添加到 classpath 中，并通过指定 `catalog-backend-impl` 属性来加载自定义的 Iceberg Catalog 实现。

### 多目录配置

Gravitino Iceberg REST 服务器支持多个 catalog 后端，你可以使用 `catalog-config-provider` 来控制管理 catalog 后端配置的行为。

| 配置项                               | 描述                                                                                                                                                                                                                                                                                                                                      | 默认值            | 必填 |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|----------|
| `gravitino.iceberg-rest.catalog-config-provider` | catalog 配置提供程序的 className，Gravitino 提供了内置的 `static-config-provider` 和 `dynamic-config-provider`，你也可以开发一个实现了 `apache.gravitino.iceberg.service.provider.IcebergConfigProvider` 的自定义类，并将相应的 jar 文件添加到 Iceberg REST 服务的 classpath 目录中。 | `static-config-provider` | 否

使用 `static-config-provider` 管理文件中的 catalog 配置，该 catalog 配置在服务器启动时加载，且无法更改。
而 `dynamic-config-provider` 用于通过 Gravitino 服务器管理 catalog 配置，您可以动态地添加、删除和更改 catalog 配置。

#### 静态目录配置提供程序

静态 catalog 配置提供者从 Gravitino Iceberg REST 服务器的配置文件中获取 catalog 配置。你可以使用 `gravitino.iceberg-rest.<param name>=<value>` 来配置默认 catalog。对于其他的，使用 `gravitino.iceberg-rest.catalog.<catalog name>.<param name>=<value>` 来配置名为 `catalog name` 的 catalog。

例如，你可以配置三个不同的目录，分别是默认目录、`hive_backend` 目录和 `jdbc_backend` 目录。

```text
gravitino.iceberg-rest.catalog-backend = jdbc
gravitino.iceberg-rest.uri = jdbc:postgresql://127.0.0.1:5432
gravitino.iceberg-rest.warehouse = hdfs://127.0.0.1:9000/user/hive/warehouse-postgresql
...
gravitino.iceberg-rest.catalog.hive_backend.catalog-backend = hive
gravitino.iceberg-rest.catalog.hive_backend.uri = thrift://127.0.0.1:9084
gravitino.iceberg-rest.catalog.hive_backend.warehouse = /user/hive/warehouse-hive/
...
gravitino.iceberg-rest.catalog.jdbc_backend.catalog-backend = jdbc
gravitino.iceberg-rest.catalog.jdbc_backend.uri = jdbc:mysql://127.0.0.1:3306/
gravitino.iceberg-rest.catalog.jdbc_backend.warehouse = hdfs://127.0.0.1:9000/user/hive/warehouse-mysql
...
```

#### 动态目录配置提供程序

动态 catalog 配置提供程序从 Gravitino 服务器检索 catalog 配置，并且 catalog 配置可以动态更新。

| 配置项                                          | 描述                                                                                                                                                                                         | 默认值 | 是否必填                                                     |
|-------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|--------------------------------------------------------------|
| `gravitino.iceberg-rest.gravitino-uri`                      | Gravitino 服务器地址的 uri，仅在 `catalog-config-provider` 为 `dynamic-config-provider` 时生效。作为内嵌在 Gravitino 服务器中的辅助服务运行时不需要。         | (none)        | 是，在独立模式下使用 `dynamic-config-provider` 时 |
| `gravitino.iceberg-rest.gravitino-metalake`                 | `dynamic-config-provider` 用于向 Gravitino 发起请求的 metalake 名称，仅在 `catalog-config-provider` 为 `dynamic-config-provider` 时生效。                                               | (none)        | 是，使用 `dynamic-config-provider` 时                    |
| `gravitino.iceberg-rest.default-catalog-name`               | 如果 Iceberg REST 客户端未显式指定 catalog 名称，Iceberg REST 服务器使用的默认 catalog 名称。仅在 `catalog-config-provider` 为 `dynamic-config-provider` 时生效。 | (none)        | 否                                                           |
| `gravitino.iceberg-rest.catalog-cache-eviction-interval-ms` | Catalog 缓存驱逐间隔。                                                                                                                                                                    | 3600000       | 否                                                           |

:::tip
使用 `dynamic-config-provider` 时，行为会根据部署模式而有所不同：

- **辅助模式**（内嵌于 Gravitino 服务器）：服务使用内部接口直接访问 Gravitino。`gravitino-uri` 配置**非必需**，若提供则会被忽略。
- **独立模式**：服务使用 HTTP/REST API 与 Gravitino 服务器进行通信。`gravitino-uri` 配置是**必需的**，并且必须指向您的 Gravitino 服务器。

授权功能仅在辅助模式下运行时可用。
:::
 
```text
gravitino.iceberg-rest.catalog-cache-eviction-interval-ms = 300000
gravitino.iceberg-rest.catalog-config-provider = dynamic-config-provider
# gravitino-uri is only required when running as a standalone server
# When running as an auxiliary service (embedded in Gravitino server), this is not needed
gravitino.iceberg-rest.gravitino-uri = http://127.0.0.1:8090
gravitino.iceberg-rest.gravitino-metalake = test
```

假设在 Gravitino 服务器中有两个 Iceberg catalog `hive_catalog` 和 `jdbc_catalog`，`dynamic-config-provider` 将在内部轮询 catalog 属性，并在 Iceberg REST 服务器端注册 `hive_catalog` 和 `jdbc_catalog`。Dynamic config provider 将获取所有 catalog 属性，对于以 `gravitino.bypass.` 前缀开头的属性，它将移除该前缀并使用剩余部分作为 catalog 属性的键。

#### 客户端目录选择

在 Iceberg REST 客户端配置中，通过将 `warehouse` 设置为特定的 catalog 名称来访问不同的 catalog。如果您未指定 `warehouse`，则将使用默认 catalog。例如，假设有三个 catalog 后端：默认 catalog、`hive_catalog` 和 `jdbc_catalog`，考虑 SparkSQL 的情况：

```shell
./bin/spark-sql -v \
...
--conf spark.sql.catalog.default_rest_catalog.type=rest  \
--conf spark.sql.catalog.default_rest_catalog.uri=http://127.0.0.1:9001/iceberg/ \
...
--conf spark.sql.catalog.hive_backend_rest_catalog.type=rest  \
--conf spark.sql.catalog.hive_backend_rest_catalog.uri=http://127.0.0.1:9001/iceberg/ \
--conf spark.sql.catalog.hive_backend_rest_catalog.warehouse=hive_backend \
...
--conf spark.sql.catalog.jdbc_backend_rest_catalog.type=rest  \
--conf spark.sql.catalog.jdbc_backend_rest_catalog.uri=http://127.0.0.1:9001/iceberg/ \
--conf spark.sql.catalog.jdbc_backend_rest_catalog.warehouse=jdbc_backend \
...
```

在 Spark SQL 端，你可以使用 `default_rest_catalog` 来访问默认的 catalog 后端，并分别使用 `hive_backend_rest_catalog` 和 `jdbc_backend_rest_catalog` 来访问 `hive_backend` 和 `jdbc_backend` catalog 后端。

### 安全与访问控制

#### OAuth2

有关如何启用 OAuth2，请参阅 [OAuth2 配置](./security/how-to-authenticate#server-configuration)。

When enabling OAuth2 and leveraging a dynamic configuration provider to retrieve catalog information from the Gravitino server, use the following configuration parameters to establish OAuth2 authentication for secure communication with the Gravitino server:

| 配置项                                   | 描述                                                                                      | 默认值         | 必填          |
|------------------------------------------------------|--------------------------------------------------------------------------------------------------|-----------------------|-------------------|
| `gravitino.iceberg-rest.gravitino-auth-type`         | 与 Gravitino 服务器通信的认证类型。支持的值：`simple`、`oauth2`。 | `simple`              | 否                |
| `gravitino.iceberg-rest.gravitino-simple.user-name`  | 使用 `simple` 认证类型时的用户名。                                                      | `iceberg-rest-server` | 否                |
| `gravitino.iceberg-rest.gravitino-oauth2.server-uri` | OAuth2 服务器 uri 地址。                                                                   | (none)                | 是，对于 `oauth2` |
| `gravitino.iceberg-rest.gravitino-oauth2.credential` | 请求 OAuth2 令牌的凭证。                                                      | (none)                | 是，对于 `oauth2` |
| `gravitino.iceberg-rest.gravitino-oauth2.token-path` | 默认 OAuth 服务器的令牌路径。                                                  | (none)                | 是，对于 `oauth2` |
| `gravitino.iceberg-rest.gravitino-oauth2.scope`      | 请求 OAuth2 令牌的作用域。                                                           | (none)                | 是，对于 `oauth2` |

以下是如何为 Gravitino Iceberg REST 服务器启用 OAuth2 的示例：

```text
gravitino.authenticators = oauth
gravitino.authenticator.oauth.serviceAudience = test
gravitino.authenticator.oauth.defaultSignKey = xx
gravitino.authenticator.oauth.tokenPath = oauth2/token
gravitino.authenticator.oauth.serverUri = http://localhost:8177
```

如果在独立模式下使用 `dynamic-config-provider`，请添加额外配置：

```text
gravitino.iceberg-rest.catalog-config-provider = dynamic-config-provider
gravitino.iceberg-rest.gravitino-metalake = test
# gravitino-uri is required when running in standalone mode
gravitino.iceberg-rest.gravitino-uri = http://127.0.0.1:8090
gravitino.iceberg-rest.gravitino-auth-type = oauth2
gravitino.iceberg-rest.gravitino-oauth2.server-uri = http://localhost:8177
gravitino.iceberg-rest.gravitino-oauth2.credential = test:test
gravitino.iceberg-rest.gravitino-oauth2.token-path = oauth2/token
gravitino.iceberg-rest.gravitino-oauth2.scope = test
```

如果您使用 Spark 访问启用了 OAuth2 的 Iceberg REST catalog，请参考以下配置：

```shell
./bin/spark-sql -v \
--conf spark.jars=/Users/fanng/deploy/demo/jars/iceberg-spark-runtime-3.5_2.12-1.11.0.jar \
--conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
--conf spark.sql.catalog.rest=org.apache.iceberg.spark.SparkCatalog \
--conf spark.sql.catalog.rest.rest.auth.type=oauth2 \
--conf spark.sql.catalog.rest.type=rest  \
--conf spark.sql.catalog.rest.uri=http://127.0.0.1:9001/iceberg/ \
--conf spark.sql.catalog.rest.prefix=${catalog_name} \
--conf spark.sql.catalog.rest.credential=test:test \
--conf spark.sql.catalog.rest.scope=test \
--conf spark.sql.catalog.rest.oauth2-server-uri=http://localhost:8177/oauth2/token
```

##### Iceberg REST 客户端的 OAuth 2.0 令牌刷新

在访问 Gravitino Iceberg REST Catalog (IRC) 时，某些查询引擎可能会遇到 OAuth 2.0 令牌刷新挑战。
这通常与不支持完整令牌交换的身份提供商有关，或者与子会话继承父会话过期策略的身份验证模型有关。

以下 Apache Iceberg 变更与此行为相关：

| 版本         | 变更                                                                                                                                                                                                    |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Iceberg 1.11.0+ | 支持禁用令牌交换、使用客户端凭证续订令牌，并确保子 `AuthSession` 实例使用自身的过期时间，而不是继承父会话的过期时间。 |

**Apache Iceberg OAuth 2.0 配置**

**Spark**

Set the following catalog property to disable token exchange:

```text
spark.sql.catalog.${catalog_name}.token-exchange-enabled=false
```

**Flink**

Set the following catalog property to disable token exchange:

```sql
  'token-exchange-enable' = 'false'
```

**Trino**

使用 Trino 479 或更高版本，并在目录配置中设置以下属性：

```properties
iceberg.rest-catalog.session=NONE
iceberg.rest-catalog.oauth2.token-exchange-enabled=false
```

省略 `iceberg.rest-catalog.session=NONE`，因为 `NONE` 是默认值。

#### HTTPS

请参考 [HTTPS 配置](./security/how-to-use-https.md#apache-iceberg-rest-service-configuration) 了解如何为 Gravitino Iceberg REST 服务器启用 HTTPS。

#### 后端认证

对于 JDBC catalog 后端，使用 `gravitino.iceberg-rest.jdbc-user` 和 `gravitino.iceberg-rest.jdbc-password` 来认证 JDBC 元数据存储连接。使用 `gravitino.iceberg-rest.authentication.type` 来指定 catalog 后端如何访问仓库存储。当仓库位于 HDFS 上时，将其设置为 `kerberos` 或 `simple`，并配置 `gravitino.iceberg-rest.authentication.kerberos.principal` 和 `gravitino.iceberg-rest.authentication.kerberos.keytab-uri` 以进行 Kerberos 认证。

对于 Hive catalog 后端，`gravitino.iceberg-rest.authentication.type` 同时控制 Hive Metastore 和 HDFS 的访问。使用 Kerberos 时，还需配置 `gravitino.iceberg-rest.hive.metastore.sasl.enabled` 以及相关的 Hive Metastore Kerberos 属性。

详细的配置项如下：

| 配置项                                                        | 描述                                                                                                             | 默认值 | 是否必填                                                                                                                                            |
|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `gravitino.iceberg-rest.authentication.type`                              | 访问 HDFS 仓库的认证类型。对于 Hive 和 JDBC catalog 后端，支持 `kerberos` 和 `simple`。 | `simple`      | 否                                                                                                                                                  |
| `gravitino.iceberg-rest.authentication.impersonation-enable`              | 是否为 Iceberg catalog 启用模拟。                                                                | `false`       | 否                                                                                                                                                  |
| `gravitino.iceberg-rest.hive.metastore.sasl.enabled`                      | 连接到 Kerberos Hive Metastore 时是否启用 SASL。                                                    | `false`       | 否。当 `gravitino.iceberg-rest.authentication.type` 为 `kerberos` 时，在大多数情况下设置为 true（某些部署改用 SSL，但这种情况很少见）。 |
| `gravitino.iceberg-rest.authentication.kerberos.principal`                | Kerberos 认证的 principal。                                                                              | (none)        | 是，如果 `gravitino.iceberg-rest.authentication.type` 为 `kerberos`。                                                                                 |
| `gravitino.iceberg-rest.authentication.kerberos.keytab-uri`               | Kerberos 认证的 keytab URI。                                                                      | (none)        | 是，如果 `gravitino.iceberg-rest.authentication.type` 为 `kerberos`。                                                                                 |
| `gravitino.iceberg-rest.authentication.kerberos.check-interval-sec`       | Iceberg catalog 的 Kerberos 凭据检查间隔。                                                      | 60            | 否                                                                                                                                                  |
| `gravitino.iceberg-rest.authentication.kerberos.keytab-fetch-timeout-sec` | 从 `authentication.kerberos.keytab-uri` 获取 Kerberos keytab 的获取超时时间。                             | 60            | 否                                                                                                                                                  |

Kerberos 适用于 **HDFS 仓库** 访问。

**带有 Kerberos 的 Hive 后端** — 向 Hive Metastore 和 HDFS 进行身份验证：

```text
gravitino.iceberg-rest.catalog-backend = hive
gravitino.iceberg-rest.uri = thrift://127.0.0.1:9083
gravitino.iceberg-rest.warehouse = hdfs://127.0.0.1:9000/user/hive/warehouse-hive

gravitino.iceberg-rest.authentication.type = kerberos
gravitino.iceberg-rest.authentication.kerberos.principal = iceberg@EXAMPLE.COM
gravitino.iceberg-rest.authentication.kerberos.keytab-uri = file:///etc/security/keytabs/iceberg.keytab

gravitino.iceberg-rest.hive.metastore.sasl.enabled = true
gravitino.iceberg-rest.hive.metastore.kerberos.principal = hive/host.example.com@EXAMPLE.COM

gravitino.iceberg-rest.hadoop.security.authentication = kerberos
gravitino.iceberg-rest.dfs.namenode.kerberos.principal = hdfs/host.example.com@EXAMPLE.COM
```

**带有 Kerberos 保护的 HDFS 仓库的 JDBC 后端** — JDBC 凭证验证元数据存储；Kerberos 仅验证 HDFS 访问：

```text
gravitino.iceberg-rest.catalog-backend = jdbc
gravitino.iceberg-rest.jdbc-driver = org.postgresql.Driver
gravitino.iceberg-rest.uri = jdbc:postgresql://127.0.0.1:5432/iceberg
gravitino.iceberg-rest.jdbc-user = iceberg
gravitino.iceberg-rest.jdbc-password = secret
gravitino.iceberg-rest.jdbc-initialize = true
gravitino.iceberg-rest.warehouse = hdfs://127.0.0.1:9000/user/hive/warehouse-jdbc

gravitino.iceberg-rest.authentication.type = kerberos
gravitino.iceberg-rest.authentication.kerberos.principal = iceberg@EXAMPLE.COM
gravitino.iceberg-rest.authentication.kerberos.keytab-uri = file:///etc/security/keytabs/iceberg.keytab

gravitino.iceberg-rest.hadoop.security.authentication = kerberos
gravitino.iceberg-rest.dfs.namenode.kerberos.principal = hdfs/host.example.com@EXAMPLE.COM
```

将 `host.example.com` 和 `EXAMPLE.COM` 替换为您的 Hive/HDFS 主机名和 Kerberos realm。JDBC 后端不需要 Hive Metastore SASL 属性。

#### 凭证售卖

有关更多详细信息，请参阅 [凭证分发](./security/credential-vending.md)。

#### 访问控制

##### 先决条件

要在 Iceberg REST 服务中使用访问控制：

1. Iceberg REST 服务必须作为 Gravitino 服务器内的辅助服务运行（访问控制不支持独立模式）
2. 通过设置 `gravitino.authorization.enable = true` 在 Gravitino 服务器中启用授权
3. 使用[动态配置提供程序](#dynamic-catalog-configuration-provider)从 Gravitino 检索 catalog 配置

:::note
Iceberg REST Catalog (IRC) 的访问控制仅在作为嵌入在 Gravitino 服务器中的辅助服务运行时受支持。独立的 Iceberg REST 服务器部署不支持访问控制功能。

当作为辅助服务运行时，`gravitino.iceberg-rest.gravitino-uri` 配置**非必需**。该服务将使用内部接口直接访问 Gravitino，从而提供更好的性能，并避免基于 HTTP 的通信。
:::

有关在 Gravitino 中如何配置授权、创建角色和授予权限的详细信息，请参阅 [Access Control](./security/access-control.md)。

##### 访问控制流

当启用访问控制时：

1. 客户端通过 Iceberg REST 服务进行身份验证（目前我们支持 Basic auth 和 OAuth2）
2. Iceberg REST 服务将已认证的用户身份、目标元数据对象和请求的操作发送到 Gravitino 服务器进行授权验证
3. Gravitino 验证用户是否具有在指定元数据对象上执行该操作所需的权限
4. 授权成功后，Iceberg REST 服务将执行该操作；否则，返回授权错误

有关完整的权限列表及如何授予权限，请参阅[访问控制](./security/access-control.md)。


### 存储

如果未配置 `gravitino.iceberg-rest.io-impl`，Iceberg REST 服务将使用
`org.apache.iceberg.io.ResolvingFileIO`，它会选择一个 `FileIO` 实现，基于
URI scheme：

- S3：`s3`、`s3a` 或 `s3n`
- OSS：`oss`
- GCS：`gs` 或 `gcs`
- ADLS：`abfs`、`abfss`、`wasb` 或 `wasbs`
- 要覆盖默认设置，请显式配置 `gravitino.iceberg-rest.io-impl`。
- 确保相应的存储包在 Iceberg REST 服务器类路径中可用。

#### S3

| 配置项                            | 描述                                                                                                                                                                                                         | 默认值                           | 必选 |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|----------|
| `gravitino.iceberg-rest.io-impl`              | Iceberg 中 `FileIO` 的 IO 实现。将其设置为 `org.apache.iceberg.aws.s3.S3FileIO` 以显式使用 S3FileIO。                                                                                           | `org.apache.iceberg.io.ResolvingFileIO` | 否       |
| `gravitino.iceberg-rest.s3-endpoint`          | S3 服务的备用端点。可用于具有不同端点的任何兼容 S3 的对象存储服务的 S3FileIO，或访问虚拟私有云中的私有 S3 端点。 | (none)                                  | 否       |
| `gravitino.iceberg-rest.s3-region`            | S3 服务的区域，例如 `us-west-2`。                                                                                                                                                                     | (none)                                  | 否       |
| `gravitino.iceberg-rest.s3-path-style-access` | 是否为 S3 使用路径风格访问。                                                                                                                                                                            | false                                   | 否       |

对于不由 Gravitino 管理的其他 Iceberg s3 属性（如 `s3.sse.type`），你可以直接通过 `gravitino.iceberg-rest.s3.sse.type` 进行配置。

有关凭证相关配置，请参阅 [S3 凭证](./security/credential-vending.md#s3-credentials)。

:::info
- 对于 JDBC catalog 后端，将 `gravitino.iceberg-rest.warehouse` 参数设置为 `s3://{bucket_name}/${prefix_name}`。 
- 对于 Hive catalog 后端，将 `gravitino.iceberg-rest.warehouse` 设置为 `s3a://{bucket_name}/${prefix_name}`。 
- 此外，下载 [Gravitino Iceberg AWS bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-aws-bundle) 并将其放入 Iceberg REST 服务器的 classpath 中。
:::

#### OSS

| 配置项                    | 描述                                                                                                                     | 默认值                           | 必填 |
|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|----------|
| `gravitino.iceberg-rest.io-impl`      | Iceberg 中 `FileIO` 的 IO 实现。将其设置为 `org.apache.iceberg.aliyun.oss.OSSFileIO` 以显式使用 OSSFileIO。 | `org.apache.iceberg.io.ResolvingFileIO` | 否       |
| `gravitino.iceberg-rest.oss-endpoint` | 阿里云 OSS 服务的端点。                                                                                             | (无)                                  | 否       |
| `gravitino.iceberg-rest.oss-region`   | OSS 服务的区域，如 `oss-cn-hangzhou`，仅在 `credential-providers` 为 `oss-token` 时使用。                    | (无)                                  | 否       |

对于不由 Gravitino 管理的其他 Iceberg OSS 属性（如 `client.security-token`），你可以直接通过 `gravitino.iceberg-rest.client.security-token` 进行配置。

有关凭证相关配置，请参阅 [OSS 凭证](./security/credential-vending.md#oss-credentials)。

下载 [Gravitino Iceberg Aliyun bundle jar](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-aliyun-bundle) 并将其放入 Iceberg REST 服务器的 classpath 中。有关 classpath 的详细信息，请参阅 [包布局](#package-layout)。

:::info
请将 `gravitino.iceberg-rest.warehouse` 参数设置为 `oss://{bucket_name}/${prefix_name}`。
:::

#### GCS

支持使用静态 GCS 凭据文件或生成 GCS 令牌来访问 GCS 数据。

| 配置项                                | 描述                                                                                                                  | 默认值                           | 必填 |
|---------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|----------|
| `gravitino.iceberg-rest.io-impl`                  | Iceberg 中 `FileIO` 的 IO 实现。将其设置为 `org.apache.iceberg.gcp.gcs.GCSFileIO` 以显式使用 GCSFileIO。 | `org.apache.iceberg.io.ResolvingFileIO` | 否       |
| `gravitino.iceberg-rest.gcs-service-account-file` | GCS 服务账号 JSON 文件的路径。用于服务端 FileIO 和 `gcs-token` 凭证分发。               | GCS 应用默认凭证。     | 否       |

对于其他不由 Gravitino 管理的 Iceberg GCS 属性（如 `gcs.project-id`），你可以直接通过 `gravitino.iceberg-rest.gcs.project-id` 来配置它。

有关凭据相关配置，请参阅 [GCS 凭据](./security/credential-vending.md#gcs-credentials)。

:::note
当设置了 `gcs-service-account-file` 时，Gravitino 会在目录初始化时加载它，并为 FileIO 注入 Iceberg `gcs.oauth2.token`。IRC 目录缓存会在令牌过期前驱逐该目录，以便下一次请求重新创建目录并生成新的令牌。如果未设置，则使用应用默认凭据（例如 GCE 元数据或 `GOOGLE_APPLICATION_CREDENTIALS`）。
:::

:::info
请将 `gravitino.iceberg-rest.warehouse` 设置为 `gs://{bucket_name}/${prefix_name}`，并下载 [Gravitino Iceberg gcp bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-gcp-bundle) 并将其放置到 Gravitino Iceberg REST 服务器的 classpath 中，对于辅助服务器放置在 `iceberg-rest-server/libs`，对于独立服务器放置在 `libs`。
:::

#### ADLS

| 配置项               | 描述                                                                                                                         | 默认值                           | 必填 |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|----------|
| `gravitino.iceberg-rest.io-impl` | Iceberg 中 `FileIO` 的 IO 实现。将其设置为 `org.apache.iceberg.azure.adlsv2.ADLSFileIO` 以显式使用 ADLSFileIO。 | `org.apache.iceberg.io.ResolvingFileIO` | 否       |

对于 Gravitino 未管理的其他 Iceberg ADLS 属性，如 `adls.read.block-size-bytes`，你可以直接通过 `gravitino.iceberg-rest.adls.read.block-size-bytes` 进行配置。

请参阅 [ADLS 凭据](./security/credential-vending.md#adls-credentials) 了解凭据相关的配置。

:::info
请将 `gravitino.iceberg-rest.warehouse` 设置为 `abfs[s]://{container-name}@{storage-account-name}.dfs.core.windows.net/{path}`，并下载 [Gravitino Iceberg Azure bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-azure-bundle) 并将其放置在 Iceberg REST 服务器的 classpath 中。
:::

#### HDFS

将 HDFS 配置文件放置到 Iceberg REST 服务器的 classpath 中，对于 Gravitino 服务器包是 `iceberg-rest-server/conf`，对于独立的 Gravitino Iceberg REST 服务器包是 `conf`。当写入 HDFS 时，Gravitino Iceberg REST catalog 服务只能以指定的 HDFS 用户身份操作，不支持代理到其他 HDFS 用户。有关更多详细信息，请参阅 [Access Apache Hadoop](gravitino-server-config.md#access-apache-hadoop)。

:::info
基于 Hadoop 2.10.x 构建。访问 Hadoop 3.x 集群时可能会出现兼容性问题。
:::

#### 其他存储

对于 Gravitino 不直接管理的存储，通过自定义 catalog 属性进行配置。

| 配置项               | 描述                                                                                                               | 默认值                           | 必填 |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|----------|
| `gravitino.iceberg-rest.io-impl` | Iceberg 中 `FileIO` 的 IO 实现。使用全限定类名以覆盖默认实现。 | `org.apache.iceberg.io.ResolvingFileIO` | 否       |

要将诸如 `security-token` 的自定义属性传递给您自定义的 `FileIO`，请通过 `gravitino.iceberg-rest.security-token` 进行配置。当调用 `FileIO` 的 initialize 方法时，`security-token` 会包含在属性中。

:::info
请将 `gravitino.iceberg-rest.warehouse` 参数设置为 `{storage_prefix}://{bucket_name}/${prefix_name}`。此外，请下载相应的 jar 包到 Iceberg REST 服务器的 classpath 中，辅助服务器对应 `iceberg-rest-server/libs`，独立服务器对应 `libs`。
:::

### 功能配置

#### 视图

在使用 JDBC catalog 后端且 schema 版本为 `V1` 时，支持视图操作。默认的 schema 版本现在为 `V1`，因此视图支持开箱即用。Iceberg 将在首次重启时自动迁移数据库 schema，并在所有后续重启时检测该迁移。

| 配置项                           | 描述                                                                                                         | 默认值 | 必填 |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.jdbc-schema-version` | JDBC catalog 后端的 schema 版本。默认为 `V1` 以启用视图操作。设置为 `V0` 可选择退出。 | `V1`          | 否       |

#### 附加 Iceberg Catalog 属性

添加在 [Iceberg 目录属性](https://iceberg.apache.org/docs/1.10.0/configuration/#catalog-properties) 中定义的其他属性。
以 `clients` 属性为例：

| 配置项               | 描述                          | 默认值 | 必填 |
|----------------------------------|--------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.clients` | 目录的客户端池大小。 | `2`           | 否       |

:::info
`catalog-impl` 无效。
:::

#### 事件监听器

Gravitino 为表操作生成前置事件和后置事件，并提供可插拔的事件监听器，允许您注入自定义逻辑。有关更多详细信息，请参阅[事件监听器配置](gravitino-server-config.md#event-listener-configuration)。

#### 审计日志

Gravitino 提供了一种可插拔的审计日志机制，请参阅 [审计日志配置](gravitino-server-config.md#audit-log-configuration)。

#### 指标存储

Gravitino 提供了一个可插拔的指标存储接口，用于存储和删除 Iceberg 指标。开发一个实现 `org.apache.gravitino.iceberg.service.metrics.IcebergMetricsStore` 的类，并将相应的 jar 文件添加到 Iceberg REST 服务 classpath 目录中。

| 配置项                              | 描述                                                                                                                         | 默认值 | 必填 |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.metricsStore`           | Iceberg 指标存储类名。                                                                                             | (无)        | 否       |
| `gravitino.iceberg-rest.metricsStoreRetainDays` | 在存储中保留 Iceberg 指标的天数，不大于 0 的值表示永久保留。                                     | -1            | 否       |
| `gravitino.iceberg-rest.metricsQueueCapacity`   | 在存储到持久化存储之前临时存储指标的队列大小。当队列满时，指标将被丢弃。 | 1000          | 否       |

如果你想使用 jdbc 作为指标存储，可以将 `gravitino.iceberg-rest.metricsStore` 设置为 `jdbc`，并设置以下配置以连接到数据库。
使用 `scripts` 目录中的 sql 脚本初始化数据库。
将相应的 JDBC 驱动程序下载到 `iceberg-rest-server/libs` 目录中。

| 配置项                                  | 描述                                                                                                                                         | 默认值 | 必填 |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.jdbc-metrics.url`           | JDBC 连接地址，例如用于 Postgres 的 `jdbc:postgresql://127.0.0.1:5432/database`，或用于 mysql 的 `jdbc:mysql://127.0.0.1:3306/database`。 | (none)        | 是      |
| `gravitino.iceberg-rest.jdbc-metrics.jdbc-user`     | JDBC 连接的用户名。                                                                                                                | (none)        | 否       |
| `gravitino.iceberg-rest.jdbc-metrics.jdbc-password` | JDBC 连接的密码。                                                                                                                | (none)        | 否       |
| `gravitino.iceberg-rest.jdbc-metrics.jdbc-driver`   | 用于 MySQL 的 `com.mysql.jdbc.Driver` 或 `com.mysql.cj.jdbc.Driver`，用于 PostgreSQL 的 `org.postgresql.Driver`。                                            | (none)        | 是      |

#### 表元数据缓存

Gravitino 具备一个可插拔的缓存系统，用于更新或检索缓存中的表元数据。它会对照 catalog 后端验证表元数据的位置，以确保缓存数据的正确性。

| 配置项                                           | 描述                                                                                                                                                                           | 默认值                                                       | 必填 |
|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|----------|
| `gravitino.iceberg-rest.table-metadata-cache-impl`           | 表元数据缓存的实现。如果 `catalog-backend` 是 `rest` 目录，或者是没有 `SupportsMetadataLocation` 接口的 `custom` 目录，则设置为空字符串("")。 | `org.apache.gravitino.iceberg.common.cache.LocalTableMetadataCache` | 否       |
| `gravitino.iceberg-rest.table-metadata-cache-capacity`       | 表元数据缓存的容量。                                                                                                                                             | 1000                                                                | 否       |
| `gravitino.iceberg-rest.table-metadata-cache-expire-minutes` | 表元数据缓存的过期时间（以分钟为单位）。                                                                                                                         | 60                                                                  | 否       |

Gravitino 提供了内置的 `org.apache.gravitino.iceberg.common.cache.LocalTableMetadataCache` 用于在内存中存储缓存数据。你也可以通过实现 `org.apache.gravitino.iceberg.common.cache.TableMetadataCache` 接口来实现自定义的表元数据缓存。

#### 扫描计划缓存

Gravitino 缓存扫描计划结果，以加速具有相同参数的重复查询。该缓存使用快照 ID 作为缓存键的一部分，因此针对不同快照的查询不会使用过期的缓存数据。

计划扫描响应遵循 Iceberg 1.11 REST API：已完成的计划仅返回结构化的 `file-scan-tasks`。不再输出旧版 `plan-tasks` JSON 字符串（由某些 Iceberg 1.9.x–1.10.x 客户端使用）。

| 配置项                                      | 描述                                              | 默认值 | 必填 |
|---------------------------------------------------------|----------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.scan-plan-cache-impl`           | 扫描计划缓存的实现。               | (none)        | 否       |
| `gravitino.iceberg-rest.scan-plan-cache-capacity`       | 扫描计划缓存的容量。                     | 200           | 否       |
| `gravitino.iceberg-rest.scan-plan-cache-expire-minutes` | 扫描计划缓存的过期时间（以分钟为单位）。 | 60            | 否       |

扫描计划缓存使用快照 ID 作为缓存键的一部分，确保在表数据发生变化时自动失效。这可以为重复查询（如仪表板刷新或 BI 工具查询）提供显著的加速。

Gravitino 提供了内置的 `org.apache.gravitino.iceberg.service.cache.LocalScanPlanCache` 用于在内存中存储缓存数据。也可以通过实现 `org.apache.gravitino.iceberg.service.cache.ScanPlanCache` 接口来实现自定义的扫描计划缓存。

#### 扩展包

| 配置项                          | 描述                                                  | 默认值 | 必填 |
|---------------------------------------------|--------------------------------------------------------------|---------------|----------|
| `gravitino.iceberg-rest.extension-packages` | 以逗号分隔的待扩展 Iceberg REST API 包列表。 | (无)        | 否       |

### 操作

#### 健康检查端点

Iceberg REST 服务器公开了三个健康检查端点，遵循与主 Gravitino 服务器相同的 [MicroProfile Health](https://microprofile.io/project/eclipse/microprofile-health) 语义。所有端点均免于身份验证。就绪探针检查 `IcebergCatalogWrapperManager` 是否已初始化。它不执行任何 I/O 操作，也没有可配置的超时时间。

| 端点                    | 描述                                                                                                               | HTTP 状态 |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------|-------------|
| `GET /iceberg/health/live`  | 存活探针。当 HTTP 线程可以响应且未观察到 OOM 时返回 200；观察到 OOM 后返回 503。     | 200 / 503   |
| `GET /iceberg/health/ready` | 就绪探针。当 catalog wrapper manager 已初始化且未观察到 OOM 时返回 200；否则返回 503。 | 200 / 503   |
| `GET /iceberg/health`       | 聚合检查。当存活和就绪检查均通过时返回 200；任何检查失败时返回 503。                             | 200 / 503   |

根级别名也可用于需要在已知根路径下进行探测的全局流量管理器：

| 别名               | 转发至                 |
|---------------------|-----------------------------|
| `GET /health`       | `GET /iceberg/health`       |
| `GET /health/live`  | `GET /iceberg/health/live`  |
| `GET /health/ready` | `GET /iceberg/health/ready` |
| `GET /health.html`  | `GET /iceberg/health`       |

**响应格式：**

在观察到 `OutOfMemoryError` 之后，所有健康端点和根别名将返回 503 并带有 `jvm` 故障，直到重启。有关检测范围，请参见 [内存溢出故障](health-and-readiness.md#out-of-memory-failures)。

所有端点返回的 JSON 主体结构与主 Gravitino 服务器相同。`code` 字段始终为 `0`。`status` 为 `UP` 或 `DOWN`。存活探针报告 `httpServer`，就绪探针报告 `catalogWrapperManager`。

健康响应 (HTTP 200)：

```json
{
  "code": 0,
  "status": "UP",
  "checks": [
    { "name": "httpServer", "status": "UP", "details": {} },
    { "name": "catalogWrapperManager", "status": "UP", "details": {} }
  ]
}
```

不健康响应 (HTTP 503):

```json
{
  "code": 0,
  "status": "DOWN",
  "checks": [
    { "name": "httpServer", "status": "UP", "details": {} },
    { "name": "catalogWrapperManager", "status": "DOWN", "details": { "reason": "catalog wrapper manager not initialized" } }
  ]
}
```

#### 内存设置

Iceberg REST 服务器使用 `GRAVITINO_MEM` 作为 JVM 堆/元空间标志。默认值：`-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m`。启动脚本会将 `GRAVITINO_MEM` 追加到 `JAVA_OPTS`；设置它以调整堆/元空间大小。
调优示例：
- 开发环境：`GRAVITINO_MEM="-Xms1g -Xmx1g -XX:MaxMetaspaceSize=512m"`
- 中等工作负载：`GRAVITINO_MEM="-Xms4g -Xmx4g -XX:MaxMetaspaceSize=1g"`
- 更高的并发或目录数量：相应地增加堆和元空间大小。

## 服务启动与验证

### 辅助服务

在 Gravitino 服务器中启动 Iceberg REST 服务作为辅助服务：

```shell
./bin/gravitino.sh start
```

### 独立服务器

启动独立的 Iceberg REST 服务器：

```shell
./bin/gravitino-iceberg-rest-server.sh start
```

### 服务验证

验证服务是否正在运行：

```shell
curl http://127.0.0.1:9001/iceberg/v1/config
```

示例响应：`{"defaults":{},"overrides":{}, "endpoints":["GET /v1/{prefix}/namespaces", ...]}%`。

## Docker

### 容器启动

在 Docker 容器中运行 Iceberg REST 服务器：

```shell
docker run -d -p 9001:9001 apache/gravitino-iceberg-rest:latest
```

### 环境变量

Docker 镜像默认支持本地存储。
对于云存储或远程存储，请通过以下环境变量配置相应的 [storage](#storage) 设置：

| 环境变量                                       | 配置项                                        |
|------------------------------------------------------------|------------------------------------------------------------|
| `GRAVITINO_ICEBERG_REST_HOST`                              | `gravitino.iceberg-rest.host`                              |
| `GRAVITINO_ICEBERG_REST_HTTP_PORT`                         | `gravitino.iceberg-rest.httpPort`                          |
| `GRAVITINO_ICEBERG_REST_URI`                               | `gravitino.iceberg-rest.uri`                               |
| `GRAVITINO_ICEBERG_REST_IO_IMPL`                           | `gravitino.iceberg-rest.io-impl`                           |
| `GRAVITINO_ICEBERG_REST_CATALOG_BACKEND`                   | `gravitino.iceberg-rest.catalog-backend`                   |
| `GRAVITINO_ICEBERG_REST_JDBC_DRIVER`                       | `gravitino.iceberg-rest.jdbc-driver`                       |
| `GRAVITINO_ICEBERG_REST_JDBC_USER`                         | `gravitino.iceberg-rest.jdbc-user`                         |
| `GRAVITINO_ICEBERG_REST_JDBC_PASSWORD`                     | `gravitino.iceberg-rest.jdbc-password`                     |
| `GRAVITINO_ICEBERG_REST_WAREHOUSE`                         | `gravitino.iceberg-rest.warehouse`                         |
| `GRAVITINO_ICEBERG_REST_REST_CLIENT_CONNECTION_TIMEOUT_MS` | `gravitino.iceberg-rest.rest-client-connection-timeout-ms` |
| `GRAVITINO_ICEBERG_REST_REST_CLIENT_SOCKET_TIMEOUT_MS`     | `gravitino.iceberg-rest.rest-client-socket-timeout-ms`     |
| `GRAVITINO_ICEBERG_REST_CREDENTIAL_PROVIDERS`              | `gravitino.iceberg-rest.credential-providers`              |
| `GRAVITINO_ICEBERG_REST_GCS_SERVICE_ACCOUNT_FILE`          | `gravitino.iceberg-rest.gcs-service-account-file`          |
| `GRAVITINO_ICEBERG_REST_S3_ACCESS_KEY`                     | `gravitino.iceberg-rest.s3-access-key-id`                  |
| `GRAVITINO_ICEBERG_REST_S3_SECRET_KEY`                     | `gravitino.iceberg-rest.s3-secret-access-key`              |
| `GRAVITINO_ICEBERG_REST_S3_ENDPOINT`                       | `gravitino.iceberg-rest.s3-endpoint`                       |
| `GRAVITINO_ICEBERG_REST_S3_REGION`                         | `gravitino.iceberg-rest.s3-region`                         |
| `GRAVITINO_ICEBERG_REST_S3_PATH_STYLE_ACCESS`              | `gravitino.iceberg-rest.s3-path-style-access`              |
| `GRAVITINO_ICEBERG_REST_S3_ROLE_ARN`                       | `gravitino.iceberg-rest.s3-role-arn`                       |
| `GRAVITINO_ICEBERG_REST_S3_EXTERNAL_ID`                    | `gravitino.iceberg-rest.s3-external-id`                    |
| `GRAVITINO_ICEBERG_REST_S3_TOKEN_SERVICE_ENDPOINT`         | `gravitino.iceberg-rest.s3-token-service-endpoint`         |
| `GRAVITINO_ICEBERG_REST_AZURE_STORAGE_ACCOUNT_NAME`        | `gravitino.iceberg-rest.azure-storage-account-name`        |
| `GRAVITINO_ICEBERG_REST_AZURE_STORAGE_ACCOUNT_KEY`         | `gravitino.iceberg-rest.azure-storage-account-key`         |
| `GRAVITINO_ICEBERG_REST_AZURE_TENANT_ID`                   | `gravitino.iceberg-rest.azure-tenant-id`                   |
| `GRAVITINO_ICEBERG_REST_AZURE_CLIENT_ID`                   | `gravitino.iceberg-rest.azure-client-id`                   |
| `GRAVITINO_ICEBERG_REST_AZURE_CLIENT_SECRET`               | `gravitino.iceberg-rest.azure-client-secret`               |
| `GRAVITINO_ICEBERG_REST_OSS_ACCESS_KEY`                    | `gravitino.iceberg-rest.oss-access-key-id`                 |
| `GRAVITINO_ICEBERG_REST_OSS_SECRET_KEY`                    | `gravitino.iceberg-rest.oss-secret-access-key`             |
| `GRAVITINO_ICEBERG_REST_OSS_ENDPOINT`                      | `gravitino.iceberg-rest.oss-endpoint`                      |
| `GRAVITINO_ICEBERG_REST_OSS_REGION`                        | `gravitino.iceberg-rest.oss-region`                        |
| `GRAVITINO_ICEBERG_REST_OSS_ROLE_ARN`                      | `gravitino.iceberg-rest.oss-role-arn`                      |
| `GRAVITINO_ICEBERG_REST_OSS_EXTERNAL_ID`                   | `gravitino.iceberg-rest.oss-external-id`                   |

### 已弃用的环境变量

使用替代的环境变量，而不是这些已弃用的名称。

| 已弃用的环境变量     | 新环境变量                         | 已弃用的版本 |
|--------------------------------------|---------------------------------------------------|--------------------|
| `GRAVITINO_CREDENTIAL_PROVIDER_TYPE` | `GRAVITINO_ICEBERG_REST_CREDENTIAL_PROVIDERS`     | 0.8.0-incubating   |
| `GRAVITINO_GCS_CREDENTIAL_FILE_PATH` | `GRAVITINO_ICEBERG_REST_GCS_SERVICE_ACCOUNT_FILE` | 0.8.0-incubating   |

### 自定义镜像构建

构建自定义镜像以添加配置或逻辑：

```shell
sh ./dev/docker/build-docker.sh --platform linux/arm64 --type iceberg-rest-server --image apache/gravitino-iceberg-rest --tag $tag
```

### 游乐场

在 [playground](./how-to-use-the-playground.md#apache-iceberg-rest-service) 中通过 Gravitino Iceberg REST catalog 服务尝试 Spark。

## 访问控制教程

使用 Gravitino 的动态配置提供程序为 Iceberg REST 服务器启用访问控制。

:::note
访问控制要求 Iceberg REST 服务器在 Gravitino 服务器中作为辅助服务运行。
独立部署不支持 Iceberg REST catalog 授权。
:::

完成以下步骤：

### 步骤 1：启用授权和动态配置提供程序

将以下内容添加到您的 Gravitino 服务器配置文件（`gravitino.conf`）中。
请注意，只有在 Gravitino 服务器内作为辅助服务运行 Iceberg REST 服务器时，才支持访问控制：

```properties
gravitino.authorization.enable = true
gravitino.authorization.serviceAdmins = adminUser

gravitino.iceberg-rest.catalog-config-provider = dynamic-config-provider
gravitino.iceberg-rest.gravitino-metalake = test
# Note: gravitino-uri is not required when running as an auxiliary service
# The service will use internal interfaces to access Gravitino
```

在更新配置后重启 Iceberg REST 服务器。

### 步骤 2：创建 Metalake

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "test"
}' http://localhost:8090/api/metalakes
```

### 步骤 3：创建目录

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
  "name": "catalog1",
  "type": "ICEBERG",
  "comment": "Iceberg catalog",
  "properties": {}
}' http://localhost:8090/api/metalakes/test/catalogs
```

### 步骤 4：创建角色并授予权限

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
   "name": "role1",
   "properties": {},
   "securableObjects": [
      {
         "fullName": "catalog1",
         "type": "CATALOG",
         "privileges": [
            {
               "name": "USE_CATALOG",
               "condition": "ALLOW"
            },
            {
               "name": "USE_SCHEMA",
               "condition": "ALLOW"
            },
            {
               "name": "SELECT_TABLE",
               "condition": "ALLOW"
            }
         ]
      }
   ]
}' http://localhost:8090/api/metalakes/test/roles
```

### 第 5 步：验证拒绝访问

在授予任何权限之前，验证该用户无法访问目录。尝试以 `user1` 身份列出表（替换为您实际的身份验证方法）：

```shell
curl -u user1:password -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:9001/iceberg/v1/catalog1/namespaces/default/tables
```

这应该返回一个指示权限不足的错误（例如 HTTP 403 Forbidden）。

### 步骤 6：向用户授予角色

现在将带有权限的角色授予用户：

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
-H "Content-Type: application/json" -d '{
    "roleNames": ["role1"]
}' http://localhost:8090/api/metalakes/test/permissions/users/user1/grant
```

### 步骤 7：验证已授予的访问权限

授予具有权限的角色后，以 `user1` 身份重复该请求：

```shell
curl -u user1:password -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:9001/iceberg/v1/catalog1/namespaces/default/tables
```

这次，请求应该会成功并返回表列表。

### 总结

- 启用授权并将配置提供者设置为 `dynamic-config-provider`。
- 创建一个 metalake。
- 创建一个 catalog。
- 创建一个角色并授予权限。
- 将角色分配给用户。

有关更多详细信息，请参阅[访问控制文档](./security/access-control.md)。
