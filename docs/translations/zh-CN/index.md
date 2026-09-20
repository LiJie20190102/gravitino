---
title: "Apache Gravitino"
slug: "/"
license: "This software is licensed under the Apache License version 2."
---

## 概述

Apache Gravitino 是一个高性能、地理分布式和联邦式的元数据湖。
它直接管理不同来源、类型和区域的元数据。
它还为用户提供针对数据和 AI 资产的统一元数据访问。

[了解更多](./overview.md)&rarr;

## 下载

从[下载页面](https://gravitino.apache.org/downloads)获取 Gravitino，
或者你可以从源代码构建 Gravitino。参见[如何构建 Gravitino](./how-to-build.md)。

Gravitino 可以在 Linux 和 macOS 平台上运行，并且需要安装 Java 17。
这应该包括 x86_64 和 ARM64 架构上的 JVM。
在单台机器上本地运行很容易，你只需要将 `java` 安装在
你的系统 `PATH` 中，或者让 `JAVA_HOME` 环境变量指向 Java 安装目录。

参见 [如何安装 Gravitino](./how-to-install.md) 了解如何安装 Gravitino 服务器。

Gravitino 在 [Docker Hub](https://hub.docker.com/u/apache) 上提供了 Docker 镜像。
拉取镜像并运行它。有关 Gravitino Docker 镜像的详细信息，请参阅
[Docker 镜像详细信息](./docker-image-details.md)。

Gravitino 还提供了一个 playground，用于与其他组件一起体验整个 Gravitino 系统。
请参见 [Gravitino playground 仓库](https://github.com/apache/gravitino-playground)
以及 [如何使用 playground](./how-to-use-the-playground.md)。

## 入门

要开始使用 Gravitino，请参阅 [入门指南](./getting-started/index.md) 了解详情。

* [本地入门](./getting-started/index.md#local-workstation)：在本地启动
和使用 Gravitino 的快速指南。

* [在 Amazon Web Services 上运行](./getting-started/index.md#aws): 一份
在 AWS 上启动和使用 Gravitino 的快速指南。

* [在 Google Cloud Platform 上运行](./getting-started/index.md#gcp):
在 GCP 上启动和使用 Gravitino 的快速指南。

## 使用 Gravitino 管理元数据

Gravitino 提供了两个 SDK，以统一的方式管理来自不同 catalog 的元数据：
REST API 和 Java SDK。
使用任意一种来管理元数据。参见

* [使用 Gravitino 管理 metalake](./manage-metalake-using-gravitino.md) 以了解如何管理
metalakes。
* [使用 Gravitino 管理关系型元数据](./manage-relational-metadata-using-gravitino.md)
以了解如何管理关系型元数据。
* [使用 Gravitino 管理视图元数据](./manage-view-metadata-using-gravitino.md)
以了解如何管理视图元数据。
* [使用 Gravitino 管理 fileset 元数据](./manage-fileset-metadata-using-gravitino.md) 以了解
如何管理 fileset 元数据。
* [使用 Gravitino 管理消息元数据](./manage-messaging-metadata-using-gravitino.md) 以了解如何管理
消息元数据。
* [使用 Gravitino 管理模型元数据](./manage-model-metadata-using-gravitino.md) 以了解如何管理
模型元数据。
* [使用 Gravitino 管理用户定义函数](./manage-user-defined-function-using-gravitino.md) 以了解如何管理
用户定义函数。

此外，你可以在以下位置找到完整的 REST API 定义：
[Gravitino Open API](./api/rest/gravitino-rest-api)，
在 [Gravitino Java doc](pathname:///docs/2.0.0-SNAPSHOT/api/java/index.html) 中找到 Java SDK 定义，
以及在 [Gravitino Python doc](pathname:///docs/2.0.0-SNAPSHOT/api/python/index.html) 中找到 Python SDK 定义。

Gravitino 还提供了一个 Web UI 来管理元数据。在浏览器中通过 `http://<ip-address>:8090` 访问该 Web UI。
详情请参见 [Gravitino web UI](./webui.md)。

Gravitino 还提供了一个命令行界面（CLI）来管理元数据。详情请参见 [Gravitino CLI](./cli.md)。

Gravitino supports the following catalogs:

**关系目录：**

* [**Doris 目录**](./jdbc-doris-catalog.md)
* [**Hologres 目录**](./jdbc-hologres-catalog.md)
* [**Hudi 目录**](./lakehouse-hudi-catalog.md)
* [**Hive 目录**](./apache-hive-catalog.md)
* [**Iceberg 目录**](./lakehouse-iceberg-catalog.md)
* [**MySQL 目录**](./jdbc-mysql-catalog.md)
* [**Paimon 目录**](./lakehouse-paimon-catalog.md)
* [**PostgreSQL 目录**](./jdbc-postgresql-catalog.md)
* [**OceanBase 目录**](./jdbc-oceanbase-catalog.md)\*
* [**StarRocks 目录**](./jdbc-starrocks-catalog.md)
* [**ClickHouse 目录**](./jdbc-clickhouse-catalog.md)\*
* [**Lakehouse 通用目录**](./lakehouse-generic-catalog.md)

要管理表和分区统计信息，请参阅[在 Gravitino 中管理统计信息](./manage-statistics-in-gravitino.md)。

**文件集目录：**

* [**文件集目录**](./fileset-catalog.md)

**消息目录：**

* [**Kafka 目录**](./kafka-catalog.md)

**模型目录：**

* [**模型目录**](./model-catalog.md)

如果你想自动化表维护工作流，请参阅 [表维护服务（优化器）](./table-maintenance-service/optimizer.md)。
从 Gravitino 内置策略和内置作业模板开始，并在需要时通过优化器接口进行扩展。

带有星号 (\*) 的 catalog 不在标准发布包和 Docker 镜像中。Gravitino 提供了一个
`catalogs-contrib` 文件夹来托管贡献的 catalog，这些 catalog 不在标准发布包中，但可以单独构建和使用。详情请参见[如何构建 Gravitino](./how-to-build.md#quick-start)。

## Apache Gravitino 游乐场

为了轻松体验 Gravitino 与其他组件的结合，Gravitino 提供了一个可运行的 playground。
它将 Apache Hadoop、Apache Hive、Trino、MySQL、PostgreSQL 和 Gravitino 集成在一起，作为一个
完整的环境。要体验所有功能，请参阅
[入门指南](./getting-started/index.md) 和
[如何使用 Gravitino playground](./how-to-use-the-playground.md)。

* [在 AWS 或 GCP 上安装 Gravitino playground](./getting-started/playground.md):
一份在 AWS 或 GCP 上启动和使用 Gravitino playground 的快速指南。
* [本地安装 Gravitino playground](./getting-started/playground.md):
一份本地启动和使用 Gravitino playground 的快速指南。
* [如何使用 Gravitino playground](./how-to-use-the-playground.md): 提供了一个如何
将 Gravitino 和其他组件结合使用。

## 接下来去哪里

### 目录

Gravitino 支持不同的目录来管理不同来源的元数据。请参见：

* [Doris catalog](./jdbc-doris-catalog.md)：使用 Gravitino 管理 Doris 数据的完整指南。
* [Hologres catalog](./jdbc-hologres-catalog.md)：使用 Gravitino 管理 Hologres 数据的完整指南。
* [StarRocks catalog](./jdbc-starrocks-catalog.md)：使用 Gravitino 管理 StarRocks 数据的完整指南。
* [Fileset catalog](./fileset-catalog.md)：使用 Gravitino 管理 fileset 的完整指南
使用 Hadoop Compatible File System (HCFS)。
* [Hive catalog](./apache-hive-catalog.md)：使用 Gravitino 管理 Apache Hive 数据的完整指南。
* [Hudi catalog](./lakehouse-hudi-catalog.md)：使用 Gravitino 管理 Apache Hudi 数据的完整指南。
* [Iceberg catalog](./lakehouse-iceberg-catalog.md)：使用 Gravitino 管理 Apache Iceberg 数据的完整指南。
* [Kafka catalog](./kafka-catalog.md)：使用 Gravitino 管理 Kafka topics 元数据的完整指南。
* [Model catalog](./model-catalog.md)：使用 Gravitino 管理 model 元数据的完整指南。
* [MySQL catalog](./jdbc-mysql-catalog.md)：使用 Gravitino 管理 MySQL 数据的完整指南。
* [Paimon catalog](./lakehouse-paimon-catalog.md)：使用 Gravitino 管理 Apache Paimon 数据的完整指南。
* [PostgreSQL catalog](./jdbc-postgresql-catalog.md)：使用 Gravitino 管理 PostgreSQL 数据的完整指南。
* [OceanBase catalog](./jdbc-oceanbase-catalog.md)：使用 Gravitino 管理 OceanBase 数据的完整指南。
* [ClickHouse catalog](./jdbc-clickhouse-catalog.md)：使用 Gravitino 管理 ClickHouse 数据的完整指南。
* [Lakehouse generic catalog](./lakehouse-generic-catalog.md)：使用 Gravitino 管理 lakehouse 数据源的完整指南。

### 治理

Gravitino 提供治理功能，以统一的方式管理元数据。参见：

* [在 Gravitino 中管理标签](./manage-tags-in-gravitino.md)：使用 Gravitino 的完整指南
来管理标签。
* [在 Gravitino 中管理策略](./manage-policies-in-gravitino.md)：使用 Gravitino 的完整指南
来管理策略。
* [在 Gravitino 中管理作业](./manage-jobs-in-gravitino.md)：使用 Gravitino 的完整指南
来管理作业。

### Gravitino Iceberg REST Catalog 服务

* [Iceberg REST catalog 服务](./iceberg-rest-service.md)：使用 Gravitino 的指南
作为 Apache Iceberg REST catalog 服务。

### Gravitino Lance REST Catalog 服务

* [Lance REST catalog 服务](./lance-rest-service.md)：使用 Gravitino
作为 Lance REST catalog 服务的指南。

### 连接器

#### Trino 连接器

Gravitino 提供了一个 Trino 连接器，用于统一管理 Trino 元数据。要使用 Trino 连接器，请参见：

* [如何使用 Gravitino Trino 连接器](./trino-connector/index.md)：使用 Gravitino Trino 连接器的完整指南。

#### Spark 连接器

Gravitino 提供了一个 Spark 连接器，以统一的方式管理元数据。要使用 Spark 连接器，请参阅：

* [Gravitino Spark connector](./spark-connector/spark-connector.md)：使用 Gravitino Spark connector 的完整指南。

#### Flink 连接器

Gravitino 提供了一个 Flink 连接器来统一管理元数据。要使用 Flink 连接器，请参阅：

* [Gravitino Flink 连接器](./flink-connector/flink-connector.md)：使用 Gravitino Flink 连接器的完整指南。

#### Daft 连接器

Gravitino 提供了 Daft 连接器，用于从 Daft 数据帧访问 Gravitino 元数据。要使用 Daft 连接器，请参阅：

* [Gravitino Daft connector](./daft-connector/daft-connector.md): Gravitino Daft connector 简介。


### 服务器管理

Gravitino 提供了多种配置和管理 Gravitino 服务器的方式。参见：

* [Gravitino metrics](./metrics.md)：提供指标配置和详细的指标列表
Gravitino 服务器的。

### 安全

Gravitino 为 Gravitino 提供安全配置，包括 HTTPS、认证和访问控制配置。

* [HTTPS](./security/how-to-use-https.md): 提供 HTTPS 配置。
* [Authentication](./security/how-to-authenticate.md): 提供身份验证配置，包括简单、基本、OAuth 和 Kerberos。
* [Local users and groups](./security/local-users-and-groups.md): 位于 HTTP Basic 身份验证之后的本地用户存储的操作员指南，包括服务管理员设置和 `/api/idp` 管理 API。
* [Access Control](./security/access-control.md): 提供访问控制配置。
* [CORS](./security/how-to-use-cors.md): 提供 CORS 配置。

### Gravitino MCP 服务器

Gravitino MCP 服务器为 AI 工具提供了管理 Gravitino 元数据的能力。

* [Gravitino MCP server](./gravitino-mcp-server.md)：使用 Gravitino MCP server 的完整指南。

### 编程指南

* [Gravitino Open API](./api/rest/gravitino-rest-api)：提供 Gravitino 的完整 Open API 定义。
* [Gravitino Java doc](pathname:///docs/2.0.0-SNAPSHOT/api/java/index.html)：提供 Gravitino API 的 Javadoc。
* [Gravitino Python doc](pathname:///docs/2.0.0-SNAPSHOT/api/python/index.html)：提供 Gravitino API 的 Python 文档。

### 开发指南

* [如何构建 Gravitino](./how-to-build.md)：一份关于从
源码构建 Gravitino 的完整指南。
* [如何测试 Gravitino](./how-to-test.md)：一份关于运行 Gravitino 单元和
集成测试的完整指南。
* [如何签名和验证 Gravitino 发行版](./how-to-sign-releases.md)：一份关于签名和验证
Gravitino 发行版的指南。
* [发布 Docker 镜像](./publish-docker-images.md)：一份关于发布 Gravitino Docker 镜像的指南；
还列出了 Gravitino CI Docker 镜像和发行版镜像的变更日志。
* [如何升级 Gravitino](./how-to-upgrade.md)：一份关于将 Gravitino 存储后端的模式从一个发行版本升级到另一个发行版本的指南。

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=Overview" alt="" />
