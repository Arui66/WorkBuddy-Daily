#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 WorkBuddy 短信验证码登录工具
════════════════════════════════════════════════════════════════
输入手机号 → 自动发送验证码 → 输入收到的验证码 → 输出 AT + RT

用法:
  python workbuddy_login.py                    # 交互式登录
  python workbuddy_login.py 13800000000        # 指定手机号
  python workbuddy_login.py 13800000000 123456 # 指定手机号和验证码（跳过等待）

输出格式（可直接用于 WORKBUDDY_REFRESH_TOKEN 环境变量）:
  手机号:AT:RT
"""
import sys, os, json, re, time, base64, datetime
import requests
from urllib.parse import urlparse, parse_qs, urlencode

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
    """完整登录流程：获取会话 → 发送验证码 → 提交登录 → 换取Token"""
    s = requests.Session()
    s.trust_env = False
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.251 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })

    # ── 第一步：获取登录页面（建立会话） ──
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

    # 提取表单 action URL 和隐藏字段
    form_match = re.search(r'<form[^>]*action="([^"]*)"', r.text)
    if not form_match:
        print("  ❌ 未找到登录表单")
        return None
    action_url = form_match.group(1).replace("&amp;", "&")

    # 提取所有隐藏字段（Keycloak 的 session 相关参数）
    hidden = {}
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"', r.text):
        name, value = m.group(1), m.group(2)
        # 跳过 Vue.js 模板表达式
        if "startsWith" in value or "{{" in value:
            continue
        hidden[name] = value

    print("  ✅ 登录页获取成功 (会话: %s)" % dict(s.cookies).get("AUTH_SESSION_ID", "?")[:20])

    # ── 第二步：发送短信验证码 ──
    if not sms_code:
        print("[2/5] 发送短信验证码到 %s ..." % phone)
        sms_url = BASE + "/auth/realms/copilot/sms/authentication-code"
        r2 = s.get(sms_url, params={"phoneNumber": phone}, timeout=20, verify=False)
        try:
            d2 = r2.json()
            expires = d2.get("expires_in", 300)
            print("  ✅ 验证码已发送 (有效期 %s 秒)" % expires)
        except Exception:
            print("  ⚠️ SMS响应: HTTP %s %s" % (r2.status_code, r2.text[:100]))
        # 等待用户输入验证码
        sms_code = input("  📱 请输入收到的验证码: ").strip()
        if not sms_code:
            print("  ❌ 验证码不能为空")
            return None
    else:
        print("[2/5] 使用命令行提供的验证码")

    # ── 第三步：提交登录表单 ──
    print("[3/5] 提交登录...")
    form_data = dict(hidden)
    form_data["phoneNumber"] = phone
    form_data["code"] = sms_code

    # 不自动跟随重定向，需要捕获 authorization code
    r3 = s.post(action_url, data=form_data, timeout=30, verify=False, allow_redirects=False)

    # 跟随重定向链，捕获 authorization code
    code = None
    redirect_count = 0
    current_url = r3.headers.get("Location", "")
    current_resp = r3

    while redirect_count < 15:
        if r3.status_code in (301, 302, 303, 307, 308):
            loc = r3.headers.get("Location", "")
            if not loc:
                break
            # 检查重定向URL中是否有 code 参数
            parsed = urlparse(loc)
            qs = parse_qs(parsed.query)
            if "code" in qs:
                code = qs["code"][0]
                print("  ✅ 获取到授权码!")
                break
            # 跟随重定向
            if loc.startswith("/"):
                parsed_base = urlparse(current_url if current_url else BASE)
                loc = parsed_base.scheme + "://" + parsed_base.netloc + loc
            try:
                r3 = s.get(loc, timeout=20, verify=False, allow_redirects=False)
                current_url = loc
                redirect_count += 1
            except Exception:
                break
        elif r3.status_code == 200:
            # 检查页面中是否有错误信息
            if "验证码" in r3.text and ("错误" in r3.text or "无效" in r3.text or "expired" in r3.text.lower()):
                print("  ❌ 验证码错误或已过期")
                return None
            if "errorMessage" in r3.text:
                err_match = re.search(r'errorMessage["\s:]+["\']([^"\']+)', r3.text)
                if err_match:
                    print("  ❌ 登录错误: %s" % err_match.group(1)[:80])
                    return None
            break
        else:
            print("  ⚠️ HTTP %s" % r3.status_code)
            break

    if not code:
        # 尝试从最终页面的 URL 或内容中提取
        print("  ❌ 未获取到授权码")
        print("  💡 可能原因: 验证码错误、账号未注册、或登录流程变更")
        return None

    # ── 第四步：用授权码换取 Token ──
    print("[4/5] 交换 Token...")
    # 获取新的 session（token 请求可能需要）
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
        print("  ❌ Token 交换失败: HTTP %s %s" % (r4.status_code, r4.text[:100]))
        return None

    if "access_token" not in d4:
        print("  ❌ Token 交换失败: %s" % json.dumps(d4, ensure_ascii=False)[:200])
        return None

    at = d4["access_token"]
    rt = d4.get("refresh_token", "")

    # 解析身份信息
    try:
        pay = at.split(".")[1]; pay += "=" * (4 - len(pay) % 4)
        j = json.loads(base64.urlsafe_b64decode(pay))
        username = j.get("preferred_username", phone)
        exp = j.get("exp", 0)
        exp_str = datetime.datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")
    except Exception:
        username = phone
        exp_str = "?"

    print("  ✅ 登录成功! 身份: %s | AT过期: %s" % (username, exp_str))

    # ── 第五步：输出结果 ──
    print("[5/5] 生成环境变量...")
    line = "%s:%s:%s" % (phone, at, rt)
    print("\n" + "═" * 60)
    print("✅ 登录成功！将下面的值追加到 WORKBUDDY_REFRESH_TOKEN 变量")
    print("════════════════════════════════════════════════════════════════")
    print(line)
    print("════════════════════════════════════════════════════════════════")
    return {"phone": phone, "access_token": at, "refresh_token": rt, "env_line": line}


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║ 🔐 WorkBuddy 短信验证码登录工具               ║")
    print("║ 输入手机号 → 收验证码 → 获取 Token            ║")
    print("╚══════════════════════════════════════════════╝")

    # 解析参数
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
        # 保存到文件
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
        print("\n❌ 登录失败，请检查手机号和验证码")


if __name__ == "__main__":
    main()
