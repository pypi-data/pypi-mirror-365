#!/usr/bin/env python3
"""
where_command.py - Uygulama konumu bulma komutları

Bu modül clapp uygulamalarının sistemdeki konumlarını
bulmak için gerekli fonksiyonları sağlar.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from package_registry import get_apps_directory, app_exists, get_manifest
from platform_utils import get_clapp_home

def locate_app_path(app_name: str) -> Optional[str]:
    """
    Uygulamanın sistemdeki konumunu bulur
    
    Args:
        app_name: Aranacak uygulama adı
        
    Returns:
        Uygulama dizininin tam yolu veya None
    """
    if not app_exists(app_name):
        return None
    
    apps_dir = get_apps_directory()
    app_path = os.path.join(apps_dir, app_name)
    
    if os.path.exists(app_path):
        return os.path.abspath(app_path)
    
    return None

def list_all_app_locations() -> Dict[str, str]:
    """
    Sistemdeki tüm uygulamaların konumlarını listeler
    
    Returns:
        Uygulama adı -> konum eşleştirmesi
    """
    from package_registry import list_packages
    
    locations = {}
    packages = list_packages()
    
    for package in packages:
        app_name = package['name']
        app_path = locate_app_path(app_name)
        if app_path:
            locations[app_name] = app_path
    
    return locations

def get_app_details(app_name: str) -> Optional[Dict]:
    """
    Uygulama hakkında detaylı bilgi döndürür
    
    Args:
        app_name: Uygulama adı
        
    Returns:
        Uygulama detayları veya None
    """
    app_path = locate_app_path(app_name)
    if not app_path:
        return None
    
    manifest = get_manifest(app_name)
    if not manifest:
        return None
    
    return {
        "name": app_name,
        "path": app_path,
        "version": manifest.get('version', '0.0.0'),
        "language": manifest.get('language', 'unknown'),
        "description": manifest.get('description', ''),
        "entry": manifest.get('entry', ''),
        "dependencies": manifest.get('dependencies', []),
        "size": get_directory_size(app_path)
    }

def get_directory_size(directory: str) -> int:
    """
    Dizin boyutunu hesaplar
    
    Args:
        directory: Dizin yolu
        
    Returns:
        Dizin boyutu (byte)
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except (OSError, PermissionError):
        pass
    
    return total_size

def format_size(size_bytes: int) -> str:
    """
    Byte cinsinden boyutu okunabilir formata çevirir
    
    Args:
        size_bytes: Byte cinsinden boyut
        
    Returns:
        Formatlanmış boyut string'i
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def handle_where_command(args):
    """where komutunu işler"""
    app_name = args.app_name
    
    if app_name:
        # Belirli bir uygulama için konum
        app_path = locate_app_path(app_name)
        if app_path:
            print(f"📍 {app_name} konumu:")
            print(f"   {app_path}")
            
            # Detaylı bilgi
            details = get_app_details(app_name)
            if details:
                print(f"\n📊 Uygulama Detayları:")
                print(f"   Sürüm: {details['version']}")
                print(f"   Dil: {details['language']}")
                print(f"   Boyut: {format_size(details['size'])}")
                print(f"   Giriş Noktası: {details['entry']}")
                
                if details['dependencies']:
                    print(f"   Bağımlılıklar: {', '.join(details['dependencies'])}")
        else:
            print(f"❌ '{app_name}' uygulaması bulunamadı")
            return False, f"Uygulama bulunamadı: {app_name}"
    else:
        # Tüm uygulamaların konumları
        locations = list_all_app_locations()
        
        if not locations:
            print("📦 Hiç uygulama kurulu değil")
            return True, "Hiç uygulama kurulu değil"
        
        print("📍 Kurulu Uygulamalar:")
        print("=" * 50)
        
        for app_name, app_path in locations.items():
            details = get_app_details(app_name)
            if details:
                print(f"📦 {app_name}")
                print(f"   Konum: {app_path}")
                print(f"   Sürüm: {details['version']}")
                print(f"   Boyut: {format_size(details['size'])}")
                print()
    
    return True, "Konum bilgileri gösterildi"

if __name__ == "__main__":
    # Test için
    print("where_command.py test")
    locations = list_all_app_locations()
    print(f"Bulunan uygulamalar: {list(locations.keys())}") 