#!/usr/bin/env python3
"""
Simple HuggingFace API Test - Issue #25
Test direct HF API call without orpheuspypractice dependencies
"""

import requests
import json

def test_hf_direct():
    """Direct HuggingFace API test"""
    print("🤖 Simple HuggingFace API Test")
    
    # Get API key securely
    api_key = input("🔑 Enter your HuggingFace API key: ").strip()
    if not api_key:
        print("❌ No API key provided.")
        return
    
    # Test with working music generation model  
    url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "upbeat jazz melody in G major",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7
        }
    }
    
    print("🎵 Testing HuggingFace API connection...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ HuggingFace API connection successful!")
            print("📊 Response received:", len(response.content), "bytes")
            
            # Try to parse response
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    print("📋 JSON Response keys:", list(data.keys()) if isinstance(data, dict) else "Non-dict response")
                else:
                    print("📋 Binary/Audio response received")
            except:
                print("📋 Raw response format")
                
        elif response.status_code == 401:
            print("❌ Authentication failed - check your API key")
        elif response.status_code == 403:
            print("❌ Access forbidden - check API permissions")
        elif response.status_code == 503:
            print("⏳ Model loading - try again in a moment")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print("Error:", response.text[:200])
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Clear API key
    api_key = None
    print("🔒 API key cleared from memory")

if __name__ == "__main__":
    test_hf_direct()