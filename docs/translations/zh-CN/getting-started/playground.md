---
slug: /getting-started/playground
license: This software is licensed under the Apache License version 2.
---
## 简介

Gravitino 提供了一组 Docker 镜像用于启动 Gravitino 演练场，
其中包括 Apache Hive、Apache Hadoop、Trino、MySQL、PostgreSQL 和 Gravitino。
使用 Docker Compose 启动全部组件。

安装 Docker 和 Docker Compose 是使用该演练场的前提条件。

```shell
sudo apt install docker docker-compose
sudo gpasswd -a $USER docker
newgrp docker
```

通过使用以下仓库，以 Docker 容器的方式安装并运行所有程序：
[gravitino-playground](https://github.com/apache/gravitino-playground)。
有关如何运行该演练场的详细信息，请参阅
[how-to-use-the-playground](../how-to-use-the-playground.md)