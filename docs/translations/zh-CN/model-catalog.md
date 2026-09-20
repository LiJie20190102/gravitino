---
title: "Model Catalog"
slug: "/model-catalog"
keyword: "model catalog, ML model, model version, model registry, Gravitino"
license: "This software is licensed under the Apache License version 2."
---

## 简介

模型目录是机器学习模型的注册表。它遵循相同的三级命名空间
与所有其他目录一样，即目录、架构、模型，并在每个模型下添加第四级
用于其版本。

它存储的是从名称到位置的映射。而不是作业和 notebook 携带一个
模型文件的路径，它们通过名称解析模型并获取所请求的版本。模型
文件本身保留在它们所在的位置。

正是这种间接性使得其余一切成为可能。模型与表处于相同的层级结构中
它们训练所用的，像其他任何对象一样带有标签和策略，并且由相同的角色
和权限管理。

Gravitino 自行管理此目录，而不是联合外部注册表，因此模型
目录不需要提供者。

## 快速开始

**1. 创建模型目录和模式。** 参见
[目录和模式](./catalogs-and-schemas.md)。模型目录不需要 provider，并且没有
必需的属性。

**2. 注册模型。** 注册会将模型创建为一个尚无版本的命名对象。

**3. 链接一个版本。** 一个版本包含模型所在的 URI，以及你想要用来
解析它的任何别名。

## 模型注册表

### 模型与版本

模型是模式中的一个命名对象，并且没有自己的位置。

模型版本是该模型的一次发布。它包含文件所在的 URI，一个可选的
注释、其自身的属性，以及从零开始按顺序分配的版本号。一个新的
发布是一个新版本，而不是对现有版本的编辑。

### 别名

一个版本可以带有别名，并且别名解析到版本的方式与其编号相同。这
就是诸如 `production` 或 `champion` 这样的移动指针的表达方式：链接一个新版本，移动
别名，并且所有通过该别名解析的内容都会获取新发布，而无需任何代码
更改。

在模型内，别名一次仅属于一个版本。

### 单个版本上的多个 URI

一个版本可以携带多个 URI，每个 URI 都有一个名称，以映射而非单个值的形式保存。
这就是同一个发布版本在多个地方被描述的方式，例如每个区域或每个
存储系统都有一个副本。

`default-uri-name` 决定当调用者未指定名称时返回哪一个，并且可以设置在
版本上或模型上，作为其所有版本的默认值。未提供名称的 URI 将被
记录为 `unknown`。

### 属性

Neither the catalog nor its schemas have predefined properties beyond the
[common catalog properties](./gravitino-server-config.md#catalog-properties-configuration). Models
and versions carry free-form properties of their own, with `default-uri-name` reserved.

## 在 UI 中使用模型

打开模型目录会列出其架构以及其中的模型。模型会显示其版本，
它们的 URI 及其别名，并且可以从那里链接版本。

模型显示其携带的标签，包括继承的标签，但无法从 UI 添加标签
今天。为模型附加标签需通过 API 进行。

## 权限

模型遵循包含它们的目录和架构的权限。参见
[目录和架构](./catalogs-and-schemas.md)。

## 使用 API

模型和版本可以被注册、链接、列出、修改和删除，通过 REST 以及
Java 和 Python 客户端。端点、负载结构和实际示例位于
[管理模型元数据](./manage-model-metadata-using-gravitino.md) 中。
