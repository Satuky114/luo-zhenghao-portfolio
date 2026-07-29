"""
民大自动打卡 v7
===============
WAF 绕过: --headless=new + Desktop Chrome UA + site-isolation 禁用
经过实际测试，iOS UA 被 WAF 拦截，桌面 Chrome UA 可以正常通过。
"""
import os, sys, time, traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PT

SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"

# Desktop Chrome UA - iOS UA gets blocked by WAF, desktop Chrome works
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)

USERNAME = os.environ.get("SWUN_USERNAME") or ""
PASSWORD = os.environ.get("SWUN_PASSWORD") or ""


def log(msg):
    safe = msg.encode("ascii", errors="replace").decode("ascii")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {safe}")


def cas_login(page):
    log("CAS login...")
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("button[type='submit'], input[type='submit']")
    page.wait_for_url("**/wxweb/**", timeout=30000)
    log("CAS login OK")


def wait_for_content(page, timeout=60):
    """Wait for page body to have actual content"""
    for i in range(timeout):
        try:
            text = page.locator("body").inner_text().strip()
            if text and len(text) > 30:
                log(f"Content after {i}s: {text[:120]}")
                return text
            if page.locator("#app, .van-nav-bar, .bg-box, .position-clock").count() > 0:
                text = page.locator("body").inner_text().strip()
                log(f"App rendered after {i}s: {text[:120]}")
                return text
        except:
            pass
        time.sleep(1)
    try:
        return page.locator("body").inner_text().strip()
    except:
        return ""


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    log("Launching Chromium (WAF bypass mode)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--headless=new",  # Use new headless mode
            ],
        )

        context = browser.new_context(
            geolocation={"latitude": SCHOOL_LAT, "longitude": SCHOOL_LNG},
            permissions=["geolocation"],
            viewport={"width": 1920, "height": 1080},
            user_agent=DESKTOP_UA,
            locale="zh-CN",
        )

        page = context.new_page()

        # GPS spoofing + anti-detection
        # navigator.webdriver is already False with our Chrome args
        # Faking navigator.plugins helps evade WAF
        page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

        try:
            # Step 1: Load home page
            log("Loading home page...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)

            # CAS
            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("ERROR: Need credentials")
                    return False
                cas_login(page)
                page.goto(WXWEB, wait_until="networkidle", timeout=60000)

            # Step 2: Wait for SPA
            log("Waiting for SPA render...")
            body = wait_for_content(page, timeout=50)
            log(f"Home body ({len(body)} chars): {body[:200]}")
            page.screenshot(path="daka_home.png", full_page=True)

            # Step 3: Navigate to clock via hash
            log("Going to clock page...")
            page.evaluate("window.location.hash = '#/PositioningClock'")
            time.sleep(3)
            body2 = wait_for_content(page, timeout=30)
            log(f"Clock body ({len(body2)} chars): {body2[:200]}")
            page.screenshot(path="daka_clock.png", full_page=True)

            if manual_mode:
                log("Manual mode - press Enter when done...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # Step 4: Find & click button
            btns = page.locator("button").all()
            log(f"Buttons found: {len(btns)}")
            for i, b in enumerate(btns[:10]):
                try:
                    log(f"  [{i}] '{b.inner_text()}'")
                except:
                    pass

            for label in ["打卡", "签到", "提交"]:
                btn = page.locator(f"button:has-text('{label}')")
                if btn.count() > 0:
                    log(f"Clicking '{label}'!")
                    btn.first.click()
                    time.sleep(5)
                    r = page.locator("body").inner_text()
                    log(f"Result: {r[:250]}")
                    page.screenshot(path="daka_done.png")
                    return True

            if "已打卡" in body2:
                log("Already checked in today")
            else:
                log("No button (outside time window?)")
            return True

        except PT as e:
            log(f"Timeout: {e}")
            page.screenshot(path="daka_error.png")
            return False
        except Exception as e:
            log(f"Error: {traceback.format_exc()}")
            page.screenshot(path="daka_error.png")
            return False
        finally:
            context.close()
            browser.close()
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
