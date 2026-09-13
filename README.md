<div align="center">

# 🌱 WorkBuddy Daily

**WorkBuddy 成长中心 · 全能签到脚本 · 单文件自包含**

🔐 Token 永续 · ✅ 18 项任务 · 🎮 8 项玩法 · 💰 三类查询 · 🎁 自动领奖 · 📢 内置推送 · 🐧 青龙友好 · ☁️ 支持 GitHub Actions

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20%E9%9D%92%E9%BE%99-4EAA25?style=for-the-badge&logo=linux&logoColor=white" />
<img src="https://img.shields.io/badge/Deploy-%E9%9D%92%E9%BE%99%20%7C%20GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
<img src="https://img.shields.io/badge/Deps-requests%20only-A78BFA?style=for-the-badge&logo=pypi&logoColor=white" />
<img src="https://img.shields.io/badge/Self--contained-1%20file-FFC75F?style=for-the-badge&logo=files&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

</div>

---

## ✨ 这是什么

一个脚本搞定 **WorkBuddy 成长中心** 的全部自动化：**Token 自动续期 → 积分/用量/成长查询 → 18 项成长任务 → 8 项互动玩法 → 自动领奖**，全流程无人值守，重复运行只补缺口、不重复领取。

> 🎯 一句话：**配一个刷新令牌，剩下交给它。**
>
> 📦 **单文件自包含**：无需任何配套模块（专家市场数据、推送通知全部内置），青龙上传一个 `workbuddy_daily.py` 即可运行。
>
> ☁️ **云端部署**：除了青龙，也支持直接跑在 **GitHub Actions** 上，零服务器、定时自动执行。

---

## 🚀 部署方式一：青龙面板（三步）

| 步骤 | 操作 |
| :---: | :--- |
| **1️⃣ 上传脚本** | 把 `workbuddy_daily.py` 放到脚本目录 |
| **2️⃣ 设置变量** | `WORKBUDDY_REFRESH_TOKEN` = 每行一个 `手机号:AT:RT`（多账号换行分隔） |
| **3️⃣ 定时任务** | 日常 `0 7,12 * * *` · 夜猫子窗口 `30 23 * * *` |

```bash
# 依赖（仅一个）
pip3 install requests
```

---

## ☁️ 部署方式二：GitHub Actions（零服务器 · 推荐）

> 本仓库已内置工作流 [`.github/workflows/workbuddy.yml`](.github/workflows/workbuddy.yml)，**Fork 或直接使用本仓库**即可开启云端定时签到。

### 第 1 步：添加 Secrets（仓库 → Settings → Secrets and variables → Actions）

| Secret 名称 | 必填 | 值 |
| :--- | :---: | :--- |
| `WORKBUDDY_REFRESH_TOKEN` | ✅ | 每行一个 `手机号:AT:RT`（多账号换行分隔） |
| `PUSHPLUS_TOKEN` | ⬜ | 可选，PushPlus 推送令牌 |

> 点 **New repository secret**，Name 填上面的名称，Secret 粘贴对应的值，保存。

### 第 2 步：开启 Actions
进入仓库 **Actions** 标签页，若提示需要启用，点 **I understand my workflows, go ahead and enable them**。

### 第 3 步：手动跑一次验证
Actions → 左侧选 **🌱 WorkBuddy Daily** → **Run workflow** → 选 `main` 分支 → 运行。看到 ✅ 即部署成功。

### 内置定时（北京时间）
| 时间 | UTC cron | 说明 |
| :---: | :---: | :--- |
| 07:00 | `0 23 * * *` | 日常全流程 |
| 12:00 | `0 4 * * *` | 日常全流程 |
| 23:30 | `30 15 * * *` | 夜猫子活动窗口 |

> 需要改时间，编辑 `workbuddy.yml` 里的 `cron`（**注意是 UTC，北京时间 − 8 小时**）。

### ⚠️ 令牌状态与安全（重要）
- 脚本每次续期都会**轮换刷新令牌**并写入 `wb_refresh_tokens.json`。
- 工作流内置安全判断：**仅在「私有仓库」中**把 `wb_refresh_tokens.json` 提交回仓库；**公开仓库会自动跳过**，避免 RT 泄露。
- **强烈建议**：如果你 Fork 本仓库用于部署，**请把 Fork 后的仓库设为 Private**（Settings → General → 拉到底 → Change visibility → Private），这样令牌才能安全持久化，续期不中断。
- 若使用公开仓库，令牌不会持久化，**每次运行都依赖 `WORKBUDDY_REFRESH_TOKEN` 这个 Secret 提供最新 RT**——需自行保证其不过期。

---

## 🔐 登录工具：短信验证码获取 Token

> 没有 AT/RT？用这个工具**一条命令**拿到。

```bash
python workbuddy_login.py                    # 交互式登录（推荐）
python workbuddy_login.py 13800000000        # 指定手机号
python workbuddy_login.py 13800000000 123456 # 指定手机号+验证码（跳过等待）
```

**流程**：输入手机号 → 自动发送短信验证码 → 输入收到的验证码 → 自动完成 Keycloak 授权流程 → 输出 `手机号:AT:RT`。

```
[1/5] 获取登录页面...
  ✅ 登录页获取成功 (会话: abc123...)
[2/5] 发送短信验证码到 138****0000 ...
  ✅ 验证码已发送 (有效期 300 秒)
  📱 请输入收到的验证码: ******
[3/5] 提交登录...
[4/5] 交换 Token...
  ✅ 登录成功! 身份: 138****0000 | AT过期: 2026-12-11 08:30
[5/5] 生成环境变量...
════════════════════════════════════════════════════════════
✅ 登录成功！将下面的值追加到 WORKBUDDY_REFRESH_TOKEN 变量
════════════════════════════════════════════════════════════
13800000000:eyJhbGciOiJSUzI1NiIs...很长...:eyJhbGciOiJIUzUxMiIs...也很长...
════════════════════════════════════════════════════════════
```

**输出**：结果同时保存到 `wb_login_result.json`（已被 `.gitignore` 屏蔽，不会提交）。

> 💡 拿到这行 `手机号:AT:RT` 后，直接粘贴到青龙的 `WORKBUDDY_REFRESH_TOKEN` 变量或 GitHub Secrets 即可，主脚本会自动续期、永不过期。

---
## 🔑 如何获取变量值（首次必看）

> 从桌面端认证文件中取 `AT` 和 `RT`，拼成 `手机号:AT:RT`。

1. **安装并登录** WorkBuddy 桌面端
2. 用记事本打开下面这个文件（`AppData` 是隐藏文件夹，地址栏直接粘贴路径）：
   ```
   C:/Users/你的用户名/AppData/Local/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info
   ```
3. 在文件里搜索 `accessToken` 和 `refreshToken`，各自后面跟一串 **`eyJ` 开头**的长字符串，那就是 **AT** 和 **RT**
4. 按格式拼一行，多账号写多行：
   ```
   1XXXXXXXXXX:eyJhbGciOiJSUzI1NiIs...很长...:eyJhbGciOiJIUzUxMiIs...也很长...
   ```

> ⚠️ AT 和 RT 之间用**英文冒号 `:`** 分隔；等号后面的引号不要带
> ⚠️ **RT 是你唯一的续期凭据，泄露了别人就能操作你的账号**

---

## ⌨️ 命令行参数

```bash
python workbuddy_daily.py                # 全流程：续期 → 查询 → 任务 → 领奖
python workbuddy_daily.py --refresh      # 仅刷新所有账号 Token
python workbuddy_daily.py --query        # 仅查询积分/用量/成长
python workbuddy_daily.py --no-desktop   # 跳过桌面任务（非 Windows 自动生效）
python workbuddy_daily.py --only 3       # 只跑第 3 个账号
```

---

## 🔧 环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `WORKBUDDY_REFRESH_TOKEN` | ✅ | 多账号刷新令牌，换行分隔，格式 `手机号:AT:RT`（AT 可留空）。首次运行自动生成 `wb_refresh_tokens.json` 并持续维护 |
| `PUSHPLUS_TOKEN` | ⬜ | 可选，内置 PushPlus 推送，运行结果推到微信 |

---

## 📦 任务清单

<details open>
<summary><b>☁️ 云端任务（14 项 · 纯 API）</b></summary>

每日签到 · 设计创意模式 · 探索优秀灵感 · 召唤 3 次专家团 · 发现应用 · 企鹅教师助手 · 和平精英主题 · 体验资料库 · 设置自动化任务 · 召唤 5 次专家 · 使用 5 个模板 · GLM-5.2 模型对话 · 和 AI 聊天 5 次 · 夜猫子活动

</details>

<details>
<summary><b>🖥️ 桌面任务（2 项 · 需 Windows 桌面端，每号一次即永久有效）</b></summary>

桌面端对话 1 次 · 尝鲜热门技能

> 💡 桌面任务需 Windows 桌面端环境（青龙 / GitHub Actions 均为 Linux，会自动跳过）。

</details>

<details>
<summary><b>🎮 互动玩法（8 项）</b></summary>

抽奖 · 盲盒 · Buddy 信息 · 派猫猫旅行 · 连签兑换 · 补签卡 · 礼包补偿 · 徽章

</details>

---

## ⚙️ 特别之处

- **📦 单文件自包含**：专家市场数据、PushPlus 推送全部内置，**无需任何外部模块**，部署零负担
- **☁️ 多云部署**：青龙面板 / GitHub Actions / 本地 Windows 均可运行
- **🏪 内置专家市场**：直接拉取专家团 / 普通专家 / 模板场景，网络异常时自动使用内置兜底数据
- **📊 全中文报告**：任务代码自动翻译为中文名称（如 `skill_1` → 尝鲜热门技能），每个账号独立分块 + 总计 + 待办分布，一目了然
- **🔄 续期节奏**：距上次刷新 > 10 天 或 AT 7 天内过期 → 自动刷新（离线会话 30 天失效）
- **♻️ RT 轮换**：每次刷新都会换发新令牌并立即保存，形成**永续循环**
- **🖥️ 桌面换血**：自动备份并切换桌面端认证文件，跑完还原，全程无需人工
- **🧩 幂等安全**：重复运行只补缺口，不重复领取
- **📁 数据文件**：`wb_refresh_tokens.json` 自动生成与维护
- **➕ 新增账号**：变量末尾追加一行 `手机号:AT:RT`，下次运行自动并入

---

## 📊 推送报告示例

```
📊 各账号运行报告

👤 账号1  账号1
   💰 主套餐剩余980积分(共1000,已用20)
   📊 共12类资源，本月已使用3456次
   🌱 等级3 | 连签7天 | 能量120
   ⏳ 未完成: 桌面端对话、尝鲜热门技能

👤 账号2  账号2
   💰 主套餐剩余500积分(共1000,已用500)
   📊 共12类资源，本月已使用1200次
   🌱 等级5 | 连签30天 | 能量300
   ✅ 全部完成！

📊 ══ 总计 ══
👥 共2个账号，任务完成 34/36 项

   · 桌面端对话（1个账号待完成）
   · 尝鲜热门技能（1个账号待完成）

🕐 2026-09-12 07:05
```

---

## 📁 目录结构

```
WorkBuddy-Daily/
├── .github/
│   └── workflows/
│       └── workbuddy.yml    # GitHub Actions 定时工作流
├── workbuddy_daily.py       # 主脚本（签到/任务/玩法，单文件自包含）
├── workbuddy_login.py       # 登录工具（短信验证码换 Token）
├── requirements.txt         # 依赖（仅 requests）
├── .gitignore               # 屏蔽凭据/运行数据
├── LICENSE                  # MIT 许可证
└── README.md
```

---

## 🔒 隐私说明

脚本**不含任何账号、手机号、Token 或设备信息**，所有凭据均由环境变量（或 GitHub Secrets）注入。请妥善保管你的 `wb_refresh_tokens.json`。

---

## ⚠️ 免责声明

本项目仅供 **学习与个人自动化** 使用。请遵守 WorkBuddy 服务条款，使用风险自负。

---

<div align="center">
  <sub>🌱 如果这个脚本帮到你，点个 <b>Star</b> 支持一下 ✨</sub>
</div>



