---
slug: /lance-rest-integration
keywords:
- lance
- lance-rest
- spark
- ray
- integration
license: This software is licensed under the Apache License version 2.
---
## 概述

本指南提供全面的说明，介绍如何将 Apache Gravitino Lance REST 服务与支持 Lance 格式的数据处理引擎集成，包括通过 [Lance Spark 连接器](https://lance.org/integrations/spark/) 集成的 Apache Spark，以及通过 [Lance Ray 连接器](https://lance.org/integrations/ray/) 集成的 Ray。

本文档假定您已熟悉 [Lance REST 服务](../../lance-rest-service) 文档中所述的 Lance REST 服务设置。

## 兼容性矩阵

下表列出了 Gravitino 版本与 Lance 连接器版本之间经过测试的兼容性：

| Gravitino 版本（Lance REST） | 支持的 lance-spark 版本 | 支持的 lance-ray 版本                  |
| ------------------------------ | ------------------------------ | --------------------------------------------- |
| 1.1.1 - 1.2.1                  | 0.0.10 - 0.0.15                | 0.0.6 - 0.0.8                                 |
| 1.3.0                          | 0.2.0, 0.4.0, 0.5.1            | 0.3.0 - 0.4.2（0.2.0 条件支持） |

:::note
- 这些版本条目显示了预期可以协同工作的版本。
- 对于 Gravitino 1.3.0，明确验证过的发布版本是
  `lance-spark`（0.2.0、0.4.0、0.5.1）和 `lance-ray`（0.3.0、0.4.2）。`lance-ray`
  0.2.0 仅在满足下述条件时受到条件支持。

- **`lance-spark` 0.1.0 和 0.1.1 在 Gravitino 1.3.0 上不受支持。**
  这些 bundle 通过调用旧版
  `POST /lance/v1/table/{id}/create-empty` 端点来创建表，而 1.3.0 不再
  暴露该端点——表声明路径已合并到
  `POST /lance/v1/table/{id}/declare`（`LanceTableOperations#declareTable`）
  当已弃用的 `createEmptyTable` API 在
  `lance-namespace-core` 0.7.5 升级期间被移除时。在 1.3.0 上运行 0.1.x 会在每个表创建流程中
  表现为 `404 Not Found`；少数
  仅列表/描述测试仍可工作，但任何写入路径都会失败。
- **`lance-ray` 0.1.0 在 Gravitino 1.3.0 上不受支持。** 它暴露
  `write_lance(... namespace=<LanceNamespace>)`，而 0.2.0+ 测试路径
  使用新的 `write_lance(... namespace_impl="rest",
  namespace_properties={...})` 签名。在 0.1.0 上调用它会引发
  `TypeError: write_lance() got an unexpected keyword argument 'namespace_impl'`。
- **`lance-ray` 0.2.0 在 Gravitino 1.3.0 上受到条件支持。** 它
  匹配新签名，但在运行时
  `lance_ray.utils.create_storage_options_provider` 会执行
  `from lance import LanceNamespaceStorageOptionsProvider`，而该名称不再
  存在于 `lance-namespace==0.7.5` 拉取的 `pylance` 6.0.0 wheel 中，
  从而引发 `ImportError: cannot import name
  'LanceNamespaceStorageOptionsProvider' from 'lance'`。您可以使用
  将 `pylance` 固定到 3.x 或 4.x，以在 Gravitino 1.3.0 上使用 `lance-ray` 0.2.0。
- 在生产环境使用之前，请先在您自己的环境中测试确切的连接器版本。
- Lance 生态系统变化很快，因此某些版本可能会引入破坏性变更。
:::

## 格式边界

Lance REST 服务是一个 Lance 表命名空间，即使其元数据后端是
与格式无关的 Generic Catalog。因此，REST 表操作会在返回 Lance 元数据或应用表变更之前，
验证存储的 `format` 属性。

当某个标识符被已知的非 Lance 表占用时，直接的 Lance 表操作会失败，
并返回 HTTP `400` 和 `INVALID_INPUT` 错误。`TableExists` 将该条目视为不存在，并
返回正常的表未找到响应。底层 Generic Catalog 元数据和存储
位置保持不变。

同样的边界也适用于针对现有实体、通过 Lance
委托器执行的创建请求：

| 请求模式         | 现有非 Lance 实体                            |
| -------------------- | ---------------------------------------------------- |
| `CREATE`             | `409` 冲突，与任何现有表名一样       |
| `EXIST_OK`           | `400 INVALID_INPUT`                                  |
| `OVERWRITE`          | `400 INVALID_INPUT`；元数据和数据会保留 |
| 注册 `OVERWRITE` | `400 INVALID_INPUT`；元数据和数据会保留 |

验证在正常授权检查之后执行。它不会转换现有的
Generic Catalog 未知格式加载错误，也不会改变 Generic Catalog 与格式无关的
`ListTables` 行为。

### 在本地复现该矩阵

两个连接器都附带多版本集成测试驱动程序，因此
无需临时编写脚本即可重新验证（并扩展）该矩阵：

```bash
# lance-spark — 针对每个 bundle 版本运行一次 LanceSparkRESTServiceIT。
# 默认列表有意省略了 0.1.0 / 0.1.1：这些 bundle 会调用
# 已移除的 /create-empty 端点，并且针对 1.3.0+ 会以 404 失败。
./gradlew :lance:lance-rest-server:lanceSparkMatrixTest \
    -PlanceSparkBundleVersions=0.2.0,0.4.0,0.5.1 \
    -PskipDockerTests=true
# 每个版本的 JUnit 报告存放在
# lance/lance-rest-server/build/reports/lance-spark-matrix/<version>/。

# lance-ray — 为每个版本在以下位置准备一个 venv：
# clients/client-python/build/lance-ray-matrix/.venv-<version>/，并运行
# tests/integration/test_lance_ray.py 对每个版本运行。Gradle wrapper
# 下方的会自动启动/停止 Gravitino。
./gradlew :clients:client-python:lanceRayMatrixTest \
    -PlanceRayVersions=0.4.2,0.3.0
```

### 原因

Lance 生态系统正在积极开发中，API 和功能频繁更新。Gravitino 的 Lance REST 服务依赖特定的连接器行为来确保可靠运行。使用不兼容的版本可能会导致：

- 运行时错误或异常
- 数据损坏或丢失
- 查询执行中的意外行为
- 性能下降

## 先决条件

在继续之前，请确保满足以下要求：

1. **Gravitino Server**：一个正在运行且已启用 Lance REST 服务的 Gravitino 服务器实例
    - 默认端点：`http://localhost:9101/lance`

2. **Lance Catalog**：使用以下任一方式在 Gravitino 中创建的 Lance catalog：
    - Lance REST namespace API（`CreateNamespace` 操作 - 请参阅 [Lance REST 服务文档](./lance-rest-service.md)
    - Gravitino REST API，更多信息请参阅 [lakehouse-generic-catalog](./lakehouse-generic-catalog.md)
    - Catalog 名称示例：`lance_catalog`

3. **Lance Spark Bundle**（用于 Spark 集成）：
    - 下载与您的 Apache Spark 版本匹配的 `lance-spark` bundle JAR
    - 记录用于配置的绝对文件路径

4. **Python 依赖项**：
    - 用于 Spark 集成：`pyspark`
    - 用于 Ray 集成：`ray`、`lance-namespace`、`lance-ray`

## 认证与授权

要进行按用户进行的元数据授权，请将引擎连接到辅助 Lance REST 服务，并设置
`gravitino.authorization.enable=true`。配置每个引擎的 REST 客户端，使其在每个命名空间和表请求上
发送调用方的 `Authorization` 头。如果该客户端版本支持，
`X-Gravitino-Active-Roles` 可以限制活动角色。请参阅
[Lance REST 认证与权限矩阵](./lance-rest-service.md#authentication-and-authorization)。

例如，在使用仅用于开发的 `simple` 认证时，此请求仅列出
`user1` 可以访问的表（不会验证密码）：

```shell
curl --user 'user1:unused' \
  -H 'X-Gravitino-Active-Roles: ALL' \
  'http://localhost:9101/lance/v1/namespace/lance_catalog.sales/table/list?delimiter=.'
```

连接器头配置取决于连接器版本。以下 Spark 和 Ray 示例
省略了凭据，并假定使用默认的 simple 认证设置；在辅助模式下，
此类请求使用配置的 Lance 服务身份。它们并不演示按用户
访问控制。在独立模式下，即使引擎提供自己的传入凭据，所有发往 Gravitino 的元数据请求都使用后端服务
身份。

在创建之前进行探测的引擎需要相应的创建权限。读取表
元数据需要具有父级访问权限的 `SELECT_TABLE` 或 `MODIFY_TABLE`，而覆盖需要
`MODIFY_TABLE`，删除需要所有权。元数据授权并不授权直接
读取或写入对象存储：请独立配置存储访问。Lance REST 响应
可以返回在 catalog 或表上配置的共享存储凭据；它不会颁发
按用户限定范围的存储凭据。

### 在本地验证认证与授权

HTTP 集成测试套件会启动带有 Lance 辅助服务的 Gravitino，并检验
调用方身份、服务身份回退、活动角色、命名空间和表权限、
过滤后的列表、被拒绝的变更，以及拒绝非空 Arrow 创建且不产生副作用。
它们还会在单独的 JVM 中通过生产入口点启动独立 Lance REST，以验证
其出站服务身份，以及后端授权拒绝通过 Gravitino
HTTP API 的传播。

```shell
./gradlew :lance:lance-rest-server:test \
  --tests '*LanceRESTServiceAuthIT' \
  --tests '*LanceNamespaceAuthorizationIT' \
  --tests '*LanceTableAuthorizationIT' \
  -PskipDockerTests=true
```

这些测试套件使用 `simple` 认证和本地存储。它们不会验证外部
OAuth2/Kerberos 提供程序或对象存储访问策略。

## Spark 集成

### 配置

以下示例演示如何配置 PySpark 会话以与 Lance REST 交互，并使用 Spark SQL 执行表操作。

```python
from pyspark.sql import SparkSession
import os
import logging

# 配置日志记录以进行调试
logging.basicConfig(level=logging.INFO)

# 配置 Spark 以使用 lance-spark 捆绑包
# 将 /path/to/lance-spark-bundle-3.5_2.12-X.X.XX.jar 替换为您实际的 JAR 路径和版本；
# 请参阅兼容性矩阵以了解支持的 lance-spark 版本。
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--jars /path/to/lance-spark-bundle-3.5_2.12-0.4.0.jar "
    "--conf \"spark.driver.extraJavaOptions=--add-opens=java.base/sun.nio.ch=ALL-UNNAMED\" "
    "--conf \"spark.executor.extraJavaOptions=--add-opens=java.base/sun.nio.ch=ALL-UNNAMED\" "
    "--master local[1] pyspark-shell"
)

# 使用 Lance REST 目录配置初始化 Spark 会话
# 注意：在运行此代码之前，目录 "lance_catalog" 必须存在于 Gravitino 中，您可以创建
# 它，通过 Lance REST API `CreateNamespace` 或 Gravitino REST API `CreateCatalog`。
spark = SparkSession.builder \
    .appName("lance_rest_integration") \
    .config("spark.sql.catalog.lance", "org.lance.spark.LanceNamespaceSparkCatalog") \
    .config("spark.sql.catalog.lance.impl", "rest") \
    .config("spark.sql.catalog.lance.uri", "http://localhost:9101/lance") \
    .config("spark.sql.catalog.lance.parent", "lance_catalog") \
    .config("spark.sql.defaultCatalog", "lance") \
    .getOrCreate()

# 启用调试日志记录以进行故障排除
spark.sparkContext.setLogLevel("DEBUG")

# 创建 schema（数据库）
spark.sql("CREATE DATABASE IF NOT EXISTS sales")

# 创建具有显式位置的 Lance 表
spark.sql("""
    CREATE TABLE sales.orders (
        id INT,
        score FLOAT
    )
    USING lance
    LOCATION '/tmp/sales/orders.lance/'
    TBLPROPERTIES ('format' = 'lance')
""")

# 插入示例数据
spark.sql("INSERT INTO sales.orders VALUES (1, 1.1)")

# 查询数据
spark.sql("SELECT * FROM sales.orders").show()
```

### 存储位置配置

`CREATE TABLE` 语句中的 `LOCATION` 子句是可选的。省略时，lance-spark 会根据 catalog 属性自动确定合适的存储位置。
有关位置解析逻辑的详细信息，请参阅 [Lakehouse Generic Catalog 文档](./lakehouse-generic-catalog.md#key-property-location)。

对于由 Gravitino 管理的 Lance catalog，请将存储配置放入 Gravitino catalog 属性中，这样 Spark 无需重复配置。

例如，使用 catalog 级别的 Lance 存储属性创建 Gravitino catalog：

```shell
curl -X POST -H "Accept: application/vnd.gravitino.v1+json" \
  -H "Content-Type: application/json" \
  -d '{
  "name": "lance_catalog",
  "type": "RELATIONAL",
  "provider": "lakehouse-generic",
  "comment": "catalog for Lance tables on MinIO",
  "properties": {
    "location": "s3://bucket/tmp",
    "lance.storage.endpoint": "http://minio:9000",
    "lance.storage.access_key_id": "ak",
    "lance.storage.secret_access_key": "sk",
    "lance.storage.allow_http": "true",
    "lance.storage.region": "us-east-1"
  }
}' http://localhost:8090/api/metalakes/test/catalogs
```

```python
spark.sql("""
    CREATE TABLE sales.orders (
        id INT,
        score FLOAT
    )
    USING lance
    LOCATION 's3://bucket/tmp/sales/orders.lance/'
    TBLPROPERTIES ('format' = 'lance')
""")
```

如果您需要按表覆盖，仍然支持 `lance.storage.*` 表属性，并且其优先级高于 catalog 默认值。

## Ray 集成

### 安装

安装所需的 Ray 集成包：

```shell
pip install lance-ray
```

:::info
- 如果尚未安装，Ray 会自动安装
- 对于 Gravitino 1.3.0，请使用与
  服务端 `lance-namespace-core` 0.7.5 或更新版本兼容的 `lance-namespace` 客户端。
- 在部署前，确保您的环境中的 Ray 版本兼容性
:::

### 示例

以下示例演示如何使用 Ray 通过 Lance REST namespace 读取和写入 Lance 数据集：

```python
import ray
import lance_namespace as ln
from lance_ray import read_lance, write_lance

# 初始化 Ray 运行时
ray.init()

# 连接到 Lance REST 命名空间
namespace = ln.connect("rest", {"uri":  "http://localhost:9101/lance"})

# 创建示例数据集
data = ray.data.range(1000).map(
    lambda row: {"id": row["id"], "value": row["id"] * 2}
)

# 将数据集写入 Lance 表
# 注意：目录 "lance_catalog" 和模式 "sales" 都必须存在于 Gravitino 中，你可以创建
# 它们可以通过 Lance REST API `CreateNamespace` 或 Gravitino REST API `CreateCatalog` 和 `CreateSchema` 来创建。
write_lance(
    data, 
    namespace=namespace, 
    table_id=["lance_catalog", "sales", "orders"]
)

# 从 Lance 表读取数据集
ray_dataset = read_lance(
    namespace=namespace, 
    table_id=["lance_catalog", "sales", "orders"]
)

# 执行过滤操作
result = ray_dataset.filter(lambda row: row["value"] < 100).count()
print(f"Filtered row count: {result}")
```

## 其他引擎

Lance REST 服务与支持 Lance 格式的其他数据处理引擎兼容，包括：

- **DuckDB**：用于分析型 SQL 查询
- **Pandas**：用于基于 Python 的数据操作
- **DataFusion**：用于基于 Rust 的查询执行

注意：这三个引擎目前尚不原生支持 Lance REST，但仍可通过从 Lance REST 服务获取的表位置路径与 Lance 数据集交互。

有关特定引擎的集成说明，请参阅 [Lance 集成文档](https://lance.org/integrations)。

### 通用集成模式

大多数兼容 Lance 的引擎都遵循以下通用模式：

1. 建立到 Lance REST 服务端点的连接
2. 使用适当的凭据进行认证
3. 使用分层命名空间结构引用表
4. 使用引擎原生 API 执行读/写操作

有关详细配置参数和代码示例，请参阅各引擎的特定文档。

## 相关

- [Lance REST 服务文档](../../lance-rest-service)
- [Lance 格式规范](https://lance.org/)
- [Apache Gravitino 文档](https://gravitino.apache.org/)
- [Lakehouse Generic Catalog 指南](./lakehouse-generic-catalog.md)