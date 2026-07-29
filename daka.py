"""
民大自动打卡脚本 v2
====================
支持：本地运行 / GitHub Actions
控制：在 GitHub → Actions → 民大每日打卡 → 右侧 "..." → Disable workflow 随时停止

本地用法：
  pip install playwright && playwright install chromium
  python daka.py          # 自动打卡
  python daka.py -m       # 手动模式（打开浏览器自己操作）

GitHub 部署：
  1. 推送仓库
  2. Settings → Secrets → 添加:
     SWUN_USERNAME: 你的学号
     SWUN_PASSWORD: 统一认证密码
  3. Actions → 民大每日打卡 → Run workflow 测试
  4. 每天 21:35 自动运行（要停就去 Actions → Disable）

技术细节：
  - Playwright geolocation 伪造 GPS = 学校坐标
  - 页面 JS 自动处理 AES 加密 + l2t2q0Jo WAF 签名
  - 无需 Cookie 管理，每次自动登录
"""
import os
import sys
import time
import traceback
from playwright.sync_api import sync_playwright, TimeoutError as PT

# ===== 学校配置 =====
SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624

# ===== URL =====
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"
CLOCK_PAGE = f"{WXWEB}#/PositioningClock"

# ===== 凭据（环境变量 > 代码内写死 > 交互输入）=====
USERNAME = os.environ.get("SWUN_USERNAME") or ""
PASSWORD = os.environ.get("SWUN_PASSWORD") or ""


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def cas_login(page):
    """CAS 统一认证登录"""
    # CAS 登录页
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=15000)
    log(f"在 CAS 登录页: {page.url[:60]}...")

    # 等待并填写表单
    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)

    # 截图看有没有验证码
    page.screenshot(path="cas_login.png")
    log("📸 已截图 cas_login.png")

    # 点击登录按钮
    page.click("button[type='submit'], input[value='登录'], .login-btn")

    # 等待跳回 wxweb
    page.wait_for_url("**/wxweb/**", timeout=30000)
    log("✅ CAS 登录成功，已跳回应用")


def do_checkin(headless=True, manual_mode=False):
    """执行打卡"""
    log("🚀 启动浏览器...")

    with sync_playwright() as p:
        # 启动带持久化的浏览器（本地运行保存 Cookie，下次更快）
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=headless,
            geolocation={"latitude": SCHOOL_LAT, "longitude": SCHOOL_LNG},
            permissions=["geolocation"],
            viewport={"width": 375, "height": 812},
            user_agent=(
                "Mozilla/5.0 (Linux; Android 10; Pixel 3) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
                "Mobile Safari/537.36"
            ),
            locale="zh-CN",
        )
        page = context.new_page()

        try:
            # ====== 第一步：访问打卡页面 ======
            log("📍 打开打卡页面...")
            page.goto(CLOCK_PAGE, wait_until="domcontentloaded", timeout=30000)

            # 检查是否被重定向到 CAS
            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("❌ 需要登录但未设置 SWUN_USERNAME / SWUN_PASSWORD")
                    log("💡 本地运行: python daka.py -m  (手动模式)")
                    log("💡 GitHub: Settings → Secrets 添加凭据")
                    return False
                cas_login(page)
                # 重新访问打卡页
                page.goto(CLOCK_PAGE, wait_until="domcontentloaded", timeout=30000)

            # 等待 Vue 应用加载
            log("⏳ 等待页面渲染...")
            page.wait_for_timeout(3000)

            # 等待地图组件初始化
            try:
                page.wait_for_selector(".position-clock, .location, .amap-demo", timeout=15000)
                log("✅ 页面加载完成")
            except PT:
                log("⚠️ 页面可能加载缓慢，继续尝试...")

            page.screenshot(path="daka_before.png")
            log("📸 截图 daka_before.png")

            # ====== 手动模式：交给用户操作 ======
            if manual_mode:
                log("👆 手动模式：请在浏览器中点击打卡，完成后按 Enter...")
                input()
                page.screenshot(path="daka_manual_result.png")
                log("📸 截图 daka_manual_result.png")
                return True

            # ====== 第二步：检查打卡状态 ======
            # 用 JS 读取 Vue 组件状态
            clock_state = page.evaluate("""() => {
                const root = document.querySelector('#app');
                const text = document.body.innerText;
                return {
                    bodyText: text.substring(0, 500),
                    url: location.href
                };
            }""")

            log(f"页面内容片段: {clock_state['bodyText'][:200]}")

            if "已打卡" in clock_state['bodyText'] or "打卡成功" in clock_state['bodyText']:
                log("✅ 今日可能已打卡，无需重复操作")
                return True

            # ====== 第三步：点击打卡按钮 ======
            # 打卡按钮在 Vue 组件中，文本为"打卡"
            log("🖱️ 正在查找打卡按钮...")

            # Van UI 按钮
            btn = page.locator("button").filter(has_text="打卡")

            if btn.count() == 0:
                # 尝试其他选择器
                btn = page.locator(".van-button:has-text('打卡'), [class*='submit']:has-text('打卡'), .punch-btn")

            if btn.count() > 0:
                log(f"找到 {btn.count()} 个按钮")
                btn.first.click()
                log("✅ 已点击打卡按钮")

                # 等待结果
                page.wait_for_timeout(4000)

                # ====== 第四步：检验结果 ======
                toast = page.locator(".van-toast, .van-notify, [class*='toast'], [class*='success']")
                body = page.locator("body").inner_text()

                if "成功" in body or "success" in body.lower() or toast.count() > 0:
                    log("🎉 打卡成功！")
                    page.screenshot(path="daka_success.png")
                    return True
                else:
                    log(f"⚠️ 反馈不明: {body[:300]}")
                    page.screenshot(path="daka_result.png")
                    return True  # 可能已经成功了，不报错
            else:
                log("⚠️ 未找到打卡按钮，可能:")
                log("   1. 不在打卡时段 (21:30-23:25)")
                log("   2. 今日已打卡")
                log("   3. 页面结构发生变化")
                page.screenshot(path="daka_no_button.png")
                return True  # 不报错，可能是时段外

        except PT as e:
            log(f"❌ 超时: {e}")
            try:
                page.screenshot(path="daka_timeout.png")
            except:
                pass
            return False

        except Exception as e:
            log(f"❌ 错误: {traceback.format_exc()}")
            try:
                page.screenshot(path="daka_error.png")
            except:
                pass
            return False

        finally:
            context.close()
            log("👋 浏览器已关闭")


def main():
    import argparse
    p = argparse.ArgumentParser(description="民大自动打卡")
    p.add_argument("-m", "--manual", action="store_true", help="手动模式：打开浏览器自己点")
    p.add_argument("--show", action="store_true", help="显示浏览器界面（非无头）")
    p.add_argument("-u", "--username", help="学号")
    p.add_argument("--password", help="密码")
    args = p.parse_args()

    global USERNAME, PASSWORD
    if args.username:
        USERNAME = args.username
    if args.password:
        PASSWORD = args.password

    # 手动模式必须显示浏览器
    headless = not (args.show or args.manual)

    ok = do_checkin(headless=headless, manual_mode=args.manual)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
