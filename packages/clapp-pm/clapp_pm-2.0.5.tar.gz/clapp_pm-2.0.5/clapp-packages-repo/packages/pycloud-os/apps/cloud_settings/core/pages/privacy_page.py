"""
Cloud Settings - Gizlilik Sayfası
Güvenlik ve gizlilik ayarları
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from .base_page import BasePage

class PrivacyPage(BasePage):
    """Gizlilik ayarları sayfası"""
    
    def __init__(self, kernel=None):
        super().__init__("privacy", "Gizlilik", "🔒", kernel)
    
    def setup_ui(self):
        """UI kurulumu"""
        super().setup_ui()
        
        # Veri toplama
        self.setup_data_collection()
        
        # Uygulama izinleri
        self.setup_app_permissions()
        
        # Dosya erişimi
        self.setup_file_access()
        
        self.add_spacer()
    
    def setup_data_collection(self):
        """Veri toplama ayarları"""
        group = self.add_group("Veri Toplama")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Analitik verilerini paylaş",
            "analytics",
            "Anonim kullanım verilerini geliştirme için paylaş"
        )
        
        self.add_checkbox(
            layout,
            "Çökme raporları gönder",
            "crash_reports",
            "Hata ayıklama için çökme raporları gönder"
        )
        
        self.add_checkbox(
            layout,
            "Konum servislerini etkinleştir",
            "location_services",
            "Uygulamaların konum bilgisine erişmesine izin ver"
        )
    
    def setup_app_permissions(self):
        """Uygulama izinleri"""
        group = self.add_group("Uygulama İzinleri")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Kamera erişimi",
            "camera_access",
            "Uygulamaların kameraya erişmesine izin ver"
        )
        
        self.add_checkbox(
            layout,
            "Mikrofon erişimi",
            "microphone_access",
            "Uygulamaların mikrofona erişmesine izin ver"
        )
    
    def setup_file_access(self):
        """Dosya erişimi"""
        group = self.add_group("Dosya Erişimi")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Dosya erişim günlüğü",
            "file_access_logging",
            "Dosya erişimlerini günlüğe kaydet"
        ) 