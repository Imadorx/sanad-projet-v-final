import requests
import json
import sys

BASE = "http://localhost:8069"

def test_login(login, password, label):
    print(f"\n=== LOGIN: {label} ({login}) ===")
    session = requests.Session()
    resp = session.post(f"{BASE}/api/auth/login", json={"login": login, "password": password})
    print(f"  HTTP Status: {resp.status_code}")
    try:
        data = resp.json()
        print(f"  Response: {json.dumps(data, indent=2, default=str)}")
    except:
        print(f"  Raw response: {resp.text[:500]}")
    
    # Check session cookie
    cookies = dict(session.cookies)
    print(f"  Session cookies: {list(cookies.keys())}")
    
    if resp.status_code == 200 and data.get("user"):
        user = data["user"]
        print(f"  PASS: Logged in as {user.get('name')} (id={user.get('id')})")
        print(f"  Roles: {user.get('roles')}")
        print(f"  Doctor ID: {user.get('doctor_id')}")
        return session
    else:
        print(f"  FAIL: Login failed")
        return None

def test_session_check(session, label):
    print(f"\n=== SESSION CHECK: {label} ===")
    resp = session.get(f"{BASE}/api/auth/session")
    print(f"  HTTP Status: {resp.status_code}")
    try:
        data = resp.json()
        print(f"  Response: {json.dumps(data, indent=2, default=str)}")
    except:
        print(f"  Raw: {resp.text[:500]}")
    return resp.status_code == 200

print("=" * 60)
print("TEST A: AUTHENTICATION")
print("=" * 60)

doctor_session = test_login("ahmed.benali@test.sanad", "demo1234", "Doctor")
test_session_check(doctor_session, "Doctor session check") if doctor_session else None

pharmacy_session = test_login("pharmacy.test@sanad.local", "demo1234", "Pharmacy")
test_session_check(pharmacy_session, "Pharmacy session check") if pharmacy_session else None

# Test bad login
print("\n=== LOGIN: Bad credentials ===")
bad_resp = requests.post(f"{BASE}/api/auth/login", json={"login": "ahmed.benali@test.sanad", "password": "wrong"})
print(f"  HTTP Status: {bad_resp.status_code}")
try:
    print(f"  Response: {json.dumps(bad_resp.json(), indent=2, default=str)}")
except:
    print(f"  Raw: {bad_resp.text[:500]}")

# Save sessions for later tests
import pickle
with open("/tmp/doctor_session.pkl", "wb") as f:
    pickle.dump(doctor_session.cookies.get_dict(), f)
with open("/tmp/pharmacy_session.pkl", "wb") as f:
    pickle.dump(pharmacy_session.cookies.get_dict(), f) if pharmacy_session else None

print("\n" + "=" * 60)
print("AUTHENTICATION TESTS COMPLETE")
print("=" * 60)
