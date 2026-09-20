---
title: "Troubleshooting"
slug: "/table-maintenance-service/troubleshooting"
keywords:
  - table maintenance
  - troubleshooting
  - spark
license: "This software is licensed under the Apache License version 2."
---

## 概述

失败分为三类，与它们在工作流中发生的位置相对应。命令和参数错误会立即出现。评估问题不会产生错误，而是没有任何输出，这正是它们令人困惑的原因。执行失败发生在 Spark 内部，因此真正的信息在暂存日志中，而不是在 API 响应中。

暂存日志位于 `/tmp/gravitino/jobs/staging/{metalake}/{job_template_name}/{job_id}/` 下，由 `gravitino.job.stagingDir` 控制。读取 `error.log` 以获取失败信息，读取 `output.log` 以获取结果。

## 命令与参数错误

这些会立即从 CLI 返回并指出问题所在。

**`无效的 --type`** — 命令名称采用 kebab-case。请使用 `update-statistics`，而不是 `update_statistics`。

**`--statistics-payload 和 --file-path 不能同时使用`** —— `local-stats-calculator` 仅接受一个输入源。

**`requires one of --statistics-payload or --file-path`** — 来自另一侧的相同规则。使用 `--calculator-name local-stats-calculator` 时，必须提供这两者之一。

**`--partition-path 必须是 JSON 数组`** —— 即使对于单个分区，也请传递一个数组：

```text
[{"dt":"2026-01-01"}]
```

**`指定的优化器配置文件不存在`** —— 检查 `--conf-path` 的值以及文件的权限。

**`未为策略类型 ... 配置 StrategyHandler 类`** — CLI 配置中缺少策略处理器映射：

```properties
gravitino.optimizer.strategyHandler.iceberg-data-compaction.className = org.apache.gravitino.maintenance.optimizer.recommender.handler.compaction.CompactionStrategyHandler
```

打包的默认配置已经包含了此项，因此看到它通常意味着是手动编写的配置文件。

## 评估不产生任何结果

这些是棘手的情况，因为成功和“策略决定不采取行动”看起来完全一样。

**`No identifiers matched strategy name ...`** — `--strategy-name` takes the policy name, for example `iceberg_compaction_default`. It does not take the policy type `system_iceberg_compaction` or the strategy type `iceberg-data-compaction`, despite being called strategy name.

**试运行不打印 `DRY-RUN` 或 `SUBMIT` 行** — 未满足触发条件。对于压缩，请检查表的统计信息中的 `custom-data-file-mse` 和 `custom-delete-file-number` 是否足够大以满足策略规则。表中的小文件太少是常见原因，解决方法是增加数据，而不是增加配置。

**`monitor-metrics` 意外返回 `evaluation=false`** — 请同时检查规则名称和采样窗口：

1. 使用 `list-table-metrics` 查询当前指标，添加 `--partition-path` 以指定分区范围。
2. 在 `gravitino.optimizer.monitor.gravitinoMetricsEvaluator.rules` 中使用您的环境返回的确切指标名称。看起来足够接近的名称无效。
3. 确保 `--action-time` 落在同时存在之前和之后样本的范围内。

## 作业执行失败

**状态长时间保持 `queued` 或 `started`** — REST 状态采用轮询而非推送，且 `gravitino.job.statusPullIntervalInMs` 默认为五分钟。在本地工作时，将其降低至 `10000` 并重启服务器。如果状态确实是卡死而非延迟，请读取暂存目录中的 `error.log`。

**Spark 因 `hdfs://localhost:9000` 或其他文件系统错误而失败** —— Spark 在没有 HDFS 的机器上默认使用 HDFS：

```properties
spark.hadoop.fs.defaultFS=file:///
```

**`submit-update-stats-job` 因 JDBC 指标错误而失败** — 当 `--updater-options` 包含 `gravitino.optimizer.jdbcMetrics.*` 时，JDBC 驱动程序必须位于 Spark 运行时类路径上。`ClassNotFoundException` 和 `No suitable driver` 都意味着同一件事：

```json
{
  "spark.jars": "/path/to/postgresql-42.7.4.jar"
}
```

**`提供的凭据不受支持`或 Iceberg `未授权`** — 安全的 Gravitino 端点需要在 `updater_options` 中为 `builtin-iceberg-update-stats` 配置 `auth_type` / `username` / `password`（或 OAuth client-credentials 字段）。安全的 Iceberg REST catalog 需要在 `spark-conf` 中为任何读取该表的内置作业配置 `rest.auth.*`。参见 [配置](./optimizer-configuration.md)。

**内置 Iceberg 作业失败并提示 `Missing Iceberg Spark session extensions`** —
当缺少 `IcebergSparkSessionExtensions` 时，Spark 仅发出警告，因此内置作业会检查
`SparkSession` 启动后的 classpath，并在缺少 Iceberg Spark
运行时时以非零状态退出。模板配置了 Iceberg 类但将 `jars` 留空，并且
`gravitino-jobs` 不捆绑 `iceberg-spark-runtime`。原生的 Spark 安装是不够的。
将版本匹配的 Iceberg Spark 运行时放在作业 classpath 上，例如：

```json
{
  "spark.jars": "/path/to/iceberg-spark-runtime-3.5_2.12-1.11.0.jar"
}
```

使用与您的集群匹配的 Spark、Scala 和 Iceberg 版本。参见
[内置作业模板](./optimizer-cli-reference.md#built-in-job-templates)。

**多级分区重写失败** — 在 `1.2.0` 版本中，重写通过恒等转换与时间转换组合分区的表，例如 `PARTITIONED BY (p, days(ts))`，会失败，错误信息为：

```text
Cannot translate Spark expression ... day(cast(ts as date)) ... to data source filter
```

通过检查 `/api/metalakes/{metalake}/jobs/runs/{job_id}` 处的作业运行情况并读取 `builtin-iceberg-rewrite-data-files` 下的 `error.log` 来确认这一点。唯一的解决方法是压缩 identity 分区表，其余表保持不变。

在 `1.2.0` 中观察到：

| 分区                                                                  | 重写 |
|-------------------------------------------------------------------------------|---------|
| `p`, `p, c2`                                                                    | 成功   |
| `p, years(ts)`, `p, months(ts)`, `p, days(ts)`, `p, hours(ts)`                  | 失败   |
| `p, truncate(1, c2)`, `p, bucket(8, id)`                                        | 失败   |

## 相关

- [表维护服务](./optimizer.md)
- [配置](./optimizer-configuration.md)
- [快速入门](./optimizer.md#walkthrough)
- [CLI 参考](./optimizer-configuration.md)
