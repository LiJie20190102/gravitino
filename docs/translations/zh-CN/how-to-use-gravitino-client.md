---
title: "Java Client"
slug: "/how-to-use-gravitino-client"
date: 2025-07-09
keyword: "Gravitino client"
license: "This software is licensed under the Apache License version 2."
---

## 简介

在 Spark、Spring 及其他 Java 环境中使用 Gravitino Java 客户端库，或
在 Spark、PyTorch、Tensorflow、Ray 及 Python 环境中使用 Gravitino Python 客户端库。

首先，你必须搭建并运行 Gravitino 服务器，你可以参考文档
[如何安装 Gravitino](./how-to-install.md) 从源代码构建 Gravitino 服务器并
将其安装到本地。

## Java 客户端

通过使用 `withClientConfig` 来自定义 Gravitino Java 客户端，如下所示：

```java
 Map<String, String> properties =
        ImmutableMap.of(
            "gravitino.client.connectionTimeoutMs", "10", 
            "gravitino.client.socketTimeoutMs", "10"
        );

GravitinoClient gravitinoClient = GravitinoClient.builder("http://localhost:8090")
.withMetalake("metalake")
.withClientConfig(properties) // add custom client config (optional)
.builder();

GravitinoAdminClient gravitinoAdminClient = GravitinoAdminClient.builder("http://localhost:8090")
.withClientConfig(properties) // add custom client config (optional)
.builder();
// ...
```

### Java 客户端配置

| 配置项                     | 描述                                          | 默认值       | 必填 |
|----------------------------------------|------------------------------------------------------|---------------------|----------|
| `gravitino.client.connectionTimeoutMs` | 可选的 http 连接超时时间，以毫秒为单位。 | `180000`(3 分钟) | 否       |
| `gravitino.client.socketTimeoutMs`     | 可选的 http socket 超时时间，以毫秒为单位。     | `180000`(3 分钟) | 否       |

**注意：** 无效的配置属性将导致异常。

## Python 客户端

像这样使用配置属性自定义 Gravitino Python 客户端：

```python
gravitino_admin_client = GravitinoAdminClient(
   uri="http://localhost:8090",
   client_config={"gravitino_client_request_timeout": 60},
)
# ...

gravitino_client = GravitinoClient(
   uri="http://localhost:8090",
   metalake_name="test",
   client_config={"gravitino_client_request_timeout": 60},
)
# ...
```

### Python 客户端配置

| 配置项                 | 描述                            | 默认值 | 必填 |
|------------------------------------|----------------------------------------|---------------|----------|
| `gravitino_client_request_timeout` | 可选的客户端超时时间（以秒为单位）。 | `10`          | 否       |

**注意：** 无效的配置属性将导致异常。
