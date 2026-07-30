# 民大自动打卡系统 🕐

基于 Playwright 浏览器自动化 + GitHub Actions 的西南民族大学每日自动打卡系统。

## 功能特性

- ✅ **全自动打卡**：每晚 21:30 自动签到，无需手动操作
- ✅ **WAF 绕过**：伪装真实浏览器环境，绕过校园云防护
- ✅ **CAS 认证**：自动完成统一身份认证登录（AES-CBC 密码加密）
- ✅ **GPS 模拟**：定位至航空港校区（避免跨校区打卡失败）
- ✅ **时间窗口保护**：多重时间校验，确保只在 21:30-23:25 内打卡
- ✅ **远程开关**：通过 GitHub Issue 评论控制脚本启停

## 技术架构

```
GitHub Actions (cron 19:30 BJT)
  │
  ▼
Playwright (Chromium headless)
  │
  ├─ WAF Bypass ──► gyglxt.swun.edu.cn/wxweb/
  │
  ├─ CAS OAuth2.0 ──► authserver.swun.edu.cn
  │     └─ AES-CBC 密码加密 (encryptPassword)
  │
  ├─ SPA Navigation ──► #/PositioningClock
  │
  └─ GPS Spoof ──► 航空港校区 (30.562897, 103.966624)
        │
        └─ 点击打卡按钮
```

## 部署指南

### 第一步：Fork 仓库

点击右上角 **Fork** → 复制到你的 GitHub 账号下。

### 第二步：配置 Secrets

1. 进入你的 Fork 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，添加以下两个密钥：

| Name | Value |
|------|-------|
| `SWUN_USERNAME` | 你的学号（如 `202430502025`） |
| `SWUN_PASSWORD` | 你的一网通办密码 |

> ⚠️ 密码只存储在你自己仓库的 Secrets 中，非常安全。GitHub 不会在任何地方明文展示。

### 第三步：启用 Actions

1. 进入 **Actions** 标签页
2. 如果提示 "Workflows aren't being run…"，点击 **I understand my workflows, go ahead and enable them**
3. 找到 **民大每日打卡** workflow，确认已启用

### 第四步：验证部署

1. 进入 **Actions** → **民大每日打卡** → **Run workflow**
2. 选择 `master`/`main` 分支，点击 **Run workflow**
3. 等待约 2-3 分钟，运行完成后下载 `daka-screenshots` artifact 查看截图

> 手动触发会以 `--force` 模式运行，仅用于测试流程是否畅通。真正的打卡需要在晚上的时间窗口内完成。

### 第五步：静待自动打卡

每天 **21:35 BJT**（GitHub Actions 自动触发），脚本会：
1. 检查是否在打卡时间窗口内
2. 自动登录、认证、导航到打卡页面
3. 点击打卡按钮
4. 上传截图作为运行结果

## 远程开关

在你的 Fork 仓库中，打开 Issue #1（**打卡开关**），评论：

- `on` 或 `开启` → 启用自动打卡
- `off` 或 `关闭` → 暂停自动打卡

---

## 技术详解（作品集）

### 关键挑战

| 挑战 | 解决方案 |
|------|----------|
| **校园 WAF 防火墙（阿里云盾）** | 新版 headless Chromium + Desktop UA + 1920×1080 视口 + `disable-site-isolation-trials` + `navigator.plugins` 伪造 |
| **CAS 统一身份认证** | 解析页面内 AES-CBC `encryptPassword()` 函数，先获取 salt，再生成加密密码填入表单 |
| **Vue.js SPA Hash 路由** | 识别 `#/login` / `#/hoyOauth` / `#/PositioningClock` 三段路由，处理 OAuth token 回调 |
| **服务端时间窗口限制** | `queryPersonDetailInfoByPersonsn` API 在非窗口时段返回 `code:500`，改为轮询 + 多重时间校验 |
| **GitHub Actions 延迟** | cron 提前到 19:30 BJT，脚本内每 2 分钟轮询等待至窗口开启 |

### 技术栈

- **Playwright** (Python) — 浏览器自动化核心
- **GitHub Actions** — CI/CD 定时调度 + artifact 存档
- **CAS OAuth2.0** — 统一身份认证协议
- **AES-CBC** — 前端密码加密逆向
- **GitHub Issues API** — 远程开关机制

### 版本历程

历经 **14 个版本**迭代：
- v1-v4：基础脚本、表单填写、验证码处理
- v5-v8：WAF 检测绕过、headless 模式优化
- v9-v11：多因素登录流程完善、SPA 导航适配
- v12：发现服务端时间窗口限制
- v13：时间窗口检查 + 手动模式 + CI 适配
- v14：轮询等待 + 多重时间校验（应对 Actions 延迟）

---

## FAQ

**Q: 密码安全吗？**
A: 密码存储在你自己仓库的 GitHub Actions Secrets 中，完全加密，不会在任何日志中明文显示。

**Q: 学校会发现吗？**
A: 脚本模拟真实 Chrome 浏览器 + GPS 定位，与手动打卡的请求完全一致。你自己使用没问题，但不要声张或教唆其他同学违规使用。

**Q: 密码改了怎么办？**
A: 更新你仓库中的 `SWUN_PASSWORD` Secret，下次运行自动生效。

**Q: 能不开 GitHub Actions 吗？**
A: 可以在本地运行 `python daka.py --show`，会弹出浏览器窗口手动观察打卡过程。

**Q: 为什么手动触发可以跑通但定时触发打不上？**
A: 打卡需要服务端在时间窗口（21:30-23:25）内，非窗口时段 API 返回 500。定时触发的脚本会轮询等待窗口开启。
