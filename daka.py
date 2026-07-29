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

            # Step 4: Navigate to clock page
            log(f"Pre-clock URL: {page.url[:100]}")
            page.evaluate("window.location.hash = '#/PositioningClock'")
            page.wait_for_timeout(5000)
            log(f"Clock page URL: {page.url[:100]}")

            body = page.locator("body").inner_text().strip()
            log(f"Clock body ({len(body)} chars): {body[:200]}")
            page.screenshot(path="daka_clock.png", full_page=True)

            if manual_mode:
                log("Manual mode - press Enter when done...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # Step 5: Find and click check-in button
            # Dump all interactive elements for debugging
            for sel in ["button", "[role=button]", "a.van-button", "div.van-button",
                        ".van-button", "[class*=btn]", "[class*=Btn]",
                        "div[class*=clock]", "div[class*=check]", "div[class*=sign]",
                        "div[class*=punch]"]:
                elems = page.locator(sel).all()
                if elems:
                    log(f"Selector '{sel}': {len(elems)} elements")

            # Full page HTML dump (headless debugging)
            html = page.content()
            log(f"Page HTML length: {len(html)}")
            # Extract all class names to understand the component library
            classes = page.evaluate("""
                Array.from(document.querySelectorAll('*'))
                    .map(el => el.className)
                    .filter(c => typeof c === 'string' && c.length > 0 && c.length < 80)
                    .slice(0, 50)
            """)
            log(f"Classes: {classes}")

            btns = page.locator("button").all()
            log(f"Buttons found: {len(btns)}")
            for i, b in enumerate(btns[:10]):
                try:
                    log(f"  [{i}] '{b.inner_text()[:40]}'")
                except:
                    pass

            # Also check for any div/span with click-like text
            for label in ["打卡", "签到", "提交", "确认"]:
                for tag in ["button", "div", "span", "a"]:
                    elem = page.locator(f"{tag}:has-text('{label}')")
                    if elem.count() > 0:
                        log(f"Found '{label}' in <{tag}> x{elem.count()}")
                        elem.first.click()
                        page.wait_for_timeout(5000)
                        result = page.locator("body").inner_text()
                        log(f"Result after clicking '{label}': {result[:250]}")
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
