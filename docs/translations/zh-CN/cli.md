---
slug: /cli
keyword: cli
last_update:
  date: 2024-10-23
  author: justinmclean
license: This software is licensed under the Apache License version 2.
title: 命令行界面
---
## 简介

本文档提供使用命令行界面 (CLI) 管理 Apache Gravitino 中元数据的指南。CLI 提供了一种基于终端的替代方案，无需使用代码或 REST 接口即可进行元数据管理。

CLI 允许查看、创建和更新 metalake、catalog、schema、table、model、column、user、role、group、tag、topic 和 fileset 的元数据信息。未来的更新将扩展这些功能。

## 运行 CLI

要运行 Gravitino CLI，使用 Gravitino bin 目录下的 `gcli.sh` 脚本。如果定义了 `GRAVITINO_HOME` 环境变量，可以通过 `$GRAVITINO_HOME/bin/gcli.sh` 在任何位置运行该脚本。

## 用法

运行 Gravitino CLI 命令的通用结构为 `gcli.sh entity command [options]`。

 ```bash
  usage: gcli.sh [metalake|catalog|schema|model|table|column|user|group|tag|topic|fileset] [list|details|create|delete|update|set|remove|properties|revoke|grant] [options]
  Options
 usage: gcli
 -a,--audit              display audit information
    --alias <arg>        model aliases
    --all                on all entities
    --auto <arg>         column value auto-increments (true/false)
 -c,--comment <arg>      entity comment
    --columnfile <arg>   CSV file describing columns
 -d,--distribution       display distribution information
    --datatype <arg>     column data type
    --default <arg>      default column value
    --disable            disable entities
    --enable             enable entities
 -f,--force              force operation
 -g,--group <arg>        group name
 -h,--help               command help information
 -i,--ignore             ignore client/sever version check
 -l,--user <arg>         user name
    --login <arg>        user name
 -m,--metalake <arg>     metalake name
 -n,--name <arg>         full entity name (dot separated)
    --null <arg>         column value can be null (true/false)
 -o,--owner              display entity owner
    --output <arg>       output format (plain/table)
 -P,--property <arg>     property name
 -p,--properties <arg>   property name/value pairs
    --partition          display partition information
    --position <arg>     position of column
    --privilege <arg>    privilege(s)
    --quiet              quiet mode
 -r,--role <arg>         role name
    --rename <arg>       new entity name
 -s,--server             Gravitino server version
    --simple             simple authentication
    --sortorder          display sortorder information
 -t,--tag <arg>          tag name
 -u,--url <arg>          Gravitino URL (default: http://localhost:8090)
    --uris <arg>         model version artifact
 -v,--version            Gravitino client version
 -V,--value <arg>        property value
 -x,--index              display index information
 -z,--provider <arg>     provider one of hadoop, hive, mysql, postgres,
                         iceberg, kafka
 ```

## 命令

以下命令用于实体管理：

- list：列出可用的实体
- details：显示实体的详细信息
- create：创建新实体
- delete：删除现有实体
- update：更新现有实体
- set：设置实体的属性
- remove：移除实体的属性
- properties：显示实体的属性

### 设置 Metalake 名称

由于处理单个 Metalake 是典型场景，可以通过多种方式设置 Metalake 名称，无需在命令行中传递。

1. 通过 `--metalake` 参数在命令行中传递。
2. 通过 `GRAVITINO_METALAKE` 环境变量设置。
3. 存储在 Gravitino CLI 配置文件中。

命令行选项会覆盖环境变量，环境变量会覆盖配置文件。

### 设置 Gravitino URL

由于每条命令都需要设置 Gravitino URL，可以通过多种方式设置该 URL：

1. 通过 `--url` 参数在命令行中传递。
2. 通过 'GRAVITINO_URL' 环境变量设置。
3. 存储在 Gravitino CLI 配置文件中。

命令行选项会覆盖环境变量，环境变量会覆盖配置文件。

### 设置认证类型

认证类型也可以通过多种方式设置：

1. 通过 `--simple` 标志在命令行中传递。
2. 通过 'GRAVITINO_AUTH' 环境变量设置。
3. 存储在 Gravitino CLI 配置文件中。

### CLI 配置文件

Gravitino CLI 可以从配置文件中读取常用的 CLI 选项。默认情况下，该文件是用户主目录下的 `.gravitino`。可以在此文件中设置 metalake、URL 和 ignore 参数。

```text
#
# Gravitino CLI configuration file
#

# Metalake to use
metalake=metalake_demo

# Gravitino server to connect to
URL=http://localhost:8090

# Ignore client/server version mismatch
ignore=true

# Authentication
auth=simple

```

OAuth 认证也可以通过配置文件进行配置。

```text
# Authentication
auth=oauth
serverURI=http://127.0.0.1:1082
credential=xx:xx
token=test
scope=token/test
```

Kerberos 认证也可以通过配置文件进行配置。

```text
# Authentication
auth=kerberos
principal=user/admin@foo.com
keytabFile=file.keytab
```

### 潜在的不安全操作

对于删除数据或重命名 metalake 的操作，会提示用户确认是否运行此命令。可以指定 `--force` 选项来覆盖此行为。

### 管理元数据

所有命令内部均通过 [Java API](../../api/java-api) 执行。

### 显示帮助

显示命令用法的帮助：

```bash
gcli.sh --help
```

### 显示客户端版本

显示客户端版本：

```bash
gcli.sh --version
```

### 显示服务端版本

显示服务端版本：

```bash
gcli.sh --server
```

### 客户端/服务端版本不匹配

如果客户端和服务端运行的 Gravitino 软件版本不同，可能需要忽略客户端/服务端版本检查才能运行命令。可以通过多种方式实现：

1. 通过 `--ignore` 参数在命令行中传递。
2. 通过 `GRAVITINO_IGNORE` 环境变量设置。
3. 存储在 Gravitino CLI 配置文件中。

### 多个属性

对于接受多个属性的命令，可以通过以下几种方式指定：

1. gcli.sh --properties n1=v1,n2=v2,n3=v3

2. gcli.sh --properties n1=v1 n2=v2 n3=v3

3. gcli.sh --properties n1=v1 --properties n2=v2 --properties n3=v3

### 设置属性和标签

 使用 `gcli.sh tag set` 添加标签和设置标签属性需要不同的选项。要添加
 标签，需指定标签（通过 --tag）和要标记的实体（通过 --name）。要设置标签的属性
 （通过 --tag），需要指定要
 设置的属性（通过 --property）和值（通过 --value）。

 要删除标签，同样需要指定标签和实体；要移除标签的属性，需要
 选择标签和属性。

### CLI 命令

运行任何这些命令之前，请在 Gravitino 配置文件或环境变量中设置 metalake。

### Metalake 命令

#### 显示所有 Metalake

```bash
gcli.sh metalake list
```

#### Metalake 详情

```bash
gcli.sh metalake details
```

#### Metalake 审计信息

```bash
gcli.sh metalake details --audit
```

#### 创建 Metalake

```bash
gcli.sh metalake create --metalake my_metalake --comment "This is my metalake"
```

#### 删除 Metalake

```bash
gcli.sh metalake delete
```

#### 重命名 Metalake

```bash
gcli.sh metalake update --rename demo
```

#### 更新 Metalake 注释

```bash
gcli.sh metalake update --comment "new comment"
```

#### Metalake 属性

```bash
gcli.sh metalake properties
```

#### 设置 Metalake 属性

```bash
gcli.sh metalake set --property test --value value
```

#### 移除 Metalake 属性

```bash
gcli.sh metalake remove --property test
```

#### 启用 Metalake

```bash
gcli.sh metalake update -m metalake_demo --enable
```

#### 启用 Metalake 及所有 Catalog

```bash
gcli.sh metalake update -m metalake_demo --enable --all
```

#### 禁用 Metalake

```bash
gcli.sh metalake update -m metalake_demo --disable
```

### Catalog 命令

#### 显示 Metalake 中的所有 Catalog

```bash
gcli.sh catalog list
```

#### Catalog 详情

```bash
gcli.sh catalog details --name catalog_postgres
```

#### Catalog 审计信息

```bash
gcli.sh catalog details --name catalog_postgres --audit
```

#### 创建 Catalog

创建的 catalog 类型由 `--provider` 选项指定。不同的 catalog 需要不同的属性，例如，Hive catalog 需要 metastore-uri 属性。

##### 创建 Hive catalog

```bash
gcli.sh catalog create --name hive --provider hive --properties metastore.uris=thrift://hive-host:9083
```

##### 创建 Iceberg catalog

```bash
gcli.sh catalog create  -name iceberg --provider iceberg --properties uri=thrift://hive-host:9083,catalog-backend=hive,warehouse=hdfs://hdfs-host:9000/user/iceberg/warehouse
```

##### 创建 MySQL catalog

```bash
gcli.sh catalog create  -name mysql --provider mysql --properties jdbc-url=jdbc:mysql://mysql-host:3306?useSSL=false,jdbc-user=user,jdbc-password=password,jdbc-driver=com.mysql.cj.jdbc.Driver
```

##### 创建 Postgres catalog

```bash
gcli.sh catalog create  -name postgres --provider postgres --properties jdbc-url=jdbc:postgresql://postgresql-host/mydb,jdbc-user=user,jdbc-password=password,jdbc-database=db,jdbc-driver=org.postgresql.Driver
```

##### 创建 Kafka catalog

```bash
gcli.sh catalog create --name kafka --provider kafka --properties bootstrap.servers=127.0.0.1:9092,127.0.0.2:9092
```

##### 创建 Doris catalog

```bash
gcli.sh catalog create --name doris --provider doris --properties jdbc-url=jdbc:mysql://localhost:9030,jdbc-driver=com.mysql.jdbc.Driver,jdbc-user=admin,jdbc-password=password
```

##### 创建 Paimon catalog

```bash
gcli.sh catalog create --name paimon --provider paimon --properties catalog-backend=jdbc,uri=jdbc:mysql://127.0.0.1:3306/metastore_db,authentication.type=simple
```

##### 创建 Hudi catalog

```bash
gcli.sh catalog create --name hudi --provider hudi --properties catalog-backend=hms,uri=thrift://127.0.0.1:9083
```

##### 创建 OceanBase catalog

```bash
gcli.sh catalog create --name oceanbase --provider oceanbase --properties jdbc-url=jdbc:mysql://localhost:2881,jdbc-driver=com.mysql.jdbc.Driver,jdbc-user=admin,jdbc-password=password
```

#### 删除 Catalog

```bash
gcli.sh catalog delete --name hive
```

#### 重命名 Catalog

```bash
gcli.sh catalog update --name catalog_mysql --rename mysql
```

#### 更改 Catalog 注释

```bash
gcli.sh catalog update --name catalog_mysql --comment "new comment"
```

#### Catalog 属性

```bash
gcli.sh catalog properties --name catalog_mysql
```

#### 设置 Catalog 属性

```bash
gcli.sh catalog set --name catalog_mysql --property test --value value
```

#### 移除 Catalog 属性

```bash
gcli.sh catalog remove --name catalog_mysql --property test
```

#### 启用 Catalog

```bash
gcli.sh catalog update -m metalake_demo --name catalog --enable 
```

#### 启用 Catalog 及其 Metalake

```bash
gcli.sh catalog update -m metalake_demo --name catalog --enable --all
```

#### 禁用 Catalog

```bash
gcli.sh catalog update -m metalake_demo --name catalog --disable
```

### Schema 命令

#### 显示 Catalog 中的所有 Schema

```bash
gcli.sh schema list --name catalog_postgres
```

#### Schema 详情

```bash
gcli.sh schema details --name catalog_postgres.hr
```

#### Schema 审计信息

```bash
gcli.sh schema details --name catalog_postgres.hr --audit
```

#### 创建 Schema

```bash
gcli.sh schema create --name catalog_postgres.new_db
```

#### Schema 属性

```bash
gcli.sh schema properties --name catalog_postgres.hr
```

Java API 或 Gravitino CLI 不支持设置和移除 schema 属性。

### Table 命令

创建 table 时，列在 CSV 文件中指定，包括列名、数据类型、注释、表示列是否可为空的 true 或 false、表示列是否自增的 true 或 false、默认值和默认类型。并非所有列都需要指定，只需指定名称和数据类型列即可。如果未指定，注释默认为 null，可为空性默认为 true，自增默认为 false。如果仅指定了默认值，则默认类型与该列的数据类型相同。

示例 CSV 文件

```text
Name,Datatype,Comment,Nullable,AutoIncrement,DefaultValue,DefaultType
name,String,person's name
ID,Integer,unique id,false,true
location,String,city they work in,false,false,Sydney,String
```

#### 显示所有 Table

```bash
gcli.sh table list --name catalog_postgres.hr
```

#### Table 详情

```bash
gcli.sh table details --name catalog_postgres.hr.departments
```

#### Table 审计信息

```bash
gcli.sh table details --name catalog_postgres.hr.departments --audit
```

#### Table 分布信息

```bash
gcli.sh table details --name catalog_postgres.hr.departments --distribution
```

#### Table 分区信息

```bash
gcli.sh table details --name catalog_postgres.hr.departments --partition
```

#### Table 排序信息

```bash
gcli.sh table details --name catalog_postgres.hr.departments --sortorder
```

### Table 索引

```bash
gcli.sh table details --name catalog_mysql.db.iceberg_namespace_properties --index
```

#### 删除 Table

```bash
gcli.sh table delete --name catalog_postgres.hr.salaries
```

#### Table 属性

```bash
gcli.sh table properties --name catalog_postgres.hr.salaries
```

#### 设置 Table 属性

```bash
gcli.sh table set --name catalog_postgres.hr.salaries --property test --value value
```

#### 移除 Table 属性

```bash
gcli.sh table remove --name catalog_postgres.hr.salaries --property test
```

#### 创建 Table

```bash
gcli.sh table create --name catalog_postgres.hr.salaries --comment "comment" --columnfile ~/table.csv
```

### User 命令

#### 创建 User

```bash
gcli.sh user create --user new_user
```

#### User 详情

```bash
gcli.sh user details --user new_user
```

#### 列出所有 User

```bash
gcli.sh user list
```

#### Role 审计信息

```bash
gcli.sh user details --user new_user --audit
```

#### 删除 User

```bash
gcli.sh user delete --user new_user
```

### Group 命令

#### 创建 Group

```bash
gcli.sh group create --group new_group
```

#### Group 详情

```bash
gcli.sh group details --group new_group
```

#### 列出所有 Group

```bash
gcli.sh group list
```

#### Group 审计信息

```bash
gcli.sh group details --group new_group --audit
```

#### 删除 Group

```bash
gcli.sh group delete --group new_group
```

### Tag 命令

#### Tag 详情

```bash
gcli.sh tag details --tag tagA
```

#### 创建 Tag

```bash
gcli.sh tag create --tag tagA tagB
```

#### 列出所有 Tag

```bash
gcli.sh tag list
```

#### 删除 Tag

```bash
gcli.sh tag delete --tag tagA tagB
```

#### 向实体添加 Tag

```bash
gcli.sh tag set --name catalog_postgres.hr --tag tagA tagB
```

#### 从实体移除 Tag

```bash
gcli.sh tag remove --name catalog_postgres.hr --tag tagA tagB
```

#### 从实体移除所有 Tag

```bash
gcli.sh tag remove --name catalog_postgres.hr
```

#### 列出实体上的所有 Tag

```bash
gcli.sh tag list --name catalog_postgres.hr
```

#### 列出 Tag 的属性

```bash
gcli.sh tag properties --tag tagA
```

#### 设置 Tag 的属性

```bash
gcli.sh tag set --tag tagA --property test --value value
```

#### 删除 Tag 的属性

```bash
gcli.sh tag remove --tag tagA --property test
```

#### 重命名 Tag

```bash
gcli.sh tag update --tag tagA --rename newTag
```

#### 更新 Tag 注释

```bash
gcli.sh tag update --tag tagA --comment "new comment"
```

### Owner 命令

#### 列出 Owner

```bash
gcli.sh catalog details --owner --name postgres
```

#### 将 Owner 设置为 User

```bash
gcli.sh catalog set --owner --user admin --name postgres
```

#### 将 Owner 设置为 Group

```bash
gcli.sh catalog set --owner --group groupA --name postgres
```

### Role 命令

授予或撤销权限时，可以使用以下权限。

create_catalog, use_catalog, create_schema, use_schema, create_table, modify_table, select_table, create_fileset, write_fileset, read_fileset, create_topic, produce_topic, consume_topic, manage_users, create_role, manage_grants

注意，某些权限仅对特定实体有效。

#### Role 详情

```bash
gcli.sh role details --role admin
```

#### 列出所有 Role

```bash
gcli.sh role list
```

#### Role 审计信息

```bash
gcli.sh role details --role admin --audit
```

#### 创建 Role

```bash
gcli.sh role create --role admin
```

#### 删除 Role

```bash
gcli.sh role delete --role admin
```

#### 向 User 添加 Role

```bash
gcli.sh user grant --user new_user --role admin
```

#### 从 User 移除 Role

```bash
gcli.sh user revoke --user new_user --role admin
```

#### 从 User 移除所有 Role

```bash
gcli.sh user revoke --user new_user --all
```

#### 向 Group 添加 Role

```bash
gcli.sh group grant --group groupA --role admin
```

#### 从 Group 移除 Role

```bash
gcli.sh group revoke --group groupA --role admin
```

#### 从 Group 移除所有 Role

```bash
gcli.sh group revoke --group groupA --all
```

### Privilege 命令

#### 授予 Privilege

```bash
gcli.sh role grant --name catalog_postgres --role admin --privilege create_table modify_table
```

#### 撤销 Privilege

```bash
gcli.sh role revoke --metalake metalake_demo --name catalog_postgres --role admin --privilege create_table modify_table
```

#### 撤销所有 Privilege

```bash
gcli.sh role revoke --metalake metalake_demo --name catalog_postgres --role admin --all
```

### Topic 命令

#### Topic 详情

```bash
gcli.sh topic details --name kafka.default.topic3
```

#### 创建 Topic

```bash
gcli.sh topic create --name kafka.default.topic3
```

#### 列出所有 Topic

```bash
gcli.sh topic list --name kafka.default
```

#### 删除 Topic

```bash
gcli.sh topic delete --name kafka.default.topic3
```

#### 更改 Topic 注释

```bash
gcli.sh topic update --name kafka.default.topic3 --comment new_comment
```

#### Topic 属性

```bash
gcli.sh topic properties --name kafka.default.topic3
```

#### 设置 Topic 属性

```bash
gcli.sh topic set --name kafka.default.topic3 --property test --value value
```

#### 移除 Topic 属性

```bash
gcli.sh topic remove --name kafka.default.topic3 --property test
```

### Fileset 命令

#### 创建 Fileset

```bash
gcli.sh fileset create --name hadoop.schema.fileset --properties managed=true,location=file:/tmp/root/schema/example
```

#### 列出 Fileset

```bash
gcli.sh fileset list --name hadoop.schema
```

#### Fileset 详情

```bash
gcli.sh fileset details --name hadoop.schema.fileset
```

#### 删除 Fileset

```bash
gcli.sh fileset delete --name hadoop.schema.fileset
```

#### 更新 Fileset 注释

```bash
gcli.sh fileset update --name hadoop.schema.fileset --comment new_comment
```

#### 重命名 Fileset

```bash
gcli.sh fileset update --name hadoop.schema.fileset --rename new_name
```

#### Fileset 属性

```bash
gcli.sh fileset properties --name hadoop.schema.fileset 
```

#### 设置 Fileset 属性

```bash
gcli.sh fileset set  --name hadoop.schema.fileset --property test --value value
```

#### 删除 Fileset 属性

```bash
gcli.sh fileset remove --name hadoop.schema.fileset --property test
```

### 列命令

需注意，部分命令是否受支持取决于底层数据库的支持情况。

设置列数据类型时，支持以下基本类型：
null, boolean, byte, ubyte, short, ushort, integer, uinteger, long, ulong, float, double, date, time, timestamp, tztimestamp, intervalyear, intervalday, uuid, string, binary

此外，还支持 decimal(precision,scale)、fixed(length)、fixedchar(length) 和 varchar(length)。

#### 显示所有列

```bash
gcli.sh column list --name catalog_postgres.hr.departments
```

#### 列审计信息

```bash
gcli.sh column details --name catalog_postgres.hr.departments.name --audit
```

#### 添加列

```bash
gcli.sh column create --name catalog_postgres.hr.departments.value --datatype long
gcli.sh column create --name catalog_postgres.hr.departments.money --datatype "decimal(10,2)"
gcli.sh column create --name catalog_postgres.hr.departments.name --datatype "varchar(100)"
gcli.sh column create --name catalog_postgres.hr.departments.fullname --datatype "varchar(250)" --default "Fred Smith" --null=false
```

#### 删除列

```bash
gcli.sh  column delete --name catalog_postgres.hr.departments.money
```

#### 更新列

```bash
gcli.sh column update --name catalog_postgres.hr.departments.value --rename values
gcli.sh column update --name catalog_postgres.hr.departments.values --datatype "varchar(500)"
gcli.sh column update --name catalog_postgres.hr.departments.values --position name
gcli.sh column update --name catalog_postgres.hr.departments.name --null true
```

#### 简单认证

```bash
gcli.sh <normal command> --simple
```

### 认证

#### 带用户名的简单认证

```bash
gcli.sh <normal command> --simple --login userName
```

### Model 命令

#### 创建 Model

```bash
gcli.sh model create --name catalog_model.schema.model
```

#### 列出 Model

```bash
gcli.sh model list --name catalog_model.schema
```

#### Model 详情

```bash
gcli.sh model details --name catalog_model.schema.model
```

#### Model 审计信息

```bash
gcli.sh model details --name catalog_model.schema.model --audit
```

#### 删除 Model

```bash
gcli.sh model delete --name catalog_model.schema.model
```

#### 更新 Model 注释

```bash
gcli.sh model update --name catalog_model.schema.model --comment new_comment
```

#### 重命名 Model

```bash
gcli.sh model update --name catalog_model.schema.model --rename new_name
```

#### 设置 Model 属性

```bash
gcli.sh model set --name catalog_model.schema.model --property k --value v
```

#### 删除 Model 属性

```bash
gcli.sh model remove --name catalog_model.schema.model --property k
```

#### 关联 Model 版本

```bash
gcli.sh model update --name catalog_model.schema.model --uris s3=s3://path,hdfs=hdfs://path --alias alias1
```

#### 更新 Model 版本注释

```bash
gcli.sh model update --name catalog_model.schema.model --version 0 --comment new_comment
```

#### 为 Model 版本添加别名

```bash
gcli.sh model update --name catalog_model.schema.model --version 0 --newalias alias1
```

#### 删除 Model 版本的别名

```bash
gcli.sh model remove --name catalog_model.schema.model --version 0 --removealias alias1
```

#### 设置 Model 版本属性

```bash
gcli.sh model set --name catalog_model.schema.model --version 0 --property k --value v
```

#### 删除 Model 版本属性

```bash
gcli.sh model remove --name catalog_model.schema.model --version 0 --property k
```

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=CLI" alt="" />