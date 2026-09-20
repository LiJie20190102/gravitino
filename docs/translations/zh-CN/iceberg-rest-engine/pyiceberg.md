---
sidebar_label: PyIceberg
title: 将 PyIceberg 连接到 Iceberg REST
---
## 简介

Apache Gravitino 暴露了一个 [Iceberg REST catalog](../iceberg-rest-service.md) 端点，任何
兼容 Iceberg 的客户端都可以直接连接。本页介绍如何将 PyIceberg 与
Gravitino 的 Iceberg REST (IRC) 端点配合使用。

## 前置条件

- Apache Gravitino 已启动并开启 Iceberg REST 服务。参见
  [Iceberg REST catalog service](../iceberg-rest-service.md) 获取配置说明。
- Gravitino IRC 端点可从 Python 环境访问。默认端口为 `9001`。
- 已安装 PyIceberg：`pip install pyiceberg`

## 配置

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "gravitino_irc",
    **{
        "type": "rest",
        "uri":  "http://<gravitino-host>:9001/iceberg",
    }
)
```

### 凭证分发 (Credential Vending)

```python
catalog = load_catalog(
    "gravitino_irc",
    **{
        "type":                            "rest",
        "uri":                             "http://<gravitino-host>:9001/iceberg",
        "header.X-Iceberg-Access-Delegation": "vended-credentials",
    }
)
```

### OAuth2 认证

```python
catalog = load_catalog(
    "gravitino_irc",
    **{
        "type":  "rest",
        "uri":   "http://<gravitino-host>:9001/iceberg",
        "token": "<your-token>",
    }
)
```

参见 [How to authenticate](../security/how-to-authenticate.md) 了解 Gravitino 认证
配置选项。

## 示例

### 列出命名空间 (Namespace)

```python
catalog.list_namespaces()
```

### 加载表

```python
table = catalog.load_table("db.table")
print(table.schema())
```

### 扫描表

```python
df = table.scan().to_arrow()
print(df)
```

### 创建命名空间和表

```python
catalog.create_namespace("db")

from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, StringType

schema = Schema(
    NestedField(1, "id",   LongType(),   required=True),
    NestedField(2, "name", StringType(), required=False),
)
catalog.create_table("db.new_table", schema=schema)
```

## Gravitino 连接器 vs. Iceberg REST

| 特性                  | Gravitino 引擎连接器      | Iceberg REST                  |
|:-------------------------|:----------------------------|:------------------------------|
| 是否需要引擎插件      | 是                        | 否                            |
| Gravitino 访问控制    | 是                        | 是                            |
| 支持的引擎            | Trino, Spark, Flink, Daft   | 任何兼容 Iceberg 的引擎       |
| 凭证分发              | 视情况而定                  | 是 (S3, GCS, OSS, ADLS)      |

## 相关链接

- [Iceberg REST catalog 服务](../iceberg-rest-service.md)
- [通过 Iceberg REST 连接 Spark](./spark.md)
- [通过 Iceberg REST 连接 Flink](./flink.md)