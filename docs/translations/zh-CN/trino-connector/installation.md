---
title: "Install the Trino Connector"
slug: "/trino-connector/installation"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

要安装 Apache Gravitino Trino 连接器，您需要先部署 Trino 环境，然后将 Gravitino Trino 连接器插件安装到 Trino 中。
请参阅[部署 Trino 文档](https://trino.io/docs/current/installation/deployment.html)并执行以下步骤：

本文档中的示例默认使用 Trino `469`。

## 获取连接器包

Gravitino 为不同的 Trino 版本段提供不同的 Trino 连接器包。
首先根据您的 Trino 服务器版本选择包。

| Trino 服务器版本 | 连接器包片段 |
|----------------------|---------------------------|
| 440-445              | `trino-connector-440-445` |
| 446-451              | `trino-connector-446-451` |
| 452-468              | `trino-connector-452-468` |
| 469-472              | `trino-connector-469-472` |
| 473-478              | `trino-connector-473-478` |

对于 Trino `469`，请选择 `trino-connector-469-472` 包。

发布包的命名格式为：

`gravitino-trino-connector-<segment>-<version>.tar.gz`

例如：

`gravitino-trino-connector-469-472-<version>.tar.gz`

通过以下方式获取该包：

1. 从 [GitHub Releases](https://github.com/apache/gravitino/releases) 下载发布包。对于 Trino `469`，请下载 `469-472` 包：

```shell
cd /tmp
wget https://github.com/apache/gravitino/releases/download/<version>/gravitino-trino-connector-469-472-<version>.tar.gz
tar -zxvf gravitino-trino-connector-469-472-<version>.tar.gz
```

2. 在 Gravitino 项目中从源码构建。对于 Trino `469`，构建模块 `trino-connector-469-472`：

```shell
cd <gravitino-source-root>
./gradlew :trino-connector:trino-connector-469-472:assembleTrinoConnector
cd distribution
tar -zxvf gravitino-trino-connector-469-472-<version>.tar.gz
```

解压后，您可以看到 connector 目录：

`gravitino-trino-connector-469-472-<version>`

## 安装连接器包

1. 下载并解压与您的 Trino 版本对应的正确 Gravitino Trino 连接器 tarball。
2. 将解压后的连接器目录重命名为 `gravitino`，然后将其复制到 Trino 插件目录中。
通常，该目录位置为 `Trino-server-<version>/plugin`，并且该目录包含 Trino 使用的其他 catalog。
3. 更新 Trino coordinator 配置。
您需要设置 `catalog.management=dynamic`，配置文件位置为 `Trino-server-<version>/etc/config.properties`，内容如下：

```text
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
catalog.management=dynamic
discovery.uri=http://0.0.0.0:8080
```

## 示例

将 Gravitino Trino 连接器安装到官方 Trino Docker 镜像中。

### 运行容器

使用 Docker 命令从 `trinodb/trino` 镜像创建一个容器。将其命名为 trino-gravitino。
在后台运行它，并将容器内的默认 Trino 端口（即 8080）映射到你机器上的 8080 端口。

```shell
docker run --name trino-gravitino -d -p 8080:8080 trinodb/trino:469
```

运行 `docker ps` 以检查容器是否正在运行。


### 安装 Trino 连接器

下载适用于 Trino `469` 的 Gravitino Trino connector tar 包并解压。

```shell
cd /tmp
wget https://github.com/apache/gravitino/releases/download/<version>/gravitino-trino-connector-469-472-<version>.tar.gz
tar -zxvf gravitino-trino-connector-469-472-<version>.tar.gz
```

解压后，查看连接器目录 `gravitino-trino-connector-469-472-<version>`。

将连接器目录重命名为 `gravitino`，然后将其复制到 Trino 容器的插件目录中。

```shell
mv /tmp/gravitino-trino-connector-469-472-<version> /tmp/gravitino
docker cp /tmp/gravitino trino-gravitino:/lib/trino/plugin
```

检查容器中的插件目录。

```shell
docker exec -it trino-gravitino /bin/bash
cd /lib/trino/plugin
```

现在您可以在插件目录中看到 Gravitino Trino 连接器目录。

### 配置 Trino

在 `/etc/trino` 目录中找到 Trino 配置文件 `config.properties`。你需要像这样修改该文件：

```text
#single node install config
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
discovery.uri=http://localhost:8080
catalog.management=dynamic
```

### 配置 Trino 连接器

假设您现在已经在主机 `gravitino-server-host` 上启动了 Gravitino 服务器，并且已经创建了一个名为 `test` 的 metalake，如果这些尚未准备好，请参阅 [Gravitino 入门](../getting-started/index.md)。

要正确配置 Gravitino Trino 连接器，您需要将以下配置放入 Trino 配置文件 `/etc/trino/catalog/gravitino.properties` 中。

```text
connector.name=gravitino
gravitino.uri=http://gravitino-server-host:8090
gravitino.metalake=test
```

- `gravitino.name` 定义了使用哪个 Gravitino Trino 连接器。它必须是 `gravitino`。
- `gravitino.metalake` 定义了使用哪个 metalake。它应该存在于 Gravitino 服务器中。
- `gravitino.uri` 定义了有关 Gravitino 服务器的连接信息。请确保您的容器可以访问 Gravitino 服务器。

Apache Gravitino Trino 连接器的完整配置可参见[此处](configuration.md)

如果您尚未创建名为 `test` 的 metalake，您可以使用以下命令来创建它。

```shell
curl -X POST -H "Content-Type: application/json" -d '{"name":"test","comment":"comment","properties":{}}' http://gravitino-server-host:8090/api/metalakes
```

然后重启 Trino 容器以加载 Gravitino Trino 连接器。

```shell
docker restart trino-gravitino
```

### 验证 Trino 连接器

使用 Trino CLI 连接到 Trino 容器并运行查询。

```text
docker exec -it trino-gravitino trino
trino> SHOW CATALOGS;
Catalog
------------------------
gravitino
jmx
memory
tpcds
tpch
system
```

在结果集中查看 `gravitino` 目录。这表示 Gravitino Trino 连接器已成功安装。

假设您已经在 Gravitino 服务器中创建了一个名为 `test.jdbc-mysql` 的目录，或者参考[创建目录](../manage-catalogs-and-schemas.md#create-a-catalog)。然后您可以使用 Trino CLI 连接到 Trino 容器并运行如下查询。

```text
docker exec -it trino-gravitino trino
trino> SHOW CATALOGS;
Catalog
------------------------
gravitino
jmx
memory
tpcds
tpch
system
jdbc-mysql
```

名为 'jdbc-mysql' 的 catalog 是你通过 gravitino server 创建的 catalog，你可以像使用其他 Trino catalog 一样使用它来访问 mysql 数据库。
