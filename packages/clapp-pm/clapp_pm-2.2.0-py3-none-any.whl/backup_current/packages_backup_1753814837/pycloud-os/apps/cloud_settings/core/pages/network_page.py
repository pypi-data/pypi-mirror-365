"""
Cloud Settings - Ağ Sayfası
İnternet ve ağ bağlantı ayarları
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from .base_page import BasePage

class NetworkPage(BasePage):
    """Ağ ayarları sayfası"""
    
    def __init__(self, kernel=None):
        super().__init__("network", "Ağ", "🌐", kernel)
    
    def setup_ui(self):
        """UI kurulumu"""
        super().setup_ui()
        
        # Bağlantı ayarları
        self.setup_connection_section()
        
        # Proxy ayarları
        self.setup_proxy_section()
        
        # DNS ayarları
        self.setup_dns_section()
        
        self.add_spacer()
    
    def setup_connection_section(self):
        """Bağlantı ayarları"""
        group = self.add_group("Bağlantı")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Otomatik bağlan",
            "auto_connect",
            "Sistem açılışında otomatik olarak ağa bağlan"
        )
        
        self.add_spinbox(
            layout,
            "Bağlantı zaman aşımı",
            "connection_timeout",
            5, 120, 30,
            " saniye",
            "Ağ bağlantısı için maksimum bekleme süresi"
        )
    
    def setup_proxy_section(self):
        """Proxy ayarları"""
        group = self.add_group("Proxy")
        layout = QVBoxLayout(group)
        
        self.add_checkbox(
            layout,
            "Proxy kullan",
            "proxy_enabled",
            "İnternet bağlantısı için proxy sunucusu kullan"
        )
        
        from PyQt6.QtWidgets import QLineEdit
        
        # Proxy host
        proxy_host = QLineEdit()
        proxy_host.setPlaceholderText("proxy.example.com")
        proxy_host.textChanged.connect(lambda text: self.on_setting_changed("proxy_host", text))
        self.widgets["proxy_host"] = proxy_host
        self.add_setting_row(layout, "Proxy Sunucusu", proxy_host, "Proxy sunucusunun adresi")
        
        # Proxy port
        self.add_spinbox(
            layout,
            "Port",
            "proxy_port",
            1, 65535, 8080,
            "",
            "Proxy sunucusunun port numarası"
        )
    
    def setup_dns_section(self):
        """DNS ayarları"""
        group = self.add_group("DNS")
        layout = QVBoxLayout(group)
        
        from PyQt6.QtWidgets import QTextEdit
        
        # DNS sunucuları
        dns_text = QTextEdit()
        dns_text.setMaximumHeight(100)
        dns_text.setPlaceholderText("8.8.8.8\n8.8.4.4")
        dns_text.textChanged.connect(self.on_dns_changed)
        self.widgets["dns_servers"] = dns_text
        
        self.add_setting_row(layout, "DNS Sunucuları", dns_text, "Her satıra bir DNS sunucusu IP adresi")
    
    def on_dns_changed(self):
        """DNS sunucuları değişti"""
        dns_text = self.widgets["dns_servers"]
        dns_list = [line.strip() for line in dns_text.toPlainText().split('\n') if line.strip()]
        self.on_setting_changed("dns_servers", dns_list) 