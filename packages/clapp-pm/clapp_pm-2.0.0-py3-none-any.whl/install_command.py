#!/usr/bin/env python3
"""
install_command.py - clapp Install Command

Bu modül 'clapp install <app_name>' komutunu uygular.
Index.json'dan uygulama bilgilerini alıp GitHub'dan indirerek
yerel apps/ klasörüne kurar.
"""

import os
import json
import shutil
import urllib.request
import zipfile
import tempfile
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from manifest_validator import validate_manifest_verbose
from progress_utils import download_with_progress, extract_with_progress, show_success_message, show_error_message

def get_apps_directory() -> str:
    """Uygulamaların kurulacağı dizini döndürür"""
    # Kullanıcının home dizininde .clapp klasörü oluştur
    home_dir = Path.home()
    clapp_dir = home_dir / ".clapp"
    apps_dir = clapp_dir / "apps"
    
    # Klasörleri oluştur
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    return str(apps_dir)

def load_index(index_path: str = "index.json") -> Tuple[bool, str, Optional[list]]:
    """
    Index.json dosyasını yükler
    
    Returns:
        (success, message, apps_list)
    """
    try:
        # Her zaman GitHub'dan güncel index.json'u indir
        print("🔄 GitHub'dan index.json indiriliyor...")
        url = "https://raw.githubusercontent.com/mburakmmm/clapp-packages/main/index.json"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            apps = json.loads(response.read().decode('utf-8'))
            # Yerel kopyasını kaydet
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(apps, f, indent=2, ensure_ascii=False)
            return True, "GitHub'dan index indirildi", apps
            
    except urllib.error.URLError as e:
        # Network hatası durumunda yerel dosyayı dene
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                apps = json.load(f)
            return True, "Yerel index yüklendi (network hatası)", apps
        else:
            return False, f"Network hatası: {e}", None
    except json.JSONDecodeError as e:
        return False, f"JSON parse hatası: {e}", None
    except Exception as e:
        return False, f"Index yükleme hatası: {e}", None

def find_app_in_index(app_name: str, apps: list) -> Optional[Dict[str, Any]]:
    """Index'te uygulama arar"""
    for app in apps:
        if app.get('name') == app_name:
            return app
    return None

def download_app_from_github(app_info: Dict[str, Any], temp_dir: str) -> Tuple[bool, str]:
    """
    GitHub'dan uygulama dosyalarını indirir
    
    Returns:
        (success, message)
    """
    try:
        repo_url = app_info.get('repo_url', 'https://github.com/mburakmmm/clapp-packages')
        app_name = app_info['name']
        
        # GitHub zip URL'si oluştur
        if 'github.com' in repo_url:
            # https://github.com/user/repo -> https://github.com/user/repo/archive/refs/heads/main.zip
            zip_url = repo_url + "/archive/refs/heads/main.zip"
        else:
            return False, f"Desteklenmeyen repo URL: {repo_url}"
        
        # Progress bar ile indir
        zip_path = os.path.join(temp_dir, "repo.zip")
        success = download_with_progress(zip_url, zip_path, f"📦 {app_name} indiriliyor")
        
        if not success:
            return False, "İndirme başarısız"
        
        # Progress bar ile çıkar
        success = extract_with_progress(zip_path, temp_dir, f"📦 {app_name} çıkarılıyor")
        
        if not success:
            return False, "Çıkarma başarısız"
        
        # Çıkarılan klasörü bul (genellikle repo-main formatında)
        extracted_folders = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_folders:
            return False, "Çıkarılan klasör bulunamadı"
        
        extracted_folder = extracted_folders[0]
        
        # YENİ: packages/{app_name} klasörünü bul
        packages_path = os.path.join(temp_dir, extracted_folder, "packages")
        app_source_path = os.path.join(packages_path, app_name)
        
        if not os.path.exists(app_source_path):
            return False, f"Uygulama klasörü bulunamadı: packages/{app_name}"
        
        return True, app_source_path
        
    except Exception as e:
        return False, f"İndirme hatası: {e}"

def install_app_locally(app_name: str, source_path: str) -> Tuple[bool, str]:
    """
    Uygulamayı yerel apps klasörüne kurar
    
    Returns:
        (success, message)
    """
    try:
        apps_dir = get_apps_directory()
        target_path = os.path.join(apps_dir, app_name)
        
        # Hedef klasör varsa sil
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            print(f"⚠️  Mevcut {app_name} kaldırıldı")
        
        # Kopyala
        shutil.copytree(source_path, target_path)
        
        # Manifest'i doğrula
        manifest_path = os.path.join(target_path, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            is_valid, errors = validate_manifest_verbose(manifest)
            if not is_valid:
                shutil.rmtree(target_path)
                return False, f"Manifest doğrulama hatası: {errors}"
        
        show_success_message(f"'{app_name}' başarıyla yüklendi!")
        
        # Bağımlılık çözümleme entegrasyonu
        print("5️⃣ Bağımlılıklar kontrol ediliyor...")
        from dependency_resolver import check_and_install_python_dependencies, check_and_install_lua_dependencies, check_engine_availability
        
        # Engine kontrolü
        engine_available, engine_message, engine_info = check_engine_availability(target_path)
        if not engine_available:
            print(f"⚠️  {engine_message}")
        
        # Dil bazlı bağımlılık kontrolü
        language = manifest.get('language', 'unknown')
        if language == 'python':
            success, message, missing_packages = check_and_install_python_dependencies(target_path)
            if success:
                if missing_packages:
                    print(f"✅ {message}")
                else:
                    print("✅ Tüm Python bağımlılıkları zaten kurulu")
            else:
                print(f"⚠️  Python bağımlılık hatası: {message}")
        
        elif language == 'lua':
            success, message, missing_packages = check_and_install_lua_dependencies(target_path)
            if success:
                if missing_packages:
                    print(f"✅ {message}")
                else:
                    print("✅ Tüm Lua bağımlılıkları zaten kurulu")
            else:
                print(f"⚠️  Lua bağımlılık hatası: {message}")
        
        return True, f"Uygulama kuruldu: {target_path}"
        
    except Exception as e:
        return False, f"Kurulum hatası: {e}"

def install_app(app_name: str) -> Tuple[bool, str]:
    """
    Ana install fonksiyonu
    
    Args:
        app_name: Kurulacak uygulamanın adı
        
    Returns:
        (success, message)
    """
    print(f"🚀 Kurulum başlatılıyor: {app_name}")
    print("=" * 50)
    
    # 1. Index'i yükle
    print("1️⃣ Index yükleniyor...")
    index_success, index_message, apps = load_index()
    
    if not index_success:
        return False, f"Index yükleme hatası: {index_message}"
    
    if apps is None:
        return False, "Index yüklendi ama uygulama listesi boş"
    
    print(f"✅ {len(apps)} uygulama listelendi")
    
    # 2. Uygulamayı index'te ara
    print("2️⃣ Uygulama aranıyor...")
    app_info = find_app_in_index(app_name, apps)
    
    if not app_info:
        available_apps = [app['name'] for app in apps]
        return False, f"Uygulama bulunamadı: {app_name}\nMevcut uygulamalar: {', '.join(available_apps)}"
    
    print(f"✅ {app_name} v{app_info['version']} bulundu")
    
    # 3. Geçici klasör oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        print("3️⃣ Uygulama indiriliyor...")
        
        # GitHub'dan indir
        download_success, download_result = download_app_from_github(app_info, temp_dir)
        
        if not download_success:
            return False, f"İndirme hatası: {download_result}"
        
        source_path = download_result
        print(f"✅ İndirme tamamlandı")
        
        # 4. Yerel kurulum
        print("4️⃣ Uygulama kuruluyor...")
        install_success, install_message = install_app_locally(app_name, source_path)
        
        if not install_success:
            return False, install_message
    
    return True, f"🎉 '{app_name}' başarıyla kuruldu!"

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Kullanım: python install_command.py <app_name>")
        print("Örnek: python install_command.py hello-python")
        sys.exit(1)
    
    app_name = sys.argv[1]
    
    success, message = install_app(app_name)
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ {message}")
        print(f"📍 Kurulum dizini: {get_apps_directory()}")
        sys.exit(0)
    else:
        print(f"❌ {message}")
        sys.exit(1)

if __name__ == "__main__":
    main() 