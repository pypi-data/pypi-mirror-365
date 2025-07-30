"""
Cloud Settings - Widget'lar Sayfası
Masaüstü widget'larının görünürlüğü ve sırası yönetimi
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from .base_page import BasePage

class WidgetListItem(QWidget):
    """Widget listesi öğesi"""
    
    visibility_changed = pyqtSignal(str, bool)  # widget_id, visible
    position_changed = pyqtSignal(str, int)     # widget_id, new_position
    
    def __init__(self, widget_id: str, widget_name: str, widget_icon: str, enabled: bool = True):
        super().__init__()
        self.widget_id = widget_id
        self.widget_name = widget_name
        self.widget_icon = widget_icon
        self.enabled = enabled
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Sürükleme tutamacı
        self.drag_handle = QLabel("⋮⋮")
        self.drag_handle.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.drag_handle.setFixedWidth(20)
        layout.addWidget(self.drag_handle)
        
        # Widget ikonu
        icon_label = QLabel(self.widget_icon)
        icon_label.setStyleSheet("font-size: 20px;")
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Widget adı ve açıklaması
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        name_label = QLabel(self.widget_name)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #212529;
            }
        """)
        text_layout.addWidget(name_label)
        
        # Widget açıklaması
        descriptions = {
            "clock": "Saat ve tarih gösterimi",
            "calendar": "Takvim widget'ı",
            "weather": "Hava durumu bilgisi",
            "system_monitor": "Sistem performans izleyici",
            "notes": "Hızlı notlar",
            "calculator": "Hesap makinesi",
            "music_player": "Müzik çalar kontrolü",
            "network_monitor": "Ağ trafiği izleyici"
        }
        
        desc_label = QLabel(descriptions.get(self.widget_id, "Widget açıklaması"))
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #6c757d;
            }
        """)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout, 1)
        
        # Görünürlük toggle
        self.visibility_toggle = QCheckBox()
        self.visibility_toggle.setChecked(self.enabled)
        self.visibility_toggle.toggled.connect(self.on_visibility_changed)
        self.visibility_toggle.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        layout.addWidget(self.visibility_toggle)
        
        # Ayarlar butonu
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        settings_btn.clicked.connect(self.show_widget_settings)
        layout.addWidget(settings_btn)
        
        # Genel stil
        self.setStyleSheet("""
            WidgetListItem {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin: 2px 0;
            }
            
            WidgetListItem:hover {
                background-color: #f8f9fa;
                border-color: #007bff;
            }
        """)
    
    def on_visibility_changed(self, checked: bool):
        """Görünürlük değişti"""
        self.enabled = checked
        self.visibility_changed.emit(self.widget_id, checked)
    
    def show_widget_settings(self):
        """Widget ayarlarını göster"""
        # Widget'a özel ayarlar dialog'u
        dialog = WidgetSettingsDialog(self.widget_id, self.widget_name, self)
        dialog.exec()
    
    def set_enabled(self, enabled: bool):
        """Etkinlik durumunu ayarla"""
        self.enabled = enabled
        self.visibility_toggle.setChecked(enabled)

class WidgetSettingsDialog(QDialog):
    """Widget ayarları dialog'u"""
    
    def __init__(self, widget_id: str, widget_name: str, parent=None):
        super().__init__(parent)
        self.widget_id = widget_id
        self.widget_name = widget_name
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle(f"{self.widget_name} Ayarları")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel(f"{self.widget_name} Widget Ayarları")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #212529;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # Widget'a özel ayarlar
        self.setup_widget_specific_settings(layout)
        
        layout.addStretch()
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def setup_widget_specific_settings(self, layout):
        """Widget'a özel ayarlar"""
        if self.widget_id == "clock":
            self.setup_clock_settings(layout)
        elif self.widget_id == "weather":
            self.setup_weather_settings(layout)
        elif self.widget_id == "calendar":
            self.setup_calendar_settings(layout)
        else:
            # Genel ayarlar
            self.setup_general_settings(layout)
    
    def setup_clock_settings(self, layout):
        """Saat widget ayarları"""
        group = QGroupBox("Saat Ayarları")
        group_layout = QVBoxLayout(group)
        
        # 24 saat formatı
        format_24h = QCheckBox("24 saat formatı kullan")
        format_24h.setChecked(True)
        group_layout.addWidget(format_24h)
        
        # Saniye göster
        show_seconds = QCheckBox("Saniyeyi göster")
        group_layout.addWidget(show_seconds)
        
        # Tarih göster
        show_date = QCheckBox("Tarihi göster")
        show_date.setChecked(True)
        group_layout.addWidget(show_date)
        
        layout.addWidget(group)
    
    def setup_weather_settings(self, layout):
        """Hava durumu widget ayarları"""
        group = QGroupBox("Hava Durumu Ayarları")
        group_layout = QFormLayout(group)
        
        # Şehir
        city_edit = QLineEdit("İstanbul")
        group_layout.addRow("Şehir:", city_edit)
        
        # Sıcaklık birimi
        temp_unit = QComboBox()
        temp_unit.addItems(["Celsius", "Fahrenheit"])
        group_layout.addRow("Sıcaklık Birimi:", temp_unit)
        
        # Güncelleme sıklığı
        update_interval = QSpinBox()
        update_interval.setRange(5, 120)
        update_interval.setValue(30)
        update_interval.setSuffix(" dakika")
        group_layout.addRow("Güncelleme Sıklığı:", update_interval)
        
        layout.addWidget(group)
    
    def setup_calendar_settings(self, layout):
        """Takvim widget ayarları"""
        group = QGroupBox("Takvim Ayarları")
        group_layout = QVBoxLayout(group)
        
        # Hafta başlangıcı
        week_start_layout = QHBoxLayout()
        week_start_layout.addWidget(QLabel("Hafta Başlangıcı:"))
        
        week_start = QComboBox()
        week_start.addItems(["Pazartesi", "Pazar"])
        week_start_layout.addWidget(week_start)
        week_start_layout.addStretch()
        
        group_layout.addLayout(week_start_layout)
        
        # Tatil günlerini vurgula
        highlight_holidays = QCheckBox("Tatil günlerini vurgula")
        highlight_holidays.setChecked(True)
        group_layout.addWidget(highlight_holidays)
        
        layout.addWidget(group)
    
    def setup_general_settings(self, layout):
        """Genel widget ayarları"""
        group = QGroupBox("Genel Ayarlar")
        group_layout = QFormLayout(group)
        
        # Şeffaflık
        transparency = QSlider(Qt.Orientation.Horizontal)
        transparency.setRange(10, 100)
        transparency.setValue(90)
        group_layout.addRow("Şeffaflık:", transparency)
        
        # Boyut
        size_combo = QComboBox()
        size_combo.addItems(["Küçük", "Orta", "Büyük"])
        size_combo.setCurrentText("Orta")
        group_layout.addRow("Boyut:", size_combo)
        
        layout.addWidget(group)

class WidgetsPage(BasePage):
    """Widget'lar ayarları sayfası"""
    
    def __init__(self, kernel=None, preview_manager=None):
        # Mevcut widget'lar - önce tanımla
        self.available_widgets = [
            ("clock", "🕐 Saat", "clock"),
            ("calendar", "📅 Takvim", "calendar"),
            ("weather", "🌤️ Hava Durumu", "weather"),
            ("system_monitor", "📊 Sistem İzleyici", "system_monitor"),
            ("notes", "📝 Notlar", "notes"),
            ("calculator", "🧮 Hesap Makinesi", "calculator"),
            ("music_player", "🎵 Müzik Çalar", "music_player"),
            ("network_monitor", "🌐 Ağ İzleyici", "network_monitor")
        ]
        
        self.widget_items = {}
        
        super().__init__("widgets", "Widget'lar", "🧩", kernel, preview_manager)
        
    def setup_ui(self):
        """UI kurulumu"""
        super().setup_ui()
        
        # Widget yönetimi bölümü
        self.setup_widget_management()
        
        # Widget düzenleme bölümü
        self.setup_widget_arrangement()
        
        # Genel widget ayarları
        self.setup_general_widget_settings()
        
        self.add_spacer()
    
    def setup_widget_management(self):
        """Widget yönetimi bölümü"""
        group = self.add_group("Widget Yönetimi")
        layout = QVBoxLayout(group)
        
        # Açıklama
        desc_label = QLabel("Masaüstünde görüntülenecek widget'ları seçin ve sıralarını düzenleyin.")
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                margin-bottom: 15px;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Widget listesi
        self.widget_list = QListWidget()
        self.widget_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.widget_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.widget_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 8px;
            }
            
            QListWidget::item {
                border: none;
                margin: 2px 0;
                border-radius: 6px;
            }
        """)
        
        # Widget'ları listeye ekle
        self.populate_widget_list()
        
        layout.addWidget(self.widget_list)
        
        # Widget ekleme butonları
        button_layout = QHBoxLayout()
        
        add_all_btn = QPushButton("Tümünü Etkinleştir")
        add_all_btn.clicked.connect(self.enable_all_widgets)
        button_layout.addWidget(add_all_btn)
        
        remove_all_btn = QPushButton("Tümünü Devre Dışı Bırak")
        remove_all_btn.clicked.connect(self.disable_all_widgets)
        button_layout.addWidget(remove_all_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def setup_widget_arrangement(self):
        """Widget düzenleme bölümü"""
        group = self.add_group("Widget Düzenleme")
        layout = QVBoxLayout(group)
        
        # Otomatik düzenleme
        self.add_checkbox(
            layout,
            "Otomatik düzenleme",
            "auto_arrange",
            "Widget'ları otomatik olarak düzenle"
        )
        
        # Grid boyutu
        self.add_slider(
            layout,
            "Grid Boyutu",
            "grid_size",
            8, 32, 16,
            "Widget yerleştirme grid'inin boyutu"
        )
        
        # Widget aralığı
        self.add_slider(
            layout,
            "Widget Aralığı",
            "widget_spacing",
            0, 50, 10,
            "Widget'lar arasındaki boşluk (piksel)"
        )
    
    def setup_general_widget_settings(self):
        """Genel widget ayarları bölümü"""
        group = self.add_group("Genel Ayarlar")
        layout = QVBoxLayout(group)
        
        # Widget şeffaflığı
        self.add_slider(
            layout,
            "Widget Şeffaflığı",
            "widget_transparency",
            10, 100, 90,
            "Tüm widget'ların şeffaflık seviyesi (%)"
        )
        
        # Widget gölgeleri
        self.add_checkbox(
            layout,
            "Widget gölgeleri",
            "widget_shadows",
            "Widget'ların altında gölge efekti göster"
        )
        
        # Widget animasyonları
        self.add_checkbox(
            layout,
            "Widget animasyonları",
            "widget_animations",
            "Widget açılma/kapanma animasyonları"
        )
        
        # Widget kilitleme
        self.add_checkbox(
            layout,
            "Widget konumlarını kilitle",
            "lock_widget_positions",
            "Widget'ların yanlışlıkla taşınmasını önle"
        )
    
    def populate_widget_list(self):
        """Widget listesini doldur"""
        for widget_id, widget_name, widget_icon in self.available_widgets:
            # Widget öğesi oluştur
            widget_item = WidgetListItem(widget_id, widget_name, widget_icon)
            widget_item.visibility_changed.connect(self.on_widget_visibility_changed)
            
            # Liste öğesi oluştur
            list_item = QListWidgetItem()
            list_item.setSizeHint(widget_item.sizeHint())
            
            # Widget'ı listeye ekle
            self.widget_list.addItem(list_item)
            self.widget_list.setItemWidget(list_item, widget_item)
            
            # Referansı sakla
            self.widget_items[widget_id] = widget_item
    
    def on_widget_visibility_changed(self, widget_id: str, visible: bool):
        """Widget görünürlüğü değişti"""
        # Etkin widget'lar listesini güncelle
        enabled_widgets = self.settings.get("enabled_widgets", [])
        
        if visible and widget_id not in enabled_widgets:
            enabled_widgets.append(widget_id)
        elif not visible and widget_id in enabled_widgets:
            enabled_widgets.remove(widget_id)
        
        self.on_setting_changed("enabled_widgets", enabled_widgets)
    
    def enable_all_widgets(self):
        """Tüm widget'ları etkinleştir"""
        enabled_widgets = [widget_id for widget_id, _, _ in self.available_widgets]
        
        for widget_id, widget_item in self.widget_items.items():
            widget_item.set_enabled(True)
        
        self.on_setting_changed("enabled_widgets", enabled_widgets)
    
    def disable_all_widgets(self):
        """Tüm widget'ları devre dışı bırak"""
        for widget_id, widget_item in self.widget_items.items():
            widget_item.set_enabled(False)
        
        self.on_setting_changed("enabled_widgets", [])
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle"""
        super().update_ui()
        
        # Widget görünürlüklerini güncelle
        enabled_widgets = self.settings.get("enabled_widgets", ["clock", "calendar", "weather"])
        
        for widget_id, widget_item in self.widget_items.items():
            widget_item.set_enabled(widget_id in enabled_widgets) 