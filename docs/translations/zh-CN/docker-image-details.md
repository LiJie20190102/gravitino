---
slug: /docker-image-details
keyword: docker
license: This software is licensed under the Apache License version 2.
---
## 用户 Docker 镜像

## Apache Gravitino Docker 镜像

使用 Gravitino Docker 镜像部署服务。

容器启动命令

```shell
docker run --rm -d -p 8090:8090 -p 9001:9001 apache/gravitino:latest
```

内存设置

JVM 堆内存和元空间由 `GRAVITINO_MEM`（默认 `-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m`）控制。通过 `-e GRAVITINO_MEM="-Xms4g -Xmx4g -XX:MaxMetaspaceSize=1g"` 覆盖以调整大小。启动脚本会将 `GRAVITINO_MEM` 追加到 `JAVA_OPTS`，因此在需要调整堆/元空间大小时设置该参数。

更新日志

- apache/gravitino:1.3.0
  - 基于 Gravitino 1.3.0 构建。更多信息参见 1.3.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.3.0)。

- apache/gravitino:1.2.0
  - 基于 Gravitino 1.2.0 构建。更多信息参见 1.2.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.2.0)。

- apache/gravitino:1.1.0
  - 基于 Gravitino 1.1.0，更多信息参见 1.1.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.1.0)。

- apache/gravitino:1.0.0
  - 基于 Gravitino 1.0.0，更多信息参见 1.0.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.0.0)。

- apache/gravitino:0.9.1
  - 基于 Gravitino 0.9.1，更多信息参见 0.9.1 [发布说明](https://github.com/apache/gravitino/releases/tag/v0.9.1)。

- apache/gravitino:0.9.0-incubating
  - 基于 Gravitino 0.9.0-incubating，更多信息参见 0.9.0-incubating [发布说明](https://github.com/apache/gravitino/releases/tag/v0.9.0-incubating)。

- apache/gravitino:0.8.0-incubating
  - 基于 Gravitino 0.8.0-incubating，更多信息参见 0.8.0-incubating [发布说明](https://github.com/apache/gravitino/releases/tag/v0.8.0-incubating)。

- apache/gravitino:0.7.0-incubating
  - 基于 Gravitino 0.7.0-incubating，更多信息参见 0.7.0-incubating [发布说明](https://github.com/apache/gravitino/releases/tag/v0.7.0-incubating)。
  - 将 bundle jar 包（gravitino-aws-bundle.jar、gravitino-gcp-bundle.jar、gravitino-aliyun-bundle.jar）放入 `${GRAVITINO_HOME}/catalogs/hadoop/libs` 目录，以支持云存储 Catalog，无需手动将 jar 包添加到 classpath。

- apache/gravitino:0.6.1-incubating
  - 基于 Gravitino 0.6.1-incubating，更多信息参见 0.6.1-incubating 发布说明。

- apache/gravitino:0.6.0-incubating（切换至 Apache 官方 DockerHub 仓库）
  - 使用最新 Gravitino 0.6.0-incubating 版本源码构建镜像。

- datastrato/gravitino:0.5.1
  - 基于 Gravitino 0.5.1，更多信息参见 0.5.1 发布说明。

- datastrato/gravitino:0.5.0
  - 基于 Gravitino 0.5.0，更多信息参见 0.5.0 发布说明。

- datastrato/gravitino:0.4.0
  - 基于 Gravitino 0.4.0，更多信息参见 0.4.0 发布说明。

- datastrato/gravitino:0.3.1
  - 修复部分问题

- datastrato/gravitino:0.3.0
  - Docker 镜像 `datastrato/gravitino:0.3.0`
  - Gravitino 服务器
  - 暴露端口：
    - `8090` Gravitino Web UI
    - `9001` Iceberg REST 服务

## Apache Gravitino Iceberg REST Server Docker 镜像

使用 Docker 镜像部署独立的 Gravitino Iceberg REST 服务器。

容器启动命令

```shell
docker run --rm -d -p 9001:9001 apache/gravitino-iceberg-rest:latest
```

内存设置

使用 `GRAVITINO_MEM` 设置 JVM 大小（默认 `-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m`）。需要不同大小时通过 `-e GRAVITINO_MEM="-Xms4g -Xmx4g -XX:MaxMetaspaceSize=1g"` 覆盖。启动脚本会将 `GRAVITINO_MEM` 追加到 `JAVA_OPTS`，设置该参数可更改堆/元空间配置。

更新日志

- apache/gravitino-iceberg-rest:1.3.0
  - 基于 Gravitino 1.3.0 构建。更多信息参见 1.3.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.3.0)。

- apache/gravitino-iceberg-rest:1.2.0
  - 将 Iceberg 升级至 1.10.1
  - 支持视图管理和授权
  - 支持跨命名空间表重命名
  - 添加扫描计划缓存以提升重复查询性能
  - 更多信息参见 1.2.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.2.0)。

- apache/gravitino-iceberg-rest:1.1.0
  - 支持扫描计划端点
  - 支持获取凭证端点
  - 支持表元数据缓存
  - 支持访问控制
  - 更多信息参见 1.1.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.1.0)。

- apache/gravitino-iceberg-rest:1.0.0
  - 将 Iceberg 版本升级至 1.9
  - 支持通过 warehouse 参数指定 Catalog 名称

- apache/gravitino-iceberg-rest:0.9.1
  - 修复启用 OAuth 时 Iceberg REST 服务器启动失败的问题。
  - 添加 StarRocks 和 Apache Doris 使用 IRC 的文档

- apache/gravitino-iceberg-rest:0.9.0-incubating
  - 将 Iceberg 版本从 1.5 升级至 1.6。
  - 支持 S3 path-style-access 属性。
  - 修复 Iceberg 内存 Catalog 后端中 warehouse 硬编码的问题。


- apache/gravitino-iceberg-rest:0.8.0-incubating
  - 支持 OSS 和 ADLS 存储。
  - 支持事件监听器。
  - 支持审计日志。

- apache/gravitino-iceberg-rest:0.7.0-incubating
  - 使用 JDBC Catalog 后端。
  - 支持 S3 和 GCS 存储。
  - 支持凭证分发。
  - 支持通过环境变量修改配置。

- apache/gravitino-iceberg-rest:0.6.1-incubating
  - 基于 Gravitino 0.6.1-incubating，更多信息参见 0.6.1-incubating 发布说明。

- apache/gravitino-iceberg-rest:0.6.0-incubating.
  - 使用内存 Catalog 后端的 Gravitino Iceberg REST 服务器。
  - 暴露端口：
    - `9001` Iceberg REST 服务

## Apache Gravitino MCP Server 镜像

使用 Docker 镜像部署 Gravitino MCP 服务器。

容器启动命令

```shell
docker run --rm -d -p 8000:8000 apache/gravitino-mcp-server:latest --metalake test --transport http --mcp-url http://0.0.0.0:8000/mcp
```

更新日志

- apache/gravitino-mcp-server:1.3.0
  - 基于 Gravitino 1.3.0 构建。更多信息参见 1.3.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.3.0)。

- apache/gravitino-mcp-server:1.2.0
  - 基于 Gravitino 1.2.0 构建。更多信息参见 1.2.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.2.0)。

- apache/gravitino-mcp-server:1.1.0
  - 基于 Gravitino 1.1.0 构建。更多信息参见 1.1.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.1.0)。

- apache/gravitino-mcp-server:1.0.0
  - 支持 `catalog`、`schema`、`table`、`fileset`、`model`、`policy`、`topic`、`statistic`、`job` 的读操作。
  - 支持关联和取消关联元数据的标签和策略
  - 支持提交和取消作业。

## Apache Gravitino Lance REST Server Docker 镜像

使用 Docker 镜像部署独立的 Gravitino Lance REST 服务器。


```shell
docker run --rm -d -p 9102:9102 -e LANCE_REST_GRAVITINO_METALAKE_NAME=test -e LANCE_REST_GRAVITINO_URI=http://gravitino-host:port -e LANCE_REST_PORT=9102 apache/gravitino-lance-rest:latest 
```

内存设置

使用 `GRAVITINO_MEM` 设置 JVM 大小（默认 `-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m`）。示例：`-e GRAVITINO_MEM="-Xms2g -Xmx2g -XX:MaxMetaspaceSize=512m"`。启动脚本会将 `GRAVITINO_MEM` 追加到 `JAVA_OPTS`，在需要调整堆/元空间大小时设置该参数。

Gravitino Lance REST 服务器支持设置以下环境变量
- LANCE_REST_GRAVITINO_METALAKE_NAME：将覆盖配置文件 `conf/gravitino-lance-rest-server.conf` 中的配置项 "gravitino.lance-rest.gravitino-metalake"。**应将其设置为 Gravitino Metalake 名称。**
- LANCE_REST_NAMESPACE_BACKEND：将覆盖配置文件 `conf/gravitino-lance-rest-server.conf` 中的配置项 "gravitino.lance-rest.namespace-backend"。默认值为 "gravitino"，目前不应更改。
- LANCE_REST_GRAVITINO_URI：将覆盖配置文件 `conf/gravitino-lance-rest-server.conf` 中的配置项 "gravitino.lance-rest.gravitino-uri"。默认值为 "http://localhost:8090"，可更改为 Gravitino 服务器地址。**注意，Gravitino 服务器 URI `http://localhost:8090` 是 Docker 容器内部地址；若 Gravitino 服务器运行在 Docker 容器外部，应将其设置为主机 IP 地址，例如 `http://host-ip:8090`。**
- LANCE_REST_HOST：将覆盖配置文件 `conf/gravitino-lance-rest-server.conf` 中的配置项 "gravitino.lance-rest.host"。默认值为 `0.0.0.0`。
- LANCE_REST_PORT：将覆盖配置文件 `conf/gravitino-lance-rest-server.conf` 中的配置项 "gravitino.lance-rest.httpPort"。默认值为 `9101`。

若不熟悉 Gravitino Lance REST 服务器且无特殊需求，不建议更改 `LANCE_REST_NAMESPACE_BACKEND`、`LANCE_REST_HOST` 和 `LANCE_REST_PORT`。

更新日志

- apache/gravitino-lance-rest:1.3.0
  - 基于 Gravitino 1.3.0 构建。更多信息参见 1.3.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.3.0)。

- apache/gravitino-lance-rest:1.2.0
  - 支持删除和重命名列操作
  - 在 loadTable 和 createTable 响应中包含数据集版本信息
  - 基于 Gravitino 1.2.0 构建。更多信息参见 1.2.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.2.0)。

- apache/gravitino-lance-rest:1.1.0
  - Lance REST 服务器首次发布
  - 支持通过 REST API 集成 Lance 表
  - 基于 Gravitino 1.1.0 构建。更多信息参见 1.1.0 [发布说明](https://github.com/apache/gravitino/releases/tag/v1.1.0)。

## Playground Docker 镜像

使用 [playground](https://github.com/apache/gravitino-playground) 体验包含其他组件的完整 Gravitino 系统。

playground 由多个 Docker 镜像组成。

playground 的 Docker 镜像已配置合适的参数供用户体验。

### Apache Hive 镜像

更新日志

- apache/gravitino-playground:hive-2.7.3（切换至 Apache 官方 DockerHub 仓库）
  - 使用 `datastrato/hive:2.7.3-no-yarn` Dockerfile 重新构建镜像。

- datastrato/hive:2.7.3-no-yarn
  - Docker 镜像 `datastrato/hive:2.7.3-no-yarn`
  - `hadoop-2.7.3`
  - `hive-2.3.9`
  - 容器启动时不启动 YARN

### Trino 镜像

更新日志

- apache/gravitino-playground:trino-478-gravitino-1.3.0
  - 使用 Gravitino 1.3.0 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-478-gravitino-1.2.0
  - 使用 Gravitino 1.2.0 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-1.1.0
  - 使用 Gravitino 1.1.0 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-1.0.0
  - 使用 Gravitino 1.0.0 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-0.9.1
  - 使用 Gravitino 0.9.1 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-0.9.0-incubating
  - 使用 Gravitino 0.9.0-incubating 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-0.8.0-incubating
  - 使用 Gravitino 0.8.0-incubating 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-0.7.0-incubating
  - 使用 Gravitino 0.7.0-incubating 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-0.6.1-incubating
  - 使用 Gravitino 0.6.1-incubating 版本的 Dockerfile 构建镜像。

- apache/gravitino-playground:trino-435-gravitino-0.6.0-incubating（切换至 Apache 官方 DockerHub 仓库）
  - 使用 Gravitino 0.6.0 版本的 Dockerfile 构建镜像。

- datastrato/trino:435-gravitino-0.5.1
  - 基于 Gravitino 0.5.1，更多详情请参考 0.5.1 版本发布说明。

- datastrato/trino:426-gravitino-0.5.0
  - 基于 Gravitino 0.5.0，更多详情请参考 0.5.0 版本发布说明。

- datastrato/trino:426-gravitino-0.4.0
  - 基于 Gravitino 0.4.0，更多详情请参考 0.4.0 版本发布说明。

- datastrato/trino:426-gravitino-0.3.1
  - 修复若干问题

- datastrato/trino:426-gravitino-0.3.0
  - Docker 镜像 `datastrato/trino:426-gravitino-0.3.0`
  - 基于 `trino:426`
  - 将 Gravitino trino-connector-0.3.0 库添加到 `/usr/lib/trino/plugin/gravitino`

## 开发者 Docker 镜像

使用此类 Docker 镜像可方便对 Gravitino 中所有 catalog 和 connector 模块进行集成测试。

## 带 Kerberos 的 Hive 镜像

使用此类镜像测试启用 Kerberos 的 Apache Hive catalog

更新日志

- apache/gravitino-ci:kerberos-hive-0.1.7
  - 从最终镜像层中排除安装归档文件以减小镜像体积。
    更多详情请参见 [PR](https://github.com/apache/gravitino/pull/12731)

- apache/gravitino-ci:kerberos-hive-0.1.6
  - 将用户名从 `datastrato` 改为 `gravitino`。
    更多详情请参见 [PR](https://github.com/apache/gravitino/pull/7040)

- apache/gravitino-ci:kerberos-hive-0.1.5（切换至 Apache 官方 DockerHub 仓库）
  - 使用 Gravitino 0.6.0 版本的 Dockerfile 构建镜像。

- datastrato/gravitino-ci-kerberos-hive:0.1.5
  - 在容器中以端口 19083 为 Hive 集群启动另一个 HMS。用于测试 Kerberos 认证在具有多个 HMS 的 Kerberos 启用 Hive 集群中是否正常工作。
  - 在启动脚本中刷新 ssh 密钥。
  - 添加通过 ssh 无密码登录 localhost 的测试逻辑。

- datastrato/gravitino-ci-kerberos-hive:0.1.4
  - 将 DataNode 状态的总检查时间增加至 150 秒。
  - 输出 DataNode 启动失败的日志

- datastrato/gravitino-ci-kerberos-hive:0.1.3
  - 在 core-site.xml 文件中添加更多代理用户。
  - 修复 `start.sh` 脚本中的错误。

- datastrato/gravitino-ci-kerberos-hive:0.1.2
  - 在启动脚本中添加 `${HOSTNAME} >> /root/.ssh/known_hosts`。
  - 添加 DataNode 状态检查，若 DataNode 在 100 秒内未运行或未就绪，容器将退出。

- datastrato/gravitino-ci-kerberos-hive:0.1.1
  - 为 Gravitino Web 服务器添加名为 'HTTP/localhost@HADOOPKRB' 的 principal。
  - 修复代理用户配置相关的问题。

- datastrato/gravitino-ci-kerberos-hive:0.1.0
    - 搭建启用 Kerberos 的 Hive 集群。
    - 安装 KDC 服务器并为 Hive 创建 principal。更多详情请参见 [kerberos-hive](../../../dev/docker/kerberos-hive)

## Hive 镜像

使用此类镜像测试 Apache Hive catalog。

更新日志

- apache/gravitino-ci:hive-0.1.20
  - 将用户名从 `datastrato` 改为 `gravitino`。
    更多详情请参见 [PR](https://github.com/apache/gravitino/pull/7040)

- apache/gravitino-ci:hive-0.1.19
  - 从源码构建 ranger 包。
 
- apache/gravitino-ci:hive-0.1.18
  - 支持 `hive-site.xml` 文件和 Hive Metastore 的 UTF-8 编码。
    更多详情请参见 [PR](https://github.com/apache/gravitino/pull/6625)
  - 更改 ranger-hive-plugin 和 ranger-hdfs-plugin 的下载 URL。

- apache/gravitino-ci:hive-0.1.17
  - 新增对 JDBC SQL 标准授权的支持
    - 在 `hive-site-for-sql-base-auth.xml` 和 `hiveserver2-site-for-sql-base-auth.xml` 中添加 JDBC SQL 标准授权相关配置
- 
- apache/gravitino-ci:hive-0.1.16
  - 在 `hive-site.xml` 文件中添加 GCS 相关配置。
  - 在 `${HADOOP_HOME}/share/hadoop/common/lib/` 中添加 GCS bundle jar

- apache/gravitino-ci:hive-0.1.15
  - 在 `hive-site.xml` 文件中添加 Azure Blob Storage(ADLS) 相关配置。

- apache/gravitino-ci:hive-0.1.14 
  - 在 `hive-site.xml` 文件中添加 Amazon S3 相关配置。
    - `fs.s3a.access.key` S3 bucket 的访问密钥。
    - `fs.s3a.secret.key` S3 bucket 的密钥。
    - `fs.s3a.endpoint` S3 bucket 的端点。

- apache/gravitino-ci:hive-0.1.13（切换至 Apache 官方 DockerHub 仓库）
  - 使用 Gravitino 0.6.0 版本的 Dockerfile 构建镜像。

- datastrato/gravitino-ci-hive:0.1.13
  - 支持 Hive 2.3.9 和 HDFS 2.7.3
    - Docker 环境变量：
      - `HIVE_RUNTIME_VERSION`: `hive2`（默认）
  - 支持 Hive 3.1.3、HDFS 3.1.0 和 Ranger 插件版本 2.4.0
    - Docker 环境变量：
      - `HIVE_RUNTIME_VERSION`: `hive3`
      - `RANGER_SERVER_URL`: Ranger admin URL
      - `RANGER_HIVE_REPOSITORY_NAME`: Ranger admin 中的 Hive repository 名称
      - `RANGER_HDFS_REPOSITORY_NAME`: Ranger admin 中的 HDFS repository 名称
    - 要启用 Hive Ranger 插件，需同时设置 `RANGER_SERVER_URL` 和 `RANGER_HIVE_REPOSITORY_NAME` 环境变量。Hive Ranger 审计日志存储在 `/tmp/root/ranger-hive-audit.log`。
    - 要启用 HDFS Ranger 插件，需同时设置 `RANGER_SERVER_URL` 和 `RANGER_HDFS_REPOSITORY_NAME` 环境变量。HDFS Ranger 审计日志存储在 `/usr/local/hadoop/logs/ranger-hdfs-audit.log`
    - 示例：docker run -e HIVE_RUNTIME_VERSION='hive3' -e RANGER_SERVER_URL='http://ranger-server:6080' -e RANGER_HIVE_REPOSITORY_NAME='hiveDev' -e RANGER_HDFS_REPOSITORY_NAME='hdfsDev' ... datastrato/gravitino-ci-hive:0.1.13

- datastrato/gravitino-ci-hive:0.1.12
  - 将 Hive Docker 镜像体积缩减 420MB

- datastrato/gravitino-ci-hive:0.1.11
  - 从启动脚本中移除 `yarn`；移除 `yarn-site.xml` 和 `yarn-env.sh` 文件；
  - 在 `mapred-site.xml` 文件中将 `mapreduce.framework.name` 的值从 `yarn` 改为 `local`。

- datastrato/gravitino-ci-hive:0.1.10
  - 从启动脚本中移除 SSH 服务。
  - 使用 `hadoop-daemon.sh` 启动 HDFS 服务。

- datastrato/gravitino-ci-hive:0.1.9
  - 安装包后清除缓存。

- datastrato/gravitino-ci-hive:0.1.8
  - 将 `hive.server2.enable.doAs` 的值改为 `true`

- datastrato/gravitino-ci-hive:0.1.7
  - 在构建 Docker 镜像前下载 MySQL JDBC 驱动
  - 将 `hdfs` 设为 HDFS 超级用户组

- datastrato/gravitino-ci-hive:0.1.6
  - 容器启动时不启动 YARN
  - 移除暴露的端口：
    - `22` SSH
    - `8088` YARN 服务

- datastrato/gravitino-ci-hive:0.1.5
  - 回退 `datastrato/gravitino-ci-hive:0.1.4` 中的 `在启动 Hadoop 前将容器主机名映射到 127.0.0.1`

- datastrato/gravitino-ci-hive:0.1.4
  - 将 HDFS DataNode 数据传输地址配置为 `0.0.0.0:50010`
  - 在启动 Hadoop 前将容器主机名映射到 `127.0.0.1`
  - 为 HDFS DataNode 暴露 `50010` 端口

- datastrato/gravitino-ci-hive:0.1.3
  - 将 MySQL bind-address 从 `127.0.0.1` 改为 `0.0.0.0`
  - 添加 `iceberg` 到 MySQL 用户，密码为 `iceberg`
  - 为 MySQL 暴露 `3306` 端口

- datastrato/gravitino-ci-hive:0.1.2
  - 基于 `datastrato/gravitino-ci-hive:0.1.1`
  - 在 `core-site.xml` 文件中将 `fs.defaultFS` 从 `local` 改为 `0.0.0.0`。
  - 在 `Dockerfile` 文件中暴露 `9000` 端口。

- datastrato/gravitino-ci-hive:0.1.1
  - 基于 `datastrato/gravitino-ci-hive:0.1.0`
  - 将 HDFS/YARN/HIVE 的 `MaxPermSize` 从 `8GB` 改为 `128MB`
  - 将 `HADOOP_HEAPSIZE` 从 `8192` 改为 `128`

- datastrato/gravitino-ci-hive:0.1.0
  - Docker 镜像 `datastrato/gravitino-ci-hive:0.1.0`
  - `hadoop-2.7.3`
  - `hive-2.3.9`
  - 暴露端口：
    - `22` SSH
    - `9000` HDFS defaultFS
    - `50070` HDFS NameNode
    - `50075` HDFS DataNode HTTP 服务器
    - `50010` HDFS DataNode 数据传输
    - `8088` YARN 服务
    - `9083` Hive metastore
    - `10000` HiveServer2
    - `10002` HiveServer2 HTTP

## Trino 镜像

使用此镜像测试 Trino。

更新日志

- apache/gravitino-ci:trino-0.1.6（切换至 Apache 官方 DockerHub 仓库）
  - 使用 Gravitino 0.6.0 发行版的 Dockerfile 构建该镜像。

- datastrato/gravitino-ci-trino:0.1.6
  - 将 trino:426 升级至 trino:435

- datastrato/gravitino-ci-trino:0.1.5
  - 新增 gravitino-trino-connector 版本检查

- datastrato/gravitino-ci-trino:0.1.4
  - 将配置文件 `/etc/trino/jvm.config` 中的 `-Xmx1G` 修改为 `-Xmx2G`

- datastrato/gravitino-ci-trino:0.1.3
  - 移除将 `gravitino-trino-connector` 文件夹内容复制至插件文件夹 `/usr/lib/trino/plugin/gravitino` 的操作

- datastrato/gravitino-ci-trino:0.1.2
  - 将 JDBC 驱动 'mysql-connector-java' 和 'postgres' 复制至 `/usr/lib/trino/iceberg/` 文件夹

- datastrato/gravitino-ci-trino:0.1.0
  - Docker 镜像 `datastrato/gravitino-ci-trino:0.1.0`
  - 基于 `trinodb/trino:426` 构建，并移除了部分未使用的插件。
  - 暴露端口：
    - `8080` Trino JDBC 端口

## Doris 镜像

使用此镜像测试 Apache Doris。

更新日志

- apache/gravitino-ci:doris-0.1.5（切换至 Apache 官方 DockerHub 仓库）
  - 使用 Gravitino 0.6.0 发行版的 Dockerfile 构建该镜像。

- datastrato/gravitino-ci-doris:0.1.5
  - 移除 Dockerfile 中的 chmod 命令以减小 Docker 镜像体积。

- datastrato/gravitino-ci-doris:0.1.4
  - 在 start.sh 中移除 chmod 以加速启动

- datastrato/gravitino-ci-doris:0.1.3
  - 为适配 CI 框架，启动失败时不再退出容器，日志不再输出至 stdout。 
  - 新增 `report_disk_state_interval_seconds` 配置以减少上报间隔。

- datastrato/gravitino-ci-doris:0.1.2
  - 新增对 Doris BE 状态的检查，并为添加 BE 节点增加重试机制。

- datastrato/gravitino-ci-doris:0.1.1
  - 优化 `start.sh`，在启动 Doris 前增加磁盘空间检查，当 FE 或 BE 启动失败时退出，并增加日志输出至 stdout

- datastrato/gravitino-ci-doris:0.1.0
  - Docker 镜像 `datastrato/gravitino-ci-doris:0.1.0`
  - 在同一容器内启动 Doris BE 与 FE
  - 在 Doris 中建表时请设置表属性 `"replication_num" = "1"`，因为默认副本数为 3，但 Doris 容器仅有一个 BE。
  - 用户名：`root`，密码：N/A（密码为空）
  - 暴露端口：
    - `8030` Doris FE HTTP 端口
    - `9030` Doris FE MySQL 服务器端口

## Ranger 镜像

使用此镜像控制 Trino 的权限。

更新日志

- apache/gravitino-ci:ranger-0.1.2
  - 从源码构建 ranger 包。

- apache/gravitino-ci:ranger-0.1.1（切换至 Apache 官方 DockerHub 仓库）
  - 使用 Gravitino 0.6.0 发行版的 Dockerfile 构建该镜像。

- datastrato/gravitino-ci-ranger:0.1.1
  - Docker 镜像 datastrato/gravitino-ci-ranger:0.1.1
  - 使用 `datastrato/apache-ranger:2.4.0` 中的 `ranger-admin` 发行版构建 Docker 镜像。
  - 移除 `start-ranger-service.sh` 中不必要的 hack。
  - 将 Docker 镜像构建时间从 `~1h` 缩短至 `~5min`。
  - 如何调试 Ranger admin 服务：
    - 使用 `docker exec -it <container_id> bash` 进入 Docker 容器。
    - 在 Docker 容器的 `/opt/ranger-admin/ews/webapp/WEB-INF/classes/conf/ranger-admin-env-debug.sh` 文件中添加以下内容：`export JAVA_OPTS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5001`
    - 执行 `./opt/ranger-admin/stop-ranger-admin.sh` 和 `./opt/ranger-admin/start-ranger-admin.sh` 以重启 Ranger admin。
    - 从 GitHub 克隆 `Apache Ranger` 项目并检出 `2.4.0` 发行版。
    - 在 IDE 中创建远程调试配置（`Use model classpath` = `EmbeddedServer`）并连接至 Ranger admin 容器。

- datastrato/gravitino-ci-ranger:0.1.0
  - Docker 镜像 `datastrato/gravitino-ci-ranger:0.1.0`
  - 支持 Apache Ranger 2.4.0
  - 使用环境变量 `RANGER_PASSWORD` 设置 Apache Ranger admin 密码。密码长度须至少为 8 个字符，且至少包含一个字母和一位数字。
  - 暴露端口：
    - `6080` Apache Ranger admin 端口