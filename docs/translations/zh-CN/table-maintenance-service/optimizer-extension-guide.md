---
title: "Extension Guide"
slug: "/table-maintenance-service/extension-guide"
keywords:
  - table maintenance
license: "This software is licensed under the Apache License version 2."
---

## 简介

当内置组件与您的环境不匹配且您需要自定义实现时，请使用本指南。

## 扩展模型

该服务支持三种加载模式：

1. `Provider` SPI (`name()` + `initialize()`): 由 `ServiceLoader` 加载，并根据配置值进行选择。
2. 策略处理器和作业适配器的类名映射。
3. 用于 `StatisticsCalculator` 和 `MetricsEvaluator` 的类型化 SPI。

## 扩展点与配置键

| 区域 | 接口 / 类型 | 配置键 | 加载模式 |
| --- | --- | --- | --- |
| 推荐器统计信息 | `StatisticsProvider` | `gravitino.optimizer.recommender.statisticsProvider` | 基于 `name()` 的 `Provider` SPI |
| 推荐器策略源 | `StrategyProvider` | `gravitino.optimizer.recommender.strategyProvider` | 基于 `name()` 的 `Provider` SPI |
| 推荐器表元数据 | `TableMetadataProvider` | `gravitino.optimizer.recommender.tableMetaProvider` | 基于 `name()` 的 `Provider` SPI |
| 推荐器作业提交 | `JobSubmitter` | `gravitino.optimizer.recommender.jobSubmitter` | 基于 `name()` 的 `Provider` SPI |
| 策略评估逻辑 | `StrategyHandler` | `gravitino.optimizer.strategyHandler.<strategyType>.className` | 基于类名反射 |
| 作业模板适配 | `GravitinoJobAdapter` | `gravitino.optimizer.jobAdapter.<jobTemplate>.className` | 基于类名反射 |
| 更新统计信息接收器 | `StatisticsUpdater` | `gravitino.optimizer.updater.statisticsUpdater` | 基于 `name()` 的 `Provider` SPI |
| 更新指标接收器 | `MetricsUpdater` | `gravitino.optimizer.updater.metricsUpdater` | 基于 `name()` 的 `Provider` SPI |
| 监控指标源 | `MetricsProvider` | `gravitino.optimizer.monitor.metricsProvider` | 基于 `name()` 的 `Provider` SPI |
| 监控表-作业关系 | `TableJobRelationProvider` | `gravitino.optimizer.monitor.tableJobRelationProvider` | 基于 `name()` 的 `Provider` SPI |
| 监控评估器 | `MetricsEvaluator` | `gravitino.optimizer.monitor.metricsEvaluator` | 类型化 SPI (`ServiceLoader<MetricsEvaluator>`) |
| 监控回调 | `MonitorCallback` | `gravitino.optimizer.monitor.callbacks` | 基于 `name()` 的 `Provider` SPI（逗号分隔） |
| CLI 计算器 | `StatisticsCalculator` | CLI `--calculator-name` | 类型化 SPI (`ServiceLoader<StatisticsCalculator>`) |

## 实现自定义 Provider

大多数扩展点使用 `Provider`：

```java
public class MyStatisticsProvider implements StatisticsProvider {
  @Override
  public String name() {
    return "my-statistics-provider";
  }

  @Override
  public void initialize(OptimizerEnv optimizerEnv) {
    // Initialize clients and resources from the configuration file.
  }

  @Override
  public void close() throws Exception {}
}
```

要求：

- 保持稳定的 `name()` 值；配置通过此名称进行解析（不区分大小写）。
- 提供一个公共的无参构造函数。
- 正确实现 `initialize(OptimizerEnv)` 和 `close()` 的生命周期。

## 使用 ServiceLoader 注册

### `Provider` 实现

创建文件：

`META-INF/services/org.apache.gravitino.maintenance.optimizer.api.common.Provider`

每行添加您的实现类名称：

```text
com.example.optimizer.MyStatisticsProvider
com.example.optimizer.MyJobSubmitter
```

### `StatisticsCalculator` 实现

创建文件：

`META-INF/services/org.apache.gravitino.maintenance.optimizer.api.updater.StatisticsCalculator`

### `MetricsEvaluator` 实现

创建文件：

`META-INF/services/org.apache.gravitino.maintenance.optimizer.api.monitor.MetricsEvaluator`

## 配置 `gravitino-optimizer.conf`

```properties
gravitino.optimizer.recommender.statisticsProvider = my-statistics-provider
gravitino.optimizer.recommender.jobSubmitter = my-job-submitter

gravitino.optimizer.strategyHandler.my-strategy.className = com.example.optimizer.MyStrategyHandler
gravitino.optimizer.jobAdapter.my-job-template.className = com.example.optimizer.MyJobAdapter

gravitino.optimizer.monitor.metricsEvaluator = my-metrics-evaluator
```

备注：

- `strategyHandler.<strategyType>.className` 必须与策略内容中的 `strategy.type` 匹配。
- `jobAdapter.<jobTemplate>.className` 必须与目标作业模板名称匹配。
- `jobSubmitterConfig.*` 条目将作为共享运行时选项传递给作业提交器。

## 打包和部署

- 构建一个包含您的类和 `META-INF/services` 文件的 JAR。
- 将该 JAR 放入运行时类路径中，例如 `${GRAVITINO_HOME}/optimizer/libs/`。
- 在测试前重启进程。

如果你还扩展 Gravitino 服务器作业执行，请参阅[在 Gravitino 中管理作业](../manage-jobs-in-gravitino.md)。

## 验证清单

1. `--help` 未显示加载时 SPI 错误。
2. 使用您的扩展的命令运行时不会出现 `No ... found for provider name` 错误。
3. 策略流可以解析处理器和作业适配器映射。
4. 试运行 (`submit-strategy-jobs --dry-run`) 打印预期的建议。

## 相关

- [表维护服务](./optimizer.md)
- [配置](./optimizer-configuration.md)
- [CLI 参考](./optimizer-configuration.md)
- [故障排除](./optimizer-troubleshooting.md)
