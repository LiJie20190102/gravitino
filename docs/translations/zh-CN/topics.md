---
title: "Topics"
slug: "/topics"
keyword: "topic, messaging, Kafka, streaming metadata, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

主题是消息流，在 Gravitino 中，它与其他任何对象一样都是元数据对象。注册
将 Kafka 集群作为消息目录，会将其主题置于与表和文件集相同的层级结构中，
从而使得流可以与其提供的数据一起被查找、分类和治理。

Gravitino 持有引用而非消息。列出 topic 会在请求时查询集群
，因此直接在 Kafka 中创建的 topic 会在下次查询 Gravitino 时出现，而通过 Gravitino 删除一个
topic 会在集群中将其删除。

其价值在于覆盖范围而非新功能。如果没有它，流将游离于目录之外，并且
也游离于适用于其他所有内容的任何分类和访问规则之外。

## 快速开始

**1. 连接消息目录。** 消息目录采用 `kafka` 提供程序和集群的
引导服务器。请参阅[目录和模式](./catalogs-and-schemas.md)和
[Apache Kafka 目录](./kafka-catalog.md)。

**2. 浏览或创建主题。** 连接的集群会显示已有的主题。创建一个
通过 Gravitino 创建会在集群中创建它。

**3. 对重要内容进行分类。** 主题带有标签和策略，方式与表相同。

## 主题模型

### 消息系统

Kafka 是目前唯一拥有目录的消息系统，通过 `kafka` 提供程序和
集群的 `bootstrap.servers` 进行连接。任何使用 Kafka 协议通信的系统都可以通过相同的
连接器工作。其他消息系统没有目录。

### 默认模式

消息目录呈现一个名为 `default` 的模式，包含集群中的每个主题。Kafka
没有自己的命名空间可以映射，因此在消息目录中创建或删除模式是
被拒绝，而不是被静默忽略。

对于大型集群而言，结果是主题在目录中不会像表那样
按数据库分组。标签是组织它们的方式。

### 名称与属性

主题名称在其 schema 中是唯一的，并与集群中的主题名称相匹配。

有两个属性可以在创建时设置。`partition-count` 设置分区数，并且可以
在之后修改。`replication-factor` 设置副本数，并且一旦主题存在便不可变。
如果任一未设置，则采用 broker 自身的默认值，分别来自 `num.partition` 和
`default.replication.factor`。

### Gravitino 存储什么以及不存储什么

Gravitino 存储主题在层次结构中的位置以及附加到其上的任何内容，包括标签，
策略和所有权。消息内容、偏移量、消费者组和延迟完全保留在
集群中。

消息模式也在目录之外。Gravitino 不与 schema registry 集成，
因此 topic 中消息的结构未在此处描述，且无法按字段进行分类
就像表列可以的那样。标签和策略附加到整个 topic 上。

## 在 UI 中使用主题

打开消息传递目录会列出其主题，选择其中一个会显示其属性。

主题显示其携带的标签和策略（包括继承的），但无法从
目前的 UI 进行打标签。将标签附加到主题需通过 API 进行。

## 权限

| 权限       | 可授予对象                        | 允许的操作        |
|-----------------|-------------------------------------|-----------------------|
| `CREATE_TOPIC`  | Metalake、目录、模式或主题 | 创建主题       |
| `PRODUCE_TOPIC` | Metalake、目录、模式或主题 | 写入主题    |
| `CONSUME_TOPIC` | Metalake、目录、模式或主题 | 从主题读取  |

在更广范围内授权将涵盖其下的所有内容。删除 topic 是保留给 metalake 的
所有者和对象所有者。

## 使用 API

主题可以通过 REST 和 Java 客户端进行创建、列出、修改和删除。该
Python 客户端不涵盖主题。端点、负载结构和实际示例位于
[管理消息元数据](./manage-messaging-metadata-using-gravitino.md)。
