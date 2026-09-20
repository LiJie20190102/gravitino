---
title: "Manage Policies"
slug: "/manage-policies-in-gravitino"
keyword: "policy management, policy, policies, Gravitino, data governance"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页介绍用于策略的 Gravitino API。有关什么是策略、哪些对象类型可以携带策略、策略内容包含什么、
继承如何解析，以及如何在 UI 中使用策略，请参阅
[策略](./policies.md)。

Python 客户端不涵盖策略，因此以下示例仅限 REST 和 Java。

## 策略操作

### 创建策略

策略需要一个名称和一个类型。内容包含规则、策略支持的对象类型，
以及可选属性。`supportedObjectTypes` 在创建后不能更改。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "retention_30d",
  "comment": "Thirty day retention",
  "policyType": "custom",
  "enabled": true,
  "content": {
    "customRules": {"retentionDays": 30},
    "supportedObjectTypes": ["CATALOG", "SCHEMA", "TABLE"],
    "properties": {"owner": "platform"}
  }
}' http://localhost:8090/api/metalakes/test/policies
```

</TabItem>
<TabItem value="java" label="Java">

```java
PolicyContent content = PolicyContents.custom(
    ImmutableMap.of("retentionDays", 30),
    ImmutableSet.of(
        MetadataObject.Type.CATALOG,
        MetadataObject.Type.SCHEMA,
        MetadataObject.Type.TABLE),
    ImmutableMap.of("owner", "platform"));

Policy policy = client.createPolicy(
    "retention_30d", "custom", "Thirty day retention", true, content);
```

</TabItem>
</Tabs>

内置的压缩策略具有固定的内容结构，记录在
[Iceberg 压缩策略](./iceberg-compaction-policy.md) 中，以及一个辅助工具，它使用
默认值来构建它。

```java
Policy policy = client.createPolicy(
    "nightly_compaction",
    "system_iceberg_compaction",
    "Compaction defaults",
    true,
    PolicyContents.icebergDataCompaction());
```

### 列出策略

列表返回名称，或者在设置了 `details=true` 时返回完整的策略对象。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/policies

curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/test/policies?details=true"
```

</TabItem>
<TabItem value="java" label="Java">

```java
String[] policyNames = client.listPolicies();
Policy[] policies = client.listPolicyInfos();
```

</TabItem>
</Tabs>

### 获取策略

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/policies/retention_30d
```

</TabItem>
<TabItem value="java" label="Java">

```java
Policy policy = client.getPolicy("retention_30d");
```

</TabItem>
</Tabs>

### 修改策略

更改在一个请求中以列表形式应用。

| 更改             | JSON                                                                 | Java                                               |
|--------------------|----------------------------------------------------------------------|----------------------------------------------------|
| 重命名 | `{"@type":"rename","newName":"policy_renamed"}` | `PolicyChange.rename("policy_renamed")` |
| 更新备注 | `{"@type":"updateComment","newComment":"new_comment"}` | `PolicyChange.updateComment("new_comment")` |
| 更新内容 | `{"@type":"updateContent","policyType":"custom","newContent":{...}}` | `PolicyChange.updateContent("custom", newContent)` |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {
      "@type": "updateContent",
      "policyType": "custom",
      "newContent": {
        "customRules": {"retentionDays": 90},
        "supportedObjectTypes": ["CATALOG", "SCHEMA", "TABLE"],
        "properties": {"owner": "platform"}
      }
    }
  ]
}' http://localhost:8090/api/metalakes/test/policies/retention_30d
```

</TabItem>
<TabItem value="java" label="Java">

```java
PolicyContent newContent = PolicyContents.custom(
    ImmutableMap.of("retentionDays", 90),
    ImmutableSet.of(
        MetadataObject.Type.CATALOG,
        MetadataObject.Type.SCHEMA,
        MetadataObject.Type.TABLE),
    ImmutableMap.of("owner", "platform"));

Policy policy = client.alterPolicy(
    "retention_30d", PolicyChange.updateContent("custom", newContent));
```

</TabItem>
</Tabs>

### 启用或禁用策略

该标志是给读者的标记。Gravitino 不会对其执行操作，并且禁用策略既不
会将其分离，也不会改变消费者接收的内容。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PATCH -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{"enable": false}' \
  http://localhost:8090/api/metalakes/test/policies/retention_30d
```

</TabItem>
<TabItem value="java" label="Java">

```java
client.disablePolicy("retention_30d");
client.enablePolicy("retention_30d");
```

</TabItem>
</Tabs>

### 删除策略

删除策略也会将其从附加到的每个对象中移除。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/policies/retention_30d
```

</TabItem>
<TabItem value="java" label="Java">

```java
client.deletePolicy("retention_30d");
```

</TabItem>
</Tabs>

## 对象操作

### 附加和分离策略

两者都发生在同一个请求中，并且任一列表都可以省略。目录、模式、表、文件集，
主题、模型、视图和函数可以携带策略。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "policiesToAdd": ["retention_30d"],
  "policiesToRemove": ["retention_7d"]
}' http://localhost:8090/api/metalakes/test/objects/catalog/catalog1/policies
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("catalog1");
catalog.supportsPolicies().associatePolicies(
    new String[] {"retention_30d"},
    new String[] {"retention_7d"});

Schema schema = catalog.asSchemas().loadSchema("schema1");
schema.supportsPolicies().associatePolicies(new String[] {"retention_30d"}, null);
```

</TabItem>
</Tabs>

### 列出对象上的策略

响应包含从祖先继承的策略。使用 `details=true` 时，每个策略都带有一个
`inherited` 字段，而普通的名称列表则没有。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/test/objects/catalog/catalog1/policies?details=true"
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("catalog1");
String[] policyNames = catalog.supportsPolicies().listPolicies();
Policy[] policies = catalog.supportsPolicies().listPolicyInfos();
```

</TabItem>
</Tabs>

### 获取对象上的一个策略

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/objects/catalog/catalog1/policies/retention_30d
```

</TabItem>
<TabItem value="java" label="Java">

```java
Policy policy = catalog.supportsPolicies().getPolicy("retention_30d");
```

</TabItem>
</Tabs>

### 列出带有策略的对象

响应仅列出直接附加项，因此附加到目录的策略会返回该目录
而不是其下的对象。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/policies/retention_30d/objects
```

</TabItem>
<TabItem value="java" label="Java">

```java
Policy policy = client.getPolicy("retention_30d");
MetadataObject[] objects = policy.associatedObjects().objects();
int count = policy.associatedObjects().count();
```

</TabItem>
</Tabs>
