"""
Cloud Settings - Bildirimler Sayfası
Bildirim tercihleri ve uygulama bildirimleri
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from .base_page import BasePage

class NotificationsPage(BasePage):
    """Bildirim ayarları sayfası"""
    
    def __init__(self, kernel=None):
        super().__init__("notifications", "Bildirimler", "🔔", kernel)
    
    def setup_ui(self):
        """UI kurulumu"""
        super().setup_ui()
        
        # Genel bildirim ayarları
        self.setup_general_section()
        
        # Görünüm ayarları
        self.setup_display_section()
        
        # Uygulama bildirimleri
        self.setup_app_notifications()
        
        self.add_spacer()
    
    def setup_general_section(self):
        """Genel bildirim ayarları"""
        group = self.add_group("Genel")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Bildirimleri etkinleştir",
            "enable_notifications",
            "Sistem ve uygulama bildirimlerini göster"
        )
        
        self.add_checkbox(
            layout,
            "Bildirim sesi",
            "notification_sound",
            "Bildirim geldiğinde ses çal"
        )
        
        self.add_checkbox(
            layout,
            "Bildirim önizlemesi göster",
            "show_preview",
            "Bildirim içeriğini önizleme olarak göster"
        )
    
    def setup_display_section(self):
        """Görünüm ayarları"""
        group = self.add_group("Görünüm")
        layout = QVBoxLayout(group)
        
        self.add_combobox(
            layout,
            "Konum",
            "notification_position",
            ["Sağ Üst", "Sol Üst", "Sağ Alt", "Sol Alt", "Merkez"],
            "Bildirimlerin ekranda görüneceği konum"
        )
        
        self.add_spinbox(
            layout,
            "Süre",
            "notification_duration",
            1, 30, 5,
            " saniye",
            "Bildirimlerin ekranda kalma süresi"
        )
        
        self.add_spinbox(
            layout,
            "Maksimum sayı",
            "max_notifications",
            1, 10, 3,
            "",
            "Aynı anda gösterilebilecek maksimum bildirim sayısı"
        )
    
    def setup_app_notifications(self):
        """Uygulama bildirimleri"""
        group = self.add_group("Uygulama Bildirimleri")
        layout = QVBoxLayout(group)
        
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QCheckBox
        from PyQt6.QtCore import Qt
        
        # Uygulama listesi
        app_list = QListWidget()
        app_items = [
            ("Sistem", True),
            ("Güvenlik", True),
            ("Güncellemeler", True),
            ("App Store", False),
            ("Cloud Files", False)
        ]
        
        for app_name, enabled in app_items:
            item = QListWidgetItem(app_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            app_list.addItem(item)
        
        layout.addWidget(app_list) 