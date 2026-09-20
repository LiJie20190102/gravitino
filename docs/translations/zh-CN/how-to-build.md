---
title: "Build Gravitino"
slug: "/how-to-build"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Gravitino 可以在 Linux 和 macOS 上原生从源码构建，并在 Windows 上通过 WSL 进行构建。以下部分涵盖了前提条件、服务器和连接器的快速入门构建步骤，以及 Windows 特定的设置步骤。

## 先决条件

+ Linux 或 macOS 操作系统
+ Git
+ 环境中已安装 Java Development Kit 版本 17，用于启动 Gradle
+ Python 3.10、3.11 或 3.12，用于构建 Gravitino Python 客户端。 
+ 可选：Docker，用于运行集成测试

:::info Please read the following notes before trying to build Gravitino.

+ Gravitino 运行 Gradle 至少需要 JDK17，因此你需要安装 JDK17 来启动构建环境。
+ Gravitino 本身支持使用 JDK 17 进行构建。Gravitino Trino 连接器使用 JDK17 进行构建（为避免在某些平台上出现与供应商相关的问题，建议在 macOS 上使用 Amazon Corretto OpenJDK 17 构建 Gravitino）。
你不必预装指定的 JDK 环境，因为 Gradle 会检测所需的 JDK 版本并自动下载。
+ Gravitino 使用 Gradle Java Toolchain 来检测和管理 JDK 版本，并通过运行 `./gradlew javaToolchains` 命令来检查已安装的 JDK。参见 [Gradle Java Toolchain](https://docs.gradle.org/current/userguide/toolchains.html#sec:java_toolchain)。
+ Gravitino 默认排除所有与 Docker 相关的测试。要运行与 Docker 相关的测试，请确保你的环境中已安装 Docker，并且 (1) 在 `gradle.properties` 文件中设置 `skipDockerTests=false`（或在命令中使用 `-PskipDockerTests=false`），或者 (2) 在 shell 中 `export SKIP_DOCKER_TESTS=false`。否则，所有需要 Docker 的测试都将被跳过。
+ macOS 使用 `docker-connector` 使 Gravitino Trino 连接器与 Docker for macOS 协同工作。有关更多详细信息，请参见 [docker-connector](https://github.com/wenjunxiao/mac-docker-connector)、`$GRAVITINO_HOME/dev/docker/tools/mac-docker-connector.sh` 和 `$GRAVITINO_HOME/dev/docker/tools/README.md`。
+ 你可以使用 OrbStack 作为 Docker for macOS 的替代品。参见 [OrbStack](https://orbstack.dev/)。使用 OrbStack，你可以运行 Gravitino 集成测试，而无需安装 `docker-connector`。
+ 根据你部署 Gravitino 的方式，与 Gravitino 结合使用的其他软件可能包含已知的安全漏洞。
:::

## 快速开始

1. 克隆 Gravitino 项目。

如果你想为这个开源项目做贡献，请先在 GitHub 上 fork 该项目。fork 之后，将 fork 后的项目 clone 到你的本地环境，进行你的修改，并提交一个 pull request (PR)。

   ```shell
   git clone git@github.com:apache/gravitino.git
   ```

2. 构建 Gravitino 项目。首次运行可能需要 15 分钟或更长时间。

   ```shell
   cd gravitino
   ./gradlew build
   ```

`./gradlew build` 命令构建所有 Gravitino 组件，包括 Gravitino 服务器、Java 和 Python 客户端、Trino 和 Spark 连接器等。

对于 Python 客户端，`./gradlew build` 命令默认使用 Python 3.12 构建 Python 客户端。如果你想使用 Python 3.10 或 3.11 进行构建，请在 `gradle.properties` 文件中将属性 `pythonVersion` 修改为 3.10 或 3.11，或者使用 `-P` 指定版本，如下所示：

   ```shell
   ./gradlew build -PpythonVersion=3.10
   ```

或者：

   ```shell
   ./gradlew build -PpythonVersion=3.11
   ```

或者：
    
   ```shell
   ./gradlew build -PpythonVersion=3.12
   ```

如果你不需要构建 Trino 连接器（例如，在没有 JDK 24 的机器上构建时），可以通过以下方式跳过：

   ```shell
   ./gradlew build -PskipTrinoConnector=true
   ```

如果你想单独构建一个模块，比如 Spark 连接器，你可以使用 Gradle 来构建一个具有特定名称的模块，如下所示：

   ```shell
   ./gradlew spark-connector:spark-runtime-3.5:build -PscalaVersion=2.12
   ```

这会在 `spark-connector/v3.5/spark-runtime/build/libs` 目录下创建 `gravitino-spark-connector-runtime-{sparkVersion}_{scalaVersion}-{version}.jar`。将 `2.12` 替换为 `2.13` 以针对不同的 Scala 版本进行构建。如果未指定 `-PscalaVersion`，则默认的 Scala 版本为 `2.12`。

对于 Spark 4，请将 `spark-runtime-3.5` 替换为 `spark-runtime-4.0`。Spark 4 仅支持 Scala 2.13，因此该模块会忽略 `-PscalaVersion` 并始终基于 2.13 进行构建。

  :::note
首次构建项目时，下载依赖项可能需要一段时间。
 
你可以添加 `-x test` 来跳过测试，使用 `./gradlew build -x test`。

构建的 Gravitino 库兼容 Java 17，并在 17 环境下进行了验证。无论构建项目时使用的是哪个 JDK 版本，请使用 Java 17 运行时来运行 Gravitino 服务器。

构建好的 jar 包位于模块的 `build/libs` 目录下。将它们发布到您的 Maven 仓库中，以便在您的项目中使用。
  :::

3. 获取 Gravitino 服务器二进制包。

   ```shell
   ./gradlew compileDistribution
   ```

   To skip compiling and packaging the Web UI artifacts, use:

   ```shell
   ./gradlew compileDistribution -PskipWebBuild=true
   ```

`compileDistribution` 命令会在 Gravitino 根目录下创建一个 `distribution` 目录。它包含两个子目录：`package` 和 `package-all`。这两个子目录的区别在于，`package` 是 **Gravitino 服务器发行包**，而 `package-all` 包含 `catalogs-contrib` 中的额外 catalog 以及 `package` 中的所有内容。
因此，如果你想使用 `catalogs-contrib` 中的 catalog，你应该使用 `package-all` 中的发行包。

  :::note
`./gradlew clean` 命令删除 `distribution` 目录。
  :::

4. 组装 Gravitino 服务器发行包。

   ```shell
   ./gradlew assembleDistribution
   ```

`assembleDistribution` 命令会在 `distribution` 目录下创建 `gravitino-{version}-bin.tar.gz`、`gravitino-{version}-bin.tar.gz.sha256`、`gravitino-{version}-bin-all.tar.gz` 和 `gravitino-{version}-bin-all.tar.gz.sha256`。
  
`gravitino-{version}-bin.tar.gz` 和 `gravitino-{version}-bin-all.tar.gz` 遵循与上一步中 `package` 和 `package-all` 相同的区分方式。

将这些部署到您的生产环境。

  :::note
`gravitino-{version}-bin.tar.gz` 文件是 Gravitino **服务器**发行包，而 `gravitino-{version}-bin.tar.gz.sha256` 文件是 Gravitino 服务器发行包的 sha256 校验和文件。
  :::

5. 组装 Gravitino Trino 连接器包

  ```shell
   ./gradlew assembleTrinoConnector
   ```

或

   ```shell
   ./gradlew assembleDistribution
   ```

这会创建 `gravitino-trino-connector-{version}.tar.gz` 和
`gravitino-trino-connector-{version}.tar.gz.sha256`，位于 `distribution` 目录下。你可以将其解压并部署到 Trino 中，以使用 Gravitino Trino 连接器。

6. 组装 Gravitino Iceberg REST 服务器包

  ```shell
   ./gradlew assembleIcebergRESTServer
   ```

这会在 `distribution` 目录下创建 `gravitino-iceberg-rest-server-{version}.tar.gz` 和 `gravitino-iceberg-rest-server-{version}.tar.gz.sha256`。你可以解压并部署它，以使用 Gravitino Iceberg REST 服务器。

## 在 Windows 上构建（使用 WSL）

### 下载 WSL (Ubuntu)

**在 Windows 上：**

有关安装，请参阅此指南：[WSL 安装指南](https://learn.microsoft.com/en-us/windows/wsl/install)

*注意：Gravitino 可以在 Ubuntu 22.04 上成功运行*

此步骤涉及设置您 Windows 计算机的 Windows Subsystem for Linux (WSL)。WSL 允许您与 Windows 并行运行 Linux 发行版，为开发提供类 Linux 环境。

### 更新软件包列表并安装必要的软件包

**在 Ubuntu (WSL)：**

```shell
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

更新软件包列表可确保您拥有关于最新版本软件包及其依赖项的最新信息。安装必要的软件包使您的系统能够安全地下载和管理额外软件。

### 下载并设置 Java SDK 17

**在 Ubuntu (WSL)：**

1. 使用任意编辑器编辑你的 `~/.bashrc` 文件。这里使用 `vim`：

   ```shell
   vim ~/.bashrc
   ```

2. 在文件末尾添加以下行。将 `/usr/lib/jvm/java-17-openjdk-amd64` 替换为您实际的 Java 安装路径：

   ```sh
   export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
   export PATH=$PATH:$JAVA_HOME/bin
   ```

3. 在 vim 中使用 `:wq` 保存并退出。

4. 运行 `source ~/.bashrc` 以更新你的 shell 会话的环境变量。

编辑 `~/.bashrc` 文件允许您设置在每个终端会话中可用的环境变量。设置 `JAVA_HOME` 并更新 `PATH` 可确保您的系统在开发时使用正确的 Java 版本。

### 安装 Docker

**在 Ubuntu (WSL)：**

```shell
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce
sudo service docker start
sudo docker run hello-world
sudo usermod -aG docker $USER
```

这些命令使用已签名的 `apt` 密钥环而非已弃用的 `apt-key` 命令来安装 Docker。运行 `hello-world` 可验证安装。将您的用户添加到 Docker 组后，即可在不使用 `sudo` 的情况下运行 Docker 命令。

### 安装 Python 3.11

**在 Ubuntu (WSL)：**

```shell
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
python3.11 --version
```

这些命令添加了一个提供最新 Python 版本的仓库，并安装 Python 3.11。

### 下载 Apache Gravitino 项目到 WSL

**在 Ubuntu (WSL)：**

```shell
git clone https://github.com/apache/gravitino.git
cd gravitino
./gradlew compileDistribution -x test
cd distribution/package/
./bin/gravitino.sh start
```

访问 [http://localhost:8090](http://localhost:8090)

构建 Gravitino 项目会编译必要的组件，启动服务器后即可在浏览器中访问该应用程序。

请参阅 [CONTRIBUTING.md](https://github.com/apache/gravitino/blob/main/CONTRIBUTING.md) 了解在 Windows 上使用 VSCode 或 IntelliJ 运行该项目的说明。

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=HowToBuild" alt="" />
