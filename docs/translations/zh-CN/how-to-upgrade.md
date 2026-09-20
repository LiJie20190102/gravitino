---
title: "Upgrade Gravitino"
slug: "/how-to-upgrade"
license: "This software is licensed under the Apache License version 2."
---

## 简介

本文档描述如何升级后端
Gravitino 实例的 schema 从一个 Gravitino 发布版本到另一个
Gravitino 发布版本。例如，通过遵循下面列出的
步骤，可以将 Gravitino 0.6.0 schema 升级为
Gravitino 0.7.0 schema。在尝试此项目之前，我们
强烈建议您通读本文档中的所有
步骤，并熟悉所需的工具。

## 升级步骤

### 步骤 1：关闭 Gravitino 实例

关闭 Gravitino 实例并限制对
Apache Gravitino 数据库的访问。非常重要的一点是，没有其他人
访问或修改数据库内容，在您
执行架构升级时。

### 步骤 2：备份 Gravitino 实例

创建数据库备份。这将允许
您撤销在升级过程中所做的任何更改，如果
出现问题。

#### MySQL

对于 MySQL，您可以使用以下命令来备份数据库：

```shell
mysqldump --opt <db_name> > backup.sql
```
请注意，您可能还需要指定主机名和用户名
使用 `--host` 和 `--user` 命令行开关。

#### H2

完成此任务的最简单方法是
通过创建包含您的数据库的目录副本。

#### PostgreSQL

对于 PostgreSQL，您可以使用以下命令来备份数据库：

```shell
pg_dump -U username -h hostname -d database_name -n schema_name -Fc -f data_backup.dump
```
`-Fc` 选项会生成 PostgreSQL 的压缩二进制转储，采用其
自定义格式，可以使用 `pg_restore` 进行恢复。与
仅模式转储不同，此备份包含模式和数据，这
是完全回滚所必需的。

如果您正在运行由独立 PostgreSQL 数据库提供支持的 Iceberg REST Catalog (IRC) 服务，
也请对其进行备份：

```shell
pg_dump -U username -h hostname -d irc_database_name -n schema_name -Fc -f data_backup_irc.dump
```

### 步骤 3：转储 Gravitino 数据库

将你的 Gravitino 数据库模式转储到文件中

#### MySQL

使用 mysqldump 工具将数据库架构转储到文件：

```shell
mysqldump --skip-add-drop-table --no-data <db_name> > schema-x.y.z-mysql.sql
```

#### H2

对于 H2，你可以使用 `Script` 工具将数据库架构导出到文件：

```shell
wget https://repo1.maven.org/maven2/com/h2database/h2/1.4.200/h2-1.4.200.jar
java -cp h2-1.4.200.jar org.h2.tools.Script -url "jdbc:h2:file:<db_file>;DB_CLOSE_DELAY=-1;MODE=MYSQL" -user <user> -password <password> -script backup.sql
```
请注意，您可能需要指定您的 h2 文件路径、用户名和密码

#### PostgreSQL

对于 PostgreSQL，您可以使用以下命令将数据库架构转储到文件中：

```shell
pg_dump -U username -h hostname -d database_name -n schema_name -s -f schema-x.y.z-postgresql.sql
```

注意：`-s` 标志以纯 SQL 格式转储仅模式。这是
与第 2 步中用于备份的 `-Fc` 自定义格式不同，
后者会生成一个必须使用 `pg_restore` 恢复的二进制转储文件。

### 第 4 步：确定现有 Schema 与官方 Schema 之间的差异

模式升级脚本假定您要升级的模式
与您特定版本的
Gravitino 的官方模式高度匹配。此目录中名称类似于
`schema-x.y.z-<type>.sql` 的文件包含官方模式的转储，
对应于每个已发布的 Gravitino 版本。您可以
确定您的模式与官方模式之间的差异，
方法是将官方转储的内容与模式转储进行比较，
即您在上一步中创建的转储。

某些差异是可以接受的，并且不会干扰
升级过程，例如对象排序或
注释的差异。但是，表结构、列类型或
缺失的表/索引需要手动解决，
否则升级脚本将无法完成。

### 步骤 5：应用升级脚本

您现在已准备好运行模式升级脚本。如果您正在
从 Gravitino 0.6.0 升级到 Gravitino 0.7.0，您需要运行
`upgrade-0.6.0-to-0.7.0-<type>.sql` 脚本，但如果您正在
从 0.6.0 升级到 0.8.0，您将需要运行 0.6.0 到 0.7.0 的升级
脚本，随后运行 0.7.0 到 0.8.0 的升级脚本。

#### MySQL

假设您正在将 Gravitino server 的版本从 0.6.0 升级到 0.8.0

```shell
mysql --verbose
mysql> use <db_name>;
Database changed
mysql> source upgrade-0.6.0-to-0.7.0-mysql.sql
mysql> source upgrade-0.7.0-to-0.8.0-mysql.sql
```

#### H2

对于 H2，你可以使用 `RunScript` 工具来应用升级脚本：

```shell
java -cp h2-1.4.200.jar org.h2.tools.RunScript -url "jdbc:h2:file:<db_file>;DB_CLOSE_DELAY=-1;MODE=MYSQL" -user <user> -password <password> -script upgrade-0.6.0-to-0.7.0-h2.sql
java -cp h2-1.4.200.jar org.h2.tools.RunScript -url "jdbc:h2:file:<db_file>;DB_CLOSE_DELAY=-1;MODE=MYSQL" -user <user> -password <password> -script upgrade-0.7.0-to-0.8.0-h2.sql
```

#### PostgreSQL

对于 PostgreSQL，您可以使用以下命令来应用升级脚本：

```shell
psql -U username -h hostname -d database_name -c "SET search_path TO schema_name;" -f upgrade-0.6.0-to-0.7.0-postgresql.sql
psql -U username -h hostname -d database_name -c "SET search_path TO schema_name;" -f upgrade-0.7.0-to-0.8.0-postgresql.sql
```


这些脚本应该运行完成且没有任何错误。如果你
确实遇到了错误，你需要分析原因并尝试
将其追溯到前面的某个步骤。

### 步骤 6：验证升级

升级过程的最后一步是验证您刚刚
升级的 schema 与官方 schema 进行对比，针对您特定的
版本的 Gravitino。这是通过重复步骤 (3) 和
(4) 来完成的，但这次是与官方版本的
升级后 schema 进行对比，例如，如果您将 schema 升级到了 Gravitino 0.8.0，那么
您将需要将您的 schema dump 与
`schema-0.8.0-<type>.sql` 的内容进行对比

## 通过 Helm Chart 升级

:::note
Gravitino Helm chart 目前不支持自动模式迁移。在运行
`helm upgrade` 之前，你必须手动备份数据库（参见 [步骤 2](#step-2-backup-your-gravitino-instance)）
并应用相应的 SQL 升级脚本（参见 [步骤 5](#step-5-apply-the-upgrade-scripts)）。
:::

本节介绍如何升级由 Gravitino Helm chart 管理的 Gravitino 部署

### 步骤 1：准备新的 values 文件

为目标版本创建一个新的 values 文件（例如，`values-<new-version>.yaml`），基于
前一个文件。将 `image.tag` 更新为目标版本，并应用任何特定于版本的字段
更改，如下文各节中所列。

#### 1.2.0 → 1.3.0

| 字段                                           | 1.2.0                  | 1.3.0                 |
| --------------------------------------------- | ---------------------- | --------------------- |
| `image.tag`                                   | `1.2.0`                | `1.3.0`               |
| `env.GRAVITINO_HOME`                          | `/root/gravitino`      | `/opt/gravitino`      |
| `extraVolumeMounts[gravitino-log].mountPath`  | `/root/gravitino/logs` | `/opt/gravitino/logs` |

关键点：
- `GRAVITINO_HOME` 路径从 `/root/gravitino` 更改为 `/opt/gravitino`。请确保
`extraVolumeMounts` 及任何其他路径引用得到一致的更新。

### 第 2 步：运行 Helm 升级

```shell
helm upgrade gravitino <path-to-gravitino-helm-chart>/gravitino-helm-<new-version>.tgz \
  -n <namespace> \
  -f values-<new-version>.yaml
```

### 步骤 3：验证发布

检查所有 pod 是否使用新镜像健康启动：

```shell
kubectl rollout status deployment/<release-name>-gravitino-helm -n <namespace>
kubectl get pods -n <namespace>
```

确认运行中的镜像标签与目标版本匹配：

```shell
kubectl get pods -n <namespace> -o jsonpath='{.items[*].spec.containers[*].image}'
```

## 升级失败时回滚

> **重要：**在恢复数据库之前停止 Gravitino 服务器
> 以避免因并发写入导致的数据损坏。

如果在升级过程中遇到错误，您可以
从步骤 2 中创建的备份恢复您的数据库。

### MySQL

使用备份文件恢复您的数据库。`mysqldump`
备份默认包含 `DROP TABLE` 语句（通过 `--opt`），
因此它会自动替换已升级的表：

```shell
mysql -u username -h hostname --database=db_name < backup.sql
```

### H2

用您制作的副本替换当前的数据库目录
在备份步骤中：

```shell
rm -rf <db_directory>
cp -r <db_directory_backup> <db_directory>
```

### PostgreSQL

使用带 `--clean` 的 `pg_restore` 在
一个事务中恢复它们之前删除现有对象。这比手动
先删除模式更安全：

```shell
pg_restore -U username -h hostname -d database_name -n schema_name --clean --if-exists --single-transaction data_backup.dump
```

注意：`pg_restore --clean` 仅删除存在于
转储文件中的对象。如果升级脚本添加了不在
备份中的新表或序列，这些对象将不会被自动删除。
恢复后验证模式是否与预期状态匹配。

恢复后，验证您的 Gravitino 实例是否启动
成功，并使用恢复的数据库，在尝试
再次升级之前。

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=HowToUpgrade" alt="" />
