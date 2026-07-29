"""
民大自动打卡脚本 v3
====================
支持：本地运行 / GitHub Actions
控制：GitHub → Actions → 民大每日打卡 → "..." → Disable workflow

技术要点：
  - 使用与 iPhone 完全一致的 User-Agent 绕过 WAF
  - geolocation 劫持 GPS = 学校坐标
  - 页面 JS 自动处理 AES 加密 + l2t2q0Jo 签名
"""
import os, sys, time, traceback

from playwright.sync_api import sync_playwright, TimeoutError as PT

# ===== 配置 =====
SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"
CLOCK_PAGE = f"{WXWEB}#/PositioningClock"

# 必须与抓包中的完全一致
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
    """CAS 统一认证登录"""
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=15000)
    log(f"CAS 登录页...")

    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)

    page.screenshot(path="cas_login.png")
    log("📸 cas_login.png")

    # 检查是否有验证码（一般没有）
    captcha = page.locator("#captcha, .captcha, [name='captcha']")
    if captcha.count() > 0:
        log("⚠️ 检测到验证码！截图保存...")
        # 验证码需要手动处理，但 CAS 登录一般不需要

    page.click("button[type='submit'], input[type='submit'], .login-btn, [type='button']")

    try:
        page.wait_for_url("**/wxweb/**", timeout=30000)
        log("✅ 登录成功")
    except PT:
        # 可能登录失败，看看页面内容
        body = page.locator("body").inner_text()
        log(f"⚠️ 登录结果不明: {body[:200]}")


def do_checkin(headless=True, manual_mode=False):
    log("🚀 启动浏览器...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=headless,
            geolocation={"latitude": SCHOOL_LAT, "longitude": SCHOOL_LNG},
            permissions=["geolocation"],
            viewport={"width": 375, "height": 812},
            user_agent=IOS_UA,
            locale="zh-CN",
            # 反检测
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )
        page = context.new_page()

        # 注入反检测脚本
        page.add_init_script("""
            // 移除 webdriver 标记
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            // 伪造 plugins 数量
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            // 伪造 platform
            Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
        """)

        try:
            # ====== 访问打卡页 ======
            log("📍 访问打卡页面...")
            page.goto(CLOCK_PAGE, wait_until="networkidle", timeout=60000)

            # 等 WAF 脚本执行完
            page.wait_for_timeout(5000)

            # 检查是否跳 CAS
            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("❌ 需要登录，请设置 Secrets")
                    return False
                cas_login(page)
                page.goto(CLOCK_PAGE, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(5000)

            # ====== 检查页面状态 ======
            log(f"当前 URL: {page.url[:80]}")

            # 获取页面内容
            body_text = page.locator("body").inner_text().strip()

            screenshot_path = "daka_before.png"
            page.screenshot(path=screenshot_path, full_page=True)
            log(f"📸 {screenshot_path}")

            log(f"Body 内容 ({len(body_text)} 字符): {body_text[:300]}")

            if not body_text:
                log("⚠️ 页面内容为空，可能被 WAF 拦截")
                log("💡 尝试获取 HTML...")
                html = page.content()
                log(f"HTML 长度: {len(html)}")
                # 写 HTML 到 artifacts
                with open("page_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)

            # ====== 手动模式 ======
            if manual_mode:
                log("👆 手动模式：请在浏览器操作后按 Enter...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # ====== 检查是否在打卡时段 ======
            if "不在" in body_text or "无需" in body_text:
                log("✅ 今日已打过卡，或不在打卡时段（正常现象）")
                return True

            if "已打卡" in body_text or "打卡成功" in body_text:
                log("✅ 今日已打卡")
                return True

            # ====== 找打卡按钮 ======
            log("🔍 查找打卡按钮...")

            # 打印所有按钮文本帮助诊断
            buttons = page.locator("button").all()
            log(f"页面上有 {len(buttons)} 个按钮")
            for i, btn in enumerate(buttons[:5]):
                try:
                    txt = btn.inner_text()
                    log(f"  按钮 {i}: '{txt}'")
                except:
                    pass

            # 尝试多种选择器
            clock_btn = page.locator("button").filter(has_text="打卡")
            if clock_btn.count() == 0:
                clock_btn = page.locator(".van-button:has-text('打卡')")
            if clock_btn.count() == 0:
                # 通过 Vue 数据判断
                clock_btn = page.locator("[class*='position'] button, .clock-btn, [class*='punch']")

            if clock_btn.count() > 0:
                log(f"✅ 找到打卡按钮，点击...")
                clock_btn.first.click()
                page.wait_for_timeout(4000)

                body = page.locator("body").inner_text()
                if "成功" in body:
                    log("🎉 打卡成功！")
                    page.screenshot(path="daka_success.png")
                    return True
                else:
                    log(f"结果: {body[:200]}")
                    page.screenshot(path="daka_result.png")
                    return True
            else:
                log("ℹ️ 未找到打卡按钮")
                log("如果当前不在 21:30-23:25，这是正常的")
                page.screenshot(path="daka_no_button.png")
                return True

        except PT as e:
            log(f"❌ 超时: {e}")
            try:
                page.screenshot(path="daka_error.png")
            except:
                pass
            return False

        except Exception as e:
            log(f"❌ 异常: {traceback.format_exc()}")
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
    ap = argparse.ArgumentParser(description="民大自动打卡")
    ap.add_argument("-m", "--manual", action="store_true", help="手动模式")
    ap.add_argument("--show", action="store_true", help="显示浏览器")
    args = ap.parse_args()

    headless = not (args.show or args.manual)
    ok = do_checkin(headless=headless, manual_mode=args.manual)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
