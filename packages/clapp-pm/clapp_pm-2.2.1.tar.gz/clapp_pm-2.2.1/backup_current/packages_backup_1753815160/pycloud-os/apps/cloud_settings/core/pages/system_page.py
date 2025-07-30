"""
Cloud Settings - Sistem Sayfası
Genel sistem ayarları ve performans seçenekleri
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from .base_page import BasePage

class SystemPage(BasePage):
    """Sistem ayarları sayfası"""
    
    def __init__(self, kernel=None):
        super().__init__("system", "Sistem", "💻", kernel)
    
    def setup_ui(self):
        """UI kurulumu"""
        super().setup_ui()
        
        # Başlangıç ayarları
        self.setup_startup_section()
        
        # Güvenlik ayarları
        self.setup_security_section()
        
        # Performans ayarları
        self.setup_performance_section()
        
        # Dil ve bölge ayarları
        self.setup_locale_section()
        
        # Sistem bilgileri
        self.setup_system_info()
        
        self.add_spacer()
    
    def setup_startup_section(self):
        """Başlangıç ayarları bölümü"""
        group = self.add_group("Başlangıç")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Otomatik giriş",
            "auto_login",
            "Sistem açılışında otomatik olarak giriş yap"
        )
        
        self.add_checkbox(
            layout,
            "Başlangıç sesi",
            "startup_sound",
            "Sistem açılışında ses çal"
        )
    
    def setup_security_section(self):
        """Güvenlik ayarları bölümü"""
        group = self.add_group("Güvenlik")
        layout = QVBoxLayout(group)
        
        self.add_spinbox(
            layout,
            "Oturum zaman aşımı",
            "session_timeout",
            0, 1440, 0,
            " dakika",
            "0 = sınırsız oturum süresi"
        )
        
        self.add_checkbox(
            layout,
            "Uyku modundan çıkarken şifre iste",
            "require_password",
            "Sistem uyku modundan çıkarken parola iste"
        )
    
    def setup_performance_section(self):
        """Performans ayarları bölümü"""
        group = self.add_group("Performans")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Animasyonları etkinleştir",
            "animations",
            "UI animasyonları ve geçiş efektleri"
        )
        
        self.add_checkbox(
            layout,
            "Şeffaflık efektleri",
            "transparency",
            "Pencere ve menü şeffaflık efektleri"
        )
        
        self.add_spinbox(
            layout,
            "Bellek sınırı",
            "memory_limit",
            256, 8192, 1024,
            " MB",
            "Sistem bellek kullanım sınırı"
        )
    
    def setup_locale_section(self):
        """Dil ve bölge ayarları bölümü"""
        group = self.add_group("Dil ve Bölge")
        layout = QVBoxLayout(group)
        
        self.add_combobox(
            layout,
            "Dil",
            "language",
            ["Türkçe (tr_TR)", "English (en_US)", "Deutsch (de_DE)"],
            "Sistem arayüz dili"
        )
        
        self.add_combobox(
            layout,
            "Zaman Dilimi",
            "timezone",
            ["Europe/Istanbul", "UTC", "Europe/London", "America/New_York"],
            "Sistem zaman dilimi"
        )
    
    def setup_system_info(self):
        """Sistem bilgileri bölümü"""
        group = self.add_group("Sistem Bilgileri")
        layout = QVBoxLayout(group)
        
        from PyQt6.QtWidgets import QFormLayout, QLabel
        
        info_layout = QFormLayout()
        
        info_layout.addRow("İşletim Sistemi:", QLabel("PyCloud OS 0.9.0-dev"))
        info_layout.addRow("Python Sürümü:", QLabel(f"{sys.version.split()[0]}"))
        info_layout.addRow("PyQt Sürümü:", QLabel("6.x"))
        
        layout.addLayout(info_layout) 