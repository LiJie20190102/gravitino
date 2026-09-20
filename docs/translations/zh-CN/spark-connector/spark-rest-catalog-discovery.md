---
slug: /spark-connector/spark-rest-catalog-discovery
keyword: spark lakehouse REST catalog discovery Lance
license: This software is licensed under the Apache License version 2.
---
## 概述

Gravitino Spark 连接器可以发现由湖仓 REST 服务器提供的目录，并
自动将它们注册到 Spark 中。一个 Spark 会话只需要发现插件和一个 REST
服务器 URI（每种湖仓格式一个）。添加到服务器的目录将在 Spark
会话重启后可用。

支持 Lance REST 发现。相应的 Iceberg REST 提供程序计划单独实现。

## 要求

将以下两个构件都添加到 Spark 应用程序类路径中：

- 与 Spark 版本匹配的 Gravitino Spark 连接器运行时。
- 一个兼容的 `lance-spark-bundle`，其中包含 `org.lance.spark.LanceNamespaceSparkCatalog` 和
  `org.lance.spark.extensions.LanceSparkSessionExtensions`。

发现提供程序使用 Lance Spark 捆绑包中附带的 Lance Namespace 客户端。Gravitino
不会在其 Spark 连接器运行时中打包该客户端的另一份副本。

## 配置

配置发现插件和 Lance REST 服务器 URI：

```text
spark.plugins=org.apache.gravitino.spark.connector.plugin.restcatalog.GravitinoLakehouseRESTDiscoveryPlugin
spark.sql.gravitino.lanceREST.uri=http://127.0.0.1:9101/lance
```

当还需要常规 Gravitino Spark 插件时，发现插件必须列在前面：

```text
spark.plugins=org.apache.gravitino.spark.connector.plugin.restcatalog.GravitinoLakehouseRESTDiscoveryPlugin,\
              org.apache.gravitino.spark.connector.plugin.GravitinoSparkPlugin
```

如果顺序颠倒，Spark 启动会失败。先初始化发现允许插件
区分用户编写的目录配置与常规插件生成的条目。

对于从 Lance REST 服务器发现的每个目录，插件会生成：

```text
spark.sql.catalog.<catalogName>=org.lance.spark.LanceNamespaceSparkCatalog
spark.sql.catalog.<catalogName>.impl=rest
spark.sql.catalog.<catalogName>.uri=<spark.sql.gravitino.lanceREST.uri>
spark.sql.catalog.<catalogName>.parent=<catalogName>
```

它还会将 `org.lance.spark.extensions.LanceSparkSessionExtensions` 添加到
`spark.sql.extensions`，当该扩展已配置时不会添加重复项。

### 目录属性

以下前缀下的属性会复制到每个发现的 Lance 目录：

```text
spark.sql.gravitino.lanceREST.catalogProperties.<key>=<value>
```

配置优先级从高到低为：

1. 用户定义的 `spark.sql.catalog.<name>` 拥有完整目录名称，并禁用该发现名称的自动
   注册。
2. 用户定义的 `spark.sql.catalog.<name>.<key>` 会覆盖该目录的值。
3. 提供程序生成的路由属性，例如 `impl`、`uri` 和 `parent`。
4. 全局 `lanceREST.catalogProperties.<key>` 默认值。

发现提供程序不会生成 `lance.storage.*` 配置。存储选项继续
来自 Lance REST 服务或显式 Spark 目录属性。

当 Lance REST 服务器使用的命名空间分隔符不是默认的 `$` 时，设置
`spark.sql.gravitino.lanceREST.catalogProperties.namespaceDelimiter`。该属性用于
发现请求，并且也会复制到每个发现的目录。

## 注册策略

默认情况下，每个发现的目录都以其发现的名称注册。要过滤或重命名
目录，请实现
`org.apache.gravitino.spark.connector.plugin.restcatalog.CatalogRegistrationPolicy`，该类具有公共
无参数构造函数，并配置其类名：

```text
spark.sql.gravitino.REST.registrationPolicy=com.example.MyCatalogRegistrationPolicy
```

该策略接收格式标记（`lance`）和发现的目录名称。重命名后的 Spark
目录仍使用发现的名称作为其 `parent`，因此 REST 路由仍以服务器为准。
如果策略返回空名称、无效标识符、重复名称，或
已被用户配置拥有的名称，Spark 启动会失败。

Gravitino 接受 Spark 无法在不加引号时引用的目录名称，例如包含
连字符的名称。如果没有配置策略，此类目录会以 WARN 级别记录并跳过，而不是
导致 Spark 启动失败，因此一个不可用的名称不会阻止会话启动。配置一个
策略，将其重命名为 Spark 接受的标识符。

## 限制

- 每种格式每个 Spark 会话支持一个 REST 服务器 URI。
- 发现是启动依赖项，没有回退机制。如果驱动程序启动时无法访问 REST 服务器，
  插件会失败，整个 Spark 会话将无法启动。
- 自动 Lance 发现不支持经过身份验证的 REST 列表。目录属性
  会应用于生成的 Spark 目录，但不会用于对发现请求进行身份验证。
- 发现仅在驱动程序启动期间运行；重启 Spark 会话以观察目录的添加
  或移除。
- Spark 注册的目录是延迟加载的，因此 `SHOW CATALOGS` 可能不会显示它，直到它被
  引用。