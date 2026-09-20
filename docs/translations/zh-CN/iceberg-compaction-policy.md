---
title: "Iceberg Compaction Policy"
slug: "/iceberg-compaction-policy"
date: 2026-03-05
keyword: "iceberg, compaction, policy, optimizer, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 概述

`system_iceberg_compaction` 是一种内置策略类型，优化器使用它来为 Iceberg 表生成压缩策略和作业上下文。

此策略支持 `CATALOG`、`SCHEMA` 和 `TABLE` 元数据对象。

## 政策内容

`system_iceberg_compaction` 的类型化内容支持以下字段：

| 字段 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `minDataFileMse` | 否 | `405323966463344` | 指标 `custom-data-file-mse` 的最小阈值。必须 `>= 0`。 |
| `minDeleteFileNumber` | 否 | `1` | 指标 `custom-delete-file-number` 的最小阈值。必须 `>= 0`。 |
| `dataFileMseWeight` | 否 | `1` | `custom-data-file-mse` 的分数权重。必须 `>= 0`。 |
| `deleteFileNumberWeight` | 否 | `100` | `custom-delete-file-number` 的分数权重。必须 `>= 0`。 |
| `maxPartitionNum` | 否 | `50` | 优化器选择的最大分区数。必须 `> 0`。 |
| `rewriteOptions` | 否 | `{}` | 额外的重写选项，展开为 `job.options.*` 规则。 |

## 生成的规则和属性

策略内容转换为：

- 属性：
- `strategy.type=iceberg-data-compaction`
- `job.template-name=builtin-iceberg-rewrite-data-files`
- 规则：
- `trigger-expr=custom-data-file-mse >= minDataFileMse || custom-delete-file-number >= minDeleteFileNumber`
- `score-expr=custom-data-file-mse * dataFileMseWeight + custom-delete-file-number * deleteFileNumberWeight`
- `max-partition-num=<maxPartitionNum>`
- `job.options.<key>=<value>` 用于每个重写选项

## 参数调优指南

### 指标单位与阈值公式

`custom-data-file-mse` 预期以 `byte^2` 为单位。

使用目标文件大小和容差率设置 `minDataFileMse`：

`minDataFileMse = (target-file-size-bytes * ratio)^2`

推荐的 `ratio` 范围：`0.1` 至 `0.2`。

默认值使用：

- `target-file-size-bytes = 134217728` (128 MiB)
- `ratio = 0.15`
- `minDataFileMse = 405323966463344`

### 触发行为

触发器表达式使用 `>=`。

- 设置 `minDeleteFileNumber = 1` 以在至少存在一个删除文件时触发。
- 设置 `minDeleteFileNumber > 1` 以降低删除文件的压缩频率。

### 评分权重

分数计算如下：

`custom-data-file-mse * dataFileMseWeight + custom-delete-file-number * deleteFileNumberWeight`

- 保持 `dataFileMseWeight = 1` 作为基准。
- 如果希望优先处理包含更多删除文件的分区，请增加 `deleteFileNumberWeight`。
- 保持这两个权重均为非负数。

### 生产环境启动的推荐默认设置

- `minDataFileMse = 405323966463344` (由 128 MiB 和比率 `0.15` 计算得出)
- `minDeleteFileNumber = 1`
- `dataFileMseWeight = 1`
- `deleteFileNumberWeight = 100`
- `maxPartitionNum = 50`

推荐的 `rewriteOptions`：

- `target-file-size-bytes = 134217728`
- `min-input-files = 5`
- `delete-file-threshold = 1`

## 策略示例

<Tabs groupId='language' queryString>
<TabItem value="shell" label="Shell">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iceberg_compaction_default",
    "comment": "Built-in iceberg compaction policy",
    "policyType": "system_iceberg_compaction",
    "enabled": true,
    "content": {}
  }' \
  http://localhost:8090/api/metalakes/test/policies
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoClient client = ...;

PolicyContent content = PolicyContents.icebergDataCompaction();

Policy policy =
    client.createPolicy(
        "iceberg_compaction_default",
        "system_iceberg_compaction",
        "Built-in iceberg compaction policy",
        true,
        content);
```

</TabItem>
</Tabs>

## 将策略附加到元数据对象

创建策略后，通过标准策略关联 API 将其与目录、架构或表进行关联。
优化器将读取生成的规则和属性，以评估策略触发和作业提交上下文。
