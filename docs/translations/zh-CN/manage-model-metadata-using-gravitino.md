---
title: "Manage Model Metadata"
slug: "/manage-model-metadata-using-gravitino"
keyword: "model management, model version, alias, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页面介绍用于模型和模型版本的 Gravitino API。关于什么是模型目录、
版本和别名如何工作，以及一个版本上的多个 URI 的行为方式，请参见
[Model Catalog](./model-catalog.md)。关于创建模型所在的目录和模式，请参见
[Manage Catalogs and Schemas](./manage-catalogs-and-schemas.md)。

## 模型运维

### 注册模型

注册会创建不含版本的模型。它需要一个名称，并且可以带有注释和
属性。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "churn_predictor",
  "comment": "Customer churn model",
  "properties": {"team": "risk"}
}' http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("models");
ModelCatalog models = catalog.asModelCatalog();

Model model = models.registerModel(
    NameIdentifier.of("customer", "churn_predictor"),
    "Customer churn model",
    ImmutableMap.of("team", "risk"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog = client.load_catalog("models")
models = catalog.as_model_catalog()

model = models.register_model(
    model_ident=NameIdentifier.of("customer", "churn_predictor"),
    comment="Customer churn model",
    properties={"team": "risk"})
```

</TabItem>
</Tabs>

### 获取模型

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor
```

</TabItem>
<TabItem value="java" label="Java">

```java
Model model = models.getModel(NameIdentifier.of("customer", "churn_predictor"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
model = models.get_model(NameIdentifier.of("customer", "churn_predictor"))
```

</TabItem>
</Tabs>

### 修改模型

| 更改             | JSON                                                         | Java                                        |
|--------------------|--------------------------------------------------------------|---------------------------------------------|
| 重命名             | `{"@type":"rename","newName":"churn_v2"}`                    | `ModelChange.rename("churn_v2")`            |
| 更新注释 | `{"@type":"updateComment","newComment":"new_comment"}`       | `ModelChange.updateComment("new_comment")`  |
| 设置属性     | `{"@type":"setProperty","property":"key1","value":"value1"}` | `ModelChange.setProperty("key1", "value1")` |
| 移除属性  | `{"@type":"removeProperty","property":"key1"}`               | `ModelChange.removeProperty("key1")`        |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "setProperty", "property": "default-uri-name", "value": "us"}
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor
```

</TabItem>
<TabItem value="java" label="Java">

```java
Model model = models.alterModel(
    NameIdentifier.of("customer", "churn_predictor"),
    ModelChange.setProperty("default-uri-name", "us"));
```

</TabItem>
</Tabs>

### 列出和删除模型

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models

curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor
```

</TabItem>
<TabItem value="java" label="Java">

```java
NameIdentifier[] identifiers = models.listModels(Namespace.of("customer"));
boolean deleted = models.deleteModel(NameIdentifier.of("customer", "churn_predictor"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
identifiers = models.list_models(Namespace.of("customer"))
deleted = models.delete_model(NameIdentifier.of("customer", "churn_predictor"))
```

</TabItem>
</Tabs>

删除模型会删除其所有版本。

## 模型版本操作

### 链接一个版本

链接会创建现有模型的一个版本。版本号按顺序分配，从
零开始。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "uri": "s3a://models/churn/v0",
  "aliases": ["production"],
  "comment": "First release",
  "properties": {"framework": "xgboost"}
}' http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/versions
```

</TabItem>
<TabItem value="java" label="Java">

```java
models.linkModelVersion(
    NameIdentifier.of("customer", "churn_predictor"),
    "s3a://models/churn/v0",
    new String[] {"production"},
    "First release",
    ImmutableMap.of("framework", "xgboost"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
models.link_model_version(
    model_ident=NameIdentifier.of("customer", "churn_predictor"),
    uri="s3a://models/churn/v0",
    aliases=["production"],
    comment="First release",
    properties={"framework": "xgboost"})
```

</TabItem>
</Tabs>

要为一个版本提供多个命名的 URI，请将 `uris` 作为 map 而不是单个 `uri` 发送，并设置
`default-uri-name` 来选择当调用方未指定名称时返回的 URI。在 Java 中，相同的
`linkModelVersion` 接受一个 map；在 Python 中为 `link_model_version_with_multiple_uris`。

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "uris": {
    "us": "s3a://models-us/churn/v0",
    "eu": "s3a://models-eu/churn/v0"
  },
  "aliases": ["production"],
  "properties": {"default-uri-name": "us"}
}' http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/versions
```

### 获取版本

版本通过编号或别名获取，并且其 URI 可以直接获取。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/versions/0

curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/aliases/production

curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/aliases/production/uri
```

</TabItem>
<TabItem value="java" label="Java">

```java
ModelVersion byNumber = models.getModelVersion(
    NameIdentifier.of("customer", "churn_predictor"), 0);

ModelVersion byAlias = models.getModelVersion(
    NameIdentifier.of("customer", "churn_predictor"), "production");
```

</TabItem>
<TabItem value="python" label="Python">

```python
by_number = models.get_model_version(
    NameIdentifier.of("customer", "churn_predictor"), 0)

by_alias = models.get_model_version_by_alias(
    NameIdentifier.of("customer", "churn_predictor"), "production")
```

</TabItem>
</Tabs>

### 修改版本

别名通过 `updateAliases` 在版本之间移动，它会在一次调用中完成添加和删除。URI 被
按名称添加、更新和删除。

| 更改             | JSON                                                                        | Java                                                       |
|--------------------|-----------------------------------------------------------------------------|------------------------------------------------------------|
| 更新评论 | `{"@type":"updateComment","newComment":"new_comment"}`                      | `ModelVersionChange.updateComment("new_comment")`          |
| 设置属性     | `{"@type":"setProperty","property":"key1","value":"value1"}`                | `ModelVersionChange.setProperty("key1", "value1")`         |
| 移除属性  | `{"@type":"removeProperty","property":"key1"}`                              | `ModelVersionChange.removeProperty("key1")`                |
| 更新 URI     | `{"@type":"updateUri","newUri":"s3a://models/churn/v1"}`                    | `ModelVersionChange.updateUri(...)`                        |
| 添加命名 URI    | `{"@type":"addUri","uriName":"eu","uri":"s3a://models-eu/churn/v0"}`        | `ModelVersionChange.addUri("eu", ...)`                     |
| 移除命名 URI | `{"@type":"removeUri","uriName":"eu"}`                                      | `ModelVersionChange.removeUri("eu")`                       |
| 移动别名       | `{"@type":"updateAliases","aliasesToAdd":["production"],"aliasesToRemove":[]}` | `ModelVersionChange.updateAliases(...)`                  |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "updateAliases", "aliasesToAdd": ["production"], "aliasesToRemove": []}
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/versions/1
```

</TabItem>
<TabItem value="java" label="Java">

```java
models.alterModelVersion(
    NameIdentifier.of("customer", "churn_predictor"),
    1,
    ModelVersionChange.updateAliases(new String[] {"production"}, new String[] {}));
```

</TabItem>
</Tabs>

将别名移动到新版本会将其从原先持有它的版本中移除，因为别名属于
一次只能属于一个版本。

### 列出和删除版本

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/versions

curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/models/schemas/customer/models/churn_predictor/versions/0
```

</TabItem>
<TabItem value="java" label="Java">

```java
int[] versions = models.listModelVersions(
    NameIdentifier.of("customer", "churn_predictor"));

boolean deleted = models.deleteModelVersion(
    NameIdentifier.of("customer", "churn_predictor"), 0);
```

</TabItem>
<TabItem value="python" label="Python">

```python
versions = models.list_model_versions(
    NameIdentifier.of("customer", "churn_predictor"))

deleted = models.delete_model_version(
    NameIdentifier.of("customer", "churn_predictor"), 0)
```

</TabItem>
</Tabs>
