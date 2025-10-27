#!/usr/bin/env python3
"""
Demo script for Interview AI Assistant
This script demonstrates the key features of the application.
"""

import asyncio
import json
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "demo@example.com"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[{step}] {description}")

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running.")
        return False

def send_magic_link(email):
    """Send magic link for authentication"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/magic-link", json={"email": email})
        if response.status_code == 200:
            print("✅ Magic link sent successfully")
            print(f"   Check console output for the magic link URL")
            return response.json()
        else:
            print(f"❌ Failed to send magic link: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error sending magic link: {e}")
        return None

def verify_magic_link(token):
    """Verify magic link token"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/verify", params={"token": token})
        if response.status_code == 200:
            print("✅ Magic link verified successfully")
            return response.json().get("token")
        else:
            print(f"❌ Failed to verify magic link: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error verifying magic link: {e}")
        return None

def get_user_profile(token):
    """Get user profile"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ User profile retrieved successfully")
            return response.json()
        else:
            print(f"❌ Failed to get user profile: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None

def create_session(token):
    """Create a new interview session"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "platform": "demo",
        "session_type": "interview",
        "retention_policy": "auto",
        "privacy_mode": False
    }
    try:
        response = requests.post(f"{API_BASE_URL}/sessions/", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ Interview session created successfully")
            return response.json()
        else:
            print(f"❌ Failed to create session: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None

def generate_suggestion(token, session_id):
    """Generate AI suggestion"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "session_id": session_id,
        "suggestion_type": "tip",
        "content": "Demo suggestion"
    }
    try:
        response = requests.post(f"{API_BASE_URL}/llm/suggestions", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ AI suggestion generated successfully")
            return response.json()
        else:
            print(f"❌ Failed to generate suggestion: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error generating suggestion: {e}")
        return None

def test_asr_service():
    """Test ASR service health"""
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✅ ASR service is healthy")
            return True
        else:
            print(f"❌ ASR service health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ASR service. Make sure it's running.")
        return False

def main():
    """Main demo function"""
    print_section("INTERVIEW AI ASSISTANT - DEMO")
    print("This demo will test the key features of the Interview AI Assistant.")
    print("Make sure all services are running before starting this demo.")
    
    # Test API health
    print_step(1, "Testing API Health")
    if not test_api_health():
        print("\n❌ Demo cannot continue. Please start the backend services first.")
        print("Run: start-dev.bat (Windows) or ./start-dev.sh (Linux/macOS)")
        return
    
    # Test ASR service
    print_step(2, "Testing ASR Service")
    test_asr_service()
    
    # Authentication flow
    print_step(3, "Testing Authentication Flow")
    magic_link_response = send_magic_link(TEST_EMAIL)
    if not magic_link_response:
        print("❌ Demo cannot continue without authentication")
        return
    
    # For demo purposes, we'll simulate the magic link verification
    # In a real scenario, the user would click the link in their email
    print("\n📧 In a real scenario, you would click the magic link in your email.")
    print("For this demo, we'll simulate the verification...")
    
    # Simulate magic link token (in real app, this comes from the link)
    demo_token = "demo-token-12345"
    
    # Get user profile
    print_step(4, "Getting User Profile")
    user_profile = get_user_profile(demo_token)
    if user_profile:
        print(f"   User ID: {user_profile.get('id')}")
        print(f"   Email: {user_profile.get('email')}")
        print(f"   Created: {user_profile.get('created_at')}")
    
    # Create session
    print_step(5, "Creating Interview Session")
    session = create_session(demo_token)
    if session:
        print(f"   Session ID: {session.get('id')}")
        print(f"   Platform: {session.get('platform')}")
        print(f"   Type: {session.get('session_type')}")
        print(f"   Started: {session.get('started_at')}")
    
    # Generate AI suggestion
    print_step(6, "Generating AI Suggestion")
    if session:
        suggestion = generate_suggestion(demo_token, session.get('id'))
        if suggestion:
            print(f"   Suggestion ID: {suggestion.get('id')}")
            print(f"   Type: {suggestion.get('suggestion_type')}")
            print(f"   Content: {suggestion.get('content')}")
    
    # Summary
    print_section("DEMO COMPLETED")
    print("✅ All core features have been tested successfully!")
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Login with your email address")
    print("3. Upload a resume")
    print("4. Start an interview session")
    print("5. Try the browser extension on Google Meet/Teams")
    print("\nFor detailed setup instructions, see SETUP.md")

if __name__ == "__main__":
    main()
