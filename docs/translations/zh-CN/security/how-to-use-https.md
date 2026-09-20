---
title: "HTTPS"
slug: "/security/how-to-use-https"
keywords:
  - security
  - https
  - tls
license: "This software is licensed under the Apache License version 2."
---

## 概述

HTTPS 会加密请求头，当这些请求头携带凭据时，这一点尤为重要。任何使用 OAuth 2.0 或 [本地用户和组](local-users-and-groups.md) 的部署都应启用它，因为两者都会在每次请求时将令牌或密码放入请求头中。

一个服务器实例服务于一种协议。启用 HTTPS 会停止纯 HTTP 监听器，而不是在其基础上增加，因此针对 HTTP 端口配置的客户端需要同时进行更新。

## 配置

Gravitino 服务器和 Iceberg REST 服务分别配置，在不同的前缀下使用相同的属性名称。Gravitino 服务器使用 `gravitino.server.webserver.`，Iceberg REST 服务使用 `gravitino.iceberg-rest.`。

| 属性名称             | 描述                                    | 默认值 | 必填                       |
|---------------------------|------------------------------------------------|---------------|--------------------------------|
| `enableHttps`             | 启用 HTTPS                                  | `false`       | 否                             |
| `httpsPort`               | Jetty Web 服务器的 HTTPS 端口            | `8433` 和 `9433` | 否                         |
| `keyStorePath`            | 密钥库文件的路径                     | (无)        | 是                            |
| `keyStorePassword`        | 密钥库的密码                     | (无)        | 是                            |
| `managerPassword`         | 密钥库的管理员密码             | (无)        | 是                            |
| `keyStoreType`            | 密钥库类型                                 | `JKS`         | 否                             |
| `tlsProtocol`             | 要使用的 TLS 协议，JVM 必须支持| (无)        | 否                             |
| `enableCipherAlgorithms`  | 要启用的加密算法                    | (空)       | 否                             |
| `enableClientAuth`        | 要求客户端使用证书进行身份验证 | `false`  | 否                             |
| `trustStorePath`          | 信任库文件的路径                   | (无)        | 是，需配合客户端身份验证 |
| `trustStorePassword`      | 信任库的密码                   | (无)        | 是，需配合客户端身份验证 |
| `trustStoreType`          | 信任库类型                               | `JKS`         | 否                             |

Gravitino 服务器的默认 HTTPS 端口为 `8433`，Iceberg REST 服务的默认 HTTPS 端口为 `9433`。当 `enableHttps` 为 `true` 时，“必填”列中的所有内容均适用。

关于 `tlsProtocol` 和 `enableCipherAlgorithms` 所接受的值，请分别参阅 Java 安全指南中“附加 JSSE 标准名称”部分下的 [协议](https://docs.oracle.com/javase/8/docs/technotes/guides/security/StandardNames.html#jssenames) 和 [密码套件](https://docs.oracle.com/javase/8/docs/technotes/guides/security/StandardNames.html#ciphersuites)。

## 本地开发示例

以下内容生成一个自签名证书，以便您可以在单台机器上测试 HTTPS 端点。这不是生产配置，因为通过编辑 JVM 信任库来信任自签名证书并非实际部署中管理证书的方式。

**1. 生成密钥库。**

```shell
cd $JAVA_HOME
bin/keytool -genkeypair -alias localhost \
  -keyalg RSA -keysize 4096 -keypass {key_password} \
  -sigalg SHA256withRSA \
  -keystore localhost.jks -storetype JKS -storepass {store_password} \
  -dname "cn=localhost,ou=localhost,o=localhost,l=beijing,st=beijing,c=cn" \
  -validity 36500
```

**2. 导出证书。**

```shell
bin/keytool -export -alias localhost -keystore localhost.jks \
  -file localhost.crt -storepass {store_password}
```

**3. 将其导入 JVM 信任库**，以便本地 Java 客户端接受它。

```shell
bin/keytool -import -alias localhost -keystore jre/lib/security/cacerts \
  -file localhost.crt -storepass changeit -noprompt
```

**4. 配置服务器。** 将以下内容追加到 `conf/gravitino.conf`，然后启动 Gravitino。配置文件不会解析环境变量，因此请写入展开的路径，而不是 `${JAVA_HOME}`。

```properties
gravitino.server.webserver.host = localhost
gravitino.server.webserver.enableHttps = true
gravitino.server.webserver.keyStorePath = {java_home}/localhost.jks
gravitino.server.webserver.keyStorePassword = {store_password}
gravitino.server.webserver.managerPassword = {key_password}
```

**5. 连接。** 在 Java 中，客户端直接获取 HTTPS URI：

```java
import org.apache.gravitino.client.GravitinoClient;
import org.apache.gravitino.client.GravitinoVersion;

public class Main {
    public static void main(String[] args) {
        String uri = "https://localhost:8433";
        GravitinoClient client = GravitinoClient.builder(uri).withMetalake("metalake").build();
        GravitinoVersion gravitinoVersion = client.getVersion();
        System.out.println(gravitinoVersion);
    }
}
```

对于 `curl`，先将证书转换为 PEM：

```shell
openssl x509 -inform der -in $JAVA_HOME/localhost.crt -out certificate.pem
curl -v -X GET --cacert ./certificate.pem \
  -H "Accept: application/vnd.gravitino.v1+json" \
  https://localhost:8433/api/version
```

## 延伸阅读

- 有关 Web 服务器其余设置的[配置](../gravitino-server-config.md)
- 有关 HTTPS 保护的身份验证方法的[如何进行身份验证](how-to-authenticate.md)
