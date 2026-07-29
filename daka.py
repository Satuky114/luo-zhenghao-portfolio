"""
民大自动打卡脚本 v4
====================

策略：
  1. 访问 wxweb/ 等待 Vue 加载
  2. SPA 内部导航到打卡页
  3. 点按钮打卡
"""
import os, sys, time, traceback
from datetime import datetime
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
    stamp = datetime.now().strftime("%H:%M:%S")
    safe = msg.encode("ascii", errors="replace").decode("ascii")
    print(f"[{stamp}] {safe}")


def cas_login(page):
    log("CAS login page detected, logging in...")
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("button[type='submit'], input[type='submit']")
    page.wait_for_url("**/wxweb/**", timeout=30000)
    log("CAS login OK")


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
        )
        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
        """)

        try:
            # Step 1: Visit home page, get WAF cookies
            log("Step 1: Visiting home page...")
            page.goto(WXWEB, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            log(f"URL: {page.url[:120]}")

            # Handle CAS redirect
            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("ERROR: Login required but no credentials set")
                    log("  Set SWUN_USERNAME and SWUN_PASSWORD env vars")
                    return False
                cas_login(page)
                page.wait_for_timeout(5000)

            # Step 2: Try navigating to clock page
            log("Step 2: Navigating to clock page...")
            page.goto(WXWEB + CLOCK_HASH, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(8000)

            page.screenshot(path="daka_page.png", full_page=True)
            log("Screenshot: daka_page.png")

            page_text = page.locator("body").inner_text().strip()[:500]
            log(f"Page text ({len(page_text)} chars): {page_text[:200]}")

            if manual_mode:
                log("Manual mode - operate browser then press Enter...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # Step 3: Look for the clock button
            btn = page.locator("button").filter(has_text="打卡")
            if btn.count() == 0:
                btn = page.locator("button").filter(has_text="签到")

            if btn.count() > 0:
                log(f"Found {btn.count()} button(s), clicking...")
                btn.first.click()
                page.wait_for_timeout(5000)

                result = page.locator("body").inner_text()
                if "成功" in result:
                    log("SUCCESS: check-in complete!")
                else:
                    log(f"Result (first 200 chars): {result[:200]}")
                page.screenshot(path="daka_done.png")
                return True

            # Step 4: Check if already done
            if "已打卡" in page_text or "打卡成功" in page_text:
                log("Already checked in today")
                return True

            log("No clock button found (outside time window or already done)")
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
            log("Browser closed")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="SWUN Auto Check-in")
    ap.add_argument("-m", "--manual", action="store_true", help="Manual mode")
    ap.add_argument("--show", action="store_true", help="Show browser")
    args = ap.parse_args()

    headless = not (args.show or args.manual)
    ok = do_checkin(headless=headless, manual_mode=args.manual)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
