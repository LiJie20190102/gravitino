---
title: "Trino Cascading Queries"
slug: "/trino-connector/trino-cascading-query"
keyword: "gravitino connector trino"
license: "This software is licensed under the Apache License version 2."
---

## 背景

借助 `Apache Gravitino Trino connector` 和 [`Gravitino Trino cascading connector`](https://github.com/datastrato/trino-cascading-connector)，您可以在 Trino 中实现级联查询。
这些连接器允许您将其他 Trino 集群作为当前 Trino 集群的数据源，
从而实现在不同 Trino 集群中跨目录的查询。

该机制优先在与数据位于同一区域的 Trino 集群中执行查询，
基于目录中的数据分布。通过这样做，它显著减少了
通过网络传输的数据量，解决了传统联邦查询引擎中常见的性能问题
在这些引擎中，需要跨网络传输大量数据。

## 部署 Trino

要搭建 Trino 级联查询环境，您应该首先部署至少两个 Trino 环境。
接下来，将 `Apache Gravitino Trino connector` 插件和 `Gravitino Trino cascading connector` 插件安装到 Trino 中。
有关详细步骤，请参阅 [部署 Trino 文档](installation.md)。

请按照以下步骤操作：

1. [下载](https://github.com/apache/gravitino/releases) `Apache Gravitino Trino connector` tarball 并解压。
该 tarball 包含一个名为 `gravitino-trino-connector-<version>` 的顶级目录。将此目录重命名为 `gravitino`。
2. [下载](https://github.com/datastrato/trino-cascading-connector/releases) `Gravitino Trino cascading connector` tarball 并解压。
该 tarball 也包含一个名为 `gravitino-trino-cascading-connector-<version>` 的顶级目录。将此目录重命名为 `trino`。
3. 将两个连接器目录复制到 Trino 的插件目录中。
通常，此目录位于 `Trino-server-<version>/plugin`，并包含 Trino 使用的其他 catalog。

确保 `plugin` 目录包含 `gravitino` 和 `trino` 子目录。
验证托管两个 Trino 集群（分别标识为 `c1-trino` 和 `c2-trino`）的机器之间的网络连通性。


### 在容器中部署 Trino

下载 `Apache Gravitino Trino connector` tarball 和 `Gravitino Trino cascading connector` tarball，然后解压它们。
解压后，您将找到名为 `gravitino-trino-connector-<version>` 的目录
和 `gravitino-trino-cascading-connector-<version>`。

要在主机 `c1-trino` 上启动 Trino 并挂载插件，请执行以下命令：

```bash
docker run --name c1-trino -d -p 8080:8080 <image-name> -v `gravitino-trino-connector-<version>`:/usr/lib/trino/plugin/gravitino \
-v `gravitino-trino-cascading-connector-<version>`:/usr/lib/trino/plugin/trino

```

同样，要在主机 `c2-trino` 上启动 Trino 并挂载插件，请使用：

```bash
docker run --name c2-trino -d -p 8080:8080 <image-name> -v `gravitino-trino-connector-<version>`:/usr/lib/trino/plugin/gravitino \
-v `gravitino-trino-cascading-connector-<version>`:/usr/lib/trino/plugin/trino
```

启动 Trino 容器后，确保配置目录 `/etc/trino` 已正确设置。
验证 `c1-trino` 和 `c2-trino` 上的 Trino 容器可以通过网络相互通信。

## 配置 Trino

有关配置 Trino 的详细说明，请参阅 [Trino 文档](https://trino.io/docs/current/installation/deployment.html#configuring-trino)。
完成基本配置后，继续配置 Gravitino 连接器。
在 `c1-trino` 主机的 `etc/catalog` 目录下创建一个 `gravitino.properties` 文件，内容如下：

```text
connector.name = gravitino
gravitino.uri = http://GRAVITINO_HOST_IP:GRAVITINO_HOST_PORT
gravitino.metalake = GRAVITINO_METALAKE_NAME
gravitino.cloud.region-code=c1
```

属性 `gravitino.cloud.region-code=c1` 指定了 `c1-trino` 主机位于 `c1` 区域，
它将处理 `c1` 区域中目录的查询。对于处理 `c2` 区域中的查询，
它们将被委派给 `c2-trino` 主机。

同样地，在 `c2-trino` 主机上，在 `etc/catalog directory` 中创建一个 `gravitino.properties` 文件：

```test
connector.name = gravitino
gravitino.uri = http://GRAVITINO_HOST_IP:GRAVITINO_HOST_PORT
gravitino.metalake = GRAVITINO_METALAKE_NAME
gravitino.cloud.region-code=c2
```

`gravitino.cloud.region-code=c2` 表示 `c2-trino` 主机被指定用于 `c2` 区域，
因此，针对该区域 catalog 的查询将在 c2-trino 上执行。

确保 `c1-trino` 和 `c2-trino` 上的 `gravitino.uri` 设置都指向同一个 Gravitino 服务器。
验证服务器是否正常运行且连接正常。在进行任何配置更改后，请重启 Trino。

## 创建目录

要验证联邦查询，请创建目录。
下面是一个在 `c2` 区域使用 `gt_mysql` 目录的示例，配置为从 `c1-trino` 进行联邦查询。
在 `c1-trino` CLI 中执行以下命令以创建目录：

要验证联邦查询，首先创建 catalog。以下是配置 `gt_mysql` catalog 的示例
在 `c2` 区域中，用于从 `c1-trino` 进行联邦查询。
在 `c1-trino` CLI 中执行以下命令来创建 catalog：

```sql
CALL gravitino.system.create_catalog(
    'gt_mysql',
    'jdbc-mysql',
    MAP(
        ARRAY['jdbc-url', 'jdbc-user', 'jdbc-password', 'jdbc-driver', 'cloud.region-code', 'cloud.trino.connection-url', 'cloud.trino.connection-user', 'cloud.trino.connection-password'],
        ARRAY['${mysql_uri}/?useSSL=false', 'trino', 'ds123', 'com.mysql.cj.jdbc.Driver', 'c2', 'jdbc:trino://c2-trino:8080', 'admin', '']
    )
);
```

其中：
- `cloud.region-code` 指定 `gt_mysql` 目录位于 `c2` 区域。
- `cloud.trino.connection-url` 指定 `c2` 区域中 Trino 的 Trino JDBC 连接 URL。
- `cloud.trino.connection-user` 指定 `c2` 区域中 Trino 的 Trino JDBC 用户。
- `cloud.trino.connection-password` 指定 `c2` 区域中 Trino 的 Trino JDBC 用户密码。

此配置使 `c1-trino` 能够通过指定的 Trino JDBC 连接信息访问 `c2-trino`。
成功创建目录后，在 `c1-trino` 和 `c2-trino` 上使用 Trino CLI 查看目录。

```sql
SHOW CATALOGS;
```

## 添加数据

创建 catalog 后，下一步是添加数据以验证查询。由于 `Gravitino Trino cascading connector`
不直接支持数据写入，请使用 `c2-trino` CLI 执行以下命令来设置您的数据环境：


```sql
CREATE SCHEMA gt_mysql.gt_db1;

CREATE TABLE gt_mysql.gt_db1.tb01 (
    name VARCHAR(255),
    salary INT
);

INSERT INTO gt_mysql.gt_db1.tb01(name, salary) VALUES ('sam', 11);
INSERT INTO gt_mysql.gt_db1.tb01(name, salary) VALUES ('jerry', 13);
INSERT INTO gt_mysql.gt_db1.tb01(name, salary) VALUES ('bob', 14), ('tom', 12);
```

## 查询验证

成功插入数据后，使用 `c1-trino` CLI 执行以下查询：

```sql
SELECT * FROM gt_mysql.gt_db1.tb01 ORDER BY name;
```

使用 `c2-trino` CLI 验证查询结果：

```sql
SELECT * FROM gt_mysql.gt_db1.tb01 ORDER BY name;
```

`c1-trino` CLI 的输出与 `c2-trino` 相同。