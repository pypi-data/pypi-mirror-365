#!/usr/bin/env python3
"""
publish_command.py - clapp Publish Command

Bu modül 'clapp publish <folder>' komutunu uygular.
Bir uygulama klasörünü validate edip packages/ klasörüne kopyalar
ve index.json'u günceller. Opsiyonel olarak clapp-packages reposuna push eder.
"""

import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from typing import Tuple, Optional
import time

from manifest_validator import validate_manifest_verbose
from manifest_schema import load_manifest

def validate_app_folder(folder_path: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Uygulama klasörünü doğrular
    
    Returns:
        (success, message, manifest_data)
    """
    if not os.path.exists(folder_path):
        return False, f"Klasör bulunamadı: {folder_path}", None
    
    if not os.path.isdir(folder_path):
        return False, f"Geçerli bir klasör değil: {folder_path}", None
    
    # manifest.json kontrolü
    manifest_path = os.path.join(folder_path, "manifest.json")
    if not os.path.exists(manifest_path):
        return False, "manifest.json dosyası bulunamadı", None
    
    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        return False, f"manifest.json okunamadı: {e}", None
    
    # Manifest doğrulama
    is_valid, errors = validate_manifest_verbose(manifest)
    if not is_valid:
        error_msg = "Manifest doğrulama hatası:\n" + "\n".join(f"  - {error}" for error in errors)
        return False, error_msg, None
    
    # Entry file kontrolü
    entry_file = manifest.get('entry')
    if entry_file:
        entry_path = os.path.join(folder_path, entry_file)
        if not os.path.exists(entry_path):
            return False, f"Entry dosyası bulunamadı: {entry_file}", None
    
    return True, "Doğrulama başarılı", manifest

def copy_app_to_packages(source_folder: str, app_name: str) -> Tuple[bool, str]:
    """
    Uygulama klasörünü ana clapp dizinindeki packages/ altına kopyalar
    
    Returns:
        (success, message)
    """
    try:
        # Ana clapp dizinini bul
        clapp_root, _ = find_clapp_root_with_build_index()
        if not clapp_root:
            return False, "Ana clapp dizini bulunamadı"
        
        packages_dir = os.path.join(clapp_root, "packages")
        target_path = os.path.join(packages_dir, app_name)
        
        # packages klasörünü oluştur
        os.makedirs(packages_dir, exist_ok=True)
        
        # Eğer hedef klasör varsa, sil
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            print(f"⚠️  Mevcut {app_name} klasörü silindi")
        
        # Önce tüm klasörü kopyala
        shutil.copytree(source_folder, target_path)
        
        # Gereksiz dosya ve klasörleri sil
        exclude_patterns = [
            '.venv', '__pycache__', '.git', '.gitignore', '.DS_Store',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
            'node_modules', '.npm', '.yarn', 'yarn.lock', 'package-lock.json',
            '*.log', '*.tmp', '*.temp', '.vscode', '.idea', '*.swp', '*.swo',
            'Thumbs.db', 'desktop.ini', '.Trashes', '.Spotlight-V100',
            'packages'  # packages klasörünü de hariç tut
        ]
        
        def remove_excluded_files(path):
            """Gereksiz dosya ve klasörleri sil"""
            for root, dirs, files in os.walk(path, topdown=False):
                # Dosyaları sil
                for file in files:
                    file_path = os.path.join(root, file)
                    basename = os.path.basename(file_path)
                    
                    for pattern in exclude_patterns:
                        if pattern.startswith('*'):
                            if basename.endswith(pattern[1:]):
                                try:
                                    os.remove(file_path)
                                    break
                                except:
                                    pass
                        else:
                            if basename == pattern:
                                try:
                                    os.remove(file_path)
                                    break
                                except:
                                    pass
                
                # Dizinleri sil
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    
                    for pattern in exclude_patterns:
                        if dir_name == pattern:
                            try:
                                shutil.rmtree(dir_path)
                                break
                            except:
                                pass
        
        # Gereksiz dosyaları sil
        remove_excluded_files(target_path)
        
        print(f"✅ {app_name} -> packages/{app_name} kopyalandı")
        
        return True, f"Uygulama başarıyla kopyalandı: packages/{app_name}"
        
    except Exception as e:
        return False, f"Kopyalama hatası: {e}"

def find_clapp_root_with_build_index():
    """
    Ana clapp dizinini ve build_index.py'yi bulur.
    1. which clapp konumundan arama
    2. pyenv which clapp konumundan arama
    3. Kesin konum kontrolü
    4. Fallback olarak mevcut çalışma dizininden arama
    Returns: (clapp_root, build_index_path) veya (None, None)
    """
    import os
    import subprocess
    
    # 1. which clapp konumundan arama
    try:
        result = subprocess.run(['which', 'clapp'], capture_output=True, text=True)
        if result.returncode == 0:
            clapp_path = result.stdout.strip()
            
            # clapp komutunun bulunduğu dizinden başlayarak yukarı çık
            clapp_dir = os.path.dirname(clapp_path)
            search_dir = clapp_dir
            
            while search_dir != os.path.dirname(search_dir):  # Root'a ulaşana kadar
                build_index_path = os.path.join(search_dir, "build_index.py")
                if os.path.exists(build_index_path):
                    return search_dir, build_index_path
                search_dir = os.path.dirname(search_dir)
    except Exception:
        pass
    
    # 2. pyenv which clapp konumundan arama
    try:
        result = subprocess.run(['pyenv', 'which', 'clapp'], capture_output=True, text=True)
        if result.returncode == 0:
            clapp_path = result.stdout.strip()
            
            # clapp komutunun bulunduğu dizinden başlayarak yukarı çık
            clapp_dir = os.path.dirname(clapp_path)
            search_dir = clapp_dir
            
            while search_dir != os.path.dirname(search_dir):  # Root'a ulaşana kadar
                build_index_path = os.path.join(search_dir, "build_index.py")
                if os.path.exists(build_index_path):
                    return search_dir, build_index_path
                search_dir = os.path.dirname(search_dir)
    except Exception:
        pass
    
    # 3. Kesin konum kontrolü
    clapp_home = "/Users/melihburakmemis/Desktop/clapp"
    build_index_path = os.path.join(clapp_home, "build_index.py")
    if os.path.exists(build_index_path):
        return clapp_home, build_index_path
    
    # 4. Fallback: Mevcut çalışma dizininden başlayarak yukarı çık
    search_dir = os.getcwd()
    while search_dir != os.path.dirname(search_dir):  # Root'a ulaşana kadar
        build_index_path = os.path.join(search_dir, "build_index.py")
        if os.path.exists(build_index_path):
            return search_dir, build_index_path
        search_dir = os.path.dirname(search_dir)
    
    return None, None


def update_index() -> Tuple[bool, str]:
    """
    build_index.py script'ini çalıştırarak index.json'u günceller
    Returns: (success, message)
    """
    try:
        clapp_root, build_index_path = find_clapp_root_with_build_index()
        if not clapp_root or not build_index_path:
            return False, "Ana clapp dizini veya build_index.py bulunamadı. Lütfen komutu ana dizinden veya bir alt klasörden çalıştırın."
        
        # build_index.py'yi ana dizinde çalıştır
        result = subprocess.run([
            sys.executable, build_index_path
        ], cwd=clapp_root)
        if result.returncode == 0:
            return True, "Index başarıyla güncellendi"
        else:
            return False, f"Index güncelleme hatası: Çalıştırılan dizin: {clapp_root}"
    except Exception as e:
        return False, f"Index script çalıştırılamadı: {e}"

def push_to_clapp_packages_repo(app_name: str, app_version: str) -> Tuple[bool, str]:
    """
    Uygulamayı direkt GitHub clapp-packages reposuna push eder
    
    Returns:
        (success, message)
    """
    try:
        print("2️⃣ GitHub repo güncelleniyor...")
        
        # clapp-packages reposunu kontrol et
        packages_repo_path = "./clapp-packages-repo"
        
        # Eğer clapp-packages repo klonlanmamışsa, klonla
        if not os.path.exists(packages_repo_path):
            print("📥 clapp-packages reposu klonlanıyor...")
            subprocess.run([
                'git', 'clone', 'https://github.com/mburakmmm/clapp-packages.git', 
                packages_repo_path
            ], check=True, cwd=".")
        
        # Publish edilecek uygulama klasörünü bul
        app_folder = None
        for root, dirs, files in os.walk("."):
            if "manifest.json" in files:
                manifest_path = os.path.join(root, "manifest.json")
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    if manifest.get('name') == app_name:
                        app_folder = root
                        break
                except:
                    continue
        
        if not app_folder:
            return False, f"{app_name} uygulaması bulunamadı"
        
        # GitHub repo'ya uygulamayı kopyala
        target_app = os.path.join(packages_repo_path, "packages", app_name)
        target_packages = os.path.join(packages_repo_path, "packages")
        os.makedirs(target_packages, exist_ok=True)
        
        # Eğer hedef uygulama klasörü varsa, sil
        if os.path.exists(target_app):
            shutil.rmtree(target_app)
        
        # Uygulamayı kopyala
        shutil.copytree(app_folder, target_app)
        print(f"✅ {app_name} uygulaması GitHub repo'ya kopyalandı")
        
        # GitHub repo'da index.json'u güncelle
        os.chdir(packages_repo_path)
        
        # build_index.py'yi GitHub repo'da çalıştır
        if os.path.exists("build_index.py"):
            result = subprocess.run([sys.executable, "build_index.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub repo'da index.json güncellendi")
            else:
                print(f"⚠️  Index güncelleme hatası: {result.stderr}")
        else:
            print("⚠️  GitHub repo'da build_index.py bulunamadı")
        
        # Git işlemleri
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("📦 Değişiklikler commit ediliyor...")
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_message = f"📦 Publish {app_name} v{app_version}\n\n- {app_name} uygulaması packages/ klasörüne eklendi\n- index.json güncellendi\n- Otomatik publish işlemi"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        else:
            print("📦 Working tree temiz, sadece push yapılıyor...")
        
        # Push et
        try:
            print("📥 Remote değişiklikleri çekiliyor...")
            subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Pull başarısız, force push yapılıyor...")
            subprocess.run(['git', 'push', 'origin', 'main', '--force'], check=True)
        else:
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        # Ana dizine geri dön
        os.chdir("..")
        
        return True, "GitHub repo başarıyla güncellendi"
        
    except subprocess.CalledProcessError as e:
        if os.getcwd() != os.path.abspath("."):
            os.chdir("..")
        return False, f"Git işlemi hatası: {e}"
    except Exception as e:
        if os.getcwd() != os.path.abspath("."):
            os.chdir("..")
        return False, f"Push hatası: {e}"

def publish_app(folder_path: str, force: bool = False, push_to_github: bool = True) -> Tuple[bool, str]:
    """
    Ana publish fonksiyonu - GitHub-First yaklaşım
    
    Args:
        folder_path: Publish edilecek uygulama klasörü
        force: Zorla üzerine yaz
        push_to_github: clapp-packages reposuna push et (varsayılan: True)
        
    Returns:
        (success, message)
    """
    print(f"🚀 Publish başlatılıyor: {folder_path}")
    print("=" * 50)
    
    # 1. Klasörü doğrula
    print("1️⃣ Uygulama doğruluyor...")
    is_valid, message, manifest = validate_app_folder(folder_path)
    
    if not is_valid:
        return False, f"Doğrulama hatası: {message}"
    
    app_name = manifest['name']
    app_version = manifest['version']
    print(f"✅ {app_name} v{app_version} doğrulandı")
    
    # 2. GitHub repo'yu güncelle
    print("2️⃣ GitHub repo güncelleniyor...")
    success, message = push_to_clapp_packages_repo(app_name, app_version)
    if not success:
        return False, message
    
    # 3. Lokal packages klasörünü GitHub'dan senkronize et
    print("3️⃣ Lokal packages klasörü senkronize ediliyor...")
    success, message = sync_local_packages_from_github()
    if not success:
        return False, message
    
    return True, f"🎉 '{app_name}' başarıyla GitHub'a publish edildi!"

def sync_local_packages_from_github() -> Tuple[bool, str]:
    """
    GitHub repo'dan lokal packages klasörünü senkronize eder
    """
    try:
        packages_repo_path = "./clapp-packages-repo"
        
        if not os.path.exists(packages_repo_path):
            return False, "clapp-packages repo bulunamadı"
        
        # GitHub repo'dan packages klasörünü kopyala
        clapp_root, _ = find_clapp_root_with_build_index()
        if not clapp_root:
            return False, "Ana clapp dizini bulunamadı"
        
        source_packages = os.path.join(packages_repo_path, "packages")
        target_packages = os.path.join(clapp_root, "packages")
        
        if os.path.exists(source_packages):
            # Mevcut packages klasörünü yedekle
            backup_dir = os.path.join(clapp_root, "backup_current")
            os.makedirs(backup_dir, exist_ok=True)
            
            if os.path.exists(target_packages):
                backup_path = os.path.join(backup_dir, f"packages_backup_{int(time.time())}")
                shutil.move(target_packages, backup_path)
                print(f"📦 Mevcut packages klasörü yedeklendi: {backup_path}")
            
            # GitHub'dan packages klasörünü kopyala
            shutil.copytree(source_packages, target_packages)
            print("✅ GitHub'dan packages klasörü senkronize edildi")
        
        # GitHub'dan index.json'u kopyala
        source_index = os.path.join(packages_repo_path, "index.json")
        target_index = os.path.join(clapp_root, "index.json")
        
        if os.path.exists(source_index):
            shutil.copy(source_index, target_index)
            print("✅ GitHub'dan index.json senkronize edildi")
        
        return True, "Lokal packages klasörü GitHub ile senkronize edildi"
        
    except Exception as e:
        return False, f"Senkronizasyon hatası: {e}"

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Kullanım: python publish_command.py <folder_path> [--push]")
        print("Örnek: python publish_command.py ./my-app")
        print("Örnek: python publish_command.py ./my-app --push")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    force = "--force" in sys.argv
    push_to_github = "--push" in sys.argv
    
    success, message = publish_app(folder_path, force, push_to_github)
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ {message}")
        sys.exit(0)
    else:
        print(f"❌ {message}")
        sys.exit(1)

if __name__ == "__main__":
    main() 