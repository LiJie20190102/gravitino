---
title: "Playground"
slug: "/how-to-use-the-playground"
keyword: "playground"
license: "This software is licensed under the Apache License version 2."
---

## 简介

演练场是一个完整的 Apache Gravitino Docker 运行时环境，包含 `Apache Hive`、`HDFS`、`Trino`、`MySQL`、`Jupyter` 以及一个 `Apache Gravitino` 服务器。

取决于您的网络和计算机，启动时间可能需要 3-5 分钟。playground 环境启动后，您可以在浏览器中打开 [http://localhost:8090](http://localhost:8090) 以访问 Gravitino Web UI。

## 先决条件

安装 Git（可选）、Docker、Docker Compose。

## 系统资源要求

2 个 CPU 核心，8 GB 内存，25 GB 磁盘存储，MacOS 或 Linux 操作系统（已验证 Ubuntu22.04 Ubuntu24.04 AmazonLinux）。

## TCP 端口

演练场运行多个服务。使用的 TCP 端口可能会与您运行的现有服务（如 MySQL 或 Postgres）发生冲突。

| Docker 容器      | 使用的端口             |
| --------------------- | ---------------------- |
| playground-gravitino  | 8090 9001              |
| playground-hive       | 3307 19000 19083 60070 |
| playground-mysql      | 13306                  |
| playground-postgresql | 15342                  |
| playground-trino      | 18080                  |
| playground-jupyter    | 18888                  |
| playground-prometheus | 19090                  |
| playground-grafana    | 13000                  |

## Playground 用法

### 启动 Playground 的 Curl 命令

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/apache/gravitino-playground/HEAD/install.sh)"
```

### 使用 Git 启动 Playground

```shell
git clone git@github.com:apache/gravitino-playground.git
cd gravitino-playground
```

#### 开始

```
./playground.sh start
```

#### 检查状态

```shell 
./playground.sh status
```

#### 停止 Playground

```shell
./playground.sh stop
```

## 通过 Trino SQL 体验 Apache Gravitino

### Docker 容器中的 Trino CLI

1. 使用以下命令登录 Gravitino playground Trino Docker 容器：

```shell
docker exec -it playground-trino bash
````

2. 在容器中打开 Trino CLI。

```shell
trino@container_id:/$ trino
```

## Jupyter Notebook

1. 在浏览器中通过 [http://localhost:18888](http://localhost:18888) 打开 Jupyter Notebook。

2. 打开 `gravitino-trino-example.ipynb` 笔记本。

3. 启动 notebook 并运行单元格。

## Spark 客户端

1. 使用以下命令登录 Gravitino playground Spark Docker 容器：

```shell
docker exec -it playground-spark bash
````

2. 在容器中打开 Spark SQL 客户端。

```shell
spark@container_id:/$ cd /opt/spark && /bin/bash bin/spark-sql
```

## 监控 Gravitino

1. 在浏览器中打开 Grafana，地址为 [http://localhost:13000](http://localhost:13000)。

2. 在导航菜单中，点击 **Dashboards** -> **Gravitino Playground**。

3. 尝试默认模板。

## 示例

### 简单的 Trino 查询

在 Trino CLI 中使用简单查询进行测试。

```SQL
SHOW CATALOGS;

CREATE SCHEMA catalog_hive.company
  WITH (location = 'hdfs://hive:9000/user/hive/warehouse/company.db');

SHOW CREATE SCHEMA catalog_hive.company;

CREATE TABLE catalog_hive.company.employees
(
  name varchar,
  salary decimal(10,2)
)
WITH (
  format = 'TEXTFILE'
);

INSERT INTO catalog_hive.company.employees (name, salary) VALUES ('Sam Evans', 55000);

SELECT * FROM catalog_hive.company.employees;

SHOW SCHEMAS from catalog_hive;

DESCRIBE catalog_hive.company.employees;

SHOW TABLES from catalog_hive.company;
```

### 跨目录查询

在一家公司中，可能有不同的部门使用不同的数据栈。在本例中，人力资源部门使用 Apache Hive 来存储其数据，而销售部门使用 PostgreSQL。Gravitino 让您可以通过有趣的查询将这两个部门的数据连接在一起。

要想知道哪位员工的销售额最高，请运行以下 SQL：

```SQL
SELECT given_name, family_name, job_title, sum(total_amount) AS total_sales
FROM catalog_hive.sales.sales as s,
  catalog_postgres.hr.employees AS e
where s.employee_id = e.employee_id
GROUP BY given_name, family_name, job_title
ORDER BY total_sales DESC
LIMIT 1;
```

要了解各州购买最多的顶级客户，请运行以下 SQL：

```SQL
SELECT customer_name, location, SUM(total_amount) AS total_spent
FROM catalog_hive.sales.sales AS s,
  catalog_hive.sales.stores AS l,
  catalog_hive.sales.customers AS c
WHERE s.store_id = l.store_id AND s.customer_id = c.customer_id
GROUP BY location, customer_name
ORDER BY location, SUM(total_amount) DESC;
```

要了解员工的平均绩效评分和总销售额，请运行此 SQL：

```SQL
SELECT e.employee_id, given_name, family_name, AVG(rating) AS average_rating, SUM(total_amount) AS total_sales
FROM catalog_postgres.hr.employees AS e,
  catalog_postgres.hr.employee_performance AS p,
  catalog_hive.sales.sales AS s
WHERE e.employee_id = p.employee_id AND p.employee_id = s.employee_id
GROUP BY e.employee_id,  given_name, family_name;
```

### Spark 和 Trino

考虑使用 SparkSQL 生成数据，然后使用 Trino 查询这些数据。用 Gravitino 试一下：

1. 登录 Spark 容器并执行 SQL 语句：

```sql
// using Hive catalog to create Hive table
USE catalog_hive;
CREATE DATABASE product;
USE product;

CREATE TABLE IF NOT EXISTS employees (
    id INT,
    name STRING,
    age INT
)
PARTITIONED BY (department STRING)
STORED AS PARQUET;
DESC TABLE EXTENDED employees;

INSERT OVERWRITE TABLE employees PARTITION(department='Engineering') VALUES (1, 'John Doe', 30), (2, 'Jane Smith', 28);
INSERT OVERWRITE TABLE employees PARTITION(department='Marketing') VALUES (3, 'Mike Brown', 32);
```

2. 登录 Trino 容器并执行 SQL：

```sql
SELECT * FROM catalog_hive.product.employees WHERE department = 'Engineering';
```

演示位于 `jupyter` 文件夹中，你可以打开 `gravitino-spark-trino-example.ipynb`
演示，通过 Jupyter Notebook 访问 [http://localhost:18888](http://localhost:18888)。

### Apache Iceberg REST 服务

假设你想将业务从 Hive 迁移到 Iceberg。一些表将使用 Hive，而其他表将使用 Iceberg。
Gravitino 提供了 Iceberg REST catalog 服务。使用 Spark 访问 REST catalog 来写入表数据。
然后，你可以使用 Trino 从 Hive 表读取数据，并将其与 Iceberg 表进行 join。

`spark-defaults.conf` 如下（已在 playground 中配置）：

```text
spark.sql.extensions org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.catalog.catalog_rest org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.catalog_rest.type rest
spark.sql.catalog.catalog_rest.uri http://gravitino:9001/iceberg/
spark.locality.wait.node 0
```

请注意，SparkSQL 中的 `catalog_rest` 与 Gravitino 和 Trino 中的 `catalog_iceberg` 共享同一个 Iceberg JDBC 后端，这意味着它们可以访问相同的数据集。

1. 登录 Spark 容器并执行这些步骤。

```shell
docker exec -it playground-spark bash
```

```shell
spark@container_id:/$ cd /opt/spark && /bin/bash bin/spark-sql
```

```SQL
use catalog_rest;
create database sales;
use sales;
create table customers (customer_id int, customer_name varchar(100), customer_email varchar(100));
describe extended customers;
insert into customers (customer_id, customer_name, customer_email) values (11,'Rory Brown','rory@123.com');
insert into customers (customer_id, customer_name, customer_email) values (12,'Jerry Washington','jerry@dt.com');
```

2. 登录 Trino 容器并执行步骤。
从 Hive 和 Iceberg 表中获取所有客户。

```shell
docker exec -it playground-trino bash
```

```shell
trino@container_id:/$ trino
```

```SQL
select * from catalog_hive.sales.customers
union
select * from catalog_iceberg.sales.customers;
```

演示位于 `jupyter` 文件夹中，你可以打开 `gravitino-spark-trino-example.ipynb`
演示，通过 Jupyter Notebook 访问 [http://localhost:18888](http://localhost:18888)。

### Gravitino 与 LlamaIndex

Gravitino playground 也提供了一个结合 LlamaIndex 的简单 RAG 演示。这个演示将向你展示
使用 Gravitino 管理表格和非表格数据集的能力，将其连接到
LlamaIndex 作为统一数据源，然后使用 LlamaIndex 和 LLM 查询表格和
非表格数据，通过一次自然语言查询。

演示位于 `jupyter` 文件夹中，您可以打开 `gravitino_llama_index_demo.ipynb`
演示，通过 Jupyter Notebook 访问 [http://localhost:18888](http://localhost:18888)。

本演示的场景是基础结构化城市统计数据存储在 MySQL 中，并且
详细的城市介绍存储在 PDF 文件中。用户希望在结构化数据和 PDF 文件中找到有关城市的答案。

在本演示中，您将使用 Gravitino 通过关系型目录管理 MySQL 表，以及 pdf
文件通过文件集目录，将 Gravitino 作为 LlamaIndex 的统一数据源来构建
表格和非表格数据的索引。然后，您可以使用 LLM 使用自然
语言查询来查询数据。

注意：要运行此演示，您需要在 `gravitino_llama_index_demo.ipynb` 中设置 `OPENAI_API_KEY`，
如下所示，`OPENAI_API_BASE` 是可选的。

```python
import os

os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_API_BASE"] = ""
```

<img src="https://analytics.apache.org/matomo.php?idsite=62&rec=1&bots=1&action_name=HowtoUsePlayground" alt="" />
