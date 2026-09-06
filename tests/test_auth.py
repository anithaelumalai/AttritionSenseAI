import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.auth import authenticate_employee, authenticate_hr

def test_authentication():
    print("Testing HR login...")
    ok, user, msg = authenticate_hr("admin", "admin123")
    assert ok and user["role"] == "hr", f"HR login failed: {msg}"
    print("[PASS] HR login verified:", user["identifier"])

    print("Testing Employee login (EmployeeNumber 1)...")
    ok, user, msg = authenticate_employee("1", "emp123")
    assert ok and user["role"] == "employee", f"Employee login failed: {msg}"
    print("[PASS] Employee login verified:", user["identifier"])

    print("Testing invalid HR login...")
    ok, user, msg = authenticate_hr("admin", "wrongpassword")
    assert not ok, "Expected fail on wrong HR password"
    print("[PASS] Invalid HR password rejected:", msg)

    print("Testing invalid Employee password...")
    ok, user, msg = authenticate_employee("1", "wrongpass")
    assert not ok, "Expected fail on wrong employee password"
    print("[PASS] Invalid Employee password rejected:", msg)

    print("Testing non-existent Employee (ID 3 is absent in IBM dataset)...")
    ok, user, msg = authenticate_employee("3", "emp123")
    assert not ok, "Expected fail on absent employee ID"
    print("[PASS] Non-existent Employee rejected:", msg)

    print("\nALL AUTHENTICATION TESTS PASSED!")

if __name__ == "__main__":
    test_authentication()
