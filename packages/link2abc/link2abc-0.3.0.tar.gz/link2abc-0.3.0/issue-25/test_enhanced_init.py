#!/usr/bin/env python3
"""
Test the enhanced init command with HuggingFace configuration
"""
import sys
import os
sys.path.insert(0, '/data/data/com.termux/files/home/src/EchoThreads/music/linktune/src')

from linktune.cli import main
from click.testing import CliRunner

def test_init_version():
    """Test that the version was updated correctly"""
    from linktune import __version__, __author__, __email__
    
    print(f"🔍 Testing updated package metadata:")
    print(f"   Version: {__version__}")
    print(f"   Author: {__author__}")
    print(f"   Email: {__email__}")
    
    assert __version__ == "0.3.0", f"Expected v0.3.0, got {__version__}"
    assert __author__ == "gerico1007", f"Expected gerico1007, got {__author__}"
    assert __email__ == "gerico@jgwill.com", f"Expected gerico@jgwill.com, got {__email__}"
    
    print("✅ Package metadata updated correctly!")
    return True

def test_cli_help():
    """Test that the CLI help includes the init option"""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    
    print(f"🔍 Testing CLI help output:")
    print(f"   Exit code: {result.exit_code}")
    
    # Check that --init option is present
    assert '--init' in result.output, "Missing --init option in help"
    assert 'Interactive setup wizard' in result.output, "Missing init description"
    
    print("✅ CLI help includes enhanced init option!")
    return True

def test_version_command():
    """Test the version command"""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    
    print(f"🔍 Testing version command:")
    print(f"   Output: {result.output.strip()}")
    print(f"   Exit code: {result.exit_code}")
    
    assert result.exit_code == 0, f"Version command failed: {result.exit_code}"
    assert "v0.3.0" in result.output, f"Version not found in output: {result.output}"
    
    print("✅ Version command works correctly!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Enhanced Link2ABC Package v0.3.0")
    print("=" * 50)
    
    try:
        # Test package metadata
        test_init_version()
        print()
        
        # Test CLI help
        test_cli_help() 
        print()
        
        # Test version command
        test_version_command()
        print()
        
        print("🎉 All tests passed! Package ready for publication.")
        print("\n📦 Next steps:")
        print("   1. Build: python -m build /path/to/linktune")
        print("   2. Test install: pip install dist/link2abc-0.3.0*.whl")
        print("   3. Test init: link2abc --init")
        print("   4. Publish: twine upload dist/*")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)