#!/usr/bin/env python3
"""
FilePicker GUI Test
VFS entegreli dosya seçim penceresini test eder
"""

import sys
import os
from pathlib import Path

# PyCloud OS path'ini ekle
sys.path.insert(0, str(Path.cwd()))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel
    from PyQt6.QtCore import Qt
    from cloud.filepicker import open_file_dialog, save_file_dialog, FilePickerFilter
    from core.bridge import BridgeIPCClient
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyQt6 veya FilePicker import hatası: {e}")
    PYQT_AVAILABLE = False

class FilePickerTestWindow(QMainWindow):
    """FilePicker test penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCloud OS - FilePicker Test")
        self.setGeometry(100, 100, 600, 400)
        
        # Bridge bağlantısı
        try:
            self.bridge_client = BridgeIPCClient()
            self.kernel = self.bridge_client.get_kernel_reference()
            self.vfs = self.kernel.get_module('vfs')
            self.connection_status = "✅ Bridge bağlantısı başarılı"
        except Exception as e:
            self.connection_status = f"❌ Bridge bağlantısı başarısız: {e}"
            self.bridge_client = None
            self.kernel = None
            self.vfs = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI kurulumu"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Başlık
        title = QLabel("🔒 PyCloud OS FilePicker & VFS Test")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Bağlantı durumu
        status_label = QLabel(self.connection_status)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)
        
        # VFS stats
        if self.vfs:
            try:
                stats = self.vfs.get_security_stats()
                vfs_info = f"📊 VFS: {stats['total_mounts']} mount, {stats['total_app_profiles']} app profili"
            except Exception as e:
                vfs_info = f"❌ VFS stats hatası: {e}"
        else:
            vfs_info = "❌ VFS modülü bulunamadı"
        
        vfs_label = QLabel(vfs_info)
        vfs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(vfs_label)
        
        # Test butonları
        btn_open_file = QPushButton("📁 Dosya Aç (FilePicker)")
        btn_open_file.clicked.connect(self.test_open_file)
        layout.addWidget(btn_open_file)
        
        btn_save_file = QPushButton("💾 Dosya Kaydet (FilePicker)")
        btn_save_file.clicked.connect(self.test_save_file)
        layout.addWidget(btn_save_file)
        
        btn_multiple_files = QPushButton("📋 Çoklu Dosya Seç")
        btn_multiple_files.clicked.connect(self.test_multiple_files)
        layout.addWidget(btn_multiple_files)
        
        btn_vfs_test = QPushButton("🔒 VFS Erişim Testi")
        btn_vfs_test.clicked.connect(self.test_vfs_access)
        layout.addWidget(btn_vfs_test)
        
        # Sonuç alanı
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(150)
        self.result_text.setPlaceholderText("Test sonuçları burada görünecek...")
        layout.addWidget(self.result_text)
        
    def log_result(self, message: str):
        """Sonuç logla"""
        self.result_text.append(f"[{os.popen('date +%H:%M:%S').read().strip()}] {message}")
        
    def test_open_file(self):
        """Dosya açma testi"""
        try:
            self.log_result("🔍 FilePicker ile dosya açma testi başlatılıyor...")
            
            filters = [
                FilePickerFilter.TEXT_FILES,
                FilePickerFilter.ALL_FILES
            ]
            
            file_path = open_file_dialog(
                app_id="test_app",
                filters=filters,
                parent=self,
                kernel=self.kernel
            )
            
            if file_path:
                self.log_result(f"✅ Dosya seçildi: {file_path}")
                
                # VFS üzerinden dosyayı okumaya çalış
                if self.kernel:
                    fs = self.kernel.get_module('fs')
                    if fs:
                        try:
                            content = fs.read_file(file_path)
                            if content:
                                preview = content[:100] + "..." if len(content) > 100 else content
                                self.log_result(f"📄 Dosya içeriği (önizleme): {preview}")
                            else:
                                self.log_result("❌ Dosya okunamadı")
                        except Exception as e:
                            self.log_result(f"❌ Dosya okuma hatası: {e}")
            else:
                self.log_result("❌ Hiç dosya seçilmedi")
                
        except Exception as e:
            self.log_result(f"❌ FilePicker hatası: {e}")
            
    def test_save_file(self):
        """Dosya kaydetme testi"""
        try:
            self.log_result("💾 FilePicker ile dosya kaydetme testi başlatılıyor...")
            
            filters = [
                FilePickerFilter.TEXT_FILES,
                FilePickerFilter.ALL_FILES
            ]
            
            file_path = save_file_dialog(
                app_id="test_app",
                filters=filters,
                parent=self,
                kernel=self.kernel
            )
            
            if file_path:
                self.log_result(f"✅ Kaydetme yolu seçildi: {file_path}")
                
                # Test içeriği yaz
                test_content = f"PyCloud OS FilePicker Test\\nTarih: {os.popen('date').read().strip()}\\nVFS Test: OK"
                
                if self.kernel:
                    fs = self.kernel.get_module('fs')
                    if fs:
                        try:
                            success = fs.write_file(file_path, test_content, owner="test_app")
                            if success:
                                self.log_result(f"✅ Dosya başarıyla kaydedildi")
                            else:
                                self.log_result(f"❌ Dosya kaydetme başarısız")
                        except Exception as e:
                            self.log_result(f"❌ Dosya yazma hatası: {e}")
            else:
                self.log_result("❌ Kaydetme yolu seçilmedi")
                
        except Exception as e:
            self.log_result(f"❌ FilePicker save hatası: {e}")
            
    def test_multiple_files(self):
        """Çoklu dosya seçim testi"""
        try:
            self.log_result("📋 Çoklu dosya seçim testi başlatılıyor...")
            self.log_result("ℹ️ Bu özellik henüz FilePicker'da implement edilmemiş")
            
        except Exception as e:
            self.log_result(f"❌ Çoklu seçim hatası: {e}")
            
    def test_vfs_access(self):
        """VFS erişim testi"""
        try:
            self.log_result("🔒 VFS erişim kontrolü testi başlatılıyor...")
            
            if not self.vfs:
                self.log_result("❌ VFS modülü bulunamadı")
                return
                
            # Test app profili oluştur
            try:
                profile = self.vfs.get_app_profile("test_app")
                if not profile:
                    self.log_result("📝 test_app profili oluşturuluyor...")
                    profile = self.vfs.create_app_profile("test_app", ["/home", "/temp"])
                    self.log_result("✅ Test app profili oluşturuldu")
                else:
                    self.log_result("✅ Test app profili mevcut")
                    
                # Mount bilgilerini al
                mount_info = self.vfs.get_mount_info()
                self.log_result(f"🗂️ Mount noktaları: {list(mount_info.keys())}")
                
                # Güvenlik stats
                stats = self.vfs.get_security_stats()
                self.log_result(f"📊 VFS Stats: {stats['total_app_profiles']} profil, {stats['active_sandboxes']} sandbox")
                
            except Exception as e:
                self.log_result(f"❌ VFS profil hatası: {e}")
                
        except Exception as e:
            self.log_result(f"❌ VFS test hatası: {e}")

def main():
    """Ana fonksiyon"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 mevcut değil, GUI test yapılamıyor")
        return
        
    print("🚀 FilePicker GUI Test başlatılıyor...")
    
    app = QApplication(sys.argv)
    
    # Test penceresini oluştur
    window = FilePickerTestWindow()
    window.show()
    
    print("✅ Test penceresi açıldı")
    print("ℹ️ Test butonlarını kullanarak FilePicker'ı test edin")
    
    # Event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 