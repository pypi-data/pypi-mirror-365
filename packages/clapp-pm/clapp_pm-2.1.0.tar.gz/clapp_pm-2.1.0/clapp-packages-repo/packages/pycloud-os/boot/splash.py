"""
PyCloud OS Boot Splash Screen
macOS tarzı açılış ekranı - sistem yüklenene kadar profesyonel deneyim
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class SplashConfig:
    """Splash screen yapılandırması"""
    
    def __init__(self):
        self.config_file = Path("system/config/splash.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Varsayılan ayarlar
        self.default_config = {
            "logo_path": "system/logo/cloud.svg",
            "text": "PyCloud OS",
            "font_family": "Product Sans",
            "fallback_font": "JetBrains Mono",
            "min_display_duration": 15000,  # 15 saniye (10 saniyeden artırdık)
            "logo_animation_loop": True,
            "blur_wallpaper": True,
            "color_theme": "dark",
            "show_version": True,
            "show_loading_text": True,
            "debug_mode": True,  # Debug modunu açtık
            "custom_splash_enabled": False,
            "animation": {
                "cloud_breathing": True,
                "text_fade_duration": 500,
                "fade_out_duration": 2000  # Fade out süresini de artırdık
            }
        }
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Yapılandırmayı yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Varsayılan config ile birleştir
                config = self.default_config.copy()
                config.update(user_config)
                return config
            else:
                # Varsayılan config'i kaydet
                self._save_config(self.default_config)
                return self.default_config.copy()
                
        except Exception as e:
            logging.error(f"Failed to load splash config: {e}")
            return self.default_config.copy()
    
    def _save_config(self, config: Dict):
        """Yapılandırmayı kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save splash config: {e}")
    
    def get(self, key: str, default=None):
        """Yapılandırma değeri al"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Yapılandırma değeri ayarla"""
        self.config[key] = value
        self._save_config(self.config)

class VersionManager:
    """Sistem versiyon yöneticisi"""
    
    def __init__(self):
        self.version_file = Path("system/version.json")
        self.version_info = self._load_version()
    
    def _load_version(self) -> Dict:
        """Versiyon bilgisini yükle"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Varsayılan versiyon bilgisi
                default_version = {
                    "version": "0.9.0-dev",
                    "build": "20241201",
                    "codename": "Nimbus",
                    "release_date": "2024-12-01",
                    "build_type": "development"
                }
                
                # Varsayılan versiyon dosyasını oluştur
                self.version_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.version_file, 'w', encoding='utf-8') as f:
                    json.dump(default_version, f, indent=2, ensure_ascii=False)
                
                return default_version
                
        except Exception as e:
            logging.error(f"Failed to load version info: {e}")
            return {"version": "Unknown", "build": "Unknown"}
    
    def get_version_string(self) -> str:
        """Versiyon string'ini al"""
        version = self.version_info.get("version", "Unknown")
        build = self.version_info.get("build", "")
        
        if build:
            return f"v{version} (Build {build})"
        else:
            return f"v{version}"
    
    def get_full_info(self) -> Dict:
        """Tam versiyon bilgisini al"""
        return self.version_info.copy()

class LoadingSteps:
    """Yükleme adımları yöneticisi"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.steps = [
            "Sistem başlatılıyor...",
            "Çekirdek modülleri yükleniyor...",
            "Güvenlik sistemi kontrol ediliyor...",
            "Dosya sistemi hazırlanıyor...",
            "Kullanıcı oturumu başlatılıyor...",
            "Tema ve görsel ayarlar yükleniyor...",
            "Arayüz bileşenleri yükleniyor...",
            "Uygulamalar keşfediliyor...",
            "Son kontroller yapılıyor...",
            "Sistem hazır!"
        ]
        
        self.current_step = 0
        self.step_logs = []
    
    def get_current_step(self) -> str:
        """Mevcut adımı al"""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return "Sistem hazır!"
    
    def next_step(self) -> str:
        """Sonraki adıma geç"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
        
        step_text = self.get_current_step()
        
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_entry = f"[{timestamp}] {step_text}"
            self.step_logs.append(log_entry)
            logging.info(f"Splash: {step_text}")
        
        return step_text
    
    def get_progress(self) -> float:
        """İlerleme yüzdesini al (0.0 - 1.0)"""
        if len(self.steps) == 0:
            return 1.0
        return min(self.current_step / (len(self.steps) - 1), 1.0)
    
    def get_logs(self) -> list:
        """Debug loglarını al"""
        return self.step_logs.copy()

class CloudLogoWidget(QWidget):
    """Animasyonlu bulut logosu widget'ı"""
    
    def __init__(self, logo_path: str, animation_enabled: bool = True):
        super().__init__()
        self.logo_path = Path(logo_path)
        self.animation_enabled = animation_enabled
        
        # Animasyon ayarları
        self.scale_factor = 1.0
        self.breathing_direction = 1  # 1: büyüyor, -1: küçülüyor
        self.breathing_speed = 0.02
        self.min_scale = 0.95
        self.max_scale = 1.05
        
        # Timer
        if self.animation_enabled:
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._update_animation)
            self.animation_timer.start(50)  # 50ms = 20 FPS
        
        # Logo yükle
        self.logo_pixmap = self._load_logo()
        
        self.setFixedSize(120, 120)
    
    def _load_logo(self) -> QPixmap:
        """Logo dosyasını yükle"""
        try:
            if self.logo_path.exists():
                if self.logo_path.suffix.lower() == '.svg':
                    # SVG desteği
                    from PyQt6.QtSvg import QSvgRenderer
                    renderer = QSvgRenderer(str(self.logo_path))
                    pixmap = QPixmap(100, 100)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    return pixmap
                else:
                    # PNG/JPG desteği
                    return QPixmap(str(self.logo_path)).scaled(
                        100, 100, Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
            else:
                # Fallback: Basit bulut çizimi
                return self._create_fallback_logo()
                
        except Exception as e:
            logging.warning(f"Failed to load logo: {e}")
            return self._create_fallback_logo()
    
    def _create_fallback_logo(self) -> QPixmap:
        """Fallback bulut logosu oluştur"""
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Bulut rengi
        painter.setBrush(QBrush(QColor(100, 150, 255, 200)))
        painter.setPen(QPen(QColor(80, 120, 200), 2))
        
        # Basit bulut şekli çiz
        painter.drawEllipse(20, 40, 30, 20)  # Sol bulut
        painter.drawEllipse(35, 30, 40, 30)  # Orta bulut
        painter.drawEllipse(55, 40, 25, 20)  # Sağ bulut
        
        painter.end()
        return pixmap
    
    def _update_animation(self):
        """Animasyonu güncelle"""
        if not self.animation_enabled:
            return
        
        # Nefes alma animasyonu
        self.scale_factor += self.breathing_direction * self.breathing_speed
        
        if self.scale_factor >= self.max_scale:
            self.breathing_direction = -1
        elif self.scale_factor <= self.min_scale:
            self.breathing_direction = 1
        
        self.update()
    
    def paintEvent(self, event):
        """Widget çizimi"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Merkeze hizala ve ölçekle
        rect = self.rect()
        center = rect.center()
        
        scaled_size = int(100 * self.scale_factor)
        scaled_rect = QRect(
            center.x() - scaled_size // 2,
            center.y() - scaled_size // 2,
            scaled_size,
            scaled_size
        )
        
        painter.drawPixmap(scaled_rect, self.logo_pixmap)

class ProgressBarWidget(QWidget):
    """Minimal progress bar widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.progress = 0.0
        self.setFixedHeight(4)
        self.setMinimumWidth(300)
    
    def set_progress(self, progress: float):
        """İlerlemeyi ayarla (0.0 - 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        self.update()
    
    def paintEvent(self, event):
        """Progress bar çizimi"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Arka plan
        painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 2, 2)
        
        # İlerleme
        if self.progress > 0:
            progress_width = int(rect.width() * self.progress)
            progress_rect = QRect(0, 0, progress_width, rect.height())
            
            painter.setBrush(QBrush(QColor(100, 150, 255, 180)))
            painter.drawRoundedRect(progress_rect, 2, 2)

class SplashScreen(QWidget):
    """Ana splash screen sınıfı"""
    
    step_changed = pyqtSignal(str)
    splash_finished = pyqtSignal()
    
    def __init__(self, kernel=None):
        super().__init__()
        
        self.kernel = kernel
        self.logger = logging.getLogger("SplashScreen")
        
        # Yapılandırma
        self.config = SplashConfig()
        self.version_manager = VersionManager()
        self.loading_steps = LoadingSteps(self.config.get("debug_mode", False))
        
        # Zamanlama
        self.start_time = time.time()
        self.min_duration = self.config.get("min_display_duration", 3000) / 1000.0  # saniyeye çevir
        
        # UI kurulumu
        self._setup_ui()
        self._setup_timers()
        
        # İlk adımı başlat
        QTimer.singleShot(2000, self.next_step)  # İlk adım için 2 saniye bekle (1 saniyeden artırdık)
    
    def _setup_ui(self):
        """UI kurulumu"""
        # Ekran boyutunu al
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # Splash boyutu
        splash_width = 600
        splash_height = 400
        
        # Merkeze konumlandır
        x = (screen_geometry.width() - splash_width) // 2
        y = (screen_geometry.height() - splash_height) // 2
        
        self.setGeometry(x, y, splash_width, splash_height)
        
        # Ana layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Logo
        self.logo_widget = CloudLogoWidget(
            self.config.get("logo_path", "system/logo/cloud.svg"),
            self.config.get("logo_animation_loop", True)
        )
        layout.addWidget(self.logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Başlık
        title_label = QLabel(self.config.get("text", "PyCloud OS"))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            font-family: 'Product Sans', 'JetBrains Mono', sans-serif;
        """)
        layout.addWidget(title_label)
        
        # Progress bar
        self.progress_bar = ProgressBarWidget()
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Yükleme metni
        self.loading_label = QLabel("Sistem başlatılıyor...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 180);
            font-family: 'JetBrains Mono', monospace;
        """)
        
        if self.config.get("show_loading_text", True):
            layout.addWidget(self.loading_label)
        
        # Versiyon bilgisi
        if self.config.get("show_version", True):
            version_label = QLabel(self.version_manager.get_version_string())
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            version_label.setStyleSheet("""
                font-size: 11px;
                color: rgba(255, 255, 255, 120);
                font-family: 'JetBrains Mono', monospace;
            """)
            layout.addWidget(version_label)
        
        # Debug log alanı
        if self.config.get("debug_mode", False):
            self.debug_text = QTextEdit()
            self.debug_text.setMaximumHeight(100)
            self.debug_text.setStyleSheet("""
                background-color: rgba(0, 0, 0, 100);
                color: #00ff00;
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 4px;
            """)
            layout.addWidget(self.debug_text)
        
        # Pencere ayarları
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Arka plan stili
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 50, 240),
                    stop:1 rgba(10, 10, 30, 240));
                border-radius: 12px;
            }
        """)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def _setup_timers(self):
        """Timer kurulumu"""
        # Adım timer'ı
        self.step_timer = QTimer()
        self.step_timer.timeout.connect(self.next_step)
        
        # Minimum süre timer'ı
        self.min_duration_timer = QTimer()
        self.min_duration_timer.setSingleShot(True)
        self.min_duration_timer.timeout.connect(self._min_duration_reached)
        self.min_duration_timer.start(int(self.min_duration * 1000))
        
        self.min_duration_reached = False
    
    def _min_duration_reached(self):
        """Minimum süre tamamlandı"""
        self.min_duration_reached = True
        self._check_finish_conditions()
    
    def next_step(self):
        """Sonraki yükleme adımına geç"""
        step_text = self.loading_steps.next_step()
        progress = self.loading_steps.get_progress()
        
        # UI güncelle
        if hasattr(self, 'loading_label'):
            self.loading_label.setText(step_text)
        
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set_progress(progress)
        
        # Debug log güncelle
        if self.config.get("debug_mode", False) and hasattr(self, 'debug_text'):
            logs = self.loading_steps.get_logs()
            self.debug_text.setPlainText('\n'.join(logs[-10:]))  # Son 10 log
            self.debug_text.moveCursor(self.debug_text.textCursor().End)
        
        # Signal yayınla
        self.step_changed.emit(step_text)
        
        # Son adım mı?
        if progress >= 1.0:
            self.loading_completed = True
            self._check_finish_conditions()
        else:
            # Sonraki adım için timer başlat (süreleri çok daha uzun yaptık)
            self.step_timer.start(4000 + int(progress * 1500))  # 4000-5500ms arası (her adım 4-5.5 saniye)
    
    def _check_finish_conditions(self):
        """Bitiş koşullarını kontrol et"""
        if hasattr(self, 'loading_completed') and self.loading_completed and self.min_duration_reached:
            self._finish_splash()
    
    def _finish_splash(self):
        """Splash screen'i bitir"""
        try:
            # Fade out animasyonu
            fade_duration = self.config.get("animation", {}).get("fade_out_duration", 700)
            
            self.fade_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.fade_effect)
            
            self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
            self.fade_animation.setDuration(fade_duration)
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.finished.connect(self._on_fade_finished)
            self.fade_animation.start()
            
        except Exception as e:
            self.logger.error(f"Fade out animation failed: {e}")
            self._on_fade_finished()
    
    def _on_fade_finished(self):
        """Fade animasyonu tamamlandı"""
        self.splash_finished.emit()
        self.close()
    
    def mousePressEvent(self, event):
        """Mouse tıklaması - splash'i hızlandır"""
        if self.min_duration_reached:
            self.loading_completed = True
            self._check_finish_conditions()

class SplashManager:
    """Splash screen yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("SplashManager")
        self.splash = None
        self.config = SplashConfig()
    
    def show_splash(self) -> Optional[SplashScreen]:
        """Splash screen'i göster"""
        try:
            if not PYQT_AVAILABLE:
                self.logger.warning("PyQt6 not available, skipping splash screen")
                return None
            
            # Custom splash kontrolü
            if self.config.get("custom_splash_enabled", False):
                custom_splash = self._try_load_custom_splash()
                if custom_splash:
                    return custom_splash
            
            # Standart splash
            self.splash = SplashScreen(self.kernel)
            self.splash.show()
            
            self.logger.info("Splash screen displayed")
            return self.splash
            
        except Exception as e:
            self.logger.error(f"Failed to show splash screen: {e}")
            return None
    
    def _try_load_custom_splash(self) -> Optional[SplashScreen]:
        """Özel splash screen yüklemeyi dene"""
        try:
            # Kullanıcı özel splash'i
            if self.kernel:
                users_module = self.kernel.get_module("users")
                if users_module:
                    current_user = users_module.get_current_user()
                    if current_user:
                        custom_splash_path = Path(f"users/{current_user}/custom_splash.py")
                        if custom_splash_path.exists():
                            # Özel splash yükleme kodu buraya
                            self.logger.info(f"Custom splash found for user {current_user}")
                            # Şimdilik standart splash döndür
                            pass
            
            return None
            
        except Exception as e:
            self.logger.error(f"Custom splash loading failed: {e}")
            return None
    
    def hide_splash(self):
        """Splash screen'i gizle"""
        if self.splash:
            self.splash._finish_splash()

# Kolaylık fonksiyonları
_splash_manager = None

def init_splash_manager(kernel=None):
    """Splash manager'ı başlat"""
    global _splash_manager
    _splash_manager = SplashManager(kernel)
    return _splash_manager

def get_splash_manager() -> Optional[SplashManager]:
    """Splash manager'ı al"""
    return _splash_manager

def show_splash(kernel=None) -> Optional[SplashScreen]:
    """Hızlı splash gösterme"""
    manager = init_splash_manager(kernel)
    return manager.show_splash() 