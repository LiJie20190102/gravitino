---
title: "Configuration"
slug: "/table-maintenance-service/optimizer-configuration"
keywords:
  - table maintenance
  - configuration
license: "This software is licensed under the Apache License version 2."
---

有三层配置适用，它们在不同的位置设置，对应不同的生命周期。服务器配置控制作业如何运行，CLI 配置控制命令如何到达 Gravitino，而 `jobConf` 控制单个作业的提交。

| 层               | 所在位置                  | 生命周期            |
|---------------------|----------------------------------|---------------------|
| 服务器              | `gravitino.conf`                 | 直到服务器重启 |
| CLI                 | `conf/gravitino-optimizer.conf`  | 每次命令          |
| 作业提交      | 请求体中的 `jobConf`    | 单次作业运行          |

## 服务器配置

在 `gravitino.conf` 中设置这些。它们控制的是作业执行器而非维护本身，因此适用于 Gravitino 运行的每个作业。

```properties
gravitino.job.executor=local
gravitino.job.statusPullIntervalInMs=300000
gravitino.jobExecutor.local.sparkHome=/path/to/spark
```

`gravitino.job.statusPullIntervalInMs` 默认为五分钟。作业状态采用轮询而非推送方式，因此 REST 状态可能会比实际的 Spark 进程滞后一个完整的间隔，这会让正在运行的作业看起来像卡住了。在本地作业时将其降低到 `10000` 并重启服务器。

## CLI 配置

CLI 需要知道 Gravitino 的位置以及要使用哪些组件。这是一个用于 `submit-strategy-jobs` 的最小工作文件。

```properties
gravitino.optimizer.gravitinoUri = http://localhost:8090
gravitino.optimizer.gravitinoMetalake = test
gravitino.optimizer.gravitinoDefaultCatalog = rest_catalog
gravitino.optimizer.recommender.statisticsProvider = gravitino-statistics-provider
gravitino.optimizer.recommender.strategyProvider = gravitino-strategy-provider
gravitino.optimizer.recommender.tableMetaProvider = gravitino-table-metadata-provider
gravitino.optimizer.recommender.jobSubmitter = gravitino-job-submitter
gravitino.optimizer.strategyHandler.iceberg-data-compaction.className = org.apache.gravitino.maintenance.optimizer.recommender.handler.compaction.CompactionStrategyHandler
gravitino.optimizer.jobSubmitterConfig.catalog_name = rest_catalog
gravitino.optimizer.jobSubmitterConfig.spark_master = local[2]
gravitino.optimizer.jobSubmitterConfig.spark_executor_instances = 1
gravitino.optimizer.jobSubmitterConfig.spark_executor_cores = 1
gravitino.optimizer.jobSubmitterConfig.spark_executor_memory = 1g
gravitino.optimizer.jobSubmitterConfig.spark_driver_memory = 1g
gravitino.optimizer.jobSubmitterConfig.catalog_type = rest
gravitino.optimizer.jobSubmitterConfig.catalog_uri = http://localhost:9001/iceberg
# Leave empty for a local filesystem; set to your warehouse URI for cloud or HDFS storage.
gravitino.optimizer.jobSubmitterConfig.warehouse_location =
gravitino.optimizer.jobSubmitterConfig.spark_conf = {"spark.master":"local[2]","spark.hadoop.fs.defaultFS":"file:///"}
```

当 Gravitino 服务器启用身份验证时，`builtin-iceberg-update-stats` 需要
在 `--updater-options` / `updater_options` 中为 Gravitino 客户端提供凭据（统计信息
更新器和 `submit-update-stats-job` `runJob` 调用）：

| `auth_type`      | 字段                                                                                         |
|------------------|------------------------------------------------------------------------------------------------|
| `none` (默认) | (无)                                                                                         |
| `simple`         | `username` (可选)                                                                          |
| `basic`          | `username`, `password`                                                                         |
| `oauth`          | 仅限客户端凭据：`oauth_server_uri`, `oauth_path`, `oauth_credential`, `oauth_scope` |

Iceberg REST catalog 认证是独立的：在 `spark-conf` 中为任何内置
与安全 IRC 通信的作业（包括 update-stats）。Expire-snapshots 和 rewrite-data-files
不读取 `updater_options` 认证字段。

`updater_options` 中的密码和 OAuth 凭据（以及 `spark_conf` 中的密钥）会随
作业命令行和 `jobConf` 一起传输；避免记录原始的 `jobConf`（submit-update-stats CLI
会在 DRY-RUN / SUBMIT 输出中对其进行脱敏处理）。

`gravitino.optimizer.jobSubmitterConfig.` 下的所有内容都会成为此 CLI 提交的作业的 `jobConf`，因此这两层在不同的名称下包含相同的键。

## 作业提交配置

直接作业提交带有其自身的 `jobConf`。这是 `builtin-iceberg-update-stats`，包含它所需的键。

```json
{
  "catalog_name": "rest_catalog",
  "table_identifier": "db.t1",
  "update_mode": "all",
  "updater_options": "{\"gravitino_uri\":\"http://localhost:8090\",\"metalake\":\"test\",\"statistics_updater\":\"gravitino-statistics-updater\",\"metrics_updater\":\"gravitino-metrics-updater\",\"auth_type\":\"basic\",\"username\":\"admin\",\"password\":\"YourSecureGravitinoPassword\"}",
  "spark_conf": "{\"spark.master\":\"local[2]\",\"spark.hadoop.fs.defaultFS\":\"file:///\"}",
  "spark_master": "local[2]",
  "spark_executor_instances": "1",
  "spark_executor_cores": "1",
  "spark_executor_memory": "1g",
  "spark_driver_memory": "1g",
  "catalog_type": "rest",
  "catalog_uri": "http://localhost:9001/iceberg",
  "warehouse_location": ""
}
```

`updater_options` 和 `spark_conf` 是 JSON 对象内的 JSON 字符串，因此它们的引号被转义。这种嵌套是导致提交格式错误的最常见原因。

内置的 Iceberg 模板将可选键列为 `--flag` + `{{placeholder}}`。从
`jobConf` 中省略某个键并不会从提交的命令中移除该标志；这可能会留下一个悬空标志，例如
`--updater-options` 没有值。建议为您使用的每个占位符发送一个显式值
（或文档中记录的默认值），而不是删除该键。参见
[内置作业模板](./optimizer-cli-reference.md#built-in-job-templates)。

内置的 Iceberg 模板还需要在 Spark classpath 上具有 Iceberg Spark 运行时。它们并不
自带该 JAR 或填充模板 `jars`，因此请自行包含它 —— 例如
`spark_conf` 中的 `"spark.jars":"/path/to/iceberg-spark-runtime-....jar"`。将 artifact 匹配到
你的 Spark、Scala 和 Iceberg 版本。详情位于
[内置作业模板](./optimizer-cli-reference.md#built-in-job-templates)。

`warehouse_location` 在进行本地文件系统测试时可以为空。对于 HDFS 或云对象存储，请将其设置为仓库 URI。

## 针对本地文件系统运行

在没有 HDFS 的机器上，Spark 仍然默认使用 `hdfs://localhost:9000` 并导致失败。请显式设置默认文件系统，在用于作业提交的 `spark_conf` 中和 CLI 的 `spark_conf` 值中进行设置：

```properties
spark.hadoop.fs.defaultFS=file:///
```

## 检查您的配置

在假设配置问题是代码问题之前，有四件事值得确认。

- `builtin-iceberg-update-stats` 和 `builtin-iceberg-rewrite-data-files` 出现在作业模板列表中。
- 策略已附加到目标表，而不仅仅是创建。
- `submit-strategy-jobs` 打印 `SUBMIT` 行，而不是没有任何输出。
- 对于非空表，重写日志显示 `Rewritten data files: N`，其中 `N` 大于零。

## 相关

- [表维护服务](./optimizer.md) 了解概念和操作流程
- [CLI 参考](./optimizer-cli-reference.md) 了解所有命令和内置作业模板
- [故障排除](./optimizer-troubleshooting.md) 用于命令或作业失败时
- [扩展指南](./optimizer-extension-guide.md) 了解自定义策略和提供程序
