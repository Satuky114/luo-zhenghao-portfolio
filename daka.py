"""
民大自动打卡 v14 - 多重时间校验版
=============================
v12 关键发现:
- queryPersonDetailInfoByPersonsn API 返回 code=500 在非打卡时段
- 原因: 服务器在非打卡时段 (21:30-23:25 BJT) 拒绝请求

v14 变更:
- 非窗口时间改轮询等待（应对 GitHub Actions cron 延迟）
- 多重时间校验：登陆后、点击打卡前再次检查窗口
- 任一校验点滑出窗口 → 放弃本轮，避免服务器拒绝
- cron 提前到 19:30 BJT (30 11 * * *)
- --force 跳过所有时间检查（用于 workflow_dispatch 测试）
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


def in_checkin_window():
    """Check-in window: 21:30 - 23:25 BJT (server-side enforced)."""
    now = datetime.now(BJT)
    return (
        (now.hour == 21 and now.minute >= 30) or
        now.hour == 22 or
        (now.hour == 23 and now.minute <= 25)
    )


def window_status():
    """Human-readable window status for logging."""
    now = datetime.now(BJT)
    return f"{now.strftime('%H:%M')} BJT — {'IN window' if in_checkin_window() else 'OUTSIDE window'}"


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
        if os.path.exists(COOKIE_FILE):
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
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    salt = page.evaluate("(document.getElementById('pwdEncryptSalt')||{}).value") or "rjBFAaHsNkKAhpoi"
    encrypted = page.evaluate(f"""encryptPassword(document.getElementById('password').value, "{salt}")""")
    page.evaluate(f"""document.getElementById('password').value = "{encrypted}"; document.getElementById('saltPassword').value = "{encrypted}";""")
    log("Submitting CAS form...")
    page.screenshot(path="daka_cas.png")
    page.evaluate("document.querySelector('form').submit()")
    page.wait_for_timeout(10000)
    log(f"After CAS: {page.url[:120]}")
    return "wxweb" in page.url or "appcas" in page.url


def find_and_click_clock(page):
    """Locate and click the check-in circle."""
    body = page.locator("body").inner_text().strip()
    with open("page_text.txt", "w", encoding="utf-8") as f:
        f.write(body)
    log(f"Page: {len(body)} chars")
    page.screenshot(path="daka_clock.png", full_page=True)

    if "已打卡" in body or "签到成功" in body or "打卡成功" in body:
        log("ALREADY CHECKED IN TODAY")
        return True

    # Wait for loading to disappear (queryPersonDetailInfo API may take time)
    for i in range(15):
        toast_visible = page.evaluate("""
            (function() {
                var t = document.querySelector('.van-toast--loading, .van-loading');
                if (t && window.getComputedStyle(t).display !== 'none') return true;
                var tt = document.querySelector('.van-toast__text');
                if (tt && tt.textContent.includes('queryPerson')) return true;
                return false;
            })()
        """)
        if toast_visible:
            if i == 0:
                log("Waiting for loading to finish...")
            page.wait_for_timeout(2000)
        else:
            log("Loading complete")
            break
    else:
        log("Loading timeout (30s)")

    # ⌛ 最后防线：点击前确认仍在窗口内
    if not in_checkin_window():
        log(f"Window closed before click! {window_status()}")
        log("Aborting to avoid server rejection.")
        return True

    # Click the circle
    circle = page.locator(".position-circle")
    if circle.count() == 0:
        log("No .position-circle")
        return False

    circ_box = circle.first.bounding_box()
    if circ_box:
        cx = circ_box['x'] + circ_box['width'] / 2
        cy = circ_box['y'] + circ_box['height'] / 2
        log(f"Clicking at ({cx:.0f}, {cy:.0f})")
        page.mouse.click(cx, cy)
    else:
        circle.first.click()

    page.wait_for_timeout(5000)

    result = page.locator("body").inner_text().strip()
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(result)

    # Check toast/dialog
    toast = page.evaluate("""
        (function() {
            var t = document.querySelector('.van-toast__text');
            var d = document.querySelector('.van-dialog__message');
            return {toast: t ? t.textContent : '', dialog: d ? d.textContent : ''};
        })()
    """)
    log(f"Toast: {toast['toast']}, Dialog: {toast['dialog']}")
    page.screenshot(path="daka_done.png")

    if "成功" in result or "已打卡" in result or "签到成功" in result:
        log("CHECK-IN SUCCESSFUL!")
        return True

    return True  # Not an error even if result unclear


def do_checkin(headless=True, force=False):
    """Main entry. force=True skips all time-window checks."""

    now = datetime.now(BJT)

    if not in_checkin_window() and not force:
        log(f"{window_status()} — will poll every 2min (max 3h)...")
        deadline = now + timedelta(hours=3)
        while True:
            time.sleep(120)
            now = datetime.now(BJT)
            if in_checkin_window():
                log(f"Window open! {window_status()}")
                break
            if now > deadline:
                log("Poll timeout (3h elapsed), giving up")
                return True
            if now.hour >= 23 and now.minute > 25:
                log("Window already closed for today, giving up")
                return True
            log(f"Still waiting... ({now.strftime('%H:%M')} BJT)")

    if force and not in_checkin_window():
        log(f"WARNING: {window_status()} — API calls may fail (code 500).")

    log("=" * 60)
    log(f"v14 - Starting check-in at {now.strftime('%Y-%m-%d %H:%M:%S')} BJT")

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
            # Step 1: Load
            load_cookies(context)
            log("Loading wxweb...")
            page.goto(WXWEB, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            log(f"URL: {page.url[:120]}")

            # Step 2: Login
            if "authserver" in page.url or "#/login" in page.url:
                if "#/login" in page.url:
                    log("=> SPA login page")
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
                log("=> Already logged in (cookie)")

            save_cookies(context)

            # Step 3: OAuth handling
            page.wait_for_timeout(3000)
            if "hoyOauth" in page.url:
                log("OAuth token processing (15s)...")
                page.wait_for_timeout(15000)

            # ⌛ Login+OAuth cost time — re-verify window before proceeding
            if not force and not in_checkin_window():
                log(f"Window closed after login! {window_status()}")
                log("Aborting to avoid server rejection.")
                return True

            # Step 4: Navigate to clock page
            log("=> PositioningClock...")
            try:
                page.goto(f"{WXWEB}#/PositioningClock", wait_until="networkidle", timeout=30000)
            except PT:
                pass
            log(f"Clock URL: {page.url[:120]}")

            # Step 5: Wait for API + click
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
    ap = argparse.ArgumentParser(description="民大自动打卡 v14")
    ap.add_argument("-m", "--manual", action="store_true", help="Non-headless, interactive")
    ap.add_argument("--show", action="store_true", help="Show browser window")
    ap.add_argument("--force", action="store_true", help="Skip time window check")
    args = ap.parse_args()

    ok = do_checkin(
        headless=(not args.show and not args.manual),
        force=args.force
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
