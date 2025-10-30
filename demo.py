#!/usr/bin/env python3
"""
Dev demo for the Inter Mock API (single FastAPI on :8000, no real auth/ASR)
"""

import requests

# Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_EMAIL = "demo@example.com"

def section(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def step(n: int, text: str):
    print(f"\n[{n}] {text}")

def test_api_health() -> bool:
    """Test if the API is running (dev: /api/v1/health)"""
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("✅ API is healthy:", r.json())
            return True
        print(f"❌ API health check failed: {r.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def send_magic_link(email: str):
    """Dev stub: just exercise the endpoint"""
    try:
        r = requests.post(f"{API_BASE_URL}/auth/magic-link", json={"email": email}, timeout=5)
        r.raise_for_status()
        print("✅ Magic link sent:", r.json())
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending magic link: {e}")
        return None

def get_user_profile():
    """Dev: /auth/me requires no token in your mock"""
    try:
        r = requests.get(f"{API_BASE_URL}/auth/me", timeout=5)
        r.raise_for_status()
        print("✅ User profile:", r.json())
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting user profile: {e}")
        return None

def create_session():
    """Create a new interview session (no auth needed in dev)"""
    data = {
        "platform": "demo",
        "session_type": "interview",
        "retention_policy": "auto",
        "privacy_mode": False
    }
    try:
        r = requests.post(f"{API_BASE_URL}/sessions/", json=data, timeout=5)
        r.raise_for_status()
        print("✅ Session created:", r.json())
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating session: {e}")
        return None

def generate_suggestion(session_id: int):
    """Call mock LLM suggestions (your API returns {'suggestion': '...'})."""
    data = {"message": "hello", "session_id": session_id}
    try:
        r = requests.post(f"{API_BASE_URL}/llm/suggestions", json=data, timeout=5)
        r.raise_for_status()
        print("✅ Suggestion:", r.json())
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating suggestion: {e}")
        return None

def test_asr_service(session_id: int):
    """Dev ASR is on same server: /api/v1/asr/health and /api/v1/asr/transcribe/{id}"""
    try:
        rh = requests.get(f"{API_BASE_URL}/asr/health", timeout=5)
        if rh.status_code == 200:
            print("✅ ASR health:", rh.json())
        else:
            print(f"❌ ASR health check failed: {rh.status_code}")
            return False

        rt = requests.post(
            f"{API_BASE_URL}/asr/transcribe/{session_id}",
            data=b"hello",  # any bytes
            headers={"Content-Type": "application/octet-stream"},
            timeout=5,
        )
        rt.raise_for_status()
        print("✅ ASR transcribe:", rt.json())
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ ASR error: {e}")
        return False

def main():
    section("INTER MOCK API - DEV DEMO")
    print("This demo exercises your mock endpoints (no auth, no DB, no ASR server).")

    # 1) Health
    step(1, "API Health")
    if not test_api_health():
        print("\n❌ Demo cannot continue. Start backend first:  uvicorn main:app --reload")
        return

    # 2) Magic link (mock)
    step(2, "Auth (mock magic link)")
    send_magic_link(TEST_EMAIL)

    # 3) Profile (no token in dev)
    step(3, "Get Profile (no token)")
    get_user_profile()

    # 4) Create session
    step(4, "Create Session")
    session = create_session()
    if not session:
        print("❌ No session created; stopping.")
        return
    sid = session.get("id", 0)

    # 5) LLM suggestion (mock shape)
    step(5, "Generate Suggestion")
    generate_suggestion(sid)

    # 6) ASR mock on same server
    step(6, "ASR (mock) on same server")
    test_asr_service(sid)

    section("DEMO COMPLETED")
    print("✅ All mock endpoints responded.")

if __name__ == "__main__":
    main()
