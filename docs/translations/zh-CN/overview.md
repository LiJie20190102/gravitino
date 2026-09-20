---
title: "Overview"
slug: "/overview"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino 是一个高性能、地理分布式且联邦化的元数据湖。它直接管理
不同来源、类型和区域中的元数据。它还为用户提供对数据和 AI 资产的统一元数据访问。

![Gravitino 架构](assets/gravitino-architecture.png)

Gravitino 旨在提供几个关键特性：

* 面向多区域数据的 SSOT (Single Source of Truth)，支持地理分布式架构。
* 面向用户和引擎的统一数据 + AI 资产管理。
* 安全集中一处，集中管理不同数据源的安全性。
* 内置数据管理 + 数据访问管理。

## 架构

![Gravitino 模型与架构](assets/gravitino-model-arch.png)

* **功能层**：Gravitino 提供了一个 API，供用户管理和治理
元数据，包括标准的元数据创建、更新和删除操作。同时，它还提供了以统一方式治理元数据的能力，包括访问控制、发现等。
* **接口层**：Gravitino 提供标准的 REST API 作为用户的接口层。未来的支持将包括 Thrift 和 JDBC 接口。
* **核心对象模型**：Gravitino 定义了一个通用的元数据模型，用于表示不同来源和类型的元数据，并以统一的方式进行管理。
* **连接层**：在连接层，Gravitino 提供了一组连接器来连接不同的元数据源，包括 Apache Hive、MySQL、PostgreSQL 等。它还允许连接和管理除表格数据之外的异构元数据。

## 功能

### 统一元数据管理与治理

Gravitino 为不同类型的元数据源抽象了统一的元数据模型和 API。
例如，用于表格数据的关系型元数据模型，如 Hive、MySQL、PostgreSQL 等。
用于所有非结构化数据的文件元数据模型，如 HDFS、S3 等。

除了统一的元数据模型之外，Gravitino 还提供了一个统一的元数据治理层
以统一的方式管理元数据，包括访问控制、审计、发现以及
其他。

### 直接元数据管理

不同于传统的元数据管理系统，它们需要收集元数据
主动或被动地从底层系统中获取，Gravitino 直接管理这些系统。
它提供了一组连接器，用于连接到不同的元数据源。
Gravitino 中的更改会直接反映在底层系统中，反之亦然。

### 地理分布支持

Gravitino 支持 Iceberg REST (IRC) 目录的地理分布式部署。Gravitino 的不同实例可以运行在不同区域或云中，通过本地 IRC 目录将请求代理到远程 IRC 目录，从而让用户获得跨区域或云的元数据全局视图。

### 多引擎支持

Gravitino 支持不同的查询引擎来访问元数据。它支持
[Trino](https://trino.io/)，用户可以使用 Trino 来查询元数据和数据，而无需
更改现有的 SQL 方言。

此外，Gravitino 已扩展支持，包含 [Apache Spark](https://spark.apache.org/)，
[Apache Flink](https://flink.apache.org/) 和 [Daft](https://docs.daft.ai/) 等查询引擎。进一步的增强和
对受支持的查询引擎的补充也已列入路线图。

### AI资产管理

Gravitino 的目标是统一数据和 AI 资产中的数据管理，包括原始文件、模型等。

## 术语

### 元数据对象

* **Metalake**：元数据的容器/租户。通常，一个组拥有一个 metalake
来管理其中的所有元数据。每个 metalake 暴露一个三级命名空间 (catalog.schema.
table) 来组织数据。
* **Catalog**：catalog 是来自特定元数据源的元数据集合。
每个 catalog 都有一个相关的连接器来连接到特定的元数据源。
* **Schema**：Schema 是用于对元数据集合进行分组的第二级命名空间，schema 可以
指关系型元数据源中的数据库/schema，例如 Apache Hive、MySQL、
PostgreSQL 等。Schema 也可以指 fileset 和 model
catalog 的逻辑命名空间。
* **Table**：对于支持关系型
元数据源的 catalog，它是对象层次结构中的最低级别。你可以在 catalog 的特定 schema 中创建 Table。
* **Fileset**：fileset 元数据对象是指
文件系统中的文件和目录集合。fileset 元数据对象用于管理文件的逻辑元数据。
* **Model**：model 元数据对象表示特定 catalog 中的元数据，该 catalog
支持模型管理。
* **Topic**：topic 元数据对象表示特定 catalog 中的元数据，该 catalog
支持管理消息队列系统（如 Kafka）的 topic。
