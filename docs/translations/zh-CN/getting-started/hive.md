---
slug: /getting-started/hive
license: This software is licensed under the Apache License version 2.
title: 安装 Apache Hive
---
## 简介

要在 Google Cloud Platform 上手动安装 Apache Hive 和 Hadoop，
参考 [Apache Hive](https://cwiki.apache.org/confluence/display/Hive/) 和
[Hadoop](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html)。

安装和配置 Hive 可能有些复杂。
如果尚未配置并运行 Hive，可使用 Docker 容器
（由 Datastrato 提供）来启动并运行 Gravitino。

按照以下说明设置
[Ubuntu 上的 Docker](https://docs.docker.com/engine/install/ubuntu/)。

```shell
sudo docker run --name gravitino-container -d \
  -p 9000:9000 -p 8088:8088 -p 50010:50010 -p 50070:50070 \
  -p 50075:50075 -p 10000:10000 -p 10002:10002 -p 8888:8888 \
  -p 9083:9083 -p 8022:22 \
  apache/gravitino-playground:hive-0.1.15
```

Docker 安装完成后，可使用以下命令启动容器：

```shell
sudo docker start gravitino-container
```

<!--TODO: Add some instructions for non-docker environment-->