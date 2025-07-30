# nonebot-plugin-lazytea-shell-extension

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://img.shields.io/badge/nonebot-v2.4.2+-000000.svg" alt="nonebot"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
  <a href="https://github.com/hlfzsi/nonebot-plugin-lazytea-shell-extension"><img src="https://img.shields.io/github/stars/hlfzsi/nonebot_plugin_lazytea_shell_extension" alt="stars"></a>
</p>

**一个为 `nonebot-plugin-lazytea` 打造的强大“命令行工具”，让你在机器人运行时，通过指令动态、精细地管理几乎所有功能的权限。**

厌倦了每次修改权限都要翻看后台、修改文件甚至重启机器人？现在，你只需要一个 `/tea` 指令。

## ✨ 功能特性

* **⚡ 运行时管理**：无需重启，所有权限变更即刻生效。
* **⌨️ 命令行界面**：提供强大易用的 `/tea` 指令，让你在聊天窗口就能完成所有操作。
* **🛡️ 精细化权限控制**：为每一个机器人功能独立设置：
  * 全局开关（开启/关闭）
  * 用户/群组白名单
  * 用户/群组黑名单
* **🔗 无缝集成**：作为 `nonebot-plugin-lazytea` 的一部分，所有通过指令进行的修改都会**实时同步到 LazyTea 的 GUI**，反之亦然。
* **⚙️ 安全可控**：可通过配置文件指定谁可以使用 `/tea` 管理指令，防止权限滥用。
* **🔄 配置热重载**：支持通过 LazyTea 的机制热重载本插件的配置文件，无需重启。

## 📦 安装

通过 `nb-cli` 或 `pip` 安装本插件：

<details>
<summary>使用 nb-cli</summary>

```bash
nb plugin install nonebot-plugin-lazytea-shell-extension
```

</details>

<details>
<summary>使用 pip</summary>

```bash
pip install nonebot-plugin-lazytea-shell-extension
```

</details>

### 依赖项

本插件依赖以下插件，请确保它们也已正确安装并加载：

* `nonebot-plugin-alconna`
* `nonebot-plugin-lazytea`

## ⚙️ 配置

为了安全起见，您需要在使用前进行简单配置，以授权指定用户使用 `/tea` 管理指令。请在您的 `.env` 文件中添加以下配置项：

```dotenv

# 是否启用 /tea 指令权限管理功能。默认为 True
ENABLE_TEA_PERM=true

# 允许使用 /tea 指令的用户ID。
# 格式为 JSON 数组，可以填入多个用户ID。
# 示例：TEA_PERM_ALLOWANCE='["12345678", "87654321"]'
TEA_PERM_ALLOWANCE='["在此处填写你的QQ号"]'
```

| 配置项               | 类型          | 默认值 | 必填 | 说明                                   |
| :------------------- | :------------ | :----- | :--- | :------------------------------------- |
| `enable_tea_perm`    | `bool`        | `True` | 否   | 是否启用 `/tea` 指令功能。             |
| `tea_perm_allowance` | `Set[str]` | `[]`   | **是** | **允许使用 `/tea` 指令的用户 ID 列表。** |

**注意：** 只有在 `tea_perm_allowance` 列表中的用户才能使用本插件的所有指令。

## 📝 指令用法

您可以使用 `/tea` 指令来动态管理机器人各项功能的开关和权限。

### 核心概念：`<目标指令>`

在所有 `/tea` 命令中，`<目标指令>` 是一个至关重要的参数。它**不仅仅是指令的名称**，而是**任何能够触发机器人某个功能的完整文本**。

* **例如**：
  * 对于一个响应 `/天气 北京` 的指令，`<目标指令>` 就是 `/天气 北京`。
  * 对于一个响应关键词 `色图` 的功能，`<目标指令>` 就是 `色图`。
  * 对于一个会回复所有消息的 `on_message` 处理器，`<目标指令>` 可以是任意一句话，如 `你好`。

插件会模拟您发送 `<目标指令>` 的过程，来找出究竟是哪个功能响应了它。

### 📖 命令参考

| 抽象命令                               | 具体示例                           | 作用效果                                                       |
| :------------------------------------- | :--------------------------------- | :------------------------------------------------------------- |
| **查询状态**                           |                                    |                                                                |
| `/tea status <目标指令>`               | `/tea status /天气`                | 查询“/天气”指令的当前权限状态，包括总开关、黑白名单等。      |
| **功能开关**                           |                                    |                                                                |
| `/tea on <目标指令>`                   | `/tea on /签到`                    | 开启“/签到”指令，使其可以被正常触发。                        |
| `/tea off <目标指令>`                  | `/tea off /签到`                   | 关闭“/签到”指令，不在白名单的人都无法触发它。                  |
| **白名单管理 (Whitelist)**             |                                    |                                                                |
| `/tea wl add user <用户ID> <目标指令>` | `/tea wl add user 12345678 /天气`  | 将用户(12345678)加入“/天气”指令的白名单。                 |
| `/tea wl add group <群号> <目标指令>`  | `/tea wl add group 87654321 /天气` | 将群组(87654321)加入“/天气”指令的白名单。               |
| `/tea wl rm user <用户ID> <目标指令>`  | `/tea wl rm user 12345678 /天气`   | 从“/天气”指令的白名单中移除该用户。                          |
| `/tea wl rm group <群号> <目标指令>`   | `/tea wl rm group 87654321 /天气`  | 从“/天气”指令的白名单中移除该群组。                          |
| **黑名单管理 (Blacklist)**             |                                    |                                                                |
| `/tea bl add user <用户ID> <目标指令>` | `/tea bl add user 12345678 /抽卡`  | 将用户(QQ:12345678)加入“/抽卡”指令的黑名单，禁止他使用。     |
| `/tea bl add group <群号> <目标指令>`  | `/tea bl add group 87654321 /抽卡` | 将群组(QQ群:87654321)加入“/抽卡”指令的黑名单，禁止该群使用。 |
| `/tea bl rm user <用户ID> <目标指令>`  | `/tea bl rm user 12345678 抽卡`    | 从“抽卡”指令的黑名单中移除该用户。                           |
| `/tea bl rm group <群号> <目标指令>`   | `/tea bl rm group 87654321 /抽卡`  | 从“/抽卡”指令的黑名单中移除该群组。                          |

## 🔬 工作原理：指令匹配机制

为了准确定位到您想管理的指令，本插件模拟了 NoneBot 的事件响应流程。当您发送如 `/tea off /签到` 指令时，插件内部会：

1. 提取出 `<目标指令>`，即 `/签到`。
2. 模拟一个包含 `/签到` 的新消息事件。
3. 将这个模拟事件依次交给机器人中所有已注册的事件响应器进行匹配尝试。
4. 找到第一个成功匹配 `/签到` 的响应器，并将其作为本次操作的目标。

* **多重匹配**：如果一个 `<目标指令>` 同时匹配了多个同优先级的处理器，插件会选择**第一个成功匹配的**进行操作，并在日志中打印警告信息。
* **定位疑难**：如果您发现 `/tea` 指令管理的目标不是您预期的那个，很可能是因为根据上述优先级规则，有另一个更高优先级的处理器先响应了您的 `<目标指令>`。请尝试使用更精确的文本来定位, 或直接在 LazyTea 的 GUI 中进行管理。
