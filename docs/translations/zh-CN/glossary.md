---
date: 2023-11-28
license: This software is licensed under the Apache License version 2.
title: 术语表
---
## API

- 应用程序编程接口，定义与服务器交互的方法和协议。

## AWS

- 亚马逊云科技，亚马逊提供的云计算平台。

## AWS Glue

- Hive Metastore 服务 (HMS) 的兼容实现。

## GPG/GnuPG

- Gnu Privacy Guard 或 GnuPG 是 OpenPGP 标准的开源实现。
  通常用于加密和签名文件及电子邮件。

## HDFS

- **HDFS** (Hadoop 分布式文件系统) 是一种开源分布式文件系统。
  它是 Apache Hadoop 生态系统的核心组件。
  HDFS 旨在作为分布式存储解决方案，存储和处理大规模数据集。
  具备高可靠性、容错性和卓越性能。

## HTTP Port

- 服务器监听传入连接的端口号。

## IP Address

- 互联网协议地址，分配给计算机网络中每个设备的数字标签。

## JDBC

- Java 数据库连接，用于将 Java 应用程序连接到关系型数据库的 API。

## JDBC URI

- 在 catalog 配置中指定的 JDBC 连接地址。
  通常包含数据库类型、主机、端口和数据库名称等组件。

## JDK

- Java 编程语言的软件开发工具包。
  JDK 提供用于编译、调试和运行 Java 应用程序的工具。

## JMX

- Java 管理扩展，提供用于管理和监控 Java 应用程序的工具。

## JSON

- JavaScript 对象表示法，一种轻量级数据交换格式。

## JSON Web Token

- 参见 [JWT](#keys-file)。

## JVM

- 一种使计算机能够运行 Java 应用程序的虚拟机。
  JVM 实现了与底层硬件不同的抽象机器。

## JVM Instrumentation

- 向 [JVM](#jvm-instrumentation) 添加监控和管理功能的过程，
  主要用于收集性能指标。

## JVM Metrics

- 与 [Java 虚拟机](#jvm-instrumentation)性能和行为相关的指标。
  一些有价值的指标包括内存使用、垃圾回收和缓冲池指标。

## JWT

- 一种紧凑、URL 安全的表示形式，用于在两方之间传递声明。

## KEYS File

- 包含用于签名先前版本公钥的文件，是验证签名所必需的。

## PGP Signature

- 使用 PGP (Pretty Good Privacy) 算法生成的数字签名。
  该签名通常用于验证文件的真实性。

## REST

- 一组用于设计网络应用程序的架构原则。

## REST API

- 表述性状态转移 应用程序编程接口。
  一组使用标准 HTTP 方法构建和与 Web 服务交互的规则和约定。

## SHA256 Checksum

- 用于验证文件完整性的加密哈希函数。

## SHA256 Checksum File

- 包含另一个文件 SHA256 哈希值的文件，用于验证目的。

## SQL

- 一种用于管理和操作关系型数据库的编程语言。

## SSH

- 安全外壳协议，一种加密网络协议，用于在计算机网络上的安全通信。

## URI

- 统一资源标识符，标识互联网上名称或资源的字符串。

## YAML

- YAML 不是标记语言，一种人类可读的文件格式，常用于结构化数据。

## Amazon Elastic Block Store (EBS)

- 亚马逊云科技 提供的可扩展块存储服务。

## Apache Gravitino

- 由 Datastrato 最初创建的开源软件平台。
  专为高性能、地理分布和联邦元数据湖设计。
  Gravitino 能够直接管理不同来源、类型和区域的元数据，
  为数据和 AI 资产提供统一的元数据访问。

## Apache Gravitino Configuration File (gravitino.conf)

- Gravitino 服务器的配置文件，位于 `conf` 目录中。
  遵循标准属性文件格式，包含 Gravitino 服务器的设置。

## Apache Hadoop

- 一种开源的分布式存储和处理框架。

## Apache Hive

- 一个开源的数据仓库软件项目。
  提供类 SQL 查询语言用于管理和查询大型数据集。

## Apache Iceberg

- 一种开源的、支持版本化的大规模数据处理表格式。

## Apache Iceberg Hive Catalog

- **Iceberg Hive catalog** 是专为 Apache Iceberg 表格式设计的元数据服务。
  允许外部系统使用 Hive metastore thrift 客户端与 Iceberg 元数据交互。

## Apache Iceberg JDBC Catalog

- **Iceberg JDBC catalog** 是专为 Apache Iceberg 表格式设计的元数据服务。
  允许外部系统使用 [JDBC](#jdbc-uri) 与 Iceberg 元数据服务交互。

## Apache Iceberg REST Catalog

- **Iceberg REST Catalog** 是专为 Apache Iceberg 表格式设计的元数据服务。
  允许外部系统使用 [REST API](#sha256-checksum) 与 Iceberg 元数据服务交互。

## Apache License Version 2

- 由 Apache 软件基金会编写的宽松开源软件许可证。

## Authentication Mechanism

- 用于验证访问服务器的用户和客户端身份的方法。

## Binary Distribution Package

- 包含已编译可执行文件的软件包，用于分发和部署。

## Catalog

- 来自特定元数据源的元数据集合。

## Catalog Provider

- 用于存储和管理元数据 catalog 的特定系统或技术。

## Columns

- 表中单独的字段或属性。
  每一列都有名称、数据类型、注释和是否可为空等属性。

## Continuous Integration (CI)

- 在代码变更提交到版本控制时自动构建和测试代码变更的做法。

## Dependencies

- 项目编译和功能所需的外部库或模块。

## Distribution

- 软件的打包和可部署版本。

## Docker

- 一个用于开发、交付和在容器中运行应用程序的平台。

## Docker Container

- 一个轻量级、独立的包，包含运行软件所需的一切。
  容器将应用程序与其依赖项和运行时打包以便分发。

## Docker Hub

- 用于 Docker 容器的基于云的注册表服务。
  用户可以使用该服务发布、浏览和下载容器化软件。

## Docker Image

- 一个轻量级、独立的包，包含运行软件所需的一切。
  Docker 镜像通常包含代码、运行时、库和系统工具。

## Dockerfile

- 用于构建 Docker 镜像的配置文件。
  Dockerfile 包含构建用于分发软件的标准镜像的指令。

## Dropwizard Metrics

- 一个 Java 库，用于测量应用程序性能并提供对各种指标类型的支持。

## Environment Variables

- 用于自定义进程运行时配置的变量。

## Geo-distributed

- 数据或服务跨多个地理位置的分布。

## Git

- 一种分布式版本控制系统，用于跟踪软件制品。

## GitHub

- 一个基于 Web 的平台，使用 Git 进行版本控制和社区协作。

## GitHub Actions

- GitHub 提供的持续集成和持续部署 (CI/CD) 服务。
  GitHub Actions 自动化构建、测试和部署工作流。

## GitHub Labels

- 分配给 GitHub issues 或 pull requests 的标签，用于组织或工作流自动化。

## GitHub Pull Request

- 用户提交的对 GitHub 仓库的建议更改。

## GitHub Repository

- GitHub 存储项目源代码和相关文件的位置。

## GitHub Workflow

- 由 GitHub 仓库上的特定事件触发的一系列自动化步骤。

## Gradle

- 一种用于构建、测试和部署项目的自动化工具。

## Gradlew

- 用于执行 Gradle 命令的 Gradle 包装器脚本。

## Hashes

- 由某些数据生成的加密哈希值。
  典型用例是验证文件的完整性。

## Headless

- 没有本地控制台的系统。

## Identity Fields

- 表中定义记录标识的字段。
  在表的范围内，标识字段用作行的唯一标识符。

## Integration Tests

- 在将组件集成到更大系统中时确保软件正确性和兼容性的测试。

## Java Database Connectivity (JDBC)

- 参见 [JDBC](#jdbc-uri)

## Java Development Kits (JDKs)

- 参见 [JDK](#jmx)

## Java Management Extensions

- 参见 [JMX](#json)

## Java Toolchain

- 用于检测和管理 JDK 版本的 Gradle 特性。 

## Java Virtual Machine

- 参见 [JVM](#jvm-instrumentation)

## Key Pair

- 一对加密密钥，包括用于验证的公钥和用于签名的私钥。

## Lakehouse

- **Lakehouse** 是一种现代数据管理架构，结合了数据湖和数据仓库的元素。
  旨在提供一个统一平台，用于存储、管理和分析原始非结构化数据
  （类似于数据湖）和精选结构化数据。

## Manifest

- 文件列表及其关联的元数据，共同定义发布或分发的结构和内容。

## Merge Operation

- Iceberg 中将多个快照的更改合并到新快照的过程。

## Metalake

- 元数据的顶层容器。 
  通常，metalake 是组织或公司的租户映射。
  所有 catalog、用户和角色都与一个 metalake 关联。 

## Metastore

- 存储数据仓库元数据的中央存储库。

## Module

- 项目中独特且可分离的部分。

## Open Authorization / OAuth

- 一种授权标准协议，允许第三方应用程序验证用户。
  应用程序无需访问用户凭据。

## OrbStack

- 在运行 Gravitino 集成测试时提到的一种 Docker 替代工具，适用于 macOS。

## Private Key

- 用于签名、解密或其他应保密操作的机密密钥。

## Properties

- 与 catalog、schema 和表关联的可配置设置和属性。
  属性设置影响相应实体的行为和存储。

## Protocol Buffers (Protobuf)

- 由 Google 开发的一种结构化数据序列化方法，类似于 XML 或 JSON。
  常用于系统之间高效且可扩展的通信。

## Public Key

- 公开共享的密钥，用于验证、加密或其他旨在公开的操作。

## Representational State Transfer

- 参见 [REST](#rest-api)

## RocksDB

- 一种开源键值存储数据库。

## Schema

- 数据库中用于组织表的逻辑容器。

## Secure Shell

- 参见 [SSH](#uri)

## Security Group

- 实例的虚拟防火墙，用于控制入站和出站流量。

## Serde

- 序列化/反序列化库。
  可以在表格格式与适合存储或传输的格式之间转换数据。

## Snapshot

- Iceberg 表状态的某一时刻快照，表示表的特定版本。

## Sort Order

- Hive 表中数据的排列，由表达式或方向指定。

## Spotless

- 一种工具或过程，用于强制执行代码格式标准并对代码应用自动格式化。

## Structured Query Language

- 参见 [SQL](#ssh)

## Table

- 以列和行存储的数据元素的结构化集合。

## Thrift

- 一种用于与 Hive Metastore 服务 (HMS) 通信的网络协议。

## Token

- 在计算和安全上下文中，<strong>令牌</strong> 是一小段不可分割的数据单元。 
  令牌在身份验证和授权等各个领域发挥关键作用。

## Trino

- 一种用于大数据处理的查询引擎。

## Trino Connector

- 用于将 Gravitino 与 Trino 集成的连接器模块。

## Ubuntu

- 基于 Debian 的 Linux 发行版，广泛用于云计算和服务器。

## Unit Test

- 一种软件测试类型，测试程序的各个组件或功能。
  单元测试有助于确保组件或功能在隔离状态下按预期工作。

## Verification

- 确认发布版本的真实性和完整性的过程。
  通常通过检查其签名和关联的哈希值来完成。

## Web UI

- 可通过 Web 浏览器访问的图形界面。