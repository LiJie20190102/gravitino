---
title: "Spark Authentication"
slug: "/spark-connector/spark-authentication"
keyword: "spark connector authentication basic oauth2 kerberos"
license: "This software is licensed under the Apache License version 2."
---

## 概述

Spark 连接器在访问 Gravitino 服务器时支持 `simple`、`basic`、`oauth2` 和 `kerberos` 身份验证。

| 属性                     | 类型   | 默认值 | 描述                                                                                                                          | 必填 |
|------------------------------|--------|---------------|--------------------------------------------------------------------------------------------------------------------------------------|----------|
| spark.sql.gravitino.authType | string | `simple`      | 用于与 Gravitino 服务器通信的身份验证机制。支持的值：`simple`、`basic`、`oauth2`、`kerberos`。 | 否       |

## 简单模式

在简单模式下，用户名源自 Spark，并通过以下顺序获取：
1. 环境变量 `SPARK_USER`
2. 环境变量 `HADOOP_USER_NAME`
3. 机器上的登录用户

## 基本模式

在 Basic 模式下，Spark 连接器使用 HTTP Basic 凭据向 Gravitino 服务器进行身份验证
针对本地用户存储。Gravitino 服务器必须启用 Basic 身份验证。参见
[如何进行身份验证](../security/how-to-authenticate.md#basic-mode) 了解服务器端设置。

| 属性                           | 类型   | 默认值 | 描述                                    | 必填            |
|------------------------------------|--------|---------------|------------------------------------------------|---------------------|
| spark.sql.gravitino.authType       | string | `simple`      | 设置为 `basic` 以启用 Basic 认证。 | 是，适用于 Basic 模式 |
| spark.sql.gravitino.basic.username | string | (none)        | 本地用户存储中的用户名。                     | 是，适用于 Basic 模式 |
| spark.sql.gravitino.basic.password | string | (none)        | 该用户的密码。                     | 是，适用于 Basic 模式 |

### 基础配置示例

```properties
spark.plugins=org.apache.gravitino.spark.connector.plugin.GravitinoSparkPlugin
spark.sql.gravitino.uri=http://localhost:8090
spark.sql.gravitino.metalake=my_metalake
spark.sql.gravitino.authType=basic
spark.sql.gravitino.basic.username=admin
spark.sql.gravitino.basic.password=YourSecureGravitinoPassword
```

## OAuth2 模式

在 OAuth2 模式下，您可以使用以下配置获取 OAuth2 令牌以访问 Gravitino 服务器。

| 属性                              | 类型   | 默认值 | 描述                                   | 必填             |
|---------------------------------------|--------|---------------|-----------------------------------------------|----------------------|
| spark.sql.gravitino.oauth2.serverUri  | string | None          | OAuth2 服务器的 URI 地址。                | 是，用于 OAuth2 模式 |
| spark.sql.gravitino.oauth2.tokenPath  | string | None          | OAuth2 服务器中 token 接口的路径。 | 是，用于 OAuth2 模式 |
| spark.sql.gravitino.oauth2.credential | string | None          | 请求 OAuth2 token 的凭证。   | 是，用于 OAuth2 模式 |
| spark.sql.gravitino.oauth2.scope      | string | None          | 请求 OAuth2 token 的范围。        | 是，用于 OAuth2 模式 |

## Kerberos 模式

在 kerberos 模式下，您可以使用 Spark kerberos 配置来获取 kerberos 票据以访问 Gravitino 服务器，使用 `spark.kerberos.principal`、`spark.kerberos.keytab` 来指定 kerberos principal 和 keytab。

Gravitino 服务器 principal 的格式为 `HTTP/$host@$realm`。请保持 `$host` 与 Gravitino 服务器 URI 中的主机一致。
请确保 Spark 可以访问 `krb5.conf`，例如通过指定配置 `spark.driver.extraJavaOptions="-Djava.security.krb5.conf=/xx/krb5.conf"`。
