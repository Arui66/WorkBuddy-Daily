#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 WorkBuddy 短信验证码登录工具
════════════════════════════════════════════════════════════════
输入手机号 → 自动发送验证码 → 输入收到的验证码 → 输出 AT + RT

用法:
  python workbuddy_login.py                    # 交互式登录
  python workbuddy_login.py 13800000000        # 指定手机号
  python workbuddy_login.py 13800000000 123456 # 指定手机号和验证码

输出格式（可直接用于 WORKBUDDY_REFRESH_TOKEN 环境变量）:
  手机号:AT:RT
"""
import sys, os, json, re, time, base64, datetime
from urllib.parse import urlparse, parse_qs, urlencode
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except Exception:
    pass

BASE = "https://www.workbuddy.cn"
AUTH_URL = BASE + "/auth/realms/copilot/protocol/openid-connect/auth"
TOKEN_URL = BASE + "/auth/realms/copilot/protocol/openid-connect/token"
SMS_URL = BASE + "/auth/realms/copilot/sms/authentication-code"
REDIRECT_URI = BASE + "/console/accounts/.apisix/redirect"
CLIENT_ID = "console"


def login(phone, sms_code=None):
    """完整登录流程"""
    s = requests.Session()
    s.trust_env = False
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.251 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })

    # ── Step 1: GET 认证URL → 获取登录页 + 会话Cookie ──
    print("[1/5] 获取登录页面...")
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile offline_access",
        "state": "wb" + str(int(time.time())),
    }
    r = s.get(AUTH_URL, params=params, timeout=20, verify=False)
    if r.status_code != 200:
        print("  ❌ 获取登录页失败: HTTP %s" % r.status_code)
        return None

    html = r.text

    # 提取表单 action URL（含 session_code/execution 等参数）
    form_match = re.search(r'<form[^>]*action="([^"]*)"', html)
    if not form_match:
        print("  ❌ 未找到登录表单")
        return None
    action_url = form_match.group(1).replace("&amp;", "&")
    print("  ✅ 登录页获取成功")

    # ── Step 2: 发送短信验证码 ──
    if not sms_code:
        print("[2/5] 发送短信验证码到 %s ..." % phone)
        sms_url = BASE + "/auth/realms/copilot/sms/authentication-code"
        r2 = s.get(sms_url, params={"phoneNumber": phone}, timeout=20, verify=False)
        try:
            d2 = r2.json()
            print("  ✅ 验证码已发送 (有效期 %s 秒)" % d2.get("expires_in", "?"))
        except Exception:
            print("  ⚠️ SMS 响应: HTTP %s" % r2.status_code)
        sms_code = input("  📱 请输入收到的验证码: ").strip()
        if not sms_code:
            print("  ❌ 验证码不能为空")
            return None
    else:
        print("[2/5] 使用提供的验证码")

    # ── Step 3: 提交登录表单 ──
    print("[3/5] 提交登录...")

    # 构建完整的表单字段（照抄登录页的所有input）
    form_data = {}

    # 提取所有隐藏字段并添加（跳过 Vue.js 表达式）
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*(?:value="([^"]*)")?', html):
        name, value = m.group(1), m.group(2) or ""
        # 跳过 Vue.js 模板表达式（JS 代码）
        if "startsWith" in value or "{{" in value or "v-model" in value:
            # phoneNumber hidden field: 值应该是实际手机号
            if name == "phoneNumber":
                form_data[name] = phone
            continue
        if name and value:
            form_data[name] = value

    # 设置登录凭据字段
    form_data["phoneNumber"] = phone
    form_data["code"] = sms_code
    form_data["credentialId"] = ""
    form_data["login"] = "登录"

    # 提交（不自动跟随重定向，捕获授权码）
    r3 = s.post(action_url, data=form_data, timeout=30, verify=False, allow_redirects=False)

    # 跟随重定向链，捕获 authorization code
    code = _follow_redirects_for_code(s, r3, action_url)

    if not code:
        # 调试：输出响应内容帮助诊断
        print("  ❌ 未获取到授权码")
        if r3.status_code == 200:
            # 检查是否是验证码错误
            err_match = re.search(r'(?i)(?:invalid|error|错误|无效|expired|过期)[^<]{0,80}', r3.text)
            if err_match:
                print("  💡 服务端提示: %s" % err_match.group(0)[:80])
            # 检查是否需要二次验证
            if "otp" in r3.text.lower() or "totp" in r3.text.lower():
                print("  💡 服务端要求 OTP 二次验证")
        print("  💡 响应状态: HTTP %s" % r3.status_code)
        return None

    print("  ✅ 授权码获取成功!")

    # ── Step 4: 用授权码换取 Token ──
    print("[4/5] 交换 Token...")
    token_data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    r4 = s.post(TOKEN_URL, data=token_data, timeout=20, verify=False)
    try:
        d4 = r4.json()
    except Exception:
        print("  ❌ Token 交换失败: HTTP %s" % r4.status_code)
        return None

    if "access_token" not in d4:
        print("  ❌ Token 交换失败: %s" % json.dumps(d4, ensure_ascii=False)[:200])
        return None

    at = d4["access_token"]
    rt = d4.get("refresh_token", "")

    # 解析身份
    try:
        pay = at.split(".")[1]; pay += "=" * (4 - len(pay) % 4)
        j = json.loads(base64.urlsafe_b64decode(pay))
        username = j.get("preferred_username", phone)
        exp = datetime.datetime.fromtimestamp(j.get("exp", 0)).strftime("%Y-%m-%d")
    except Exception:
        username = phone
        exp = "?"

    print("  ✅ 登录成功! 身份: %s | AT过期: %s" % (username, exp))

    # ── Step 5: 输出 ──
    print("[5/5] 完成!")
    env_line = "%s:%s:%s" % (phone, at, rt)
    print("\n" + "═" * 60)
    print("✅ 将下面的值追加到 WORKBUDDY_REFRESH_TOKEN 变量")
    print("═" * 60)
    print(env_line)
    print("═" * 60)
    return {"phone": phone, "access_token": at, "refresh_token": rt, "env_line": env_line}


def _follow_redirects_for_code(s, resp, base_url):
    """跟随重定向链，捕获 authorization code"""
    code = None
    current_url = base_url
    max_redirects = 15

    for _ in range(max_redirects):
        # 检查当前响应的 Location 头
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("Location", "")
            if not loc:
                break
            # 解析 URL 中的 code 参数
            parsed = urlparse(loc)
            qs = parse_qs(parsed.query)
            if "code" in qs:
                code = qs["code"][0]
                break
            # 相对路径转绝对路径
            if loc.startswith("/"):
                p = urlparse(current_url)
                loc = p.scheme + "://" + p.netloc + loc
            # 跟随重定向
            try:
                resp = s.get(loc, timeout=20, verify=False, allow_redirects=False)
                current_url = loc
            except Exception:
                break
        elif resp.status_code == 200:
            # 检查页面内容中是否有重定向 JS
            js_match = re.search(r'window\.location\s*=\s*["\']([^"\']+)["\']', resp.text)
            if js_match:
                loc = js_match.group(1)
                parsed = urlparse(loc)
                qs = parse_qs(parsed.query)
                if "code" in qs:
                    code = qs["code"][0]
                    break
            break

    return code


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║ 🔐 WorkBuddy 短信验证码登录工具               ║")
    print("║ 输入手机号 → 收验证码 → 获取 Token            ║")
    print("╚══════════════════════════════════════════════╝")

    args = sys.argv[1:]
    phone = args[0] if len(args) > 0 else ""
    sms_code = args[1] if len(args) > 1 else None

    if not phone:
        phone = input("📱 请输入手机号: ").strip()
    if not phone:
        print("❌ 手机号不能为空")
        return

    result = login(phone, sms_code)
    if result:
        save_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wb_login_result.json")
        results = []
        if os.path.exists(save_file):
            try:
                results = json.load(open(save_file, encoding="utf-8"))
            except Exception:
                results = []
        results.append(result)
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        print("📁 结果已保存到: %s" % save_file)
    else:
        print("\n❌ 登录失败")


if __name__ == "__main__":
    main()
