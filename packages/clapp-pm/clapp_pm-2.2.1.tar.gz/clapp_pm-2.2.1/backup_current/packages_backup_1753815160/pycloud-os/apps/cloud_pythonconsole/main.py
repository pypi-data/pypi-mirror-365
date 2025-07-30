#!/usr/bin/env python3
"""
Cloud Python Console - Ana Başlatıcı
PyCloud OS Python REPL Konsolu
"""

import sys
import os
import logging

# PyCloud modül yolunu ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from cloud.pythonconsole import PythonConsole, main as console_main
    from PyQt6.QtWidgets import QApplication
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import hatası: {e}")
    IMPORTS_OK = False

def main():
    """Ana fonksiyon"""
    if not IMPORTS_OK:
        print("Gerekli modüller yüklenemedi.")
        return 1
    
    try:
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # QApplication kontrol
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("Cloud Python Console")
            app.setApplicationVersion("1.0.0")
        
        # Kernel referansını al (eğer varsa)
        kernel = None
        try:
            from core.kernel import get_kernel
            kernel = get_kernel()
        except ImportError:
            pass
        
        # Console penceresi oluştur
        console = PythonConsole(kernel)
        console.show()
        
        # Event loop başlat (sadece ana uygulama değilse)
        if not QApplication.instance().property("pycloud_main_app"):
            return app.exec()
        
        return 0
        
    except Exception as e:
        print(f"Uygulama başlatma hatası: {e}")
        logging.exception("Python Console başlatma hatası")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 