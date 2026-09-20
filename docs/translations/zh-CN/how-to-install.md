---
title: "Install Gravitino"
slug: "/how-to-install"
license: "This software is licensed under the Apache License version 2."
---

## 从二进制发行版安装

:::note
Apache Gravitino 支持在 Java 17 上运行，更高版本应该也能运行，但尚未经过全面测试。请确保您已安装 Java 并且
`JAVA_HOME` 配置正确。要确认 Java 版本，请运行
`${JAVA_HOME}/bin/java -version` 命令。
:::

Gravitino 包包含 Gravitino 服务器和 Gravitino Iceberg REST 服务器。独立管理这些服务器，或者在单台服务器上并发运行它们。

### 获取二进制分发包

在安装 Gravitino 之前，请确保您拥有 Gravitino 二进制分发包。从 [GitHub](https://github.com/apache/gravitino/releases) 下载最新的 Gravitino 二进制分发包。
要自行构建，请按照 [How to Build Gravitino](./how-to-build.md) 中的说明进行操作。

- 如果你使用 `./gradlew compileDistribution` 命令自行构建 Gravitino，你可以在 `distribution/package` 和 `distribution/package-all` 目录中找到 Gravitino 的二进制分发包。这两个包的主要区别在于，`package-all` 包包含所有的 catalog（包括 `catalogs-contrib` 文件夹下的 catalog），而 `package` 包仅包含 `catalogs` 文件夹下的主要 catalog。

- 如果你使用 `./gradlew assembleDistribution` 命令自行构建 Gravitino，你可以在 `distribution` 目录中获取名为 `gravitino-<version>-bin.tar.gz` 的压缩 Gravitino 二进制发行版包，以及 sha256 校验和文件 `gravitino-<version>-bin.tar.gz.sha256`。此外，你可以在 `distribution` 目录中获取名为 `gravitino-<version>-bin-all.tar.gz` 的完整压缩 Gravitino 二进制发行版包，以及 sha256 校验和文件 `gravitino-<version>-bin-all.tar.gz.sha256`。这两个包的主要区别在于，`-all` 包包含所有 catalog，包括 `catalogs-contrib` 文件夹下的 catalog，而普通包仅包含 `catalogs` 文件夹下的主要 catalog。

注意：**Apache Gravitino 仅在 GitHub releases 上发布 `gravitino-<version>-bin.tar.gz` 包，而 `gravitino-<version>-bin-all.tar.gz` 包仅供有兴趣自行从源代码构建 Gravitino 的用户使用。**

Gravitino 二进制分发包包含以下文件：

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
由于包大小限制和许可证兼容性问题，`OceanBase` 和 `ClickHouse` 目录默认不包含在 Gravitino 二进制发行包中（见上文）。
如果你想使用这两个目录，请自行构建 Gravitino 二进制发行包并使用 tarball `gravitino-<version>-bin-all.tar.gz`，该包包含所有目录，包括 `catalogs-contrib` 模块中的目录。
有关更多详细信息，请参阅 [Reorg catalogs structure](https://github.com/apache/gravitino/pull/9781)
:::

#### 初始化 RDBMS（可选）

如果你想使用关系型后端存储，你需要先初始化 RDBMS。有关初始化 RDBMS 的详细信息，请参阅[如何使用关系型后端存储](./how-to-use-relational-backend-storage.md)。

#### 配置服务器

Gravitino 服务器的配置文件是 `conf/gravitino.conf`。通过修改此文件来配置 Gravitino 服务器。该文件中已添加了基本配置。所有配置均列在 [Gravitino 服务器配置](./gravitino-server-config.md) 中。

#### 配置服务器日志

Gravitino 服务器的日志配置文件是 `conf/log4j2.properties`。Gravitino 使用 Log4j2 作为日志系统。请参考 [Log4j2 配置指南](https://logging.apache.org/log4j/2.x/) 来进行日志配置。

#### 配置服务器环境

Gravitino 服务器的环境配置文件是 `conf/gravitino-env.sh`。Gravitino 暴露了几个环境变量。在此文件中修改它们。

#### 配置目录

Gravitino 支持多个目录。通过修改 `catalogs/<catalog-provider>/conf` 目录下的相关配置文件来配置目录级别的配置。您在此处设置的配置将应用于您创建的所有同类型的目录。

例如，如果你想配置 Hive catalog，你可以修改文件 `catalogs/hive/conf/hive.conf`。详细的配置列在特定的 catalog 文档中。

:::note
Gravitino 按照以下顺序获取目录配置：

1. 在目录创建 API 或 REST API 中指定的目录 `properties`。
2. 在目录配置文件中指定的目录配置。

目录 `properties` 可以覆盖配置文件中指定的目录配置。
:::

如果你添加 `gravitino.bypass.`，Gravitino 支持传入 catalog 特定配置。例如，如果你想将 HMS 特定配置 `hive.metastore.client.capability.check` 传递给 Hive catalog 中的底层 Hive 客户端，请添加 `gravitino.bypass.` 前缀。

此外，Gravitino 支持从外部文件加载特定 catalog 的配置。例如，你可以将自己的 `hive-site.xml` 文件放在 `catalogs/hive/conf` 目录中，Gravitino 会自动加载它。

#### 启动服务器

配置 Gravitino 服务器后，运行以下命令启动 Gravitino 服务器：

```shell
./bin/gravitino.sh start
```

或者，要启动 Gravitino 服务器 Web UI，请运行：

```shell
./bin/gravitino.sh run
```

在浏览器中输入 [http://localhost:8090](http://localhost:8090) 访问 Gravitino Web UI，或者你可以运行：

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" http://localhost:8090/api/version
```

以确保 Gravitino 正在运行。

:::info
如果你需要调试 Gravitino 服务器，请在 `conf/gravitino-env.sh` 文件中启用 `GRAVITINO_DEBUG_OPTS` 环境变量。然后在 `IntelliJ IDEA` 中创建一个 `Remote JVM Debug` 配置，并调试 `gravitino.server.main`。
:::

#### 管理 Gravitino Package 中的 Gravitino Iceberg REST Server

可以将 Iceberg REST 服务器作为独立服务器运行，或者作为嵌入在 Gravitino 服务器中的辅助服务运行。要将其作为独立服务器启动，请使用命令 `./bin/gravitino-iceberg-rest-server.sh start`，并在 `./conf/gravitino-iceberg-rest-server.conf` 中指定配置。或者，使用 `./bin/gravitino.sh start` 来启动集成了 Iceberg REST 服务和 Gravitino 服务的 Gravitino 服务器，所有配置都集中在 `conf/gravitino.conf` 中。

有关 Gravitino Iceberg REST 服务器的更多详细信息，请参阅 [Iceberg REST 服务器文档](./iceberg-rest-service.md)。

## 使用 Docker 安装

### 获取 Docker 镜像

Gravitino 将 Docker 镜像发布到 [Docker Hub](https://hub.docker.com/r/apache/gravitino/tags)。
运行以下命令以启动 Gravitino Docker 镜像：

```shell
docker run -d -i -p 8090:8090 apache/gravitino:<version>
```

通过在浏览器中输入 `http://localhost:8090` 来访问 Gravitino Web UI，或者你
可以运行

```shell
curl -v -X GET -H "Accept: application/vnd.gravitino.v1+json" -H "Content-Type: application/json" http://localhost:8090/api/version
```

以确保 Gravitino 正在运行。

### 结合 Docker 使用 GCS 作为对象存储

如果您的目录使用 Google Cloud Storage (GCS) 作为对象存储，请设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量，并将服务帐号密钥文件挂载到容器中：

```shell
docker run -d -i -p 8090:8090 \
  -v /path/to/your-service-account-key.json:/etc/gcs/key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/etc/gcs/key.json \
  apache/gravitino:<version>
```

## 使用 Docker Compose 安装

发布的 Gravitino Docker 镜像仅包含带有基本配置的 Gravitino 服务器。如果您想体验包含其他组件的完整 Gravitino 系统，请使用 Docker `compose` 文件。

有关详细信息，请查看
[Gravitino playground 仓库](https://github.com/apache/gravitino-playground) 和
[playground 示例](./how-to-use-the-playground.md)。

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=HowToInstall" alt="" />

## 在 Kubernetes 上使用 Helm Chart 部署

Apache Gravitino Helm chart 提供了一种在 Kubernetes 上部署 Gravitino 的方法，并支持完全自定义的配置。 
有关详细的安装说明和配置选项，请参阅 [Apache Gravitino helm Chart](./chart.md)。
