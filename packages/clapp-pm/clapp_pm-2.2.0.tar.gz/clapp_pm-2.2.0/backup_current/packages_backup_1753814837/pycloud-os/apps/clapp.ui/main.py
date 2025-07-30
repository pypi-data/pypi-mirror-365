#!/usr/bin/env python3
"""
Clapp UI - PyCloud OS App Store
Ana başlatıcı dosyası
"""

import sys
import os

# PyCloud modüllerini yüklemek için sistem yolunu ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def main():
    """Ana fonksiyon"""
    try:
        # Clapp UI uygulamasını başlat
        from clapp.ui import main as clapp_main
        return clapp_main()
        
    except ImportError as e:
        print(f"Clapp UI modülü yüklenemedi: {e}")
        print("Lütfen PyCloud OS'i doğru şekilde yüklediğinizden emin olun.")
        return 1
    except Exception as e:
        print(f"Clapp UI başlatılamadı: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 