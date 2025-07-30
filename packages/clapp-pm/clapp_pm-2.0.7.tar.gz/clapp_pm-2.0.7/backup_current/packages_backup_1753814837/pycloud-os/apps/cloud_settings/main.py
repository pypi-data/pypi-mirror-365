#!/usr/bin/env python3
"""
Cloud Settings v2.0.0 - Modern Sistem Ayarları
PyCloud OS için gelişmiş ayar yönetimi uygulaması
"""

import sys
import os
import logging
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
except ImportError:
    print("❌ PyQt6 bulunamadı!")
    sys.exit(1)

try:
    from core import CloudSettings
except ImportError as e:
    print(f"❌ Core modülleri yüklenemedi: {e}")
    sys.exit(1)

def setup_logging():
    """Logging sistemini kur"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "cloud_settings.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_kernel():
    """Kernel referansını al"""
    try:
        # PyCloud OS kernel'ını bulmaya çalış
        import sys
        from pathlib import Path
        
        # Kernel modülünü bul
        possible_paths = [
            Path(__file__).parent.parent.parent / "kernel",
            Path(__file__).parent.parent / "kernel", 
            Path("kernel"),
            Path("../kernel"),
            Path("../../kernel")
        ]
        
        for kernel_path in possible_paths:
            if kernel_path.exists() and (kernel_path / "__init__.py").exists():
                sys.path.insert(0, str(kernel_path.parent))
                try:
                    from kernel import PyCloudKernel  # type: ignore
                    return PyCloudKernel.get_instance()
                except (ImportError, ModuleNotFoundError):
                    continue
                    
    except Exception as e:
        logging.warning(f"Kernel bulunamadı: {e}")
    
    return None

def main():
    """Ana fonksiyon"""
    setup_logging()
    logger = logging.getLogger("CloudSettings.Main")
    
    logger.info("🚀 Cloud Settings v2.0.0 başlatılıyor...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Settings")
    app.setApplicationVersion("2.0.0")
    
    try:
        kernel = get_kernel()
        main_window = CloudSettings(kernel)
        main_window.show()
        
        logger.info("✅ Cloud Settings başarıyla başlatıldı")
        return app.exec()
        
    except Exception as e:
        logger.error(f"❌ Kritik hata: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    exit_code = main()
    sys.exit(exit_code) 