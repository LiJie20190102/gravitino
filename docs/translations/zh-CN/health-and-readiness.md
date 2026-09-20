---
title: "Health and readiness"
slug: /health-and-readiness
keywords:
  - health
  - readiness
  - liveness
  - monitoring
license: "This software is licensed under the Apache License version 2."
---

Gravitino 暴露了独立的存活和就绪端点，以便调用者能够区分“重启此
进程”和“将流量发送到其他地方”。存活检查会检查服务器是否能够响应
并且没有观察到内存溢出错误。就绪检查还会检查它是否能够到达实体
存储。

端点遵循 MicroProfile Health 语义。健康的检查返回 200，而不健康的检查
返回 503，两者都带有 JSON 主体，指明了所运行的各个检查的名称。

## 快速开始

**1. 检查存活状态。** 当 HTTP 线程能够响应且没有内存溢出错误
被观察到时，此操作返回 200。

```shell
GRAVITINO_URL=http://localhost:8090

curl -i "${GRAVITINO_URL}/api/health/live"
```

**2. 检查就绪状态。** 此操作返回 200，仅当实体存储响应且未观察到内存不足
错误。

```shell
curl -i "${GRAVITINO_URL}/api/health/ready"
```

**3. 同时检查两者。** 聚合端点同时运行存活性和就绪性检查
如果其中任何一个失败，则报告 503。

```shell
curl -i "${GRAVITINO_URL}/api/health"
```

## 端点

| 路径                | 检查                                  | 返回 503 的情况                                                    |
|---------------------|-----------------------------------------|---------------------------------------------------------------------|
| `/api/health/live`  | HTTP 服务器和 OOM 状态               | 观察到内存溢出错误                                 |
| `/api/health/ready` | 实体存储和 OOM 状态              | 观察到内存溢出错误或实体存储检查失败 |
| `/api/health`       | HTTP 服务器、实体存储和 OOM 状态 | 任何检查失败                                                     |

每个路径也都在服务器的根目录下提供服务，不带 `/api` 前缀，供负载均衡器
和需要在知名位置进行探测的流量管理器使用。根别名是 `/health`、
`/health/live`、`/health/ready` 和 `/health.html`，其中最后一个映射到聚合
端点，而不是其自身的检查。

响应体携带一个总体状态和单个检查的列表。每个检查都有一个名称，
`up` 或 `down` 的状态，以及一个解释故障的详细信息映射。在 Gravitino 服务器上，这两个
常规检查名称为 `httpServer` 和 `entityStore`。在观察到内存溢出错误后，所有
三个端点转而报告下文描述的 `jvm` 故障。

## 内存不足失败

Metaspace 或堆 `OutOfMemoryError` 可能会让已加载的端点继续成功响应
而其他操作失败。因此，成功的 HTTP 响应或实体存储查找并不能
证明在 OOM 之后已恢复。

Gravitino、Iceberg REST 和 Lance REST 服务器记录由其 Jersey 异常
监听器、错误映射器以及安装在其他过滤器和 servlet 之前的 servlet 过滤器所观察到的 OOM。
身份验证错误处理和请求执行/错误响应辅助程序（包括内置的
IdP 辅助程序）也会记录它们处理的错误。主服务器还会记录健康探测
任务中的失败。Jetty worker 未捕获异常处理程序是一个额外的后备机制，而不是请求
异常边界。
包装的原因也会被检查。一旦记录，受影响服务的健康端点和根
别名会返回 HTTP 503。Gravitino 和 Lance REST 将状态值序列化为 `up`/`down`；
Iceberg REST 使用 `UP`/`DOWN`。以下主体展示了 Gravitino 和 Lance REST 的格式
（主服务器使用 `/api/health` 前缀）；Iceberg REST 对两个状态字段都使用 `"DOWN"`：

```json
{
  "code": 0,
  "status": "down",
  "checks": [
    {
      "name": "jvm",
      "status": "down",
      "details": { "reason": "OutOfMemoryError; restart required" }
    }
  ]
}
```

此状态将持续到进程重启，即使后续的普通 API 请求成功。健康
检查在记录 OOM 后会跳过实体存储探测。数据库故障、普通 HTTP 500、
`StackOverflowError` 或缺少连接器类单独不会设置此状态。

此策略也适用于由单个请求引起的 OOM，例如过大的列表响应
或 `Requested array size exceeds VM limit`。服务器不区分可恢复的分配
失败与持续性内存耗尽：即使内存再次可用，健康
状态在重启前仍为不健康。如果存活探针触发了自动重启，重复
针对不同副本重试相同的过大请求会导致这些副本重启
连续地。在配置请求限制和重试策略时，请考虑到这一行为。

检测涵盖到达这些服务器边界的错误；它无法检测到被
连接器或无关的后台执行器完全吞没的 OOM。这不是 JVM 范围的 OOM 捕获。如果
JVM 无法分配足够的内存来响应探测，探测可能会失败且没有 JSON 响应。
仅检查可抛出对象本身及其原因链。仅存在于被抑制的
异常（例如，来自资源清理）中的 OOM 不会被检测到，从而避免在检查故障时
进行防御性数组拷贝。

当 Iceberg REST 和 Lance REST 嵌入在主服务器中运行时，默认的辅助
类加载器共享同一个 `ServerHealth` 标记。这些服务中任何一个记录的 OOM 都会使
其所有的健康端点都报告为不健康。在独立 JVM 进程中运行的服务会独立跟踪
OOM。

## 就绪状态实际测试的内容

实体存储检查会对名为 `gravitino_health_probe` 的 metalake 发出存在性查找。
该名称是一个哨兵值，预期并不存在。重要的是存储是否响应，而不是
响应了什么，因此一个可达的存储会报告 UP，即使查找未找到任何内容。

查找操作在一个小型专用线程池上运行，而不是在请求线程上，因此一个
已停止响应的存储无法占用 HTTP 线程。该池持有一个核心线程，可增长到四个，
并最多排队二十个探测任务，然后再拒绝后续的探测。

## Iceberg REST 和 Lance REST 端点

Iceberg REST 服务和 Lance REST 服务各自在它们自己的
端口上运行自己的 HTTP 服务器，包括当它们在 Gravitino 服务器进程内运行时。嵌入式服务共享
OOM 标记，但 HTTP 可用性和初始化检查仍特定于每个服务。
因此，运行其中任一服务的部署也需要针对其端口进行探测。

在观察到 OOM 之后，两个服务从所有健康端点和根别名返回 503，并伴随
上述 `jvm` 故障，直到重启。在 OOM 之前，它们现有的初始化检查适用。

| 服务器               | 默认端口 | 健康路径前缀 | 就绪检查         |
|----------------------|--------------|--------------------|-------------------------|
| Gravitino 服务器     | `8090`       | `/api/health`      | `entityStore`           |
| Iceberg REST 服务 | `9001`       | `/iceberg/health`  | `catalogWrapperManager` |
| Lance REST 服务   | `9101`       | `/lance/health`    | `namespaceWrapper`      |

每个前缀为其下的 `/live` 和 `/ready` 提供服务，并在该前缀本身进行聚合检查。
这三个服务器中的每一个还提供根别名 `/health`、`/health/live`、`/health/ready`，
以及位于其各自端口上的 `/health.html`。

这两个 REST 服务的就绪检查回答的问题比针对 Gravitino 的就绪检查更狭窄，
服务器，并且这两个服务都不会超出其自身进程去测试其背后的元数据。
Iceberg REST 服务在其 catalog wrapper manager 存在后即报告 UP，这发生在
启动期间，因此该检查确认的是服务已经启动，而不是 catalog 可达。
Lance REST 服务在其 namespace wrapper 初始化后即报告 UP，并且该
初始化会推迟到第一次 namespace 或 table 请求时。

延迟初始化使得 `/lance/health/ready` 不适合作为 Kubernetes 就绪探针，如果单独
使用。失败的就绪探针会将 pod 排除在 Service 之外，因此没有命名空间或表
请求到达服务器，包装器永远不会初始化，pod 也永远不会就绪。探测
`/lance/health/live` 上的 Lance REST 服务，并将就绪探针留在执行
命名空间操作的请求路径上。

`gravitino.server.health.entityStore.probeTimeoutMs` 仅适用于 Gravitino 服务器。两者均不
REST 服务发起后端探测，因此两者都没有可调整的超时时间。

## 配置

| 属性                                             | 描述                                  | 默认值 |
|------------------------------------------------------|----------------------------------------------|---------|
| `gravitino.server.health.entityStore.probeTimeoutMs` | 实体存储就绪探针的超时时间 | `2000`  |

将此值设置为高于存储的最坏情况延迟，而不是其典型延迟。一个探针如果
超时会被取消并报告为 DOWN，这会将服务器移出轮换，因此一个
调整得过于紧凑的值会将缓慢的后端变成服务中断。

## 失败原因

DOWN 实体存储检查在其详细信息中指明了原因。

| 原因                         | 含义                                                         |
|--------------------------------|-----------------------------------------------------------------|
| `entity store not initialized` | 服务器仍在启动中，存储尚不可用 |
| `timeout`                      | 探测超过了配置的超时时间并被取消     |
| `probe-rejected`               | 探测队列已满，探测从未运行            |
| `interrupted`                  | 探测线程被中断                                |
| 异常类名称        | 存储引发了该异常                                 |

持续不断的 `probe-rejected` 意味着探测流量超过了存储的处理速度，而不是指任何
单个探测失败，因此它通常指向激进的探测间隔或性能下降的后端
而不是配置错误。

## 身份验证与审计

健康路径绕过身份验证，因此探针不需要凭据，并且在
服务器上启用身份验证时不会中断。它们也被排除在审计日志之外，因此探针流量
不会填满审计日志。

这两种行为都涵盖了根别名以及规范路径，因为转发的请求
仍然报告其原始 URI，并且两者在所有三台服务器上都适用，因此 Iceberg REST 和 Lance
REST 健康检查路径在它们各自的端口上也被豁免。

## Kubernetes 探针

Gravitino chart 的默认存活和就绪探针均以 `/` 为目标，而不是健康
端点，因此开箱即用的安装不使用本页所述的检查。探针
针对 `/` 仅确认 HTTP 监听器正在接受连接，这意味着一个 pod，其
实体存储已失败，仍报告就绪并仍接收流量。

将探针指向 values 文件中的健康端点。

```yaml
livenessProbe:
  httpGet:
    path: /api/health/live
    port: http
  initialDelaySeconds: 20
  timeoutSeconds: 5

readinessProbe:
  httpGet:
    path: /api/health/ready
    port: http
  initialDelaySeconds: 20
  timeoutSeconds: 5
```

请将就绪超时保持在实体存储探测超时之上，以便 Kubernetes 等待
服务器自身的响应，而不是先超时并丢失失败的原因。

Liveness 应保留在 liveness 端点上，而不是 readiness 或聚合端点。将
liveness 指向包含实体存储的检查意味着数据库宕机会重启每个 pod，这
会移除那些在存储恢复时本可恢复的服务器。

Iceberg REST 和 Lance REST charts 默认将其探针指向请求路径而不是 `/`，因此
这些探针不携带凭据，一旦启用身份验证就会失败。将 Iceberg REST
探针指向 `/iceberg/health/live` 和 `/iceberg/health/ready`，这两个路径免于身份验证。
将 Lance REST 的 liveness probe 指向 `/lance/health/live`，并将其 readiness probe 保留在
请求路径上，这是出于上文所述的初始化原因。
