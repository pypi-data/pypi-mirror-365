#!/usr/bin/env python3
"""
CloudSearch - PyCloud OS Gelişmiş Arama Uygulaması
Modern Flet tabanlı dosya ve içerik arama motoru
"""

import flet as ft
import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import logging

# PyOS core modüllerini import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class CloudSearchEngine:
    """Gelişmiş arama motoru"""
    
    def __init__(self):
        self.logger = logging.getLogger("CloudSearchEngine")
        self.search_index = {}
        self.search_paths = [
            "/users",
            "/apps", 
            "/system"
        ]
        
    def build_index(self):
        """Arama indeksini oluştur"""
        self.logger.info("Arama indeksi oluşturuluyor...")
        
        # Simüle edilmiş dosya sistemi
        mock_files = [
            {
                "name": "document.txt",
                "path": "/users/documents/document.txt",
                "type": "text",
                "size": "2.4 KB",
                "modified": "2 saat önce",
                "content": "Bu bir test belgesidir. Python ve PyCloud OS hakkında bilgiler içerir.",
                "tags": ["belge", "test", "python"]
            },
            {
                "name": "project.py",
                "path": "/users/projects/project.py",
                "type": "python",
                "size": "15.7 KB", 
                "modified": "1 gün önce",
                "content": "import flet as ft\nclass MyApp:\n    def __init__(self):\n        pass",
                "tags": ["kod", "python", "flet"]
            },
            {
                "name": "image.png",
                "path": "/users/pictures/image.png",
                "type": "image",
                "size": "1.2 MB",
                "modified": "3 gün önce",
                "content": "",
                "tags": ["resim", "png", "grafik"]
            },
            {
                "name": "config.json",
                "path": "/system/config/config.json",
                "type": "config",
                "size": "856 B",
                "modified": "1 hafta önce",
                "content": '{"theme": "dark", "language": "tr"}',
                "tags": ["ayar", "json", "sistem"]
            },
            {
                "name": "notes.md",
                "path": "/users/documents/notes.md",
                "type": "markdown",
                "size": "3.1 KB",
                "modified": "5 saat önce",
                "content": "# PyCloud OS Notları\n\n## Özellikler\n- Modern arayüz\n- Flet entegrasyonu",
                "tags": ["not", "markdown", "belge"]
            },
            {
                "name": "app.py",
                "path": "/apps/cloud_search/main.py",
                "type": "python",
                "size": "8.9 KB",
                "modified": "Az önce",
                "content": "CloudSearch uygulaması ana dosyası",
                "tags": ["uygulama", "arama", "python"]
            }
        ]
        
        for file_data in mock_files:
            self.search_index[file_data["path"]] = file_data
            
        self.logger.info(f"İndeks oluşturuldu: {len(self.search_index)} dosya")
        
    def search(self, query: str, search_type: str = "all") -> list:
        """Arama yap"""
        if not query or len(query) < 2:
            return []
            
        query = query.lower()
        results = []
        
        for path, file_data in self.search_index.items():
            match_score = 0
            
            # Dosya adında arama
            if query in file_data["name"].lower():
                match_score += 10
                
            # İçerikte arama
            if query in file_data["content"].lower():
                match_score += 5
                
            # Etiketlerde arama
            for tag in file_data["tags"]:
                if query in tag.lower():
                    match_score += 3
                    
            # Dosya tipinde arama
            if search_type != "all" and file_data["type"] != search_type:
                match_score = 0
                
            if match_score > 0:
                file_data["match_score"] = match_score
                results.append(file_data.copy())
                
        # Skorlara göre sırala
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:20]  # İlk 20 sonuç

class CloudSearchApp:
    """CloudSearch ana uygulama sınıfı"""
    
    def __init__(self):
        self.logger = logging.getLogger("CloudSearchApp")
        self.search_engine = CloudSearchEngine()
        self.search_results = []
        self.current_query = ""
        self.search_type = "all"
        
        # Arama indeksini oluştur
        self.search_engine.build_index()
        
    def search_files(self, e):
        """Dosya arama yap"""
        query = e.control.value.strip()
        if len(query) < 2:
            self.search_results = []
            self.update_results(e.page)
            return
            
        self.current_query = query
        self.logger.info(f"Arama yapılıyor: {query}")
        
        # Arama yap
        self.search_results = self.search_engine.search(query, self.search_type)
        self.update_results(e.page)
        
    def filter_by_type(self, file_type: str, e):
        """Dosya tipine göre filtrele"""
        self.search_type = file_type
        self.logger.info(f"Filtre: {file_type}")
        
        if self.current_query:
            self.search_results = self.search_engine.search(self.current_query, file_type)
            self.update_results(e.page)
            
        # Filtre butonlarını güncelle
        self.update_filter_buttons(e.page)
        
    def update_filter_buttons(self, page):
        """Filtre butonlarını güncelle"""
        # Bu fonksiyon UI'daki filtre butonlarının görünümünü güncelleyecek
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"🔍 Filtre: {self.search_type}"),
            bgcolor=ft.Colors.BLUE_400
        )
        page.snack_bar.open = True
        page.update()
        
    def update_results(self, page):
        """Arama sonuçlarını güncelle"""
        # Sonuç sayısını göster
        if hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"🔍 {len(self.search_results)} sonuç bulundu"),
                bgcolor=ft.Colors.GREEN_400
            )
            page.snack_bar.open = True
            page.update()
            
    def open_file(self, file_path: str, e):
        """Dosyayı aç"""
        self.logger.info(f"Dosya açılıyor: {file_path}")
        if hasattr(e.page, 'snack_bar'):
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"📂 {file_path} açılıyor..."),
                bgcolor=ft.Colors.BLUE_400
            )
            e.page.snack_bar.open = True
            e.page.update()
            
    def get_file_icon(self, file_type: str) -> str:
        """Dosya tipine göre ikon döndür"""
        icons = {
            "text": ft.Icons.DESCRIPTION,
            "python": ft.Icons.CODE,
            "image": ft.Icons.IMAGE,
            "config": ft.Icons.SETTINGS,
            "markdown": ft.Icons.ARTICLE,
            "folder": ft.Icons.FOLDER,
            "default": ft.Icons.INSERT_DRIVE_FILE
        }
        return icons.get(file_type, icons["default"])
        
    def get_file_color(self, file_type: str) -> str:
        """Dosya tipine göre renk döndür"""
        colors = {
            "text": ft.Colors.BLUE_400,
            "python": ft.Colors.GREEN_400,
            "image": ft.Colors.PURPLE_400,
            "config": ft.Colors.ORANGE_400,
            "markdown": ft.Colors.TEAL_400,
            "folder": ft.Colors.YELLOW_400,
            "default": ft.Colors.GREY_400
        }
        return colors.get(file_type, colors["default"])
        
    def build_ui(self, page: ft.Page):
        """Ana UI'ı oluştur"""
        
        # Arama sonuçları listesi
        def build_results():
            if not self.search_results:
                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.SEARCH,
                                color=ft.Colors.WHITE30,
                                size=64
                            ),
                            ft.Text(
                                "Arama yapmak için yukarıdaki kutuya yazın",
                                size=16,
                                color=ft.Colors.WHITE54,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                f"İndekste {len(self.search_engine.search_index)} dosya var",
                                size=12,
                                color=ft.Colors.WHITE38,
                                text_align=ft.TextAlign.CENTER
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16
                    ),
                    alignment=ft.alignment.center,
                    height=300
                )
                
            result_items = []
            for result in self.search_results:
                result_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                # Dosya ikonu
                                ft.Container(
                                    content=ft.Icon(
                                        self.get_file_icon(result['type']),
                                        color=ft.Colors.WHITE,
                                        size=24
                                    ),
                                    bgcolor=self.get_file_color(result['type']),
                                    border_radius=10,
                                    width=40,
                                    height=40,
                                    alignment=ft.alignment.center
                                ),
                                
                                # Dosya bilgileri
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(
                                                result['name'],
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS
                                            ),
                                            ft.Text(
                                                result['path'],
                                                size=11,
                                                color=ft.Colors.WHITE60,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS
                                            ),
                                            ft.Row(
                                                controls=[
                                                    ft.Text(
                                                        result['size'],
                                                        size=10,
                                                        color=ft.Colors.WHITE54
                                                    ),
                                                    ft.Text("•", size=10, color=ft.Colors.WHITE54),
                                                    ft.Text(
                                                        result['modified'],
                                                        size=10,
                                                        color=ft.Colors.WHITE54
                                                    ),
                                                    ft.Text("•", size=10, color=ft.Colors.WHITE54),
                                                    ft.Text(
                                                        f"Skor: {result.get('match_score', 0)}",
                                                        size=10,
                                                        color=ft.Colors.GREEN_400
                                                    )
                                                ],
                                                spacing=4
                                            )
                                        ],
                                        spacing=4,
                                        tight=True
                                    ),
                                    expand=True
                                ),
                                
                                # Aç butonu
                                ft.IconButton(
                                    icon=ft.Icons.OPEN_IN_NEW,
                                    icon_color=ft.Colors.WHITE70,
                                    icon_size=20,
                                    on_click=lambda e, path=result['path']: self.open_file(path, e)
                                )
                            ],
                            spacing=16,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=ft.padding.all(16),
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                        border_radius=12
                    ),
                    elevation=0,
                    color=ft.Colors.TRANSPARENT
                )
                
                result_items.append(result_card)
                
            return ft.ListView(
                controls=result_items,
                spacing=12,
                expand=True,
                auto_scroll=False
            )
        
        # Ana layout
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Başlık
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE, size=32),
                                ft.Text(
                                    "CloudSearch",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Container(expand=True),
                                ft.Text(
                                    f"v1.0.0",
                                    size=12,
                                    color=ft.Colors.WHITE54
                                )
                            ]
                        ),
                        padding=ft.padding.only(bottom=24)
                    ),
                    
                    # Arama kutusu
                    ft.Container(
                        content=ft.TextField(
                            hint_text="Dosya adı, içerik, etiket ara...",
                            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
                            text_style=ft.TextStyle(color=ft.Colors.WHITE, size=16),
                            border_color=ft.Colors.WHITE30,
                            focused_border_color=ft.Colors.BLUE_400,
                            cursor_color=ft.Colors.WHITE,
                            prefix_icon=ft.Icons.SEARCH,
                            border_radius=16,
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                            height=56,
                            on_change=lambda e: self.search_files(e)
                        ),
                        padding=ft.padding.only(bottom=20)
                    ),
                    
                    # Filtre butonları
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "📄 Tümü",
                                    bgcolor=ft.Colors.BLUE_400 if self.search_type == "all" else ft.Colors.GREY_600,
                                    color=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                    on_click=lambda e: self.filter_by_type("all", e)
                                ),
                                ft.ElevatedButton(
                                    "📝 Belgeler",
                                    bgcolor=ft.Colors.BLUE_400 if self.search_type == "text" else ft.Colors.GREY_600,
                                    color=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                    on_click=lambda e: self.filter_by_type("text", e)
                                ),
                                ft.ElevatedButton(
                                    "🖼️ Resimler",
                                    bgcolor=ft.Colors.PURPLE_400 if self.search_type == "image" else ft.Colors.GREY_600,
                                    color=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                    on_click=lambda e: self.filter_by_type("image", e)
                                ),
                                ft.ElevatedButton(
                                    "💻 Kod",
                                    bgcolor=ft.Colors.GREEN_400 if self.search_type == "python" else ft.Colors.GREY_600,
                                    color=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                    on_click=lambda e: self.filter_by_type("python", e)
                                )
                            ],
                            spacing=12,
                            scroll=ft.ScrollMode.AUTO
                        ),
                        padding=ft.padding.only(bottom=20)
                    ),
                    
                    # Sonuç sayısı
                    ft.Text(
                        f"Sonuçlar ({len(self.search_results)})" if self.search_results else "Arama sonuçları burada görünecek",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE70
                    ),
                    
                    # Arama sonuçları
                    ft.Container(
                        content=build_results(),
                        expand=True,
                        padding=ft.padding.only(top=16)
                    )
                ],
                spacing=0,
                expand=True
            ),
            padding=ft.padding.all(24),
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_900),
            expand=True
        )

def main(page: ft.Page):
    """Ana uygulama fonksiyonu"""
    page.title = "CloudSearch - PyCloud OS"
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    page.bgcolor = ft.Colors.GREY_900
    page.theme_mode = ft.ThemeMode.DARK
    
    # Uygulama oluştur
    app = CloudSearchApp()
    
    # UI'ı sayfaya ekle
    page.add(app.build_ui(page))

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP) 