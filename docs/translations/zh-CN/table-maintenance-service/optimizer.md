---
title: "Table Maintenance Service"
slug: "/table-maintenance-service/optimizer"
keywords:
  - table maintenance
  - compaction
  - statistics
  - quick start
license: "This software is licensed under the Apache License version 2."
---

## 概述

表维护服务无需任何人监控即可保持表的健康状态。您将策略附加到目录、架构或表上；该服务会收集统计信息，根据该策略对其进行评估，并在策略指示需要工作时提交作业。

该框架是通用的。指标收集、策略评估和作业提交不与任何特定的表格式绑定，并且每一项都是一个 Java ServiceLoader 扩展点。内置功能被刻意限制得更窄，在 alpha 版本中，这意味着对恒等分区表进行 Iceberg 数据文件压缩。

CLI 二进制文件、其配置文件及其配置键保留了旧名称 `optimizer`，因此你会在各处看到 `gravitino-optimizer.sh`、`gravitino-optimizer.conf` 和 `gravitino.optimizer.*`。这些是字面字符串，而不是第二个产品。

## Alpha Scope

在开始针对内置功能进行评估之前，请确认您的环境符合此列表。列表之外的任何内容都需要自定义扩展，这在[扩展指南](./optimizer-extension-guide.md)中有所介绍。

- 压缩是唯一的内置策略。没有内置的快照过期、孤儿文件清理或排序和聚簇维护。
- 压缩仅适用于 Iceberg 表，且仅适用于每个分区都使用恒等变换的情况。
- 该服务通过 CLI 工作流驱动，而不是按自身计划运行。


## 工作原理

维护以四个步骤运行。每个步骤都是一个独立的命令，因此您可以在其中任何一个步骤之后停止，而第二步的试运行会在任何实际运行之前显示将要提交的内容。

| 步骤     | 你运行的内容                                      | 它生成的内容                                        |
|----------|---------------------------------------------------|---------------------------------------------------------|
| 收集  | `update-statistics`, `append-metrics`             | 表的统计信息，JDBC 仓库中的指标 |
| 评估 | `submit-strategy-jobs --dry-run`                  | 候选操作，不提交任何内容               |
| 提交   | `submit-strategy-jobs`, `submit-update-stats-job` | 一个 Spark 作业，通过作业状态和暂存日志进行跟踪     |
| 观察  | `monitor-metrics`, `list-table-metrics`           | 前后指标，以及重写的数据文件      |

## 执行模式

有两种方法，它们的区别在于数字的来源，而不是它们的作用。

内置工作流通过 Gravitino 服务器及其作业模板驱动一切，使用附加到表上的策略来决定运行什么。将其用于服务器端操作运行。

本地计算器会读取你提供的 JSONL 文件，并直接从中更新统计信息和指标。将其用于测试和批处理脚本，在这些场景中你已经有了数据，并希望将其输入进去，而无需服务器进行计算。

## 命名

三个标识符看似可以互换，实则不然。

| 术语          | 示例                      | 出现位置                                           |
|---------------|------------------------------|------------------------------------------------------------|
| Policy name   | `iceberg_compaction_default` | The policy's own name, and the CLI `--strategy-name`       |
| Policy type   | `system_iceberg_compaction`  | The `policyType` field when creating a policy over REST    |
| Strategy type | `iceberg-data-compaction`    | The `strategy.type` field, and the strategy handler config |

`--strategy-name` 接受的是**策略名称**，尽管它的命名与此不符。传入另外两个中的任意一个都会报告没有匹配的标识符，而不是指出错误所在。

## 演练

这将使一个 Iceberg 表经历整个工作流程：创建它、用小文件填充它、附加压缩策略、收集统计信息，并让服务决定对其进行压缩。它在本地 Spark 上运行，大约需要十五分钟。

每个步骤都以检查结束。如果检查失败，请在此停止，因为每个步骤都依赖于前一个步骤。

### 先决条件

- 一个正在运行的带有 metalake 的 Gravitino 服务器。示例中使用 `test`。
- Spark 对作业执行器可用，通过 `SPARK_HOME` 或 `gravitino.jobExecutor.local.sparkHome`。
- 在该 Spark classpath 上有 Iceberg Spark runtime。内置的 Iceberg 模板配置了
`IcebergSparkSessionExtensions` 和 `SparkCatalog`，但 `gravitino-jobs` 不附带
Iceberg Spark runtime，且模板将 `jars` 留空，以便您的 Spark 和 Iceberg 版本
保持由您控制。标准的 Spark 发行版是不够的。请放置一个匹配的
`iceberg-spark-runtime-*` JAR 到作业 classpath 上 — 例如通过 `spark.jars` 在
`spark_conf` 中设置，或将其安装到您的 Spark 环境中。选择与您的
Spark、Scala 和 Iceberg 版本匹配的 artifact。jobs 模块是基于 Spark 3.5.x
和 Iceberg 1.11.0 构建和测试的（例如
`org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.11.0`）。如果没有它，作业在
Spark 启动后会失败，并报错指出缺少的 Iceberg 类。参见
[故障排除](./optimizer-troubleshooting.md#job-execution-failures)。
- `gravitino.job.statusPullIntervalInMs` 降低到 `10000` 并重启服务器。默认值为五分钟，这会让本教程中的每次状态检查都感觉像是出了问题。

如果你的 Iceberg REST 后端在内存中运行，请勿在中途重启。重启会重置元数据和数据文件，你将从头开始。

### 步骤 1：确认 Job Templates 是否存在

```bash
curl -sS "http://localhost:8090/api/metalakes/test" | jq
curl -sS "http://localhost:8090/api/metalakes/test/jobs/templates?details=true" \
  | jq '.jobTemplates[].name'
```

模板列表必须包含 `builtin-iceberg-update-stats` 和 `builtin-iceberg-rewrite-data-files`。如果不包含，说明 `auxlib` 中缺少 `gravitino-jobs` JAR 包。请添加它并重启服务器后再继续。

### 第 2 步：创建演示 Catalog、Schema 和 Table

```bash
# Catalog. An "already exists" error here is fine.
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rest_catalog",
    "type": "RELATIONAL",
    "comment": "Iceberg REST catalog",
    "provider": "lakehouse-iceberg",
    "properties": {
      "catalog-backend": "rest",
      "uri": "http://localhost:9001/iceberg"
    }
  }' \
  http://localhost:8090/api/metalakes/test/catalogs

# Schema
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{"name": "db", "comment": "maintenance demo schema", "properties": {}}' \
  http://localhost:8090/api/metalakes/test/catalogs/rest_catalog/schemas

# Table
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "t1",
    "comment": "maintenance demo table",
    "columns": [
      {"name": "id", "type": "integer", "nullable": true},
      {"name": "name", "type": "string", "nullable": true}
    ],
    "properties": {}
  }' \
  http://localhost:8090/api/metalakes/test/catalogs/rest_catalog/schemas/db/tables
```

### 步骤 3：创建值得压缩的内容

空表让策略无从响应，因此写入 100,000 行，每个文件上限为 1,000 行。这会产生许多小文件，而 compaction 存在的目的就是为了合并这些小文件。

```bash
${SPARK_HOME}/bin/spark-sql \
  --conf spark.hadoop.fs.defaultFS=file:/// \
  --conf spark.sql.catalog.rest_catalog=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.rest_catalog.type=rest \
  --conf spark.sql.catalog.rest_catalog.uri=http://localhost:9001/iceberg \
  -e "CREATE NAMESPACE IF NOT EXISTS rest_catalog.db; \
      SET spark.sql.files.maxRecordsPerFile=1000; \
      INSERT INTO rest_catalog.db.t1 \
      SELECT id, concat('name_', CAST(id AS STRING)) FROM range(0, 100000);"
```

如果没有 `spark.hadoop.fs.defaultFS=file:///`，Spark 会尝试访问 `hdfs://localhost:9000` 并失败。

### 步骤 4：附加压缩策略

创建策略是不够的。它必须附加到表上，而服务读取的正是该附加内容。

```bash
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iceberg_compaction_default",
    "comment": "Built-in Iceberg compaction policy",
    "policyType": "system_iceberg_compaction",
    "enabled": true,
    "content": {}
  }' \
  http://localhost:8090/api/metalakes/test/policies

curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{"policiesToAdd": ["iceberg_compaction_default"]}' \
  http://localhost:8090/api/metalakes/test/objects/table/rest_catalog.db.t1/policies
```

在继续之前，请确认附件：

```bash
curl -sS "http://localhost:8090/api/metalakes/test/objects/table/rest_catalog.db.t1/policies?details=true" | jq
```

### 第 5 步：收集统计信息

```bash
update_stats_job_id=$(curl -sS -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "jobTemplateName": "builtin-iceberg-update-stats",
    "jobConf": {
      "catalog_name": "rest_catalog",
      "table_identifier": "db.t1",
      "update_mode": "all",
      "updater_options": "{\"gravitino_uri\":\"http://localhost:8090\",\"metalake\":\"test\",\"statistics_updater\":\"gravitino-statistics-updater\",\"metrics_updater\":\"gravitino-metrics-updater\"}",
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
  }' \
  http://localhost:8090/api/metalakes/test/jobs/runs | jq -r '.job.jobId')

echo "update-stats job id: ${update_stats_job_id}"
```

等待它完成，然后确认统计数据已落地：

```bash
curl -sS "http://localhost:8090/api/metalakes/test/objects/table/rest_catalog.db.t1/statistics" | jq
```

响应必须包含 `custom-data-file-mse` 和 `custom-delete-file-number`。这两项是压缩策略评估的内容，因此如果缺失，下一步将无从决定。

### 步骤 6：评估并提交

Write the CLI configuration first. `--strategy-name` takes the **policy name**, not the policy type or the strategy type.

```bash
cat > /tmp/gravitino-optimizer-submit.conf <<'EOF_CONF'
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
EOF_CONF
```

先预览。试运行会评估策略并打印其将要执行的操作，而不会提交任何内容。

```bash
./bin/gravitino-optimizer.sh \
  --type submit-strategy-jobs \
  --identifiers rest_catalog.db.t1 \
  --strategy-name iceberg_compaction_default \
  --dry-run \
  --limit 10 \
  --conf-path /tmp/gravitino-optimizer-submit.conf
```

`DRY-RUN` 行意味着策略已触发。完全没有输出意味着它未触发，这通常意味着第 5 步的统计数据低于策略阈值，而不是出现了什么故障。

然后正式提交：

```bash
submit_output=$(./bin/gravitino-optimizer.sh \
  --type submit-strategy-jobs \
  --identifiers rest_catalog.db.t1 \
  --strategy-name iceberg_compaction_default \
  --limit 10 \
  --conf-path /tmp/gravitino-optimizer-submit.conf)
echo "${submit_output}"

strategy_job_id=$(echo "${submit_output}" | sed -n 's/.*jobId=\([^[:space:]]*\).*/\1/p')
[[ -z "${strategy_job_id}" ]] && echo 'ERROR: failed to extract strategy job ID' && exit 1
echo "strategy rewrite job id: ${strategy_job_id}"
```

### 步骤 7：验证重写

```bash
curl -sS "http://localhost:8090/api/metalakes/test/jobs/runs/${update_stats_job_id}" | jq
curl -sS "http://localhost:8090/api/metalakes/test/jobs/runs/${strategy_job_id}" | jq

log_dir="/tmp/gravitino/jobs/staging/test/builtin-iceberg-rewrite-data-files/${strategy_job_id}"
grep -E "Rewritten data files|Added data files|completed successfully" "${log_dir}/output.log"
```

`Rewritten data files: N` 且 `N` 大于零意味着工作流端到端运行成功。暂存路径来自 `gravitino.job.stagingDir`，其默认值为 `/tmp/gravitino/jobs/staging`。

REST 作业状态是轮询而非推送的，因此它滞后于实际的 Spark 进程，最多相差一个轮询间隔。这就是为什么前置条件将其降至十秒的原因。

## 相关

- 三个配置层的[配置](./optimizer-configuration.md)
- 所有命令和内置作业模板的[CLI 参考](./optimizer-cli-reference.md)
- 当上述内容未按预期运行时的[故障排除](./optimizer-troubleshooting.md)
- 自定义策略和提供程序的[扩展指南](./optimizer-extension-guide.md)
- 用于调整内置策略的 [Iceberg 合并策略](../iceberg-compaction-policy.md)
