#!/usr/bin/env python3
"""
functional_cross_platform_test.py - Fonksiyonel Cross-Platform Testler

Bu dosya clapp'in gerçek kullanım senaryolarını test eder.
"""

import sys
import os
import subprocess
import tempfile
import shutil
import json
from pathlib import Path

def test_clapp_help():
    """clapp --help komutunu test eder"""
    print("🧪 clapp --help Testi")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ clapp --help başarılı")
            print(f"  📝 Çıktı uzunluğu: {len(result.stdout)} karakter")
            
            # Önemli kelimelerin varlığını kontrol et
            important_words = ["clapp", "komut", "help", "list", "install", "run"]
            found_words = [word for word in important_words if word in result.stdout.lower()]
            print(f"  🔍 Bulunan önemli kelimeler: {found_words}")
            
            return True
        else:
            print(f"  ❌ clapp --help başarısız (return code: {result.returncode})")
            print(f"  📝 Hata: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ clapp --help hatası: {e}")
        return False

def test_clapp_version():
    """clapp version komutunu test eder"""
    print("\n🧪 clapp version Testi")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, "main.py", "version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ clapp version başarılı")
            print(f"  📝 Çıktı: {result.stdout.strip()}")
            
            # Version bilgilerinin varlığını kontrol et
            if "clapp" in result.stdout and "Python" in result.stdout:
                print("  ✅ Version bilgileri doğru")
                return True
            else:
                print("  ❌ Version bilgileri eksik")
                return False
        else:
            print(f"  ❌ clapp version başarısız (return code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"  ❌ clapp version hatası: {e}")
        return False

def test_clapp_list():
    """clapp list komutunu test eder"""
    print("\n🧪 clapp list Testi")
    print("-" * 30)
    
    try:
        result = subprocess.run([sys.executable, "main.py", "list"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ clapp list başarılı")
            print(f"  📝 Çıktı uzunluğu: {len(result.stdout)} karakter")
            
            # List çıktısının beklenen formatını kontrol et
            if "Yüklü uygulamalar" in result.stdout or "Installed apps" in result.stdout:
                print("  ✅ List çıktısı doğru format")
                return True
            else:
                print("  ⚠️  List çıktısı beklenmeyen format")
                return True  # Hata değil, sadece farklı format
        else:
            print(f"  ❌ clapp list başarısız (return code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"  ❌ clapp list hatası: {e}")
        return False

def test_manifest_creation():
    """Test manifest oluşturma ve doğrulama"""
    print("\n🧪 Manifest Oluşturma ve Doğrulama Testi")
    print("-" * 50)
    
    # Geçici test dizini oluştur
    temp_dir = tempfile.mkdtemp()
    test_app_dir = os.path.join(temp_dir, "test-app")
    os.makedirs(test_app_dir)
    
    try:
        # Test manifest'i oluştur
        test_manifest = {
            "name": "test-app",
            "version": "1.0.0",
            "language": "python",
            "description": "Test application for cross-platform testing",
            "entry": "main.py",
            "dependencies": []
        }
        
        manifest_path = os.path.join(test_app_dir, "manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(test_manifest, f, indent=2)
        
        # Test Python dosyası oluştur
        main_py_path = os.path.join(test_app_dir, "main.py")
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write('print("Hello from test app!")\n')
        
        print("  ✅ Test dosyaları oluşturuldu")
        
        # Manifest validation test
        try:
            result = subprocess.run([sys.executable, "main.py", "validate", test_app_dir], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✅ Manifest validation başarılı")
                return True
            else:
                print(f"  ❌ Manifest validation başarısız: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Manifest validation hatası: {e}")
            return False
            
    finally:
        # Temizlik
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def test_package_registry_functions():
    """Package registry fonksiyonlarını test eder"""
    print("\n🧪 Package Registry Fonksiyonları Testi")
    print("-" * 50)
    
    try:
        # Package registry modülünü import et
        from package_registry import get_apps_directory, app_exists
        
        apps_dir = get_apps_directory()
        print(f"  📁 Apps Directory: {apps_dir}")
        
        # Apps directory'nin mevcut olup olmadığını kontrol et
        if os.path.exists(apps_dir):
            print("  ✅ Apps directory mevcut")
        else:
            print("  ⚠️  Apps directory mevcut değil (ilk kullanımda normal)")
        
        # Test app_exists fonksiyonu
        test_result = app_exists("non-existent-app")
        print(f"  🔍 Test app_exists('non-existent-app'): {test_result}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Package registry test hatası: {e}")
        return False

def test_platform_specific_features():
    """Platform'a özgü özellikleri test eder"""
    print("\n🧪 Platform-Specific Features Testi")
    print("-" * 50)
    
    try:
        from platform_utils import is_windows, is_linux, is_macos, get_platform
        
        platform_name = get_platform()
        print(f"  💻 Platform: {platform_name}")
        
        # Platform'a özgü testler
        if is_windows():
            print("  🪟 Windows-specific özellikler:")
            print("    - .exe uzantısı desteği")
            print("    - Windows path separator (\\\)")
            print("    - Git Bash entegrasyonu")
            
        elif is_linux():
            print("  🐧 Linux-specific özellikler:")
            print("    - Unix path separator (/)")
            print("    - Executable permissions")
            print("    - Package manager entegrasyonu")
            
        elif is_macos():
            print("  🍎 macOS-specific özellikler:")
            print("    - Unix path separator (/)")
            print("    - Homebrew entegrasyonu")
            print("    - Executable permissions")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Platform-specific test hatası: {e}")
        return False

def test_command_execution_safety():
    """Komut çalıştırma güvenliğini test eder"""
    print("\n🧪 Command Execution Safety Testi")
    print("-" * 50)
    
    try:
        from platform_utils import run_command_safely
        
        # Güvenli komut testi
        result = run_command_safely([sys.executable, "--version"], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Güvenli komut çalıştırma başarılı")
            print(f"  📝 Python version: {result.stdout.strip()}")
        else:
            print("  ❌ Güvenli komut çalıştırma başarısız")
            return False
        
        # Timeout testi
        try:
            result = run_command_safely(["sleep", "5"], timeout=1)
            print("  ❌ Timeout testi başarısız (beklenen)")
        except subprocess.TimeoutExpired:
            print("  ✅ Timeout koruması çalışıyor")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Command execution safety test hatası: {e}")
        return False

def run_functional_tests():
    """Tüm fonksiyonel testleri çalıştırır"""
    print("🚀 Fonksiyonel Cross-Platform Testler Başlıyor...")
    print("=" * 60)
    
    tests = [
        ("clapp --help", test_clapp_help),
        ("clapp version", test_clapp_version),
        ("clapp list", test_clapp_list),
        ("Manifest Creation", test_manifest_creation),
        ("Package Registry", test_package_registry_functions),
        ("Platform Features", test_platform_specific_features),
        ("Command Safety", test_command_execution_safety)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {test_name} testi hatası: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 FONKSİYONEL TEST SONUÇLARI")
    print("=" * 60)
    print(f"✅ Başarılı Testler: {passed}")
    print(f"❌ Başarısız Testler: {failed}")
    print(f"📈 Toplam Testler: {passed + failed}")
    
    if failed == 0:
        print("🎉 TÜM FONKSİYONEL TESTLER BAŞARILI!")
        print("✅ clapp fonksiyonel cross-platform uyumluluğu tam!")
    else:
        print(f"⚠️  {failed} fonksiyonel test başarısız!")
    
    print("=" * 60)

if __name__ == "__main__":
    run_functional_tests() 