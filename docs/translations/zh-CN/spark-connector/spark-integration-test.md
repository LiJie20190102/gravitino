---
title: "Spark Connector Integration Tests"
slug: "/spark-connector/spark-connector-integration-test"
keyword: "spark connector integration test"
license: "This software is licensed under the Apache License version 2."
---

## 概述

spark connector 中有两种类型的集成测试：像 `SparkXXCatalogIT` 这样的普通集成测试，以及 golden file 集成测试。

## 正常集成测试

常规集成测试主要用于测试元数据的正确性，已在 GitHub CI 中启用。你可以使用特定的 Spark 版本运行测试，例如：

```
./gradlew :spark-connector:spark-3.5:test --tests "org.apache.gravitino.spark.connector.integration.test.hive.SparkHiveCatalogIT35.testCreateHiveFormatPartitionTable"
```

每个版本模块都包含每个共享 IT 的自身子类，并以 Spark 次要版本命名，因此 Spark 4.0 的等价物是 `:spark-connector:spark-4.0:test --tests "...SparkHiveCatalogIT40.testCreateHiveFormatPartitionTable"`。

## 黄金文件集成测试

黄金文件集成测试主要是为了测试海量数据下 SQL 结果的正确性，它在 GitHub CI 中被禁用，你可以使用以下命令运行测试：

```
./gradlew :spark-connector:spark-3.5:test --tests  "org.apache.gravitino.spark.connector.integration.test.sql.SparkSQLRegressionTest35" -PenableSparkSQLITs
```

如果你想测试其他 Spark 版本，请更改 Spark 版本号。
如果你想更改测试行为，请修改 `spark-connector/spark-common/src/test/resources/spark-test.conf`。

| 配置项                         | 描述                                                                                                                                                                            | 默认值                                        | 必填 |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|----------|
| `gravitino.spark.test.dir`                 | Spark SQL 测试基础目录，包含 `test-sqls` 和 `data`。                                                                                                                           | `spark-connector/spark-common/src/test/resources/`   | No       |
| `gravitino.spark.test.sqls`                | 指定测试 SQL，使用目录指定一组 SQL，例如 `test-sqls/hive`，使用文件路径指定单个 SQL，例如 `test-sqls/hive/basic.sql`，使用 `,` 分隔多个部分 | 运行所有 SQL                                         | No       |
| `gravitino.spark.test.generateGoldenFiles` | 是否生成用于检查 SQL 结果正确性的 golden 文件                                                                                                | false                                                | No       |
| `gravitino.spark.test.metalake`            | 运行测试的 metalake 名称                                                                                                                                                      | `test`                                               | No       |
| `gravitino.spark.test.setupEnv`            | 是否设置 Gravitino 和 Hive 环境                                                                                                                                        | `false`                                              | No       |
| `gravitino.spark.test.uri`                 | Gravitino uri 地址，仅在 `gravitino.spark.test.setupEnv` 为 false 时可用                                                                                                    | http://127.0.0.1:8090                                | No       |
| `gravitino.spark.test.iceberg.warehouse`   | warehouse 位置，仅在 `gravitino.spark.test.setupEnv` 为 false 时可用                                                                                                   | hdfs://127.0.0.1:9000/user/hive/warehouse-spark-test | No       |

测试 SQL 文件默认位于 `spark-connector/spark-common/src/test/resources/` 中。共有三个目录：
- `hive`，针对 Hive catalog 的 SQL 测试。
- `lakehouse-iceberg`，针对 Iceberg catalog 的 SQL 测试。
- `tpcds`，针对 Hive catalog 中 `tpcds` 的 SQL 测试。

你可以创建一个简单的 SQL 文件，比如 `hive/catalog.sql`，程序将使用 `hive/catalog.sql.out` 检查输出。对于像 `tpcds` 这样的复杂情况，你可以在 `prepare.sql` 中做一些准备工作，比如建表和加载数据。
