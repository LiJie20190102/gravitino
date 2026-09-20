---
slug: /chart
keyword: chart
license: This software is licensed under the Apache License version 2.
title: 在 Kubernetes 上安装 Gravitino
---
## 简介

此 Helm chart 用于在 Kubernetes 上部署 Apache Gravitino，并支持自定义配置。

## 前提条件

- Kubernetes 1.29+
- Helm 3+

## 安装

### 从 OCI Registry 安装（推荐用于已发布版本）

从 Docker Hub OCI registry 拉取 chart：

```console
helm pull oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION>
```

或者直接安装：

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> -n <NAMESPACE> --create-namespace
```

### 从本地仓库安装（用于开发或未发布版本）

克隆仓库并进入 chart 目录：

```console
git clone https://github.com/apache/gravitino.git
cd gravitino/dev/charts
```

更新 chart 依赖：

```console
helm dependency update gravitino
```

安装 chart：

```console
helm upgrade --install gravitino ./gravitino -n <NAMESPACE> --create-namespace
```

## 查看 Chart Values

自定义 values.yaml 参数可覆盖 chart 的默认设置。此外，gravitino.conf 中的 Gravitino 配置可通过 Helm values.yaml 进行修改。

运行以下命令以显示 Gravitino chart 的默认值：

```console
helm show values oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION>
```

## 安装 Helm Chart

```console
helm upgrade --install [RELEASE_NAME] oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> [flags]
```

### 使用默认配置部署

运行以下命令以使用默认设置部署 Gravitino：

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> -n <NAMESPACE> --create-namespace
```

### 使用自定义配置部署

要自定义部署，可使用 --set 标志覆盖特定值：

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> \
  -n <NAMESPACE> --create-namespace \
  --set key1=val1,key2=val2,...
```

或者，可以提供一个自定义的 values.yaml 文件：

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> \
  -n <NAMESPACE> --create-namespace \
  -f /path/to/values.yaml
```

### 使用 MySQL 作为存储后端部署 Gravitino

要同时部署 Gravitino 和 MySQL，并使 MySQL 作为存储后端，需启用内置的 MySQL 实例：

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> \
  -n <NAMESPACE> --create-namespace \
  --set mysql.enabled=true
```

#### 禁用动态存储分配

默认情况下，MySQL PersistentVolumeClaim(PVC) 的存储类为 local-path。要禁用动态分配，需将存储类设置为 "-"：

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> \
  -n <NAMESPACE> --create-namespace \
  --set mysql.enabled=true \
  --set global.defaultStorageClass="-"
```

然后手动创建 PersistentVolume (PV)。

### 使用现有 MySQL 数据库部署 Gravitino

确保准备好以下 MySQL 凭证：用户名、密码、数据库名称。在创建数据库时，建议将其命名为 `gravitino`。

在部署 Gravitino 之前，需初始化现有的 MySQL 实例，并创建 Gravitino 正常运行所需的数据表。

```console
mysql -h database-1.***.***.rds.amazonaws.com -P 3306 -u <YOUR-USERNAME> -p <YOUR-PASSWORD> < schema-0.*.0-mysql.sql
```

使用 Helm 安装或升级 Gravitino，并指定 MySQL 连接详情。

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> \
  -n <NAMESPACE> --create-namespace \
  --set entity.jdbcUrl="jdbc:mysql://database-1.***.***.rds.amazonaws.com:3306/gravitino" \
  --set entity.jdbcDriver="com.mysql.cj.jdbc.Driver" \
  --set entity.jdbcUser="admin" \
  --set entity.jdbcPassword="admin123"
```

_注意： \
请将 database-1.***.***.rds.amazonaws.com 替换为实际的 MySQL 主机。 \
将 admin 和 admin123 更改为实际的 MySQL 用户名和密码。 \
确保在部署前目标 MySQL 数据库 已存在。_

### 使用 GCS 作为对象存储部署 Gravitino

如果 catalog 使用 Google Cloud Storage (GCS) 作为对象存储，需要在容器中设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量，并挂载服务账号密钥文件。

1. 使用 GCS 服务账号密钥创建 Kubernetes secret：

```console
kubectl create secret generic gcs-key --from-file=key.json=/path/to/your-service-account-key.json -n <NAMESPACE>
```

2. 在自定义的 `values.yaml` 中使用 GCS 配置部署 Gravitino：

```yaml
env:
  - name: GRAVITINO_MEM
    value: "-Xms1024m -Xmx1024m -XX:MaxMetaspaceSize=512m"
  - name: GOOGLE_APPLICATION_CREDENTIALS
    value: /etc/gcs/key.json

extraVolumes:
  - name: gravitino-log
    emptyDir: {}
  - name: gcs-key
    secret:
      secretName: gcs-key

extraVolumeMounts:
  - name: gravitino-log
    mountPath: /opt/gravitino/logs
  - name: gcs-key
    mountPath: /etc/gcs
    readOnly: true
```

```console
helm upgrade --install gravitino oci://registry-1.docker.io/apache/gravitino-helm --version <VERSION> \
  -n <NAMESPACE> --create-namespace \
  -f /path/to/values.yaml
```

## 卸载 Helm Chart

```console
helm uninstall [RELEASE_NAME] -n <NAMESPACE>
```