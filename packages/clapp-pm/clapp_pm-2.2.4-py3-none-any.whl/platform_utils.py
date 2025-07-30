#!/usr/bin/env python3
"""
platform_utils.py - Cross-Platform Uyumluluk Araçları

Bu modül Windows, Linux ve macOS arasındaki farklılıkları
yönetmek için gerekli fonksiyonları sağlar.
"""

import os
import sys
import platform
import subprocess
from typing import Optional, List, Tuple

def get_platform() -> str:
    """Platform bilgisini döndürür"""
    return platform.system().lower()

def is_windows() -> bool:
    """Windows'ta çalışıp çalışmadığını kontrol eder"""
    return get_platform() == "windows"

def is_linux() -> bool:
    """Linux'ta çalışıp çalışmadığını kontrol eder"""
    return get_platform() == "linux"

def is_macos() -> bool:
    """macOS'ta çalışıp çalışmadığını kontrol eder"""
    return get_platform() == "darwin"

def is_unix() -> bool:
    """Unix benzeri sistemde çalışıp çalışmadığını kontrol eder"""
    return is_linux() or is_macos()

def get_executable_extension() -> str:
    """Platform'a göre executable uzantısını döndürür"""
    return ".exe" if is_windows() else ""

def get_path_separator() -> str:
    """Platform'a göre path separator'ını döndürür"""
    return "\\" if is_windows() else "/"

def normalize_path(path: str) -> str:
    """Path'i platform'a uygun şekilde normalize eder"""
    if is_windows():
        return path.replace("/", "\\")
    else:
        return path.replace("\\", "/")

def find_executable(executable_name: str) -> Optional[str]:
    """
    Executable'ı PATH'te arar
    
    Args:
        executable_name: Aranacak executable adı
        
    Returns:
        Executable'ın tam yolu veya None
    """
    # Windows'ta .exe uzantısını ekle
    if is_windows() and not executable_name.endswith('.exe'):
        executable_name += '.exe'
    
    # which komutu yerine cross-platform alternatif
    try:
        if is_windows():
            # Windows'ta where komutu kullan
            result = subprocess.run(['where', executable_name], 
                                  capture_output=True, text=True, timeout=10)
        else:
            # Unix sistemlerde which komutu kullan
            result = subprocess.run(['which', executable_name], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return None

def get_python_executable() -> str:
    """Python executable'ının yolunu döndürür"""
    return sys.executable

def get_pyenv_path() -> Optional[str]:
    """pyenv yolunu platform'a göre bulur"""
    if is_windows():
        # Windows'ta pyenv genellikle farklı yerde
        possible_paths = [
            os.path.expanduser("~/.pyenv/bin/pyenv"),
            os.path.expanduser("~/.pyenv/pyenv-win/bin/pyenv.exe"),
            "pyenv.exe"  # PATH'te olabilir
        ]
    else:
        # Unix sistemlerde
        possible_paths = [
            os.path.expanduser("~/.pyenv/bin/pyenv"),
            "/usr/local/bin/pyenv",
            "pyenv"  # PATH'te olabilir
        ]
    
    for path in possible_paths:
        if os.path.exists(path) or find_executable(path):
            return path
    
    return None

def run_command_safely(command: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Komutu güvenli şekilde çalıştırır
    
    Args:
        command: Çalıştırılacak komut listesi
        **kwargs: subprocess.run için ek parametreler
        
    Returns:
        subprocess.CompletedProcess objesi
    """
    # Windows'ta shell=True gerekebilir
    if is_windows() and len(command) == 1:
        kwargs['shell'] = True
    
    # Timeout ekle
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 30
    
    return subprocess.run(command, **kwargs)

def get_temp_dir() -> str:
    """Platform'a uygun temp dizinini döndürür"""
    import tempfile
    return tempfile.gettempdir()

def create_temp_path(prefix: str = "clapp_", suffix: str = "") -> str:
    """
    Platform'a uygun temp path oluşturur
    
    Args:
        prefix: Dosya adı öneki
        suffix: Dosya adı son eki
        
    Returns:
        Temp dosya yolu
    """
    import tempfile
    import time
    import uuid
    
    # Benzersiz ID oluştur
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time() * 1000)  # Milisaniye hassasiyeti
    
    if is_windows():
        # Windows'ta daha kısa path kullan
        return os.path.join(get_temp_dir(), f"{prefix}{timestamp}_{unique_id}{suffix}")
    else:
        # Unix sistemlerde daha uzun path kullanabilir
        return os.path.join(get_temp_dir(), f"{prefix}{timestamp}_{unique_id}{suffix}")

def ensure_executable_permissions(file_path: str) -> None:
    """
    Dosyaya executable izni verir (Unix sistemlerde)
    
    Args:
        file_path: İzin verilecek dosya yolu
    """
    if is_unix() and os.path.exists(file_path):
        try:
            os.chmod(file_path, 0o755)
        except OSError:
            pass  # İzin verilemezse sessizce geç

def get_home_dir() -> str:
    """Kullanıcının home dizinini döndürür"""
    return os.path.expanduser("~")

def get_clapp_home() -> str:
    """Clapp home dizinini döndürür"""
    home = get_home_dir()
    if is_windows():
        return os.path.join(home, ".clapp")
    else:
        return os.path.join(home, ".clapp")

def is_git_available() -> bool:
    """Git'in kullanılabilir olup olmadığını kontrol eder"""
    try:
        result = run_command_safely(['git', '--version'], 
                                  capture_output=True, text=True)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_git_command() -> List[str]:
    """Platform'a uygun git komutunu döndürür"""
    if is_windows():
        # Windows'ta git komutunu bul
        git_path = find_executable('git')
        if git_path:
            return [git_path]
        else:
            # Git Bash varsa onu kullan
            git_bash = find_executable('git-bash')
            if git_bash:
                return [git_bash, '-c', 'git']
    else:
        # Unix sistemlerde git genellikle PATH'te
        return ['git']
    
    return ['git']  # Fallback 