"""
民大自动打卡 v10
===============
新增网络请求监控，诊断 queryPersonDetailInfo API 问题
"""
import os, sys, time, json, traceback
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
    page.click("#userNameLogin_a")
    page.wait_for_timeout(2000)
    log("Switched to account login tab")

    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)

    salt = page.evaluate("document.getElementById('pwdEncryptSalt').value")
    if not salt:
        salt = "rjBFAaHsNkKAhpoi"
    log("Encrypting password...")

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


def do_checkin(headless=True, manual_mode=False):
    if not headless:
        manual_mode = True

    log("=" * 40)
    log("v10 - Launching Chromium...")

    api_log = []

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
        # Fake time to check-in window (21:35 BJT = 13:35 UTC)
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

        # Monitor ALL API requests/responses on wxweb domain
        def on_response(resp):
            url = resp.url
            if "gyglxt" in url or "swun" in url:
                if any(kw in url for kw in ["queryPerson", "clock", "check", "punch", "sign", "attendance", "login", "oauth", "token", "info", "detail"]):
                    try:
                        status = resp.status
                        body = ""
                        try:
                            body = resp.text()[:300]
                        except:
                            body = "[binary/non-text]"
                        api_log.append(f"  [{status}] {url[:120]}")
                        if status >= 400 or "error" in body.lower():
                            api_log.append(f"    Body: {body[:200]}")
                    except:
                        api_log.append(f"  [ERR] {url[:120]}")

        page.on("response", on_response)

        try:
            # === Step 1: Load wxweb ===
            log("Loading wxweb...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            log(f"URL: {page.url[:120]}")

            # === Step 2: Login flow ===
            if "authserver" in page.url:
                log("=> Direct CAS redirect")
                do_cas_login(page)
                try:
                    page.wait_for_url("**/wxweb/**", timeout=30000)
                except PT:
                    pass

            if "#/login" in page.url or "/login" in page.url:
                log("=> On SPA login page")
                page.locator("text=统一身份认证登录").first.click()
                page.wait_for_timeout(3000)
                log(f"After click: {page.url[:120]}")

                try:
                    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
                    log("=> On CAS login page")
                    do_cas_login(page)
                    try:
                        page.wait_for_url("**/wxweb/**", timeout=30000)
                        log("=> Back on wxweb after CAS")
                    except PT:
                        log(f"No wxweb redirect, URL: {page.url[:120]}")
                except PT:
                    log(f"No authserver redirect, URL: {page.url[:120]}")

            # === Step 3: Navigate to clock page ===
            log(f"Current URL: {page.url[:120]}")
            page.wait_for_timeout(5000)

            log("=> Navigating to PositioningClock...")
            try:
                page.goto(f"{WXWEB}#/PositioningClock", wait_until="networkidle", timeout=30000)
            except PT:
                log("PositioningClock page load timeout")
            log(f"Clock URL: {page.url[:120]}")

            # Wait longer for all API calls
            log("Waiting for API calls to settle (30s)...")
            page.wait_for_timeout(30000)
            log("API wait complete")

            # Dump API log
            log(f"--- API calls captured ({len(api_log)}) ---")
            for entry in api_log[-30:]:  # last 30 entries
                log(entry)

            # Check localStorage/sessionStorage for auth tokens
            storage = page.evaluate("""
                (function() {
                    var ls = {};
                    try {
                        for (var i = 0; i < localStorage.length; i++) {
                            var k = localStorage.key(i);
                            ls['LS:'+k] = localStorage.getItem(k).substring(0, 80);
                        }
                        for (var i = 0; i < sessionStorage.length; i++) {
                            var k = sessionStorage.key(i);
                            ls['SS:'+k] = sessionStorage.getItem(k).substring(0, 80);
                        }
                    } catch(e) { ls['error'] = e.toString(); }
                    return ls;
                })()
            """)
            log(f"Storage keys: {list(storage.keys())}")
            for k, v in storage.items():
                log(f"  {k}: {v}")

            # Page state
            body = page.locator("body").inner_text().strip()
            with open("page_text.txt", "w", encoding="utf-8") as f:
                f.write(body)
            log(f"Body: {len(body)} chars")
            page.screenshot(path="daka_clock.png", full_page=True)

            if manual_mode:
                log("Manual mode - press Enter when done...")
                input()
                return True

            # === Step 5: Click check-in ===
            circle = page.locator(".position-circle")
            if circle.count() > 0:
                box = circle.first.bounding_box()
                if box:
                    log(f"Circle: x={box['x']:.0f} y={box['y']:.0f} w={box['width']:.0f} h={box['height']:.0f}")
                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
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
                log(f"Toast/dialog after click: {toast}")
                log(f"URL after click: {page.url[:120]}")
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
    args = ap.parse_args()
    ok = do_checkin(headless=(not args.show and not args.manual), manual_mode=args.manual)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
