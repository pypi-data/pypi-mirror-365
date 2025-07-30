#!/usr/bin/env python3
"""
Cloud Files App Launcher
PyCloud OS Dosya Yöneticisi Başlatıcısı
"""

import sys
import os
import argparse
from pathlib import Path

# PyCloud OS core modüllerini ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from PyQt6.QtWidgets import QApplication
    from cloud.files import CloudFiles
    
    def main():
        """Files uygulamasını başlat"""
        # Komut satırı parametrelerini parse et
        parser = argparse.ArgumentParser(description='PyCloud OS Files')
        parser.add_argument('--open-path', type=str, help='Açılacak dizin yolu')
        parser.add_argument('--open-file', type=str, help='Açılacak dosya yolu')
        args, unknown = parser.parse_known_args()
        
        # QApplication oluştur veya var olanı kullan
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("Cloud Files")
            app.setApplicationVersion("2.0.0")
        
        # Kernel referansı - Bridge sistemi üzerinden al (opsiyonel)
        kernel = None
        try:
            # Bridge sistemi üzerinden kernel'e erişim
            from core.bridge import get_bridge_manager
            bridge_manager = get_bridge_manager()
            if bridge_manager:
                kernel = bridge_manager.get_kernel_reference()
                print("✅ Kernel referansı bridge üzerinden alındı")
            else:
                print("⚠️ Bridge manager bulunamadı, standalone modda çalışılıyor")
        except Exception as e:
            print(f"⚠️ Bridge bağlantısı kurulamadı: {e}")
            print("📁 Standalone modda çalışılıyor...")
        
        # Files'ı oluştur (yeni CloudFiles sınıfı kernel parametresi almıyor)
        files_app = CloudFiles()
        
        # Dizin açma parametresi varsa o dizine git
        if args.open_path:
            dir_path = Path(args.open_path)
            if dir_path.exists() and dir_path.is_dir():
                files_app.navigate_to_path(dir_path)
                print(f"📂 Açılan dizin: {dir_path}")
            else:
                print(f"❌ Dizin bulunamadı: {args.open_path}")
        
        # Dosya açma parametresi varsa dosyayı aç
        if args.open_file:
            file_path = Path(args.open_file)
            if file_path.exists():
                if file_path.is_dir():
                    files_app.navigate_to_path(file_path)
                    print(f"📂 Açılan klasör: {file_path}")
                else:
                    # Dosyanın bulunduğu dizine git
                    files_app.navigate_to_path(file_path.parent)
                    print(f"📄 Dosya konumu: {file_path}")
            else:
                print(f"❌ Dosya bulunamadı: {args.open_file}")
        
        # Pencereyi göster
        files_app.show()
        print("🚀 Cloud Files başlatıldı!")
        
        # Event loop'u başlat
        return app.exec()

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ Cloud Files başlatılamadı: {e}")
    print("⚠️ Lütfen PyCloud OS bağımlılıklarının yüklü olduğundan emin olun.")
    print("💡 PyQt6 kurulu mu? pip install PyQt6")
    sys.exit(1) 