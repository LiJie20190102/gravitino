---
title: "Manage Metalakes"
slug: "/manage-metalake-using-gravitino"
keyword: "metalake management, metalake, admin client, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## Introduction

This page covers the Gravitino API for metalakes. For what a metalake is, what it isolates, the
in-use behavior, deletion semantics, and permissions, see [Metalakes](./metalakes.md).

Metalakes sit above any single metalake, so these operations use the admin client rather than the
client used for everything inside one. Creating a metalake is reserved for service admins,
configured with `gravitino.authorization.serviceAdmins`.

## Metalake Operations

### Create a Metalake

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "production",
  "comment": "Production estate",
  "properties": {}
}' http://localhost:8090/api/metalakes
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoAdminClient adminClient = GravitinoAdminClient
    .builder("http://localhost:8090")
    .build();

GravitinoMetalake metalake = adminClient.createMetalake(
    "production", "Production estate", new HashMap<>());
```

</TabItem>
<TabItem value="python" label="Python">

```python
admin_client = GravitinoAdminClient(uri="http://localhost:8090")
admin_client.create_metalake(
    name="production", comment="Production estate", properties={})
```

</TabItem>
</Tabs>

### Load a Metalake

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/production
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoMetalake metalake = adminClient.loadMetalake("production");
```

</TabItem>
<TabItem value="python" label="Python">

```python
metalake = admin_client.load_metalake("production")
```

</TabItem>
</Tabs>

### Alter a Metalake

Changes are applied as a list in one request.

| Change             | JSON                                                         | Java                                           | Python                                          |
|--------------------|--------------------------------------------------------------|------------------------------------------------|-------------------------------------------------|
| Rename             | `{"@type":"rename","newName":"metalake_renamed"}`            | `MetalakeChange.rename("metalake_renamed")`    | `MetalakeChange.rename("metalake_renamed")`     |
| Update the comment | `{"@type":"updateComment","newComment":"new_comment"}`       | `MetalakeChange.updateComment("new_comment")`  | `MetalakeChange.update_comment("new_comment")`  |
| Set a property     | `{"@type":"setProperty","property":"key1","value":"value1"}` | `MetalakeChange.setProperty("key1", "value1")` | `MetalakeChange.set_property("key1", "value1")` |
| Remove a property  | `{"@type":"removeProperty","property":"key1"}`               | `MetalakeChange.removeProperty("key1")`        | `MetalakeChange.remove_property("key1")`        |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "updateComment", "newComment": "Production estate, EMEA"}
  ]
}' http://localhost:8090/api/metalakes/production
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoMetalake metalake = adminClient.alterMetalake(
    "production", MetalakeChange.updateComment("Production estate, EMEA"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
metalake = admin_client.alter_metalake(
    "production", MetalakeChange.update_comment("Production estate, EMEA"))
```

</TabItem>
</Tabs>

### Enable or Disable a Metalake

A metalake that is not in use can only be listed, loaded, enabled, or dropped. Enabling one that is
already in use does nothing, and the same is true of disabling one already out of use.

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PATCH -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{"inUse": false}' \
  http://localhost:8090/api/metalakes/production
```

</TabItem>
<TabItem value="java" label="Java">

```java
adminClient.disableMetalake("production");
adminClient.enableMetalake("production");
```

</TabItem>
<TabItem value="python" label="Python">

```python
admin_client.disable_metalake("production")
admin_client.enable_metalake("production")
```

</TabItem>
</Tabs>

### 删除 Metalake

如果没有 `force`，metalake 必须没有 catalog 且必须未被使用。如果使用 `force`，Gravitino
将删除 metalake 及其下注册的所有内容，无论其是否正在被使用。外部
系统不受影响；托管对象及其数据将被删除。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/production?force=false"
```

</TabItem>
<TabItem value="java" label="Java">

```java
boolean dropped = adminClient.dropMetalake("production", false);
```

</TabItem>
<TabItem value="python" label="Python">

```python
dropped = admin_client.drop_metalake("production", force=False)
```

</TabItem>
</Tabs>

### 列出 Metalakes

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoMetalake[] metalakes = adminClient.listMetalakes();
```

</TabItem>
<TabItem value="python" label="Python">

```python
metalakes = admin_client.list_metalakes()
```

</TabItem>
</Tabs>
