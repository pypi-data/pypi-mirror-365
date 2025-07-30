#!/usr/bin/env python3
"""
📋 LinkTune Cross-Platform Clipboard Module
Enhanced with mobile/Termux support for G.Music Assembly

Provides comprehensive clipboard access across desktop and mobile environments
with graceful fallbacks for all scenarios.
"""

import os
import sys
import platform
import subprocess
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClipboardResult:
    """Result container for clipboard operations"""
    success: bool
    content: Optional[str] = None
    method: Optional[str] = None
    error_message: Optional[str] = None
    environment: Optional[str] = None


class EnvironmentDetector:
    """
    🔍 Cross-platform environment detection
    
    Specialized for Termux/Android detection with multiple verification methods
    """
    
    @staticmethod
    def detect_environment() -> Dict[str, Any]:
        """
        Comprehensive environment detection
        
        Returns:
            dict: Environment information including type, capabilities, and metadata
        """
        env_info = {
            "type": "unknown",
            "is_termux": False,
            "is_android": False,
            "is_linux": False,
            "is_windows": False,
            "is_mac": False,
            "clipboard_methods": [],
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "platform_system": platform.system(),
            "platform_details": platform.platform()
        }
        
        # Detect basic platform
        system = platform.system().lower()
        if system == "linux":
            env_info["is_linux"] = True
        elif system == "windows":
            env_info["is_windows"] = True
        elif system == "darwin":
            env_info["is_mac"] = True
        
        # Android/Termux detection (multiple methods)
        is_android = EnvironmentDetector._detect_android()
        is_termux = EnvironmentDetector._detect_termux()
        
        if is_termux:
            env_info["type"] = "termux"
            env_info["is_termux"] = True
            env_info["is_android"] = True
        elif is_android:
            env_info["type"] = "android"
            env_info["is_android"] = True
        elif env_info["is_linux"]:
            env_info["type"] = "linux"
        elif env_info["is_windows"]:
            env_info["type"] = "windows"
        elif env_info["is_mac"]:
            env_info["type"] = "mac"
        
        # Detect available clipboard methods
        env_info["clipboard_methods"] = EnvironmentDetector._detect_clipboard_methods(env_info)
        
        return env_info
    
    @staticmethod
    def _detect_android() -> bool:
        """Detect Android environment using multiple methods"""
        
        # Method 1: Check Android environment variables
        android_env_vars = ['ANDROID_DATA', 'ANDROID_ROOT', 'ANDROID_ARGUMENT', 'ANDROID_PRIVATE']
        for var in android_env_vars:
            if var in os.environ:
                return True
        
        # Method 2: Check standard Android env var values
        if (os.getenv("ANDROID_DATA") == "/data" and 
            os.getenv("ANDROID_ROOT") == "/system"):
            return True
        
        # Method 3: Check for Android directories
        android_dirs = ['/system/app', '/system/priv-app', '/android_root', '/data']
        if all(os.path.exists(d) for d in android_dirs[:2]):
            return True
        
        # Method 4: Use uname command
        try:
            result = subprocess.check_output(['uname', '-o'], 
                                           stderr=subprocess.DEVNULL,
                                           timeout=2)
            if b'Android' in result:
                return True
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False
    
    @staticmethod
    def _detect_termux() -> bool:
        """Detect Termux environment specifically"""
        
        # Method 1: Check for com.termux in HOME path
        home = os.environ.get('HOME', '')
        if 'com.termux' in home:
            return True
        
        # Method 2: Check for Termux-specific paths
        termux_paths = [
            '/data/data/com.termux',
            os.path.expanduser('~/../../usr/bin/termux-setup-storage')
        ]
        for path in termux_paths:
            if os.path.exists(path):
                return True
        
        # Method 3: Check for Termux API availability
        try:
            result = subprocess.run(['which', 'termux-clipboard-get'], 
                                  capture_output=True, timeout=2)
            if result.returncode == 0:
                return True
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False
    
    @staticmethod
    def _detect_clipboard_methods(env_info: Dict[str, Any]) -> list:
        """Detect available clipboard access methods"""
        methods = []
        
        if env_info["is_termux"]:
            # Check for Termux clipboard commands
            if EnvironmentDetector._command_exists('termux-clipboard-get'):
                methods.append('termux_clipboard')
        
        if env_info["is_linux"] or env_info["is_android"]:
            # Check for Linux clipboard tools
            if EnvironmentDetector._command_exists('xclip'):
                methods.append('xclip')
            if EnvironmentDetector._command_exists('xsel'):
                methods.append('xsel')
        
        if env_info["is_mac"]:
            # macOS has built-in pbcopy/pbpaste
            methods.append('pbcopy_pbpaste')
        
        if env_info["is_windows"]:
            # Windows has built-in clipboard
            methods.append('windows_clipboard')
        
        # Check for pyperclip availability
        try:
            import pyperclip
            methods.append('pyperclip')
        except ImportError:
            pass
        
        # Manual input is always available as fallback
        methods.append('manual_input')
        
        return methods
    
    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            # Use 'command -v' instead of 'which' for better cross-platform support
            result = subprocess.run(['sh', '-c', f'command -v {command}'], 
                                  capture_output=True, timeout=2)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False


class ClipboardManager:
    """
    📋 Cross-platform clipboard manager
    
    Provides unified clipboard access with intelligent fallbacks
    specialized for mobile/Termux environments.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.env_info = EnvironmentDetector.detect_environment()
        
        if self.verbose:
            self._print_environment_info()
    
    def get_clipboard_content(self) -> ClipboardResult:
        """
        📥 Get content from clipboard using best available method
        
        Returns:
            ClipboardResult: Result with content, method used, and success status
        """
        methods = self.env_info["clipboard_methods"]
        
        if self.verbose:
            print(f"🔍 Available clipboard methods: {methods}")
        
        for method in methods:
            if self.verbose:
                print(f"🧪 Trying method: {method}")
            
            result = self._try_clipboard_method(method)
            if result.success:
                if self.verbose:
                    print(f"✅ Success with {method}")
                return result
            elif self.verbose:
                print(f"❌ Failed with {method}: {result.error_message}")
        
        # If all methods fail, return failure result
        return ClipboardResult(
            success=False,
            method="none",
            error_message="No clipboard access methods available",
            environment=self.env_info["type"]
        )
    
    def _try_clipboard_method(self, method: str) -> ClipboardResult:
        """Try a specific clipboard access method"""
        
        try:
            if method == 'termux_clipboard':
                return self._get_termux_clipboard()
            elif method == 'pyperclip':
                return self._get_pyperclip()
            elif method == 'xclip':
                return self._get_xclip()
            elif method == 'xsel':
                return self._get_xsel()
            elif method == 'pbcopy_pbpaste':
                return self._get_macos_clipboard()
            elif method == 'windows_clipboard':
                return self._get_windows_clipboard()
            elif method == 'manual_input':
                return self._get_manual_input()
            else:
                return ClipboardResult(
                    success=False,
                    method=method,
                    error_message=f"Unknown clipboard method: {method}",
                    environment=self.env_info["type"]
                )
        
        except Exception as e:
            return ClipboardResult(
                success=False,
                method=method,
                error_message=str(e),
                environment=self.env_info["type"]
            )
    
    def _get_termux_clipboard(self) -> ClipboardResult:
        """Get clipboard content using Termux API"""
        try:
            result = subprocess.run(['termux-clipboard-get'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                content = result.stdout.strip()
                return ClipboardResult(
                    success=bool(content),
                    content=content if content else None,
                    method="termux_clipboard",
                    error_message=None if content else "Clipboard is empty",
                    environment=self.env_info["type"]
                )
            else:
                return ClipboardResult(
                    success=False,
                    method="termux_clipboard",
                    error_message=result.stderr.strip() or "termux-clipboard-get failed",
                    environment=self.env_info["type"]
                )
                
        except FileNotFoundError:
            return ClipboardResult(
                success=False,
                method="termux_clipboard",
                error_message="termux-clipboard-get command not found. Install termux-api package.",
                environment=self.env_info["type"]
            )
        except subprocess.TimeoutExpired:
            return ClipboardResult(
                success=False,
                method="termux_clipboard",
                error_message="termux-clipboard-get timed out",
                environment=self.env_info["type"]
            )
    
    def _get_pyperclip(self) -> ClipboardResult:
        """Get clipboard content using pyperclip library"""
        try:
            import pyperclip
            content = pyperclip.paste()
            
            return ClipboardResult(
                success=bool(content),
                content=content if content else None,
                method="pyperclip",
                error_message=None if content else "Clipboard is empty",
                environment=self.env_info["type"]
            )
        except ImportError:
            return ClipboardResult(
                success=False,
                method="pyperclip",
                error_message="pyperclip library not available",
                environment=self.env_info["type"]
            )
        except Exception as e:
            return ClipboardResult(
                success=False,
                method="pyperclip",
                error_message=f"pyperclip error: {str(e)}",
                environment=self.env_info["type"]
            )
    
    def _get_xclip(self) -> ClipboardResult:
        """Get clipboard content using xclip command"""
        try:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-out'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                content = result.stdout.strip()
                return ClipboardResult(
                    success=bool(content),
                    content=content if content else None,
                    method="xclip",
                    error_message=None if content else "Clipboard is empty",
                    environment=self.env_info["type"]
                )
            else:
                return ClipboardResult(
                    success=False,
                    method="xclip",
                    error_message="xclip command failed",
                    environment=self.env_info["type"]
                )
        except FileNotFoundError:
            return ClipboardResult(
                success=False,
                method="xclip",
                error_message="xclip command not found",
                environment=self.env_info["type"]
            )
        except subprocess.TimeoutExpired:
            return ClipboardResult(
                success=False,
                method="xclip",
                error_message="xclip timed out",
                environment=self.env_info["type"]
            )
    
    def _get_xsel(self) -> ClipboardResult:
        """Get clipboard content using xsel command"""
        try:
            result = subprocess.run(['xsel', '--clipboard', '--output'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                content = result.stdout.strip()
                return ClipboardResult(
                    success=bool(content),
                    content=content if content else None,
                    method="xsel",
                    error_message=None if content else "Clipboard is empty",
                    environment=self.env_info["type"]
                )
            else:
                return ClipboardResult(
                    success=False,
                    method="xsel",
                    error_message="xsel command failed",
                    environment=self.env_info["type"]
                )
        except FileNotFoundError:
            return ClipboardResult(
                success=False,
                method="xsel",
                error_message="xsel command not found",
                environment=self.env_info["type"]
            )
        except subprocess.TimeoutExpired:
            return ClipboardResult(
                success=False,
                method="xsel",
                error_message="xsel timed out",
                environment=self.env_info["type"]
            )
    
    def _get_macos_clipboard(self) -> ClipboardResult:
        """Get clipboard content using macOS pbpaste"""
        try:
            result = subprocess.run(['pbpaste'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                content = result.stdout.strip()
                return ClipboardResult(
                    success=bool(content),
                    content=content if content else None,
                    method="pbpaste",
                    error_message=None if content else "Clipboard is empty",
                    environment=self.env_info["type"]
                )
            else:
                return ClipboardResult(
                    success=False,
                    method="pbpaste",
                    error_message="pbpaste command failed",
                    environment=self.env_info["type"]
                )
        except FileNotFoundError:
            return ClipboardResult(
                success=False,
                method="pbpaste",
                error_message="pbpaste command not found",
                environment=self.env_info["type"]
            )
        except subprocess.TimeoutExpired:
            return ClipboardResult(
                success=False,
                method="pbpaste",
                error_message="pbpaste timed out",
                environment=self.env_info["type"]
            )
    
    def _get_windows_clipboard(self) -> ClipboardResult:
        """Get clipboard content on Windows"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            content = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            return ClipboardResult(
                success=bool(content),
                content=content if content else None,
                method="win32clipboard",
                error_message=None if content else "Clipboard is empty",
                environment=self.env_info["type"]
            )
        except ImportError:
            return ClipboardResult(
                success=False,
                method="win32clipboard",
                error_message="win32clipboard library not available",
                environment=self.env_info["type"]
            )
        except Exception as e:
            return ClipboardResult(
                success=False,
                method="win32clipboard",
                error_message=f"Windows clipboard error: {str(e)}",
                environment=self.env_info["type"]
            )
    
    def _get_manual_input(self) -> ClipboardResult:
        """Fallback: Manual text input"""
        try:
            print("\n📋 Clipboard access not available. Please enter your content manually:")
            print("💡 Tip: Paste your content and press Enter. Use Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done.")
            print("-" * 50)
            
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                # User pressed Ctrl+D/Ctrl+Z
                pass
            except KeyboardInterrupt:
                # User pressed Ctrl+C
                return ClipboardResult(
                    success=False,
                    method="manual_input",
                    error_message="Input cancelled by user",
                    environment=self.env_info["type"]
                )
            
            content = '\n'.join(lines).strip()
            
            return ClipboardResult(
                success=bool(content),
                content=content if content else None,
                method="manual_input",
                error_message=None if content else "No content entered",
                environment=self.env_info["type"]
            )
            
        except Exception as e:
            return ClipboardResult(
                success=False,
                method="manual_input",
                error_message=f"Manual input error: {str(e)}",
                environment=self.env_info["type"]
            )
    
    def _print_environment_info(self):
        """Print detailed environment information"""
        print("🔍 Environment Detection Results:")
        print(f"   Type: {self.env_info['type']}")
        print(f"   Platform: {self.env_info['platform_system']}")
        print(f"   Termux: {self.env_info['is_termux']}")
        print(f"   Android: {self.env_info['is_android']}")
        print(f"   Clipboard methods: {', '.join(self.env_info['clipboard_methods'])}")
        print("-" * 50)
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get detected environment information"""
        return self.env_info.copy()


# Convenience functions for easy integration
def get_clipboard_content(verbose: bool = False) -> ClipboardResult:
    """
    🎯 Simple function to get clipboard content
    
    Args:
        verbose: Print debug information
        
    Returns:
        ClipboardResult: Result with clipboard content
    """
    manager = ClipboardManager(verbose=verbose)
    return manager.get_clipboard_content()


def detect_environment() -> Dict[str, Any]:
    """
    🔍 Simple function to detect environment
    
    Returns:
        dict: Environment information
    """
    return EnvironmentDetector.detect_environment()


# Example usage and testing
if __name__ == "__main__":
    print("🧪 LinkTune Clipboard Module Test")
    print("=" * 50)
    
    # Test environment detection
    env = detect_environment()
    print(f"Environment: {env['type']}")
    print(f"Available methods: {env['clipboard_methods']}")
    print("-" * 30)
    
    # Test clipboard access
    result = get_clipboard_content(verbose=True)
    
    if result.success:
        print(f"✅ Clipboard content retrieved via {result.method}:")
        print(f"Content length: {len(result.content or '')}")
        print(f"Preview: {(result.content or '')[:100]}...")
    else:
        print(f"❌ Clipboard access failed: {result.error_message}")
        print(f"Method attempted: {result.method}")