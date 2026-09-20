---
title: "Web V2 UI"
slug: "/webui-v2"
keyword: "webui v2"
last_update:
  date: 2026-01-30
  author: LauraXia123
license: "This software is licensed under the Apache License version 2."
---

## 简介

本文档概述了用户如何使用 Web V2 UI 在 Apache Gravitino 中管理元数据，Web V2 UI 是最新的可通过 Web 浏览器访问的图形界面，可作为编写代码或使用 REST 接口的替代方案。

[构建](./how-to-build.md#quick-start) 并 [部署](./getting-started/index.md#local-workstation) Gravitino Web UI，并在浏览器中打开 `http://<gravitino-host>:<gravitino-port>`。默认情况下，它是 [http://localhost:8090](http://localhost:8090)。

## Web V2 (UI 版本 1.3.0)

从 1.3.0 版本开始，Gravitino 引入了 Web V2。默认情况下，Gravitino 使用 Web V2（未设置时为 `GRAVITINO_USE_WEB_V2=true`）。要切换回旧版 v1 UI，请显式设置 `GRAVITINO_USE_WEB_V2=false`。要强制使用 Web V2，请将其设置为 `true`。

如果要从服务器环境文件中配置此项，请在启动服务器之前在 `conf/gravitino-env.sh` 中设置以下环境变量：

```bash
# In <path-to-gravitino>/conf/gravitino-env.sh
GRAVITINO_USE_WEB_V2=true
```

更改此值后，重启 Gravitino 服务器以使更改生效：

```bash
<path-to-gravitino>/bin/gravitino.sh restart
```

### 会话超时配置

Web V2 支持在服务器端配置会话超时。所有值均以毫秒为单位：

| 服务器配置 | UI 环境回退 | 默认 | 描述 |
| --- | --- | ---: | --- |
| `gravitino.ui.sessionIdleTimeoutMs` | `NEXT_PUBLIC_IDLE_TIMEOUT_MS` | `900000` | 在此期间无活动后将用户登出。 |
| `gravitino.ui.sessionMaxDurationMs` | `NEXT_PUBLIC_MAX_SESSION_DURATION_MS` | `18000000` | 在此总会话时长之后将用户登出，无论是否有活动。 |
| `gravitino.ui.sessionIdleWarningLeadMs` | `NEXT_PUBLIC_IDLE_WARNING_LEAD_MS` | `60000` | 在空闲超时前提前这么长时间显示无活动警告。 |

UI 按以下顺序解析每个值：`/configs` API、相应的 `NEXT_PUBLIC_*` 环境变量，然后是默认值。要通过 `/configs` 暴露服务器值，请在 `gravitino.server.visibleConfigs` 中配置这些键：

```properties
gravitino.ui.sessionIdleTimeoutMs = 900000
gravitino.ui.sessionMaxDurationMs = 18000000
gravitino.ui.sessionIdleWarningLeadMs = 60000
gravitino.server.visibleConfigs = gravitino.ui.sessionIdleTimeoutMs,gravitino.ui.sessionMaxDurationMs,gravitino.ui.sessionIdleWarningLeadMs
```

请勿将 `gravitino.authorization.serviceAdmins` 添加到 `gravitino.server.visibleConfigs` 中，因为
未经身份验证的 `/configs` 端点返回的值是公开的。UI 会从经过身份验证的
`/api/authn/me` 端点获取当前用户的服务管理员状态。

## Web V2

以下各节介绍了 Web V2。这是默认的 UI；设置 `GRAVITINO_USE_WEB_V2=false` 以使用旧版 v1 UI。
Web V2 引入了额外的模块（如 Jobs、Job Templates、Data Compliance 和 Access），并扩展了表的创建和编辑功能，以支持跨提供商的更复杂数据类型。

数据合规包括**标签**和**策略**。**访问**模块仅在 `gravitino.authorization.enable=true` 时可见，并且包括**用户**、**用户组**和**角色**。

### 初始页面

Web V2 落地页取决于身份验证模式，以及在 `<path-to-gravitino>/conf/gravitino.conf` 中是否启用了授权。

- 当 `gravitino.authorization.enable=false` 时，授权被禁用。在 `simple` 模式下，UI 会直接打开 metalake 列表页面。

![metalakes-list](./assets/webui-v2/metalakes-list.png)

- 当 `gravitino.authorization.enable=true` 时，将启用授权。在 `simple` 模式下，UI 会显示一个登录页面。输入任意用户名，无需密码。

![simple-with-login](./assets/webui-v2/simple-with-login.png)

- 当 `gravitino.authenticators=basic` 且本地用户 REST 扩展包已注册时，
Web UI 会显示基于本地用户元数据的用户名和密码登录表单。参见
[本地用户和组](security/local-users-and-groups.md)。

- 当 `gravitino.authenticators=oauth` 时，登录需要 OAuth 配置。OAuth 模式需要 `gravitino.authorization.enable=true`。详情请见 [安全](security/how-to-authenticate.md)

![oauth-login](./assets/webui-v2/oauth-login.png)

### Metalakes

Web V2 中 Metalake 的概览。

![metalakes-list](./assets/webui-v2/metalakes-list.png)

#### 创建 Metalake

点击 `CREATE METALAKE` 按钮打开创建对话框。填写表单字段并提交以创建 metalake。

![create-metalake](./assets/webui-v2/create-metalake.png)

创建后，基本信息在 metalake 列表中可见。

#### 属性弹出框

将鼠标悬停在 **Properties** 列中的数字上以查看属性弹出框。

![metalake-properties-popover](./assets/webui-v2/metalake-properties-popover.png)

#### 操作

在 **操作** 列中，您可以编辑或删除 metalake。设置下拉菜单包括：

- **设置所有者**（仅在 `gravitino.authorization.enable=true` 时可用）
- **切换使用中 / 未使用**

![metalake 操作](./assets/webui-v2/metalake-actions.png)

#### 删除 Metalake

要删除 metalake，该 metalake 必须处于**未使用**状态（在 [Actions](#actions) 设置下拉菜单中进行设置），并且必须先删除所有子实体。删除对话框要求在删除前输入 metalake 名称以进行确认。

![metalake-delete-confirm](./assets/webui-v2/metalake-delete-confirm.png)

### 目录

Web V2 中的目录概览。

#### 目录类型筛选器

在 catalogs 页面上，使用左上角的 catalog 类型选择器在 `relational`、`messaging`、`fileset` 和 `model` 之间切换。列表将更新以显示所选类型的 catalogs。


#### 标签与策略关联

目录列表显示基本目录信息以及关联的 **标签** 和 **策略**。使用列表中的 **关联标签** 和 **关联策略** 来添加关联。点击标签上的 **X** 将其移除。

![catalogs-list](./assets/webui-v2/catalogs-list.png)

#### 禁用目录

从 **操作** 设置下拉菜单中，将目录切换为 **未使用**。目录名称旁边会显示一个禁用图标，并且目录名称变为不可点击（您无法进入目录详情页面）。

![catalog-actions](./assets/webui-v2/catalog-actions.png)

#### 提供者过滤器

使用 **Provider** 表头上的筛选器，按提供商缩小目录列表范围。

![catalogs-disabled-icon-and-filter-catalogs](./assets/webui-v2/catalogs-disabled-icon-and-filter-catalogs.png)

#### 创建目录

点击 **创建目录** 以打开所选目录类型的创建表单。在步骤 1 中，为所选类型选择提供商。点击 **下一步** 进入步骤 2，填写必填属性，并提交以创建目录。某些提供商支持 **测试连接**，以便您可以在提交前验证连接性。

![catalogs-create-step1](./assets/webui-v2/create-catalog-step1.png)

![catalogs-create-step2](./assets/webui-v2/create-catalog-step2.png)

#### 删除目录

如果目录仍处于使用中，UI 会显示**删除**选项，如**下图 1**所示。将目录切换为**未使用**（参见[禁用目录](#disable-catalog)）后，**删除**选项变为**下图 2**所示。输入目录名称进行二次确认，然后即可将其删除。

![catalog-delete-figure-1](./assets/webui-v2/catalog-delete-figure-1.png)

![catalog-delete-figure-2](./assets/webui-v2/catalog-delete-figure-2.png)

#### 导航栏

导航栏提供以下快捷方式：

- 点击右侧的 **System Mode** 图标以导航回 metalake 列表页面。
- **User** 图标下拉菜单显示所有 metalake 名称的列表（点击以切换）。
- 当 `gravitino.authorization.enable=true` 时，**User** 图标下拉菜单还会显示当前用户名以及一个返回登录页面的 **Logout** 按钮。

![navbar-system-mode](./assets/webui-v2/navbar-system-mode.png)
![navbar-user-dropdown](./assets/webui-v2/navbar-user-dropdown.png)

### 目录详情与模式

通过点击左侧树或右侧列表中的目录名称进入目录详情页。目录名称下方会显示基本目录信息。将鼠标悬停在高亮显示的数字上，可打开包含更多详细信息的弹出框。

在目录信息下方，页面显示了**Schemas**列表以及目录的**关联角色**。**关联角色**部分仅在 `gravitino.authorization.enable=true` 时可见，并列出了角色名称及其权限。

#### 模式列表

Web V2 中的 Schema 概览。

![schemas-list](./assets/webui-v2/schemas-list.png)

#### 关联角色

Web V2 关联角色概述。（仅在 `gravitino.authorization.enable=true` 时可见）

![catalog-associated-roles](./assets/webui-v2/catalog-associated-roles.png)

Apache Gravitino Spark 连接器支持加载已注册的用户定义函数（UDF）
在 Gravitino 函数注册表中。一旦函数被
[在 Gravitino 中注册](./manage-user-defined-function-using-gravitino.md)，Spark 就可以发现并
通过标准的 Spark SQL 语法调用它——无需额外的 `CREATE FUNCTION` 语句。
如果注册了 UDF，您可以在模式详情页上看到一个 **Functions** 列表选项卡。

![schema-functions-list](./assets/webui-v2/schema-functions-list.png)

点击函数树节点或列表中的函数名，以查看
函数定义的详细参数。

![功能详情](./assets/webui-v2/function-details.png)

### 表格

Web V2 中表格的概述。

![表列表](./assets/webui-v2/tables-list.png)

#### 创建表

在 **Schema 详情** 页面中，列表显示了所选 Schema 下的所有表。点击 **创建表** 打开建表表单。

在表单中，添加列并选择列类型。Web V2 支持 `char`、`varchar` 和 `decimal` 的复合输入。根据提供程序的不同，支持某些复杂类型（例如 `list`、`map`、`struct`、`union`）。

根据提供商的不同，您可以配置 **Partitions**、**Sort Orders** 和 **Distribution**。

![tables-create-columns](./assets/webui-v2/create-table.png)
![tables-create-columns2](./assets/webui-v2/create-table2.png)
![create-table-sortOrders](./assets/webui-v2/create-table-sortOrders.png)


在**属性**中，默认值已预填且可以更改。在提交前重新选择并更新这些值。

![tables-create-properties](./assets/webui-v2/tables-create-properties.png)

提交表单以创建复杂表格

### 文件集

Web V2 中 Fileset 的概览。

![文件集列表](./assets/webui-v2/filesets-list.png)

Web V2 中 fileset 下文件的概述。

![files-list](./assets/webui-v2/files-list.png)

### 主题

Web V2 中的 Topic 概述。

![topics-list](./assets/webui-v2/topics-list.png)

### 模型

Web V2 中的模型概述。

![models-list](./assets/webui-v2/models-list.png)

### 版本

Web V2 中的版本概述。

![versions-list](./assets/webui-v2/versions-list.png)

### 工作

Web V2 中的作业概览。

![jobs-list](./assets/webui-v2/jobs-list.png)

#### 运行作业

点击 **运行作业**，选择一个作业模板，并在左侧查看模板参数。在右侧，使用 **作业配置** 替换由 `{{}}` 定义的模板占位符。替换完成后，将生成并执行最终的作业脚本。

![run-job](./assets/webui-v2/run-job.png)

在作业模板选择下拉菜单中，您可以选择 **注册作业模板** 来创建新模板，或者点击 **前往作业模板** 导航至作业模板列表页面。

![run-job](./assets/webui-v2/run-job2.png)

### 作业模板

Web V2 中的作业模板概览。

![jobTemplates-list](./assets/webui-v2/jobTemplates-list.png)

#### 注册作业模板

点击 **注册作业模板** 打开创建模板表单。选择作业类型，填写必填字段，然后提交以注册模板。

![job-template-register](./assets/webui-v2/job-template-register.png)


### 标签

Web V2 中数据合规标签的概述。

![tags-list](./assets/webui-v2/tags-list.png)

#### 创建标签

点击 **创建标签** 打开创建表单。填写必填字段并提交以创建标签。

![tags-create](./assets/webui-v2/tags-create.png)

#### 标签元数据对象

点击标签以导航至 **元数据对象** 页面，该页面列出了与所选标签关联的所有元数据对象。

![tag-metadata-objects](./assets/webui-v2/tag-metadata-objects.png)

### 策略

Web V2 中的数据合规政策概述。

![policies-list](./assets/webui-v2/policies-list.png)

#### 创建策略

点击 **Create Policy** 打开创建表单。填写必填字段并提交以创建策略。

![policies-create](./assets/webui-v2/policies-create.png)

#### 策略元数据对象

点击策略标签以导航至**元数据对象**页面，该页面列出了与所选策略关联的所有元数据对象。

![policy-metadata-objects](./assets/webui-v2/policy-metadata-objects.png)

### 访问

Access 模块仅在 `gravitino.authorization.enable=true` 时可见。

### 用户访问

Web V2 中面向 Access 用户的概述。

![users-list](./assets/webui-v2/users-list.png)

#### 添加用户

点击 **添加用户** 打开创建表单。填写必填字段并提交以创建用户。

![users-add](./assets/webui-v2/users-add.png)

#### 授予角色

从 **操作** 中，点击 **授予角色** 图标，为所选用户分配角色。

![users-grant-role](./assets/webui-v2/users-grant-role.png)

### 用户组访问权限

Web V2 中的访问用户组概述。

![userGroups-list](./assets/webui-v2/userGroups-list.png)

#### 添加用户组

点击**添加用户组**打开创建表单。填写必填字段并提交以创建用户组。

![userGroups-add](./assets/webui-v2/userGroups-add.png)

#### 授予角色

从 **操作** 中，点击 **授予角色** 图标，为所选用户组分配角色。

![userGroups-grant-role](./assets/webui-v2/userGroups-grant-role.png)

### 角色访问

Web V2 中访问角色的概述。

![roles-list](./assets/webui-v2/roles-list.png)

#### 创建角色

点击 **创建角色** 打开创建表单。一个角色可以包含多个安全对象。不同的安全对象类型具有不同的可用权限。详情请参见[安全对象](security/access-control.md#securable-objects)和[权限类型](security/access-control.md#privilege-types)。

![roles-create](./assets/webui-v2/roles-create.png)
