---
slug: /how-to-install
license: This software is licensed under the Apache License version 2.
---
## 从二进制发行版安装

:::note
Apache Gravitino 支持在 Java 17 上运行，更高版本也应当可以运行，但尚未经过完整测试。请确保已安装 Java 并且
`JAVA_HOME` 已正确配置。要确认 Java 版本，请运行
`${JAVA_HOME}/bin/java -version` 命令。
:::

Gravitino 包同时包含 Gravitino 服务器和 Gravitino Iceberg REST 服务器。可以独立管理这些服务器，也可以在单个服务器上同时运行它们。

### 获取二进制发行版包

安装 Gravitino 之前，请确保已获得 Gravitino 二进制发行版包。可从 [GitHub](https://github.com/apache/gravitino/releases) 下载最新的 Gravitino 二进制发行版包。
如需自行构建，请按照 [如何构建 Gravitino](./how-to-build.md) 中的说明操作。

- 如果你使用 `./gradlew compileDistribution` 命令自行构建 Gravitino，可以在 `distribution/package` 和 `distribution/package-all` 目录中找到 Gravitino 二进制发行版包。这两个包的主要区别在于，`package-all` 包包含所有 catalog，包括 `catalogs-contrib` 文件夹下的 catalog，而 `package` 包仅包含 `catalogs` 文件夹下的主要 catalog。

- 如果你使用 `./gradlew assembleDistribution` 命令自行构建 Gravitino，可以在 `distribution` 目录中获取名为 `gravitino-<version>-bin.tar.gz` 的压缩 Gravitino 二进制发行版包，以及 sha256 校验和文件 `gravitino-<version>-bin.tar.gz.sha256`。此外，你还可以在 `distribution` 目录中获取名为 `gravitino-<version>-bin-all.tar.gz` 的完整压缩 Gravitino 二进制发行版包，以及 sha256 校验和文件 `gravitino-<version>-bin-all.tar.gz.sha256`。这两个包的主要区别在于，`-all` 包包含所有 catalog，包括 `catalogs-contrib` 文件夹下的 catalog，而普通包仅包含 `catalogs` 文件夹下的主要 catalog。

注意：**Apache Gravitino 在 GitHub releases 上仅发布 `gravitino-<version>-bin.tar.gz` 包，而 `gravitino-<version>-bin-all.tar.gz` 包仅面向有兴趣自行从源代码构建 Gravitino 的用户。**

Gravitino 二进制发行版包包含以下文件：

```text
|── ...
└── distribution/package
    |── bin/
    |   ├── gravitino.sh                        # Gravitino server Launching scripts.
    |   └── gravitino-iceberg-rest-server.sh    # Gravitino Iceberg REST server Launching scripts.
    |── catalogs
    |   └── fileset/                            # Fileset catalog dependencies and configurations.
    |   └── hive/                               # Apache Hive catalog dependencies and configurations.
    |   └── jdbc-doris/                         # JDBC doris catalog dependencies and configurations.
    |   └── jdbc-mysql/                         # JDBC MySQL catalog dependencies and configurations.
    |   └── jdbc-starrocks/                     # JDBC Starrocks catalog dependencies and configurations.
    |   └── jdbc-postgresql/                    # JDBC PostgreSQL catalog dependencies and configurations.
    |   └── jdbc-hudi/                          # Hudi catalog dependencies and configurations.
    |   └── kafka/                              # Apache Kafka catalog dependencies and configurations.
    |   └── lakehouse-iceberg/                  # Apache Iceberg catalog dependencies and configurations.
    |   └── lakehouse-paimon/                   # Apache Paimon catalog dependencies and configurations.
    |   └── model/                              # Model catalog dependencies and configurations.
    |── conf/                                   # All configurations for Gravitino.
    |   ├── gravitino.conf                      # Gravitino server and Gravitino Iceberg REST server configuration.
    |   ├── gravitino-iceberg-rest-server.conf  # Gravitino server configuration.
    |   ├── gravitino-env.sh                    # Environment variables, etc., JAVA_HOME, GRAVITINO_HOME, and more.
    |   └── log4j2.properties                   # log4j configuration for the Gravitino server and Gravitino Iceberg REST server.
    |── libs/                                   # Gravitino server dependencies libraries.
    |── logs/                                   # Gravitino server and Gravitino Iceberg REST server logs. Automatically created after the server starts.
    |── data/                                   # Default directory for the Gravitino server to store data.
    |── iceberg-rest-server/                    # Gravitino Iceberg REST server package and dependencies libraries.
    └── scripts/                                # Extra scripts for Gravitino.
```

:::note
由于包大小限制和许可证兼容性问题，`OceanBase` 和 `ClickHouse` catalog 默认不包含在 Gravitino 二进制发行版包中（见上文）。
如果你想使用这两个 catalog，请自行构建 Gravitino 二进制发行版包，并使用 tarball `gravitino-<version>-bin-all.tar.gz`，其中包含所有 catalog，包括 `catalogs-contrib` 模块中的那些。
有关更多详细信息，请参阅 [重组 catalog 结构](https://github.com/apache/gravitino/pull/9781)
:::

#### 初始化 RDBMS（可选）

如果你想使用关系型后端存储，需要先初始化 RDBMS。有关初始化 RDBMS 的详细信息，请参阅 [如何使用关系型后端存储](./how-to-use-relational-backend-storage.md)。

#### 配置服务器

Gravitino 服务器配置文件是 `conf/gravitino.conf`。通过修改此文件来配置 Gravitino 服务器。此文件中已经添加了基本配置。所有配置都列在 [Gravitino 服务器配置](./gravitino-server-config.md) 中。

#### 配置服务器日志

Gravitino 服务器日志配置文件是 `conf/log4j2.properties`。Gravitino 使用 Log4j2 作为日志系统。请参阅 [Log4j2 配置指南](https://logging.apache.org/log4j/2.x/) 进行日志配置。

##### 日志轮转与保留

当日志的当前文件达到滚动大小时，或在一天结束时，日志会轮转。每次轮转都会将该文件压缩为其各自的归档文件 `<log name>_<yyyyMMdd>.<index>.log.gz`，因此不会有一个归档文件替换另一个归档文件的情况。

当日志轮转时，如果某个归档文件早于 `logMaxAge`，或者该日志的归档文件超过其总大小上限，则会删除该日志的归档文件。最旧的归档文件会先被删除。删除操作只查看该日志自身的归档文件，也就是直接位于日志目录中的归档文件。该上限只计算归档文件，不计算正在写入的文件。

| 日志文件                            | 配置文件                              | 滚动大小 | 保留时间 | 总大小上限                  |
|-------------------------------------|-------------------------------------------------|-----------|----------|---------------------------------|
| `gravitino-server.log`              | `conf/log4j2.properties`                        | 100MB     | 30 天  | 2GB (`serverLogMaxTotalSize`)   |
| `gravitino_audit.log`               | `conf/log4j2.properties`                        | 256MB     | 30 天  | 10GB (`auditLogMaxTotalSize`)   |
| `gravitino_lineage.log`             | `conf/log4j2.properties`                        | 100MB     | 30 天  | 1GB (`lineageLogMaxTotalSize`)  |
| `gravitino-iceberg-rest-server.log` | `conf/gravitino-iceberg-rest-log4j2.properties` | 100MB     | 30 天  | 2GB (`serverLogMaxTotalSize`)   |
| `gravitino-lance-rest-server.log`   | `conf/gravitino-lance-rest-log4j2.properties`   | 100MB     | 30 天  | 1GB (`serverLogMaxTotalSize`)   |

保留属性位于每个配置文件的顶部。例如，要保留 90 天的日志，并将服务器日志归档文件的总大小限制在最多 5GB：

```properties
property.logMaxAge = 90d
property.serverLogMaxTotalSize = 5GB
```

`logMaxAge` 适用于同一文件中的每个日志。删除规则是 Log4j2 [Delete action](https://logging.apache.org/log4j/2.x/manual/appenders/rolling-file.html#DeleteAction) 条件，每个 `if...` 键都以条件类型命名：`ifFileName`（`IfFileName`）按名称选择该日志的归档文件，而 `ifAny`（`IfAny`）在 `ifLastModified`（`IfLastModified`，早于某个时间）或 `ifAccumulatedFileSize`（`IfAccumulatedFileSize`，超过大小上限）任一匹配时删除归档文件。若要仅更改某一个日志的保留时间，请设置 `appender.<name>.strategy.delete.ifFileName.ifAny.ifLastModified.age`。如果你更改了 `filePattern` 中的归档文件名，请相应更改 `appender.<name>.strategy.delete.ifFileName.glob` 以匹配，否则该日志的归档文件将永远不会被删除。

`bin/gravitino.sh start` 还会将进程的标准输出和标准错误写入 `logs/gravitino-server.out`。每次 `start` 都会先轮转此文件，并将之前的文件保留为 `gravitino-server.out.1`（最新）到 `gravitino-server.out.5`。在 `conf/gravitino-env.sh` 中设置 `GRAVITINO_OUT_FILE_KEEP` 可保留不同数量的文件，或设置为 `0` 表示不保留。

#### 配置服务器环境

Gravitino 服务器环境配置文件是 `conf/gravitino-env.sh`。Gravitino 暴露了若干环境变量。可在此文件中修改它们。

#### 配置 catalog

Gravitino 支持多个 catalog。通过修改 `catalogs/<catalog-provider>/conf` 目录中的相关配置文件来配置 catalog 级别的配置。你在此处设置的配置会应用于你创建的所有同类型 catalog。

例如，如果你想配置 Hive catalog，可以修改文件 `catalogs/hive/conf/hive.conf`。详细配置列在特定 catalog 的文档中。

:::note
Gravitino 按以下顺序采用 catalog 配置：

1. 在 catalog 创建 API 或 REST API 中指定的 Catalog `properties`。
2. 在 catalog 配置文件中指定的 catalog 配置。

catalog `properties` 可以覆盖配置文件中指定的 catalog 配置。
:::

如果你添加 `gravitino.bypass.`，Gravitino 支持传入 catalog 特定的配置。例如，如果你想将 HMS 特定的配置 `hive.metastore.client.capability.check` 传入 Hive catalog 中的底层 Hive 客户端，请添加 `gravitino.bypass.` 前缀。

此外，Gravitino 支持从外部文件加载 catalog 特定的配置。例如，你可以将自己的 `hive-site.xml` 文件放在 `catalogs/hive/conf` 目录中，Gravitino 会自动加载它。

#### 启动服务器

配置 Gravitino 服务器后，通过运行以下命令启动 Gravitino 服务器：

```shell
./bin/gravitino.sh start
```

或者，要启动 Gravitino 服务器 Web UI，请运行：

```shell
./bin/gravitino.sh run
```

在浏览器中输入 [http://localhost:8090](http://localhost:8090) 来访问 Gravitino Web UI，或者你可以运行：

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" http://localhost:8090/api/version
```

以确保 Gravitino 正在运行。

:::info
如果你需要调试 Gravitino 服务器，请在 `conf/gravitino-env.sh` 文件中启用 `GRAVITINO_DEBUG_OPTS` 环境变量。然后在 `IntelliJ IDEA` 中创建 `Remote JVM Debug` 配置，并调试 `gravitino.server.main`。
:::

#### 在 Gravitino 包中管理 Gravitino Iceberg REST 服务器

可以将 Iceberg REST 服务器作为独立服务器运行，也可以作为嵌入 Gravitino 服务器的辅助服务运行。要将其作为独立服务器启动，请使用命令 `./bin/gravitino-iceberg-rest-server.sh start`，并在 `./conf/gravitino-iceberg-rest-server.conf` 中指定配置。或者，使用 `./bin/gravitino.sh start` 启动一个同时集成 Iceberg REST 服务和 Gravitino 服务的 Gravitino 服务器，所有配置都集中在 `conf/gravitino.conf` 中。

有关 Gravitino Iceberg REST 服务器的更多详细信息，请参阅 [Iceberg REST 服务器文档](./iceberg-rest-service.md)。

## 使用 Docker 安装

### 获取 Docker 镜像

Gravitino 将 Docker 镜像发布到 [Docker Hub](https://hub.docker.com/r/apache/gravitino/tags)。
通过运行以下命令来运行 Gravitino Docker 镜像：

```shell
docker run -d -i -p 8090:8090 apache/gravitino:<version>
```

在浏览器中输入 `http://localhost:8090` 来访问 Gravitino Web UI，或者你
可以运行

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" http://localhost:8090/api/version
```

以确保 Gravitino 正在运行。

### 在 Docker 中将 GCS 用作对象存储

如果你的 catalog 使用 Google Cloud Storage (GCS) 作为对象存储，请设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量，并将服务账号密钥文件挂载到容器中：

```shell
docker run -d -i -p 8090:8090 \
  -v /path/to/your-service-account-key.json:/etc/gcs/key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/etc/gcs/key.json \
  apache/gravitino:<version>
```

## 使用 Docker Compose 安装

发布的 Gravitino Docker 镜像仅包含具有基本配置的 Gravitino 服务器。如果你想体验带有其他组件的完整 Gravitino 系统，请使用 Docker `compose` 文件。

有关详细信息，请查看
[Gravitino playground 仓库](https://github.com/apache/gravitino-playground) 和
[playground 示例](./how-to-use-the-playground.md)。

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=HowToInstall" alt="" />

## 使用 Helm Chart 在 Kubernetes 上部署

Apache Gravitino Helm chart 提供了一种在 Kubernetes 上部署 Gravitino 的方式，并支持完全可自定义的配置。
有关详细的安装说明和配置选项，请参阅 [Apache Gravitino Helm Chart](./chart.md)。