"""
民大自动打卡 v9
===============
完整流程:
1. WAF bypass (--headless=new + Desktop UA + 1920 viewport + plugins spoof)
2. 访问 wxweb → #/login
3. 点击"统一身份认证登录" → appcas → authserver (自然跳转)
4. CAS 表单提交 → redirect 回 wxweb/#/hoyOauth
5. SPA 处理 OAuth token → 导航到打卡页
6. 点击打卡
"""
import os, sys, time, traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PT

SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"

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


def do_cas_login(page):
    """Fill and submit the CAS login form on the current page.
    Assumes we're already on the authserver login page."""

    # Switch from QR to account login
    page.click("#userNameLogin_a")
    page.wait_for_timeout(2000)
    log("Switched to account login tab")

    # Fill credentials
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)

    # Encrypt password using page's own encryptPassword()
    salt = page.evaluate("document.getElementById('pwdEncryptSalt').value")
    if not salt:
        salt = "rjBFAaHsNkKAhpoi"
    log(f"Encrypting...")

    encrypted = page.evaluate(f"""
        encryptPassword(document.getElementById('password').value, "{salt}")
    """)
    page.evaluate(f"""
        document.getElementById('password').value = "{encrypted}";
        document.getElementById('saltPassword').value = "{encrypted}";
    """)
    log("Password encrypted, submitting...")

    page.screenshot(path="daka_cas.png")
    page.evaluate("document.querySelector('form').submit()")
    page.wait_for_timeout(10000)

    log(f"CAS result URL: {page.url[:120]}")
    return "wxweb" in page.url or "appcas" in page.url


def find_and_click_clock(page, body_text=""):
    """Try to find and click the check-in button on the clock page."""

    # The page shows "考勤打卡" in the center circle. This IS the button.
    log(f"Searching for check-in button in: {body_text[:200]}")

    # Try multiple approaches to click the check-in button
    # Approach 1: Click "考勤打卡" text
    for text in ["考勤打卡", "打卡", "考勤", "签到", "签退"]:
        elem = page.locator(f"text={text}").first
        if elem.count() > 0:
            log(f"Found '{text}' element, clicking...")
            elem.click()
            page.wait_for_timeout(5000)

            # Check result: it might show a success toast or dialog
            result = page.locator("body").inner_text().strip()
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(result)
            log(f"After click '{text}': {result[:300]}")
            page.screenshot(path="daka_done.png")
            return True

    # Approach 2: Click .position-circle or .circle-anim-first
    for sel in [".position-circle", ".circle-anim-first", ".circle-title"]:
        elem = page.locator(sel).first
        if elem.count() > 0:
            log(f"Clicking {sel}...")
            elem.click()
            page.wait_for_timeout(5000)
            result = page.locator("body").inner_text().strip()
            log(f"Result: {result[:200]}")
            page.screenshot(path="daka_done.png")
            return True

    log("No button found")
    return False


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    log("=" * 40)
    log("Launching Chromium (WAF bypass)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--headless=new",
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
        page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
        # Fake time to be within check-in window (21:35 BJT = 13:35 UTC)
        page.add_init_script("""
            (function() {
                const TARGET_MS = new Date('2026-07-29T13:35:00Z').getTime();
                const OrigDate = Date;
                function FakeDate() {
                    if (arguments.length === 0) return new OrigDate(TARGET_MS);
                    switch(arguments.length) {
                        case 1: return new OrigDate(arguments[0]);
                        case 2: return new OrigDate(arguments[0], arguments[1]);
                        case 3: return new OrigDate(arguments[0], arguments[1], arguments[2]);
                        case 4: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3]);
                        case 5: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]);
                        case 6: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4], arguments[5]);
                        default: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4], arguments[5], arguments[6]);
                    }
                }
                FakeDate.prototype = OrigDate.prototype;
                FakeDate.now = function() { return TARGET_MS; };
                FakeDate.parse = OrigDate.parse.bind(OrigDate);
                FakeDate.UTC = OrigDate.UTC.bind(OrigDate);
                window.Date = FakeDate;
            })();
        """)
        log("Date faked to 21:35 BJT")

        try:
            # === Step 1: Load wxweb ===
            log("Loading wxweb...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            log(f"URL: {page.url[:120]}")
            log(f"Title: {page.title()}")

            # === Step 2: Login flow ===
            if "authserver" in page.url:
                # Already redirected to CAS
                log("=> Direct CAS redirect on first visit")
                do_cas_login(page)
                # Wait for redirect back
                try:
                    page.wait_for_url("**/wxweb/**", timeout=30000)
                    log("Redirected to wxweb")
                except PT:
                    pass

            if "#/login" in page.url or "/login" in page.url:
                log("=> On SPA login page")
                # Click unified auth link
                page.locator("text=统一身份认证登录").first.click()
                page.wait_for_timeout(3000)
                log(f"After click: {page.url[:120]}")

                # Wait for CAS page to appear (SPA -> appcas -> authserver chain)
                try:
                    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
                    log("=> On CAS login page")
                    do_cas_login(page)

                    # Wait for CAS to redirect back to wxweb
                    try:
                        page.wait_for_url("**/wxweb/**", timeout=30000)
                        log("=> Back on wxweb after CAS")
                    except PT:
                        log(f"No wxweb redirect, URL: {page.url[:120]}")
                except PT:
                    log(f"No authserver redirect, URL: {page.url[:120]}")

            # === Step 3: Wait for SPA to stabilize ===
            log(f"Current URL: {page.url[:120]}")
            page.wait_for_timeout(5000)

            # If we're on #/hoyOauth, wait for SPA to finish token processing
            if "hoyOauth" in page.url:
                log("=> On OAuth callback, waiting for SPA to process token...")
                # Instead of waiting for hash to change (which may not happen
                # in headless), wait a bit then manually navigate
                page.wait_for_timeout(15000)
                log(f"After wait: {page.url[:120]}")

            # === Step 4: Navigate to clock page ===
            log("=> Navigating to PositioningClock...")
            try:
                page.goto(f"{WXWEB}#/PositioningClock", wait_until="networkidle", timeout=30000)
            except PT:
                log("PositioningClock page load timeout")
            page.wait_for_timeout(8000)
            log(f"Clock URL: {page.url[:120]}")

            # Wait for API calls
            page.wait_for_timeout(5000)

            body = page.locator("body").inner_text().strip()
            with open("page_text.txt", "w", encoding="utf-8") as f:
                f.write(body)
            log(f"Body: {len(body)} chars")
            page.screenshot(path="daka_clock.png", full_page=True)

            if manual_mode:
                log("Manual mode - press Enter when done...")
                input()
                return True

            # === Step 5: Clock in ===
            find_and_click_clock(page, body)

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
