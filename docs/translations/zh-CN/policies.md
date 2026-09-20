---
title: "Policies"
slug: "/policies"
keyword: "policy, policies, governance, metadata object, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

## 介绍

策略是一个命名的规则集合，您在 metalake 中创建一次并附加到元数据对象。
将策略附加到 catalog 或 schema 会将其应用于其下的所有内容，因此，一个变化的设置
按表可以在其适用的级别上表达一次，并在其不适用的地方被覆盖。

标签和策略是近亲，区别在于它们所承载的内容。标签用于分类，而
其内容就是它的名称。策略用于规定，其内容是一组某事物据以行动的规则。

策略分为两种。内置策略具有由 Gravitino 定义的类型以及一个消费者，该消费者
对其执行操作。自定义策略携带您自己的规则，Gravitino 会存储、继承这些规则，并将其提供
给您围绕它构建的任何系统。

常见用途：

- 为整个 catalog 设置表维护行为，而不是逐表设置，并让新的
表无需进一步操作即可获取该行为
- 针对存在于多个 catalog 中的元数据记录一次规则，这样每个通过
Gravitino 访问这些对象的引擎都能看到相同的规则
- 为从 Gravitino 读取策略的外部执行或调度系统提供数据，而不是
保留其自身的规则适用范围副本

## 快速开始

**1. 创建策略。** 策略是从 UI 中的策略列表创建的，这会创建自定义
策略。一个策略需要一个名称、它支持的对象类型及其规则。内置策略是
通过 REST 创建的。

**2. Attach it to an object.** Open the catalog, schema, table, fileset, topic, model, view, or function you want to
govern and add the policy from its policy control. Only policies that already exist in the metalake
are offered.

**3. 查看策略附加的位置。** 在策略列表中选择一个策略名称会显示
其直接附加到的对象。

## 策略模型

### 策略类型

| Type                        | Rules                                | Consumed by               |
|-----------------------------|--------------------------------------|---------------------------|
| `system_iceberg_compaction` | 压缩阈值和调度 | 表维护服务 |
| `custom`                    | 您定义的自由格式映射           | 您提供的系统      |

内置类型的名称以 `system_` 开头，并具有由 Gravitino 定义的内容形状。该
压缩策略记录在 [Iceberg 压缩策略](./iceberg-compaction-policy.md) 中，并且
作用于它的服务在
[表维护服务](./table-maintenance-service/optimizer.md) 中。

自定义策略的类型为 `custom`，Gravitino 不会尝试解释其内部
`customRules` 的内容。这些规则会被存储，沿层级结构向下继承，并返回给任何请求的
客户端。

UI 仅创建自定义策略。内置策略通过 REST 创建，并具有其自身的内容
形状。

### 什么可以承载策略

元数据对象由类型和名称标识，目录以下的每个层级由
点分隔。八种对象类型可以携带策略。

| 对象类型 | 名称形式                                     |
|-------------|-----------------------------------------------|
| `CATALOG`   | `{catalog_name}`                              |
| `SCHEMA`    | `{catalog_name}.{schema_name}`                |
| `TABLE`     | `{catalog_name}.{schema_name}.{table_name}`   |
| `FILESET`   | `{catalog_name}.{schema_name}.{fileset_name}` |
| `TOPIC`     | `{catalog_name}.{schema_name}.{topic_name}`   |
| `MODEL`     | `{catalog_name}.{schema_name}.{model_name}`   |
| `VIEW`      | `{catalog_name}.{schema_name}.{view_name}`    |
| `FUNCTION`  | `{catalog_name}.{schema_name}.{function_name}`|

Columns cannot carry a policy, which is narrower than
[tags](./tags.md). A metalake cannot carry one either, so to reach every object
in a catalog, attach the policy to the catalog.

每个策略还会声明其自己的 `supportedObjectTypes`，这会进一步缩小该
策略的列表。

### 内容

策略内容包含三个部分：`supportedObjectTypes` 列表、规则和属性。

`supportedObjectTypes` 在策略创建时即被固定，且之后无法更改，因此一个
仅针对表的策略在其整个生命周期内都会保持该状态。

规则是消费者所评估的内容。对于自定义策略，它们作为一个 map 存在于 `customRules` 下
由你定义，其中名称由你决定，值为任意 JSON 值。

```json
"customRules": {
  "retentionDays": 30,
  "maxTableSizeGb": 500,
  "requiresApproval": true
}
```

Gravitino 不解释这些名称或值。任何消费该策略的组件决定
`retentionDays` 的含义以及如何处理它。

内置策略具有一个由 Gravitino 定义的规则集，并且使用它的服务记录了如何
应用这些规则。压缩策略包含 `minDataFileMse`、`minDeleteFileNumber`、
`dataFileMseWeight`、`deleteFileNumberWeight`、`max-partition-num`，以及触发器和评分
表达式，以及传递给作业的任何 `job.options.` 条目。这些名称及其
含义在 [Iceberg compaction policy](./iceberg-compaction-policy.md) 中有介绍。

属性描述的是策略本身，而不是它所要求的行为。规则会随着你
调整阈值而变化，而属性保持稳定。压缩策略使用属性来指定其
策略类型和作业模板名称，这些属性告诉表维护服务要运行什么，并且这些
是由 Gravitino 设置的，而不是由你设置的。对于自定义策略，属性是你自己的，适合用于记录事实
例如哪个团队拥有该策略，哪个系统使用它，或者哪个版本的规则集
代表。任何针对对象进行评估的内容都应属于规则。

属性位于策略而非附件上，因此携带该策略的每个对象看到
相同的值。

### 启用标志

`enabled` 标志将策略标记为对读者处于活动或非活动状态。Gravitino 不会对其执行操作，
因此，禁用策略不会将其分离，也不会改变消费者接收的内容。将其视为一种信号，
传递给读取该策略的人，这对于在审查期间保留策略而不删除它非常有用。

### 继承

一个对象会显示附加到它的策略以及附加到其每个祖先的策略，所以
catalog 上的策略适用于其下的每个 schema、table、fileset、topic、model、view 和 function。对于
支持多级 schema 的 catalog，中间的 schema 也是祖先。

每个策略出现一次，无论它是通过一个还是多个祖先到达该对象。一个策略
直接附加到对象上的算作直接，即使祖先也带有它。

直接和继承的附加项是可区分的。在 UI 中，继承的策略会标有一个
锁图标。通过 REST，使用 `details=true` 请求的策略列表会在
每个策略中包含一个 `inherited` 字段，而纯名称列表则没有。

仅通过继承到达对象的策略无法在那里移除。将其从
携带它的祖先中分离，这也会影响该祖先之下的所有其他对象。

继承是在读取对象时解析的，而不是存储在对象上，因此将一个
策略附加到目录会立即对之后创建的表生效。

## 在 UI 中使用策略

### 管理策略集

策略列表包含 metalake 中的每个策略，并且可以被搜索。策略可以被重命名，其
注释和规则被编辑，并且其启用标志可以从那里切换。通过 REST 创建的策略，
包括内置的，与其余的一起出现在列表中。

删除策略会将其从所有附加了该策略的对象中移除，且不会警告有多少
受影响的对象，并且无法恢复附加关系。

### 附加与分离

策略是从对象附加而非从策略附加的，因此请打开对象并使用策略
控件。继承的策略不带有移除控件。分离操作仅移除直接附加
，因此对象仍然会显示它从祖先继承的策略。

### 查找策略的使用位置

选择策略名称会打开一个视图，列出该策略直接附加到的对象。
不包含继承的覆盖范围，因此附加到某个目录的策略会列出该目录，而不是
其下的表。

## 权限

策略权限保留在策略上，并且除了对象上的权限之外还适用，这些对象
受管。

| 权限       | 可授权对象                 | 允许的操作                                 |
|-----------------|------------------------------|------------------------------------------------|
| `CREATE_POLICY` | Metalake                     | 在 Metalake 中创建策略              |
| `APPLY_POLICY`  | Metalake 或单个策略 | 读取策略并将其附加或分离 |

修改和删除策略仅限 metalake 所有者和策略所有者。附加
策略也需要访问受管对象的权限。策略列表仅显示
用户被允许读取的策略。

## 使用 API

可以通过 REST 和 Java 客户端创建、附加和读取策略。端点、负载
形状和实际示例位于[管理策略](./manage-policies-in-gravitino.md)中。
