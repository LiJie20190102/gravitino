---
title: "Manage User-Defined Functions"
slug: "/manage-user-defined-function-using-gravitino"
keyword: "function management, UDF, user-defined function, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## 简介

本页介绍用于函数的 Gravitino API。关于什么是函数、函数类型、
确定性以及定义和实现如何关联，请参见 [Functions](./functions.md)。关于
创建函数所在的 catalog 和 schema，请参见
[Manage Catalogs and Schemas](./manage-catalogs-and-schemas.md)。

:::note
注册函数会将其元数据存储在 Gravitino 中；引擎是否能够调用它取决于
引擎的连接器。Trino 连接器仅公开语言为 `SQL` 且
运行时为 `TRINO` 的实现；Python 和 Java 实现，以及任何具有其他运行时的实现，都
在 Gravitino 中进行管理，但在 Trino 中不可见或不可调用。参见
[Trino 连接器 UDF 支持](./trino-connector/udf-support.md)。
:::

## 函数运算

### 注册 SQL 函数

一个函数需要一个名称、一个类型、一个确定性标志，以及至少一个定义。一个定义
包含其参数、其返回类型，以及一个或多个实现。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "add_one",
  "functionType": "SCALAR",
  "deterministic": true,
  "comment": "Adds one to the input",
  "definitions": [
    {
      "parameters": [{"name": "x", "dataType": "integer"}],
      "returnType": "integer",
      "impls": [
        {"language": "SQL", "runtime": "TRINO", "sql": "x + 1"}
      ]
    }
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions
```

</TabItem>
<TabItem value="java" label="Java">

```java
Catalog catalog = client.loadCatalog("sales");
FunctionCatalog functions = catalog.asFunctionCatalog();

FunctionImpl sqlImpl = FunctionImpls.ofSql(FunctionImpl.RuntimeType.TRINO, "x + 1");

FunctionDefinition definition = FunctionDefinitions.of(
    new FunctionParam[] {FunctionParams.of("x", Types.IntegerType.get())},
    Types.IntegerType.get(),
    new FunctionImpl[] {sqlImpl});

Function function = functions.registerFunction(
    NameIdentifier.of("public", "add_one"),
    "Adds one to the input",
    FunctionType.SCALAR,
    true,
    new FunctionDefinition[] {definition});
```

</TabItem>
<TabItem value="python" label="Python">

```python
catalog = client.load_catalog("sales")
functions = catalog.as_function_catalog()

sql_impl = (
    SQLImpl.builder()
    .with_runtime_type(SQLImpl.RuntimeType.TRINO)
    .with_sql("x + 1")
    .build()
)

definition = FunctionDefinitions.of(
    [FunctionParams.of("x", Types.IntegerType.get())],
    Types.IntegerType.get(),
    [sql_impl])

function = functions.register_function(
    ident=NameIdentifier.of("public", "add_one"),
    comment="Adds one to the input",
    function_type=FunctionType.SCALAR,
    deterministic=True,
    definitions=[definition])
```

</TabItem>
</Tabs>

### 注册 Python 函数

一个 Python 实现会命名一个 handler 入口点，并且可以携带内联代码和这些包，这些
运行时所需的。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "normalize_phone",
  "functionType": "SCALAR",
  "deterministic": true,
  "comment": "Strips formatting from a phone number",
  "definitions": [
    {
      "parameters": [{"name": "raw", "dataType": "varchar(64)"}],
      "returnType": "varchar(64)",
      "impls": [
        {
          "language": "PYTHON",
          "runtime": "SPARK",
          "handler": "normalize.main",
          "codeBlock": "def main(raw):\n    return \"\".join(c for c in raw if c.isdigit())"
        }
      ]
    }
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions
```

</TabItem>
</Tabs>

### 注册 Java 函数

Java 实现会命名一个类，通常也会命名包含它的 jar 包。表值函数
声明 `returnColumns` 而不是单个 `returnType`。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "generate_series",
  "functionType": "TABLE",
  "deterministic": true,
  "comment": "Generates a range of integers",
  "definitions": [
    {
      "parameters": [
        {"name": "start_val", "dataType": "integer"},
        {"name": "end_val", "dataType": "integer"}
      ],
      "returnColumns": [
        {"name": "value", "dataType": "integer", "comment": "The generated value"}
      ],
      "impls": [
        {
          "language": "JAVA",
          "runtime": "SPARK",
          "className": "com.example.GenerateSeriesFunction",
          "resources": {"jars": ["hdfs:///path/to/udtf.jar"]}
        }
      ]
    }
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions
```

</TabItem>
</Tabs>

### 注册重载

具有多个定义的函数在一个名称下接受多个参数列表。每个定义
带有其自身的返回类型和实现。

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "name": "add",
  "functionType": "SCALAR",
  "deterministic": true,
  "comment": "Adds two or three integers",
  "definitions": [
    {
      "parameters": [
        {"name": "x", "dataType": "integer"},
        {"name": "y", "dataType": "integer"}
      ],
      "returnType": "integer",
      "impls": [{"language": "SQL", "runtime": "TRINO", "sql": "x + y"}]
    },
    {
      "parameters": [
        {"name": "x", "dataType": "integer"},
        {"name": "y", "dataType": "integer"},
        {"name": "z", "dataType": "integer"}
      ],
      "returnType": "integer",
      "impls": [{"language": "SQL", "runtime": "TRINO", "sql": "x + y + z"}]
    }
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions
```

</TabItem>
</Tabs>

### 获取函数

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions/add_one
```

</TabItem>
<TabItem value="java" label="Java">

```java
Function function = functions.getFunction(NameIdentifier.of("public", "add_one"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
function = functions.get_function(NameIdentifier.of("public", "add_one"))
```

</TabItem>
</Tabs>

### 列表函数

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X GET -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions
```

</TabItem>
<TabItem value="java" label="Java">

```java
NameIdentifier[] identifiers = functions.listFunctions(Namespace.of("public"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
identifiers = functions.list_functions(Namespace.of("public"))
```

</TabItem>
</Tabs>

### 修改函数

更改在一个请求中以列表形式应用。

| 更改             | JSON                                                         | Java                                             |
|--------------------|--------------------------------------------------------------|--------------------------------------------------|
| 重命名             | `{"@type":"rename","newName":"add_one_v2"}`                  | `FunctionChange.rename("add_one_v2")`            |
| 更新注释 | `{"@type":"updateComment","newComment":"new_comment"}`       | `FunctionChange.updateComment("new_comment")`    |
| 设置属性     | `{"@type":"setProperty","property":"key1","value":"value1"}` | `FunctionChange.setProperty("key1", "value1")`   |
| 移除属性  | `{"@type":"removeProperty","property":"key1"}`               | `FunctionChange.removeProperty("key1")`          |

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X PUT -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" -d '{
  "updates": [
    {"@type": "updateComment", "newComment": "Adds one, reviewed"}
  ]
}' http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions/add_one
```

</TabItem>
<TabItem value="java" label="Java">

```java
Function function = functions.alterFunction(
    NameIdentifier.of("public", "add_one"),
    FunctionChange.updateComment("Adds one, reviewed"));
```

</TabItem>
</Tabs>

### 删除函数

<Tabs groupId='language' queryString>
<TabItem value="shell" label="REST">

```shell
curl -X DELETE -H "Accept: application/vnd.gravitino.v1+json" \
  http://localhost:8090/api/metalakes/example/catalogs/sales/schemas/public/functions/add_one
```

</TabItem>
<TabItem value="java" label="Java">

```java
boolean dropped = functions.dropFunction(NameIdentifier.of("public", "add_one"));
```

</TabItem>
<TabItem value="python" label="Python">

```python
dropped = functions.drop_function(NameIdentifier.of("public", "add_one"))
```

</TabItem>
</Tabs>
