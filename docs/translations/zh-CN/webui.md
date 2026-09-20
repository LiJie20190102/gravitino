---
title: "Web UI"
slug: "/webui"
keyword: "webui"
last_update:
  date: 2024-10-30
  author: LauraXia123
license: "This software is licensed under the Apache License version 2."
---

## 简介

本文档主要概述了用户如何使用 Web UI 在 Apache Gravitino 中管理元数据，该图形界面可通过 Web 浏览器访问，作为编写代码或使用 REST 接口的替代方案。

集成 [OAuth 设置](security/how-to-authenticate.md) 以查看、添加、修改和删除 metalake，创建 catalog，以及查看 catalog、schema 和 table 等功能。

[构建](./how-to-build.md#quick-start) 并 [部署](./getting-started/index.md#local-workstation) Gravitino Web UI，并在浏览器中打开 `http://<gravitino-host>:<gravitino-port>`，默认为 [http://localhost:8090](http://localhost:8090)。

## 初始页面

Gravitino 中显示的 Web UI 主页取决于 OAuth 模式的配置参数，详情请参见 [Security](security/how-to-authenticate.md)。

设置 `gravitino.authenticators` 参数：[`simple`](#simple-mode)、[`basic`](../security/how-to-authenticate.md#basic-mode) 或 [`oauth`](#oauth-mode)。Simple 模式是默认的身份验证选项。如果设置了多个身份验证器，默认使用第一个。

:::tip
更改配置后，请务必重启 Gravitino 服务器。

`<path-to-gravitino>/bin/gravitino.sh restart`
:::

### 简单模式

```text
gravitino.authenticators = simple
```

将配置参数 `gravitino.authenticators` 设置为 `simple`，Web UI 将显示主页 (Metalakes)。

![webui-metalakes-simple](./assets/webui/metalakes-simple.png)

在右上角，UI 显示当前 Gravitino 版本。

主内容区显示现有的 metalake 列表。

### OAuth 模式

```text
gravitino.authenticators = oauth
```

将配置参数 `gravitino.authenticators` 设置为 `oauth`，Web UI 将显示登录页面。

:::caution
如果同时设置了 `OAuth` 和 `HTTPS`，由于不同浏览器的安全权限规则不同，为避免跨域错误，
建议使用 [Chrome](https://www.google.com/chrome/) 浏览器进行访问和操作。

例如 Safari 需要启用开发者菜单，并从开发菜单中选择 `Disable Cross-Origin Restrictions`。
:::

![webui-login-with-oauth](./assets/webui/login-with-oauth.png)

1. 输入与您的特定配置对应的值。有关详细说明，请参阅 [Security](security/how-to-authenticate.md)。

2. 点击 `LOGIN` 按钮即可进入主页。

![webui-metalakes-oauth](./assets/webui/metalakes-oauth.png)

右上角有一个图标按钮，点击后会跳转到登录页面。

## 管理元数据

> 所有管理操作均通过使用 [REST API](api/rest/gravitino-rest-api) 来执行

### Metalake

#### 创建 Metalake

请参阅 [API 参考](./getting-started/index.md#interact-with-apache-gravitino-api) 以了解底层的 REST 调用。

在主页上，点击 `CREATE METALAKE` 按钮会显示一个创建 metalake 的对话框。

![create-metalake-dialog](./assets/webui/create-metalake-dialog.png)

创建 metalake 需要以下字段：

1. **名称**(**_必填_**): metalake 的名称。
2. **注释**(_可选_): metalake 的注释。
3. **属性**(_可选_): 点击 `ADD PROPERTY` 按钮以添加自定义属性。

![metalake-list](./assets/webui/metalake-list.png)

你可以对 metalake 执行 3 种操作。

![metalake-actions](./assets/webui/metalake-actions.png)

#### 显示 Metalake 详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此 metalake 的详细信息。

![metalake-details](./assets/webui/metalake-details.png)

#### 编辑 Metalake

点击表格单元格中的操作图标 <Icon icon='mdi:square-edit-outline' fontSize='24' /> 。

显示修改所选 metalake 字段的对话框。

![create-metalake-dialog](./assets/webui/create-metalake-dialog.png)

#### 禁用 Metalake

Metalake 在成功创建后默认为使用中状态。

将鼠标悬停在 metalake 名称旁边的开关上，即可看到 'In-use' 提示。

![metalake-in-use](./assets/webui/metalake-in-use.png)

点击开关将禁用 metalake，将鼠标悬停在 metalake 名称旁边的开关上可看到“未使用”的提示。

![metalake-not-in-use](./assets/webui/metalake-not-in-use.png)

#### 删除 Metalake

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示一个确认对话框，点击 `DROP` 按钮删除此 metalake。

![delete-metalake](./assets/webui/delete-metalake.png)

### 目录

在表格中点击 metalake 名称可查看 metalake 中的 catalogs。

如果是第一次，直到创建目录之后才会显示数据。

点击左箭头图标按钮 <Icon icon='mdi:arrow-left' fontSize='24' color='#6877ef' /> 将带你进入 metalake 页面。

![metalake-catalogs](./assets/webui/metalake-catalogs.png)

点击选项卡 - `DETAILS` 查看 metalake catalogs 页面上 metalake 的详细信息。

![metalake-catalogs-details](./assets/webui/metalake-catalogs-details.png)

页面左侧是一个树形列表，目录的图标与其类型和提供者相对应。

- 目录 <Icon icon='openmoji:iceberg' fontSize='24px' /> (例如 iceberg 目录)
- 模式 <Icon icon='bx:coin-stack' fontSize='24px' />
- 表 <Icon icon='bx:table' fontSize='24px' />

![tree-view](./assets/webui/tree-view.png)

将鼠标悬停在相应的图标上，使数据变为重新加载图标 <Icon icon='mdi:reload' fontSize='24px' />。点击此图标以重新加载当前选定的数据。

![tree-view-reload-catalog](./assets/webui/tree-view-reload-catalog.png)

#### 创建目录

点击 `CREATE CATALOG` 按钮会显示创建目录的对话框。

![create-catalog](./assets/webui/create-catalog.png)

创建目录需要这些字段：

1. **目录名称**(**_必填_**)：目录的名称
2. **类型**(**_必填_**)：`relational`/`fileset`/`messaging`/`model`，默认值为 `relational`
3. **提供者**(**_必填_**)：
1. 类型 `relational` - `hive`/`iceberg`/`mysql`/`postgresql`/`doris`/`paimon`/`hudi`/`oceanbase`/`hologres`
2. 类型 `fileset` 没有提供者
3. 类型 `messaging` - `kafka`
4. 类型 `model` 没有提供者
4. **注释**(_可选_)：此目录的注释
5. **属性**(**每个 `provider` 必须具体填写所需的属性字段**)

##### 提供者

> 各个提供程序中的必需属性

###### 1. 输入 `relational`

<Tabs>
<TabItem value='hive' label='Hive'>
请遵循 [Apache Hive catalog](./apache-hive-catalog.md) 文档。

<Image img={require('./assets/webui/props-hive.png')} style={{ width: 480 }} />

|键           |描述                                           |
    |--------------|------------------------------------------------------|
|metastore.uris|Hive metastore 的 URI，例如 `thrift://127.0.0.1:9083`|

</TabItem>
<TabItem value='iceberg' label='Iceberg'>
请按照 [Lakehouse Iceberg catalog](./lakehouse-iceberg-catalog.md) 文档进行操作。

参数 `catalog-backend` 提供两个值：`hive` 和 `jdbc`。

|键            |描述      |
    |---------------|-----------------|
|catalog-backend|`hive` 或 `jdbc`|

- `hive`

<Image img={require('./assets/webui/props-iceberg-hive.png')} style={{ width: 480 }} />

|键      |描述                     |
    |---------|--------------------------------|
|uri      |Iceberg catalog URI 配置      |
|warehouse|Iceberg catalog warehouse 配置|

- `jdbc`

<Image img={require('./assets/webui/props-iceberg-jdbc.png')} style={{ width: 480 }} />

|键          |描述                                                                                            |
    |-------------|-------------------------------------------------------------------------------------------------------|
|uri          |Iceberg catalog URI 配置                                                                             |
|warehouse    |Iceberg catalog warehouse 配置                                                                       |
|jdbc-driver  |"com.mysql.jdbc.Driver" 或 "com.mysql.cj.jdbc.Driver" 用于 MySQL，"org.postgresql.Driver" 用于 PostgreSQL|
|jdbc-user    |jdbc 用户名                                                                                          |
|jdbc-password|jdbc 密码                                                                                          |

参数 `authentication.type` 提供两个值：`simple` 和 `Kerberos`。

<Image img={require('./assets/webui/props-authentication-type.png')} style={{ width: 480 }} />

- `Kerberos`

<Image img={require('./assets/webui/props-authentication-kerberos.png')} style={{ width: 480 }} />

|键                               |描述                                                                                                  |
    |----------------------------------|-------------------------------------------------------------------------------------------------------------|
|authentication.type               |Paimon catalog 后端的认证类型，Gravitino 仅支持 Kerberos 和 simple。|
|authentication.kerberos.principal |Kerberos 认证的 principal。                                                                                |
|authentication.kerberos.keytab-uri|Kerberos 认证的 keytab 的 URI。                                                                              |

</TabItem>
<TabItem value='mysql' label='MySQL'>
请按照 [JDBC MySQL catalog](./jdbc-mysql-catalog.md) 文档操作。

<Image img={require('./assets/webui/props-mysql.png')} style={{ width: 480 }} />

|键          |描述                                                                                        |
    |-------------|---------------------------------------------------------------------------------------------------|
|jdbc-driver  |用于连接数据库的 JDBC URL。例如 `com.mysql.jdbc.Driver` 或 `com.mysql.cj.jdbc.Driver`|
|jdbc-url     |例如 `jdbc:mysql://localhost:3306`                                                                 |
|jdbc-user    |JDBC 用户名                                                                                         |
|jdbc-password|JDBC 密码                                                                                           |

</TabItem>
<TabItem value='postgresql' label='PostgreSQL'>
请按照 [JDBC PostgreSQL catalog](./jdbc-postgresql-catalog) 文档操作。

<Image img={require('./assets/webui/props-pg.png')} style={{ width: 480 }} />

|键          |描述                                          |
    |-------------|-----------------------------------------------------|
|jdbc-driver  |例如 `org.postgresql.Driver`                         |
|jdbc-url     |例如 `jdbc:postgresql://localhost:5432/your_database`|
|jdbc-user    |JDBC 用户名                                   |
|jdbc-password|JDBC 密码                                    |
|jdbc-database|例如 `pg_database`                                   |

</TabItem>
<TabItem value='doris' label='Doris'>
请遵循 [JDBC Doris catalog](./jdbc-doris-catalog.md) 文档。

<Image img={require('./assets/webui/props-doris.png')} style={{ width: 480 }} />

|键          |描述                                                          |
    |-------------|---------------------------------------------------------------------|
|jdbc-driver  |用于连接数据库的 JDBC URL。例如 `com.mysql.jdbc.Driver`|
|jdbc-url     |例如 `jdbc:mysql://localhost:9030`                                   |
|jdbc-user    |JDBC 用户名                                                   |
|jdbc-password|JDBC 密码                                                    |

</TabItem>
<TabItem value='Paimon' label='Paimon'>
请遵循 [lakehouse-paimon-catalog](./lakehouse-paimon-catalog.md) 文档。

参数 `catalog-backend` 提供三个值：`filesystem`、`hive` 和 `jdbc`。

|键            |描述                    |
    |---------------|-------------------------------|
|catalog-backend|`filesystem`、`hive` 或 `jdbc`|

- `filesystem`

<Image img={require('./assets/webui/props-paimon-filesystem.png')} style={{ width: 480 }} />

|键      |描述                     |
    |---------|--------------------------------|
|仓库|Paimon catalog 仓库配置 |

- `hive`

<Image img={require('./assets/webui/props-paimon-hive.png')} style={{ width: 480 }} />

|键      |描述                     |
    |---------|--------------------------------|
|uri      |Paimon catalog URI 配置       |
|warehouse|Paimon catalog warehouse 配置 |

- `jdbc`

<Image img={require('./assets/webui/props-paimon-jdbc.png')} style={{ width: 480 }} />

|键          |描述                                                                                            |
    |-------------|-------------------------------------------------------------------------------------------------------|
|uri          |Paimon catalog URI 配置                                                                              |
|warehouse    |Paimon catalog warehouse 配置                                                                        |
|jdbc-driver  |"com.mysql.jdbc.Driver" 或 "com.mysql.cj.jdbc.Driver" 用于 MySQL，"org.postgresql.Driver" 用于 PostgreSQL|
|jdbc-user    |jdbc 用户名                                                                                          |
|jdbc-password|jdbc 密码                                                                                          |
  
参数 `authentication.type` 提供两个值：`simple` 和 `Kerberos`。

<Image img={require('./assets/webui/props-authentication-type.png')} style={{ width: 480 }} />

- `Kerberos`

<Image img={require('./assets/webui/props-authentication-kerberos.png')} style={{ width: 480 }} />


|键                               |描述                                                                                                  |
    |----------------------------------|-------------------------------------------------------------------------------------------------------------|
|authentication.type               |Paimon catalog 后端的认证类型，Gravitino 仅支持 Kerberos 和 simple。|
|authentication.kerberos.principal |Kerberos 认证的 principal。                                                                                |
|authentication.kerberos.keytab-uri|Kerberos 认证的 keytab 的 URI。                                                                              |

</TabItem>
<TabItem value='Hudi' label='Hudi'>
请遵循 [lakehouse-hudi-catalog](./lakehouse-hudi-catalog.md) 文档。

<Image img={require('./assets/webui/props-hudi.png')} style={{ width: 480 }} />

|键            |描述                    |
    |---------------|-------------------------------|
|catalog-backend|`hms`                          |
|uri            |Hudi catalog URI 配置        |

</TabItem>
<TabItem value='OceanBase' label='OceanBase'>
请按照 [jdbc-oceanbase-catalog](./jdbc-oceanbase-catalog.md) 文档操作。

<Image img={require('./assets/webui/props-oceanbase.png')} style={{ width: 480 }} />

|键          |描述                                                                        |
    |-------------|-----------------------------------------------------------------------------------|
|jdbc-driver  |例如 com.mysql.jdbc.Driver 或 com.mysql.cj.jdbc.Driver 或 com.oceanbase.jdbc.Driver|
|jdbc-url     |例如 jdbc:mysql://localhost:2881 或 jdbc:oceanbase://localhost:2881                |
|jdbc-user    |JDBC 用户名                                                                 |
|jdbc-password|JDBC 密码                                                                  |

</TabItem>
<TabItem value='Hologres' label='Hologres'>
请按照 [jdbc-hologres-catalog](./jdbc-hologres-catalog.md) 文档操作。

|键          |描述                                                                                       |
    |-------------|--------------------------------------------------------------------------------------------------|
|jdbc-driver  |例如 `org.postgresql.Driver`                                                                      |
|jdbc-url     |例如 `jdbc:postgresql://hgprecn-cn-xxx.hologres.aliyuncs.com:80/my_database`                      |
|jdbc-user    |JDBC 用户名（AccessKey ID 或数据库用户名）                                            |
|jdbc-password|JDBC 密码（AccessKey Secret 或数据库密码）                                         |
|jdbc-database|例如 `my_database`                                                                                |

</TabItem>
</Tabs>

###### 2. 输入 `fileset`

<Tabs>
<TabItem value='fileset' label='Fileset'>
请遵循 [Fileset catalog](./fileset-catalog.md) 文档。

<Image img={require('./assets/webui/create-fileset-hadoop-catalog-dialog.png')} style={{ width: 480 }} />

</TabItem>
</Tabs>

###### 3. 输入 `messaging`

<Tabs>
<TabItem value='kafka' label='Kafka'>
请遵循 [Kafka catalog](./kafka-catalog.md) 文档。

<Image img={require('./assets/webui/create-messaging-kafka-catalog-dialog.png')} style={{ width: 480 }} />

| 键               | 描述                                                                               |
    | ----------------- | ----------------------------------------------------------------------------------------- |
| bootstrap.servers | 要连接的 Kafka broker，允许通过逗号分隔来指定多个 broker |

</TabItem>
</Tabs>

验证这些字段的值后，点击 `CREATE` 按钮即可创建目录。

![created-catalog](./assets/webui/created-catalog.png)

#### 显示目录详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此目录的详细信息。

![show-catalog-details](./assets/webui/show-catalog-details.png)

#### 编辑目录

点击表格单元格中的操作图标 <Icon icon='mdi:square-edit-outline' fontSize='24' /> 。

显示用于修改所选目录字段的对话框。

![update-catalog](./assets/webui/update-catalog.png)

只能修改 `properties` 中的 `name`、`comment` 和自定义字段，其他字段如 `type`、`provider` 以及 `properties` 中的默认字段不能修改。

不允许修改的字段在 Web UI 中无法被选择和修改。

#### 禁用目录

目录在成功创建后默认为使用中。

将鼠标悬停在目录名称旁边的开关上，以查看“使用中”提示。

![catalog-in-use](./assets/webui/catalog-in-use.png)

点击开关将禁用目录，将鼠标悬停在目录名称旁边的开关上可查看“未使用”提示。

![目录未使用](./assets/webui/catalog-not-in-use.png)

#### 删除目录

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示确认对话框，点击 SUBMIT 按钮将删除此目录。

![delete-catalog](./assets/webui/delete-catalog.png)

### 模式

点击左侧边栏的目录树节点或表格单元格中的目录名称链接。

Displays the list schemas of the catalog.

![list-schemas](./assets/webui/list-schemas.png)

#### 创建架构

点击 `CREATE SCHEMA` 按钮会显示创建 schema 的对话框。

![create-schema](./assets/webui/create-schema.png)

创建 schema 需要这些字段：

1. **名称**(**_必填_**)：schema 的名称。
2. **注释**(_可选_)：schema 的注释。
3. **属性**(_可选_)：点击 `ADD PROPERTY` 按钮添加自定义属性。

#### 显示 Schema 详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此 schema 的详细信息。

![schema-details](./assets/webui/schema-details.png)

#### Edit Schema

点击表格单元格中的操作图标 <Icon icon='mdi:square-edit-outline' fontSize='24' /> 。

显示用于修改所选架构字段的对话框。

![update-schema-dialog](./assets/webui/update-schema-dialog.png)

#### Drop Schema

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示一个确认对话框，点击 `DROP` 按钮将删除此 schema。

![delete-schema](./assets/webui/delete-schema.png)

### 表格

点击左侧边栏的 hive schema 树节点或表格单元格中的 schema 名称链接。

显示模式的表列表。

![list-tables](./assets/webui/list-tabels.png)

#### 创建表

点击 `CREATE TABLE` 按钮显示创建表的对话框。

![create-table](./assets/webui/create-table.png)

创建表需要这些字段：

1. **Name**(**_required_**): 表的名称。
2. **columns**(**_required_**): 
1. 每一列的名称和类型都是必填的。
2. 仅支持简单类型，无法通过 ui 支持复杂类型，你可以通过 api 创建复杂类型。
3. **Comment**(_optional_): 表的注释。
4. **Properties**(_optional_): 点击 `ADD PROPERTY` 按钮以添加自定义属性。

#### 显示表详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此表格的详细信息。

![table-details](./assets/webui/table-details.png)

点击左侧边栏的表树节点或表格单元格中的表名链接。

查看右侧页面上的列和详细信息。

![list-columns](./assets/webui/list-columns.png)
![table-selected-details](./assets/webui/table-selected-details.png)

#### 编辑表格

点击表格单元格中的操作图标 <Icon icon='mdi:square-edit-outline' fontSize='24' /> 。

显示用于修改所选表字段的对话框。

![update-table-dialog](./assets/webui/update-table-dialog.png)

#### 删除表

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示确认对话框，点击 `DROP` 按钮将删除该表。

![删除表格](./assets/webui/delete-table.png)

### 文件集

点击左侧边栏上的 fileset schema 树节点或表格单元格中的 schema 名称链接。

显示 schema 的 filesets 列表。

![list-filesets](./assets/webui/list-filesets.png)

#### 创建文件集

点击 `CREATE FILESET` 按钮会显示创建文件集的对话框。

![create-fileset](./assets/webui/create-fileset.png)

创建文件集需要以下字段：

1. **名称**(**_必填_**): 文件集的名称。
2. **类型**(**_必填_**): `managed`/`external`，默认值为 `managed`。
3. **存储位置**(_可选_): 
1. 如果文件集为 'Managed' 类型，且已在父级 catalog 或 schema 级别指定了存储位置，则为可选。
2. 如果文件集类型为 'External' 或父级未定义存储位置，则此项为必填。
4. **注释**(_可选_): 文件集的注释。
5. **属性**(_可选_): 点击 `ADD PROPERTY` 按钮以添加自定义属性。

#### 显示文件集详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此文件集的详细信息。

![fileset-details](./assets/webui/fileset-details.png)

点击左侧边栏上的文件集树节点或表格单元格中的文件集名称链接。

查看右侧页面上的详细信息。

![fileset-selected-details](./assets/webui/fileset-selected-details.png)

#### 编辑文件集

点击表格单元格中的操作图标 <Icon icon='mdi:square-edit-outline' fontSize='24' /> 。

显示用于修改所选文件集字段的对话框。

![update-fileset-dialog](./assets/webui/update-fileset-dialog.png)

#### 删除 Fileset

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示确认对话框，点击 `DROP` 按钮将删除该文件集。

![delete-fileset](./assets/webui/delete-fileset.png)

### 主题

点击左侧边栏的 kafka schema 树节点，或表格单元格中的 schema 名称链接。

显示架构的主题列表。

![list-topics](./assets/webui/list-topics.png)

#### 创建主题

点击 `CREATE TOPIC` 按钮会显示创建主题的对话框。

![create-topic](./assets/webui/create-topic.png)

创建主题需要这些字段：

1. **名称**(**_必填_**): 主题的名称。
2. **备注**(_可选_): 主题的备注。
3. **属性**(_可选_): 点击 `ADD PROPERTY` 按钮以添加自定义属性。

#### 显示主题详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

请在右侧的抽屉组件中查看此主题的详细信息。

![topic-details](./assets/webui/topic-drawer-details.png)

点击左侧边栏的主题树节点或表格单元格中的主题名称链接。

查看右侧页面上的详细信息。

![topic-details](./assets/webui/topic-details.png)

#### 编辑主题

点击表格单元格中的操作图标 <Icon icon='mdi:square-edit-outline' fontSize='24' /> 。

显示用于修改所选主题字段的对话框。

![update-topic-dialog](./assets/webui/update-topic-dialog.png)

#### 丢弃主题

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示一个确认对话框，点击 `DROP` 按钮将删除该主题。

![删除主题](./assets/webui/delete-topic.png)

### 模型

点击左侧边栏的模型 schema 树节点或表格单元格中的 schema 名称链接。

显示 schema 的列表模型。

![list-models](./assets/webui/list-models.png)

#### 注册模型

点击 `REGISTER MODEL` 按钮会显示注册模型的对话框。

![register-model](./assets/webui/register-model.png)

注册模型需要这些字段：

1. **名称**(**_必填_**): 模型的名称。
2. **注释**(_可选_): 模型的注释。
3. **属性**(_可选_): 点击 `ADD PROPERTY` 按钮添加自定义属性。

#### 显示模型详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此模型的详细信息。

![model-details](./assets/webui/model-details.png)

#### Drop Model

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

Displays a confirmation dialog, clicking on the `DROP` button drops this model.

![delete-model](./assets/webui/delete-model.png)

### 版本

点击左侧边栏的模型树节点或表格单元格中的模型名称链接。

显示模型的版本列表。

![list-model-versions](./assets/webui/list-model-versions.png)

#### 链接版本

点击 `LINK VERSION` 按钮会显示用于链接版本的对话框。

![link-version](./assets/webui/link-version.png)

关联一个版本需要以下字段：

1. **URI**(**_必填_**): 版本的 uri。
2. **Aliases**(**_必填_**): 版本的别名，别名不能是数字或数字字符串。
3. **Comment**(_可选_): 模型的注释。
4. **Properties**(_可选_): 点击 `ADD PROPERTY` 按钮以添加自定义属性。

#### 显示版本详情

点击表格单元格中的操作图标 <Icon icon='bx:show-alt' fontSize='24' />。

在右侧的抽屉组件中查看此版本的详细信息。

![version-details](./assets/webui/version-details.png)

#### 丢弃版本

点击表格单元格中的操作图标 <Icon icon='mdi:delete-outline' fontSize='24' color='red' />。

显示确认对话框，点击 `DROP` 按钮将删除此版本。

![delete-version](./assets/webui/delete-version.png)

## 功能特性

| 页面     | 功能                                                                      |
| -------- | --------------------------------------------------------------------------------- |
| Metalake | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10004; / _`删除`_ &#10004; |
| Catalog  | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10004; / _`删除`_ &#10004; |
| Schema   | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10004; / _`删除`_ &#10004; |
| Table    | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10004; / _`删除`_ &#10004; |
| Fileset  | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10004; / _`删除`_ &#10004; |
| Topic    | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10004; / _`删除`_ &#10004; |
| Model    | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10008; / _`删除`_ &#10004; |
| Version  | _`查看`_ &#10004; / _`创建`_ &#10004; / _`编辑`_ &#10008; / _`删除`_ &#10004; |

## E2E 测试

Web前端的端到端测试使用[Selenium](https://www.selenium.dev/documentation/)测试框架进行，该框架基于Java。

测试用例可以在项目目录中找到：`integration-test/src/test/java/org/apache/gravitino/integration/test/web/ui`，其中 `pages` 目录专门用于存储前端元素的定义等。
根目录包含测试用例的实际步骤。

:::tip
在编写测试用例时，在本地环境中运行它们可能不会出现任何问题。

然而，由于 GitHub Actions 的性能有限，涉及 DOM 延迟加载的场景——例如弹出动画打开所需的时间——可能会导致测试失败。

为了规避此问题，需要手动插入延迟操作，例如，通过添加诸如 `Thread.sleep(sleepTimeMillis)` 的代码。

这确保测试在进行下一步操作前等待延迟动画完成，从而避免了该问题。

建议使用 Selenium 内置的 [`waits`](https://www.selenium.dev/documentation/webdriver/waits/) 方法来替代 `Thread.sleep()`。
:::
