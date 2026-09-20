---
title: "Python Client"
slug: "/how-to-use-gravitino-python-client"
date: 2024-05-09
keyword: "Gravitino Python client"
license: "This software is licensed under the Apache License version 2."
---
## 简介

Apache Gravitino 是一个高性能、地理分布的联邦式元数据湖。
它直接管理不同来源、类型和区域中的元数据，同时为用户提供
面向数据和 AI 资产的统一元数据访问。

Gravitino Python 客户端帮助数据科学家使用 Python 语言轻松管理元数据。

![gravitino-python-client-introduction](./assets/gravitino-python-client-introduction.png)

## 用法

在 Spark、PyTorch、Tensorflow、Ray 和 Python 环境中使用 Gravitino Python 客户端库。

首先，你必须搭建并运行 Gravitino 服务器，你可以参考文档
[如何安装 Gravitino](./how-to-install.md) 来从源代码构建 Gravitino 服务器并
将其安装到本地。

### Python 客户端 API

```shell
pip install apache-gravitino
```

1. [使用 Gravitino Python API 管理 metalake](./manage-metalake-using-gravitino.md?language=python)
2. [使用 Gravitino Python API 管理 fileset 元数据](./manage-fileset-metadata-using-gravitino.md?language=python)

### 文件集示例

我们提供了一个 playground 环境来帮助您快速了解如何使用 Gravitino Python
客户端，通过 Gravitino 中的 Fileset 来管理 HDFS 上的非表格式数据。您可以参考
文档[如何使用 playground](./how-to-use-the-playground.md)
在您的本地 Docker 环境中启动 Gravitino 服务器、HDFS 和 Jupyter notebook 环境。

等待 playground Docker 环境启动，您可以直接打开
`http://localhost:18888/lab/tree/gravitino-fileset-example.ipynb`，并在浏览器中运行示例。

[gravitino-fileset-example](https://github.com/apache/gravitino-playground/blob/main/init/jupyter/gravitino-fileset-example.ipynb)
包含以下代码片段：

1. 安装 HDFS Python 客户端。
2. 创建一个 HDFS 客户端以连接 HDFS 并执行一些测试操作。
3. 安装 Gravitino Python 客户端。
4. 初始化 Gravitino 管理员客户端并创建一个 Gravitino metalake。
5. 初始化 Gravitino 客户端并列出 metalakes。
6. 创建一个 Gravitino `Catalog`，指定 `type` 为 `Catalog.Type.FILESET`，且 `provider` 为
[fileset](./fileset-catalog.md)
8. 创建一个 Gravitino `Schema`，其 `location` 指向 HDFS 路径，并使用 `hdfs client`
检查 schema location 是否在 HDFS 中成功创建。
8. 创建一个 `Fileset`，其 `type` 为 [Fileset.Type.MANAGED](./manage-fileset-metadata-using-gravitino.md#fileset-operations)，
使用 `hdfs client` 检查 fileset location 是否在 HDFS 中成功创建。
9. 删除此 `Fileset.Type.MANAGED` 类型的 fileset，并检查 fileset location 是否
在 HDFS 中被成功删除。
10. 创建一个 `Fileset`，其 `type` 为 [Fileset.Type.EXTERNAL](./manage-fileset-metadata-using-gravitino.md#fileset-operations)
且 `location` 指向已存在的 HDFS 路径
11. 删除此 `Fileset.Type.EXTERNAL` 类型的 fileset，并检查 fileset location 是否
未在 HDFS 中被删除。

## Python 客户端开发

使用任意 IDE 开发 Gravitino Python 客户端。直接在 IDE 中打开 client-python 模块项目。

### 先决条件

+ Python 3.10+
+ 参考[如何构建 Gravitino](./how-to-build.md#prerequisites) 以准备好必要的构建
环境，以便进行构建。

### 构建和测试

1. 克隆 Gravitino 项目。

    ```shell
    git clone git@github.com:apache/gravitino.git
    ```

2. 构建 Gravitino Python 客户端模块

    ```shell
    # Default Python version is 3.12
    ./gradlew :clients:client-python:build
    # If you want to build Python client with specific Python version,
    # add `-PpythonVersion` with version number:
    ./gradlew :clients:client-python:build -PpythonVersion=3.11
    ```
 
3. 运行单元测试

    ```shell
    ./gradlew :clients:client-python:test -PskipITs
    ```

4. 运行集成测试

因为 Python 客户端连接到 Gravitino Server 来运行集成测试，
所以它会自动运行 `./gradlew compileDistribution -x test` 命令来编译
`distribution` 目录中的 Gravitino 项目。当你通过 Gradle
命令或 IDE 运行集成测试时，Gravitino 集成测试框架（`integration_test_env.py`）
将自动启动和停止 Gravitino server。

    ```shell
    ./gradlew :clients:client-python:test
    ```

5. 分发 Gravitino Python 客户端模块

    ```shell
    ./gradlew :clients:client-python:distribution
    ```

6. 部署 Gravitino Python 客户端到 https://pypi.org/project/apache-gravitino/

    ```shell
    ./gradlew :clients:client-python:deploy
    ```
   
### IDE 特定设置

#### JetBrains IntelliJ IDEA

我们使用 Conda 环境来管理 Python 环境，要配置 Python
SDK，您需要：

1. 确保你已安装 [Python Plugin](https://plugins.jetbrains.com/plugin/631-python)。
2. 确保你已按照 [Build and Test](#build-and-test) 中的步骤构建 python 模块。
3. 确保你位于 Gravitino Git 仓库的根目录。
4. 通过执行此命令找到 conda 可执行文件

   ```shell
   find $(pwd)/.gradle/python/*/Miniforge3/bin/conda
   
   # example output
   /Users/YOUR_USER_NAME/gravitino/.gradle/python/MacOSX/Miniforge3/bin/conda
   ```

5. 使用此命令查找 Python 解释器：

   ```shell
   find $(pwd)/.gradle/python/*/Miniforge3/envs/*/bin/python
   
   # example output
   /Users/YOUR_USER_NAME/gravitino/.gradle/python/MacOSX/Miniforge3/envs/python-3.12/bin/python
   ```

6. 按照[创建 conda 环境](https://www.jetbrains.com/help/idea/configuring-python-sdk.html#gdizlj_44)中的步骤操作，
并在第 5 步选择[现有 conda 环境](https://www.jetbrains.com/help/idea/configuring-python-sdk.html#existing-conda-environment)

7. 将第 4 步的输出填入 *Conda executable* 字段，第 5 步的输出填入 *Interpreter* 字段。
![配置 conda_env](./assets/configure-conda-env.png)
你会看到添加了一个新的 Python SDK，并且其中安装了一些包。
![添加 Platform SDK](./assets/add-platform-sdk.png)

8. 将 `clients/client-python` 模块 sdk 设置为我们在上一步中设置的 sdk。
![配置 python 模块 sdk](./assets/configure-python-module-sdk.png)

9. 完成！现在，打开任意 python 文件，开始开发 Gravitino Python Client。

##### 在 IntelliJ IDEA 中运行集成测试

因为集成测试需要 Gravitino Java 发行版，所以你无法使用 IntelliJ 运行测试
[运行测试按钮](https://www.jetbrains.com/help/idea/performing-tests.html)，
请使用 [Gradle 插件](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin.html) 执行此 gradle 任务
或者在命令行中运行集成测试。

```shell
./gradlew clients:client-python:integrationTest
```

或者，你会看到如下错误：

```shell
...
ERROR:tests.integration.integration_test_env:Gravitino Python client integration test must configure `GRAVITINO_HOME`

Process finished with exit code 0
```

## 资源

+ 官方网站 https://gravitino.apache.org/
+ GitHub 项目主页：https://github.com/apache/gravitino/
+ Docker 演练场：https://github.com/apache/gravitino-playground
+ 用户文档：https://gravitino.apache.org/docs/
+ Slack 社区：[https://the-asf.slack.com#gravitino](https://the-asf.slack.com/archives/C078RESTT19)

## 许可证

Gravitino 遵循 Apache License Version 2.0 许可证，详情请参阅 [LICENSE](https://github.com/apache/gravitino/blob/main/LICENSE)。

