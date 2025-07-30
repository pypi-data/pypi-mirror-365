"""
Cloud Browser PDF Görüntüleyici
PDF dosyalarını görüntüleme desteği
"""

import os
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import *
    from PyQt6.QtWebEngineCore import *
    from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
    WEBENGINE_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        WEBENGINE_AVAILABLE = False
    except ImportError:
        raise ImportError("PyQt6 is required for Cloud Browser")

class PDFViewer(QWidget):
    """
    PDF görüntüleyici widget'ı
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pdf_path = None
        self.current_page = 1
        self.total_pages = 1
        self.zoom_factor = 1.0
        
        self.init_ui()
    
    def init_ui(self):
        """UI'yı başlat"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PDF toolbar
        self.create_pdf_toolbar()
        layout.addWidget(self.pdf_toolbar)
        
        # PDF görüntüleme alanı
        if WEBENGINE_AVAILABLE:
            # WebEngine ile PDF görüntüleme
            self.pdf_view = QWebEngineView()
            self.pdf_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.pdf_view.customContextMenuRequested.connect(self.show_pdf_context_menu)
        else:
            # Basit metin görüntüleme
            self.pdf_view = QTextEdit()
            self.pdf_view.setReadOnly(True)
            self.pdf_view.setHtml("""
                <h2>PDF Görüntüleyici</h2>
                <p>WebEngine mevcut değil. PDF dosyaları görüntülenemiyor.</p>
                <p>PDF desteği için PyQt6-WebEngine gereklidir:</p>
                <code>pip install PyQt6-WebEngine</code>
            """)
        
        layout.addWidget(self.pdf_view)
        
        # Status bar
        self.status_label = QLabel("PDF yüklenmedi")
        layout.addWidget(self.status_label)
    
    def create_pdf_toolbar(self):
        """PDF toolbar oluştur"""
        self.pdf_toolbar = QToolBar()
        self.pdf_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Dosya aç
        open_action = QAction("📂 Aç", self)
        open_action.setToolTip("PDF dosyası aç")
        open_action.triggered.connect(self.open_pdf_file)
        self.pdf_toolbar.addAction(open_action)
        
        self.pdf_toolbar.addSeparator()
        
        # Sayfa navigasyonu
        self.prev_page_action = QAction("⬅️ Önceki", self)
        self.prev_page_action.setToolTip("Önceki sayfa")
        self.prev_page_action.triggered.connect(self.prev_page)
        self.prev_page_action.setEnabled(False)
        self.pdf_toolbar.addAction(self.prev_page_action)
        
        # Sayfa numarası
        self.page_label = QLabel("Sayfa: 0 / 0")
        self.pdf_toolbar.addWidget(self.page_label)
        
        self.next_page_action = QAction("➡️ Sonraki", self)
        self.next_page_action.setToolTip("Sonraki sayfa")
        self.next_page_action.triggered.connect(self.next_page)
        self.next_page_action.setEnabled(False)
        self.pdf_toolbar.addAction(self.next_page_action)
        
        self.pdf_toolbar.addSeparator()
        
        # Zoom kontrolleri
        zoom_out_action = QAction("🔍-", self)
        zoom_out_action.setToolTip("Uzaklaştır")
        zoom_out_action.triggered.connect(self.zoom_out)
        self.pdf_toolbar.addAction(zoom_out_action)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.pdf_toolbar.addWidget(self.zoom_label)
        
        zoom_in_action = QAction("🔍+", self)
        zoom_in_action.setToolTip("Yakınlaştır")
        zoom_in_action.triggered.connect(self.zoom_in)
        self.pdf_toolbar.addAction(zoom_in_action)
        
        zoom_fit_action = QAction("📄 Sığdır", self)
        zoom_fit_action.setToolTip("Sayfaya sığdır")
        zoom_fit_action.triggered.connect(self.zoom_fit)
        self.pdf_toolbar.addAction(zoom_fit_action)
        
        self.pdf_toolbar.addSeparator()
        
        # Yazdır
        print_action = QAction("🖨️ Yazdır", self)
        print_action.setToolTip("PDF'i yazdır")
        print_action.triggered.connect(self.print_pdf)
        self.pdf_toolbar.addAction(print_action)
        
        # Stil uygula
        self.pdf_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }
            QToolBar QAction {
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QToolBar QAction:hover {
                background-color: #e9ecef;
            }
            QLabel {
                padding: 4px 8px;
                color: #6c757d;
            }
        """)
    
    def load_pdf(self, file_path: str):
        """PDF dosyası yükle"""
        if not os.path.exists(file_path):
            self.show_error("Dosya bulunamadı", f"PDF dosyası bulunamadı: {file_path}")
            return False
        
        if not file_path.lower().endswith('.pdf'):
            self.show_error("Geçersiz dosya", "Bu dosya bir PDF değil.")
            return False
        
        try:
            self.current_pdf_path = file_path
            
            if WEBENGINE_AVAILABLE:
                # WebEngine ile PDF yükle
                file_url = QUrl.fromLocalFile(os.path.abspath(file_path))
                self.pdf_view.setUrl(file_url)
                
                # PDF yükleme tamamlandığında
                self.pdf_view.loadFinished.connect(self.pdf_loaded)
            else:
                # Basit metin gösterimi
                self.pdf_view.setHtml(f"""
                    <h2>PDF Dosyası</h2>
                    <p><b>Dosya:</b> {os.path.basename(file_path)}</p>
                    <p><b>Yol:</b> {file_path}</p>
                    <p><b>Boyut:</b> {self.format_file_size(os.path.getsize(file_path))}</p>
                    <br>
                    <p>WebEngine mevcut olmadığı için PDF içeriği görüntülenemiyor.</p>
                    <p>PDF desteği için PyQt6-WebEngine gereklidir.</p>
                """)
            
            # UI güncelle
            self.update_ui()
            return True
            
        except Exception as e:
            self.show_error("PDF Yükleme Hatası", f"PDF yüklenirken hata oluştu: {e}")
            return False
    
    def pdf_loaded(self, success):
        """PDF yükleme tamamlandığında"""
        if success:
            self.status_label.setText(f"PDF yüklendi: {os.path.basename(self.current_pdf_path)}")
            # TODO: Sayfa sayısını al (WebEngine API'si gerekli)
            self.total_pages = 1  # Placeholder
            self.current_page = 1
            self.update_page_info()
        else:
            self.show_error("PDF Yükleme Hatası", "PDF dosyası yüklenemedi.")
    
    def open_pdf_file(self):
        """PDF dosyası seç ve aç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF Dosyası Aç",
            "",
            "PDF Dosyaları (*.pdf);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def prev_page(self):
        """Önceki sayfa"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_page_info()
            # TODO: WebEngine'de sayfa değiştirme implementasyonu
    
    def next_page(self):
        """Sonraki sayfa"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_page_info()
            # TODO: WebEngine'de sayfa değiştirme implementasyonu
    
    def zoom_in(self):
        """Yakınlaştır"""
        self.zoom_factor = min(self.zoom_factor * 1.2, 5.0)
        self.apply_zoom()
    
    def zoom_out(self):
        """Uzaklaştır"""
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.2)
        self.apply_zoom()
    
    def zoom_fit(self):
        """Sayfaya sığdır"""
        self.zoom_factor = 1.0
        self.apply_zoom()
    
    def apply_zoom(self):
        """Zoom uygula"""
        if WEBENGINE_AVAILABLE and hasattr(self.pdf_view, 'setZoomFactor'):
            self.pdf_view.setZoomFactor(self.zoom_factor)
        
        # Zoom label güncelle
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
    
    def print_pdf(self):
        """PDF'i yazdır"""
        if not self.current_pdf_path:
            self.show_error("Hata", "Yazdırılacak PDF dosyası yok.")
            return
        
        if WEBENGINE_AVAILABLE:
            # WebEngine print dialog
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec() == QDialog.DialogCode.Accepted:
                # TODO: WebEngine print implementasyonu
                QMessageBox.information(self, "Yazdırma", "Yazdırma özelliği henüz implementasyonda...")
        else:
            QMessageBox.information(self, "Yazdırma", "Yazdırma için WebEngine gereklidir.")
    
    def show_pdf_context_menu(self, position):
        """PDF context menü"""
        if not WEBENGINE_AVAILABLE:
            return
        
        menu = QMenu(self)
        
        # Kopyala
        copy_action = menu.addAction("📋 Kopyala")
        copy_action.triggered.connect(self.copy_selection)
        
        # Seç
        select_all_action = menu.addAction("🔘 Tümünü Seç")
        select_all_action.triggered.connect(self.select_all)
        
        menu.addSeparator()
        
        # Zoom
        zoom_in_action = menu.addAction("🔍+ Yakınlaştır")
        zoom_in_action.triggered.connect(self.zoom_in)
        
        zoom_out_action = menu.addAction("🔍- Uzaklaştır")
        zoom_out_action.triggered.connect(self.zoom_out)
        
        zoom_fit_action = menu.addAction("📄 Sığdır")
        zoom_fit_action.triggered.connect(self.zoom_fit)
        
        menu.addSeparator()
        
        # Yazdır
        print_action = menu.addAction("🖨️ Yazdır")
        print_action.triggered.connect(self.print_pdf)
        
        menu.exec(self.pdf_view.mapToGlobal(position))
    
    def copy_selection(self):
        """Seçili metni kopyala"""
        if WEBENGINE_AVAILABLE and hasattr(self.pdf_view, 'page'):
            # TODO: WebEngine selection copy implementasyonu
            pass
    
    def select_all(self):
        """Tümünü seç"""
        if WEBENGINE_AVAILABLE and hasattr(self.pdf_view, 'page'):
            # TODO: WebEngine select all implementasyonu
            pass
    
    def update_ui(self):
        """UI'yı güncelle"""
        has_pdf = self.current_pdf_path is not None
        
        # Sayfa navigasyon butonları
        self.prev_page_action.setEnabled(has_pdf and self.current_page > 1)
        self.next_page_action.setEnabled(has_pdf and self.current_page < self.total_pages)
        
        # Sayfa bilgisi
        if has_pdf:
            self.update_page_info()
        else:
            self.page_label.setText("Sayfa: 0 / 0")
    
    def update_page_info(self):
        """Sayfa bilgisini güncelle"""
        self.page_label.setText(f"Sayfa: {self.current_page} / {self.total_pages}")
        
        # Navigasyon butonları
        self.prev_page_action.setEnabled(self.current_page > 1)
        self.next_page_action.setEnabled(self.current_page < self.total_pages)
    
    def show_error(self, title: str, message: str):
        """Hata mesajı göster"""
        QMessageBox.critical(self, title, message)
        self.status_label.setText(f"Hata: {message}")
    
    def format_file_size(self, size_bytes: int) -> str:
        """Dosya boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

class PDFTab(QWidget):
    """
    PDF sekmesi için özel widget
    """
    
    def __init__(self, pdf_path: str, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PDF viewer
        self.pdf_viewer = PDFViewer(self)
        layout.addWidget(self.pdf_viewer)
        
        # PDF'i yükle
        self.pdf_viewer.load_pdf(pdf_path)
    
    def get_title(self) -> str:
        """Sekme başlığını al"""
        if self.pdf_path:
            return f"📄 {os.path.basename(self.pdf_path)}"
        return "📄 PDF"
    
    def get_url(self) -> str:
        """URL'yi al"""
        if self.pdf_path:
            return f"file://{self.pdf_path}"
        return "about:blank"

def is_pdf_url(url: str) -> bool:
    """URL PDF dosyası mı kontrol et"""
    if not url:
        return False
    
    # URL'den dosya uzantısını al
    if url.lower().endswith('.pdf'):
        return True
    
    # MIME type kontrolü (gelecekte implementasyon)
    # TODO: HTTP response header'larından MIME type kontrolü
    
    return False

def create_pdf_tab(url: str, parent=None) -> Optional[PDFTab]:
    """PDF sekmesi oluştur"""
    if not is_pdf_url(url):
        return None
    
    # file:// URL'sini dosya yoluna çevir
    if url.startswith('file://'):
        file_path = url[7:]  # file:// kısmını kaldır
        if os.path.exists(file_path):
            return PDFTab(file_path, parent)
    
    # HTTP/HTTPS URL'leri için (gelecekte implementasyon)
    # TODO: PDF dosyasını indir ve geçici dosya olarak aç
    
    return None 