---
title: "Sign and Verify Releases"
slug: "/how-to-sign-releases"
license: "This software is licensed under the Apache License version 2."
---

## 简介

这些说明提供了对 Apache Gravitino 发行版进行签名和验证的指南，以增强发行版的安全性。签名的发行版使人们能够确认发行版的作者，并保证代码未被篡改。

## 先决条件

在签名或验证 Gravitino 发行版之前，请确保已安装以下先决条件：

- GPG/GnuPG
- 发布产物

## 平台支持

这些说明适用于 macOS。您可能需要针对其他平台进行调整。

1. **如何安装 GPG 或 GnuPG：**

[GnuPG](https://www.gnupg.org) 是 OpenPGP 标准的开源实现，允许你加密和签名文件或电子邮件。GnuPG，也称为 GPG，是一个命令行工具。

运行以下命令检查是否已安装 GPG：

   ```shell
   gpg -help
   ```

如果未安装 GPG/GnuPG，请运行以下命令进行安装。此步骤只需执行一次。

    ```shell
    brew install gpg
    ```

## 签署发行版

1. **创建一个公钥/私钥对：**

运行以下命令，检查你是否已有公钥/私钥对：

    ```shell
    gpg --list-secret-keys
    ```

如果没有输出，你需要生成一个公钥/私钥对。

使用此命令生成公钥/私钥对。这是一个一次性过程。将密钥过期时间设置为 5 年并省略注释。所有其他默认设置均可接受。

    ```shell
    gpg --full-generate-key
    ```

以下是使用上一条命令生成公钥/私钥对的示例。

    ```shell
    gpg (GnuPG) 2.4.3; Copyright (C) 2023 g10 Code GmbH
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.

    Please select what kind of key you want:
    (1) RSA and RSA
    (2) DSA and Elgamal
    (3) DSA (sign only)
    (4) RSA (sign only)
    (9) ECC (sign and encrypt) *default*
    (10) ECC (sign only)
    (14) Existing key from card
    Your selection?
    Please select which elliptic curve you want:
    (1) Curve 25519 *default*
    (4) NIST P-384
    (6) Brainpool P-256
    Your selection?
    Please specify how long the key should be valid.
            0 = key does not expire
        <n>  = key expires in n days
        <n>w = key expires in n weeks
        <n>m = key expires in n months
        <n>y = key expires in n years
    Key is valid for? (0) 5y
    Key expires at Mon 13 Nov 16:08:58 2028 AEDT
    Is this correct? (y/N) y

    GnuPG needs to construct a user ID to identify your key.

    Real name: John Smith
    Email address: john@apache.org
    Comment:
    You selected this USER-ID:
        "John Smith <john@apache.org>"

    Change (N)ame, (C)omment, (E)mail or (O)kay/(Q)uit? o
    We need to generate a lot of random bytes. It is a good idea to perform
    some other action (type on the keyboard, move the mouse, utilize the
    disks) during the prime generation; this gives the random number
    generator a better chance to gain enough entropy.
    We need to generate a lot of random bytes. It is a good idea to perform
    some other action (type on the keyboard, move the mouse, utilize the
    disks) during the prime generation; this gives the random number
    generator a better chance to gain enough entropy.
    gpg: revocation certificate stored as '/Users/justin/.gnupg/openpgp-revocs.d/CC6BD9B0A3A31A7ACFF9E1383DF672F671B7F722.rev'
    public and secret key created and signed.

    pub   ed25519 2023-11-15 [SC] [expires: 2028-11-13]
        CC6BD9B0A3A31A7ACFF9E1383DF672F671B7F722
    uid                      John Smith <john@apache.org>
    sub   cv25519 2023-11-15 [E] [expires: 2028-11-13]
    ```

:::caution important
请妥善保管你的私钥，并将其保存在除计算机以外的其他地方。不要忘记你的密钥密码，并且也要将其安全地记录在某个地方。如果你丢失了密钥或忘记了密码，你将无法对发布版本进行签名。
:::

2. **签署发布：**

要对发布版本进行签名，请对每个发布文件使用以下命令：

    ```shell
    gpg --detach-sign --armor <filename>.[zip|tar.gz]
    ```

例如，要对 Gravitino 0.2.0 发行版进行签名，您将使用此命令。

    ```shell
    gpg --detach-sign --armor gravitino.0.2.0.zip
    ```

这会生成一个包含 PGP 签名的 .asc 文件。任何人都可以使用此文件和您的公开签名来验证发布版本。

3. **为发布版本生成哈希：**

使用以下命令为发布版本生成哈希：

    ```shell
    shasum -a 256 <filename>.[zip|tar.gz] > <filename>.[zip|tar.gz].sha256
    ```

例如，要为 Gravitino 0.2.0 版本生成哈希，您可以使用以下命令：

    ```shell
    shasum -a 256 gravitino.0.2.0.zip > gravitino.0.2.0.zip.sha256
    ```

4. **将您的公钥复制到 KEYS 文件：**

KEYS 文件包含用于对先前版本进行签名的公钥。您只需执行此步骤一次。执行以下命令将您的公钥复制到 KEY 文件，然后将您的 KEY 追加到 KEYS 文件中。KEYS 文件包含用于对先前版本进行签名的所有公钥。

    ```shell
    gpg --output KEY --armor --export <youremail>
    cat KEY >> KEYS
    ```

5. **发布哈希值和签名：**

将生成的 .asc 和 .sha256 文件连同发布产物和 KEYS 文件一起上传到发布区域。

## 验证发布版本

1. **导入公钥：**

从 https://downloads.apache.org/gravitino/KEYS 下载 KEYS 文件。使用此命令导入用于为所有先前版本签名的公钥。如果您已经导入了密钥，也没关系。

    ```shell
    gpg --import KEYS
    ```

2. **验证签名：**

下载 .asc 和 release 文件。使用以下命令验证签名：

    ```shell
    gpg --verify <filename>.[zip|tar.gz].asc
    ```

输出应包含文本 "Good signature from ...".

例如，要验证 Gravitino 0.2.0 zip 文件，您可以使用以下命令：

    ```shell
     gpg --verify gravitino.0.2.0.zip.asc
    ```

3. **验证哈希值：**

检查哈希值是否匹配，使用以下命令：

    ```shell
    diff -u <filename>.[zip|tar.gz].sha256 <(shasum -a 256 <filename>.[zip|tar.gz])
    ```

例如，要验证 Gravitino 2.0 zip 文件，您可以使用以下命令：

    ```shell
    diff -u gravitino.0.2.0.zip.sha256 <(shasum -a 256 gravitino.0.2.0.zip)
    ```

此命令确保签名匹配，并且它们之间没有差异。
