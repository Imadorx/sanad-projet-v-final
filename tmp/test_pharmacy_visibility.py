"""
Focused Pharmacy Visibility Smoke Test
Tests the pharmacy visibility fix (domain change + user linking)
"""
import requests
import json

BASE = "http://localhost:8069"

def login(login, password):
    s = requests.Session()
    resp = s.post(f"{BASE}/api/auth/login", json={"login": login, "password": password})
    return s, resp

doctor_session, _ = login("ahmed.benali@test.sanad", "demo1234")
pharmacy_session, _ = login("pharmacy.test@sanad.local", "demo1234")

print("=" * 60)
print("PHARMACY VISIBILITY SMOKE TEST")
print("=" * 60)

# Test 1: GET /api/pharmacies
print("\n--- T1: GET /api/pharmacies (pharmacy user) ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacies")
print(f"  HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 200 and data.get("pharmacies"):
    print(f"  PASS: {len(data['pharmacies'])} pharmacies returned")
    for p in data["pharmacies"]:
        print(f"    id={p['id']} name={p['name']}")
else:
    print(f"  FAIL: {resp.status_code} {data}")

# Test 2: Pharmacy lists prescriptions (the critical test)
print("\n--- T2: Pharmacy lists prescriptions (RX#28 should be visible) ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacy/prescriptions")
print(f"  HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 200:
    rx_list = data.get("prescriptions", [])
    print(f"  Prescriptions visible: {len(rx_list)}")
    rx_ids = [p["id"] for p in rx_list]
    print(f"  Prescription IDs: {rx_ids}")
    if 28 in rx_ids:
        print(f"  PASS: RX#28 (pharmacy_id=1) IS visible to pharmacy.test@sanad.local")
        # Find and show details
        for p in rx_list:
            if p["id"] == 28:
                print(f"    medication={p['medication']}, status={p['pharmacy_status']}")
                break
    else:
        print(f"  FAIL: RX#28 NOT visible")
    if 29 in rx_ids:
        print(f"  NOTE: RX#29 (pharmacy_id=None) is also visible")
    else:
        print(f"  OK: RX#29 (pharmacy_id=None) correctly NOT visible")
else:
    print(f"  FAIL: {resp.status_code} {data}")

# Test 3: Pharmacy filters by status
print("\n--- T3: Pharmacy filters prescriptions by status=pending ---")
resp = pharmacy_session.get(f"{BASE}/api/pharmacy/prescriptions", params={"status": "pending"})
print(f"  HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 200:
    rx_list = data.get("prescriptions", [])
    rx_ids = [p["id"] for p in rx_list]
    print(f"  Pending prescriptions: {len(rx_list)}, IDs: {rx_ids}")
    if 28 in rx_ids:
        print(f"  PASS: RX#28 visible with status=pending filter")
    else:
        print(f"  FAIL: RX#28 not found with status=pending")
else:
    print(f"  FAIL: {resp.status_code}")

# Test 4: Different pharmacy user (pharmacy.alamal) should NOT see RX#28
print("\n--- T4: Al Amal pharmacy should NOT see RX#28 ---")
alamal_session, _ = login("pharmacy.alamal@test.sanad", "demo1234")
resp = alamal_session.get(f"{BASE}/api/pharmacy/prescriptions")
print(f"  HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 200:
    rx_list = data.get("prescriptions", [])
    rx_ids = [p["id"] for p in rx_list]
    print(f"  Al Amal sees: {len(rx_list)} prescriptions, IDs: {rx_ids}")
    if 28 not in rx_ids:
        print(f"  PASS: RX#28 correctly NOT visible to Al Amal pharmacy")
    else:
        print(f"  FAIL: RX#28 incorrectly visible to Al Amal pharmacy")
else:
    print(f"  FAIL: {resp.status_code}")

# Test 5: Doctor still sees all prescriptions (no regression)
print("\n--- T5: Doctor still sees all prescriptions (no regression) ---")
resp = doctor_session.get(f"{BASE}/api/prescriptions")
print(f"  HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 200:
    rx_list = data.get("prescriptions", [])
    rx_ids = [p["id"] for p in rx_list]
    print(f"  Doctor sees: {len(rx_list)} prescriptions")
    if 28 in rx_ids and 29 in rx_ids:
        print(f"  PASS: Both RX#28 and RX#29 visible to doctor")
    else:
        print(f"  FAIL: Missing prescriptions (found: {rx_ids})")
else:
    print(f"  FAIL: {resp.status_code}")

# Test 6: Create a new prescription with pharmacy_id and verify visibility
print("\n--- T6: Create new RX and verify pharmacy visibility ---")
resp = doctor_session.post(f"{BASE}/api/prescriptions", json={
    "patient_id": 9,
    "pharmacy_id": 1,
    "medication": "Test Visibility RX",
    "dosage": "100mg",
    "frequency": "Once daily",
    "duration": "3 days",
    "instructions": "Smoke test",
})
print(f"  Create: HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 201 and data.get("prescription"):
    new_rx_id = data["prescription"]["id"]
    print(f"  Created RX#{new_rx_id}")
    
    # Now check pharmacy can see it
    resp = pharmacy_session.get(f"{BASE}/api/pharmacy/prescriptions")
    data = resp.json()
    rx_ids = [p["id"] for p in data.get("prescriptions", [])]
    if new_rx_id in rx_ids:
        print(f"  PASS: New RX#{new_rx_id} immediately visible to pharmacy")
    else:
        print(f"  FAIL: New RX#{new_rx_id} NOT visible to pharmacy")
else:
    print(f"  FAIL: Could not create prescription: {resp.status_code} {data}")

print("\n" + "=" * 60)
print("PHARMACY VISIBILITY SMOKE TEST COMPLETE")
print("=" * 60)
