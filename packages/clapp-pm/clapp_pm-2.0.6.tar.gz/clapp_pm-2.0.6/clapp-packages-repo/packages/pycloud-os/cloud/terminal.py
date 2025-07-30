"""
Cloud Terminal - PyCloud OS Terminal Uygulaması
Sistem içi komut desteği, komut geçmişi, çoklu oturum desteği ile modern terminal
"""

import sys
import os
import json
import subprocess
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# PyQt6 import with fallback
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtSerialPort import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 bulunamadı - Terminal text modunda çalışacak")

class TerminalSession:
    """Terminal oturumu"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.current_dir = os.getcwd()
        self.history: List[str] = []
        self.env_vars: Dict[str, str] = os.environ.copy()
        self.active = True
        
    def add_to_history(self, command: str):
        """Komut geçmişine ekle"""
        if command.strip() and (not self.history or self.history[-1] != command):
            self.history.append(command)
            # Son 1000 komutu tut
            if len(self.history) > 1000:
                self.history = self.history[-1000:]

class TerminalCommands:
    """Terminal komutları"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.system_commands = {
            'help': self.cmd_help,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,  # Windows alias
            'cat': self.cmd_cat,
            'echo': self.cmd_echo,
            'date': self.cmd_date,
            'whoami': self.cmd_whoami,
            'ps': self.cmd_ps,
            'kill': self.cmd_kill,
            'clapp': self.cmd_clapp,
            'pycloud': self.cmd_pycloud,
        }
    
    def execute_command(self, command: str, session: TerminalSession) -> Dict[str, Any]:
        """Komut çalıştır"""
        try:
            parts = command.strip().split()
            if not parts:
                return {"output": "", "error": "", "return_code": 0}
            
            cmd_name = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Sistem komutları
            if cmd_name in self.system_commands:
                return self.system_commands[cmd_name](args, session)
            
            # Python komutları
            if cmd_name == 'python' or cmd_name == 'python3':
                return self._execute_python(parts, session)
            
            # Harici komutlar
            return self._execute_external(parts, session)
            
        except Exception as e:
            return {
                "output": "",
                "error": f"Komut çalıştırma hatası: {e}",
                "return_code": 1
            }
    
    def cmd_help(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Yardım komutu"""
        help_text = """
PyCloud OS Terminal Komutları:

Dosya Sistemi:
  pwd                 - Mevcut dizini göster
  cd <dizin>          - Dizin değiştir  
  ls [dizin]          - Dosyaları listele
  cat <dosya>         - Dosya içeriğini göster
  
Sistem:
  ps                  - Çalışan işlemleri göster
  kill <pid>          - İşlemi sonlandır
  date                - Sistem tarih/saati
  whoami              - Mevcut kullanıcı
  
Clapp Package Manager:
  clapp list                    - Kurulu uygulamaları listele
  clapp install <app>           - Uygulama kur
  clapp remove <app>            - Uygulama kaldır
  clapp update <app>            - Uygulama güncelle
  clapp update --all            - Tüm uygulamaları güncelle
  clapp search <query>          - Uygulama ara
  clapp info <app>              - Uygulama bilgisi göster
  clapp doctor                  - Sistem sağlık kontrolü
  clapp help                    - Clapp yardımı
  
PyCloud Sistem:
  pycloud status      - Sistem durumu
  pycloud restart     - Sistemi yeniden başlat
  
Diğer:
  python <dosya>      - Python betiği çalıştır
  clear               - Ekranı temizle
  exit                - Terminal'den çık
  help                - Bu yardımı göster
"""
        return {"output": help_text, "error": "", "return_code": 0}
    
    def cmd_clear(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Ekranı temizle"""
        return {"output": "", "error": "", "return_code": 0, "clear": True}
    
    def cmd_exit(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Terminal'den çık"""
        session.active = False
        return {"output": "Terminal kapatılıyor...", "error": "", "return_code": 0, "exit": True}
    
    def cmd_pwd(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Mevcut dizini göster"""
        return {"output": session.current_dir, "error": "", "return_code": 0}
    
    def cmd_cd(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Dizin değiştir"""
        if not args:
            target_dir = str(Path.home())
        else:
            target_dir = args[0]
        
        try:
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(session.current_dir, target_dir)
            
            target_dir = os.path.abspath(target_dir)
            
            if os.path.exists(target_dir) and os.path.isdir(target_dir):
                session.current_dir = target_dir
                os.chdir(target_dir)
                return {"output": "", "error": "", "return_code": 0}
            else:
                return {"output": "", "error": f"Dizin bulunamadı: {target_dir}", "return_code": 1}
                
        except Exception as e:
            return {"output": "", "error": f"Dizin değiştirme hatası: {e}", "return_code": 1}
    
    def cmd_ls(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Dosyaları listele"""
        try:
            target_dir = args[0] if args else session.current_dir
            
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(session.current_dir, target_dir)
            
            if not os.path.exists(target_dir):
                return {"output": "", "error": f"Dizin bulunamadı: {target_dir}", "return_code": 1}
            
            items = []
            for item in sorted(os.listdir(target_dir)):
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    size_str = self._format_size(size)
                    items.append(f"📄 {item} ({size_str})")
            
            return {"output": "\n".join(items), "error": "", "return_code": 0}
            
        except Exception as e:
            return {"output": "", "error": f"Listeleme hatası: {e}", "return_code": 1}
    
    def cmd_cat(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Dosya içeriğini göster"""
        if not args:
            return {"output": "", "error": "Kullanım: cat <dosya>", "return_code": 1}
        
        try:
            file_path = args[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join(session.current_dir, file_path)
            
            if not os.path.exists(file_path):
                return {"output": "", "error": f"Dosya bulunamadı: {file_path}", "return_code": 1}
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {"output": content, "error": "", "return_code": 0}
            
        except Exception as e:
            return {"output": "", "error": f"Dosya okuma hatası: {e}", "return_code": 1}
    
    def cmd_echo(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Echo komutu"""
        return {"output": " ".join(args), "error": "", "return_code": 0}
    
    def cmd_date(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Tarih/saat göster"""
        now = datetime.now()
        return {"output": now.strftime("%Y-%m-%d %H:%M:%S"), "error": "", "return_code": 0}
    
    def cmd_whoami(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Mevcut kullanıcı"""
        import getpass
        username = getpass.getuser()
        return {"output": username, "error": "", "return_code": 0}
    
    def cmd_ps(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Çalışan işlemleri göster"""
        try:
            import psutil
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append(f"{info['pid']:>6} {info['name']:<20} CPU: {info['cpu_percent']:>5.1f}% MEM: {info['memory_percent']:>5.1f}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            header = f"{'PID':>6} {'NAME':<20} {'CPU':<10} {'MEMORY'}"
            output = header + "\n" + "-" * 50 + "\n" + "\n".join(processes[:20])
            
            return {"output": output, "error": "", "return_code": 0}
            
        except ImportError:
            return {"output": "", "error": "psutil modülü bulunamadı", "return_code": 1}
        except Exception as e:
            return {"output": "", "error": f"İşlem listesi hatası: {e}", "return_code": 1}
    
    def cmd_kill(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """İşlemi sonlandır"""
        if not args:
            return {"output": "", "error": "Kullanım: kill <pid>", "return_code": 1}
        
        try:
            pid = int(args[0])
            import psutil
            
            proc = psutil.Process(pid)
            proc.terminate()
            
            return {"output": f"İşlem {pid} sonlandırıldı", "error": "", "return_code": 0}
            
        except ValueError:
            return {"output": "", "error": "Geçersiz PID", "return_code": 1}
        except ImportError:
            return {"output": "", "error": "psutil modülü bulunamadı", "return_code": 1}
        except Exception as e:
            return {"output": "", "error": f"İşlem sonlandırma hatası: {e}", "return_code": 1}
    
    def cmd_clapp(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Clapp paket yöneticisi - Gerçek Clapp Core entegrasyonu"""
        try:
            # Clapp Core modülünü import et
            from clapp.core import ClappCore
            
            # Clapp Core instance oluştur
            clapp_core = ClappCore(self.kernel)
            
            if not args:
                return {"output": "", "error": "Kullanım: clapp <list|install|remove|update|search|info|doctor|help> [args]", "return_code": 1}
            
            # Komut satırını oluştur
            command_line = " ".join(args)
            
            # Clapp Core ile komutu çalıştır
            result = clapp_core.execute_command(command_line)
            
            # Sonucu terminal formatına çevir
            if result.result.value == "success":
                return {"output": result.output, "error": "", "return_code": 0}
            elif result.result.value == "warning":
                return {"output": result.output, "error": "", "return_code": 0}
            elif result.result.value == "info":
                return {"output": result.output, "error": "", "return_code": 0}
            else:
                return {"output": "", "error": result.output, "return_code": 1}
                
        except ImportError:
            # Fallback: Clapp Core mevcut değilse basit implementasyon
            return self._clapp_fallback(args, session)
        except Exception as e:
            return {"output": "", "error": f"Clapp hatası: {e}", "return_code": 1}
    
    def _clapp_fallback(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Clapp Core mevcut değilse fallback implementasyon"""
        action = args[0].lower()
        
        if action == "list":
            # Kurulu uygulamaları listele
            apps_dir = Path("apps")
            if not apps_dir.exists():
                return {"output": "Kurulu uygulama bulunamadı", "error": "", "return_code": 0}
            
            apps = []
            for app_dir in apps_dir.iterdir():
                if app_dir.is_dir():
                    app_json = app_dir / "app.json"
                    if app_json.exists():
                        try:
                            with open(app_json, 'r', encoding='utf-8') as f:
                                app_info = json.load(f)
                            apps.append(f"{app_info.get('id', app_dir.name):<20} - {app_info.get('name', 'Bilinmeyen')}")
                        except:
                            apps.append(f"{app_dir.name:<20} - (app.json okunamadı)")
            
            return {"output": "\n".join(apps) if apps else "Kurulu uygulama yok", "error": "", "return_code": 0}
        
        elif action == "help":
            help_text = """
Clapp Package Manager - Fallback Mode

Kullanılabilir komutlar:
  list                    - Kurulu uygulamaları listele
  
Not: Tam Clapp özelliklerini kullanmak için Clapp Core modülünü yükleyin.
"""
            return {"output": help_text.strip(), "error": "", "return_code": 0}
        
        else:
            return {"output": "", "error": f"Clapp Core mevcut değil. Sadece 'list' komutu kullanılabilir. Komut: {action}", "return_code": 1}
    
    def cmd_pycloud(self, args: List[str], session: TerminalSession) -> Dict[str, Any]:
        """PyCloud sistem komutları"""
        if not args:
            return {"output": "", "error": "Kullanım: pycloud <status|restart|shutdown>", "return_code": 1}
        
        action = args[0].lower()
        
        if action == "status":
            uptime = "Sistem aktif"
            if self.kernel:
                uptime = f"Sistem başlatma: {self.kernel.start_time if hasattr(self.kernel, 'start_time') else 'Bilinmiyor'}"
            
            status_info = f"""
PyCloud OS Sistem Durumu:
{uptime}
Aktif modüller: {len(self.kernel.modules) if self.kernel else 'Bilinmiyor'}
Çalışan servisler: Kontrol ediliyor...
Bellek kullanımı: Kontrol ediliyor...
"""
            return {"output": status_info, "error": "", "return_code": 0}
        
        elif action == "restart":
            return {"output": "Sistem yeniden başlatma komutu alındı...", "error": "", "return_code": 0}
        
        elif action == "shutdown":
            return {"output": "Sistem kapatma komutu alındı...", "error": "", "return_code": 0}
        
        else:
            return {"output": "", "error": f"Bilinmeyen işlem: {action}", "return_code": 1}
    
    def _execute_python(self, parts: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Python betiği çalıştır"""
        try:
            result = subprocess.run(
                parts, 
                cwd=session.current_dir,
                capture_output=True, 
                text=True, 
                timeout=30,
                env=session.env_vars
            )
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Komut zaman aşımına uğradı (30s)", "return_code": 124}
        except Exception as e:
            return {"output": "", "error": f"Python çalıştırma hatası: {e}", "return_code": 1}
    
    def _execute_external(self, parts: List[str], session: TerminalSession) -> Dict[str, Any]:
        """Harici komut çalıştır"""
        try:
            result = subprocess.run(
                parts, 
                cwd=session.current_dir,
                capture_output=True, 
                text=True, 
                timeout=10,
                env=session.env_vars
            )
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Komut zaman aşımına uğradı", "return_code": 124}
        except FileNotFoundError:
            return {"output": "", "error": f"Komut bulunamadı: {parts[0]}", "return_code": 127}
        except Exception as e:
            return {"output": "", "error": f"Komut çalıştırma hatası: {e}", "return_code": 1}
    
    def _format_size(self, size_bytes: int) -> str:
        """Boyutu okunabilir formata çevir"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"

# PyQt6 GUI Terminal
if PYQT_AVAILABLE:
    class TerminalWidget(QWidget):
        """PyQt6 Terminal Widget"""
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.commands = TerminalCommands(kernel)
            self.sessions: Dict[str, TerminalSession] = {}
            self.current_session_id = "main"
            
            # Ana oturum oluştur
            self.sessions[self.current_session_id] = TerminalSession(self.current_session_id)
            
            self.init_ui()
            self.apply_theme()
        
        def init_ui(self):
            """UI'yı başlat"""
            self.setWindowTitle("PyCloud Terminal")
            self.setGeometry(100, 100, 800, 600)
            
            layout = QVBoxLayout()
            
            # Terminal çıktı alanı
            self.output_area = QTextEdit()
            self.output_area.setReadOnly(True)
            self.output_area.setFont(QFont("Consolas", 12))
            
            # Komut girişi
            self.input_line = QLineEdit()
            self.input_line.setFont(QFont("Consolas", 12))
            self.input_line.returnPressed.connect(self.execute_command)
            
            # Oturum sekmeleri
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.tabCloseRequested.connect(self.close_session)
            
            # İlk sekme
            main_tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(self.output_area)
            tab_layout.addWidget(self.input_line)
            main_tab.setLayout(tab_layout)
            
            self.tab_widget.addTab(main_tab, "Terminal")
            
            # Ana layout
            layout.addWidget(self.tab_widget)
            
            # Durum çubuğu
            status_layout = QHBoxLayout()
            self.status_label = QLabel("PyCloud Terminal Hazır")
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            status_layout.addWidget(self.status_label)
            status_layout.addStretch()
            
            layout.addLayout(status_layout)
            
            self.setLayout(layout)
            
            # Hoşgeldin mesajı
            self.write_output("PyCloud OS Terminal v1.0\n")
            self.write_output("Yardım için 'help' yazın.\n\n")
            self.show_prompt()
        
        def apply_theme(self):
            """Tema uygula"""
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #0a0a0a;
                    color: #00ff00;
                    border: 1px solid #333333;
                    font-family: Consolas, monospace;
                }
                QLineEdit {
                    background-color: #0a0a0a;
                    color: #00ff00;
                    border: 1px solid #333333;
                    padding: 5px;
                    font-family: Consolas, monospace;
                }
                QTabWidget::pane {
                    border: 1px solid #333333;
                }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 8px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #404040;
                }
            """)
        
        def execute_command(self):
            """Komut çalıştır"""
            command = self.input_line.text().strip()
            if not command:
                return
            
            session = self.sessions[self.current_session_id]
            session.add_to_history(command)
            
            # Komutu göster
            self.write_output(f"$ {command}\n")
            
            # Komutu çalıştır
            result = self.commands.execute_command(command, session)
            
            # Çıktıyı göster
            if result.get("output"):
                self.write_output(result["output"] + "\n")
            
            if result.get("error"):
                self.write_error(result["error"] + "\n")
            
            # Özel durumlar
            if result.get("clear"):
                self.output_area.clear()
            
            if result.get("exit"):
                self.close()
                return
            
            self.input_line.clear()
            self.show_prompt()
        
        def write_output(self, text: str):
            """Çıktı yaz"""
            self.output_area.insertPlainText(text)
            self.output_area.moveCursor(QTextCursor.MoveOperation.End)
        
        def write_error(self, text: str):
            """Hata yaz"""
            cursor = self.output_area.textCursor()
            format = QTextCharFormat()
            format.setForeground(QColor("#ff0000"))
            cursor.insertText(text, format)
            self.output_area.moveCursor(QTextCursor.MoveOperation.End)
        
        def show_prompt(self):
            """Prompt göster"""
            session = self.sessions[self.current_session_id]
            prompt = f"{os.path.basename(session.current_dir)}$ "
            self.write_output(prompt)
        
        def close_session(self, index: int):
            """Oturumu kapat"""
            if self.tab_widget.count() > 1:
                self.tab_widget.removeTab(index)

# Text-mode Terminal (PyQt6 yoksa)
class TextTerminal:
    """Text-mode terminal"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.commands = TerminalCommands(kernel)
        self.session = TerminalSession("main")
        self.running = True
    
    def run(self):
        """Terminal'i çalıştır"""
        print("PyCloud OS Terminal v1.0 (Text Mode)")
        print("Yardım için 'help' yazın.\n")
        
        while self.running and self.session.active:
            try:
                prompt = f"{os.path.basename(self.session.current_dir)}$ "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                self.session.add_to_history(command)
                result = self.commands.execute_command(command, self.session)
                
                if result.get("output"):
                    print(result["output"])
                
                if result.get("error"):
                    print(f"Error: {result['error']}", file=sys.stderr)
                
                if result.get("exit"):
                    break
                    
            except KeyboardInterrupt:
                print("\nTerminal kapatılıyor...")
                break
            except EOFError:
                break
        
        print("Terminal kapatıldı.")

# Ana fonksiyonlar
def create_terminal_app(kernel=None):
    """Terminal uygulaması oluştur"""
    if PYQT_AVAILABLE:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        terminal = TerminalWidget(kernel)
        terminal.show()
        return terminal
    else:
        return TextTerminal(kernel)

def run_terminal(kernel=None):
    """Terminal'i çalıştır"""
    if PYQT_AVAILABLE:
        terminal = create_terminal_app(kernel)
        return terminal
    else:
        terminal = TextTerminal(kernel)
        terminal.run()
        return None

if __name__ == "__main__":
    run_terminal() 