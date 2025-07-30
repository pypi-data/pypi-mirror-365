#!/usr/bin/env python3
"""
deploy.py - Otomatik Deployment Script

Bu script clapp-pm paketini otomatik olarak deploy eder:
1. Version günceller
2. Git commit yapar
3. Build oluşturur
4. PyPI'ya upload eder
5. GitHub'a push eder
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

def get_pypi_token():
    """PyPI token'ını kullanıcıdan alır"""
    print("🔐 PyPI Token Gerekli")
    print("Token'ı https://pypi.org/manage/account/token/ adresinden alabilirsiniz")
    print("Token formatı: pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print()
    
    while True:
        token = input("PyPI Token'ınızı girin: ").strip()
        
        if not token:
            print("❌ Token boş olamaz!")
            continue
            
        if not token.startswith("pypi-"):
            print("❌ Token 'pypi-' ile başlamalı!")
            continue
            
        if len(token) < 50:
            print("❌ Token çok kısa görünüyor!")
            continue
            
        print("✅ Token formatı doğru")
        return token

# PyPI Token'ı kullanıcıdan al
PYPI_TOKEN = get_pypi_token()

def run_command(command, description, check=True):
    """Komut çalıştırır ve sonucu döndürür"""
    print(f"🔄 {description}...")
    try:
        # Komut listesi olarak geçirilmişse doğrudan kullan
        if isinstance(command, list):
            cmd_parts = command
        else:
            # String komutları split et
            cmd_parts = command.split()
            
        result = subprocess.run(
            cmd_parts, 
            check=check, 
            capture_output=True, 
            text=True,
            timeout=60  # 60 saniye timeout ekle
        )
        if result.stdout:
            print(f"✅ {description} başarılı")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} başarısız: {e}")
        if e.stderr:
            print(f"   Hata: {e.stderr}")
        return False, e.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ {description} zaman aşımı")
        return False, "Zaman aşımı"
    except Exception as e:
        print(f"❌ {description} beklenmeyen hata: {e}")
        return False, str(e)

def update_version(version_type="patch"):
    """Version numarasını günceller"""
    print(f"📝 Version güncelleniyor ({version_type})...")
    
    # version.json dosyasını oku
    with open("version.json", "r", encoding="utf-8") as f:
        version_data = json.load(f)
    
    current_version = version_data["version"]
    major, minor, patch = map(int, current_version.split("."))
    
    # Kullanıcıdan sürüm tipini al
    print(f"\n🔄 Mevcut sürüm: {current_version}")
    print("Sürüm güncelleme tipini seçin:")
    print("1. Major (x.0.0) - Büyük değişiklikler")
    print("2. Minor (0.x.0) - Yeni özellikler")
    print("3. Patch (0.0.x) - Hata düzeltmeleri")
    
    while True:
        choice = input("\nSeçiminiz (1/2/3): ").strip()
        if choice == "1":
            version_type = "major"
            major += 1
            minor = 0
            patch = 0
            break
        elif choice == "2":
            version_type = "minor"
            minor += 1
            patch = 0
            break
        elif choice == "3":
            version_type = "patch"
            patch += 1
            break
        else:
            print("❌ Geçersiz seçim! 1, 2 veya 3 girin.")
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Onay al
    print(f"\n📋 Sürüm güncellemesi: {current_version} → {new_version}")
    confirm = input("Devam etmek istiyor musunuz? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', 'evet']:
        print("❌ Sürüm güncellemesi iptal edildi")
        return None
    
    # version.json güncelle
    version_data["version"] = new_version
    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)
    
    # version.py güncelle
    with open("version.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace(f'__version__ = "{current_version}"', f'__version__ = "{new_version}"')
    
    with open("version.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Version {current_version} → {new_version} güncellendi")
    return new_version

def deploy(version_type="patch", message=None, skip_version=False):
    """Ana deployment fonksiyonu"""
    print("🚀 clapp-pm Deployment Başlatılıyor")
    print("=" * 50)
    
    # 1. Version güncelle (opsiyonel)
    if not skip_version:
        new_version = update_version(version_type)
    else:
        # Mevcut version'u oku
        with open("version.json", "r", encoding="utf-8") as f:
            version_data = json.load(f)
        new_version = version_data["version"]
    
    # 2. Git status kontrolü
    success, output = run_command("git status --porcelain", "Git durumu kontrol ediliyor")
    if not success:
        return False
    
    if not output.strip():
        print("⚠️  Değişiklik yok, deployment iptal ediliyor")
        return False
    
    # 3. Git add
    success, _ = run_command("git add .", "Değişiklikler Git'e ekleniyor")
    if not success:
        return False
    
    # 4. Git commit
    if not message:
        message = f"Auto-deploy v{new_version}"
    
    success, _ = run_command(['git', 'commit', '-m', message], "Git commit yapılıyor")
    if not success:
        return False
    
    # 5. Build
    success, _ = run_command("python -m build", "Paket build ediliyor")
    if not success:
        return False
    
    # 6. PyPI upload
    upload_command = ['python', '-m', 'twine', 'upload', '--username', '__token__', '--password', PYPI_TOKEN, f'dist/clapp_pm-{new_version}*']
    success, _ = run_command(upload_command, "PyPI'ya upload ediliyor")
    if not success:
        return False
    
    # 7. Git push
    success, _ = run_command("git push origin master", "GitHub'a push ediliyor")
    if not success:
        return False
    
    print("\n" + "=" * 50)
    print(f"🎉 Deployment başarılı! v{new_version}")
    print(f"📦 PyPI: https://pypi.org/project/clapp-pm/{new_version}/")
    print(f"🐙 GitHub: https://github.com/mburakmmm/clapp")
    print("=" * 50)
    
    return True

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="clapp-pm otomatik deployment script")
    parser.add_argument("--version-type", choices=["major", "minor", "patch"], 
                       default="patch", help="Version güncelleme tipi")
    parser.add_argument("--message", "-m", help="Commit mesajı")
    parser.add_argument("--skip-version", action="store_true", 
                       help="Version güncellemeyi atla")
    
    args = parser.parse_args()
    
    success = deploy(
        version_type=args.version_type,
        message=args.message,
        skip_version=args.skip_version
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 