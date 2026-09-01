"""
Laboratory Selection Smoke Test
Tests the new GET /api/laboratories endpoint and lab request creation
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
print("LABORATORY SELECTION SMOKE TEST")
print("=" * 60)

# T1: GET /api/laboratories
print("\n--- T1: GET /api/laboratories ---")
resp = doctor_session.get(f"{BASE}/api/laboratories")
print(f"  HTTP {resp.status_code}")
data = resp.json()
if resp.status_code == 200 and data.get("laboratories"):
    labs = data["laboratories"]
    print(f"  PASS: {len(labs)} laboratories returned")
    for lab in labs:
        print(f"    id={lab['id']} name={lab['name']}")
else:
    print(f"  FAIL: {resp.status_code} {data}")

# T2: Create lab request using laboratory name (not ID)
print("\n--- T2: Create lab request with lab dropdown ---")
lab_id = labs[0]["id"] if labs else None
lab_name = labs[0]["name"] if labs else "unknown"
print(f"  Selected: {lab_name} (id={lab_id})")
resp = doctor_session.post(f"{BASE}/api/lab-requests", json={
    "patient_id": 9,
    "laboratory_id": lab_id,
    "analysis_type": "Complete Blood Count",
    "instructions": "Smoke test - fasting required",
})
print(f"  HTTP {resp.status_code}")
data = resp.json()
req_id = None
if resp.status_code in [200, 201] and data.get("lab_request"):
    req = data["lab_request"]
    req_id = req["id"]
    print(f"  PASS: Lab request created, id={req_id}")
    print(f"    laboratory_id={req['laboratory_id']}, laboratory_name={req['laboratory_name']}")
    print(f"    analysis_type={req['analysis_type']}, status={req['status']}")
else:
    print(f"  FAIL: {resp.status_code} {json.dumps(data, default=str)[:300]}")

# T3: Transition to 'sent'
if req_id:
    print("\n--- T3: Transition lab request to 'sent' ---")
    resp = doctor_session.post(f"{BASE}/api/lab-requests/{req_id}/action", json={"action": "send"})
    print(f"  HTTP {resp.status_code}")
    data = resp.json()
    if resp.status_code == 200 and data.get("lab_request"):
        print(f"  PASS: status={data['lab_request']['status']}")
    else:
        print(f"  FAIL: {resp.status_code} {json.dumps(data, default=str)[:300]}")

# T4: Verify in list
print("\n--- T4: Lab request appears in list ---")
resp = doctor_session.get(f"{BASE}/api/lab-requests")
data = resp.json()
if resp.status_code == 200:
    requests_list = data.get("lab_requests", [])
    found = [r for r in requests_list if r.get("id") == req_id]
    if found:
        r = found[0]
        print(f"  PASS: Found id={r['id']}, lab={r['laboratory_name']}, type={r['analysis_type']}, status={r['status']}")
    else:
        print(f"  FAIL: Request id={req_id} not found in list")

# T5: Verify laboratories appear in the frontend build
print("\n--- T5: Verify frontend build contains laboratories ---")
import subprocess
result = subprocess.run(
    ["findstr", "/i", "listLaboratories", r"C:\Users\HP\Desktop\SANAD_audited_backend\frontend\dist\assets\index-CGu751QJ.js"],
    capture_output=True, text=True
)
if "listLaboratories" in result.stdout:
    print("  PASS: listLaboratories found in production bundle")
else:
    print("  FAIL: listLaboratories NOT found in production bundle")

# T6: Verify laboratories dropdown markup in build
result2 = subprocess.run(
    ["findstr", "/i", "Select a laboratory", r"C:\Users\HP\Desktop\SANAD_audited_backend\frontend\dist\assets\index-CGu751QJ.js"],
    capture_output=True, text=True
)
if "Select a laboratory" in result2.stdout:
    print("  PASS: 'Select a laboratory' dropdown text found in bundle")
else:
    print("  FAIL: Dropdown text not found in bundle")

print("\n" + "=" * 60)
print("LABORATORY SELECTION SMOKE TEST COMPLETE")
print("=" * 60)
