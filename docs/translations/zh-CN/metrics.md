---
title: "Metrics"
slug: "/metrics"
keywords:
  - metrics
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino 指标构建于 [Dropwizard Metrics](https://metrics.dropwizard.io/) 之上。它通过 JMX 和 HTTP 服务器导出这些指标，支持 JSON 和 Prometheus 格式。通过 HTTP 请求检索它们，如下所示：

```shell
// Use Gravitino Server address or Iceberg REST server address to replace 127.0.0.1:8090
// Get metrics in JSON format
curl http://127.0.0.1:8090/metrics
// Get metrics in Prometheus format
curl http://127.0.0.1:8090/prometheus/metrics
```

### 指标来源

#### HTTP 服务器指标

HTTP 服务器指标包含 HTTP 请求处理时间的直方图以及 HTTP 响应码的数量，按不同的 HTTP 接口（例如 `create-table` 和 `load-table`）进行分类。

例如，你可以按如下方式获取 Gravitino 服务器中 `create-table` 操作的 Prometheus 指标：

```text
gravitino_server_1xx_responses_total{operation="create-table",} 0.0
gravitino_server_4xx_responses_total{operation="create-table",} 0.0
gravitino_server_5xx_responses_total{operation="create-table",} 0.0
gravitino_server_2xx_responses_total{operation="create-table",} 0.0
gravitino_server_3xx_responses_total{operation="create-table",} 0.0
gravitino_server_http_request_duration_seconds_count{operation="create-table",} 0.0
gravitino_server_http_request_duration_seconds{operation="create-table",quantile="0.5",} 0.0
gravitino_server_http_request_duration_seconds{operation="create-table",quantile="0.75",} 0.0
gravitino_server_http_request_duration_seconds{operation="create-table",quantile="0.95",} 0.0
gravitino_server_http_request_duration_seconds{operation="create-table",quantile="0.98",} 0.0
gravitino_server_http_request_duration_seconds{operation="create-table",quantile="0.99",} 0.0
gravitino_server_http_request_duration_seconds{operation="create-table",quantile="0.999",} 0.0
```

:::info
带有 `gravitino-server` 前缀的指标与 Gravitino 服务器相关，而带有 `iceberg-rest-server` 前缀的指标用于 Gravitino Iceberg REST 服务器。
:::

#### JVM 指标

JVM 指标源使用 [JVM instrumentation](https://metrics.dropwizard.io/4.2.0/manual/jvm.html)，包含 BufferPoolMetricSet、GarbageCollectorMetricSet 和 MemoryUsageGaugeSet。
这些指标以 `jvm` 前缀开头，例如 JSON 格式中的 `jvm.heap.used`，以及 Prometheus 格式中的 `jvm_heap_used`。

#### 目录指标

Catalog 指标提供来自不同 catalog 实例的指标。
在 Prometheus 格式中，所有 catalog 指标都以 `gravitino-catalog` 前缀开头，并带有 `provider`、`metalake` 和 `catalog` 标签，以区分不同的 catalog 实例。

Catalog 指标仅支持 Fileset catalog 和 JDBC catalog。

按如下方式获取 Gravitino 服务器中名为 `test_metalake` 的 metalake 下名为 `test_catalog` 的 Fileset catalog 的 Prometheus 指标：

```text
gravitino_catalog_filesystem_cache_hits{provider="fileset",metalake="test_metalake",catalog="test_catalog",} 0.0
gravitino_catalog_filesystem_cache_misses{provider="fileset",metalake="test_metalake",catalog="test_catalog",} 0.0
```

获取 Gravitino 服务器中名为 `test_metalake` 的 metalake 下名为 `test_catalog` 的 JDBC catalog 的 Prometheus 指标，如下：

```text
gravitino_catalog_datasource_idle_connections{provider="jdbc",metalake="test_metalake",catalog="test_catalog",} 1.0
gravitino_catalog_datasource_active_connections{provider="jdbc",metalake="test_metalake",catalog="test_catalog",} 0.0
gravitino_catalog_datasource_max_connections{provider="jdbc",metalake="test_metalake",catalog="test_catalog",} 10.0
```
