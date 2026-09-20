---
sidebar_label: Ray
title: 将 Ray 连接到 Iceberg REST
---
## 简介

Apache Gravitino 暴露了一个 [Iceberg REST catalog](../iceberg-rest-service.md) 端点，任何
兼容 Iceberg 的客户端都可以直接连接。本页介绍如何将 Ray Data 与
Gravitino 的 Iceberg REST (IRC) 端点配合使用。

:::note
Ray Data 仅支持对已有 Iceberg 表进行读写操作，不支持
创建、删除或修改表、Schema 或 Catalog 等 DDL 操作。请使用 Spark
或 PyIceberg 管理表元数据。
:::

## 前置条件

- Apache Gravitino 已启动并启用 Iceberg REST 服务。参见
  [Iceberg REST catalog 服务](../iceberg-rest-service.md) 了解配置说明。
- Gravitino IRC 端点可从 Python 环境访问。默认端口为 `9001`。
- 已安装 Ray：`pip install ray[data]`

## 配置

Ray Data 通过直接传递给读写函数的 `catalog_kwargs` 连接到 Gravitino IRC 端点，
无需单独注册 Catalog。

### 无认证

```python
catalog_kwargs = {
    "name": "default",
    "type": "rest",
    "uri": "http://<gravitino-host>:9001/iceberg/",
}
```

### 使用 Basic 认证的凭证分发

如果 Gravitino 使用 [本地用户和用户组](../security/local-users-and-groups.md) 进行 Basic
认证，则在 catalog 参数中传递凭证：

```python
catalog_kwargs = {
    "name": "default",
    "type": "rest",
    "uri": "http://<gravitino-host>:9001/iceberg/",
    "header.X-Iceberg-Access-Delegation": "vended-credentials",
    "auth": {
        "type": "basic",
        "basic": {"username": "<user>", "password": "<password>"}
    }
}
```

参见 [如何进行认证](../security/how-to-authenticate.md) 了解 Gravitino 认证
配置选项。

## 示例

### 写入 Iceberg 表

```python
import ray
import pandas as pd

docs = [{"id": i, "data": f"Doc {i}"} for i in range(4)]
ds = ray.data.from_pandas(pd.DataFrame(docs))
ds.write_iceberg(
    table_identifier="default.sample",
    catalog_kwargs=catalog_kwargs
)
```

### 读取 Iceberg 表

```python
import ray

ds = ray.data.read_iceberg(
    table_identifier="default.sample",
    catalog_kwargs=catalog_kwargs
)
ds.show(limit=1)
```

## Gravitino 连接器与 Iceberg REST 对比

| 特性                      | Gravitino 引擎连接器        | Iceberg REST                  |
|:-------------------------|:----------------------------|:------------------------------|
| 需要引擎插件             | 是                          | 否                            |
| Gravitino 访问控制        | 是                          | 是                            |
| 支持的引擎                | Trino、Spark、Flink、Daft   | 任何兼容 Iceberg 的引擎       |
| 凭证分发                  | 视情况而定                  | 是（S3、GCS、OSS、ADLS）      |

## 相关文档

- [Iceberg REST catalog 服务](../iceberg-rest-service.md)
- [通过 Iceberg REST 连接 PyIceberg](./pyiceberg.md)
- [通过 Iceberg REST 连接 Spark](./spark.md)