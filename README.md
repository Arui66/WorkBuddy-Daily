<div align="center">

# 🌱 WorkBuddy Daily

**WorkBuddy 成长中心 · 全能签到脚本 · 单文件自包含**

🔐 Token 永续 · ✅ 18 项任务 · 🎮 8 项玩法 · 💰 三类查询 · 🎁 自动领奖 · 📢 内置推送 · 🐧 青龙友好

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20%E9%9D%92%E9%BE%99-4EAA25?style=for-the-badge&logo=linux&logoColor=white" />
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

---

## 🚀 快速开始（青龙面板三步）

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

</details>

<details>
<summary><b>🎮 互动玩法（8 项）</b></summary>

抽奖 · 盲盒 · Buddy 信息 · 派猫猫旅行 · 连签兑换 · 补签卡 · 礼包补偿 · 徽章

</details>

---

## ⚙️ 特别之处

- **📦 单文件自包含**：专家市场数据、PushPlus 推送全部内置，**无需任何外部模块**，部署零负担
- **🏪 内置专家市场**：直接拉取专家团 / 普通专家 / 模板场景，网络异常时自动使用内置兜底数据
- **📊 结构化报告**：每账号一行摘要 + 总计 + 待办分布，推送一目了然不截断
- **🔄 续期节奏**：距上次刷新 > 10 天 或 AT 7 天内过期 → 自动刷新（离线会话 30 天失效）
- **♻️ RT 轮换**：每次刷新都会换发新令牌并立即保存，形成**永续循环**
- **🖥️ 桌面换血**：自动备份并切换桌面端认证文件，跑完还原，全程无需人工
- **🧩 幂等安全**：重复运行只补缺口，不重复领取
- **📁 数据文件**：`wb_refresh_tokens.json` 自动生成与维护
- **➕ 新增账号**：变量末尾追加一行 `手机号:AT:RT`，下次运行自动并入

---

## 📊 推送报告示例

```
🌱 WorkBuddy 签到报告

📋 账号概览 (2个)

👤 账号1  等级3  完成16/18｜待办:2项
👤 账号2  等级5  完成18/18｜✅全清

🏆 总计: 34/36 项已完成

📌 待办分布:
  · RichMeow_Chat ×1
  · skill_1 ×1

🕐 2026-09-12 07:05
```

---

## 📁 目录结构

```
WorkBuddy-Daily/
├── workbuddy_daily.py      # 主脚本（单文件自包含）
├── requirements.txt        # 依赖（仅 requests）
├── .gitignore              # 屏蔽凭据/运行数据
├── LICENSE                 # MIT 许可证
└── README.md
```

---

## 🔒 隐私说明

脚本**不含任何账号、手机号、Token 或设备信息**，所有凭据均由环境变量注入。请妥善保管你的 `wb_refresh_tokens.json`。

---

## ⚠️ 免责声明

本项目仅供 **学习与个人自动化** 使用。请遵守 WorkBuddy 服务条款，使用风险自负。

---

<div align="center">
  <sub>🌱 如果这个脚本帮到你，点个 <b>Star</b> 支持一下 ✨</sub>
</div>
