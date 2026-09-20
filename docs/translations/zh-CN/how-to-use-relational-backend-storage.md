---
title: "Relational Backend Storage"
slug: "/how-to-use-relational-backend-storage"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Apache Gravitino 通过 JDBC 后端将其元数据存储在关系型数据库中。H2 是
默认的，无需配置，但 Gravitino 不对
存储在 H2 中的元数据提供一致性或持久性保证。请仅将其用于本地开发和测试。存放您
关心的元数据的服务器应使用 MySQL 或 PostgreSQL。

本页面涵盖如何将 Gravitino 服务器指向 MySQL 或 PostgreSQL。关于连接池和
无论您使用哪种数据库都适用的版本保留属性，以及 H2 存储路径，
请参见 [Gravitino 服务器配置](gravitino-server-config.md#storage-backend)。

## 快速开始

设置 MySQL 或 PostgreSQL 归结为服务器配置文件中的四个属性，
`${GRAVITINO_HOME}/conf/gravitino.conf`：

```text
# conf/gravitino.conf
gravitino.entity.store.relational.jdbcUrl      = {jdbc_url}
gravitino.entity.store.relational.jdbcDriver   = {driver_class}
gravitino.entity.store.relational.jdbcUser     = {username}
gravitino.entity.store.relational.jdbcPassword = {password}
```

`gravitino.entity.store` 和 `gravitino.entity.store.relational` 已经默认为 `relational`
和 `JDBCBackend`。保持不变即可。

要使用的值，以及每个值所需的驱动程序：

| 数据库            | JDBC URL                                                          | 驱动类               | 驱动 Jar                    |
|---------------------|-------------------------------------------------------------------|----------------------------|-------------------------------|
| H2（默认）        | `jdbc:h2`                                                         | `org.h2.Driver`            | 随发行版捆绑提供 |
| MySQL 5.7 或 8.0    | `jdbc:mysql://{host}:3306/{database}`                             | `com.mysql.cj.jdbc.Driver` | `com.mysql:mysql-connector-j` |
| PostgreSQL 12 至 16 | `jdbc:postgresql://{host}:5432/{database}?currentSchema={schema}` | `org.postgresql.Driver`    | `org.postgresql:postgresql`   |

其他 PostgreSQL 版本未经社区测试，可能无法正常工作。

Gravitino 仅在 H2 上自动初始化其 schema，通过在启动时运行
`scripts/h2/schema-{version}-h2.sql`。对于 MySQL 和 PostgreSQL，你需要创建数据库
并在首次启动服务器之前自行运行脚本。请按照以下
步骤操作。

## 设置 MySQL

**1. 创建数据库。** Gravitino 不会为您创建它。

```sql
CREATE DATABASE {database};
```

**2. 运行 schema 脚本。** 如果您尚未下载并解压 Gravitino 发行包，请
先进行此操作；请参阅 [如何安装 Gravitino](how-to-install.md)。MySQL 脚本位于
`${GRAVITINO_HOME}/scripts/mysql/` 中。运行 `schema-*-mysql.sql` 文件，匹配您的 Gravitino
版本，针对您刚刚创建的数据库执行：

```shell
mysql -h {host} -u {username} -p {database} < ${GRAVITINO_HOME}/scripts/mysql/schema-{version}-mysql.sql
```

如果您是要推进现有部署而不是从头开始，请运行
`upgrade-{old_version}-to-{new_version}-mysql.sql` 脚本，按顺序执行，每个版本步骤一个。

**3. 安装驱动。** 从以下地址下载与您的 MySQL 版本匹配的 MySQL Connector/J jar 包：
[Maven Central](https://central.sonatype.com/artifact/com.mysql/mysql-connector-j)，并将其放置在
`${GRAVITINO_HOME}/libs/` 目录中。该构件已从 `mysql:mysql-connector-java` 重命名为
`com.mysql:mysql-connector-j`，因此该 jar 包名为 `mysql-connector-j-{version}.jar`。旧版的
`mysql-connector-java-{version}.jar` 构建仍然可用，但不再接收修复。

**4. 配置服务器。** 在 `${GRAVITINO_HOME}/conf/gravitino.conf` 中：

```text
# conf/gravitino.conf
gravitino.entity.store.relational.jdbcUrl      = jdbc:mysql://{host}:3306/{database}
gravitino.entity.store.relational.jdbcDriver   = com.mysql.cj.jdbc.Driver
gravitino.entity.store.relational.jdbcUser     = {username}
gravitino.entity.store.relational.jdbcPassword = {password}
```

**5. 启动服务器。**

```shell
${GRAVITINO_HOME}/bin/gravitino.sh start
```

## 设置 PostgreSQL

PostgreSQL 遵循相同的五个步骤，但有一个区别：Gravitino 指向内部的 schema
数据库，因此你需要创建这两者，并且 JDBC URL 会指定这两者。两者均不可省略。

**1. 创建数据库和架构。**

```postgresql
psql --username=postgres --password

CREATE DATABASE {database};
\c {database}
CREATE SCHEMA {schema};
```

**2. 运行 schema 脚本。** PostgreSQL 脚本位于 `${GRAVITINO_HOME}/scripts/postgresql/` 中。
首先设置搜索路径，以便表存入您的 schema 而不是 `public`：

```postgresql
\c {database}
SET search_path TO {schema};
\i ${GRAVITINO_HOME}/scripts/postgresql/schema-{version}-postgresql.sql
```

若要推进现有部署，请改为按顺序运行
`upgrade-{old_version}-to-{new_version}-postgresql.sql` 脚本。

**3. 安装驱动程序。** 从以下地址下载当前的 pgJDBC 驱动程序：
[jdbc.postgresql.org](https://jdbc.postgresql.org/download/) ，并将 `postgresql-{version}.jar` 放置在
`${GRAVITINO_HOME}/libs/` 中。请获取最新版本，而不是锁定旧版本；若干
早期版本存在已发布的 CVE。

**4. 配置服务器。** 注意 `currentSchema` 参数：

```text
# conf/gravitino.conf
gravitino.entity.store.relational.jdbcUrl      = jdbc:postgresql://{host}:5432/{database}?currentSchema={schema}
gravitino.entity.store.relational.jdbcDriver   = org.postgresql.Driver
gravitino.entity.store.relational.jdbcUser     = {username}
gravitino.entity.store.relational.jdbcPassword = {password}
```

**5. 启动服务器。**

```shell
${GRAVITINO_HOME}/bin/gravitino.sh start
```

## 验证连接

就绪端点会探测实体存储，因此它直接回答了这个问题。一台服务器，如果它
连接到了其数据库，就会返回 `UP`：

```shell
curl http://{host}:8090/health/ready
```

如果后端不可达或响应缓慢，端点会返回 503，且 `entityStore` 检查处于
`DOWN` 状态。请参阅
[Health Check Endpoints](gravitino-server-config.md#health-check-endpoints) 以了解响应
格式和探针超时时间。
