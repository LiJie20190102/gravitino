---
slug: /development/custom-job-executor
keyword: job executor, job system, extension, JobExecutor, Gravitino
license: This software is licensed under the Apache License version 2.
---
## 简介

Gravitino 内置的 `local` 作业执行器在 Gravitino 服务器上以进程方式运行作业，
仅用于测试。若要在其他环境（如分布式调度器）中运行作业，
则需要实现自定义作业执行器。

## 实现自定义作业执行器

Gravitino 的作业系统是可扩展的：可以实现自定义作业执行器
以在分布式环境中运行作业。请参阅代码中的 `JobExecutor` 接口，
见[此处](https://github.com/apache/gravitino/blob/main/core/src/main/java/org/apache/gravitino/connector/job/JobExecutor.java)。

实现自定义作业执行器后，需要通过
`gravitino.conf` 文件在 Gravitino 服务器中注册它。例如，若实现了名为
`airflow` 的作业执行器，需进行如下配置：

```
gravitino.job.executor = airflow
gravitino.jobExecutor.airflow.class = com.example.MyAirflowJobExecutor
```

通过附加属性配置作业执行器，如下：

```
gravitino.jobExecutor.airflow.host = http://localhost:8080
gravitino.jobExecutor.airflow.username = myuser
gravitino.jobExecutor.airflow.password = mypassword
```

实例化 airflow 作业执行器时将传递这些属性。