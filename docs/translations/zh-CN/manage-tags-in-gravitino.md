---
title: "Manage Tags"
slug: "/manage-tags-in-gravitino"
keyword: "tag management, tag, tags, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页面涵盖了用于标签的 Gravitino API。关于什么是标签、哪些对象类型可以携带标签、继承如何
解析，以及如何在 UI 中使用标签，请参见 [Tags](./tags.md)。

## 标签操作

### 创建标签

标签需要一个名称，并且可以携带注释和属性。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "pii",
  "comment": "Personally identifiable information",
  "properties": {"owner": "data-governance"}
}' http://localhost:8090/api/metalakes/test/tags
```

</TabItem>
<TabItem value="java" label="Java">

```java
GravitinoClient client = ...
Tag tag = client.createTag(
    "pii",
    "Personally identifiable information",
    ImmutableMap.of("owner", "data-governance"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
tag = client.create_tag(
    tag_name="pii",
    comment="Personally identifiable information",
    properties={"owner": "data-governance"})
```

</TabItem>
</Tabs>

### 创建带有值约束的标签

标签可以接受任何值、无值，或者仅接受一组固定值。该约束在
创建时设置，且以后无法更改。在 REST 或 Python 中省略 `allowedValues` 会创建一个
不受限的标签；空列表会创建一个只能在不带值的情况下分配的标签。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "data_domain",
  "comment": "Business data domain",
  "allowedValues": ["finance", "risk", "ml"]
}' http://localhost:8090/api/metalakes/test/tags
```

</TabItem>
<TabItem value="java" label="Java">

```java
Tag tag = client.createTag(
    "data_domain",
    "Business data domain",
    ImmutableMap.of(),
    TagValueConstraint.ofAllowedValues("finance", "risk", "ml"));
```

使用 `TagValueConstraint.anyValue()` 表示不受限制的标签，而
`TagValueConstraint.noValue()` 用于不能携带赋值的标签。

</TabItem>
<TabItem value="python" label="Python">

```python
tag = client.create_tag(
    tag_name="data_domain",
    comment="Business data domain",
    properties={},
    allowed_values=["finance", "risk", "ml"])
```

</TabItem>
</Tabs>

### 列表标签

列表返回名称，或在设置了 `details=true` 时返回完整的标签对象。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/tags

curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/test/tags?details=true"
```

</TabItem>
<TabItem value="java" label="Java">

```java
String[] tagNames = client.listTags();
Tag[] tags = client.listTagsInfo();
```

</TabItem>
<TabItem value="python" label="Python">

```python
tag_names = client.list_tags()
tags = client.list_tags_info()
```

</TabItem>
</Tabs>

### 获取标签

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/tags/pii
```

</TabItem>
<TabItem value="java" label="Java">

```java
Tag tag = client.getTag("pii");
```

</TabItem>
<TabItem value="python" label="Python">

```python
tag = client.get_tag("pii")
```

</TabItem>
</Tabs>

### 修改标签

更改在一个请求中以列表形式应用。

| 更改             | JSON                                                         | Java                                      | Python                                       |
|--------------------|--------------------------------------------------------------|-------------------------------------------|----------------------------------------------|
| 重命名             | `{"@type":"rename","newName":"tag_renamed"}`                 | `TagChange.rename("tag_renamed")`         | `TagChange.rename("tag_renamed")`            |
| 更新备注           | `{"@type":"updateComment","newComment":"new_comment"}`       | `TagChange.updateComment("new_comment")`  | `TagChange.update_comment("new_comment")`    |
| 设置属性           | `{"@type":"setProperty","property":"key1","value":"value1"}` | `TagChange.setProperty("key1", "value1")` | `TagChange.set_property("key1", "value1")`   |
| 移除属性           | `{"@type":"removeProperty","property":"key1"}`               | `TagChange.removeProperty("key1")`        | `TagChange.remove_property("key1")`          |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "updateComment", "newComment": "Reviewed quarterly"},
    {"@type": "setProperty", "property": "owner", "value": "privacy-office"}
  ]
}' http://localhost:8090/api/metalakes/test/tags/pii
```

</TabItem>
<TabItem value="java" label="Java">

```java
Tag tag = client.alterTag(
    "pii",
    TagChange.updateComment("Reviewed quarterly"),
    TagChange.setProperty("owner", "privacy-office"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
tag = client.alter_tag(
    "pii",
    TagChange.update_comment("Reviewed quarterly"),
    TagChange.set_property("owner", "privacy-office"))
```

</TabItem>
</Tabs>

### 删除标签

删除标签也会将其从附加了该标签的每个对象中移除。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/tags/pii
```

</TabItem>
<TabItem value="java" label="Java">

```java
client.deleteTag("pii");
```

</TabItem>
<TabItem value="python" label="Python">

```python
client.delete_tag("pii")
```

</TabItem>
</Tabs>

## 对象操作

### 附加和分离标签

两者均发生在一个请求中，且任一列表均可省略。对象类型和全名位于
路径中，因此同一调用涵盖了目录、模式、表、视图、列、文件集、主题、模型，
和函数。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "tagsToAdd": ["pii"],
  "tagsToRemove": ["unreviewed"]
}' http://localhost:8090/api/metalakes/test/objects/table/catalog1.schema1.customers/tags

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "tagsToAdd": ["pii"]
}' http://localhost:8090/api/metalakes/test/objects/fileset/catalog1.schema1.raw_events/tags
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table customers = ...
customers.supportsTags().associateTags(
    new String[] {"pii"},
    new String[] {"unreviewed"});

Fileset rawEvents = ...
rawEvents.supportsTags().associateTags(new String[] {"pii"}, null);
```

</TabItem>
<TabItem value="python" label="Python">

```python
customers = ...
customers.supports_tags().associate_tags(["pii"], ["unreviewed"])

raw_events = ...
raw_events.supports_tags().associate_tags(["pii"], None)
```

</TabItem>
</Tabs>

### 分配和移除标签值

标签值以标签名称和值的键值对形式进行更新。添加一个键值对会保留该标签的其他
值；删除一个键值对仅移除该值。省略 `value` 以表示没有
值的赋值。REST 操作使用 v2 媒体类型作为请求体。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v2+json" \
  -H "Content-Type: application/vnd.gravitino.v2+json" -d '{
  "tagsToAdd": [
    {"name": "data_domain", "value": "finance"},
    {"name": "data_domain", "value": "risk"},
    {"name": "pii"}
  ],
  "tagsToRemove": [
    {"name": "data_domain", "value": "old"}
  ]
}' http://localhost:8090/api/metalakes/test/objects/table/catalog1.schema1.customers/tags
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table customers = ...
customers.supportsTags().associateTags(
    new TagValue[] {
      TagValue.of("data_domain", "finance"),
      TagValue.of("data_domain", "risk"),
      TagValue.noValue("pii")
    },
    new TagValue[] {TagValue.of("data_domain", "old")});
```

</TabItem>
<TabItem value="python" label="Python">

```python
customers = ...
customers.supports_tags().assign_tags(
    tags_to_add=[
        {"name": "data_domain", "value": "finance"},
        {"name": "data_domain", "value": "risk"},
        {"name": "pii"},
    ],
    tags_to_remove=[{"name": "data_domain", "value": "old"}])
```

</TabItem>
</Tabs>

同一对可以重复添加或删除，而不会改变结果。请求不能添加
同时带值和不带值的同一标签，或在两个列表中包含同一对。要将
带值的赋值转换为不带值的赋值，请移除所有活动值，并在
同一请求中添加不带值的对。移除最后一个值而不添加不带值的对会分离该标签。

### 列出对象上的标签

响应包含从祖先继承的标签。使用 `details=true` 时，每个标签都带有一个
`inherited` 字段及其 `assignmentValues`，而普通的名称列表则没有。一个空的
`assignmentValues` 数组表示该标签在不带值的情况下被分配。`allowedValues` 对于
不受限制的标签为 null，对于仅无值的标签为空，否则包含该标签允许的值。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/test/objects/table/catalog1.schema1.customers/tags?details=true"
```

响应包含每个标签的定义和分配详情：

```json
{
  "code": 0,
  "tags": [
    {
      "name": "data_domain",
      "comment": "Business data domain",
      "properties": {},
      "allowedValues": ["finance", "risk", "ml"],
      "assignmentValues": ["finance", "risk"],
      "inherited": false
    }
  ]
}
```

</TabItem>
<TabItem value="java" label="Java">

```java
Table customers = ...
String[] tagNames = customers.supportsTags().listTags();
Tag[] tags = customers.supportsTags().listTagsInfo();
String[] values =
    tags[0].assignment().map(assignment -> assignment.values()).orElse(new String[0]);
```

</TabItem>
<TabItem value="python" label="Python">

```python
customers = ...
tag_names = customers.supports_tags().list_tags()
tags = customers.supports_tags().list_tags_info()
values = tags[0].assignment_values()
```

</TabItem>
</Tabs>

### 获取对象上的一个标签

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/objects/table/catalog1.schema1.customers/tags/pii
```

</TabItem>
<TabItem value="java" label="Java">

```java
Tag tag = customers.supportsTags().getTag("pii");
```

</TabItem>
<TabItem value="python" label="Python">

```python
tag = customers.supports_tags().get_tag("pii")
```

</TabItem>
</Tabs>

### 列出带有标签的对象

响应仅列出直接附加项，因此附加到目录的标签会返回该目录
而不是其下的对象。传递 `value` 以仅返回包含该
精确、区分大小写的值的直接分配。无值分配不匹配值过滤器。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/test/tags/pii/objects

curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  "http://localhost:8090/api/metalakes/test/tags/data_domain/objects?value=finance"
```

</TabItem>
<TabItem value="java" label="Java">

```java
Tag tag = client.getTag("pii");
MetadataObject[] objects = tag.associatedObjects().objects();
int count = tag.associatedObjects().count();

Tag domain = client.getTag("data_domain");
MetadataObject[] financeObjects = domain.associatedObjects().objects("finance");
```

</TabItem>
<TabItem value="python" label="Python">

```python
tag = client.get_tag("data_domain")
objects = tag.associated_objects().objects()
finance_objects = tag.associated_objects().objects(value="finance")
```

</TabItem>
</Tabs>
