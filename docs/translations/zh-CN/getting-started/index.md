---
slug: /getting-started/index
license: This software is licensed under the Apache License version 2.
title: 入门
---
## 简介

开始使用 Apache Gravitino 有几种方式。

<!--Docker option-->
安装和配置 Hive 和 Trino 可能有些复杂。
如果对这些技术不熟悉，使用 Docker 可能是个不错的选择。
已经提供了预打包的容器，用于 Gravitino、Apache Hive、Apache Hadoop、
Trino、MySQL、PostgreSQL 等。
查看 [安装 Gravitino playground](./playground.md) 了解更多详情。

<!--Build from source-->
本页将指导完成从源码下载并安装 Gravitino
的过程。

1. [准备环境](#aws)
   - 在 [Amazon Web Service (AWS)](#gcp) 上部署并运行 Gravitino
   - 在 [Google Compute Platform (GCP)](#本地工作站) 上部署并运行 Gravitino
   - 在[本地机器](#安装-gravitino)上运行 Gravitino
1. [安装 Gravitino](#启动-gravitino)
1. [启动 Gravitino](#安装-apache-hive)
1. [安装 Apache Hive](#与-apache-gravitino-api-交互)
1. [与 Apache Gravitino API 交互](#下一步)

:::note
如果需要远程访问实例，务必阅读
[在外部访问 AWS 上的 Gravitino](./aws-remote-access.md)。
:::

## 环境准备

### AWS

要在 AWS 环境中运行，请按照以下步骤操作：

1. 在 AWS 控制台中，启动一个新实例。
   选择 `Ubuntu` 作为操作系统，`t2.xlarge` 作为实例类型。
   创建一个名为 *Gravitino.pem* 的密钥对用于 SSH 访问并下载。
   如果需要远程连接到实例，请允许 HTTP 和 HTTPS 流量。
   将 Elastic Block Store 存储设置为 20GiB。
   其他所有设置保持默认值。
   其他操作系统和实例类型可能也可以运行，但尚未经过全面测试。

1. 启动实例，并使用下载的 `.pem` 文件通过 SSH 连接到该实例：

   ```shell
   ssh ubuntu@<IP_address> -i ~/Downloads/Gravitino.pem
   ```

   <strong>注意</strong>：可能需要使用
   `chmod 400` 调整 `.pem` 文件权限以启用 SSH 连接。

1. 更新 Ubuntu OS 以确保其处于最新状态：

   ```shell
   sudo apt update
   sudo apt upgrade
   ```

   <!--TODO: need Red Hat commands?-->
   可能需要重启实例才能使所有更改生效。

1. 安装 Java Development Kit (JDK)。支持 Java 17。

   ```shell
   sudo apt install openjdk-<version>-jdk-headless
   ```

   使用以下命令验证 Java 版本：

   ```shell
   java -version
   ```

   将看到有关 OpenJDK 版本的信息。

### GCP

要在 GCP 平台上运行，请按照以下步骤操作：

1. 在 Google Cloud 控制台中，启动一个新实例。
   选择 `e2-standard-4` 作为实例类型，并将启动磁盘大小设置为 20 GB。
   如果需要远程连接到实例，请允许 HTTP 和 HTTPS 流量。
   其他所有设置保持默认值。
   其他操作系统和实例类型可能也可以运行，但尚未经过全面测试。

1. 启动实例，并通过浏览器中的 SSH 工具连接到该实例。

1. 更新 Debian OS 以确保其处于最新状态：

   ```shell
   sudo apt update
   sudo apt upgrade
   ```

   可能需要重启实例才能使所有更改生效。

1. 安装 Java Development Kit (JDK)，支持 Java 17。

   ```shell
   wget -O - https://apt.corretto.aws/corretto.key | sudo gpg --dearmor -o /usr/share/keyrings/corretto-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/corretto-keyring.gpg] https://apt.corretto.aws stable main" | sudo tee /etc/apt/sources.list.d/corretto.list
   sudo apt-get update
   sudo apt-get install -y java-<version>-amazon-corretto-jdk
   ```

   使用以下命令验证 Java 版本：

   ```shell
   java -version
   ```

   将看到有关 OpenJDK 版本的信息。

### 本地工作站

要在 macOS 或 Linux 工作站上本地构建和安装 Gravitino，
请按照以下步骤操作：

1. 安装 Java Development Kit (JDK)。支持 Java 17。
   这可以通过 [sdkman](https://sdkman.io/) 来完成，例如：

   ```shell
   sdk install java <version>
   ```

   也可以使用不同的包管理器来安装 JDK，例如，
   在 macOS 上使用 [Homebrew](https://brew.sh/)，在 Ubuntu/Debian 上使用 `apt`，以及
   在 CentOS/RedHat 上使用 `yum`。

## 安装 Gravitino

从二进制发布包或容器镜像安装 Gravitino。
请遵循 [how-to-install](../how-to-install.md)。

或者可以从零开始安装 Gravitino。
请遵循 [how-to-build](../how-to-build.md) 和 [how-to-install](../how-to-install.md)。

## 启动 Gravitino

使用 `gravitino.sh` 脚本启动 Gravitino：

```shell
<path-to-gravitino>/bin/gravitino.sh start
```

## 安装 Apache Hive

如果环境中已经有 Apache Hive 和 Apache Hadoop，
可以跳过此步骤，并使用现有服务与 Gravitino 配合使用。
否则，可以按照[说明](./hive.md)安装 Apache Hive。

## 与 Apache Gravitino API 交互

部署 Gravitino 服务器后，可以通过
RESTful API 与其交互，以创建和修改元数据。

:::tip
以下示例使用 `localhost` 作为主机名。
请根据实际环境进行修改。
:::

1. 创建一个 Metalake：

   ```shell
   curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     -d '{"name":"my_metalake","comment":"Test metalake"}' \
     http://localhost:8090/api/metalakes
   ```

   验证 MetaLake 是否已创建：

   ```shell
   curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     http://localhost:8090/api/metalakes

   curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     http://localhost:8090/api/metalakes/my_metalake
   ```

   注意，如果请求一个不存在的 Metalake，将会收到
   `NoSuchMetalakeException` 错误。

   ```shell
   curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     http://localhost:8090/api/metalakes/none
   ```

1. 在 Hive 中创建一个 catalog：

   首先，列出当前的 catalog 以验证不存在任何 catalog。

   ```shell
   curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     http://localhost:8090/api/metalakes/my_metalake/catalogs
   ```

   创建一个新的 Hive catalog。

   ```shell
   curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     -d '{"name":"my-catalog","comment":"Test catalog", "type":"RELATIONAL", "provider":"hive", "properties":{"metastore.uris":"thrift://localhost:9083"}}' \
     http://localhost:8090/api/metalakes/my_metalake/catalogs
   ```

   验证该 catalog 是否已创建：

   ```shell
   curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
     -H "Content-Type: application/json" \
     http://localhost:8090/api/metalakes/my_metalake/catalogs
   ```

   :::tip
   用于 Hive catalog 的 `metastore.uris` 属性必须
   根据实际环境进行调整。
   :::

## 下一步

- 深入了解[文档](https://gravitino.apache.org/docs/latest)
  以获取高级功能和配置选项。

- 收藏 [Gravitino 网站](https://gravitino.apache.org) 以获取更新、
   最新版本、新功能、优化和安全增强等信息。

- 阅读[博客](https://gravitino.apache.org/blog)

- 加入 Gravitino 社区论坛，与开发人员和其他用户建立联系，
  分享经验并在需要时寻求帮助。
  欢迎提出问题和评论。

  - 加入 [Gravitino Slack 频道](https://the-asf.slack.com)
  - 浏览 GitHub 仓库中的 [issues](https://github.com/apache/gravitino/issues)
    或 [pull requests](https://github.com/apache/gravitino/pulls)，
    选择感兴趣的内容参与贡献。

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=GettingStarted" alt="" />