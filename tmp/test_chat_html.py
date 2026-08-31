"""
Focused Chat HTML Stripping Smoke Test
Tests the html.unescape() fix in strip_html()
"""
import requests
import json

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
    "body": "Plain text message for baseline test"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  PASS: Body = '{body}'")
    if "<" in body:
        print(f"  FAIL: Contains angle brackets")
    else:
        print(f"  OK: No angle brackets")
else:
    print(f"  FAIL: {resp.status_code}")

# T3: Send HTML tags (real HTML)
print("\n--- T3: Send real HTML tags ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "<p>Hello <b>world</b></p>"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Stored body = '{body}'")
    # Odoo wraps in <p>...</p> and stores, so strip_html should remove outer tags
    has_real_html = any(tag in body for tag in ["<p>", "<b>", "<br", "<div>"])
    if has_real_html:
        print(f"  FAIL: Response still contains HTML tags: {body[:200]}")
    else:
        print(f"  PASS: HTML tags stripped in response")
else:
    print(f"  FAIL: {resp.status_code}")

# T4: Send HTML entities (the actual bug)
print("\n--- T4: Send HTML entities (the actual bug) ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "Tom &amp; Jerry &lt;best friends&gt;"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Stored body = '{body}'")
    if "&amp;" in body or "&lt;" in body or "&gt;" in body:
        print(f"  FAIL: HTML entities NOT decoded: {body}")
    elif "&" in body and "amp" not in body:
        print(f"  FAIL: Entities partially decoded: {body}")
    else:
        print(f"  PASS: HTML entities decoded to plain text")
else:
    print(f"  FAIL: {resp.status_code}")

# T5: Send complex HTML with entities
print("\n--- T5: Send complex HTML+entities ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "&lt;script&gt;alert('xss')&lt;/script&gt; &amp; <b>bold</b>"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Stored body = '{body}'")
    has_html = any(tag in body for tag in ["<script>", "<b>", "<p>"])
    has_entities = any(ent in body for ent in ["&lt;", "&gt;", "&amp;"])
    if has_entities:
        print(f"  FAIL: HTML entities still present: {body}")
    elif has_html:
        print(f"  FAIL: HTML tags still present: {body}")
    else:
        print(f"  PASS: Fully cleaned to plain text")
else:
    print(f"  FAIL: {resp.status_code}")

# T6: Verify old messages also stripped on retrieval
print("\n--- T6: Retrieve all messages, verify no HTML anywhere ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
data = resp.json()
msgs = data.get("messages", [])
print(f"  Total messages: {len(msgs)}")
all_clean = True
for m in msgs:
    body = m.get("body", "")
    has_html = any(tag in body for tag in ["<p>", "<b>", "<br", "<div>", "<script>"])
    has_entities = any(ent in body for ent in ["&lt;", "&gt;", "&amp;", "&nbsp;"])
    if has_html:
        print(f"  FAIL: msg id={m['id']} has HTML tags: {body[:100]}")
        all_clean = False
    elif has_entities:
        print(f"  FAIL: msg id={m['id']} has HTML entities: {body[:100]}")
        all_clean = False
if all_clean and msgs:
    print(f"  PASS: All {len(msgs)} messages are clean plain text")

# T7: Send Unicode + entities
print("\n--- T7: Send Unicode with entities ---")
resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
    "body": "مرحبا &lt;أحمد&gt; &amp; سعيد"
})
data = resp.json()
if resp.status_code in [200, 201] and data.get("message"):
    body = data["message"]["body"]
    print(f"  Stored body = '{body}'")
    if "&lt;" in body or "&amp;" in body:
        print(f"  FAIL: Entities not decoded: {body}")
    else:
        print(f"  PASS: Unicode + entities handled correctly")
else:
    print(f"  FAIL: {resp.status_code}")

print("\n" + "=" * 60)
print("CHAT HTML STRIPPING SMOKE TEST COMPLETE")
print("=" * 60)
