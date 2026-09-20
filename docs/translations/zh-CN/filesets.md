---
slug: /filesets
keyword: fileset, files, storage location, GVFS, Gravitino
license: This software is licensed under the Apache License version 2.
title: 文件集
---
## 简介

文件集（Fileset）是指向文件的命名指针。表描述行与列，而文件集描述
位置，因此非结构化和半结构化数据与目录中的其他所有对象获得同等待遇：
目录（Catalog）：名称、层级结构中的位置、标签、策略以及所有者。

核心在于间接引用。通过名称读取文件集的代码不需要携带存储桶路径，因此
在集群或存储系统之间移动数据只需更改文件集，而无需更改每个读取它的作业。

这种间接引用由 Gravitino 虚拟文件系统（Gravitino Virtual File System，简称 GVFS）提供。GVFS 是一种文件系统
实现，它将文件集名称解析为其存储位置，然后
透传到底层系统，无论是 HDFS、S3、GCS、ADLS 还是 OSS。路径采用
`gvfs://fileset/{catalog_name}/{schema_name}/{fileset_name}` 的形式，因此 Spark 作业、pandas 脚本或
Hadoop shell 命令读取的是目录名，而不是存储桶 URL。

GVFS 提供两种实现。Java 实现了 Hadoop 兼容文件系统
接口，因此任何已经支持 HDFS 路径的工具都能工作，且需要 Hadoop 3.3.1 或更高版本。
Python 实现基于 fsspec 构建，因此可与 pandas、PyArrow 及该
生态系统中的其他工具配合使用。此外还有一个 FUSE 实现，用于将文件集挂载为本地目录。

:::note
FUSE 实现（`gvfs-fuse`）已弃用。它被排除在 Gradle 构建之外，且
不再获得进一步开发或支持；请改用 Java 或 Python GVFS 实现。
:::

凭证是另一半关键所在。通过 GVFS 访问存储的调用方可以获取
由 Gravitino 分发的短期凭证，而不是持有自身的长期云密钥，
这正是将间接引用转变为治理边界而不仅仅是便利之处的关键。参见
[凭证分发](./security/credential-vending.md)。

文件集位于文件集目录内的模式（Schema）中。Gravitino 自身管理该目录，而非
联邦外部目录，因此创建时不需要提供者。

## 快速开始

**1. 创建文件集目录和模式。** 参见
[目录和模式](./catalogs-and-schemas.md)。文件集目录通常携带基础
`location`，模式可以进一步缩小其范围。

**2. 创建文件集。** 为其指定名称、类型和存储位置。创建托管
文件集会创建目录；指向现有路径则使其成为外部文件集。

**3. 按名称读取。** 引擎通过 GVFS 或客户端访问文件，而不是通过原始路径。
参见[如何使用 GVFS](./how-to-use-gvfs.md)。

## 文件集模型

### 托管与外部

托管文件集属于 Gravitino。创建它会创建目录，删除它会删除
数据。

外部文件集指向已存在的位置，并保持由其他方控制。
删除它会移除 Gravitino 记录，但保留文件。

这种区别仅在删除时才有意义，并且这是创建时最需要
正确处理的关键点。

### 存储位置

一个文件集至少有一个存储位置，也可以有多个，每个都有名称。默认位置由
`default-location-name` 属性选择，未提供名称的存储位置将被记录为
`unknown`。

一个文件集上的多个位置用于在不同集群或
区域间描述同一逻辑数据集，读取方选择其应使用的位置，而不是各自携带自己的路径。

位置也可以继承：具有 `location` 属性的目录或模式提供基础路径，
在其下创建的文件集可以从中获取其位置，而无需明确指定完整路径。

位置可以是模板，而不是固定路径。诸如 `{{catalog}}`、
`{{schema}}`、`{{user}}` 和 `{{project}}` 等占位符在文件集创建时被填充，其值由
`placeholder-` 属性提供。随后，一个目录级模板会为在其下创建的每个文件集生成一致的
目录布局，而不是每个文件集都靠手动
明确指定。

### 属性

属性是自由格式的，其中 `default-location-name` 和 `location-{name}` 键保留用于
位置分配。其他所有属性由用户定义，并随文件集一起传递。

## 在 UI 中使用文件集

打开文件集目录会列出其中的模式和文件集。文件集显示其类型、
存储位置和属性。

文件集显示其携带的标签（包括继承的标签），但目前无法从 UI
进行标记。将标签附加到文件集需要通过 API 进行。

## 权限

| 权限        | 可授予对象                          | 允许的操作              |
|------------------|---------------------------------------|-----------------------------|
| `CREATE_FILESET` | Metalake、目录、模式或文件集 | 创建文件集           |
| `READ_FILESET`   | Metalake、目录、模式或文件集 | 读取文件集的文件   |
| `WRITE_FILESET`  | Metalake、目录、模式或文件集 | 写入文件集的文件   |

在更广范围内授权会覆盖其下的所有内容。删除文件集的操作仅保留给
Metalake 所有者和对象所有者。

## 使用 API

可以通过 REST 以及 Java 和 Python
客户端创建、列出、修改和删除文件集。端点、负载结构以及完整示例请参见
[管理文件集元数据](./manage-fileset-metadata-using-gravitino.md)。