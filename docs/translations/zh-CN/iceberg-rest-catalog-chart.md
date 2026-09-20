---
title: "Install Iceberg REST Catalog Server on Kubernetes"
slug: "/iceberg-rest-catalog-chart"
keyword:
  - Iceberg REST Helm Chart
license: "This software is licensed under the Apache License version 2."
---

## 简介

此 Helm chart 在 Kubernetes 上部署 Apache Gravitino Iceberg REST Catalog Server，并支持自定义配置。

## 先决条件

- Kubernetes 1.29+
- Helm 3+

## 安装

### 从 OCI Registry 安装（推荐用于已发布版本）

从 Docker Hub OCI 注册表拉取 chart：

```console
helm pull oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION>
```

或者直接安装：

```console
helm upgrade --install gravitino-iceberg oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION> -n gravitino --create-namespace
```

### 从本地仓库安装（用于开发或未发布版本）

克隆仓库并进入 chart 目录：

```console
git clone https://github.com/apache/gravitino.git
cd gravitino/dev/charts
```

更新图表依赖：

```console
helm dependency update gravitino-iceberg-rest-server
```

安装 chart：

```console
helm upgrade --install gravitino-iceberg ./gravitino-iceberg-rest-server -n gravitino --create-namespace
```

## 查看图表值

自定义 values.yaml 参数以覆盖 chart 默认设置。此外，[gravitino-iceberg-rest-server.conf](../dev/charts/gravitino-iceberg-rest-server/resources/gravitino-iceberg-rest-server.conf) 中的 Gravitino Iceberg REST Catalog Server 配置可以通过 Helm values.yaml 进行修改。

要显示图表的默认值，请运行：

```console
helm show values oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION>
```

## 安装 Helm Chart

```console
helm upgrade --install [RELEASE_NAME] oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION> [flags]
```

### 使用默认配置部署

运行以下命令，使用默认设置部署 Gravitino Iceberg REST Catalog Server：

```console
helm upgrade --install gravitino-iceberg oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION> \
  -n gravitino \
  --create-namespace \
  --set replicas=2 \
  --set resources.requests.memory="4Gi" \
  --set resources.requests.cpu="2"
```

### 使用自定义配置部署

若要自定义部署，请使用 --set 标志覆盖特定值：

```console
helm upgrade --install gravitino-iceberg oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION> \
  -n gravitino \
  --create-namespace \
  --set key1=val1,key2=val2,...
```

或者，您也可以提供自定义的 values.yaml 文件：

```console
helm upgrade --install gravitino-iceberg oci://registry-1.docker.io/apache/gravitino-iceberg-rest-server-helm --version <VERSION> \
  -n gravitino \
  --create-namespace \
  -f /path/to/values.yaml
```

## 卸载 Helm Chart

```console
helm uninstall [RELEASE_NAME] -n [NAMESPACE]
```
