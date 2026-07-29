"""
民大自动打卡脚本 v4
====================

技术策略：
  1. 先访问 wxweb/ 首页获取 WAF Cookie 和 JS 签名
  2. 等 WAF JS 执行完 + Vue 应用加载
  3. 用 page.evaluate 导航到打卡页面（SPA 内部路由）
  4. 找到按钮点击打卡
"""
import os, sys, time, traceback
from playwright.sync_api import sync_playwright, TimeoutError as PT

SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"
CLOCK_HASH = "#/PositioningClock"

IOS_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "lantuMobilecampus lantuMC"
)

USERNAME = os.environ.get("SWUN_USERNAME") or ""
PASSWORD = os.environ.get("SWUN_PASSWORD") or ""


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def cas_login(page):
    log("🔐 CAS 登录...")
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("button[type='submit'], input[type='submit']")
    page.wait_for_url("**/wxweb/**", timeout=30000)
    log("✅ CAS 登录完成")


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    log("🚀 启动 Chromium...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=headless,
            geolocation={"latitude": SCHOOL_LAT, "longitude": SCHOOL_LNG},
            permissions=["geolocation"],
            viewport={"width": 375, "height": 812},
            user_agent=IOS_UA,
            locale="zh-CN",
        )
        page = context.new_page()

        # 反检测
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'platform', {get: () => 'iPhone'});
        """)

        try:
            # ====== Step 1: 先访问首页，让 WAF 放行 ======
            log("📍 Step 1: 访问首页获取 Cookie...")
            page.goto(WXWEB, wait_until="domcontentloaded", timeout=30000)

            # 等 WAF JS 执行 + 设置 Cookie
            page.wait_for_timeout(8000)

            log(f"首页 URL: {page.url[:100]}")
            log(f"HTML 长度: {len(page.content())}")

            # 如果跳去了 CAS
            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("❌ 需要登录凭据")
                    return False
                cas_login(page)
                # 再给我们一次加载机会
                page.wait_for_timeout(8000)

            # ====== Step 2: 截图首页诊断 ======
            page.screenshot(path="daka_home.png", full_page=True)
            log("📸 daka_home.png")

            # ====== Step 3: SPA 内部导航到打卡页 ======
            log("📍 Step 3: 导航到打卡页面...")

            # 用 JS 触发 Vue Router 导航
            page.evaluate(f"""
                // 方式1: 修改 hash
                window.location.hash = '{CLOCK_HASH}';
                // 方式2: 如果页面使用了 Vue Router，尝试直接推入路由
                try {{
                    const app = document.querySelector('#app').__vue_app__;
                    if (app) {{
                        const router = app.config.globalProperties.$router;
                        if (router) router.push('{CLOCK_HASH}');
                    }}
                }} catch(e) {{}}
            """)

            # 等新页面渲染
            page.wait_for_timeout(8000)

            log(f"打卡页 URL: {page.url[:100]}")
            page.screenshot(path="daka_clock_page.png", full_page=True)
            log("📸 daka_clock_page.png")

            body_text = page.locator("body").inner_text().strip()
            log(f"Body ({len(body_text)} 字符): {body_text[:300]}")

            # ====== Step 4: 等待地图组件 ======
            log("📍 Step 4: 等待页面组件...")
            try:
                page.wait_for_selector(".position-clock, .location, .bg-box, [class*='clock']", timeout=15000)
                log("✅ 组件已加载")
                page.wait_for_timeout(3000)
                body_text = page.locator("body").inner_text().strip()
                log(f"Body ({len(body_text)} 字符): {body_text[:300]}")
            except PT:
                log("⚠️ 组件未在预期时间加载")

            page.screenshot(path="daka_ready.png", full_page=True)

            # ====== 手动模式 ======
            if manual_mode:
                log("👆 手动模式：操作浏览器后按 Enter...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # ====== Step 5: 检查状态并打卡 ======
            if not body_text:
                log("⚠️ Body 仍为空——WAF 确实拦截了")
                log("   需要真实手机 Cookie 来跨过 WAF")
                log("   建议今晚 21:30 用手机登录后导出 Cookie")
                return True  # 不报错

            if "已打卡" in body_text or "无需" in body_text:
                log("✅ 已打卡或不在时段")
                return True

            # 查找按钮
            buttons = page.locator("button").all()
            log(f"找到 {len(buttons)} 个按钮:")
            for i, btn in enumerate(buttons[:10]):
                try:
                    log(f"  [{i}] '{btn.inner_text()}' class={btn.get_attribute('class')}")
                except:
                    pass

            # 尝试点击
            for text in ["打卡", "签到", "提交"]:
                btn = page.locator(f"button:has-text('{text}')")
                if btn.count() > 0:
                    log(f"🎯 找到 '按钮'——点击！")
                    btn.first.click()
                    page.wait_for_timeout(5000)
                    body = page.locator("body").inner_text()
                    if "成功" in body:
                        log("🎉 打卡成功！")
                    else:
                        log(f"反馈: {body[:200]}")
                    page.screenshot(path="daka_done.png")
                    return True

            log("ℹ️ 未找到打卡按钮（可能不在时段或已打卡）")
            return True

        except PT as e:
            log(f"❌ Timeout: {e}")
            page.screenshot(path="daka_error.png")
            return False
        except Exception as e:
            log(f"❌ {traceback.format_exc()}")
            page.screenshot(path="daka_error.png")
            return False
        finally:
            context.close()
            log("👋 Done")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--manual", action="store_true")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()
    ok = do_checkin(headless=(not args.show and not args.manual), manual_mode=args.manual)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
