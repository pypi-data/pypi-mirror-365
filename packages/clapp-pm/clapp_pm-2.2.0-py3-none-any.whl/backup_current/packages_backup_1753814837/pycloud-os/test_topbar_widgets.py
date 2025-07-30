#!/usr/bin/env python3
"""
PyCloud OS Topbar Widget Konumlandırma Testi
Denetim merkezi ve diğer widget'ların ekran içinde doğru konumlandırıldığını test eder
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt
from rain.topbar import RainTopbar

class MockKernel:
    """Test için mock kernel"""
    def __init__(self):
        self.running = True
        
    def get_uptime(self):
        return 3600  # 1 saat
        
    def get_memory_usage(self):
        return 45.2  # %45.2
        
    def get_cpu_usage(self):
        return 23.1  # %23.1

class TopbarTestWindow(QMainWindow):
    """Topbar test penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCloud OS Topbar Widget Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Mock kernel
        self.kernel = MockKernel()
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Topbar oluştur
        self.topbar = RainTopbar(self.kernel)
        layout.addWidget(self.topbar)
        
        # Test alanı
        test_widget = QWidget()
        test_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #87CEEB,
                    stop:1 #4682B4);
            }
        """)
        
        test_layout = QVBoxLayout(test_widget)
        test_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Test butonları
        test_buttons = [
            ("🔔 Bildirim Widget'ını Test Et", self.test_notification_widget),
            ("🕐 Saat Widget'ını Test Et", self.test_clock_widget),
            ("⚙️ Denetim Merkezi Widget'ını Test Et", self.test_control_center_widget),
            ("🔍 CloudSearch Widget'ını Test Et", self.test_cloudsearch_widget),
            ("🎯 Tüm Widget'ları Test Et", self.test_all_widgets),
            ("❌ Tüm Widget'ları Kapat", self.close_all_widgets)
        ]
        
        for text, handler in test_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(300, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.9);
                    border: 2px solid rgba(0, 0, 0, 0.2);
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #333;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 1.0);
                    border: 2px solid rgba(0, 0, 0, 0.3);
                }
                QPushButton:pressed {
                    background: rgba(240, 240, 240, 1.0);
                }
            """)
            btn.clicked.connect(handler)
            test_layout.addWidget(btn)
        
        layout.addWidget(test_widget)
        
        print("🚀 Topbar Widget Test Penceresi Hazır!")
        print("📍 Widget'ların ekran içinde doğru konumlandırıldığını test edin")
        
    def test_notification_widget(self):
        """Bildirim widget'ını test et"""
        print("🔔 Bildirim widget'ı test ediliyor...")
        self.topbar.show_flet_notification_widget()
        
    def test_clock_widget(self):
        """Saat widget'ını test et"""
        print("🕐 Saat widget'ı test ediliyor...")
        self.topbar.show_flet_clock_widget()
        
    def test_control_center_widget(self):
        """Denetim merkezi widget'ını test et"""
        print("⚙️ Denetim merkezi widget'ı test ediliyor...")
        self.topbar.show_flet_control_center_widget()
        
    def test_cloudsearch_widget(self):
        """CloudSearch widget'ını test et"""
        print("🔍 CloudSearch widget'ı test ediliyor...")
        self.topbar.show_flet_cloudsearch_widget()
        
    def test_all_widgets(self):
        """Tüm widget'ları test et"""
        print("🎯 Tüm widget'lar test ediliyor...")
        self.test_notification_widget()
        self.test_clock_widget()
        self.test_control_center_widget()
        self.test_cloudsearch_widget()
        
    def close_all_widgets(self):
        """Tüm widget'ları kapat"""
        print("❌ Tüm widget'lar kapatılıyor...")
        self.topbar.hide_all_html_widgets()

def main():
    """Ana test fonksiyonu"""
    app = QApplication(sys.argv)
    
    # Test penceresi oluştur
    window = TopbarTestWindow()
    window.show()
    
    print("\n" + "="*60)
    print("🧪 PYCLOUD OS TOPBAR WIDGET KONUMLANDIRMA TESTİ")
    print("="*60)
    print("📋 Test Senaryoları:")
    print("   1. Her widget'ın ekran içinde açılması")
    print("   2. Widget'ların doğru konumlandırılması")
    print("   3. Ekran sınırlarının kontrol edilmesi")
    print("   4. CloudSearch ikonu yüklenmesi")
    print("="*60)
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 