---
title: "MCP Server"
slug: "/gravitino-mcp-server"
keyword: "Gravitino MCP metadata"
license: "This software is licensed under the Apache License version 2."
---

## 介绍

Gravitino MCP 服务器为 LLM 提供了管理 Gravitino 元数据的能力。

## 要求

1. Python 3.10+
2. 已安装 uv。请按照[官方指南](https://docs.astral.sh/uv/getting-started/installation/)安装 uv。

## 用法

1. 从 GitHub 克隆代码，并切换到 `mcp-server` 目录
2. 创建虚拟环境，`uv venv`
3. 安装所需的 Python 包。`uv pip install -e .`
4. 将 Gravitino MCP 服务器添加到相应的 LLM 工具中。以 Cursor 为例，编辑 `~/.cursor/mcp.json`，为本地 Gravitino MCP 服务器使用以下配置：

```json
{
  "mcpServers": {
    "gravitino": {
      "command": "uv",
      "args": [
        "--directory",
        "$path/mcp-server",
        "run",
        "mcp_server",
        "--metalake",
        "test",
        "--gravitino-uri",
        "http://127.0.0.1:8090"
      ],
      "env": {
        "GRAVITINO_OAUTH_TOKEN_ENDPOINT": "https://idp.example/realms/gravitino/protocol/openid-connect/token",
        "GRAVITINO_OAUTH_CLIENT_ID": "mcp-service",
        "GRAVITINO_OAUTH_CLIENT_SECRET": "<secret>",
        "GRAVITINO_OAUTH_SCOPE": "gravitino"
      }
    }
  }
}
```

在 Cursor stdio 模式下，MCP 进程通常不会从客户端接收到 `Authorization` 头。设置 `GRAVITINO_OAUTH_*` 变量（或匹配的 CLI 标志），以便 MCP 使用 `client_credentials` 授权获取服务令牌。省略 `env` 以匿名运行，或者使用 `--token` / `GRAVITINO_TOKEN` 作为静态凭据。

或者通过 `uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090 --transport http --mcp-url http://localhost:8000/mcp` 启动 HTTP MCP 服务器，并使用以下配置：

```json
{
  "mcpServers": {
    "gravitino": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Docker 说明

你可以通过 Docker 镜像启动 Gravitino MCP 服务器，`docker run -p 8000:8000 --network=host apache/gravitino-mcp-server:latest --metalake test --transport http --mcp-url http://0.0.0.0:8000/mcp --gravitino-uri http://127.0.0.1:8090`。请注意，Docker 容器中的 MCP 服务器不支持 `stdio` 传输模式。

## 支持的工具

Gravitino MCP 服务器支持以下工具，并且您可以按标签导出工具。

| 工具名称                           | 描述                                                                    | 标签          |
|-------------------------------------|--------------------------------------------------------------------------------|--------------|
| `list_metalakes`                    | Retrieve the metalakes the caller can access.                                  | `metalake`   |
| `get_list_of_catalogs`              | Retrieve a list of all catalogs in the system.                                 | `catalog`    |
| `create_catalog`                    | Create a new catalog.                                                          | `catalog`    |
| `alter_catalog`                     | Alter an existing catalog.                                                     | `catalog`    |
| `drop_catalog`                      | Drop a catalog.                                                                | `catalog`    |
| `set_catalog_in_use`                | Enable or disable a catalog.                                                   | `catalog`    |
| `get_list_of_schemas`               | Retrieve a list of schemas belonging to a specific catalog.                    | `schema`     |
| `create_schema`                     | Create a new schema.                                                           | `schema`     |
| `alter_schema`                      | Alter an existing schema.                                                      | `schema`     |
| `drop_schema`                       | Drop a schema.                                                                 | `schema`     |
| `get_list_of_tables`                | Retrieve a list of tables within a specific catalog and schema.                | `table`      |
| `get_table_metadata_details`        | Retrieve comprehensive metadata details for a specific table.                  | `table`      |
| `create_table`                      | Create a new table.                                                            | `table`      |
| `alter_table`                       | Alter an existing table.                                                       | `table`      |
| `drop_table`                        | Drop a table.                                                                  | `table`      |
| `list_of_models`                    | Retrieve a list of models within a specific catalog and schema.                | `model`      |
| `load_model`                        | Retrieve comprehensive metadata details for a specific model.                  | `model`      |
| `list_model_versions`               | Retrieve a list of versions for a specific model.                              | `model`      |
| `load_model_version`                | Retrieve comprehensive metadata details for a specific model version.          | `model`      |
| `load_model_version_by_alias`       | Retrieve comprehensive metadata details for a specific model version by alias. | `model`      |
| `register_model`                    | Register a new model.                                                          | `model`      |
| `delete_model`                      | Delete a model.                                                                | `model`      |
| `link_model_version`                | Link a new version to a model.                                                 | `model`      |
| `delete_model_version`              | Delete a model version.                                                        | `model`      |
| `delete_model_version_by_alias`     | Delete a model version by one of its aliases.                                  | `model`      |
| `alter_model`                       | Alter an existing model.                                                       | `model`      |
| `alter_model_version`               | Alter a model version.                                                         | `model`      |
| `alter_model_version_by_alias`      | Alter a model version by one of its aliases.                                   | `model`      |
| `metadata_type_to_fullname_formats` | Retrieve the metadata type to fullname formats mapping.                        | `metadata`   |
| `list_of_topics`                    | Retrieve a list of topics within a specific catalog and schema.                | `topic`      |
| `load_topic`                        | 检索特定主题的全面元数据详细信息。                  | `topic`      |
| `create_topic`                      | 创建一个新主题。                                                            | `topic`      |
| `alter_topic`                       | 修改现有主题。                                                       | `topic`      |
| `delete_topic`                      | 删除主题。                                                                | `topic`      |
| `list_of_filesets`                  | 检索特定目录和模式内的文件集列表。              | `fileset`    |
| `load_fileset`                      | 检索特定文件集的全面元数据详细信息。                | `fileset`    |
| `list_files_in_fileset`             | 检索特定文件集内的文件列表。                            | `fileset`    |
| `create_fileset`                    | 创建一个新文件集。                                                          | `fileset`    |
| `alter_fileset`                     | 修改现有文件集。                                                     | `fileset`    |
| `drop_fileset`                      | 删除文件集。                                                                | `fileset`    |
| `list_of_jobs`                      | 检索作业列表                                                        | `job`        |
| `get_job_by_id`                     | 根据ID检索作业。                                                      | `job`        |
| `list_of_job_templates`             | 检索作业模板列表。                                              | `job`        |
| `get_job_template_by_name`          | 根据名称检索作业模板。                                           | `job`        |
| `run_job`                           | 使用指定参数运行作业。                                       | `job`        |
| `cancel_job`                        | 根据ID取消正在运行的作业。                                                | `job`        |
| `get_tag_by_name`                   | 根据名称检索标签。                                                    | `tag`        |
| `list_of_tags`                      | 检索标签列表。                                                       | `tag`        |
| `list_tags_for_metadata`            | 检索与特定元数据项关联的标签列表。              | `tag`        |
| `list_metadata_by_tag`              | 检索与特定标签关联的元数据项列表。              | `tag`        |
| `associate_tag_with_metadata`       | 将标签与特定元数据项关联。                                  | `tag`        |
| `disassociate_tag_from_metadata`    | 取消标签与特定元数据项的关联。                               | `tag`        |
| `create_tag`                        | 创建一个新标签。                                                              | `tag`        |
| `alter_tag`                         | 修改现有标签。                                                         | `tag`        |
| `delete_tag`                        | 删除标签。                                                                  | `tag`        |
| `list_statistics_for_metadata`      | 检索与特定元数据项关联的统计信息列表。        | `statistics` |
| `list_statistics_for_partition`     | 检索与特定分区关联的统计信息列表。            | `statistics` |
| `get_list_of_policies`              | 检索系统中的策略列表。                                     | `policy`     |
| `get_policy_detail_information`     | 根据策略名称检索特定策略的详细信息。            | `policy`     |
| `list_policies_for_metadata`        | 列出与特定元数据项关联的所有策略。                    | `policy`     |
| `list_metadata_by_policy`           | 列出与特定策略关联的所有元数据项。                     | `policy`     |
| `get_policy_for_metadata`           | 获取与特定元数据项关联的策略。                         | `policy`     |
| `list_of_partitions`                | 检索表的分区。仅适用于具有分区 API 的目录。       | `partition`  |
| `get_partition`                     | 检索分区的元数据。仅适用于具有分区 API 的目录。       | `partition`  |
| `list_of_views`                     | 检索模式的视图列表。仅适用于支持视图的目录。     | `view`       |
| `load_view`                         | 检索视图的元数据。仅适用于支持视图的目录。                | `view`       |


## 配置

你可以通过参数配置 Gravitino MCP server，`uv run mcp_server -h` 显示详细信息。

| 参数                         | 描述                                                                                                                     | 默认值               | 必填 |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------|-----------------------------|----------|
| `--metalake`                     | 默认 metalake，供任何未指定名称的工具调用使用。参见选择 metalake。                                       | none                        | No       |
| `--gravitino-uri`                | Gravitino 服务器的 URI。                                                                                                    | `http://127.0.0.1:8090`     | No       |
| `--transport`                    | 传输协议：stdio（本地）、http / streamable-http（流式 HTTP）。                                                    | `stdio`                     | No       |
| `--mcp-url`                      | 如果使用 HTTP 传输，则为 MCP 服务器的 URL。                                                                                  | `http://127.0.0.1:8000/mcp` | No       |
| `--token`                        | Gravitino 的静态凭据；或设置 `GRAVITINO_TOKEN`。参见身份验证。优先于 OAuth client-credentials。              | none (anonymous)            | No       |
| `--oauth-token-endpoint`         | 用于 client-credentials 的 OAuth2 token URL。或 `GRAVITINO_OAUTH_TOKEN_ENDPOINT`。                                                   | none                        | No       |
| `--oauth-client-id`              | OAuth2 client id。或 `GRAVITINO_OAUTH_CLIENT_ID`。                                                                               | none                        | No       |
| `--oauth-client-secret`          | OAuth2 client secret。或 `GRAVITINO_OAUTH_CLIENT_SECRET`。                                                                       | none                        | No       |
| `--oauth-scope`                  | 可选的 OAuth2 scope。或 `GRAVITINO_OAUTH_SCOPE`。                                                                              | none                        | No       |
| `--no-service-identity-fallback` | 仅限 HTTP：当设置了 OAuth 或 `--token` 时，拒绝没有 `Authorization` 的请求。或 `GRAVITINO_NO_SERVICE_IDENTITY_FALLBACK`。 | `false`                     | No       |
| `--tls-cert`                     | 用于通过 HTTPS 提供端点服务的 PEM 证书。需要 `--tls-key`。                                                         | none                        | No       |
| `--tls-key`                      | 用于通过 HTTPS 提供端点服务的 PEM 私钥。需要 `--tls-cert`。                                                        | none                        | No       |

## 身份验证

默认情况下，MCP 服务器以匿名方式与 Gravitino 通信。在调用 Gravitino 时，有三种方式可以对 MCP 进行身份验证。

### 静态启动令牌 (stdio 和 HTTP)

传递 `--token`（或设置 `GRAVITINO_TOKEN` 环境变量）以使用静态凭据对服务器进行身份验证。令牌在服务器的日志输出中会被掩码处理。

裸值会被视为 OAuth2 令牌，并作为 `Authorization: Bearer <token>` 发送。已经以 HTTP 认证方案开头的值在转发时会保留该方案，以便凭据可以匹配服务器配置的任何 `gravitino.authenticators`：

| `--token` 值             | `Authorization` 发送的标头    |
|-----------------------------|--------------------------------|
| `abc`                       | `Bearer abc`                   |
| `Bearer abc`                | `Bearer abc`                   |
| `Basic dXNlcjpwYXNz`        | `Basic dXNlcjpwYXNz`           |
| `Custom credentials`        | `Custom credentials`           |
| 空或仅包含空白字符    | 无（匿名）               |

内置的方案名称（`Basic`、`Bearer`、`Negotiate`）会被不区分大小写地识别，并规范化为 Gravitino 认证器所期望的大小写格式；自定义方案名称则原样转发。

因为裸令牌只有在不含 scheme 时才会被加上 Bearer 前缀，如果静态凭据的值包含空格且以类似 scheme 的单词开头，则会被解释为 scheme 加凭据。请使用显式 scheme 对此类值加引号（例如 `--token "Bearer my secret"`），以使其保持为 Bearer 令牌。

```shell
uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090 --token <your-token>
# or, against a server configured with `gravitino.authenticators = basic`
uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090 --token "Basic $(printf '%s' 'user:password' | base64)"
# or
export GRAVITINO_TOKEN=<your-token>
uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090
```

在 `stdio` 模式下，此令牌用于每个请求。在 HTTP 模式下，它仅作为后备，用于传入请求未携带其自身 `Authorization` 头的情况。如果同时设置了 `--token` 和 OAuth 客户端凭据，则以 `--token` 为准。

### OAuth 客户端凭据（服务身份）

当 Gravitino 使用 `gravitino.authenticators = oauth` 时，粘贴在 `--token` 中的 Bearer 访问令牌会过期且不会刷新。对于**服务**身份（Cursor stdio，或者当调用方未发送 `Authorization` 标头时的 HTTP），请将 MCP 配置为 Gravitino 信任的同一身份提供者的 OAuth 客户端。

同时设置 `--oauth-token-endpoint`、`--oauth-client-id` 和 `--oauth-client-secret`，以及可选的 `--oauth-scope`（或匹配的 `GRAVITINO_OAUTH_*` 环境变量）。MCP 使用 `client_credentials` 授权请求访问令牌，将其缓存，在过期前刷新，并在遇到 HTTP 401 时重试一次。

在 Cursor 中，将 `GRAVITINO_OAUTH_*` 值放入 `~/.cursor/mcp.json` 的 `env` 块中（见 [Usage](#usage)）。`--token` / `GRAVITINO_TOKEN` 会覆盖 OAuth 客户端凭证并保持静态（无刷新）。传入的 HTTP `Authorization` 标头将按原样转发，并且不会被 MCP 刷新。

Gravitino 根据 [`gravitino.authenticator.oauth.principalFields`](./security/how-to-authenticate.md#server-configuration) 中配置的声明（通常是 `sub`）将 JWT 映射到 metalake 主体；该主体可能与 `--oauth-client-id` 不同。它必须作为一个具有所需授权的 metalake 用户存在，否则工具调用将失败并返回 403。

优先使用环境变量（或 `~/.cursor/mcp.json` 中的 `env` 块）来存放客户端密钥，这样它就不会出现在 `ps` 输出或 shell 历史记录中：

```shell
export GRAVITINO_OAUTH_TOKEN_ENDPOINT=https://idp.example/realms/gravitino/protocol/openid-connect/token
export GRAVITINO_OAUTH_CLIENT_ID=mcp-service
export GRAVITINO_OAUTH_CLIENT_SECRET=<secret>
export GRAVITINO_OAUTH_SCOPE=gravitino

uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090
```

相应的 CLI 标志（`--oauth-token-endpoint`、`--oauth-client-id`、`--oauth-client-secret`、`--oauth-scope`）的工作方式相同，但在生产环境中请避免在命令行上传递 `--oauth-client-secret`。

此路径在 HTTP 模式下不会替代每个请求的用户身份（见下文）。

### 按请求身份 (HTTP)

当服务器以 HTTP 传输方式运行时，每个传入 MCP 请求的 `Authorization` 头会被原封不动地转发给 Gravitino。认证方案会被保留，因此 OAuth2 (`Bearer`)、Gravitino 简单认证 (`Basic <base64(user:dummy)>`) 以及其他方式都能正常工作。这使得来自不同主体的并发会话保持隔离——一个主体的身份永远不会泄露到另一个主体的调用中——并允许 Gravitino 对每个调用者强制执行授权。每个请求的头部优先于静态 `--token` 和 OAuth 客户端凭据。

**安全警告：** 当配置了 OAuth 客户端凭证或 `--token` 时，**不**包含 `Authorization` 标头的 HTTP 请求将被认证为**服务身份**，而非匿名身份。使用 OAuth 时，该身份会自动刷新并保持长时间有效。如果 MCP HTTP 端点可被多个调用方访问，任何省略 `Authorization` 的人都将获得服务主体的完全权限。对于单用户集成（例如 Cursor），请使用 stdio 传输，将 HTTP 绑定到受信任的网络，或者将端点置于需要身份验证的反向代理之后。

对于暴露的或多调用方的 HTTP 部署，请设置 `--no-service-identity-fallback`（或 `GRAVITINO_NO_SERVICE_IDENTITY_FALLBACK=1`），以便拒绝没有 `Authorization` 的请求，而不是使用服务身份。对于 stdio 传输，该标志会被忽略。

授权本身始终由 Gravitino 强制执行：MCP 服务器转发身份，但不自行做出访问控制决策。

### 通过 HTTPS (TLS) 提供服务

要通过 TLS 提供 MCP HTTP 端点（即 `--mcp-url`，而非 `--gravitino-uri`），请同时提供 `--tls-cert` 和 `--tls-key`，并使用 `https://` 的 `--mcp-url`。证书和密钥必须一起提供，且 URL scheme 必须与 TLS 设置匹配（没有 cert/key 的 `https://` URL，或 `http://` URL 搭配 cert/key，在启动时会被拒绝）。

```shell
uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090 \
  --transport streamable-http --mcp-url https://localhost:8000/mcp \
  --tls-cert /path/to/cert.pem --tls-key /path/to/key.pem
```

## 选择一个 metalake

metalake 是 Gravitino 的顶级租户边界，每个工具都在其中运行。`--metalake` 设置 **默认值**：任何未自行指定 metalake 的工具调用所使用的 metalake。它在所有传输方式上都是可选的。

任何工具调用都可以通过 `metalake` 参数指定不同的 metalake，该参数优先于默认值。该参数在每个工具上都是可选的，因此对于忽略它的调用者来说，使用 `--metalake` 配置的服务器其行为与以往完全相同。

调用的 metalake 按以下顺序解析：

1. 调用自身的 `metalake` 参数，当传递了该参数时。
2. `--metalake` 启动默认值，当其被配置时。
3. 否则调用失败，告诉代理调用 `list_metalakes` 并重试。

因为每次调用都带有自己的 metalake，一个服务器实例可以同时服务多个 metalake：调用之间不保留任何状态，因此并发调用者永远不会看到彼此的 metalake，并且无论运行多少个副本，服务器都能保持正确。这在 stdio 和 HTTP 上的工作方式完全相同。

使用 `list_metalakes` 工具来发现调用者可以使用哪些 metalakes。它是唯一不需要 metalake 的工具，因此它可以在完全没有使用 `--metalake` 启动的服务器上运行。

统计工具（`list_statistics_for_metadata`、`list_statistics_for_partition`）在 metalake 选择统一之前自带了它们自己的 `metalake_name` 参数。它仍被作为 `metalake` 的弃用别名接受，因此现有调用者可继续工作；同时传递两者且值不同会被拒绝。新的调用者应使用 `metalake`。

这些工具使用 `metadata_full_name` 作为元数据对象名称，与标签和策略工具保持一致。之前的拼写 `metadata_fullname` 作为已弃用的输入别名被接受，但未在工具 schema 中公布。每次调用仅提供一个拼写；同时传递两者会被拒绝。新的调用者应使用 `metadata_full_name`。

授权保持不变 — 调用者的身份（见上文）决定了它在指定 metalake 中可以看到的内容，这与通过 REST API 完全相同。请注意，调用者现在可以访问其凭据允许的任何 metalake，因此在必要时请相应地限制凭据的范围。

### 示例

单一 metalake，代理从不考虑它——常见情况，且保持不变：

```bash
uv run mcp_server --metalake test --gravitino-uri http://127.0.0.1:8090
```

一台服务器后端有多个 metalakes，默认为 `prod`：

```bash
uv run mcp_server --metalake prod --transport http --mcp-url http://0.0.0.0:8000/mcp
```

然后代理默认在 `prod` 中工作，并在被要求时按请求切换 —— 当被问到“暂存 metalake 中有哪些目录？”时，仅在该次调用中发送 `metalake=staging`，无需重启或重新配置任何内容。

完全没有默认值，每次调用都进行选择：

```bash
uv run mcp_server --transport http --mcp-url http://0.0.0.0:8000/mcp
```

## 审计日志

每次工具调用都会在 `gravitino-mcp-audit.log` 中记录为一行结构化的 JSON 数据（写入服务器的工作目录）。如果存在传入的 HTTP `Authorization` 头，每条记录都会归属于该头；否则归属于配置的服务身份（`--token` 或 OAuth 客户端 ID）。

| 字段        | 描述                                                                                                                                                                             |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `timestamp`  | 调用的 UTC ISO-8601 时间。                                                                                                                                                          |
| `principal`  | 调用者身份：`Basic` 简单认证的用户名，Bearer 令牌的 `bearer:<first-8-chars>`，当 OAuth client-credentials 是服务身份（stdio 或无 caller header 的 HTTP）时的 `oauth:<first-8-chars-of-client-id>`，或当不存在身份时的 `anonymous`。 |
| `tool`       | 调用的 MCP 工具的名称。                                                                                                                                                           |
| `outcome`    | 成功调用为 `allow`，失败调用为 `deny`。任何工具调用异常都会发出 `deny`（授权拒绝是常见情况）；检查 `error_type` 以消除歧义。 |
| `error_type` | 异常类名，仅在 `outcome` 为 `deny` 时出现。                                                                                                                            |

示例记录：

```json
{"timestamp": "2026-06-16T03:21:09.123456+00:00", "principal": "alice", "tool": "get_list_of_catalogs", "outcome": "allow"}
```
