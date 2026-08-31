"""
Focused Chat HTML Stripping Smoke Test
Tests the html.unescape() fix in strip_html()
"""
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8069"

def login(login, password):
    s = requests.Session()
    resp = s.post(f"{BASE}/api/auth/login", json={"login": login, "password": password})
    return s, resp

doctor_session, _ = login("ahmed.benali@test.sanad", "demo1234")

print("=" * 60)
print("CHAT HTML STRIPPING SMOKE TEST")
print("=" * 60)

# Get existing conversation
print("\n--- T1: Get conversation ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations")
data = resp.json()
conv_id = data["conversations"][0]["id"]
print(f"  Using conversation_id={conv_id}")

# T2: Send plain text (baseline)
print("\n--- T2: Send plain text message ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "Plain text message for baseline test 2"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Body = '{body}'")
    if "<" in body or "&" in body:
        print(f"  FAIL: Contains HTML or entities")
    else:
        print(f"  PASS: Clean plain text")
else:
    print(f"  FAIL: {resp.status_code}")

# T3: Send real HTML tags (user types HTML in chat)
print("\n--- T3: Send real HTML tags ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "<p>Hello <b>world</b></p>"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Body = '{body}'")
    has_real_html = any(tag in body for tag in ["<p>", "<b>", "<br", "<div>"])
    if has_real_html:
        print(f"  FAIL: Still contains HTML tags")
    else:
        print(f"  PASS: HTML tags stripped")
else:
    print(f"  FAIL: {resp.status_code}")

# T4: Send text with & (real-world usage - user types ampersand)
print("\n--- T4: Send text with ampersand (real-world) ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "Tom & Jerry love cartoons"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Body = '{body}'")
    if "&amp;" in body:
        print(f"  FAIL: ampersand not decoded: {body}")
    elif body == "Tom & Jerry love cartoons":
        print(f"  PASS: Ampersand correctly decoded")
    else:
        print(f"  UNEXPECTED: {body}")
else:
    print(f"  FAIL: {resp.status_code}")

# T5: Send text with < character (real-world usage)
print("\n--- T5: Send text with less-than (real-world) ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "3 < 5 and 5 > 3"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Body = '{body}'")
    if "&lt;" in body:
        print(f"  FAIL: less-than not decoded: {body}")
    elif body == "3 < 5 and 5 > 3":
        print(f"  PASS: Comparison operators displayed correctly")
    else:
        print(f"  UNEXPECTED: {body}")
else:
    print(f"  FAIL: {resp.status_code}")

# T6: Send HTML script tag (XSS attempt)
print("\n--- T6: Send HTML script tag (XSS attempt) ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "<script>alert('xss')</script>"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Body = '{body}'")
    if "<script>" in body:
        print(f"  FAIL: Script tag NOT stripped")
    elif body == "alert('xss')":
        print(f"  PASS: Script tag stripped, text preserved")
    else:
        print(f"  Result: {body}")
else:
    print(f"  FAIL: {resp.status_code}")

# T7: Retrieve all messages and check
print("\n--- T7: Retrieve all messages, verify no HTML ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
data = resp.json()
msgs = data.get("messages", [])
print(f"  Total messages: {len(msgs)}")
all_clean = True
for m in msgs:
    body = m.get("body", "")
    has_html = any(tag in body for tag in ["<p>", "<b>", "<br", "<div>", "<script>"])
    has_entities = any(ent in body for ent in ["&lt;", "&gt;", "&amp;"])
    if has_html:
        print(f"  FAIL: msg id={m['id']} has HTML: {body[:100]}")
        all_clean = False
    elif has_entities:
        print(f"  FAIL: msg id={m['id']} has entities: {body[:100]}")
        all_clean = False
if all_clean and msgs:
    print(f"  PASS: All {len(msgs)} messages are clean plain text")

print("\n" + "=" * 60)
print("CHAT HTML STRIPPING SMOKE TEST COMPLETE")
print("=" * 60)
