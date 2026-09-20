---
title: "Publish Docker Images"
slug: "/publish-docker-images"
keyword: "docker"
license: "This software is licensed under the Apache License version 2."
---


## 介绍

Apache Gravitino 项目提供了一组 Docker 镜像，以促进 Gravitino 项目的发布、开发和测试。
[Apache Docker Hub](https://hub.docker.com/u/apache) 仓库发布了官方的 Gravitino Docker 镜像。

## 将 Docker 镜像发布到 Docker Hub

使用 GitHub Actions 将 Docker 镜像发布到 Docker Hub 仓库。

1. 打开 [Docker 发布链接](https://github.com/apache/gravitino/actions/workflows/docker-image.yml)
2. 点击 `Run workflow` 按钮。
3. 选择您想要构建的分支
+ 选择主分支将发布带有指定标签和最新标签的 Docker 镜像。
+ 选择其他分支，将发布带有指定标签的 Docker 镜像。
4. 选择您想要构建的镜像
+ `apache/gravitino-ci:hive`。
+ `apache/gravitino-ci:trino`。
+ 未来的计划包括支持其他数据源。
5. 输入 `tag name`，例如：`0.1.0`，然后构建并推送 Docker 镜像名称。Docker 镜像名称的格式为：
1. 如果这是 trino CI 镜像，则为 `apache/gravitino-ci:{image-type}-0.1.0`，image-type 为 `trino`、`hive`、`kerberos-hive`、`doris`、`ranger`。
2. 如果这是 playground 镜像，则为 `apache/gravitino-playground:{image-type}-0.1.0`，image-type 为 `trino`、`hive`、`ranger`。
3. 如果这是 gravitino 服务器镜像，则为 `apache/gravitino:0.1.0`。
4. 如果这是 iceberg-rest 服务器镜像，则为 `apache/gravitino-iceberg-rest:0.1.0`。
6. 您必须输入正确的 `docker user name` 和 `publish docker token`，然后才能执行运行 `Publish Docker Image` 工作流。
7. 如果您想更新最新标签，请勾选 `Whether to update the latest tag` 复选框。
8. 等待工作流完成。一个新的 Docker 镜像将出现在 [Apache Docker Hub](https://hub.docker.com/u/apache) 仓库中。

![发布 Docker 镜像](assets/publish-docker-image.png)

## Docker 镜像的更多细节

+ [Gravitino Docker 镜像](docker-image-details.md)
