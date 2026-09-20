---
title: "CLI Reference"
slug: "/table-maintenance-service/optimizer-cli-reference"
keywords:
  - table maintenance
  - cli
  - job template
license: "This software is licensed under the Apache License version 2."
---

## 简介

使用 `--help` 列出所有命令，或使用 `--help --type <command>` 获取特定命令的帮助。

默认情况下，优化器 CLI 从当前工作
目录加载 `conf/gravitino-optimizer.conf`。仅当需要自定义配置文件时才使用 `--conf-path`。

## 命令快速参考

| 命令 (`--type`) | 必需选项 | 可选选项 | 用途 |
| --- | --- | --- | --- |
| `submit-strategy-jobs` | `--identifiers`, `--strategy-name` | `--dry-run`, `--limit` | 推荐并可选地提交作业 |
| `update-statistics` | `--calculator-name` | `--identifiers`, `--statistics-payload`, `--file-path` | 计算并持久化统计信息 |
| `append-metrics` | `--calculator-name` | `--identifiers`, `--statistics-payload`, `--file-path` | 计算并追加指标 |
| `monitor-metrics` | `--identifiers`, `--action-time` | `--range-seconds`, `--partition-path` | 使用前/后指标评估规则 |
| `list-table-metrics` | `--identifiers` | `--partition-path` | 查询已存储的表或分区指标 |
| `list-job-metrics` | `--identifiers` | 无 | 查询已存储的作业指标 |
| `submit-update-stats-job` | `--identifiers` | `--dry-run`, `--update-mode`, `--updater-options`, `--spark-conf` | 提交内置的 Iceberg 更新统计信息/指标 Spark 作业 |

## 选项字段含义

| 选项 | 含义 | 使用者 |
| --- | --- | --- |
| `--identifiers` | 逗号分隔的标识符。表格式支持 `catalog.schema.table`（或在配置了默认目录时支持 `schema.table`）。 | 大多数命令 |
| `--strategy-name` | 要评估的策略名称，例如 `iceberg_compaction_default`。 | `submit-strategy-jobs` |
| `--dry-run` | 预览模式。打印建议或作业配置而不提交作业。 | `submit-strategy-jobs`, `submit-update-stats-job` |
| `--limit` | 要处理的最大策略作业数。必须 `> 0`。 | `submit-strategy-jobs` |
| `--calculator-name` | 统计/指标计算器实现名称（例如 `local-stats-calculator`）。 | `update-statistics`, `append-metrics` |
| `--statistics-payload` | 作为输入的内联 JSON Lines 内容。与 `--file-path` 互斥。 | `update-statistics`, `append-metrics` |
| `--file-path` | JSON Lines 输入文件的路径。与 `--statistics-payload` 互斥。 | `update-statistics`, `append-metrics` |
| `--action-time` | 以 epoch 秒为单位的操作时间戳，用作评估锚点。 | `monitor-metrics` |
| `--range-seconds` | 用于监控评估的时间窗口（秒）。默认为 `86400`（24小时）。 | `monitor-metrics` |
| `--partition-path` | 分区路径 JSON 数组，例如 `'[{"dt":"2026-01-01"}]'`。需要且仅需要一个标识符。 | `monitor-metrics`, `list-table-metrics` |
| `--update-mode` | 控制内置更新作业更新的内容：`stats`、`metrics` 或 `all`（默认）。 | `submit-update-stats-job` |
| `--updater-options` | 传递给更新器逻辑的扁平 JSON 映射。对于 `stats`/`all`，需包含 `gravitino_uri` 和 `metalake`。 | `submit-update-stats-job` |
| `--spark-conf` | 作业使用的 Spark 和 Iceberg 目录配置的扁平 JSON 映射。 | `submit-update-stats-job` |

全局选项：

- `--conf-path`：可选的自定义配置文件路径。如果省略，CLI 将使用 `conf/gravitino-optimizer.conf`。

## `local-stats-calculator` 的输入格式

`local-stats-calculator` 读取 JSON Lines（每行一个 JSON 对象）。

## 保留字段

- `stats-type`：`table`、`partition` 或 `job`
- `identifier`：对象标识符
- `partition-path`：仅用于分区数据，例如 `{"dt":"2026-01-01"}`
- `timestamp`：可选的 epoch 秒数（指标点的记录级默认时间戳）

所有其他字段都被视为指标或统计值。

## 按作用域分类的支持示例

使用 JSON Lines（每行一个 JSON 对象）。以下示例侧重于表、分区和
作业范围，包含多个指标/统计字段：

```json
{"stats-type":"table","identifier":"catalog.db.t1","timestamp":1735689600,"row_count":100}
{"stats-type":"table","identifier":"catalog.db.t1","row_count":100,"total_file_size":1048576}
{"stats-type":"table","identifier":"catalog.db.t1","timestamp":1735689660,"row_count":120,"file_count":24,"avg_file_size":10485.76}
{"stats-type":"partition","identifier":"catalog.db.t1","timestamp":1735689720,"partition-path":{"dt":"2026-01-01"},"row_count":20}
{"stats-type":"partition","identifier":"catalog.db.t1","partition-path":{"dt":"2026-01-01","region":"us"},"row_count":12,"file_count":3}
{"stats-type":"job","identifier":"job-1","timestamp":1735689800,"duration_ms":12500,"rewritten_files":18}
```

## 标识符规则

- 表和分区记录：`catalog.schema.table`
- 如果设置了 `gravitino.optimizer.gravitinoDefaultCatalog`，也接受 `schema.table`
- 作业记录：解析为常规的 Gravitino `NameIdentifier`

## CLI 工作流示例

## 批次统计更新

从 JSONL 输入计算并持久化表或分区统计信息。

```bash
./bin/gravitino-optimizer.sh \
  --type update-statistics \
  --calculator-name local-stats-calculator \
  --file-path ./table-stats.jsonl
```

## 批量追加指标

从 JSONL 输入中计算并追加表或作业指标。

```bash
./bin/gravitino-optimizer.sh \
  --type append-metrics \
  --calculator-name local-stats-calculator \
  --file-path ./table-stats.jsonl
```

## 试运行策略提交

预览建议，而无需实际提交作业。

```bash
./bin/gravitino-optimizer.sh \
  --type submit-strategy-jobs \
  --identifiers rest_catalog.db.t1 \
  --strategy-name iceberg_compaction_default \
  --dry-run \
  --limit 10
```

## 提交策略作业

为匹配给定策略名称的标识符提交作业。

```bash
./bin/gravitino-optimizer.sh \
  --type submit-strategy-jobs \
  --identifiers rest_catalog.db.t1 \
  --strategy-name iceberg_compaction_default \
  --limit 10
```

## 监控指标

评估操作时间前后的监控规则。

```bash
./bin/gravitino-optimizer.sh \
  --type monitor-metrics \
  --identifiers catalog.db.sales \
  --action-time 1735689600 \
  --range-seconds 86400
```

在 `gravitino-optimizer.conf` 中配置评估器规则：

```properties
gravitino.optimizer.monitor.gravitinoMetricsEvaluator.rules = table:row_count:avg:le,job:duration:latest:le
```

规则格式为 `scope:metricName:aggregation:comparison`：

- `scope`：`table` 或 `job`（`table` 规则也适用于分区范围）
- `aggregation`：`max|min|avg|latest`
- `comparison`：`lt|le|gt|ge|eq|ne`

当指标由 `submit-update-stats-job --update-mode metrics` 生成时，指标名称为
通常为 `custom-*`（例如 `custom-data-file-mse`）。请先使用 `list-table-metrics`，并
使用您的环境返回的确切指标名称来配置规则。

## 提交内置更新统计信息作业

直接提交内置的 Iceberg 更新统计信息/指标的 Spark 作业。

```bash
./bin/gravitino-optimizer.sh \
  --type submit-update-stats-job \
  --identifiers rest_catalog.db.t1 \
  --update-mode all \
  --updater-options '{"gravitino_uri":"http://localhost:8090","metalake":"test"}' \
  --spark-conf '{"spark.sql.catalog.rest_catalog.type":"rest","spark.sql.catalog.rest_catalog.uri":"http://localhost:9001/iceberg","spark.hadoop.fs.defaultFS":"file:///"}'
```

备注：

- `--identifiers` 支持 `catalog.schema.table` 或 `schema.table`（当配置了默认 catalog 时）。
- `--update-mode` 支持 `stats|metrics|all`（默认为 `all`）。
- 对于 `stats` 或 `all`，`--updater-options` 必须包含 `gravitino_uri` 和 `metalake`。
- 如果 `--updater-options` 包含外部 JDBC metrics 设置
（`gravitino.optimizer.jdbcMetrics.*`），请确保 JDBC 驱动 JAR 对 Spark 可用
运行时 classpath（例如通过 `--spark-conf` 中的 `spark.jars`）。
- `--spark-conf` 和 `--updater-options` 是扁平的 JSON map。

## 列出表格指标

查询表作用域下存储的指标。

```bash
./bin/gravitino-optimizer.sh \
  --type list-table-metrics \
  --identifiers catalog.db.sales
```

对于分区范围，请提供一个分区路径 JSON 数组：

```bash
./bin/gravitino-optimizer.sh \
  --type list-table-metrics \
  --identifiers catalog.db.sales \
  --partition-path '[{"dt":"2026-01-01"}]'
```

## 列出作业指标

查询作业作用域内存储的指标。

```bash
./bin/gravitino-optimizer.sh \
  --type list-job-metrics \
  --identifiers catalog.db.optimizer_job
```

## 输出指南

- `SUMMARY: ...`: `update-statistics` 和 `append-metrics` 的摘要
- `DRY-RUN: ...`: 不提交作业的推荐预览
- `SUBMIT: ...`: 策略作业或内置 update-stats 作业提交成功
- `SUMMARY: submit-update-stats-job ...`: 内置 update-stats 提交的摘要
- `MetricsResult{...}`: 由 list 命令返回
- `EvaluationResult{...}`: 由 monitor 命令返回

示例：

```text
SUMMARY: statistics totalRecords=3 tableRecords=2 partitionRecords=1 jobRecords=0
DRY-RUN: strategy=iceberg-data-compaction identifier=rest_catalog.db.t1 score=95 jobTemplate=builtin-iceberg-rewrite-data-files jobOptions={catalog_name=rest_catalog, table_identifier=db.t1}
SUBMIT: strategy=iceberg-data-compaction identifier=rest_catalog.db.t1 score=95 jobTemplate=builtin-iceberg-rewrite-data-files jobOptions={catalog_name=rest_catalog, table_identifier=db.t1} jobId=1f54c6d3-4e27-4cc8-bdfa-b05ecf59a4c2
DRY-RUN: identifier=rest_catalog.db.t1 jobTemplate=builtin-iceberg-update-stats jobConfig={catalog_name=rest_catalog, table_identifier=db.t1, update_mode=all, updater_options={"gravitino_uri":"http://localhost:8090","metalake":"test"}, spark_conf={"spark.master":"local[2]","spark.hadoop.fs.defaultFS":"file:///"}}
SUMMARY: submit-update-stats-job total=1 submitted=1 dryRun=false
MetricsResult{scopeType=TABLE, identifier=rest_catalog.db.t1, partitionPath=<table-or-job-scope>, metrics={row_count=[{timestamp=1735689600, value=100}]}}
EvaluationResult{scopeType=TABLE, identifier=rest_catalog.db.t1, partitionPath=<table-or-job-scope>, evaluation=true, evaluatorName=gravitino-metrics-evaluator, actionTimeSeconds=1735689600, rangeSeconds=86400, beforeMetrics={row_count=[MetricSample{timestampSeconds=1735686000, value=120}]}, afterMetrics={row_count=[MetricSample{timestampSeconds=1735689600, value=100}]}}
```

## 内置作业模板

该服务自带三个作业模板，它们是互补的，而非替代方案。一次完整的维护过程会收集统计信息、压缩数据文件，然后使压缩刚刚创建的快照历史过期。

| 作业模板                              | 作用                                     |
|---------------------------------------|-------------------------------------------|
| `builtin-iceberg-update-stats`        | 收集文件统计信息和指标      |
| `builtin-iceberg-rewrite-data-files`  | 压缩小数据文件                 |
| `builtin-iceberg-expire-snapshots`    | 移除旧的快照元数据             |

每个都可以直接通过 REST 提交，并且前两个也是策略驱动的工作流代您提交的内容。有关策略驱动路径，请参见 [快速入门](./optimizer.md#walkthrough)。

这些模板设置了 Iceberg Spark 会话和 catalog 类，但它们没有列出 Iceberg Spark
`jars` 中的 runtime。`gravitino-jobs` 也从其 shaded JAR 中排除了该 runtime，因此
与你的 Spark 集群一起运行的版本需要由你来提供。请提供一个匹配的
`iceberg-spark-runtime-<sparkMajor>_<scala>` JAR，放在作业执行器使用的 Spark classpath 上 ——
通常通过 `spark_conf` 中的 `spark.jars`，或者将其安装到 `SPARK_HOME` 中。请对齐
artifact 与你实际运行的 Spark、Scala 和 Iceberg 版本。一个参考坐标用于
Gravitino 自身的作业测试中是 `org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.11.0`。
如果没有该 runtime，内置的 Iceberg 作业会在 Spark 启动后失败，而不是在没有
Iceberg 支持的情况下继续运行。

可选模板参数仍然以 `--flag` + `{{placeholder}}` 对的形式列出。如果 `jobConf`
省略了某个键（或未解析占位符），该标志将作为
悬空参数保留在进程命令行上（例如 `--updater-options` 在 `--spark-conf` 之前没有值）。调用者
和 UI 应该为他们关心的每个占位符提供显式值，包括可选的
那些他们有意禁用或保留为文档记录的默认值的参数，而不是省略该键。

## 更新统计信息

`builtin-iceberg-update-stats` 读取表并写回供策略评估的统计信息和指标。压缩策略会读取 `custom-data-file-mse` 和 `custom-delete-file-number`，因此在此作业至少运行一次之前，其他任何策略都不会触发。

其 `jobConf` 记录在 [Configuration](./optimizer-configuration.md#job-submission-configuration) 中。

## 重写数据文件

`builtin-iceberg-rewrite-data-files` 自行执行压缩，将小数据文件合并为较大的文件。当超过其阈值时，压缩策略就会提交它。

在 alpha 版本中，这仅适用于每个分区都使用 identity 转换的 Iceberg 表。将 identity 与 time 或 bucket 转换结合使用的表在重写期间会失败，相关内容详见[故障排除](./optimizer-troubleshooting.md#job-execution-failures)。

有关驱动它的策略，包括阈值调优，请参见 [Iceberg Compaction Policy](../iceberg-compaction-policy.md)。

## 使快照过期

`builtin-iceberg-expire-snapshots` 移除旧的 Iceberg 快照及其背后的元数据文件。如果没有定期的过期处理，快照 JSON 文件和 manifest 列表会无限累积，这会减慢表操作并浪费存储空间。压缩会加剧这一问题，因为每次重写都会创建一个快照。

该作业通过 Spark SQL 调用 Iceberg 的 `expire_snapshots` 存储过程。

| 属性    | 值                                                                       |
|-------------|-----------------------------------------------------------------------------|
| 名称        | `builtin-iceberg-expire-snapshots`                                          |
| 类型        | Spark                                                                       |
| 版本     | `v1`                                                                        |
| 主类  | `org.apache.gravitino.maintenance.jobs.iceberg.IcebergExpireSnapshotsJob`   |

## 参数

`catalog_name` 和 `table_identifier` 是必填项。其余为可选项。

| 键              | 描述                                                          | 默认值                     |
|------------------|-----------------------------------------------------------------------|-----------------------------|
| `catalog_name`   | 在 Spark 中注册的 Iceberg catalog 名称                          | 必填                    |
| `table_identifier` | 完全限定的表名，例如 `db.sample`                    | 必填                    |
| `older_than`     | 使早于此 `yyyy-MM-dd HH:mm:ss` 时间戳的快照过期     | 五天前               |
| `retain_last`    | 无论时间长短，至少保留的最近快照数量         | `1`                         |
| `stream_results` | 当存在中间删除结果时进行流式传输                     | 已禁用                    |
| `spark_conf`     | Spark 配置的 JSON 映射                                      | 无                        |

`older_than` 和 `retain_last` 共同作用，且以 `retain_last` 为准。将 `older_than` 设置为昨天，同时将 `retain_last` 设置为 `5`，会保留五个快照，即使这五个快照都早于昨天。

## 提交作业

```bash
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
    "jobTemplateName": "builtin-iceberg-expire-snapshots",
    "jobConf": {
      "catalog_name": "rest_catalog",
      "table_identifier": "db.t1",
      "older_than": "2024-01-01 00:00:00",
      "retain_last": "3",
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
  http://localhost:8090/api/metalakes/test/jobs
```

省略 `older_than` 并仅传递 `retain_last` 是首次运行时更安全的默认设置，因为它通过数量而不是你需要推算的日期来限制结果。

任务构建此语句，仅包含您提供的可选参数：

```sql
CALL `rest_catalog`.system.expire_snapshots(
  table => 'db.t1',
  older_than => TIMESTAMP '2024-01-01 00:00:00',
  retain_last => 3,
  stream_results => true
)
```

## 验证结果

```bash
curl -sS "http://localhost:8090/api/metalakes/test/jobs/{job_id}" | jq '.job.state'
cat /tmp/gravitino/jobs/staging/test/builtin-iceberg-expire-snapshots/{job_id}/stdout.log
```

成功的运行会将其状态报告为 `SUCCEEDED` 并记录其移除的计数：

```text
Expire Snapshots Results:
  Deleted data files: 12
  Deleted manifest files: 8
  Deleted manifest lists: 3
```

## 相关

- [表维护服务](./optimizer.md) 以了解概念和操作指南
- [配置](./optimizer-configuration.md) 以了解三层配置
- [Iceberg Compaction Policy](../iceberg-compaction-policy.md) 以调整内置策略
- [管理作业](../manage-jobs-in-gravitino.md) 以了解作业状态和模板
