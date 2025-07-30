"""
Cloud AppStore Dialogs
Uygulama detay dialog'u ve diğer popup'lar
"""

import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .appstore import AppInfo, AppStatus
from .widgets import StarRatingWidget

class AppDetailDialog(QDialog):
    """Uygulama detay dialog'u"""
    
    # Sinyaller
    install_requested = pyqtSignal(str)  # app_id
    remove_requested = pyqtSignal(str)   # app_id
    update_requested = pyqtSignal(str)   # app_id
    rating_submitted = pyqtSignal(str, int, str)  # app_id, rating, review
    
    def __init__(self, app_info: AppInfo, dark_mode: bool = False, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.dark_mode = dark_mode
        self.user_rating = 0
        self.user_review = ""
        
        self.setup_ui()
        self.apply_theme()
        self.load_app_data()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle(f"{self.app_info.name} - Uygulama Detayları")
        self.setFixedSize(600, 700)
        self.setModal(True)
        
        # Ana layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # İçerik widget'ı
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        # Başlık bölümü
        self.setup_header_section(content_layout)
        
        # Bilgi bölümü
        self.setup_info_section(content_layout)
        
        # Ekran görüntüleri
        self.setup_screenshots_section(content_layout)
        
        # Yorumlar ve puanlama
        self.setup_reviews_section(content_layout)
        
        # Kullanıcı puanlama
        self.setup_user_rating_section(content_layout)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, 1)
        
        # Alt butonlar
        self.setup_bottom_buttons(layout)
    
    def setup_header_section(self, layout: QVBoxLayout):
        """Başlık bölümü"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        
        # İkon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(80, 80)
        self.load_app_icon()
        header_layout.addWidget(self.icon_label)
        
        # Bilgiler
        info_layout = QVBoxLayout()
        
        # Uygulama adı
        self.name_label = QLabel(self.app_info.name)
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 4px;")
        info_layout.addWidget(self.name_label)
        
        # Geliştirici
        self.developer_label = QLabel(f"Geliştirici: {self.app_info.developer}")
        self.developer_label.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 4px;")
        info_layout.addWidget(self.developer_label)
        
        # Sürüm ve kategori
        meta_layout = QHBoxLayout()
        
        self.version_label = QLabel(f"Sürüm: {self.app_info.version}")
        self.version_label.setStyleSheet("font-size: 12px; color: #888;")
        meta_layout.addWidget(self.version_label)
        
        self.category_badge = QLabel(self.app_info.category)
        self.category_badge.setStyleSheet("""
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        meta_layout.addWidget(self.category_badge)
        meta_layout.addStretch()
        
        info_layout.addLayout(meta_layout)
        
        # Rating ve indirme sayısı
        stats_layout = QHBoxLayout()
        
        self.rating_widget = StarRatingWidget(self.app_info.rating, read_only=True, size=20)
        stats_layout.addWidget(self.rating_widget)
        
        self.rating_text = QLabel(f"{self.app_info.rating:.1f}")
        self.rating_text.setStyleSheet("font-size: 14px; font-weight: bold; margin-left: 8px;")
        stats_layout.addWidget(self.rating_text)
        
        self.downloads_label = QLabel(f"• {self.app_info.downloads:,} indirme")
        self.downloads_label.setStyleSheet("font-size: 12px; color: #666; margin-left: 12px;")
        stats_layout.addWidget(self.downloads_label)
        
        stats_layout.addStretch()
        info_layout.addLayout(stats_layout)
        
        # Durum badge'i
        if self.app_info.is_installed:
            if self.app_info.has_update():
                status_text = "🔄 Güncelleme Mevcut"
                status_color = "#ff9800"
            else:
                status_text = "✅ Yüklü"
                status_color = "#4caf50"
        else:
            status_text = "📦 Mevcut"
            status_color = "#2196f3"
        
        self.status_badge = QLabel(status_text)
        self.status_badge.setStyleSheet(f"""
            background-color: {status_color};
            color: white;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 8px;
        """)
        info_layout.addWidget(self.status_badge)
        
        header_layout.addLayout(info_layout, 1)
        layout.addWidget(header_widget)
    
    def setup_info_section(self, layout: QVBoxLayout):
        """Bilgi bölümü"""
        # Açıklama
        desc_label = QLabel("Açıklama")
        desc_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 8px; margin-bottom: 8px;")
        layout.addWidget(desc_label)
        
        self.description_text = QTextEdit()
        self.description_text.setPlainText(self.app_info.description)
        self.description_text.setReadOnly(True)
        self.description_text.setFixedHeight(100)
        layout.addWidget(self.description_text)
        
        # Detaylı bilgiler
        details_widget = QWidget()
        details_layout = QGridLayout(details_widget)
        details_layout.setContentsMargins(0, 8, 0, 8)
        
        row = 0
        
        # Lisans
        if self.app_info.license:
            details_layout.addWidget(QLabel("Lisans:"), row, 0)
            license_label = QLabel(self.app_info.license)
            license_label.setStyleSheet("color: #666;")
            details_layout.addWidget(license_label, row, 1)
            row += 1
        
        # Son güncelleme
        if self.app_info.last_updated:
            details_layout.addWidget(QLabel("Son Güncelleme:"), row, 0)
            update_label = QLabel(self.app_info.last_updated)
            update_label.setStyleSheet("color: #666;")
            details_layout.addWidget(update_label, row, 1)
            row += 1
        
        # Boyut (simülasyon)
        if self.app_info.size > 0:
            details_layout.addWidget(QLabel("Boyut:"), row, 0)
            size_mb = self.app_info.size / (1024 * 1024)
            size_label = QLabel(f"{size_mb:.1f} MB")
            size_label.setStyleSheet("color: #666;")
            details_layout.addWidget(size_label, row, 1)
            row += 1
        
        # Gereksinimler
        if self.app_info.requires:
            details_layout.addWidget(QLabel("Gereksinimler:"), row, 0)
            req_label = QLabel(", ".join(self.app_info.requires))
            req_label.setStyleSheet("color: #666;")
            req_label.setWordWrap(True)
            details_layout.addWidget(req_label, row, 1)
            row += 1
        
        # İzinler
        if self.app_info.permissions:
            details_layout.addWidget(QLabel("İzinler:"), row, 0)
            perm_label = QLabel(", ".join(self.app_info.permissions))
            perm_label.setStyleSheet("color: #666;")
            perm_label.setWordWrap(True)
            details_layout.addWidget(perm_label, row, 1)
            row += 1
        
        # Ana sayfa
        if self.app_info.homepage:
            details_layout.addWidget(QLabel("Ana Sayfa:"), row, 0)
            homepage_label = QLabel(f'<a href="{self.app_info.homepage}">{self.app_info.homepage}</a>')
            homepage_label.setOpenExternalLinks(True)
            homepage_label.setStyleSheet("color: #2196f3;")
            details_layout.addWidget(homepage_label, row, 1)
            row += 1
        
        layout.addWidget(details_widget)
        
        # Etiketler
        if self.app_info.tags:
            tags_label = QLabel("Etiketler")
            tags_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 8px; margin-bottom: 8px;")
            layout.addWidget(tags_label)
            
            tags_widget = QWidget()
            tags_layout = QHBoxLayout(tags_widget)
            tags_layout.setContentsMargins(0, 0, 0, 0)
            
            for tag in self.app_info.tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet("""
                    background-color: #f0f0f0;
                    color: #666;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    margin-right: 4px;
                """)
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            layout.addWidget(tags_widget)
    
    def setup_screenshots_section(self, layout: QVBoxLayout):
        """Ekran görüntüleri bölümü"""
        if not self.app_info.screenshots:
            return
        
        screenshots_label = QLabel("Ekran Görüntüleri")
        screenshots_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 16px; margin-bottom: 8px;")
        layout.addWidget(screenshots_label)
        
        # Scroll area for screenshots
        screenshots_scroll = QScrollArea()
        screenshots_scroll.setFixedHeight(200)
        screenshots_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        screenshots_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        screenshots_widget = QWidget()
        screenshots_layout = QHBoxLayout(screenshots_widget)
        screenshots_layout.setContentsMargins(8, 8, 8, 8)
        
        for screenshot_path in self.app_info.screenshots[:5]:  # Maksimum 5 ekran görüntüsü
            screenshot_label = QLabel()
            screenshot_label.setFixedSize(150, 100)
            screenshot_label.setStyleSheet("""
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f5f5f5;
            """)
            screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            screenshot_label.setText("📷\nÖnizleme")
            screenshots_layout.addWidget(screenshot_label)
        
        screenshots_layout.addStretch()
        screenshots_scroll.setWidget(screenshots_widget)
        layout.addWidget(screenshots_scroll)
    
    def setup_reviews_section(self, layout: QVBoxLayout):
        """Yorumlar bölümü"""
        reviews_label = QLabel("Kullanıcı Yorumları")
        reviews_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 16px; margin-bottom: 8px;")
        layout.addWidget(reviews_label)
        
        # Mock yorumlar
        mock_reviews = [
            {"user": "Ahmet K.", "rating": 5, "comment": "Harika bir uygulama! Çok kullanışlı ve hızlı.", "date": "2024-01-20"},
            {"user": "Zeynep M.", "rating": 4, "comment": "Güzel tasarım, birkaç küçük hata var ama genel olarak memnunum.", "date": "2024-01-18"},
            {"user": "Mehmet S.", "rating": 5, "comment": "Tam aradığım şey. Kesinlikle tavsiye ederim!", "date": "2024-01-15"}
        ]
        
        for review in mock_reviews:
            review_widget = self.create_review_widget(review)
            layout.addWidget(review_widget)
    
    def create_review_widget(self, review: dict) -> QWidget:
        """Yorum widget'ı oluştur"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                margin: 4px 0;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Üst satır: Kullanıcı ve rating
        top_layout = QHBoxLayout()
        
        user_label = QLabel(review["user"])
        user_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        top_layout.addWidget(user_label)
        
        rating_widget = StarRatingWidget(review["rating"], read_only=True, size=14)
        top_layout.addWidget(rating_widget)
        
        date_label = QLabel(review["date"])
        date_label.setStyleSheet("color: #666; font-size: 11px;")
        top_layout.addStretch()
        top_layout.addWidget(date_label)
        
        layout.addLayout(top_layout)
        
        # Yorum metni
        comment_label = QLabel(review["comment"])
        comment_label.setWordWrap(True)
        comment_label.setStyleSheet("color: #333; font-size: 12px; line-height: 1.4;")
        layout.addWidget(comment_label)
        
        return widget
    
    def setup_user_rating_section(self, layout: QVBoxLayout):
        """Kullanıcı puanlama bölümü"""
        if not self.app_info.is_installed:
            return  # Sadece yüklü uygulamalar için
        
        rating_label = QLabel("Bu Uygulamayı Puanla")
        rating_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 16px; margin-bottom: 8px;")
        layout.addWidget(rating_label)
        
        rating_widget = QWidget()
        rating_layout = QVBoxLayout(rating_widget)
        rating_layout.setContentsMargins(12, 12, 12, 12)
        rating_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        
        # Yıldız puanlama
        stars_layout = QHBoxLayout()
        stars_layout.addWidget(QLabel("Puanınız:"))
        
        self.user_rating_widget = StarRatingWidget(0, read_only=False, size=24)
        self.user_rating_widget.rating_changed.connect(self.on_user_rating_changed)
        stars_layout.addWidget(self.user_rating_widget)
        stars_layout.addStretch()
        
        rating_layout.addLayout(stars_layout)
        
        # Yorum kutusu
        comment_layout = QVBoxLayout()
        comment_layout.addWidget(QLabel("Yorumunuz (isteğe bağlı):"))
        
        self.user_comment_edit = QTextEdit()
        self.user_comment_edit.setFixedHeight(80)
        self.user_comment_edit.setPlaceholderText("Bu uygulama hakkındaki düşüncelerinizi paylaşın...")
        comment_layout.addWidget(self.user_comment_edit)
        
        rating_layout.addLayout(comment_layout)
        
        # Gönder butonu
        submit_layout = QHBoxLayout()
        submit_layout.addStretch()
        
        self.submit_rating_btn = QPushButton("Puanı Gönder")
        self.submit_rating_btn.setEnabled(False)
        self.submit_rating_btn.clicked.connect(self.submit_rating)
        submit_layout.addWidget(self.submit_rating_btn)
        
        rating_layout.addLayout(submit_layout)
        layout.addWidget(rating_widget)
    
    def setup_bottom_buttons(self, layout: QVBoxLayout):
        """Alt butonlar"""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(20, 12, 20, 20)
        button_layout.setSpacing(12)
        
        # Kapat butonu
        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)
        
        button_layout.addStretch()
        
        # Ana aksiyon butonu
        if self.app_info.is_installed:
            if self.app_info.has_update():
                self.action_btn = QPushButton("🔄 Güncelle")
                self.action_btn.setStyleSheet(self.get_button_style("#ff9800"))
                self.action_btn.clicked.connect(lambda: self.update_requested.emit(self.app_info.app_id))
            else:
                self.action_btn = QPushButton("🗑️ Kaldır")
                self.action_btn.setStyleSheet(self.get_button_style("#f44336"))
                self.action_btn.clicked.connect(lambda: self.remove_requested.emit(self.app_info.app_id))
        else:
            self.action_btn = QPushButton("⬇️ Kur")
            self.action_btn.setStyleSheet(self.get_button_style("#4caf50"))
            self.action_btn.clicked.connect(lambda: self.install_requested.emit(self.app_info.app_id))
        
        button_layout.addWidget(self.action_btn)
        
        layout.addWidget(button_widget)
    
    def get_button_style(self, color: str) -> str:
        """Buton stili"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """
    
    def darken_color(self, color: str, factor: float = 0.9) -> str:
        """Rengi koyulaştır"""
        color_map = {
            "#4caf50": "#45a049",
            "#f44336": "#d32f2f", 
            "#2196f3": "#1976d2",
            "#ff9800": "#f57c00"
        }
        return color_map.get(color, color)
    
    def load_app_icon(self):
        """Uygulama ikonunu yükle"""
        try:
            icon_path = Path(self.app_info.icon_path)
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.icon_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.icon_label.setPixmap(scaled_pixmap)
                    return
        except Exception:
            pass
        
        # Varsayılan ikon
        self.set_default_icon()
    
    def set_default_icon(self):
        """Varsayılan ikon ayarla"""
        # Kategori bazlı emoji ikonlar
        category_icons = {
            "Sistem": "⚙️",
            "Geliştirme": "💻",
            "İnternet": "🌐",
            "Multimedya": "🎵",
            "Grafik": "🎨",
            "Oyunlar": "🎮",
            "Ofis": "📄",
            "Eğitim": "📚",
            "Araçlar": "🔧"
        }
        
        emoji = category_icons.get(self.app_info.category, "📱")
        
        # Emoji'yi QPixmap'e çevir
        pixmap = QPixmap(self.icon_label.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont("Apple Color Emoji", 48)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        
        self.icon_label.setPixmap(pixmap)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QScrollArea {
                    border: none;
                    background-color: #2d2d2d;
                }
                QTextEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #555;
                    border-radius: 6px;
                    color: #ffffff;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #404040;
                    border: 1px solid #555;
                    border-radius: 6px;
                    padding: 8px 16px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    color: #333;
                }
                QWidget {
                    background-color: #ffffff;
                    color: #333;
                }
                QScrollArea {
                    border: none;
                    background-color: #ffffff;
                }
                QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    color: #333;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px 16px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QLabel {
                    color: #333;
                }
            """)
    
    def load_app_data(self):
        """Uygulama verilerini yükle"""
        # Simülasyon - gerçek uygulamada API'den gelecek
        pass
    
    def on_user_rating_changed(self, rating: int):
        """Kullanıcı puanı değişti"""
        self.user_rating = rating
        self.submit_rating_btn.setEnabled(rating > 0)
    
    def submit_rating(self):
        """Puanı gönder"""
        if self.user_rating == 0:
            return
        
        self.user_review = self.user_comment_edit.toPlainText().strip()
        
        # Sinyal gönder
        self.rating_submitted.emit(self.app_info.app_id, self.user_rating, self.user_review)
        
        # Başarı mesajı
        QMessageBox.information(
            self, "Puan Gönderildi",
            "Puanınız başarıyla gönderildi. Teşekkür ederiz!"
        )
        
        # Puanlama bölümünü devre dışı bırak
        self.user_rating_widget.setEnabled(False)
        self.user_comment_edit.setEnabled(False)
        self.submit_rating_btn.setEnabled(False)
        self.submit_rating_btn.setText("Gönderildi ✓") 