"""
民大自动打卡 v5
===============
核心修复:
  1. 超长等待 SPA 渲染（WAF JS 需要时间）
  2. 增强反检测
  3. 逐秒检查页面状态直到内容出现
"""
import os, sys, time, traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PT

SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"

IOS_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "lantuMobilecampus lantuMC"
)

USERNAME = os.environ.get("SWUN_USERNAME") or ""
PASSWORD = os.environ.get("SWUN_PASSWORD") or ""


def log(msg):
    safe = msg.encode("ascii", errors="replace").decode("ascii")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {safe}")


def cas_login(page):
    log("CAS redirect detected, logging in...")
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("button[type='submit'], input[type='submit']")
    page.wait_for_url("**/wxweb/**", timeout=30000)
    log("CAS login OK")


def wait_for_spa(page, max_wait=60):
    """Wait for Vue SPA to render — polls until body has content"""
    log(f"Waiting for SPA (max {max_wait}s)...")
    for i in range(max_wait):
        try:
            text = page.locator("body").inner_text().strip()
            if text and len(text) > 50:
                log(f"SPA ready after {i+1}s: '{text[:100]}...'")
                return True
            # Also check for specific elements
            has_app = page.locator("#app").count() > 0
            has_vue = page.locator("[class*='van-'], [class*='position-'], .bg-box").count() > 0
            if has_vue:
                log(f"Vue components visible after {i+1}s")
                return True
        except:
            pass
        time.sleep(1)

    # Last attempt
    try:
        text = page.locator("body").inner_text().strip()
        log(f"Final body: '{text[:200]}'")
    except:
        log("Could not read body")
    return False


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    log("Launching Chromium...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=headless,
            geolocation={"latitude": SCHOOL_LAT, "longitude": SCHOOL_LNG},
            permissions=["geolocation"],
            viewport={"width": 375, "height": 812},
            user_agent=IOS_UA,
            locale="zh-CN",
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )
        page = context.new_page()

        # Anti-detection: hide webdriver flag BEFORE any page load
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']});
            window.chrome = { runtime: {} };
        """)

        try:
            # Step 1: Visit home page
            log("Step 1: Loading home page...")
            page.goto(WXWEB, wait_until="domcontentloaded", timeout=30000)

            # Check for CAS redirect immediately
            page.wait_for_timeout(3000)
            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("ERROR: Need SWUN_USERNAME / SWUN_PASSWORD")
                    return False
                cas_login(page)
                page.goto(WXWEB, wait_until="domcontentloaded", timeout=30000)

            # Step 2: WAIT for SPA to fully render
            log("Step 2: Waiting for Vue app to load...")
            ready = wait_for_spa(page, max_wait=45)

            if not ready:
                log("SPA did not render in time, taking screenshot...")
                page.screenshot(path="daka_stuck.png", full_page=True)

            # Step 3: Navigate to clock page via hash
            log("Step 3: Going to clock page...")
            page.evaluate("window.location.hash = '#/PositioningClock'")
            ready2 = wait_for_spa(page, max_wait=30)

            page.screenshot(path="daka_clock.png", full_page=True)
            log("Screenshot: daka_clock.png")

            if manual_mode:
                log("Manual mode - operate then press Enter...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # Step 4: Try to click
            body = page.locator("body").inner_text()
            log(f"Body: {body[:300]}")

            buttons = page.locator("button").all()
            log(f"Found {len(buttons)} buttons")
            for btn in buttons[:10]:
                try:
                    log(f"  btn: '{btn.inner_text()}'")
                except:
                    pass

            for label in ["打卡", "签到", "提交"]:
                btn = page.locator(f"button:has-text('{label}')")
                if btn.count() > 0:
                    log(f"Clicking '{label}' button!")
                    btn.first.click()
                    page.wait_for_timeout(5000)
                    result = page.locator("body").inner_text()
                    if "成功" in result:
                        log("SUCCESS!")
                    else:
                        log(f"Result: {result[:200]}")
                    page.screenshot(path="daka_done.png")
                    return True

            log("No clickable button found (time window issue or already done)")
            return True

        except PT as e:
            log(f"Timeout: {e}")
            try: page.screenshot(path="daka_error.png")
            except: pass
            return False
        except Exception as e:
            log(f"Error: {traceback.format_exc()}")
            try: page.screenshot(path="daka_error.png")
            except: pass
            return False
        finally:
            context.close()
            log("Done")


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
