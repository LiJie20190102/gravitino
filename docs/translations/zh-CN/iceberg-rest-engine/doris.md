---
sidebar_label: Doris
---
## 简介

Apache Gravitino 暴露了一个 [Iceberg REST catalog](../iceberg-rest-service.md) 端点，任何
兼容 Iceberg 的引擎都可以直接连接。本文介绍如何配置 Apache Doris
以使用 Gravitino 的 Iceberg REST (IRC) 端点。

## 前提条件

- 运行中的 Apache Gravitino 且已启用 Iceberg REST 服务。参见
  [Iceberg REST catalog service](../iceberg-rest-service.md) 了解设置说明。
- Doris 环境可访问 Gravitino IRC 端点。默认端口为 `9001`。

## 配置

在 Doris 中创建一个指向 Gravitino IRC 端点的 Iceberg catalog：

```sql
CREATE CATALOG iceberg PROPERTIES (
    "uri"                  = "http://<gravitino-host>:9001/iceberg/",
    "type"                 = "iceberg",
    "iceberg.catalog.type" = "rest",
    "s3.endpoint"          = "http://s3.<region>.amazonaws.com",
    "s3.region"            = "<region>",
    "s3.access_key"        = "<access-key>",
    "s3.secret_key"        = "<secret-key>"
);
```

## 示例

```sql
SWITCH iceberg;
CREATE DATABASE db;
USE db;
CREATE TABLE t(a int);
INSERT INTO t VALUES (1);
SELECT * FROM t;
```

## Gravitino Connector 与 Iceberg REST 对比

| 特性                      | Gravitino Engine Connector  | Iceberg REST                  |
|:-------------------------|:----------------------------|:------------------------------|
| 是否需要引擎插件          | 是                          | 否                            |
| Gravitino 访问控制        | 是                          | 是                            |
| 支持的引擎               | Trino, Spark, Flink, Daft   | 任何兼容 Iceberg 的引擎       |
| 凭证分发                 | 视情况而定                  | 是 (S3, GCS, OSS, ADLS)       |

## 相关文档

- [Iceberg REST catalog service](../iceberg-rest-service.md)
- [通过 Iceberg REST 连接 Spark](./spark.md)
- [通过 Iceberg REST 连接 Trino](./trino.md)