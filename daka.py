"""
民大自动打卡 v11 - 最终版
========================
v10 诊断结果:
- CAS login OK, token OK, userInfo OK
- queryPersonDetailInfoByPersonsn returns 200
- Toast shows 'queryPersonDetailInfoByPersonsnV1' indefinitely
- Cause: FakeDate breaks Vue.js timers. Toast uses setTimeout for auto-dismiss.
- Solution: REMOVE Date hack. Check-in window check must be at the server level,
  not via client-side time spoofing.

Strategy:
- Server-side time check: the clock page itself shows when check-in is allowed.
  The app's business logic determines if the clock button is active.
- The script should run during actual check-in window (21:30-23:25 BJT).
- For testing: use --no-check-time flag to bypass time window.

Removed: Date override (breaks Vue reactivity)
Added: Cookie persistence, time window check, clean flow
"""
import os, sys, time, json, traceback
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PT

BJT = timezone(timedelta(hours=8))

SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"
COOKIE_FILE = "swun_cookies.json"

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)

USERNAME = os.environ.get("SWUN_USERNAME") or ""
PASSWORD = os.environ.get("SWUN_PASSWORD") or ""


def log(msg):
    safe = msg.encode("ascii", errors="replace").decode("ascii")
    print(f"[{datetime.now(BJT).strftime('%H:%M:%S')}] {safe}")


def save_cookies(context):
    try:
        cookies = context.cookies()
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f)
        log(f"Saved {len(cookies)} cookies")
    except Exception as e:
        log(f"Cookie save err: {e}")


def load_cookies(context):
    try:
        with open(COOKIE_FILE) as f:
            cookies = json.load(f)
            if cookies:
                context.add_cookies(cookies)
                log(f"Loaded {len(cookies)} cookies")
                return True
    except:
        pass
    return False


def do_cas_login(page):
    """CAS login: click tab, fill form, encrypt password, submit"""
    page.click("#userNameLogin_a")
    page.wait_for_timeout(2000)
    log("Account login tab")

    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)

    salt = page.evaluate("(document.getElementById('pwdEncryptSalt')||{}).value") or "rjBFAaHsNkKAhpoi"
    encrypted = page.evaluate(f"""encryptPassword(document.getElementById('password').value, "{salt}")""")
    page.evaluate(f"""document.getElementById('password').value = "{encrypted}"; document.getElementById('saltPassword').value = "{encrypted}";""")
    log("Password encrypted, submitting...")

    page.screenshot(path="daka_cas.png")
    page.evaluate("document.querySelector('form').submit()")
    page.wait_for_timeout(10000)
    log(f"CAS URL: {page.url[:120]}")
    return "wxweb" in page.url or "appcas" in page.url


def find_and_click_clock(page):
    """Find the check-in circle and click it."""
    body = page.locator("body").inner_text().strip()
    with open("page_text.txt", "w", encoding="utf-8") as f:
        f.write(body)
    log(f"Page: {len(body)} chars")
    page.screenshot(path="daka_clock.png", full_page=True)

    # Check if in clock window (page shows "考勤打卡" = ready, otherwise shows time range)
    if "已打卡" in body:
        log("ALREADY CHECKED IN TODAY")
        return True

    # Click the center circle
    circle = page.locator(".position-circle")
    if circle.count() == 0:
        log("No .position-circle found")
        return False

    box = circle.first.bounding_box()
    if box:
        cx = box['x'] + box['width'] / 2
        cy = box['y'] + box['height'] / 2
        log(f"Click at ({cx:.0f},{cy:.0f})")
        page.mouse.click(cx, cy)
    else:
        circle.first.click()

    page.wait_for_timeout(5000)

    result = page.locator("body").inner_text().strip()
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(result)

    toast = page.evaluate("""
        (function() {
            var t = document.querySelector('.van-toast__text');
            var d = document.querySelector('.van-dialog__message');
            return {toast: t ? t.textContent : '', dialog: d ? d.textContent : ''};
        })()
    """)
    log(f"Post-click toast: {toast['toast']}, dialog: {toast['dialog']}")
    page.screenshot(path="daka_done.png")
    return True


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    # Time window check
    now = datetime.now(BJT)
    in_window = (
        (now.hour == 21 and now.minute >= 30) or
        now.hour == 22 or
        (now.hour == 23 and now.minute <= 25)
    )
    if not in_window and not manual_mode:
        log(f"NOT in check-in window (21:30-23:25 BJT). Current: {now.strftime('%H:%M')} BJT")
        log("Skipping. Use --manual to force.")
        return True  # success = skipped correctly

    log("=" * 40)
    log("v11 - Starting...")

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
        page.add_init_script("""Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});""")

        try:
            # Step 1: Load wxweb
            load_cookies(context)
            log("Loading wxweb...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            log(f"URL: {page.url[:120]}")

            # Step 2: Login if needed
            if "authserver" in page.url:
                log("=> CAS redirect (not logged in)")
                do_cas_login(page)
                try:
                    page.wait_for_url("**/wxweb/**", timeout=30000)
                except PT:
                    pass
            elif "#/login" in page.url:
                log("=> SPA login page")
                page.locator("text=统一身份认证登录").first.click()
                page.wait_for_timeout(3000)
                try:
                    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
                    do_cas_login(page)
                    try:
                        page.wait_for_url("**/wxweb/**", timeout=30000)
                    except PT:
                        pass
                except PT:
                    log(f"Not redirected to CAS: {page.url[:120]}")
            else:
                log("=> Already logged in")

            # Save cookies
            save_cookies(context)

            # Step 3: Handle OAuth and navigate to clock page
            page.wait_for_timeout(3000)
            if "hoyOauth" in page.url:
                log("OAuth token processing...")
                page.wait_for_timeout(10000)

            log("=> Navigating to PositioningClock...")
            try:
                page.goto(f"{WXWEB}#/PositioningClock", wait_until="networkidle", timeout=30000)
            except PT:
                pass
            page.wait_for_timeout(5000)
            log(f"Clock URL: {page.url[:120]}")

            # Step 4: Wait for page to fully render (API calls)
            log("Waiting for API calls...")
            page.wait_for_timeout(15000)

            # Page state
            body = page.locator("body").inner_text().strip()
            with open("page_text.txt", "w", encoding="utf-8") as f:
                f.write(body)
            log(f"Page body ({len(body)} chars)")

            if manual_mode:
                log("Manual mode - press Enter when done...")
                try:
                    input()
                except EOFError:
                    log("(EOF on input, continuing automatically)")
                page.screenshot(path="daka_result.png")
                # Also try clicking in manual mode
                find_and_click_clock(page)
                return True

            # Step 5: Find and click check-in button
            ok = find_and_click_clock(page)
            return ok

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
    ap.add_argument("-m", "--manual", action="store_true", help="Manual mode (non-headless)")
    ap.add_argument("--show", action="store_true", help="Show browser window")
    ap.add_argument("--force", action="store_true", help="Force run (bypass time window check)")
    args = ap.parse_args()
    ok = do_checkin(
        headless=(not args.show and not args.manual),
        manual_mode=(args.manual or args.force)
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
