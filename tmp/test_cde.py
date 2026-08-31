"""
SANAD Smoke Tests C, D, E - run separately
"""
import requests
import json

BASE = "http://localhost:8069"

def login(login, password):
    s = requests.Session()
    resp = s.post(f"{BASE}/api/auth/login", json={"login": login, "password": password})
    return s, resp

def pretty(resp):
    print(f"  HTTP {resp.status_code}")
    try:
        data = resp.json()
        print(f"  Body: {json.dumps(data, indent=4, default=str)[:1000]}")
        return data
    except:
        print(f"  Raw: {resp.text[:500]}")
        return None

doctor_session, _ = login("ahmed.benali@test.sanad", "demo1234")
pharmacy_session, _ = login("pharmacy.test@sanad.local", "demo1234")

# ══════════════════════════════════════════════════════════════
# TEST C: PHARMACY
# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST C: PHARMACY")
print("=" * 60)

print("\n--- C1: GET /api/pharmacies (doctor session) ---")
resp = doctor_session.get(f"{BASE}/api/pharmacies")
data = pretty(resp)
if resp.status_code == 200 and data and data.get("pharmacies"):
    print(f"  PASS: {len(data['pharmacies'])} pharmacies returned")
    for p in data["pharmacies"]:
        print(f"    id={p['id']} name={p['name']}")
else:
    print(f"  FAIL: Could not list pharmacies")

print("\n--- C2: GET /api/pharmacies (pharmacy session) ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacies")
data = pretty(resp)
if resp.status_code == 200 and data and data.get("pharmacies"):
    print(f"  PASS: {len(data['pharmacies'])} pharmacies returned")
else:
    print(f"  FAIL: Status {resp.status_code}")

print("\n--- C3: Pharmacy lists prescriptions ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacy/prescriptions")
data = pretty(resp)
if resp.status_code == 200 and data and data.get("prescriptions"):
    rx_list = data["prescriptions"]
    print(f"  PASS: {len(rx_list)} prescriptions visible to pharmacy")
    found_28 = [p for p in rx_list if p.get("id") == 28]
    found_29 = [p for p in rx_list if p.get("id") == 29]
    if found_28:
        print(f"  PASS: Prescription id=28 (pharmacy_id=1) IS visible to pharmacy")
    else:
        print(f"  FAIL: Prescription id=28 (pharmacy_id=1) is NOT visible to pharmacy")
    if found_29:
        print(f"  NOTE: Prescription id=29 (pharmacy_id=None) IS visible to pharmacy")
    else:
        print(f"  INFO: Prescription id=29 (pharmacy_id=None) is NOT visible to pharmacy")
else:
    print(f"  FAIL: Status {resp.status_code}")

print("\n--- C4: Verify pharmacy_id via API ---")
resp = doctor_session.get(f"{BASE}/api/prescriptions")
data = resp.json()
for p in data.get("prescriptions", []):
    if p["id"] == 28:
        print(f"  RX#28: pharmacy_id={p.get('pharmacy_id')}")
        if p.get("pharmacy_id") == 1:
            print(f"  PASS: pharmacy_id correctly set to 1")
        else:
            print(f"  FAIL: pharmacy_id expected 1, got {p.get('pharmacy_id')}")
        break

print("\n--- C5: Pharmacy records rule - check which prescriptions visible ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacy/prescriptions")
data = resp.json()
rx_ids = [p["id"] for p in data.get("prescriptions", [])]
print(f"  Pharmacy can see prescription IDs: {rx_ids}")
if not rx_ids:
    print(f"  WARNING: Pharmacy sees ZERO prescriptions - record rules may be blocking")
    print(f"  This may be because pharmacy orgs have empty user_ids")


# ══════════════════════════════════════════════════════════════
# TEST E: CHAT
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TEST E: CHAT")
print("=" * 60)

print("\n--- E1: Doctor lists conversations ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations")
data = pretty(resp)
conv_id = None
if resp.status_code == 200 and data and data.get("conversations"):
    print(f"  PASS: {len(data['conversations'])} conversations found")
    if data["conversations"]:
        conv_id = data["conversations"][0]["id"]
        print(f"  Using conversation_id={conv_id}")
else:
    print(f"  INFO: No conversations found")

if not conv_id:
    print("\n--- E1b: Create a conversation (doctor -> patient) ---")
    resp = doctor_session.post(f"{BASE}/api/chat/conversations", json={
        "other_user_id": 8,
        "conversation_type": "doctor_patient"
    })
    data = pretty(resp)
    if resp.status_code in [200, 201] and data:
        conv = data.get("conversation", data)
        conv_id = conv.get("id")
        if conv_id:
            print(f"  PASS: Conversation created, id={conv_id}")
        else:
            print(f"  Response: {json.dumps(data, default=str)[:500]}")
    else:
        print(f"  FAIL: Could not create conversation")

print("\n--- E2: List messages ---")
if conv_id:
    resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
    data = pretty(resp)
    if resp.status_code == 200 and data is not None:
        msgs = data.get("messages", [])
        print(f"  PASS: {len(msgs)} messages in conversation")
        for m in msgs:
            body = m.get("body", "")
            has_html = any(tag in body for tag in ["<p>", "<br", "<div>", "<script>", "<b>"])
            if has_html:
                print(f"  FAIL: Message id={m['id']} has HTML: {body[:120]}")
            elif body:
                print(f"  OK: id={m['id']} body={body[:80]}")
else:
    print("  SKIP: No conversation available")

print("\n--- E3: Send a message ---")
msg_id = None
if conv_id:
    resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
        "body": "Hello from smoke test - testing HTML stripping"
    })
    data = pretty(resp)
    if resp.status_code in [200, 201] and data and data.get("message"):
        msg_id = data["message"]["id"]
        print(f"  PASS: Message sent, id={msg_id}")
        body = data["message"].get("body", "")
        has_html = any(tag in body for tag in ["<p>", "<br", "<div>", "<script>", "<b>"])
        if has_html:
            print(f"  FAIL: Response contains HTML: {body[:200]}")
        else:
            print(f"  OK: Plain text response: {body[:100]}")
    else:
        print(f"  FAIL: Could not send message")

print("\n--- E4: Send HTML message, verify stripping ---")
if conv_id:
    html_msg = "<p>This is <b>bold</b> and <script>alert('xss')</script> text</p>"
    resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
        "body": html_msg
    })
    data = pretty(resp)
    if resp.status_code in [200, 201] and data and data.get("message"):
        body = data["message"].get("body", "")
        has_html = any(tag in body for tag in ["<p>", "<br", "<div>", "<script>", "<b>"])
        if has_html:
            print(f"  FAIL: HTML NOT stripped in response: {body[:200]}")
        else:
            print(f"  PASS: HTML stripped in response: {body[:200]}")

    # Retrieve and check
    resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    html_found = False
    for m in msgs:
        body = m.get("body", "")
        if any(tag in body for tag in ["<p>", "<br", "<div>", "<script>", "<b>"]):
            html_found = True
            print(f"  FAIL: Message id={m['id']} has HTML: {body[:120]}")
    if not html_found and msgs:
        print(f"  PASS: All {len(msgs)} messages are plain text (HTML stripped)")

print("\n--- E5: Verify persistence ---")
if conv_id:
    resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    found_test = [m for m in msgs if "smoke test" in m.get("body", "").lower()]
    found_html = [m for m in msgs if "bold" in m.get("body", "").lower() or "alert" in m.get("body", "").lower()]
    print(f"  Messages with 'smoke test': {len(found_test)}")
    print(f"  Messages with 'bold'/'alert': {len(found_html)}")
    if len(found_test) > 0:
        print(f"  PASS: Plain text message persisted")
    if len(found_html) > 0:
        all_clean = all("<" not in m.get("body", "") for m in found_html)
        if all_clean:
            print(f"  PASS: HTML message persisted as plain text")
        else:
            print(f"  FAIL: HTML persisted with tags")
    if len(found_test) == 0 and len(found_html) == 0:
        print(f"  INFO: No test messages found in conversation")

# ══════════════════════════════════════════════════════════════
# TEST D: NOTIFICATIONS (API-level)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TEST D: NOTIFICATIONS (API-level)")
print("=" * 60)

print("\n--- D1: Check notification-related endpoints ---")
for endpoint in ["/api/chat/conversations", "/api/chat/unseen", "/api/notifications"]:
    resp = doctor_session.get(f"{BASE}{endpoint}")
    status = resp.status_code
    print(f"  GET {endpoint}: HTTP {status}")
    if status == 200:
        try:
            d = resp.json()
            print(f"    Keys: {list(d.keys()) if isinstance(d, dict) else type(d).__name__}")
        except:
            pass

print("\n  NOTE: NotificationBell.jsx changes are UI-only:")
print("  - Click-outside-to-close: requires browser DOM events")
print("  - Navigate-away-to-close: requires React router integration")
print("  - Max-height overflow: requires CSS rendering check")
print("  These CANNOT be verified via API calls alone.")

print("\n" + "=" * 60)
print("ALL SMOKE TESTS COMPLETE")
print("=" * 60)
