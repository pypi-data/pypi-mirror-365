"""
PyCloud OS Login Screen
Kullanıcı seçimli ve parola korumalı giriş ekranı
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                                QScrollArea, QFrame, QMessageBox, QGridLayout,
                                QSpacerItem, QSizePolicy)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
    from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPalette, QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

@dataclass
class UserProfile:
    """Kullanıcı profili"""
    username: str
    display_name: str
    password_hash: str
    avatar_path: str = ""
    theme: str = "dark"
    role: str = "user"
    last_login: Optional[datetime] = None
    login_count: int = 0
    auto_login: bool = False

class LoginManager:
    """Login yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("LoginManager")
        self.users_dir = Path("users")
        self.users_dir.mkdir(exist_ok=True)
        self.config_file = self.users_dir / "login_config.json"
        
        self.users: Dict[str, UserProfile] = {}
        self.selected_user: Optional[str] = None
        self.failed_attempts: Dict[str, int] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        
        self.load_users()
        self.create_default_user()
    
    def load_users(self):
        """Kullanıcıları yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for username, user_data in data.get("users", {}).items():
                    self.users[username] = UserProfile(
                        username=user_data["username"],
                        display_name=user_data.get("display_name", username),
                        password_hash=user_data["password_hash"],
                        avatar_path=user_data.get("avatar_path", ""),
                        theme=user_data.get("theme", "dark"),
                        role=user_data.get("role", "user"),
                        last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None,
                        login_count=user_data.get("login_count", 0),
                        auto_login=user_data.get("auto_login", False)
                    )
                    
                self.logger.info(f"Loaded {len(self.users)} users")
                
        except Exception as e:
            self.logger.error(f"Failed to load users: {e}")
    
    def save_users(self):
        """Kullanıcıları kaydet"""
        try:
            data = {
                "users": {}
            }
            
            for username, user in self.users.items():
                data["users"][username] = {
                    "username": user.username,
                    "display_name": user.display_name,
                    "password_hash": user.password_hash,
                    "avatar_path": user.avatar_path,
                    "theme": user.theme,
                    "role": user.role,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "login_count": user.login_count,
                    "auto_login": user.auto_login
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save users: {e}")
    
    def create_default_user(self):
        """Varsayılan kullanıcı oluştur"""
        if not self.users:
            default_user = UserProfile(
                username="admin",
                display_name="Yönetici",
                password_hash=self.hash_password("admin"),
                avatar_path="",
                theme="dark",
                role="admin",
                auto_login=True
            )
            
            self.users["admin"] = default_user
            self.save_users()
            self.logger.info("Created default admin user")
    
    def hash_password(self, password: str) -> str:
        """Parolayı hash'le"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username: str, password: str) -> bool:
        """Parolayı doğrula"""
        if username not in self.users:
            return False
        
        # Hesap kilitli mi kontrol et
        if self.is_account_locked(username):
            return False
        
        user = self.users[username]
        password_hash = self.hash_password(password)
        
        if password_hash == user.password_hash:
            # Başarılı giriş
            self.failed_attempts[username] = 0
            user.last_login = datetime.now()
            user.login_count += 1
            self.save_users()
            return True
        else:
            # Başarısız giriş
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            
            # 3 başarısız denemede hesabı kilitle
            if self.failed_attempts[username] >= 3:
                self.locked_accounts[username] = datetime.now()
                self.logger.warning(f"Account locked: {username}")
            
            return False
    
    def is_account_locked(self, username: str) -> bool:
        """Hesap kilitli mi?"""
        if username not in self.locked_accounts:
            return False
        
        # 5 dakika sonra kilidi aç
        lock_time = self.locked_accounts[username]
        if (datetime.now() - lock_time).seconds > 300:
            del self.locked_accounts[username]
            self.failed_attempts[username] = 0
            return False
        
        return True
    
    def get_auto_login_user(self) -> Optional[str]:
        """Otomatik giriş kullanıcısını al"""
        for username, user in self.users.items():
            if user.auto_login:
                return username
        return None

if PYQT_AVAILABLE:
    class UserButton(QPushButton):
        """Kullanıcı seçim butonu"""
        
        user_selected = pyqtSignal(str)
        
        def __init__(self, user: UserProfile):
            super().__init__()
            self.user = user
            self.setup_ui()
        
        def setup_ui(self):
            """Buton UI'ını kur"""
            self.setFixedSize(200, 120)
            self.setObjectName("userButton")
            
            # Layout
            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(8)
            
            # Avatar
            avatar_label = QLabel()
            avatar_label.setFixedSize(64, 64)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Avatar resmi yükle
            if self.user.avatar_path and Path(self.user.avatar_path).exists():
                pixmap = QPixmap(self.user.avatar_path)
                pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                avatar_label.setPixmap(pixmap)
            else:
                # Varsayılan avatar
                avatar_label.setText("👤")
                avatar_label.setStyleSheet("font-size: 48px;")
            
            layout.addWidget(avatar_label)
            
            # Kullanıcı adı
            name_label = QLabel(self.user.display_name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
            layout.addWidget(name_label)
            
            # Role
            role_label = QLabel(self.user.role.title())
            role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            role_label.setStyleSheet("font-size: 12px; color: #888;")
            layout.addWidget(role_label)
            
            self.setup_style()
            self.clicked.connect(lambda: self.user_selected.emit(self.user.username))
        
        def setup_style(self):
            """Buton stilini ayarla"""
            self.setStyleSheet("""
                QPushButton#userButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid transparent;
                    border-radius: 15px;
                    padding: 10px;
                }
                QPushButton#userButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-color: rgba(33, 150, 243, 0.8);
                }
                QPushButton#userButton:pressed {
                    background-color: rgba(33, 150, 243, 0.3);
                }
            """)

    class PasswordDialog(QWidget):
        """Parola giriş dialogu"""
        
        login_attempt = pyqtSignal(str, str)  # username, password
        back_requested = pyqtSignal()
        
        def __init__(self, user: UserProfile):
            super().__init__()
            self.user = user
            self.attempts = 0
            self.setup_ui()
        
        def setup_ui(self):
            """UI'ı kur"""
            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(20)
            
            # Avatar ve kullanıcı adı
            user_info = QVBoxLayout()
            user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_info.setSpacing(10)
            
            # Avatar
            avatar_label = QLabel()
            avatar_label.setFixedSize(80, 80)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if self.user.avatar_path and Path(self.user.avatar_path).exists():
                pixmap = QPixmap(self.user.avatar_path)
                pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                avatar_label.setPixmap(pixmap)
            else:
                avatar_label.setText("👤")
                avatar_label.setStyleSheet("font-size: 60px;")
            
            user_info.addWidget(avatar_label)
            
            # Kullanıcı adı
            name_label = QLabel(self.user.display_name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
            user_info.addWidget(name_label)
            
            layout.addLayout(user_info)
            
            # Parola girişi
            password_layout = QVBoxLayout()
            password_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            password_layout.setSpacing(10)
            
            # Parola etiketi
            password_label = QLabel("Parola:")
            password_label.setStyleSheet("color: white; font-size: 14px;")
            password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            password_layout.addWidget(password_label)
            
            # Parola girişi
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setFixedSize(250, 40)
            self.password_input.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 20px;
                    padding: 10px 15px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #2196f3;
                }
            """)
            self.password_input.returnPressed.connect(self.attempt_login)
            password_layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Hata mesajı
            self.error_label = QLabel()
            self.error_label.setStyleSheet("color: #f44336; font-size: 12px;")
            self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.error_label.hide()
            password_layout.addWidget(self.error_label)
            
            layout.addLayout(password_layout)
            
            # Butonlar
            button_layout = QHBoxLayout()
            button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.setSpacing(15)
            
            # Geri butonu
            back_btn = QPushButton("← Geri")
            back_btn.setFixedSize(100, 35)
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 17px;
                    color: white;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            back_btn.clicked.connect(self.back_requested.emit)
            button_layout.addWidget(back_btn)
            
            # Giriş butonu
            login_btn = QPushButton("Giriş Yap")
            login_btn.setFixedSize(120, 35)
            login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    border: none;
                    border-radius: 17px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976d2;
                }
                QPushButton:pressed {
                    background-color: #0d47a1;
                }
            """)
            login_btn.clicked.connect(self.attempt_login)
            button_layout.addWidget(login_btn)
            
            layout.addLayout(button_layout)
            
            # Focus'u parola alanına ver
            self.password_input.setFocus()
        
        def attempt_login(self):
            """Giriş denemesi"""
            password = self.password_input.text()
            if password:
                self.login_attempt.emit(self.user.username, password)
        
        def show_error(self, message: str):
            """Hata mesajı göster"""
            self.error_label.setText(message)
            self.error_label.show()
            self.password_input.clear()
            self.password_input.setFocus()
            
            # Hata mesajını 3 saniye sonra gizle
            QTimer.singleShot(3000, self.error_label.hide)

    class CloudLogin(QMainWindow):
        """Ana giriş penceresi"""
        
        login_successful = pyqtSignal(str)  # username
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.logger = logging.getLogger("CloudLogin")
            
            self.login_manager = LoginManager(kernel)
            self.current_widget = None
            
            self.setup_ui()
            self.setup_connections()
            
            # Otomatik giriş kontrolü
            auto_user = self.login_manager.get_auto_login_user()
            if auto_user:
                QTimer.singleShot(1000, lambda: self.auto_login(auto_user))
        
        def setup_ui(self):
            """Ana UI'ı kur"""
            self.setWindowTitle("PyCloud OS - Giriş")
            self.setFixedSize(1200, 800)
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            
            # Ana widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Arkaplan
            self.setup_background()
            
            # Ana layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Üst spacer
            main_layout.addStretch(1)
            
            # Logo ve başlık
            header_layout = QVBoxLayout()
            header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.setSpacing(20)
            
            # Logo
            logo_label = QLabel("🌩️")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("font-size: 80px;")
            header_layout.addWidget(logo_label)
            
            # Başlık
            title_label = QLabel("PyCloud OS")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 36px; 
                font-weight: bold; 
                color: white;
            """)
            header_layout.addWidget(title_label)
            
            main_layout.addLayout(header_layout)
            
            # Content area
            self.content_area = QWidget()
            self.content_area.setFixedSize(800, 300)
            
            content_layout = QHBoxLayout()
            content_layout.addStretch()
            content_layout.addWidget(self.content_area)
            content_layout.addStretch()
            
            main_layout.addLayout(content_layout)
            
            # Alt spacer
            main_layout.addStretch(1)
            
            # Alt bilgi
            footer_layout = QHBoxLayout()
            footer_layout.setContentsMargins(20, 10, 20, 20)
            
            # Saat
            self.time_label = QLabel()
            self.time_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
            footer_layout.addWidget(self.time_label)
            
            footer_layout.addStretch()
            
            # Versiyon
            version_label = QLabel("v0.9.0-dev")
            version_label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
            footer_layout.addWidget(version_label)
            
            main_layout.addLayout(footer_layout)
            
            # Zamanı güncelle
            self.time_timer = QTimer()
            self.time_timer.timeout.connect(self.update_time)
            self.time_timer.start(1000)
            self.update_time()
            
            # Kullanıcı seçim ekranını göster
            self.show_user_selection()
        
        def setup_background(self):
            """Arkaplan ayarla"""
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
                }
            """)
        
        def setup_connections(self):
            """Sinyal bağlantılarını kur"""
            pass
        
        def update_time(self):
            """Zamanı güncelle"""
            current_time = datetime.now().strftime("%d %B %Y, %H:%M")
            self.time_label.setText(current_time)
        
        def show_user_selection(self):
            """Kullanıcı seçim ekranını göster"""
            if self.current_widget:
                self.current_widget.setParent(None)
            
            self.current_widget = QWidget()
            layout = QVBoxLayout(self.current_widget)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(20)
            
            # Başlık
            title = QLabel("Bir kullanıcı seçin")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            layout.addWidget(title)
            
            # Kullanıcı butonları
            users_layout = QHBoxLayout()
            users_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            users_layout.setSpacing(20)
            
            for username, user in self.login_manager.users.items():
                user_btn = UserButton(user)
                user_btn.user_selected.connect(self.select_user)
                users_layout.addWidget(user_btn)
            
            layout.addLayout(users_layout)
            
            # Content area'ya ekle
            content_layout = QVBoxLayout(self.content_area)
            content_layout.addWidget(self.current_widget)
        
        def select_user(self, username: str):
            """Kullanıcı seç"""
            if username not in self.login_manager.users:
                return
            
            user = self.login_manager.users[username]
            
            # Hesap kilitli mi kontrol et
            if self.login_manager.is_account_locked(username):
                QMessageBox.warning(self, "Hesap Kilitli", 
                                  "Bu hesap geçici olarak kilitlenmiş. Lütfen 5 dakika sonra tekrar deneyin.")
                return
            
            self.show_password_dialog(user)
        
        def show_password_dialog(self, user: UserProfile):
            """Parola dialogunu göster"""
            if self.current_widget:
                self.current_widget.setParent(None)
            
            self.current_widget = PasswordDialog(user)
            self.current_widget.login_attempt.connect(self.attempt_login)
            self.current_widget.back_requested.connect(self.show_user_selection)
            
            # Content area'ya ekle
            content_layout = QVBoxLayout(self.content_area)
            content_layout.addWidget(self.current_widget)
        
        def attempt_login(self, username: str, password: str):
            """Giriş denemesi"""
            self.logger.info(f"Login attempt for user: {username}")
            
            if self.login_manager.verify_password(username, password):
                self.logger.info(f"Login successful for user: {username}")
                self.login_successful.emit(username)
                
                # Kullanıcı oturumunu başlat
                if self.kernel:
                    user_manager = self.kernel.get_module("users")
                    if user_manager:
                        user_manager.login_user(username)
                
                self.close()
            else:
                self.logger.warning(f"Login failed for user: {username}")
                
                if self.login_manager.is_account_locked(username):
                    error_msg = "Hesap 5 dakika süreyle kilitlendi."
                else:
                    remaining = 3 - self.login_manager.failed_attempts.get(username, 0)
                    error_msg = f"Hatalı parola. Kalan deneme: {remaining}"
                
                if isinstance(self.current_widget, PasswordDialog):
                    self.current_widget.show_error(error_msg)
        
        def auto_login(self, username: str):
            """Otomatik giriş"""
            self.logger.info(f"Auto login for user: {username}")
            self.login_successful.emit(username)
            
            # Kullanıcı oturumunu başlat
            if self.kernel:
                user_manager = self.kernel.get_module("users")
                if user_manager:
                    user_manager.login_user(username)
            
            self.close()
        
        def keyPressEvent(self, event):
            """Klavye olayları"""
            if event.key() == Qt.Key.Key_Escape:
                if isinstance(self.current_widget, PasswordDialog):
                    self.show_user_selection()
                else:
                    event.ignore()
            else:
                super().keyPressEvent(event)

# Text-mode fallback
class CloudLoginText:
    """Text modunda giriş ekranı"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("CloudLoginText")
        self.login_manager = LoginManager(kernel)
    
    def show(self):
        """Giriş ekranını göster"""
        print("\n" + "="*50)
        print("🌩️  PyCloud OS - Giriş Ekranı")
        print("="*50)
        
        # Kullanıcıları listele
        print("\nKullanıcılar:")
        for i, (username, user) in enumerate(self.login_manager.users.items(), 1):
            status = " (Kilitli)" if self.login_manager.is_account_locked(username) else ""
            print(f"  {i}. {user.display_name} ({username}){status}")
        
        while True:
            try:
                # Kullanıcı seçimi
                choice = input(f"\nKullanıcı seçin (1-{len(self.login_manager.users)}) veya 'q' çıkış: ").strip()
                
                if choice.lower() == 'q':
                    return False
                
                user_index = int(choice) - 1
                usernames = list(self.login_manager.users.keys())
                
                if 0 <= user_index < len(usernames):
                    username = usernames[user_index]
                    
                    # Hesap kilitli mi?
                    if self.login_manager.is_account_locked(username):
                        print("❌ Bu hesap geçici olarak kilitli. Lütfen daha sonra tekrar deneyin.")
                        continue
                    
                    # Parola iste
                    password = input(f"Parola ({username}): ")
                    
                    if self.login_manager.verify_password(username, password):
                        print(f"✅ Giriş başarılı! Hoş geldin {self.login_manager.users[username].display_name}")
                        
                        # Kullanıcı oturumunu başlat
                        if self.kernel:
                            user_manager = self.kernel.get_module("users")
                            if user_manager:
                                user_manager.login_user(username)
                        
                        return True
                    else:
                        if self.login_manager.is_account_locked(username):
                            print("❌ Hesap 5 dakika süreyle kilitlendi.")
                        else:
                            remaining = 3 - self.login_manager.failed_attempts.get(username, 0)
                            print(f"❌ Hatalı parola. Kalan deneme: {remaining}")
                else:
                    print("❌ Geçersiz seçim.")
                    
            except ValueError:
                print("❌ Lütfen geçerli bir sayı girin.")
            except KeyboardInterrupt:
                print("\n\nÇıkış yapılıyor...")
                return False

def create_login_screen(kernel=None):
    """Giriş ekranı oluştur"""
    if PYQT_AVAILABLE:
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            login = CloudLogin(kernel)
            return login
        except Exception as e:
            logging.getLogger("CloudLogin").error(f"Failed to create GUI login: {e}")
    
    # Text-mode fallback
    return CloudLoginText(kernel)

# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if PYQT_AVAILABLE:
        app = QApplication([])
        login = CloudLogin()
        login.show()
        app.exec()
    else:
        login = CloudLoginText()
        login.show() 