---
sidebar_label: StarRocks
---
## 简介

Apache Gravitino 暴露了一个 [Iceberg REST 目录](../iceberg-rest-service.md) 端点，任何兼容
Iceberg 的引擎都可以直接连接。本页介绍如何配置 StarRocks
以使用 Gravitino 的 Iceberg REST (IRC) 端点。

## 前提条件

- 运行 Apache Gravitino 并启用 Iceberg REST 服务。有关设置说明，请参阅
  [Iceberg REST 目录服务](../iceberg-rest-service.md)。
- StarRocks 环境可访问 Gravitino IRC 端点。默认端口为 `9001`。

## 配置

在 StarRocks 中创建一个指向 Gravitino IRC 端点的外部 Iceberg 目录：

```sql
CREATE EXTERNAL CATALOG iceberg
COMMENT "Gravitino Iceberg REST catalog"
PROPERTIES
(
  "type"                          = "iceberg",
  "iceberg.catalog.type"          = "rest",
  "iceberg.catalog.uri"           = "http://<gravitino-host>:9001/iceberg",
  "aws.s3.access_key"             = "<access-key>",
  "aws.s3.secret_key"             = "<secret-key>",
  "aws.s3.endpoint"               = "http://<s3-host>:9000",
  "aws.s3.enable_path_style_access" = "true",
  "client.factory"                = "com.starrocks.connector.iceberg.IcebergAwsClientFactory"
);
```

:::note
必须显式设置 `client.factory`，StarRocks 才能正确初始化 Iceberg AWS 客户端。
:::

## 示例

```sql
SET CATALOG iceberg;
CREATE DATABASE db;
USE db;
CREATE TABLE t(a int);
INSERT INTO t VALUES (1);
SELECT * FROM t;
```

## Gravitino 连接器与 Iceberg REST 对比

| 特性                      | Gravitino 引擎连接器        | Iceberg REST                  |
|:-------------------------|:----------------------------|:------------------------------|
| 是否需要引擎插件         | 是                          | 否                            |
| Gravitino 访问控制        | 是                          | 是                            |
| 支持的引擎               | Trino, Spark, Flink, Daft   | 任何兼容 Iceberg 的引擎       |
| 凭证分发                 | 视情况而定                  | 是 (S3, GCS, OSS, ADLS)       |

## 相关内容

- [Iceberg REST 目录服务](../iceberg-rest-service.md)
- [通过 Iceberg REST 连接 Spark](./spark.md)
- [通过 Iceberg REST 连接 Trino](./trino.md)

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**免责声明**：
本文件由 AI 翻译服务 [Co-op Translator](https://github.com/Azure/co-op-translator) 翻译完成。尽管我们力求准确，但请注意，自动翻译可能包含错误或不准确之处。原始语言版文件应视为权威来源。对于重要信息，建议使用专业人工翻译。我们对因使用本翻译而产生的任何误解或误释不承担责任。
<!-- CO-OP TRANSLATOR DISCLAIMER END -->