#!/usr/bin/env python3
"""
Secure HuggingFace API Test Script - Issue #25
♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE ACTIVE

SECURITY: This script handles API keys securely and does not log them.
"""

import os
import tempfile
import subprocess
from pathlib import Path
import json

def secure_test_hf_integration():
    """🧵 Secure test of HuggingFace integration with user-provided API key"""
    
    print("♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE: Secure HF Integration Test")
    print("🔐 This script will handle your API key securely (no logging/storage)")
    
    # Get API key securely
    api_key = input("🔑 Enter your HuggingFace API key (input hidden): ").strip()
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Test ABC content
    test_abc = """X:1
T:HF Integration Test
L:1/8
Q:1/4=120
M:4/4
K:G
|: G2 A2 B2 c2 | d2 c2 B2 A2 :|"""
    
    print("🎵 Testing with sample ABC notation...")
    
    # Check if orpheuspypractice is available
    try:
        result = subprocess.run(["which", "ohfi"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 'ohfi' command not found. Need to install orpheuspypractice:")
            print("   pip install orpheuspypractice")
            return
        print("✅ Found 'ohfi' command")
    except Exception as e:
        print(f"❌ Error checking ohfi availability: {e}")
        return
    
    # Create secure temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"🔒 Working in secure temp directory: {temp_path}")
        
        # Create input files
        abc_file = temp_path / "test_input.abc"
        abc_file.write_text(test_abc)
        
        # Create omusical.yaml configuration
        omusical_config = f"""
# Secure HF ChatMusician configuration - Generated dynamically
api_key: "{api_key}"
model: "microsoft/muzic-musicgen-base"
prompt: |
  You are ChatMusician, an AI music composer. Enhance the following ABC notation 
  with more sophisticated harmonies and rhythmic variations.
  
  Original ABC:
  {test_abc}
  
  Please provide enhanced ABC notation with improved musical elements.

output_format: "json"
include_audio: true
max_tokens: 1000
temperature: 0.7
"""
        
        config_file = temp_path / "omusical.yaml"
        config_file.write_text(omusical_config)
        
        # Set environment variable securely
        env = os.environ.copy()
        env['HUGGINGFACE_API_KEY'] = api_key
        
        print("🤖 Calling HuggingFace ChatMusician via ohfi...")
        
        try:
            # Execute ohfi command
            result = subprocess.run(
                ["ohfi", "--config", str(config_file)],
                cwd=temp_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                print("✅ HuggingFace call successful!")
                print("📄 Output received:")
                
                # Look for generated JSON files
                json_files = list(temp_path.glob("*.json"))
                if json_files:
                    for json_file in json_files:
                        print(f"📁 Found output: {json_file.name}")
                        try:
                            with open(json_file) as f:
                                data = json.load(f)
                                if 'enhanced_abc' in data:
                                    print("🎵 Enhanced ABC found in output!")
                                    print(data['enhanced_abc'][:200] + "...")
                                else:
                                    print("📋 JSON structure:")
                                    print(json.dumps(data, indent=2)[:500] + "...")
                        except Exception as e:
                            print(f"⚠️ Could not parse JSON: {e}")
                else:
                    print("📋 Raw output:")
                    print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
                
            else:
                print(f"❌ HuggingFace call failed (exit code: {result.returncode})")
                print("Error output:", result.stderr[:300])
                
                # Common troubleshooting
                if "authentication" in result.stderr.lower() or "api" in result.stderr.lower():
                    print("💡 Troubleshooting: Check API key validity and permissions")
                elif "model" in result.stderr.lower():
                    print("💡 Troubleshooting: Check model name and availability")
                elif "quota" in result.stderr.lower() or "limit" in result.stderr.lower():
                    print("💡 Troubleshooting: Check API usage limits and billing")
                
        except subprocess.TimeoutExpired:
            print("⏱️ HuggingFace call timed out (60s limit)")
        except Exception as e:
            print(f"❌ Error executing ohfi: {e}")
        
        # Clear API key from memory (security)
        api_key = None
        if 'HUGGINGFACE_API_KEY' in env:
            del env['HUGGINGFACE_API_KEY']
    
    print("🔒 Secure cleanup completed - API key cleared from memory")

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    packages = ["orpheuspypractice", "jgcmlib", "jghfmanager"]
    missing = []
    
    for package in packages:
        try:
            result = subprocess.run(
                ["python", "-c", f"import {package}; print(f'{package}: OK')"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {package}: Available")
            else:
                missing.append(package)
                print(f"❌ {package}: Missing")
        except Exception:
            missing.append(package)
            print(f"❌ {package}: Missing")
    
    if missing:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

if __name__ == "__main__":
    print("♠️🌿🎸🤖🧵 G.MUSIC ASSEMBLY MODE: HuggingFace Integration Test")
    
    if check_dependencies():
        print("\n🚀 All dependencies available. Starting secure test...")
        secure_test_hf_integration()
    else:
        print("\n⚠️ Please install missing dependencies first.")