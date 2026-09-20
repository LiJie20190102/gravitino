---
title: "Test Gravitino"
slug: "/how-to-test"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino 有两种类型的测试：

- 单元测试，专注于特定类、模块或组件的功能。
- 集成测试，覆盖整个系统的端到端测试。

:::note before test
* 如果你想运行完整的集成测试套件，你需要在你的
环境中安装 Docker。
* 参考[如何构建 Gravitino](./how-to-build.md) 以确保你拥有
一个准备就绪的构建环境。
* 使用 [OrbStack](https://orbstack.dev/) 替代 Docker Desktop
在 macOS 上。OrbStack 会自动配置 Docker 容器之间的网络。
* 如果你正在使用 macOS 版的 Docker Desktop，在运行测试之前启动
[mac-docker-connector](https://github.com/wenjunxiao/mac-docker-connector)。
阅读 `$GRAVITINO_HOME/dev/docker/tools/README.md` 和
`$GRAVITINO_HOME/dev/docker/tools/mac-docker-connector.sh` 以获取更多详细信息。
:::

## 运行单元测试

要运行单元测试，请运行以下命令：

```shell

./gradlew test -PskipITs
```

此命令运行所有单元测试并跳过集成测试。

## 运行集成测试

Gravitino 有两种运行集成测试的模式：默认的 `embedded` 模式和 `deploy` 模式。

* 在 `embedded` 模式下，集成测试会启动一个内嵌的 `MiniGravitino` 服务器
在与集成测试相同的进程内运行集成测试。
* 在 `deploy` 模式下，你必须事先构建（`./gradlew compileDistribution`）一个 Gravitino 二进制包。该
集成测试会启动并连接到本地的 Gravitino 服务器来运行集成
测试。

### 在嵌入式模式下运行集成测试

1. 运行 `./gradlew build -x test` 命令以构建 Gravitino 项目。

2. 使用 `./gradlew test [--rerun-tasks] -PskipTests -PtestMode=embedded` 命令来运行
集成测试。

:::note
运行 `./gradlew build` 命令会触发构建，并在嵌入式模式下运行集成测试。
:::

### 部署服务器并在部署模式下运行集成测试

要在本地部署 Gravitino 服务器以运行集成测试，请按照以下步骤操作：

1. 运行 `./gradlew build -x test` 命令来构建 Gravitino 项目。
2. 使用 `./gradlew compileDistribution` 命令来编译并打包 Gravitino 项目，
在 `distribution` 目录中。
4. 使用 `./gradlew test [--rerun-tasks] -PskipTests -PtestMode=deploy` 命令来运行
`distribution` 目录中的集成测试。
4. 使用 `bash trino-connector/integration-test/trino-test-tools/trino_test.sh` 命令来运行所有
`trino-connector/integration-test/src/test/resources/trino-ci-testset/testsets` 目录中的 Trino 测试集。
指定 `--trino_worker_num` 参数以使 Trino 测试集在分布式环境中运行。
指定 `--trino_version` 参数以使 Trino 测试集在特定的 trino 版本下运行。
指定 `--trino_connector_dir` 参数以使用位于 `gravitino-trino-connector` 插件目录中的 JAR 文件来运行 Trino 测试。

## 跳过测试

* 使用 `./gradlew build -PskipTests` 命令跳过单元测试。
* 使用 `./gradlew build -PskipITs` 命令跳过集成测试。
* 使用 `./gradlew build -x :web:integration-test:test` 命令跳过 Web 前端集成测试。
* 使用 `./gradlew build -x test` 或 `./gradlew build -PskipTests -PskipITs` 命令同时跳过单元测试和集成测试。

## 配置集成测试参数

### `DISPLAY_WEBPAGE_IN_TESTING`

默认情况下，在运行集成测试时，Gravitino Web 前端页面不会弹出。
如果你想在集成测试期间显示 Web 前端页面，可以在 build.gradle.kts 文件的 `setIntegrationTestEnvironment` 中设置 `DISPLAY_WEBPAGE_IN_TESTING` 环境变量。
例如：
```param.environment("DISPLAY_WEBPAGE_IN_TESTING", true)```

## Docker Test Environment

Some integration test cases depend on the Gravitino CI Docker image.

If an integration test relies on the specific Gravitino CI Docker image,
set the `@tag(gravitino-docker-test)` annotation in the test class.
For example, the `integration-test/src/test/.../CatalogHiveIT.java` test needs to connect to
the `apache/gravitino-ci:hive-{hive-version}` Docker container for testing the Hive data source.
Therefore, it should have the following `@tag` annotation:`@tag(gravitino-docker-test)`. This annotation
helps identify the specific Docker container required for the integration test.

For example:

```java
@Tag("gravitino-docker-test")
public class CatalogHiveIT extends AbstractIT {
...
}
```

## Run All Integration Tests

:::note
* Make sure that the `Docker server` is running before running all the
  integration tests. Otherwise, it only runs the integration tests without the `gravitino-docker-test` tag.
* To run Docker-related tests, make sure you have installed Docker in your environment and either
   set skipDockerTests=false in the gradle.properties file (or use `-PskipDockerTests=false` in the command) or
  (2) export SKIP_DOCKER_TESTS=false in shell. Otherwise, all tests requiring Docker will be skipped.
* On macOS, be sure to run the `${GRAVITINO_HOME}/dev/docker/tools/mac-docker-connector.sh`
  script before running the integration tests; or make sure that
  [OrbStack](https://orbstack.dev/) is running.
:::

When integration tests run, they check the whole environment and output the status of the
required environment, for example:

```text
------------------ 检查 Docker 环境 ---------------------
Docker 服务器状态 ............................................ [running]
mac-docker-connector 状态 ..................................... [stop]
OrbStack 状态 ................................................. [yes]
使用 Gravitino IT Docker 容器运行所有集成测试。 [deploy test]
-----------------------------------------------------------------
```

Complete integration tests only run when all the required environments are met. Otherwise,
only parts of them without the `gravitino-docker-test` tag run.

## Debug Server and Integration Tests in Embedded Mode

By default, the integration tests run in the embedded mode, in which `MiniGravitino` starts in the
same process. Debugging `MiniGravitino` is simple and easy, you can modify any code in the
Gravitino project and set breakpoints anywhere.

## Debug Server and Integration Tests in Deploy Mode

This mode is closer to the actual environment, but more complex to debug. To debug the Gravitino server code, follow these steps:

* Run the `./gradlew build -x test` command to build the Gravitino project.
* Use the `./gradlew compileDistribution` command to republish the packaged project in the `distribution` directory.
* If you are only debugging integration test codes, You don't have to do any setup to debug directly.
* If you need to debug Gravitino server codes, follow these steps:
  * Enable the `GRAVITINO_DEBUG_OPTS` environment variable in the
  `distribution/package/conf/gravitino-env.sh` file to enable remote JVM debugging.
  * Manually start the Gravitino server using the `./distribution/package/bin/gravitino.sh
  start` command.
  * Select the `gravitino.server.main` module classpath in the `Remote JVM Debug` to attach the
  Gravitino server process and debug it.

## Run on GitHub Actions

* GitHub Actions automatically run integration tests in the embedded and deploy modes when you
  submit a pull request.
* View the test results in the `Actions` tab of the pull request page.
* Run the integration tests in several steps:
  * The Gravitino integration tests pull the CI Docker image from the Docker Hub repository. This step typically takes around 15 seconds.
  * The Gravitino project compiles and packages in the `distribution` directory using the `./gradlew compileDistribution` command.
  * Run the `./gradlew test -PtestMode=[embedded|deploy]` command.

## Test Failure and Test Logs

If a test fails, you can retrieve valuable information from the logs and test reports. Test reports are in the `./build/reports` directory. The integration test logs are in the `./integrate-test/build` directory. In deploy mode, Gravitino server logs are in the `./distribution/package/logs/` directory. 

In the event of a test failure within the GitHub workflow, the system generates archived logs and test reports. To obtain the archive, follow these steps:

1. Click the `detail` link associated with the failed integration test in the pull request. This redirects you to the job page.

   ![pr page Image](assets/test-fail-pr.png)

2. On the job page, locate the `Summary` button on the left-hand side and click it to access the workflow summary page.

   ![job page Image](assets/test-fail-job.png)

3. Look for the Artifacts item on the summary page and download the archive from there.

   ![summary page Image](assets/test-fail-summary.png)

4. You can also add the tag `upload log` to your PR to upload the logs to the PR page. in this case, no matter the CI pipeline status, the logs will be uploaded to the PR page.
   ![upload log](assets/upload-log-tag.png)
