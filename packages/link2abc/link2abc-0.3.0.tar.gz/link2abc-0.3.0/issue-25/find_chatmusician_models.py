#!/usr/bin/env python3
"""
Find ChatMusician Models on HuggingFace - Issue #25
"""

import requests
import json

def search_chatmusician_models():
    """Search for ChatMusician models on HuggingFace"""
    print("🔍 Searching for ChatMusician models on HuggingFace...")
    
    # Search HuggingFace model hub
    search_terms = ["chatmusician", "music", "abc", "midi", "musical"]
    
    for term in search_terms:
        print(f"\n🎵 Searching for: {term}")
        
        try:
            # HuggingFace Hub API search
            url = f"https://huggingface.co/api/models?search={term}&sort=downloads&direction=-1&limit=10"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                
                for model in models:
                    model_id = model.get('modelId', 'Unknown')
                    downloads = model.get('downloads', 0)
                    tags = model.get('tags', [])
                    
                    # Filter for music-related models
                    if any(music_tag in tags for music_tag in ['music', 'audio', 'midi', 'abc']):
                        print(f"  📋 {model_id} (downloads: {downloads})")
                        print(f"     Tags: {', '.join(tags[:5])}")
            else:
                print(f"  ❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error searching {term}: {e}")

def test_specific_models():
    """Test specific known music models"""
    print("\n🎼 Testing known music generation models...")
    
    models_to_test = [
        "microsoft/musicgen-small",
        "facebook/musicgen-small", 
        "sander-wood/text-to-music",
        "huggingface/CodeBERTa-small-v1",  # Sometimes used for structured data
    ]
    
    for model in models_to_test:
        print(f"\n🔍 Testing model: {model}")
        
        try:
            # Check if model exists
            url = f"https://huggingface.co/api/models/{model}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                model_info = response.json()
                print(f"  ✅ Model exists!")
                print(f"     Pipeline tag: {model_info.get('pipeline_tag', 'Unknown')}")
                print(f"     Tags: {', '.join(model_info.get('tags', [])[:3])}")
                
                # Check if it has an inference API
                inference_url = f"https://api-inference.huggingface.co/models/{model}"
                print(f"     Inference API: {inference_url}")
                
            elif response.status_code == 404:
                print(f"  ❌ Model not found")
            else:
                print(f"  ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def show_chatmusician_instructions():
    """Show instructions for ChatMusician integration"""
    print("\n" + "="*60)
    print("🤖 CHATMUSICIAN INTEGRATION INSTRUCTIONS")
    print("="*60)
    
    print("""
Based on the original issue description, ChatMusician integration requires:

1. 📋 Model Repository: Look for 'ChatMusician' on HuggingFace Hub
   - Search: https://huggingface.co/models?search=chatmusician
   
2. 🔧 Integration Method: Through orpheuspypractice 'ohfi' command
   - This suggests a custom integration, not direct HF API
   
3. 📝 Configuration: Uses 'omusical.yaml' configuration files
   - Custom prompt templates for ABC notation enhancement

4. 💡 Next Steps:
   - Get your HuggingFace API key from: https://huggingface.co/settings/tokens
   - Wait for orpheuspypractice installation to complete
   - Test 'ohfi' command with proper ChatMusician model
   
5. 🔍 Alternative Approach:
   - If ChatMusician isn't publicly available, we may need to:
     - Use alternative music generation models
     - Adapt the integration for available models
     - Create custom ABC enhancement logic
""")

if __name__ == "__main__":
    print("♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE: ChatMusician Model Discovery")
    
    search_chatmusician_models()
    test_specific_models() 
    show_chatmusician_instructions()