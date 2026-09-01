"""
Lab & Pharmacy Chat Smoke Test
Verifies that lab/pharmacy users can:
1. Login
2. List conversations
3. Create a conversation with a doctor
4. Send a message
5. Retrieve messages
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

print("=" * 60)
print("LAB & PHARMACY CHAT SMOKE TEST")
print("=" * 60)

# Login as doctor (to be the other side of the conversation)
doctor_session, _ = login("ahmed.benali@test.sanad", "demo1234")

# Login as lab user
lab_session, lab_resp = login("lab.test@sanad.local", "demo1234")
lab_data = lab_resp.json()
print("\n--- Lab Login ---")
print(f"  HTTP {lab_resp.status_code}, user={lab_data.get('user', {}).get('name')}, roles={lab_data.get('user', {}).get('roles')}")

# Login as pharmacy user
pharm_session, pharm_resp = login("pharmacy.test@sanad.local", "demo1234")
pharm_data = pharm_resp.json()
print("\n--- Pharmacy Login ---")
print(f"  HTTP {pharm_resp.status_code}, user={pharm_data.get('user', {}).get('name')}, roles={pharm_data.get('user', {}).get('roles')}")

# ============================================
# LAB CHAT TESTS
# ============================================
print("\n" + "=" * 60)
print("LAB CHAT")
print("=" * 60)

# T1: Lab lists existing conversations
print("\n--- Lab: List conversations ---")
resp = lab_session.get(f"{BASE}/api/chat/conversations")
data = resp.json()
convs = data.get("conversations", [])
print(f"  HTTP {resp.status_code}, conversations: {len(convs)}")
for c in convs:
    print(f"    id={c['id']} type={c['conversation_type']} participants={c['participant_names']}")

# T2: Lab creates conversation with doctor
print("\n--- Lab: Create conversation with doctor ---")
resp = lab_session.post(f"{BASE}/api/chat/conversations", json={
    "other_user_id": 5,  # doctor ahmed.benali
    "conversation_type": "doctor_laboratory"
})
print(f"  HTTP {resp.status_code}")
data = resp.json()
lab_conv_id = None
if resp.status_code in [200, 201]:
    conv = data.get("conversation", data)
    lab_conv_id = conv.get("id")
    print(f"  Conversation created: id={lab_conv_id}")
    print(f"  Type: {conv.get('conversation_type')}")
    print(f"  Participants: {conv.get('participant_names')}")
else:
    print(f"  Response: {json.dumps(data, default=str)[:300]}")

# T3: Lab sends a message
print("\n--- Lab: Send message ---")
if lab_conv_id:
    resp = lab_session.post(f"{BASE}/api/chat/conversations/{lab_conv_id}/messages", json={
        "body": "Hello Dr. Benali, lab results for patient #9 are ready."
    })
    data = resp.json()
    print(f"  HTTP {resp.status_code}")
    if data.get("message"):
        print(f"  Message sent: id={data['message']['id']}, body={data['message']['body']}")
    else:
        print(f"  Response: {json.dumps(data, default=str)[:300]}")

# T4: Lab retrieves messages
print("\n--- Lab: Retrieve messages ---")
if lab_conv_id:
    resp = lab_session.get(f"{BASE}/api/chat/conversations/{lab_conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    print(f"  HTTP {resp.status_code}, messages: {len(msgs)}")
    for m in msgs:
        print(f"    id={m['id']} author={m['author_name']} body={m['body'][:80]}")

# T5: Doctor sees the lab conversation
print("\n--- Doctor: Check lab conversation ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations")
data = resp.json()
convs = data.get("conversations", [])
lab_conv_found = any(c["id"] == lab_conv_id for c in convs) if lab_conv_id else False
print(f"  Doctor sees {len(convs)} conversations")
if lab_conv_found:
    print(f"  PASS: Doctor can see lab conversation id={lab_conv_id}")
else:
    print(f"  FAIL: Doctor cannot see lab conversation id={lab_conv_id}")

# ============================================
# PHARMACY CHAT TESTS
# ============================================
print("\n" + "=" * 60)
print("PHARMACY CHAT")
print("=" * 60)

# T6: Pharmacy lists existing conversations
print("\n--- Pharmacy: List conversations ---")
resp = pharm_session.get(f"{BASE}/api/chat/conversations")
data = resp.json()
convs = data.get("conversations", [])
print(f"  HTTP {resp.status_code}, conversations: {len(convs)}")
for c in convs:
    print(f"    id={c['id']} type={c['conversation_type']} participants={c['participant_names']}")

# T7: Pharmacy creates conversation with doctor
print("\n--- Pharmacy: Create conversation with doctor ---")
resp = pharm_session.post(f"{BASE}/api/chat/conversations", json={
    "other_user_id": 5,  # doctor ahmed.benali
    "conversation_type": "doctor_pharmacy"
})
print(f"  HTTP {resp.status_code}")
data = resp.json()
pharm_conv_id = None
if resp.status_code in [200, 201]:
    conv = data.get("conversation", data)
    pharm_conv_id = conv.get("id")
    print(f"  Conversation created: id={pharm_conv_id}")
    print(f"  Type: {conv.get('conversation_type')}")
    print(f"  Participants: {conv.get('participant_names')}")
else:
    print(f"  Response: {json.dumps(data, default=str)[:300]}")

# T8: Pharmacy sends a message
print("\n--- Pharmacy: Send message ---")
if pharm_conv_id:
    resp = pharm_session.post(f"{BASE}/api/chat/conversations/{pharm_conv_id}/messages", json={
        "body": "Dr. Benali, prescription #28 has been prepared."
    })
    data = resp.json()
    print(f"  HTTP {resp.status_code}")
    if data.get("message"):
        print(f"  Message sent: id={data['message']['id']}, body={data['message']['body']}")
    else:
        print(f"  Response: {json.dumps(data, default=str)[:300]}")

# T9: Pharmacy retrieves messages
print("\n--- Pharmacy: Retrieve messages ---")
if pharm_conv_id:
    resp = pharm_session.get(f"{BASE}/api/chat/conversations/{pharm_conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    print(f"  HTTP {resp.status_code}, messages: {len(msgs)}")
    for m in msgs:
        print(f"    id={m['id']} author={m['author_name']} body={m['body'][:80]}")

# T10: Doctor sees the pharmacy conversation
print("\n--- Doctor: Check pharmacy conversation ---")
resp = doctor_session.get(f"{BASE}/api/chat/conversations")
data = resp.json()
convs = data.get("conversations", [])
pharm_conv_found = any(c["id"] == pharm_conv_id for c in convs) if pharm_conv_id else False
print(f"  Doctor sees {len(convs)} conversations")
if pharm_conv_found:
    print(f"  PASS: Doctor can see pharmacy conversation id={pharm_conv_id}")
else:
    print(f"  FAIL: Doctor cannot see pharmacy conversation id={pharm_conv_id}")

# T11: Doctor replies to pharmacy
print("\n--- Doctor: Reply to pharmacy ---")
if pharm_conv_id:
    resp = doctor_session.post(f"{BASE}/api/chat/conversations/{pharm_conv_id}/messages", json={
        "body": "Thank you! I will update the patient record."
    })
    data = resp.json()
    print(f"  HTTP {resp.status_code}")
    if data.get("message"):
        print(f"  Reply sent: id={data['message']['id']}, body={data['message']['body']}")

# T12: Pharmacy sees the reply
print("\n--- Pharmacy: Retrieve updated messages ---")
if pharm_conv_id:
    resp = pharm_session.get(f"{BASE}/api/chat/conversations/{pharm_conv_id}/messages")
    data = resp.json()
    msgs = data.get("messages", [])
    print(f"  HTTP {resp.status_code}, messages: {len(msgs)}")
    for m in msgs:
        print(f"    id={m['id']} author={m['author_name']} body={m['body'][:80]}")
    if len(msgs) >= 2:
        print(f"  PASS: Two-way chat works between doctor and pharmacy")
    else:
        print(f"  FAIL: Expected >=2 messages, got {len(msgs)}")

print("\n" + "=" * 60)
print("LAB & PHARMACY CHAT SMOKE TEST COMPLETE")
print("=" * 60)
