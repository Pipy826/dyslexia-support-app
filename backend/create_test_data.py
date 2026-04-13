# -*- coding: utf-8 -*-
"""创建测试数据脚本"""
import urllib.request
import json

BASE = "http://localhost:8000"

def api(path, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"  HTTP {e.code}: {err}")
        return None

print("=== 创建测试数据 ===\n")

# 1. 注册账号
print("1. 注册账号...")
accounts = [
    {"username": "test", "password": "test123456"},
    {"username": "demo", "password": "demo123456"},
]
for acc in accounts:
    res = api("/api/auth/register", "POST", acc)
    if res:
        print(f"   ✓ 注册成功: {acc['username']}")
    else:
        print(f"   - 账号已存在: {acc['username']}")

# 2. 登录 test 账号
print("\n2. 登录 test 账号...")
res = api("/api/auth/login", "POST", {"username": "test", "password": "test123456"})
token = res["access_token"]
print(f"   ✓ 登录成功")

# 3. 清理旧档案
print("\n3. 清理旧档案...")
children = api("/api/children/", token=token)
for c in (children if isinstance(children, list) else []):
    api(f"/api/children/{c['id']}", "DELETE", token=token)
    print(f"   删除旧档案 ID={c['id']}")

# 4. 创建儿童档案
print("\n4. 创建儿童档案...")
child = api("/api/children/", "POST", {
    "name": "小明",
    "gender": "male",
    "birth_date": "2017-03-15",
    "grade": "2",
    "has_difficulty": False
}, token=token)
if child:
    print(f"   ✓ 档案创建成功: {child['name']}, ID={child['id']}")
    child_id = child["id"]
else:
    print("   ✗ 档案创建失败")
    exit(1)

print("\n=== 测试账号信息 ===")
print("账号1: test / test123456  (已有儿童档案：小明)")
print("账号2: demo / demo123456  (空账号，可自行创建档案)")
print("\n后端地址: http://localhost:8000")
print("API文档:  http://localhost:8000/docs")
