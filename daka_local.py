"""
民大自动打卡 — 本地版 + 远程开关
===================================

工作原理：
  1. 每天 21:35 自动运行（Windows 计划任务）
  2. 运行前检查 GitHub 上的开关状态
  3. 开关开启 → 自动打卡；开关关闭 → 跳过
  4. 你可以从任何设备上控制开关（打开/关闭 GitHub Issue）

开关控制：
  开启：https://github.com/Satuky114/luo-zhenghao-portfolio/issues/1
       在 Issue 里评论 "on" 或 "开启"
  关闭：评论 "off" 或 "关闭"
  状态：脚本会自动读取最新评论判断开关状态

首次运行：
  pip install playwright requests
  playwright install chromium
  python daka_local.py --login     # 手动登录一次，保存 Cookie
  python daka_local.py             # 测试自动打卡（如果不在打卡时段会跳过）
"""
import os, sys, time, json, re, traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PT

# ===== 配置 =====
SCHOOL_LAT = 30.562897
SCHOOL_LNG = 103.966624
WXWEB = "https://gyglxt.swun.edu.cn/wxweb/"
CLOCK_HASH = "#/PositioningClock"
GITHUB_REPO = "Satuky114/luo-zhenghao-portfolio"
SWITCH_ISSUE_NUMBER = 1  # 用于远程开关的 Issue 编号

# Desktop Chrome UA - WAF blocks iOS UA but passes desktop Chrome
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)

USERNAME = os.environ.get("SWUN_USERNAME") or ""
PASSWORD = os.environ.get("SWUN_PASSWORD") or ""


def log(msg):
    timestamp = datetime.now().strftime("%m-%d %H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        clean_msg = msg.encode("ascii", errors="replace").decode("ascii")
        print(f"[{timestamp}] {clean_msg}")


def check_remote_switch():
    """
    检查远程开关状态。
    读取 Issue #1 的最新评论：包含 "on"/"开启" → 开启，否则关闭。
    如果无评论，默认开启（首次运行）。
    """
    import urllib.request as req

    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{SWITCH_ISSUE_NUMBER}/comments?per_page=5&sort=updated&direction=desc"
        r = req.urlopen(url, timeout=10)
        comments = json.loads(r.read().decode())

        if not comments:
            log("[SWITCH] 开关未设置（无评论），默认: 开启")
            return True

        latest = comments[0]["body"].strip().lower()
        enabled = any(word in latest for word in ["on", "开启", "打卡", "true", "1"])

        log(f"[SWITCH] 远程开关状态: {'[OK] 开启' if enabled else '[FAIL] 关闭'}（'{latest[:50]}'）")
        return enabled

    except Exception as e:
        log(f"[WARN] 无法检查开关（{e}），默认: 开启")
        return True  # 网络异常时默认开启，保证打卡


def cas_login(page):
    """统一认证登录"""
    page.wait_for_url("**/authserver.swun.edu.cn/**", timeout=20000)
    log("[AUTH] CAS 登录中...")
    page.wait_for_selector("#username", timeout=10000)
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("button[type='submit'], input[type='submit'], button")
    page.wait_for_url("**/wxweb/**", timeout=30000)
    log("[OK] 登录完成")


def do_checkin(manual=False, headless=True):
    log("[START] 启动打卡流程...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=headless,
            geolocation={"latitude": SCHOOL_LAT, "longitude": SCHOOL_LNG},
            permissions=["geolocation"],
            viewport={"width": 1280, "height": 720},
            user_agent=DESKTOP_UA,
            locale="zh-CN",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--headless=new",
            ],
        )
        page = context.new_page()

        # 反检测
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: ()=>false});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        """)

        try:
            # ===== 访问首页 =====
            log("[NAV] 访问首页...")
            page.goto(WXWEB, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(8000)
            log(f"URL: {page.url[:80]}")

            if "authserver" in page.url:
                if not USERNAME or not PASSWORD:
                    log("[FAIL] 未设置密码！请设置环境变量或使用 --login")
                    return False
                cas_login(page)
                page.wait_for_timeout(5000)

            # ===== 导航到打卡页 =====
            log("[NAV] 导航到打卡页...")
            page.evaluate("window.location.hash = '#/PositioningClock'")
            page.wait_for_timeout(8000)

            page.screenshot(path="daka_screen.png", full_page=True)
            log("[SNAP] daka_screen.png")

            body = page.locator("body").inner_text().strip()
            log(f"页面: {body[:200]}")

            if manual:
                log("[MANUAL] 手动模式，操作后按 Enter...")
                input()
                page.screenshot(path="daka_result.png")
                return True

            # ===== 查找并点击打卡按钮 =====
            clock_btn = page.locator("button").filter(has_text="打卡")

            if clock_btn.count() == 0:
                clock_btn = page.locator("button").filter(has_text="签到")

            if clock_btn.count() == 0:
                # 检查是否已打卡
                if "已打卡" in body:
                    log("[OK] 今日已打卡！")
                else:
                    log("[INFO] 可能不在打卡时段(21:30-23:25)")
                return True

            log("[HIT] 点击打卡按钮...")
            clock_btn.first.click()
            page.wait_for_timeout(5000)

            result_text = page.locator("body").inner_text()
            if "成功" in result_text:
                log("[SUCCESS] 打卡成功！")
            else:
                log(f"结果: {result_text[:200]}")

            page.screenshot(path="daka_done.png")
            return True

        except PT as e:
            log(f"[FAIL] 超时: {e}")
            page.screenshot(path="daka_error.png")
            return False
        except Exception as e:
            log(f"[FAIL] {traceback.format_exc()}")
            page.screenshot(path="daka_error.png")
            return False
        finally:
            context.close()


def setup_credentials():
    """交互式设置凭据"""
    print("=" * 50)
    print("[SETUP] 首次配置")
    print("=" * 50)
    print()
    uname = input("学号: ").strip()
    pwd = input("统一认证密码: ").strip()

    # 保存到用户环境变量（Windows）
    if os.name == "nt":
        os.system(f'setx SWUN_USERNAME "{uname}" >nul 2>&1')
        os.system(f'setx SWUN_PASSWORD "{pwd}" >nul 2>&1')
    print()
    print("[OK] 凭据已保存！重新打开终端后生效")
    print("   （或者直接在当前终端继续运行 python daka_local.py）")

    global USERNAME, PASSWORD
    USERNAME = uname
    PASSWORD = pwd


def setup_scheduled_task():
    """创建 Windows 计划任务"""
    script_path = os.path.abspath(__file__)
    python = sys.executable

    task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T21:35:00</StartBoundary>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>"{python}"</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>"{os.path.dirname(script_path)}"</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <Hidden>true</Hidden>
  </Settings>
</Task>'''

    task_file = os.path.join(os.path.dirname(script_path), "daka_task.xml")
    with open(task_file, "w", encoding="utf-8") as f:
        f.write(task_xml)

    print()
    print("=" * 50)
    print("[TASK] 创建 Windows 计划任务")
    print("=" * 50)
    print()
    print("请以管理员身份运行 PowerShell 并执行：")
    print()
    print(f'  schtasks /create /tn "民大打卡" /xml "{task_file}"')
    print()
    print("创建后可在 Windows 搜索 '任务计划程序' 管理")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="民大自动打卡")
    ap.add_argument("--login", action="store_true", help="手动登录保存 Cookie")
    ap.add_argument("--setup", action="store_true", help="设置凭据")
    ap.add_argument("--manual", "-m", action="store_true", help="手动模式")
    ap.add_argument("--show", action="store_true", help="显示浏览器窗口")
    ap.add_argument("--no-switch", action="store_true", help="跳过远程开关检查")
    ap.add_argument("--install-task", action="store_true", help="安装 Windows 计划任务")
    args = ap.parse_args()

    if args.setup:
        setup_credentials()
        return

    if args.install_task:
        setup_scheduled_task()
        return

    if args.login:
        # 直接打开浏览器让用户手动登录
        do_checkin(manual=True, headless=False)
        return

    # ===== 正常打卡流程 =====
    # 1. 检查远程开关
    if not args.no_switch:
        if not check_remote_switch():
            log("[STOP] 远程开关已关闭，跳过打卡")
            return

    # 2. 检查是否在打卡时段
    now = datetime.now()
    # 打卡时段 21:30-23:25
    # 如果是其他时间（非自动触发），也允许运行
    is_clock_time = (
        now.hour == 21 and now.minute >= 30 or
        now.hour == 22 or
        (now.hour == 23 and now.minute <= 25)
    )
    if not is_clock_time and not (args.manual or args.show):
        log(f"[TIME] 当前 {now.strftime('%H:%M')}，不在打卡时段(21:30-23:25)")
        log("   如果是手动测试，请加 --manual 参数")
        return

    # 3. 执行打卡
    do_checkin(manual=args.manual, headless=(not args.show))


if __name__ == "__main__":
    main()
