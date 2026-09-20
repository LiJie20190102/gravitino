---
title: "Trino Connector Development"
slug: "/trino-connector/development"
keyword: "gravitino connector development"
license: "This software is licensed under the Apache License version 2."
---

## 简介

本文档将指导您在本地开发 Apache Gravitino Trino 连接器。

## 多版本架构

Gravitino Trino 连接器支持多个 Trino 版本（见[需求](requirements.md)）。源代码被组织成一个共享基础模块和几个版本分段模块：

```text
trino-connector/
├── trino-connector/              # Shared base source code
│   └── src/main/java/            # Common implementation used by all versions
├── trino-connector-440-445/      # Version-specific adapters for Trino 440-445
│   └── src/main/java/
├── trino-connector-446-451/      # Version-specific adapters for Trino 446-451
│   └── src/main/java/
├── trino-connector-452-468/      # Version-specific adapters for Trino 452-468
│   └── src/main/java/
├── trino-connector-469-472/      # Version-specific adapters for Trino 469-472
│   └── src/main/java/
├── trino-connector-473-478/      # Version-specific adapters for Trino 473-478
│   └── src/main/java/
└── integration-test/             # Integration tests
```

每个版本分段模块通过 Gradle `sourceSets` 包含共享的基础源代码，并添加特定于版本的适配器类（例如，`GravitinoConnector469.java`、`GravitinoPlugin469.java`）以处理不同版本间 Trino SPI 的差异。

在 Trino 项目中针对特定 Trino 版本进行开发时，你需要在 Maven `pom.xml` 中将共享基础源码和匹配的版本片段源码**同时**作为源码目录包含在内。

## 先决条件

在开始之前，请确保满足以下条件：

1. 在本地启动 Gravitino 服务器。有关更多信息，请参阅[如何安装](../how-to-install.md)。
2. 在 Gravitino 服务器中创建目录。有关更多信息，请参阅[Gravitino 元数据管理](../manage-relational-metadata-using-gravitino.md)。例如，创建一个 MySQL 目录：

```curl
curl -X POST -H "Content-Type: application/json" -d '{"name":"test","comment":"comment","properties":{}}' http://localhost:8090/api/metalakes

curl -X POST -H "Content-Type: application/json" -d '{"name":"mysql_catalog3","type":"RELATIONAL","comment":"comment","provider":"jdbc-mysql", "properties":{
  "jdbc-url": "jdbc:mysql://127.0.0.1:3306?useSSL=false&allowPublicKeyRetrieval=true",
  "jdbc-user": "root",
  "jdbc-password": "123456",
  "jdbc-driver": "com.mysql.cj.jdbc.Driver"
}}' http://localhost:8090/api/metalakes/test/catalogs
```

:::note
修改 `localhost`、`port` 以及 metalake 和 catalogs 的名称，以匹配您的环境。
:::

## 开发环境

### 想法

1. 从 [GitHub](https://github.com/trinodb/trino) 克隆 Trino 仓库。本文档默认使用 Trino `469`。检出与你的目标 Trino 版本匹配的标签（例如，`git checkout 469`）。
2. 在 IDEA 中打开 Trino 项目。
3. 在 Trino 项目中创建一个名为 `trino-gravitino` 的新模块，如下所示：
![trino-gravitino](../assets/trino/create-gravitino-trino-connector.jpg)

4. 确定哪个 version-segment 模块与您的 Trino 版本匹配：

| Trino 版本 | 版本-分段模块    |
   |---------------|---------------------------|
| 440-445       | `trino-connector-440-445` |
| 446-451       | `trino-connector-446-451` |
| 452-468       | `trino-connector-452-468` |
| 469-472       | `trino-connector-469-472` |
| 473-478       | `trino-connector-473-478` |

5. 将 `<module>plugin/trino-gravitino</module>` 添加到 `trino/pom.xml` 中，并为 `trino-gravitino` 模块创建 `pom.xml`。下面的示例使用 Trino `469`。确保 `trino-root` 版本与您正在开发的 Trino 版本相匹配。

`<build>` 部分使用 `build-helper-maven-plugin` 直接添加 Gravitino 源代码目录。将 `/path/to/gravitino` 替换为您本地 Gravitino 项目根目录的绝对路径，并将 `trino-connector-469-472` 更改为步骤 4 中的版本段模块。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>io.trino</groupId>
        <artifactId>trino-root</artifactId>
        <version>469</version>
        <relativePath>../../pom.xml</relativePath>
    </parent>

    <artifactId>trino-gravitino</artifactId>
    <packaging>trino-plugin</packaging>
    <description>Trino - Gravitino Connector</description>

    <properties>
        <air.main.basedir>${project.parent.basedir}</air.main.basedir>
    </properties>

    <dependencies>

        <!--
            You can use the snapshot version. For example, to use the jar from
            the latest main branch, run the following command in the Gravitino project:
            ./gradlew publishToMavenLocal
        -->
        <dependency>
            <groupId>org.apache.gravitino</groupId>
            <artifactId>catalog-common</artifactId>
            <version><GRAVITINO_VERSION></version>
            <exclusions>
                <exclusion>
                    <groupId>io.dropwizard.metrics</groupId>
                    <artifactId>metrics-core</artifactId>
                </exclusion>
                <exclusion>
                    <groupId>io.netty</groupId>
                    <artifactId>netty</artifactId>
                </exclusion>
                <exclusion>
                    <groupId>org.apache.logging.log4j</groupId>
                    <artifactId>log4j-core</artifactId>
                </exclusion>
            </exclusions>
        </dependency>

        <dependency>
            <groupId>org.apache.gravitino</groupId>
            <artifactId>client-java-runtime</artifactId>
            <version><GRAVITINO_VERSION></version>
        </dependency>

        <dependency>
            <groupId>io.airlift</groupId>
            <artifactId>json</artifactId>
        </dependency>

        <dependency>
            <groupId>io.airlift.resolver</groupId>
            <artifactId>resolver</artifactId>
            <version>1.6</version>
        </dependency>

        <dependency>
            <groupId>io.trino</groupId>
            <artifactId>trino-client</artifactId>
        </dependency>

        <dependency>
            <groupId>io.trino</groupId>
            <artifactId>trino-jdbc</artifactId>
        </dependency>

        <dependency>
            <groupId>joda-time</groupId>
            <artifactId>joda-time</artifactId>
        </dependency>

        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-collections4</artifactId>
            <version>4.4</version>
        </dependency>

        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
        </dependency>

        <dependency>
            <groupId>org.codehaus.plexus</groupId>
            <artifactId>plexus-xml</artifactId>
            <version>4.0.2</version>
        </dependency>

        <dependency>
            <groupId>io.airlift</groupId>
            <artifactId>log</artifactId>
        </dependency>

        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-jdk14</artifactId>
            <version>2.0.17</version>
        </dependency>

        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-annotations</artifactId>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>io.opentelemetry</groupId>
            <artifactId>opentelemetry-api</artifactId>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>io.trino</groupId>
            <artifactId>trino-spi</artifactId>
            <scope>provided</scope>
        </dependency>

    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>build-helper-maven-plugin</artifactId>
                <executions>
                    <execution>
                        <id>add-source</id>
                        <phase>generate-sources</phase>
                        <goals>
                            <goal>add-source</goal>
                        </goals>
                        <configuration>
                            <sources>
                                <!-- Shared base source -->
                                <source>/path/to/gravitino/trino-connector/trino-connector/src/main/java</source>
                                <!-- Version-segment source (change to match your Trino version) -->
                                <source>/path/to/gravitino/trino-connector/trino-connector-469-472/src/main/java</source>
                            </sources>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>

</project>
```

6. 尝试编译 `trino-gravitino` 模块以检查错误：

```shell
# Build the whole Trino project
./mvnw -pl '!core/trino-server-rpm' package -DskipTests -Dair.check.skip-all=true

# Build only the trino-gravitino module
./mvnw clean -pl 'plugin/trino-gravitino' package -DskipTests -Dair.check.skip-all=true
```

:::note
如果由于 `The following artifacts could not be resolved: org.apache.gravitino:xxx:jar` 导致编译错误，请先在 Gravitino 项目中运行 `./gradlew publishToMavenLocal`。
:::

7. 在 Trino 项目中为 Gravitino Trino 连接器设置配置，如下所示：
![](../assets/trino/add-config.jpg)

相应的配置文件：

- Gravitino 属性文件：`gravitino.properties`

   ```properties
   connector.name=gravitino
   gravitino.uri=http://localhost:8090
   gravitino.metalake=test
   ```

- Trino 配置文件：`config.properties`

   ```properties
   #
   # WARNING
   # ^^^^^^^
   # This configuration file is for development only and should NOT be used
   # in production. For example configuration, see the Trino documentation.
   #
   node.id=ffffffff-ffff-ffff-ffff-ffffffffffff
   node.environment=test
   node.internal-address=localhost
   experimental.concurrent-startup=true

   # Default port is 8080, change it to 8180 to avoid conflicts
   http-server.http.port=8180

   discovery.uri=http://localhost:8180

   exchange.http-client.max-connections=1000
   exchange.http-client.max-connections-per-server=1000
   exchange.http-client.connect-timeout=1m
   exchange.http-client.idle-timeout=1m

   scheduler.http-client.max-connections=1000
   scheduler.http-client.max-connections-per-server=1000
   scheduler.http-client.connect-timeout=1m
   scheduler.http-client.idle-timeout=1m

   query.client.timeout=5m
   query.min-expire-age=30m

   plugin.bundles=\
     ../../plugin/trino-iceberg/pom.xml,\
     ../../plugin/trino-hive/pom.xml,\
     ../../plugin/trino-local-file/pom.xml,\
     ../../plugin/trino-mysql/pom.xml,\
     ../../plugin/trino-postgresql/pom.xml,\
     ../../plugin/trino-exchange-filesystem/pom.xml,\
     ../../plugin/trino-gravitino/pom.xml

   node-scheduler.include-coordinator=true

   # The Gravitino Trino connector only supports the dynamic catalog manager
   catalog.management=dynamic
   ```

   :::note
如果相应的 `plugin/trino-xxx/pom.xml` 未在 `plugin.bundles` 中列出，则删除 `/etc/catalogs/xxx.properties`。对于 Hive 插件，请使用 `plugin/trino-hive/pom.xml`。
   :::

8. 启动 Trino 服务器并连接到 Gravitino 服务器。
![](../assets/trino/start-trino.jpg)

9. `DevelopmentServer` 成功启动后，使用 Trino CLI 连接到 Trino 服务器：

   ```shell
   java -jar trino-cli-*-executable.jar --server localhost:8180
   ```

   :::note
从 [Trino 发布页面](https://trino.io/docs/469/client/cli.html) 下载 `trino-cli` jar 包。使用与您的 Trino 服务器版本相匹配的 CLI 版本。
   :::

10. 在 Gravitino 项目中开发 Gravitino Trino 连接器，并在 Trino 项目中进行调试。
![](../assets/trino/show-catalogs.jpg)
