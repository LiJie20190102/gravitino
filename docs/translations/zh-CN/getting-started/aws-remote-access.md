---
slug: /getting-started/aws-remote-access
license: This software is licensed under the Apache License version 2.
title: AWS 上的远程访问
---
## 从外部访问 AWS 上的 Apache Gravitino

在 AWS 上部署 Gravitino 后，从外部访问需要
根据 AWS 网络的工作方式进行一些额外配置。

AWS 会为实例分配公网 IP 地址，但 Gravitino 无法绑定到该地址。
要解决此问题，必须找到分配给 AWS 实例的内网 IP 地址。
可在 AWS 控制台中查找私有 IP 地址，或运行以下命令：

```shell
ip a
```

确定内网地址后，修改 Gravitino 配置以绑定到该地址。
打开文件 `<gravitino-home>/conf/gravitino.conf`，将 `gravitino.server.webserver.host`
参数从 `127.0.0.1` 修改为 AWS 实例的私有 IP4 地址；
也可以使用 '0.0.0.0'。在此场景下，'0.0.0.0' 表示主机的 IP 地址。
重启 Gravitino 服务器使更改生效。

```shell
<gravitino-home>/bin/gravitino.sh restart
```

还需要在 AWS 实例的安全组中开放 8090 端口才能访问 Gravitino。
要访问 Hive，需要在安全组中开放 10000 端口。

完成上述步骤后，可以从本地计算机的
命令行或 Web 浏览器访问 Gravitino REST 接口。
通过 DBeaver 或其他数据库 IDE 连接 Hive。