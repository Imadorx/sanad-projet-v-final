"""
SANAD Full Smoke Test - Tests B, C, D, E
"""
import requests
import json
import time

BASE = "http://localhost:8069"

# ── Helpers ────────────────────────────────────────────────────
def login(login, password):
    s = requests.Session()
    resp = s.post(f"{BASE}/api/auth/login", json={"login": login, "password": password})
    return s, resp

def pretty(label, resp):
    print(f"  HTTP {resp.status_code}")
    try:
        data = resp.json()
        print(f"  Body: {json.dumps(data, indent=4, default=str)[:1000]}")
        return data
    except:
        print(f"  Raw: {resp.text[:500]}")
        return None

# ── Login sessions ─────────────────────────────────────────────
doctor_session, _ = login("ahmed.benali@test.sanad", "demo1234")
pharmacy_session, _ = login("pharmacy.test@sanad.local", "demo1234")

# ══════════════════════════════════════════════════════════════
# TEST B: PRESCRIPTION
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TEST B: PRESCRIPTION")
print("=" * 60)

# B1: Get patients list (doctor needs to know patient IDs)
print("\n--- B1: Doctor lists patients ---")
resp = doctor_session.get(f"{BASE}/api/patients")
patients_data = pretty("Doctor lists patients", resp)
patient_id = None
if patients_data and patients_data.get("patients"):
    patient_id = patients_data["patients"][0]["id"]
    print(f"  Using patient_id={patient_id} ({patients_data['patients'][0].get('name', 'unknown')})")
else:
    print("  FATAL: No patients found!")
    # Try to create one
    print("  Attempting to create a test patient...")
    resp = doctor_session.post(f"{BASE}/api/patients", json={
        "name": "Smoke Test Patient",
        "user_id": 8,  # patient.test@sanad.local
    })
    data = pretty("Create test patient", resp)
    if data and data.get("patient"):
        patient_id = data["patient"]["id"]
        print(f"  Created patient_id={patient_id}")
    else:
        print("  FAIL: Cannot create patient. Aborting prescription tests.")

# B2: Create prescription WITHOUT doctor_id (auto-detect test)
print("\n--- B2: Create prescription (no doctor_id, should auto-detect) ---")
rx_payload = {
    "patient_id": patient_id,
    "medication": "Amoxicillin 500mg",
    "dosage": "500mg",
    "frequency": "3 times daily",
    "duration": "7 days",
    "instructions": "Take with food",
    "pharmacy_id": 1,  # Pharmacy Test
}
print(f"  Payload: {json.dumps(rx_payload, default=str)}")
resp = doctor_session.post(f"{BASE}/api/prescriptions", json=rx_payload)
rx_data = pretty("Create prescription (no doctor_id)", resp)
rx_id = None
if resp.status_code == 201 and rx_data and rx_data.get("prescription"):
    rx_id = rx_data["prescription"]["id"]
    print(f"  PASS: Prescription created, id={rx_id}")
    print(f"  doctor_id on record: {rx_data['prescription'].get('doctor_id')}")
    print(f"  pharmacy_id on record: {rx_data['prescription'].get('pharmacy_id')}")
else:
    print(f"  FAIL: Prescription creation failed")

# B3: Create prescription WITH explicit doctor_id
print("\n--- B3: Create prescription (explicit doctor_id=2) ---")
rx_payload2 = {
    "patient_id": patient_id,
    "doctor_id": 2,
    "medication": "Ibuprofen 400mg",
    "dosage": "400mg",
    "frequency": "As needed",
    "duration": "5 days",
    "instructions": "Take after meals",
}
resp = doctor_session.post(f"{BASE}/api/prescriptions", json=rx_payload2)
rx_data2 = pretty("Create prescription (with doctor_id)", resp)
rx_id2 = None
if resp.status_code == 201 and rx_data2 and rx_data2.get("prescription"):
    rx_id2 = rx_data2["prescription"]["id"]
    print(f"  PASS: Prescription created, id={rx_id2}")
else:
    print(f"  FAIL: Prescription creation failed")

# B4: Create prescription with MISSING required fields
print("\n--- B4: Create prescription (missing required fields) ---")
resp = doctor_session.post(f"{BASE}/api/prescriptions", json={"patient_id": patient_id})
data = pretty("Create incomplete prescription", resp)
if resp.status_code in [400, 422]:
    print(f"  PASS: Correctly rejected with {resp.status_code}")
elif resp.status_code == 201:
    print(f"  NOTE: Server accepted incomplete data (status 201) - no validation on required fields")

# B5: List prescriptions (verify creation)
print("\n--- B5: List prescriptions ---")
resp = doctor_session.get(f"{BASE}/api/prescriptions")
data = pretty("List prescriptions", resp)
if data and data.get("prescriptions"):
    print(f"  Total prescriptions visible to doctor: {len(data['prescriptions'])}")
    found = [p for p in data["prescriptions"] if p.get("id") in [rx_id, rx_id2]]
    print(f"  Found our newly created: {[p['id'] for p in found]}")
else:
    print(f"  FAIL: Could not list prescriptions")

# B6: Verify in PostgreSQL
print("\n--- B6: Verify prescription in PostgreSQL ---")
import subprocess
verify_script = f"""
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {{}})
    if {rx_id}:
        p = env["sanad.prescription"].browse({rx_id})
        print(f"  id={p.id} medication={p.medication} doctor_id={p.doctor_id.id} pharmacy_id={p.pharmacy_id.id if p.pharmacy_id else 'None'} patient_id={p.patient_id.id} pharmacy_status={p.pharmacy_status}")
    if {rx_id2}:
        p2 = env["sanad.prescription"].browse({rx_id2})
        print(f"  id={p2.id} medication={p2.medication} doctor_id={p2.doctor_id.id} pharmacy_id={p2.pharmacy_id.id if p2.pharmacy_id else 'None'} patient_id={p2.patient_id.id} pharmacy_status={p2.pharmacy_status}")
    cr.commit()
"""
with open("C:/Users/HP/Desktop/SANAD_audited_backend/tmp/verify_rx.py", "w") as f:
    f.write(verify_script)
result = subprocess.run(["docker", "cp", "C:\\Users\\HP\\Desktop\\SANAD_audited_backend\\tmp\\verify_rx.py", "sanad_odoo:/tmp/verify_rx.py"], capture_output=True, text=True)
result2 = subprocess.run(["docker", "exec", "sanad_odoo", "python3", "/tmp/verify_rx.py"], capture_output=True, text=True, timeout=30)
print(f"  {result2.stdout.strip()}")
if result2.stderr.strip():
    # Filter out WARNING lines
    for line in result2.stderr.strip().split('\n'):
        if 'ERROR' in line or 'Traceback' in line:
            print(f"  ERR: {line}")


# ══════════════════════════════════════════════════════════════
# TEST C: PHARMACY
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TEST C: PHARMACY")
print("=" * 60)

# C1: GET /api/pharmacies (doctor session)
print("\n--- C1: GET /api/pharmacies (doctor session) ---")
resp = doctor_session.get(f"{BASE}/api/pharmacies")
data = pretty("GET /api/pharmacies", resp)
if resp.status_code == 200 and data and data.get("pharmacies"):
    print(f"  PASS: {len(data['pharmacies'])} pharmacies returned")
    for p in data["pharmacies"]:
        print(f"    id={p['id']} name={p['name']}")
else:
    print(f"  FAIL: Could not list pharmacies")

# C2: GET /api/pharmacies (pharmacy session)
print("\n--- C2: GET /api/pharmacies (pharmacy session) ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacies")
data = pretty("GET /api/pharmacies (pharmacy user)", resp)
if resp.status_code == 200 and data and data.get("pharmacies"):
    print(f"  PASS: {len(data['pharmacies'])} pharmacies returned")
else:
    print(f"  FAIL: Status {resp.status_code}")

# C3: Pharmacy dashboard - list prescriptions
print("\n--- C3: Pharmacy lists prescriptions ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacy/prescriptions")
data = pretty("Pharmacy lists prescriptions", resp)
if resp.status_code == 200 and data and data.get("prescriptions"):
    print(f"  PASS: {len(data['prescriptions'])} prescriptions visible to pharmacy")
    # Check if our prescription is there
    found = [p for p in data["prescriptions"] if p.get("id") == rx_id]
    if found:
        print(f"  PASS: Our prescription (id={rx_id}) IS visible to pharmacy")
    else:
        print(f"  FAIL: Our prescription (id={rx_id}) is NOT visible to pharmacy")
        print(f"  NOTE: This may be due to record rules - pharmacy_id.user_ids is empty")
else:
    print(f"  FAIL: Status {resp.status_code}")

# C4: Verify pharmacy_id on the prescription
print("\n--- C4: Verify pharmacy_id on prescription ---")
# Already shown in B6, but let's double check via API
if rx_id:
    # Check by listing prescriptions and finding ours
    resp = doctor_session.get(f"{BASE}/api/prescriptions")
    data = resp.json()
    for p in data.get("prescriptions", []):
        if p["id"] == rx_id:
            print(f"  Prescription id={rx_id}: pharmacy_id={p.get('pharmacy_id')}")
            if p.get("pharmacy_id"):
                print(f"  PASS: pharmacy_id is set to {p['pharmacy_id']}")
            else:
                print(f"  FAIL: pharmacy_id is None/missing")
            break


# ══════════════════════════════════════════════════════════════
# TEST E: CHAT  (doing before D since D is UI-only)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TEST E: CHAT")
print("=" * 60)

# E1: List conversations
print("\n--- E1: Doctor lists conversations ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations")
data = pretty("Doctor lists conversations", resp)
conv_id = None
if resp.status_code == 200 and data and data.get("conversations"):
    print(f"  PASS: {len(data['conversations'])} conversations found")
    conv_id = data["conversations"][0]["id"]
    print(f"  Using conversation_id={conv_id}")
else:
    print(f"  INFO: No conversations found (may need to create one)")

# E1b: Create a conversation if none exist
if not conv_id:
    print("\n--- E1b: Create a conversation (doctor -> patient) ---")
    resp = doctor_session.post(f"{BASE}/api/chat/conversations", json={
        "other_user_id": 8,  # patient.test@sanad.local
        "conversation_type": "doctor_patient"
    })
    data = pretty("Create conversation", resp)
    if resp.status_code in [200, 201] and data and data.get("conversation"):
        conv_id = data["conversation"]["id"]
        print(f"  PASS: Conversation created, id={conv_id}")
    else:
        print(f"  FAIL: Could not create conversation")

# E2: List messages
print("\n--- E2: List messages ---")
if conv_id:
    resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
    data = pretty("List messages", resp)
    if resp.status_code == 200 and data is not None:
        msgs = data.get("messages", [])
        print(f"  PASS: {len(msgs)} messages in conversation")
        # Check if any messages contain HTML tags
        for m in msgs:
            body = m.get("body", "")
            if "<p>" in body or "<br>" in body or "<div>" in body:
                print(f"  FAIL: Message id={m['id']} contains HTML tags: {body[:100]}")
            elif body:
                print(f"  OK: Message id={m['id']} body={body[:80]}")
    else:
        print(f"  FAIL: Status {resp.status_code}")

# E3: Send a message
print("\n--- E3: Send a message ---")
if conv_id:
    test_msg = "Hello from smoke test - testing HTML stripping"
    resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
        "body": test_msg
    })
    data = pretty("Send message", resp)
    msg_id = None
    if resp.status_code in [200, 201] and data and data.get("message"):
        msg_id = data["message"]["id"]
        print(f"  PASS: Message sent, id={msg_id}")
        body = data["message"].get("body", "")
        if "<" in body:
            print(f"  FAIL: Response body contains HTML: {body[:200]}")
        else:
            print(f"  OK: Response body is plain text: {body[:100]}")
    else:
        print(f"  FAIL: Could not send message")

# E4: Send an HTML message, verify it's stripped on retrieval
print("\n--- E4: Send HTML message, verify stripping ---")
if conv_id:
    html_msg = "<p>This is <b>bold</b> and <script>alert('xss')</script> text</p>"
    resp = doctor_session.post(f"{BASE}/api/chat/conversations/{conv_id}/messages", json={
        "body": html_msg
    })
    data = pretty("Send HTML message", resp)
    if resp.status_code in [200, 201] and data and data.get("message"):
        print(f"  Stored body: {data['message'].get('body', '')[:200]}")
        if "<p>" in data["message"].get("body", "") or "<script>" in data["message"].get("body", ""):
            print(f"  FAIL: HTML was NOT stripped in response")
        else:
            print(f"  PASS: HTML was stripped in response")
    
    # Now retrieve messages and check
    resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    html_found = False
    for m in msgs:
        if "<p>" in m.get("body", "") or "<script>" in m.get("body", ""):
            html_found = True
            print(f"  FAIL: Message id={m['id']} still has HTML: {m['body'][:100]}")
    if not html_found and msgs:
        print(f"  PASS: All {len(msgs)} messages are plain text (no HTML tags)")

# E5: Verify persistence (reload messages)
print("\n--- E5: Verify persistence (re-fetch messages) ---")
if conv_id:
    resp = doctor_session.get(f"{BASE}/api/chat/conversations/{conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    # Look for our test messages
    found_test = [m for m in msgs if "smoke test" in m.get("body", "").lower()]
    found_html = [m for m in msgs if "bold" in m.get("body", "").lower() or "alert" in m.get("body", "").lower()]
    print(f"  Messages with 'smoke test': {len(found_test)}")
    print(f"  Messages with 'bold'/'alert': {len(found_html)}")
    if len(found_test) > 0:
        print(f"  PASS: Plain text message persisted")
    if len(found_html) > 0:
        # Check they're stripped
        all_clean = all("<" not in m.get("body", "") for m in found_html)
        if all_clean:
            print(f"  PASS: HTML message persisted as plain text")
        else:
            print(f"  FAIL: HTML message persisted with tags intact")


# ══════════════════════════════════════════════════════════════
# TEST D: NOTIFICATIONS (API-level only - UI behavior requires browser)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TEST D: NOTIFICATIONS (API-level)")
print("=" * 60)

# D1: Check if notification endpoint exists
print("\n--- D1: List notifications ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations")
data = resp.json() if resp.status_code == 200 else {}
# The notification system uses bus.bus - check if it's accessible
# The NotificationBell uses chatService.listUnseenMessages and similar
# Let's check what endpoints exist
for endpoint in ["/api/chat/unseen", "/api/notifications"]:
    resp = doctor_session.get(f"{BASE}{endpoint}")
    print(f"  GET {endpoint}: HTTP {resp.status_code}")
    if resp.status_code == 200:
        try:
            print(f"    {json.dumps(resp.json(), default=str)[:300]}")
        except:
            pass

print("\n  NOTE: Notification DROPDOWN behavior (click outside, navigate away)")
print("        requires browser-level testing and cannot be verified via API alone.")
print("        The NotificationBell.jsx changes are UI-only fixes.")


print("\n" + "=" * 60)
print("ALL SMOKE TESTS COMPLETE")
print("=" * 60)
