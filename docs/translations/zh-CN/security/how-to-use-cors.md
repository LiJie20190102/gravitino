---
title: "CORS"
slug: "/security/how-to-use-cors"
keywords:
  - security
  - cors
license: "This software is licensed under the Apache License version 2."
---

## 概述

跨源资源共享是一种浏览器机制，用于控制哪些 Web 源可以调用 HTTP API。如果页面的源与服务器的主机、端口或协议不同，浏览器会阻止来自该页面的请求，除非服务器另有指示，因此，任何与 Gravitino 分开托管的基于浏览器的客户端都需要启用 CORS 过滤器。

过滤器默认关闭，且仅适用于浏览器。来自引擎、CLI 和其他服务端客户端的请求无论哪种情况均不受影响。

## 配置

Gravitino 服务器和 Iceberg REST 服务各自拥有自己的 CORS 过滤器，在不同的前缀下配置相同的属性名称。Gravitino 服务器使用 `gravitino.server.webserver.`，Iceberg REST 服务使用 `gravitino.iceberg-rest.`，并且仅为需要它的服务进行设置。

| 属性名称           | 描述                                                                                 | 默认值                                 |
|-------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------|
| `enableCorsFilter`      | 启用 CORS 过滤器                                                                     | `false`                                       |
| `allowedOrigins`        | 以逗号分隔的允许访问资源的来源，或使用 `*` 表示所有来源                     | `*`                                           |
| `allowedTimingOrigins`  | 以逗号分隔的允许对资源进行计时的来源。为空表示无                     | (empty)                                       |
| `allowedMethods`        | 访问资源时允许的以逗号分隔的 HTTP 方法                           | `GET,POST,HEAD,DELETE,PUT`                    |
| `allowedHeaders`        | 允许的以逗号分隔的请求头，或使用单个 `*` 接受任何请求头               | `X-Requested-With,Content-Type,Accept,Origin` |
| `exposedHeaders`        | 对客户端可读的以逗号分隔的响应头。为空表示无              | (empty)                                       |
| `preflightMaxAgeInSecs` | 客户端可以缓存预检响应的时间长度                                            | `1800`                                        |
| `allowCredentials`      | 是否允许携带凭据的请求                                           | `true`                                        |
| `chainPreflight`        | 将预检请求作为 `OPTIONS` 请求传递给目标资源，而不是在过滤器中响应它们 | `true`                    |

### 起源与凭证

这两个默认设置无法同时生效。浏览器会拒绝既允许凭证又允许所有来源的响应，因此，将 `allowedOrigins` 保留为 `*` 且 `allowCredentials` 保留为 `true` 意味着即使启用了过滤器，任何经过身份验证的浏览器请求都会失败。

改为列出您的客户端实际使用的来源。通配符来源仅在 `allowCredentials` 为 `false` 时可用，这排除了任何携带令牌或 Cookie 的请求。

### 示例

由 `https://console.example.com` 提供服务的 Web UI 调用其他位置的 Gravitino 服务器时，需要在 `gravitino.conf` 中包含以下内容。

```properties
gravitino.server.webserver.enableCorsFilter = true
gravitino.server.webserver.allowedOrigins = https://console.example.com
gravitino.server.webserver.allowedHeaders = X-Requested-With,Content-Type,Accept,Origin,Authorization
```

之所以添加 `Authorization`，是因为默认标头列表中省略了它，并且发送 bearer token 的浏览器会在其预检请求中指定该标头。
