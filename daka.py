"""
民大自动打卡 v8
===============
WAF 绕过验证: --headless=new + Desktop Chrome UA + 1920 viewport
完整流程: WAF → SPA登录页 → CAS认证 → 定位打卡
"""
import os, sys, time, traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PT

SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"
CAS_REDIRECT = "https://gyglxt.swun.edu.cn/appcas/ssoMobileLogin.jsp"

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


def cas_login_full(page):
    """
    Full CAS login flow:
    1. Navigate to CAS with service redirect
    2. Switch from QR code tab to account login tab
    3. Fill credentials, encrypt password, submit form
    """
    cas_url = f"https://authserver.swun.edu.cn/authserver/login?service={CAS_REDIRECT}"
    log(f"Going to CAS: {cas_url[:80]}...")
    page.goto(cas_url, timeout=30000, wait_until="networkidle")
    page.wait_for_timeout(3000)

    # CAS shows QR code by default. Click '账号登录' tab.
    page.click("#userNameLogin_a")
    page.wait_for_timeout(2000)
    log("Switched to account login")

    # Fill credentials
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)

    # Get encryption salt and encrypt password
    salt = page.evaluate("document.getElementById('pwdEncryptSalt').value")
    if not salt:
        salt = "rjBFAaHsNkKAhpoi"  # Fallback default salt from login.js
    log(f"Encrypting with salt: {salt[:10]}...")

    # Use CAS's own encryptPassword function from encrypt.js
    encrypted = page.evaluate(f"""
        encryptPassword(document.getElementById('password').value, "{salt}")
    """)
    # Set the encrypted password back
    page.evaluate(f"""
        document.getElementById('password').value = "{encrypted}";
        document.getElementById('saltPassword').value = "{encrypted}";
    """)
    log("Password encrypted")

    # Monitor POST response
    page.screenshot(path="daka_cas.png")
    log("Submitting CAS form...")
    page.evaluate("document.querySelector('form').submit()")
    page.wait_for_timeout(10000)

    log(f"CAS result URL: {page.url[:120]}")
    return "wxweb" in page.url or "appcas" in page.url


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
        # Only spoof plugins (webdriver=False is already handled by Chrome args)
        page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
        # Override Date BEFORE any page JS runs
        page.add_init_script("""
            (function() {
                const TARGET_MS = new Date('2026-07-29T13:35:00Z').getTime();
                const OrigDate = Date;
                const OrigNow = Date.now;
                const OrigParse = Date.parse;
                const OrigUTC = Date.UTC;

                function FakeDate() {
                    if (arguments.length === 0) return new OrigDate(TARGET_MS);
                    // Need to use .apply with the arguments object in a way that works
                    switch(arguments.length) {
                        case 1: return new OrigDate(arguments[0]);
                        case 2: return new OrigDate(arguments[0], arguments[1]);
                        case 3: return new OrigDate(arguments[0], arguments[1], arguments[2]);
                        case 4: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3]);
                        case 5: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]);
                        case 6: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4], arguments[5]);
                        case 7: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4], arguments[5], arguments[6]);
                        default: return new OrigDate(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4], arguments[5], arguments[6]);
                    }
                }
                FakeDate.prototype = OrigDate.prototype;
                FakeDate.now = function() { return TARGET_MS; };
                FakeDate.parse = OrigParse;
                FakeDate.UTC = OrigUTC;
                FakeDate.__proto__ = OrigDate;

                window.Date = FakeDate;
                window.__origDate = OrigDate;
            })();
        """)
        log("Date overridden to 21:35 BJT")

        try:
            # Step 1: Load wxweb home
            log("Loading wxweb...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)
            log(f"URL: {page.url[:100]}")

            # Step 2: Handle CAS / login
            if "authserver" in page.url:
                log("CAS redirect detected")
                if not USERNAME or not PASSWORD:
                    log("ERROR: No credentials in env")
                    return False
                ok = cas_login_full(page)
                if not ok:
                    log("CAS login may have failed, but continuing...")
                # Go back to wxweb
                page.goto(WXWEB, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(5000)

            # Step 3: Handle SPA login page
            if "#/login" in page.url or "/login" in page.url:
                log("On SPA login page - clicking unified auth...")
                # Click the "统一身份认证登录，点击进入>>" element
                auth_elem = page.locator("text=统一身份认证登录").first
                if auth_elem.count() > 0:
                    auth_elem.click()
                    page.wait_for_timeout(5000)
                    log(f"After click URL: {page.url[:100]}")

                    # Now we should be on CAS
                    if "authserver" in page.url:
                        if not USERNAME or not PASSWORD:
                            log("ERROR: No credentials")
                            return False
                        ok = cas_login_full(page)
                        if ok:
                            # After CAS, wait for redirect back to wxweb
                            try:
                                page.wait_for_url("**/wxweb/**", timeout=30000)
                            except PT:
                                log(f"Post-CAS URL: {page.url[:100]}")
                    else:
                        log("No CAS redirect after clicking unified auth")
                else:
                    log("Unified auth element not found on login page")

            # Step 4: Handle OAuth callback or navigate to clock page
            log(f"Pre-clock URL: {page.url[:100]}")

            # If CAS returned us to #/hoyOauth, wait for SPA to process token
            if "hoyOauth" in page.url or "oauth" in page.url.lower():
                log("Detected OAuth callback, waiting for token processing...")
                page.wait_for_timeout(5000)
                log(f"Post-OAuth URL: {page.url[:100]}")

            page.evaluate("window.location.hash = '#/PositioningClock'")
            page.wait_for_timeout(5000)
            log(f"Clock page URL: {page.url[:100]}")

            body = page.locator("body").inner_text().strip()
            log(f"Clock body ({len(body)} chars): {body[:300]}")
            page.screenshot(path="daka_clock.png", full_page=True)

            if manual_mode:
                log("Manual mode - press Enter when done...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # Step 5: Find and click check-in button
            # The page uses Vant UI (van-* classes). Dump clock container HTML.
            clock_html = page.evaluate("""
                (function() {
                    var el = document.querySelector('.position-clock') || document.querySelector('.content-box');
                    return el ? el.innerHTML.substring(0, 3000) : 'NO_CLOCK';
                })()
            """)
            log(f"Clock HTML: {clock_html[:500]}")
            log(f"---HTML clipped---")

            # Dump ALL text nodes in the clock area
            all_text = page.evaluate("""
                Array.from(document.querySelectorAll('*'))
                    .filter(el => el.children.length === 0 && el.textContent.trim().length > 0)
                    .map(el => el.tagName + ':' + el.className + '="' + el.textContent.trim().substring(0,30) + '"')
                    .filter(s => !s.includes('van-tabbar'))
                    .slice(0, 60)
            """)
            for t in all_text:
                log(f"  {t}")

            # Check time on the page
            time_info = page.evaluate("""
                (function() {
                    var t = document.querySelector('.position-time');
                    return t ? t.textContent.trim() : 'NO_TIME';
                })()
            """)
            log(f"Page time: {time_info}")

            # Try clicking the central circle animation (the clock-in button)
            circle = page.locator(".circle-anim-first, .circle-title, .title-body, .circle-anim-first *")
            if circle.count() > 0:
                log(f"Clicking circle animation element...")
                circle.first.click()
                page.wait_for_timeout(5000)
                result = page.locator("body").inner_text()
                log(f"Result: {result[:300]}")
                page.screenshot(path="daka_done.png")
                return True

            if "已打卡" in body:
                log("Already checked in today")
            else:
                log("No clickable check-in element found (outside clock window?)")
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
