"""
民大自动打卡 — Cookie 管理工具
用于本地登录后导出 Cookie，上传到 GitHub Secrets 供 Actions 使用
"""
import os
import json
import base64
import sys

COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_data", "Default", "Cookies")
STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_data", "Default", "Local Storage", "leveldb")


def export_cookies_from_playwright():
    """导出 Playwright persistent context 中的认证信息为 base64"""
    # Playwright 的持久化上下文会保存 cookies 到 browser_data/
    # 但我们需要导出为可移植格式
    print("=" * 50)
    print("📤 Cookie 导出工具")
    print("=" * 50)
    print()
    print("此工具将 browser_data/ 目录打包为 base64 字符串")
    print("你需要将其上传到 GitHub Secrets 作为 SWUN_COOKIES")
    print()

    import tempfile
    import shutil

    browser_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_data")

    if not os.path.exists(browser_data_dir):
        print("❌ browser_data/ 目录不存在！")
        print("   请先运行: python daka.py --login")
        sys.exit(1)

    # 创建临时压缩包
    temp_file = os.path.join(tempfile.gettempdir(), "swun_cookies.zip")

    # 删除旧文件
    if os.path.exists(temp_file):
        os.remove(temp_file)

    shutil.make_archive(
        os.path.join(tempfile.gettempdir(), "swun_cookies"),
        'zip',
        browser_data_dir
    )

    # 读取并编码
    with open(temp_file, 'rb') as f:
        data = f.read()

    encoded = base64.b64encode(data).decode('ascii')

    print(f"✅ 已导出 Cookie 数据（{len(data)} 字节 → {len(encoded)} 字符 base64）")
    print()
    print("=" * 50)
    print("📋 请将以下内容复制到 GitHub Secrets:")
    print("   名称: SWUN_COOKIES")
    print("   值: (下面的 base64 字符串)")
    print("=" * 50)
    print()
    print(encoded[:500] + "...")
    print()
    print(f"完整内容共 {len(encoded)} 字符，已保存到 swun_cookies_base64.txt")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "swun_cookies_base64.txt"), "w") as f:
        f.write(encoded)

    # 清理临时文件
    os.remove(temp_file)

    print("📁 文件: swun_cookies_base64.txt (请勿提交到 Git！)")


if __name__ == "__main__":
    export_cookies_from_playwright()
