---
slug: /development/custom-partition-storage
keyword: partition statistics, storage, extension, PartitionStatisticStorageFactory,
  Gravitino
license: This software is licensed under the Apache License version 2.
title: 自定义分区存储
---
## 简介

分区统计使用可插拔的存储后端，通过
`gravitino.stats.partition.storageFactoryClass` 进行设置。Gravitino 内置了 JDBC 和 Lance 后端；编写
自定义后端意味着实现存储工厂接口。

## 实现自定义分区存储

通过实现接口 `org.apache.gravitino.stats.storage.PartitionStatisticStorageFactory` 并
将配置项 `gravitino.stats.partition.storageFactoryClass` 设置为该类名，来实现自定义分区存储。

例如：

```java
public class MyPartitionStatsStorageFactory implements PartitionStatisticStorageFactory {
    @Override
    public PartitionStatisticStorage create(Map<String, String> options) {
        // 在这里创建您的自定义 PartitionStatsStorage
        return new MyPartitionStatsStorage(...);
    }
}
```

```java
public class MyPartitionStatsStorage implements PartitionStatisticStorage {

    @Override
    public void close() throws IOException {
        // 在此处关闭您的存储
    }

    @Override
    public void updateStatistics(String metalake, List<MetadataObjectStatisticsUpdate> updates)
            throws IOException {
        // 在此处更新您的存储中的分区统计信息
    }

    @Override
    public List<PersistedPartitionStatistics> listStatistics(
            String metalake, MetadataObject metadataObject, PartitionRange range)
            throws IOException {
        // 在此处列出您的存储中的分区统计信息
        return Lists.newArrayList();
    }

    @Override
    public int dropStatistics(String metalake, List<MetadataObjectStatisticsDrop> drops)
            throws IOException {
        // 在此处删除您的存储中的分区统计信息，并返回实际删除的数量
        return drops.size();
    }
}
```