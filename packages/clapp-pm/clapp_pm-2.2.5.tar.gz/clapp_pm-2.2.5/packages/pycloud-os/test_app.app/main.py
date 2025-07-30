#!/usr/bin/env python3
"""
Test Uygulaması
PyCloud OS için basit test uygulaması
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Uygulaması")
        self.setGeometry(100, 100, 400, 300)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Başlık
        title_label = QLabel("🧪 Test Uygulaması")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # Açıklama
        desc_label = QLabel("Bu PyCloud OS için test uygulamasıdır.\n.app paketi kurulum sistemi test ediliyor.")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(desc_label)
        
        # Buton
        test_button = QPushButton("Test Başarılı! ✅")
        test_button.setStyleSheet("font-size: 16px; padding: 10px; margin: 20px;")
        test_button.clicked.connect(self.show_success)
        layout.addWidget(test_button)
        
        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    
    def show_success(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Başarılı", "Test uygulaması başarıyla çalışıyor!")

def main():
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 