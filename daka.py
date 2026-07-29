"""
民大自动打卡 v12 - 诊断版
========================
v11 发现: 移除 Date 覆盖后，toast 仍然显示 queryPersonDetailInfoByPersonsnV1
需要诊断: API 响应的实际内容、JS 控制台错误、Vue 组件状态
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


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    log("=" * 40)
    log("v12 - Diagnostic mode...")

    console_logs = []
    api_data = {}

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

        # Hook JS console
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text[:200]}"))
        page.on("pageerror", lambda err: console_logs.append(f"[UNCAUGHT] {str(err)[:300]}"))

        # Hook API responses for key endpoints
        def capture_response(resp):
            url = resp.url
            if any(kw in url for kw in [
                "queryPersonDetailInfo", "queryAttend", "queryClock",
                "saveClock", "saveAttend", "clockIn", "punchClock",
                "studentInfo", "user/info", "getClockSetting"
            ]):
                try:
                    api_data[url] = {"status": resp.status, "body": resp.text()[:1000]}
                except:
                    api_data[url] = {"status": resp.status, "body": "(binary)"}
        page.on("response", capture_response)

        try:
            # Step 1-3: Login flow (known working)
            load_cookies(context)
            log("Loading wxweb...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            log(f"URL: {page.url[:120]}")

            if "authserver" in page.url or "#/login" in page.url:
                if "#/login" in page.url:
                    page.locator("text=统一身份认证登录").first.click()
                    page.wait_for_timeout(3000)
                    try:
                        page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
                    except PT:
                        pass
                do_cas_login(page)
                try:
                    page.wait_for_url("**/wxweb/**", timeout=30000)
                except PT:
                    pass
            else:
                log("Cookie login OK")

            save_cookies(context)

            # Step 4: Navigate to clock page
            page.wait_for_timeout(3000)
            if "hoyOauth" in page.url:
                page.wait_for_timeout(15000)

            log("Navigating to clock page...")
            try:
                page.goto(f"{WXWEB}#/PositioningClock", wait_until="networkidle", timeout=30000)
            except PT:
                pass
            page.wait_for_timeout(20000)
            log(f"Clock URL: {page.url[:120]}")

            # Print console logs
            log(f"--- Console logs ({len(console_logs)} entries) ---")
            for m in console_logs[-25:]:
                log(m)

            # Print API data
            log(f"--- API responses ({len(api_data)} calls) ---")
            for url, data in api_data.items():
                log(f"  [{data['status']}] {url[:120]}")
                log(f"    Body: {data['body'][:300]}")

            # Check notification permission (needed for geolocation)
            notif = page.evaluate("Notification ? Notification.permission : 'no Notification API'")
            log(f"Notification permission: {notif}")

            body = page.locator("body").inner_text().strip()
            with open("page_text.txt", "w", encoding="utf-8") as f:
                f.write(body)
            page.screenshot(path="daka_clock.png", full_page=True)

            # Try force clicking the circle using JS
            log("Dispatching click event on circle...")
            page.evaluate("""
                (function() {
                    var c = document.querySelector('.position-circle');
                    if (c) {
                        var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                        c.dispatchEvent(evt);
                        // Also try touch events (this is a mobile app)
                        var te = new TouchEvent('touchend', {
                            bubbles: true, cancelable: true,
                            touches: [], targetTouches: [], changedTouches: []
                        });
                        c.dispatchEvent(te);
                    }
                })()
            """)
            page.wait_for_timeout(5000)

            result = page.locator("body").inner_text().strip()
            with open("result.txt", "w", encoding="utf-8") as f:
                f.write(result)
            page.screenshot(path="daka_done.png")
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
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    ok = do_checkin(
        headless=(not args.show and not args.manual),
        manual_mode=(args.manual or args.force)
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
