---
title: "Metalakes"
slug: "/metalakes"
keyword: "metalake, tenant, namespace, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

metalake 是 Gravitino 层次结构的顶层，也是其他所有内容存在的边界。
Catalogs、schemas、tables、filesets、topics、models 和 functions 都位于其下，同样还有
应用于它们的用户、组、角色、标签、策略和作业。

没有任何事物能跨越该边界：

- 用户和组是一个 metalake 中的记录。同一个人在两个 metalake 中工作需要
在每个 metalake 中都有一个用户，并且置备是按 metalake 完成的
- 角色在一个 metalake 内定义和授予，因此在一个 metalake 中持有的角色在
另一个中不具备任何权限
- 在一个 metalake 中创建的标签或策略不能附加到另一个 metalake 中的对象上
- 名称只需在一个 metalake 内唯一即可

这使得 metalake 成为隔离环境、业务部门或租户时的首选单元
它们不应看到彼此的元数据。

大多数安装只需要很少的。每个生产环境一个 metalake，也许还有一个用于开发环境，
是一种常见的架构。每个客户端连接到单个 metalake 并在其中工作，因此添加更多
意味着人们必须知道他们处于哪一个之中。

## 快速开始

**1. 创建 metalake。** Metalake 是从 UI 中的 metalake 列表创建的，或者使用
admin 客户端。一个 metalake 需要一个名称，并且可以带有注释和属性。只有服务管理员
才能创建一个。

**2. 连接一个 catalog。** 新建的 metalake 是空的。参见
[Catalogs 和 Schemas](./catalogs-and-schemas.md).

**3. 将客户端指向它。** 客户端在连接时会指定 metalake，因此它们所做的所有操作
之后都会在其中进行。

## Metalake 模型

### 名称和属性

metalake 名称在整个服务器中是唯一的，也是每个客户端在连接时所指定的名称，因此
重命名一个会改变每个已存储连接必须请求的内容。

属性是自由格式的键值对，包含一个保留键。`in-use` 记录
metalake 是否可用，默认为 `true`，并通过启用和禁用操作进行设置
而不是直接写入该属性。

metalake 不能带有标签或策略，因此无法对一切进行分类或治理，在
顶层一次性进行。最广泛的附加点是 catalog。

### 使用中与未使用

一个未被使用的 metalake 只能被列出、加载、启用或删除。所有其他操作
对它或其内部任何内容的操作都会失败，这使得禁用成为一种将 estate 下线的方式
且不会删除任何内容。

启用一个已经在使用中的 metalake 不会产生任何作用，同样地，禁用一个
已经不在使用中的 metalake 也是如此。

## 在 UI 中使用 Metalakes

metalake 列表包含服务器上的每一个 metalake。可以创建、编辑、启用或
禁用，并从那里删除。

选择 metalake 决定了 UI 其余部分的范围。其他所有屏幕，包括 catalogs，
compliance 和 dashboard 视图，描述了当前选定的 metalake。

## 删除 Metalake

metalake 被强制或非强制删除，且这种区别很重要。

如果不强制，metalake 必须不包含任何 catalogs 且未被使用。任一条件失败
将导致请求失败，而不是删除任何内容。

强制操作下，Gravitino 会删除 metalake 及其下注册的所有内容，包括 catalogs，
schemas、tags 和 policies，无论 metalake 是否正在使用。外部系统不受影响，
因此，由 Gravitino 注册而非创建的 Hive 表或 S3 存储桶得以保留。
托管对象，例如托管 fileset，会连同其数据一起被删除。

## 权限

创建 metalake 的权限仅保留给服务管理员，通过
服务器配置中的 `gravitino.authorization.serviceAdmins` 进行配置。其他任何人都无法创建，无论
他们持有什么权限。

修改、启用、禁用和删除 metalake 的操作保留给其所有者。

## 使用 API

Metalakes 可以通过 REST 以及通过
Java 和 Python 管理客户端进行创建、列出、更改、启用、禁用和删除。端点、负载结构和操作示例位于
[管理 Metalakes](./manage-metalake-using-gravitino.md)。
