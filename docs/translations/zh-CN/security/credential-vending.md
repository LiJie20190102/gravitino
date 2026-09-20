---
title: "Credential Vending"
slug: "/security/credential-vending"
keyword: "security credential vending"
license: "This software is licensed under the Apache License version 2."
---

## 背景

Gravitino 凭据分发用于生成访问数据的临时或静态凭据。借助凭据分发，Gravitino 提供了一种统一的方式来控制跨不同平台对多种数据源的访问。

## 支持的目录

| Catalog type | Vends                           |
|--------------|---------------------------------|
| Fileset      | S3, OSS, GCS, ADLS, COS         |
| Hive         | S3, OSS, GCS, ADLS              |
| Iceberg      | S3, OSS, GCS, ADLS              |
| Glue         | S3                              |
| JDBC         | JDBC 用户名和密码          |
| Paimon       | S3, OSS, JDBC 用户名和密码 |

S3 是 Amazon S3，OSS 是 Alibaba Cloud OSS，GCS 是 Google Cloud Storage，ADLS 是 Azure Data Lake Storage，COS 是 Tencent Cloud COS。Gravitino Spark、Flink 和 Trino 连接器会自动为这些目录使用分发凭证。

## 快速开始

通过 IRC 向 Spark 下发限定范围的 S3 凭证。通过 Gravitino REST catalog API 创建 catalog：

```shell
curl -X POST http://localhost:8090/api/metalakes/{metalake}/catalogs \
-H "Content-Type: application/json" \
-d '{
  "name": "iceberg_catalog",
  "type": "RELATIONAL",
  "provider": "lakehouse-iceberg",
  "properties": {
    "catalog-backend": "jdbc",
    "uri": "jdbc:postgresql://{postgres_host}:5432/{database}",
    "jdbc-driver": "org.postgresql.Driver",
    "jdbc-user": "{jdbc_user}",
    "jdbc-password": "{jdbc_password}",
    "jdbc-initialize": "true",
    "warehouse": "s3://{bucket_name}/{warehouse_path}",
    "io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
    "credential-providers": "s3-token",
    "s3-access-key-id": "{access_key_id}",
    "s3-secret-access-key": "{secret_access_key}",
    "s3-region": "{region_name}",
    "s3-role-arn": "{role_arn}"
  }
}'
```

将 Spark 指向 IRC，并使用 delegation 标头请求 vended credentials：

```shell
./bin/spark-sql -v \
--packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0,org.apache.iceberg:iceberg-aws-bundle:1.10.0 \
--conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
--conf spark.sql.catalog.rest=org.apache.iceberg.spark.SparkCatalog \
--conf spark.sql.catalog.rest.type=rest \
--conf spark.sql.catalog.rest.uri=http://127.0.0.1:9001/iceberg/ \
--conf spark.sql.catalog.rest.prefix=iceberg_catalog \
--conf spark.sql.catalog.rest.header.X-Iceberg-Access-Delegation=vended-credentials
```

`s3-role-arn` 中的角色需要具备信任策略和 S3 权限才能正常工作。参见 [`s3-token`](#s3-token)。

对于 Trino 而不是 Spark：

```properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://127.0.0.1:9001/iceberg/
iceberg.rest-catalog.prefix=iceberg_catalog
iceberg.rest-catalog.vended-credentials-enabled=true
fs.native-s3.enabled=true
s3.region={region_name}
```

有关完整的 Trino 设置，请参阅[将 Trino 连接到 IRC](../iceberg-rest-engine/trino.md)。

## 设置属性

当你通过 Gravitino REST catalog API 创建它时，凭据分发属性会与仓库位置和其他 catalog 设置一起放入 catalog 的 `properties` map 中。

Gravitino Iceberg REST Catalog (IRC) 是个例外。它也可以直接从 `gravitino.conf` 读取 catalog，使用以 `gravitino.iceberg-rest.` 为前缀的相同属性名：

```properties
s3-role-arn                             # as a catalog property
gravitino.iceberg-rest.s3-role-arn      # in gravitino.conf
```

在 `gravitino.conf` 中定义的目录未在 metalake 中注册，因此 Gravitino 访问控制不适用于它们。权限是在 metalake 中的目录上授予的，因此没有可供授予权限的对象。

## 常规配置

| 属性                        | 描述                                                                                                                       | 默认值 | 必填             |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|---------------|----------------------|
| `credential-providers`          | 凭据提供者类型，以逗号分隔。如果省略，Gravitino 会从现有的其他属性中推断部分提供者。 | (无)        | 是，除非已推断 |
| `credential-cache-expire-ratio` | Gravitino 从缓存中移除凭据时的凭据过期时间比率。                                   | 0.15          | 否                   |
| `credential-cache-max-size`     | 凭据缓存的最大容量。                                                                                                | 10000         | 否                   |

### `credential-providers` 的值

| 值                | 存储 | Vends                                                      |
|----------------------|---------|------------------------------------------------------------|
| `s3-token`           | S3      | 临时的 STS 凭证，范围限定在表路径        |
| `aws-irsa`           | S3      | 来自服务账户 IAM 角色的凭证，用于 EKS |
| `s3-secret-key`      | S3      | 已配置的静态访问密钥和密钥                |
| `oss-token`          | OSS     | 临时的 STS 凭证，范围限定在表路径        |
| `oss-secret-key`     | OSS     | 已配置的静态访问密钥和密钥                |
| `adls-token`         | ADLS    | 用户委托 SAS 令牌                                |
| `azure-account-key`  | ADLS    | 已配置的静态存储账户密钥                  |
| `gcs-token`          | GCS     | 降权访问令牌                                  |
| `cos-token`          | COS     | 临时的 STS 令牌                                      |
| `cos-secret-key`     | COS     | 已配置的静态访问密钥和密钥                |
| `jdbc-user-password` | JDBC    | 已配置的 JDBC 用户名和密码                  |

每个值都有其自身的属性，列在以下章节中。要在目录上为多种存储类型进行分发，请用逗号分隔值。可以通过实现 `CredentialProvider` 来添加自定义提供程序，这在[自定义凭据](#custom-credentials)中有描述。

### 当省略 `credential-providers` 时

如果 catalog 未设置 `credential-providers`，Gravitino 会从现有的凭据属性中推断提供者：

| 现有属性                                           | 提供程序已启用    |
|--------------------------------------------------------------|---------------------|
| `s3-access-key-id` 和 `s3-secret-access-key`                | `s3-secret-key`     |
| `oss-access-key-id` 和 `oss-secret-access-key`              | `oss-secret-key`    |
| `azure-storage-account-name` 和 `azure-storage-account-key` | `azure-account-key` |
| `gcs-service-account-file`                                   | `gcs-token`         |

JDBC 目录还会从 `jdbc-user` 和 `jdbc-password` 推断出 `jdbc-user-password`。

四个提供程序没有推断规则，必须始终显式设置：`s3-token`、`oss-token`、`adls-token` 和 `aws-irsa`。特别是，在没有设置 `credential-providers` 的情况下设置 `s3-role-arn` 并不会启用 `s3-token`。目录会回退到 `s3-secret-key` 并改为发放静态访问密钥，该密钥是长期有效的，且不限定于表路径。每当您需要基于令牌的发放时，请显式设置 `credential-providers`。

## S3

### `s3-token`

Gravitino 调用 STS [AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html) 并返回作用域限定为表路径的临时凭证。

| 属性                          | 描述                                                                                             | 默认值           | 必填       |
|-----------------------------|------------------------------------------------------------------------------------------------|---------------|----------|
| `s3-role-arn`               | Gravitino 担任的角色的 ARN，格式为 `arn:aws:iam::{account_id}:role/{role_name}`。   | (无)        | 是      |
| `s3-region`                 | S3 服务的区域，例如 `us-west-2`。                                                    | (无)        | 否       |
| `s3-token-expire-in-secs`   | 分发凭证的会话生命周期。不能超过角色的最大会话持续时间。 | 3600          | 否       |
| `s3-external-id`            | 在 AssumeRole 时传递的外部 ID，用于需要它的跨账户信任策略。           | (无)        | 否       |
| `s3-token-service-endpoint` | 备用的 STS 端点，用于诸如 MinIO 等 S3 兼容存储。                             | (无)        | 否       |

还需设置 `s3-access-key-id` 和 `s3-secret-access-key`。Gravitino 使用它们来调用 AssumeRole，而不是用于访问数据，并且它们永远不会被发送到引擎。

#### 角色上的信任策略

`s3-role-arn` 中的角色必须允许 `s3-access-key-id` 主体扮演它。否则，AssumeRole 将被拒绝，且不会发放任何凭证。

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::{account_id}:user/{gravitino_user}" },
    "Action": "sts:AssumeRole"
  }]
}
```

#### 角色的权限策略

分发的凭证继承此策略，范围缩小至表路径。若没有对仓库前缀的 S3 访问权限，凭证会被分发，但无法读取或写入。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::{bucket_name}/{warehouse_path}/*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": "arn:aws:s3:::{bucket_name}"
    }
  ]
}
```

### `aws-irsa`

对于在 EKS 上运行的 Gravitino。Gravitino 不使用访问密钥，而是使用其 pod 的 IAM 角色来调用 AssumeRole，因此整个设置中不存在任何静态密钥。

| 属性                    | 描述                                                                                    | 默认值 | 必填                    |
|-----------------------------|------------------------------------------------------------------------------------------------|---------------|-----------------------------|
| `s3-role-arn`               | 要扮演的角色的 ARN，格式为 `arn:aws:iam::{account_id}:role/{role_name}`。           | (无)        | 用于路径作用域凭证 |
| `s3-region`                 | 用于 STS 操作的 AWS 区域。                                                                 | (无)        | 否                          |
| `s3-token-expire-in-secs`   | 分发凭证的会话生命周期。不能超过角色的最大会话持续时间。 | 3600          | 否                          |
| `s3-token-service-endpoint` | 备用 STS 端点，用于兼容 S3 的存储。                                           | (无)        | 否                          |

设置 `s3-role-arn` 以获取作用域限定为表路径的凭证，并为每个表生成涵盖其数据、元数据和写入位置的 IAM 策略。如果没有它，分发的凭证将具有 pod 角色的完全权限。

`s3-role-arn` 中的角色需要与上面的 `s3-token` 相同的两个策略，除了信任策略指定的是 pod 的 IAM 角色而非 IAM 用户。

IRSA 本身必须已经配置在 pod 的 Kubernetes 服务账户上。配置好后，EKS 会将一个已签名的服务账户令牌注入到 pod 中，并将 `AWS_WEB_IDENTITY_TOKEN_FILE` 设置为其路径，AWS SDK 会使用该路径来获取凭证。如果发放失败，请检查 pod 中是否存在此变量。

### `s3-secret-key`

在 `loadTable` 响应中，将目录配置的访问密钥和密钥原样返回给客户端。

该密钥是长期有效的，携带其 IAM 用户拥有的所有权限，并且未限定在表路径范围内。任何能够加载表的客户端都会收到它，并且在查询结束后仍然有效。建议优先使用 `s3-token`，它会返回限定在表路径范围内的临时凭证。在配置角色之前，使用 `s3-secret-key` 来确认分发路径是否有效。

| 属性               | 描述                                          | 默认值 | 必填 |
|------------------------|------------------------------------------------------|---------------|----------|
| `s3-access-key-id`     | 用于访问 S3 数据的静态访问密钥 ID。     | (无)        | 是      |
| `s3-secret-access-key` | 用于访问 S3 数据的静态秘密访问密钥。 | (无)        | 是      |

## OSS

### `oss-token`

Gravitino 调用阿里云 STS [AssumeRole](https://www.alibabacloud.com/help/en/oss/developer-reference/use-temporary-access-credentials-provided-by-sts-to-access-oss) 并返回限定在表路径范围内的临时凭证。

还需要设置 `oss-access-key-id` 和 `oss-secret-access-key`。Gravitino 使用它们来调用 AssumeRole，而不是用于访问数据，并且它们永远不会被发送到引擎。

| 属性                   | 描述                                                                                                  | 默认值 | 必填 |
|----------------------------|--------------------------------------------------------------------------------------------------------------|---------------|----------|
| `oss-access-key-id`        | 用于访问 OSS 数据的静态访问密钥 ID。                                                            | (none)        | 是      |
| `oss-secret-access-key`    | 用于访问 OSS 数据的静态秘密访问密钥。                                                        | (none)        | 是      |
| `oss-role-arn`             | 用于访问 OSS 数据的角色 ARN。                                                                  | (none)        | 是      |
| `oss-region`               | OSS 服务的区域，例如 `oss-cn-hangzhou`，仅在 `credential-providers` 为 `oss-token` 时使用。 | (none)        | 否       |
| `oss-external-id`          | 用于生成令牌的 OSS 外部 ID。                                                                   | (none)        | 否       |
| `oss-token-expire-in-secs` | OSS 安全令牌的过期时间（以秒为单位）。                                                                  | 3600          | 否       |

#### RAM 角色的信任策略

`oss-role-arn` 中的角色必须允许 `oss-access-key-id` 主体扮演该角色。

```json
{
  "Version": "1",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:AssumeRole",
    "Principal": { "RAM": ["acs:ram::{account_id}:user/{gravitino_user}"] }
  }]
}
```

#### RAM 角色的权限策略

分发的凭证继承此策略，缩小至表路径。

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["oss:GetObject", "oss:PutObject", "oss:DeleteObject"],
      "Resource": "acs:oss:*:*:{bucket_name}/{warehouse_path}/*"
    },
    {
      "Effect": "Allow",
      "Action": ["oss:ListObjects", "oss:GetBucketInfo"],
      "Resource": "acs:oss:*:*:{bucket_name}"
    }
  ]
}
```

### `oss-secret-key`

将目录配置的访问密钥和 secret 原样返回给客户端。

该密钥是长期有效的，携带其 RAM 用户拥有的所有权限，并且不限定于表路径。任何能够加载表的客户端都会收到它，并且在查询完成后仍然有效。首选 `oss-token`。在配置角色之前，使用 `oss-secret-key` 确认分发路径是否正常工作。

| 属性                | 描述                                           | 默认值 | 必填 |
|-------------------------|-------------------------------------------------------|---------------|----------|
| `oss-access-key-id`     | 用于访问 OSS 数据的静态访问密钥 ID。     | (无)        | 是      |
| `oss-secret-access-key` | 用于访问 OSS 数据的静态秘密访问密钥。 | (无)        | 是      |

## COS

### `cos-token`

Gravitino 调用腾讯云 STS [AssumeRole](https://www.tencentcloud.com/document/product/598/33416) 并返回限定于表路径的临时凭证。该角色是腾讯云上的访问管理 (CAM) 角色；本节通篇使用 CAM 缩写。

还需设置 `cos-access-key-id` 和 `cos-secret-access-key`。Gravitino 使用它们来调用 AssumeRole，而不是用于访问数据，并且它们永远不会被发送到引擎。

| 属性                   | 描述                                                                                                                 | 默认值 | 必填 |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------|---------------|----------|
| `cos-access-key-id`        | Gravitino 用于调用 STS `AssumeRole` 的静态访问密钥 ID（腾讯云 `SecretId`）。                             | (无)        | 是      |
| `cos-secret-access-key`    | Gravitino 用于调用 STS `AssumeRole` 的静态秘密访问密钥（腾讯云 `SecretKey`）。                        | (无)        | 是      |
| `cos-role-arn`             | 要扮演的 CAM 角色的 ARN，例如 `qcs::cam::uin/100012345678:roleName/GravitinoCOSAccess`。                           | (无)        | 是      |
| `cos-region`               | 存储桶所在区域，例如 `ap-guangzhou`。用于构建 STS 端点和资源 ARN。                         | (无)        | 是      |
| `cos-app-id`               | 存储桶所有者的数字腾讯云 AppId（存储桶名称的末尾部分，例如 `1250000000`）。           | (无)        | 是      |
| `cos-external-id`          | 传递给 STS `AssumeRole` 的可选 `ExternalId`，用于将角色的信任策略锁定到 Gravitino。                          | (无)        | 否       |
| `cos-token-expire-in-secs` | COS 安全令牌的过期时间（以秒为单位）。不得超过角色的最大会话持续时间。                                | 3600          | 否       |

#### CAM 角色的信任策略

`cos-role-arn` 中的角色必须允许 `cos-access-key-id` 主体代入它。如果设置了 `cos-external-id`，信任策略必须要求相同的值。

```json
{
  "version": "2.0",
  "statement": [{
    "effect": "allow",
    "action": "name/sts:AssumeRole",
    "principal": { "qcs": ["qcs::cam::uin/{account_uin}:uin/{account_uin}"] },
    "condition": {
      "string_equal": { "sts:external_id": "{external_id}" }
    }
  }]
}
```

#### CAM 角色的权限策略

分发的凭证继承此策略，缩小至表路径。

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "cos:GetObject",
        "cos:HeadObject",
        "cos:PutObject",
        "cos:DeleteObject",
        "cos:InitiateMultipartUpload",
        "cos:UploadPart",
        "cos:ListParts",
        "cos:CompleteMultipartUpload",
        "cos:AbortMultipartUpload"
      ],
      "resource": "qcs::cos:{region}:uid/{app_id}:{bucket_name}-{app_id}/{warehouse_path}/*"
    },
    {
      "effect": "allow",
      "action": ["cos:GetBucket", "cos:HeadBucket", "cos:GetBucketLocation"],
      "resource": "qcs::cos:{region}:uid/{app_id}:{bucket_name}-{app_id}/*"
    }
  ]
}
```

### `cos-secret-key`

将目录配置的访问密钥和 secret 原样返回给客户端。

该密钥是长期有效的，携带其 CAM 用户拥有的所有权限，并且不限定于表路径。任何能够加载表的客户端都会接收到它，并且在查询结束后仍然保持有效。优先使用 `cos-token`。在配置角色之前，使用 `cos-secret-key` 来确认分发路径是否正常工作。

| 属性                | 描述                                           | 默认值 | 必填 |
|-------------------------|-------------------------------------------------------|---------------|----------|
| `cos-access-key-id`     | 用于访问 COS 数据的静态访问密钥 ID。     | (无)        | 是      |
| `cos-secret-access-key` | 用于访问 COS 数据的静态秘密访问密钥。 | (无)        | 是      |

## ADLS

### `adls-token`

Gravitino 请求一个 Azure [用户委托 SAS](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas) 并将其返回给客户端，作用域限定为表路径。

Azure 通过角色分配而非策略文档来授予访问权限。由 `azure-tenant-id`、`azure-client-id` 和 `azure-client-secret` 标识的 Microsoft Entra ID 服务主体需要两个角色：

- **存储 Blob 委派者**，在存储帐户上分配，允许其请求对 SAS 进行签名的用户委派密钥。
- **存储 Blob 数据参与者**，在容器或仓库路径上分配，这决定了所分发 SAS 的权限。对于只读访问，请使用 **存储 Blob 数据读取者**。

没有委派者角色，SAS 根本无法签发。没有数据角色，SAS 虽然会签发，但不授予任何权限。

| 属性                     | 描述                                                         | 默认值 | 必填 |
|------------------------------|---------------------------------------------------------------------|---------------|----------|
| `azure-storage-account-name` | 用于访问 ADLS 数据的静态存储账户名称。           | (无)        | 是      |
| `azure-tenant-id`            | Azure Active Directory (AAD) 租户 ID。                             | (无)        | 是      |
| `azure-client-id`            | 用于身份验证的 Azure Active Directory (AAD) 客户端 ID。     | (无)        | 是      |
| `azure-client-secret`        | 用于身份验证的 Azure Active Directory (AAD) 客户端密钥。 | (无)        | 是      |
| `adls-token-expire-in-secs`  | ADLS SAS 令牌过期时间（以秒为单位）。                             | 3600          | 否       |

### `azure-account-key`

将目录配置的存储帐户密钥原样返回给客户端。

存储账户密钥授予对存储账户中每个容器的完全访问权限，而不仅仅是仓库路径，并且它不会过期。任何能够加载表的客户端都会接收到它。首选 `adls-token`，它具有作用域且受时间限制。在配置服务主体之前，使用 `azure-account-key` 确认分发路径有效。

| 属性                     | 描述                                               | 默认值 | 必填 |
|------------------------------|-----------------------------------------------------------|---------------|----------|
| `azure-storage-account-name` | 用于访问 ADLS 数据的静态存储帐户名。 | (无)        | 是      |
| `azure-storage-account-key`  | 用于访问 ADLS 数据的静态存储帐户密钥。  | (无)        | 是      |

## GCS

### `gcs-token`

Gravitino 使用 GCS [凭据访问边界](https://cloud.google.com/iam/docs/downscoping-short-lived-credentials) 缩小其自身凭据的权限范围，并返回一个作用域限定为表路径的令牌。

没有要代入的角色。身份是 `gcs-service-account-file` 中的服务账号，或者在该项未设置时的应用默认凭据。在仓库存储桶上为该服务账号授予 **Storage Object User** (`roles/storage.objectUser`)，或者对于只读访问授予 **Storage Object Viewer**。缩小权限范围是基于这些权限进行的，因此分发的令牌永远不会超过服务账号本身所持有的权限。

| 属性                   | 描述                              | 默认值                       | 必填 |
|----------------------------|------------------------------------------|-------------------------------------|----------|
| `gcs-service-account-file` | GCS 凭证文件的位置。 | GCS 应用默认凭证。 | 否       |

`gcs-service-account-file` 既用于生成降权令牌，也用于在服务器上对 Iceberg `GCSFileIO` 进行身份验证（Gravitino 在加载 catalog 时会注入 `gcs.oauth2.token`，因为 Iceberg 没有 service-account-file 属性）。确保服务器进程可读取该文件。如果未设置该属性，FileIO 和令牌生成将回退到应用默认凭据（例如 GCE 元数据或 `GOOGLE_APPLICATION_CREDENTIALS`）。

## 请求 Vended Credentials

客户端如何请求取决于它使用的接口。

### 通过 IRC

仅在客户端请求时才会分发凭证。Spark、Flink 及其他 IRC 客户端通过请求头进行请求：

```
X-Iceberg-Access-Delegation: vended-credentials
```

在 Spark 中，将其设置为 catalog 配置键：

```properties
spark.sql.catalog.{name}.header.X-Iceberg-Access-Delegation=vended-credentials
```

Trino 改为使用 catalog 属性进行请求，并为你发送 header：

```properties
iceberg.rest-catalog.vended-credentials-enabled=true
```

### 通过 Gravitino REST Catalog API

Hive、Glue、JDBC、Paimon 和 Fileset 目录通过 Gravitino REST 目录 API 访问，该 API 没有委派标头。凭据属性在目录 GET 响应中被隐藏，因此客户端改为从 Gravitino 凭据端点获取它们。这适用于任何元数据对象：

```
GET /api/metalakes/{metalake}/objects/{type}/{full_name}/credentials
```

对于目录，`{type}` 是 `catalog`，`{full_name}` 是目录名称：

```
GET /api/metalakes/{metalake}/objects/catalog/{catalog}/credentials
```

Gravitino Spark 和 Flink 连接器会为你调用此方法并注入返回的凭据，因此无需进行客户端配置。

### 读写范围

在 IRC 上，当调用者有权修改表时，会分发用于写入的凭证，否则分发用于读取的凭证。使用 `X-Gravitino-Active-Roles` 标头缩小调用者的角色范围也会缩小此范围，因此，对于其活动角色不再包含 `MODIFY_TABLE` 的调用者，将分发只读凭证。参见 [使用活动角色缩小访问范围](access-control.md#narrowing-access-with-active-roles)。

## 自定义凭证

Gravitino 支持自定义凭据。你可以实现 `org.apache.gravitino.credential.CredentialProvider` 接口来支持自定义凭据，并将相应的 jar 包放置在 IRC 或 Fileset catalog 的 classpath 中。

## 部署

凭证提供程序的实现打包在单独的 jar 中。任何提供凭证的组件都需要在其 classpath 中包含正确的 jar，否则将无法创建提供程序，也不会提供任何凭证。

| Vending 组件 | Jar                                                | Classpath                                                                              |
|-------------------|----------------------------------------------------|----------------------------------------------------------------------------------------|
| IRC               | `gravitino-iceberg-{cloud}-bundle`                 | See [Deployment](../iceberg-rest-service.md#deployment); it differs by deployment mode |
| Iceberg catalog   | `gravitino-iceberg-{cloud}-bundle`                 | `catalogs/lakehouse-iceberg/libs/`                                                     |
| Fileset catalog   | `gravitino-{cloud}-bundle`                         | `catalogs/fileset/libs/`                                                               |
| Hive catalog      | `gravitino-{cloud}`                                | `catalogs/hive/libs/`                                                                  |
| Glue catalog      | `gravitino-aws`                                    | `catalogs/glue/libs/`                                                                  |
| Paimon catalog    | `gravitino-aws` for S3, `gravitino-aliyun` for OSS | `catalogs/lakehouse-paimon/libs/`                                                      |

将 `{cloud}` 替换为 `aws`、`gcp`、`aliyun` 或 `azure`。注意这两个 jar 系列：`-bundle` 变体还包含 Hadoop 和云 SDK 包，Fileset catalog 和 IRC 需要这些包。Hive、Glue 和 Paimon catalog 仅提供凭据，因此它们使用普通的 `gravitino-{cloud}` jar。

Gravitino Iceberg cloud bundle jar 包已经包含了 Iceberg cloud bundle jar 包，因此无需单独下载并引入它们。

提供 JDBC 用户和密码不需要额外的 jar。

Maven Central 上的 Bundle jar 包：

- [gravitino-aws-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aws-bundle), [gravitino-gcp-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-gcp-bundle), [gravitino-aliyun-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aliyun-bundle), [gravitino-azure-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-azure-bundle)
- [gravitino-iceberg-aws-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-aws-bundle), [gravitino-iceberg-gcp-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-gcp-bundle), [gravitino-iceberg-aliyun-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-aliyun-bundle), [gravitino-iceberg-azure-bundle](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-iceberg-azure-bundle)
- [gravitino-aws](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aws), [gravitino-aliyun](https://mvnrepository.com/artifact/org.apache.gravitino/gravitino-aliyun)

## 从早于 1.3.0 的版本升级

敏感的 catalog 属性（例如 `s3-access-key-id`、`s3-secret-access-key` 和 `jdbc-password`）会被掩码或排除在默认的 `GET /api/metalakes/{metalake}/catalogs/{catalog}` 响应之外（`jdbc-user` 和 `azure-storage-account-name` 以明文形式返回）。通过 `getSecrets` / `GET .../objects/{type}/{fullName}/secrets` 获取由 secret-manager 支持的属性和具有敏感名称的内联值。当属性名称看起来不敏感时，该 API **不**会恢复仅在元数据中声明为 `hidden` 的属性；这些属性在与 `properties()` 合并后保持为 `******`。凭证 API（`getCredentials` / `JdbcCredential`）仍然可用于类型化凭证传递。针对早期版本编写并直接从默认加载中读取这些属性的客户端将失去对它们的访问权限。

要进行零停机迁移，请在 `gravitino.conf` 中设置以下内容：

```properties
gravitino.catalog.credential.backfillToProperties = true
```

Gravitino 服务器随后会在其 catalog GET 响应中重新包含隐藏属性。一旦所有客户端都使用 Gravitino credential endpoint，请将其关闭，因为它会以明文形式暴露凭据。
