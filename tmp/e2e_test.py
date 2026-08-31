import requests
import json

BASE = 'http://localhost:3000'

def login(username, password):
    """Login and return session cookies"""
    resp = requests.post(f'{BASE}/api/auth/login', json={
        'login': username, 'password': password
    }, allow_redirects=False)
    print(f"  Login {username}: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"    user: {data.get('user', {}).get('login')} roles={data.get('user', {}).get('roles')}")
        return resp.cookies
    else:
        print(f"    ERROR: {resp.text[:200]}")
        return None

def test_pharmacy_list(cookies):
    """Test GET /api/pharmacies"""
    resp = requests.get(f'{BASE}/api/pharmacies', cookies=cookies)
    print(f"  GET /api/pharmacies: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        for ph in data.get('pharmacies', []):
            print(f"    id={ph['id']} name={ph['name']}")
    else:
        print(f"    ERROR: {resp.text[:200]}")

def test_create_prescription(cookies):
    """Test POST /api/prescriptions with pharmacy_id"""
    resp = requests.post(f'{BASE}/api/prescriptions', json={
        'patient_id': 33,
        'pharmacy_id': 12,
        'medication': 'Ibuprofen',
        'dosage': '200mg',
        'frequency': '3x daily',
        'duration': '5 days',
        'instructions': 'Take with food',
    }, cookies=cookies)
    print(f"  POST /api/prescriptions: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        p = data.get('prescription', {})
        print(f"    id={p.get('id')} medication={p.get('medication')} pharmacy_id={p.get('pharmacy_id')}")
        return p.get('id')
    else:
        print(f"    ERROR: {resp.text[:200]}")
        return None

def test_pharmacy_prescriptions(cookies):
    """Test GET /api/pharmacy/prescriptions"""
    resp = requests.get(f'{BASE}/api/pharmacy/prescriptions', cookies=cookies)
    print(f"  GET /api/pharmacy/prescriptions: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        rxs = data.get('prescriptions', [])
        print(f"    count: {len(rxs)}")
        for p in rxs:
            print(f"    id={p['id']} medication={p['medication']} status={p['pharmacy_status']}")
    else:
        print(f"    ERROR: {resp.text[:200]}")

def test_pharmacy_action(cookies, rx_id, action):
    """Test POST /api/pharmacy/prescriptions/:id/action"""
    resp = requests.post(f'{BASE}/api/pharmacy/prescriptions/{rx_id}/action',
                         json={'action': action}, cookies=cookies)
    print(f"  POST /api/pharmacy/prescriptions/{rx_id}/action ({action}): {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        p = data.get('prescription', {})
        print(f"    status: {p.get('pharmacy_status')}")
    else:
        print(f"    ERROR: {resp.text[:200]}")

def test_chat_send(cookies):
    """Test POST /api/chat/send"""
    resp = requests.post(f'{BASE}/api/chat/send', json={
        'to_user_id': 31,
        'body': 'Hello from test',
    }, cookies=cookies)
    print(f"  POST /api/chat/send: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        msg = data.get('message', {})
        print(f"    id={msg.get('id')} body={msg.get('body')}")
    else:
        print(f"    ERROR: {resp.text[:200]}")

def test_chat_conversations(cookies):
    """Test GET /api/chat/conversations"""
    resp = requests.get(f'{BASE}/api/chat/conversations', cookies=cookies)
    print(f"  GET /api/chat/conversations: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        convos = data.get('conversations', [])
        print(f"    count: {len(convos)}")
        for c in convos[:3]:
            print(f"    peer={c.get('peer_name')} last_msg={c.get('last_message', {}).get('body', '')[:40]}")
    else:
        print(f"    ERROR: {resp.text[:200]}")

# ==============================
print("=== 1. Login as Doctor (ahmed.benali) ===")
doctor_cookies = login('ahmed.benali@test.sanad', 'admin')

print("\n=== 2. Doctor: List pharmacies ===")
test_pharmacy_list(doctor_cookies)

print("\n=== 3. Doctor: Create prescription with pharmacy_id ===")
rx_id = test_create_prescription(doctor_cookies)

print("\n=== 4. Login as Pharmacy (pharmacy.test -> Pharmacie SANAD) ===")
pharm_cookies = login('pharmacy.test@sanad.local', 'admin')

print("\n=== 5. Pharmacy: List prescriptions ===")
test_pharmacy_prescriptions(pharm_cookies)

if rx_id:
    print(f"\n=== 6. Pharmacy: Receive prescription {rx_id} ===")
    test_pharmacy_action(pharm_cookies, rx_id, 'receive')

print("\n=== 7. Login as Al Amal Pharmacy ===")
alamal_cookies = login('pharmacy.alamal@test.sanad', 'admin')

print("\n=== 8. Al Amal: List prescriptions ===")
test_pharmacy_prescriptions(alamal_cookies)

print("\n=== 9. Doctor: Send chat message to Al Amal ===")
test_chat_send(doctor_cookies)

print("\n=== 10. Doctor: Chat conversations ===")
test_chat_conversations(doctor_cookies)

print("\n=== ALL TESTS DONE ===")
