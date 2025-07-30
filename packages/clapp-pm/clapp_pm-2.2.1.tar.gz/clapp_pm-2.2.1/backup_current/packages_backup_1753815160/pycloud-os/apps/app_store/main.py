#!/usr/bin/env python3
"""
App Store - PyCloud OS Modern Uygulama Mağazası
Ana başlatıcı dosyası
"""

import sys
import os
from pathlib import Path

# PyCloud modüllerini yüklemek için sistem yolunu ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Ana fonksiyon"""
    try:
        # App Store uygulamasını başlat
        from apps.app_store.core.appstore import main as appstore_main
        return appstore_main()
        
    except ImportError as e:
        print(f"App Store modülü yüklenemedi: {e}")
        print("Lütfen PyCloud OS'i doğru şekilde yüklediğinizden emin olun.")
        return 1
    except Exception as e:
        print(f"App Store başlatılamadı: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 