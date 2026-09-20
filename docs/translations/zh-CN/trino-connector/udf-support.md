---
title: "Trino Connector UDF Support"
slug: "/trino-connector/udf-support"
keyword: "gravitino connector trino udf function"
license: "This software is licensed under the Apache License version 2."
---

## 简介

Gravitino Trino 连接器支持在 Apache Gravitino 中注册的用户定义函数（UDFs）。
具有 `RuntimeType.TRINO` 和 SQL 语言实现的函数会自动暴露为
[Trino 语言函数](https://trino.io/docs/current/routines/function.html)，使其能够在 Trino 查询中使用。

## 机制

当 Gravitino catalog 包含已注册的函数时，Trino 连接器：

1. 列出 Gravitino 服务器中每个 schema 的函数。
2. 过滤以仅包含带有 `RuntimeType.TRINO` 和 `Language.SQL` 的函数。
3. 将每个函数实现映射到 Trino `LanguageFunction`，其签名令牌由函数名和参数类型派生而来。

只有语言为 `SQL` 且运行时为 `TRINO` 的函数对 Trino 可见并可从 Trino 调用。为其他语言或运行时（例如运行时为 `SPARK` 的 Python 或 Java 实现）注册的函数在 Gravitino 中进行管理，但**不**会通过此连接器公开：它们不会出现在 `SHOW FUNCTIONS` 中，并且调用其中一个会失败并报 Trino `Function "<catalog>.<schema>.<name>" not registered` 错误。该函数仍然存在于 Gravitino 中；连接器只是将其过滤掉。Gravitino UI 函数详细视图会针对每个实现显示其是否通过 Trino 连接器公开。

### SQL 主体格式

`SQL`/`TRINO` 实现的 `sql` 字段是函数体。连接器根据函数名、参数、返回类型和确定性标志组装出完整的 [Trino SQL routine](https://trino.io/docs/current/routines/function.html) 规范（`FUNCTION <name>(<params>) RETURNS <type> [NOT] DETERMINISTIC SECURITY INVOKER ...`），然后再将其交给 Trino。函数体可以是：

- 一个裸表达式，例如 `x + 1`。连接器将其包装为 `RETURN x + 1`。
- 一个控制语句，例如 `RETURN x + 1` 或 `BEGIN ... END`。

形式由主体的第一个标记决定，忽略开头的 SQL 注释。由于 `return`、`begin` 和 `function` 也是有效的标识符，具有这些名称之一的参数会遮蔽关键字：此时主体总是被视为一个表达式，例如，对于名为 `return` 的参数，为 `return + 1`。不支持本身即为完整 `FUNCTION ...` 规范的主体，并且该函数会被跳过并发出警告。

在生成的规范中，函数、参数和行字段名称被加上了引号。无论是否加引号，Trino 都不区分大小写地解析例程和参数名称，因此主体可以将参数作为普通标识符引用。

## 先决条件

- Gravitino catalog 必须支持函数操作（即实现 `FunctionCatalog`）。
- 必须先通过 Gravitino 客户端或 REST API 在 Gravitino 中注册函数，然后才能从 Trino 中查询它们。

## 注册 UDF

使用 Gravitino Java 客户端注册一个函数：

```java
FunctionCatalog functionCatalog = catalog.asFunctionCatalog();
functionCatalog.registerFunction(
    NameIdentifier.of("my_schema", "add_one"),
    "Adds one to input",
    FunctionType.SCALAR,
    true,
    FunctionDefinitions.of(
        FunctionDefinitions.of(
            FunctionParams.of(FunctionParams.of("x", Types.IntegerType.get())),
            Types.IntegerType.get(),
            FunctionImpls.of(
                FunctionImpls.ofSql(FunctionImpl.RuntimeType.TRINO, "RETURN x + 1")))));
```

## 从 Trino 查询 UDFs

注册后，该函数将出现在 Trino 中：

```sql
-- List available functions in a schema
SHOW FUNCTIONS FROM catalog.my_schema;

-- Invoke the function
SELECT catalog.my_schema.add_one(5);
-- Returns: 6
```

## 局限性

- **只读**：Trino 连接器支持列出和调用 Gravitino UDF。尚不支持通过 Trino SQL（`CREATE FUNCTION` / `DROP FUNCTION`）创建或删除函数。
- **仅限 SQL**：仅映射 SQL 语言实现。Java 和 Python 实现不会暴露给 Trino。
- **仅限 TRINO 运行时**：仅具有 `RuntimeType.TRINO` 的函数可见。使用 `RuntimeType.SPARK` 或其他运行时注册的函数将被过滤掉，并在调用时因 `Function ... not registered` 而失败。
- **仅限标量**：仅暴露 `SCALAR` 函数。聚合函数和表值函数将被跳过。
- **无参数默认值**：Trino SQL 例程不支持参数默认值，因此参数的 `defaultValue` 将被忽略，并且在从 Trino 调用时该参数是必需的。
- **类型映射**：函数参数和返回类型从 Gravitino 类型转换为 Trino 类型。不支持的类型将导致该函数被跳过并记录警告日志。
