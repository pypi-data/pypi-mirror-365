"""
Cloud PyIDE - Proje Başlatıcı Arayüz ve Template Yöneticisi
.template formatında proje şablonları
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

@dataclass
class ProjectTemplate:
    """Proje şablonu"""
    id: str
    name: str
    description: str
    category: str
    author: str
    version: str
    icon: str = ""
    files: List[str] = None
    variables: Dict[str, str] = None

class TemplateManager:
    """Template yöneticisi"""
    
    def __init__(self, ide_instance=None):
        self.ide_instance = ide_instance
        self.logger = logging.getLogger("TemplateManager")
        
        # Template dizini
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Yüklü template'ler
        self.templates: Dict[str, ProjectTemplate] = {}
        
        # Yükle
        self.load_templates()
    
    def load_templates(self):
        """Template'leri yükle"""
        try:
            # Varsayılan template'leri yükle
            self.load_default_templates()
            
            # Kullanıcı template'lerini yükle
            self.load_user_templates()
            
            self.logger.info(f"Loaded {len(self.templates)} templates")
            
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
    
    def load_default_templates(self):
        """Varsayılan template'leri yükle"""
        default_templates = [
            ProjectTemplate(
                id="python_cli",
                name="Python CLI Application",
                description="Komut satırı uygulaması için temel Python projesi",
                category="Python",
                author="PyCloud",
                version="1.0.0",
                icon="🐍",
                files=["main.py", "requirements.txt", "README.md", ".gitignore"],
                variables={
                    "project_name": "My CLI App",
                    "author_name": "Your Name",
                    "description": "A Python CLI application"
                }
            ),
            ProjectTemplate(
                id="flask_app",
                name="Flask Web Application",
                description="Flask web uygulaması şablonu",
                category="Web",
                author="PyCloud",
                version="1.0.0",
                icon="🌐",
                files=["app.py", "requirements.txt", "templates/", "static/", "README.md"],
                variables={
                    "app_name": "My Flask App",
                    "author_name": "Your Name",
                    "description": "A Flask web application"
                }
            ),
            ProjectTemplate(
                id="tkinter_gui",
                name="Tkinter GUI Application",
                description="Tkinter ile masaüstü GUI uygulaması",
                category="Desktop",
                author="PyCloud",
                version="1.0.0",
                icon="🖥️",
                files=["main.py", "gui/", "requirements.txt", "README.md"],
                variables={
                    "app_name": "My GUI App",
                    "author_name": "Your Name",
                    "description": "A Tkinter GUI application"
                }
            ),
            ProjectTemplate(
                id="data_science",
                name="Data Science Project",
                description="Veri bilimi projesi için Jupyter notebook'lar ve Python scriptleri",
                category="Data Science",
                author="PyCloud",
                version="1.0.0",
                icon="📊",
                files=["analysis.ipynb", "data/", "src/", "requirements.txt", "README.md"],
                variables={
                    "project_name": "Data Analysis Project",
                    "author_name": "Your Name",
                    "description": "A data science project"
                }
            ),
            ProjectTemplate(
                id="api_server",
                name="REST API Server",
                description="FastAPI ile REST API sunucusu",
                category="API",
                author="PyCloud",
                version="1.0.0",
                icon="🔌",
                files=["main.py", "models/", "routes/", "requirements.txt", "README.md"],
                variables={
                    "api_name": "My API",
                    "author_name": "Your Name",
                    "description": "A REST API server"
                }
            ),
            ProjectTemplate(
                id="markdown_notes",
                name="Markdown Notes",
                description="Markdown notları için organize edilmiş proje yapısı",
                category="Documentation",
                author="PyCloud",
                version="1.0.0",
                icon="📝",
                files=["README.md", "notes/", "assets/", ".gitignore"],
                variables={
                    "project_name": "My Notes",
                    "author_name": "Your Name",
                    "description": "Personal notes and documentation"
                }
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
            
            # Template dizinini oluştur
            template_dir = self.templates_dir / template.id
            if not template_dir.exists():
                self.create_template_files(template)
    
    def load_user_templates(self):
        """Kullanıcı template'lerini yükle"""
        try:
            for template_file in self.templates_dir.glob("*.template"):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                template = ProjectTemplate(**template_data)
                self.templates[template.id] = template
                
                self.logger.info(f"Loaded user template: {template.name}")
                
        except Exception as e:
            self.logger.error(f"Error loading user templates: {e}")
    
    def create_template_files(self, template: ProjectTemplate):
        """Template dosyalarını oluştur"""
        try:
            template_dir = self.templates_dir / template.id
            template_dir.mkdir(exist_ok=True)
            
            # Template.json dosyası oluştur
            template_json = template_dir / "template.json"
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "author": template.author,
                "version": template.version,
                "icon": template.icon,
                "files": template.files or [],
                "variables": template.variables or {}
            }
            
            with open(template_json, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            # Örnek dosyaları oluştur
            self.create_sample_files(template, template_dir)
            
        except Exception as e:
            self.logger.error(f"Error creating template files: {e}")
    
    def create_sample_files(self, template: ProjectTemplate, template_dir: Path):
        """Örnek dosyaları oluştur"""
        try:
            if template.id == "python_cli":
                # main.py
                main_py = template_dir / "main.py"
                with open(main_py, 'w', encoding='utf-8') as f:
                    f.write('''#!/usr/bin/env python3
"""
{{project_name}}
{{description}}

Author: {{author_name}}
"""

import argparse
import sys


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="{{description}}")
    parser.add_argument("--version", action="version", version="1.0.0")
    
    args = parser.parse_args()
    
    print("Merhaba, {{project_name}}!")


if __name__ == "__main__":
    main()
''')
                
                # requirements.txt
                req_txt = template_dir / "requirements.txt"
                with open(req_txt, 'w', encoding='utf-8') as f:
                    f.write("# Python dependencies\n")
                
                # README.md
                readme_md = template_dir / "README.md"
                with open(readme_md, 'w', encoding='utf-8') as f:
                    f.write('''# {{project_name}}

{{description}}

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
python main.py
```

## Yazar

{{author_name}}
''')
            
            elif template.id == "flask_app":
                # app.py
                app_py = template_dir / "app.py"
                with open(app_py, 'w', encoding='utf-8') as f:
                    f.write('''from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='{{app_name}}')


@app.route('/api/hello')
def api_hello():
    return {'message': 'Hello from {{app_name}}!'}


if __name__ == '__main__':
    app.run(debug=True)
''')
                
                # templates dizini
                templates_dir = template_dir / "templates"
                templates_dir.mkdir(exist_ok=True)
                
                # templates/index.html
                index_html = templates_dir / "index.html"
                with open(index_html, 'w', encoding='utf-8') as f:
                    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>{{app_name}}</h1>
    <p>{{description}}</p>
</body>
</html>
''')
                
                # static dizini
                static_dir = template_dir / "static"
                static_dir.mkdir(exist_ok=True)
                
                # requirements.txt
                req_txt = template_dir / "requirements.txt"
                with open(req_txt, 'w', encoding='utf-8') as f:
                    f.write("Flask==2.3.3\n")
            
            # Diğer template'ler için benzer dosyalar...
            
        except Exception as e:
            self.logger.error(f"Error creating sample files: {e}")
    
    def create_project_from_template(self, template_id: str, project_path: str, variables: Dict[str, str] = None) -> bool:
        """Template'den proje oluştur"""
        try:
            if template_id not in self.templates:
                self.logger.error(f"Template not found: {template_id}")
                return False
            
            template = self.templates[template_id]
            template_dir = self.templates_dir / template_id
            
            if not template_dir.exists():
                self.logger.error(f"Template directory not found: {template_dir}")
                return False
            
            project_path = Path(project_path)
            
            # Proje dizinini oluştur
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Template dosyalarını kopyala
            for item in template_dir.iterdir():
                if item.name == "template.json":
                    continue
                
                if item.is_file():
                    # Dosyayı kopyala ve değişkenleri değiştir
                    self.copy_and_process_file(item, project_path / item.name, variables or {})
                elif item.is_dir():
                    # Dizini kopyala
                    shutil.copytree(item, project_path / item.name, dirs_exist_ok=True)
            
            self.logger.info(f"Created project from template {template_id} at {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating project from template: {e}")
            return False
    
    def copy_and_process_file(self, source_file: Path, target_file: Path, variables: Dict[str, str]):
        """Dosyayı kopyala ve değişkenleri işle"""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Değişkenleri değiştir
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                content = content.replace(placeholder, var_value)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.logger.error(f"Error processing file {source_file}: {e}")
            # Fallback: sadece kopyala
            shutil.copy2(source_file, target_file)
    
    def get_available_templates(self) -> List[ProjectTemplate]:
        """Mevcut template'leri al"""
        return list(self.templates.values())
    
    def get_templates_by_category(self, category: str) -> List[ProjectTemplate]:
        """Kategoriye göre template'leri al"""
        return [template for template in self.templates.values() if template.category == category]
    
    def get_categories(self) -> List[str]:
        """Tüm kategorileri al"""
        categories = set(template.category for template in self.templates.values())
        return sorted(categories)
    
    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """Template al"""
        return self.templates.get(template_id)
    
    def install_template(self, template_path: str) -> bool:
        """Template kur"""
        try:
            template_path = Path(template_path)
            
            if not template_path.exists():
                self.logger.error(f"Template path not found: {template_path}")
                return False
            
            if template_path.is_file() and template_path.suffix == '.zip':
                # ZIP dosyasından kur
                return self.install_from_zip(template_path)
            elif template_path.is_dir():
                # Dizinden kur
                return self.install_from_directory(template_path)
            else:
                self.logger.error(f"Invalid template format: {template_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing template: {e}")
            return False
    
    def install_from_zip(self, zip_path: Path) -> bool:
        """ZIP dosyasından template kur"""
        try:
            import zipfile
            import tempfile
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # ZIP'i çıkar
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Çıkarılan dizini kur
                extracted_dir = Path(temp_dir)
                
                # Ana dizini bul
                subdirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
                if len(subdirs) == 1:
                    template_dir = subdirs[0]
                else:
                    template_dir = extracted_dir
                
                return self.install_from_directory(template_dir)
                
        except Exception as e:
            self.logger.error(f"Error installing from ZIP: {e}")
            return False
    
    def install_from_directory(self, source_dir: Path) -> bool:
        """Dizinden template kur"""
        try:
            # Template.json dosyasını kontrol et
            template_json = source_dir / "template.json"
            if not template_json.exists():
                self.logger.error(f"template.json not found in {source_dir}")
                return False
            
            # Template bilgisini oku
            with open(template_json, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template_id = template_data.get('id')
            if not template_id:
                self.logger.error("Template ID not found in template.json")
                return False
            
            # Hedef dizini oluştur
            target_dir = self.templates_dir / template_id
            
            if target_dir.exists():
                self.logger.warning(f"Template already exists: {template_id}")
                shutil.rmtree(target_dir)
            
            # Dosyaları kopyala
            shutil.copytree(source_dir, target_dir)
            
            # .template dosyası oluştur
            template_file = self.templates_dir / f"{template_id}.template"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            # Template'i yükle
            template = ProjectTemplate(**template_data)
            self.templates[template_id] = template
            
            self.logger.info(f"Installed template: {template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing from directory: {e}")
            return False
    
    def uninstall_template(self, template_id: str) -> bool:
        """Template'i kaldır"""
        try:
            if template_id not in self.templates:
                self.logger.warning(f"Template not found: {template_id}")
                return False
            
            template = self.templates[template_id]
            
            # Varsayılan template'leri silmeye izin verme
            if template.author == "PyCloud":
                self.logger.warning(f"Cannot delete default template: {template_id}")
                return False
            
            # Dosyaları sil
            template_dir = self.templates_dir / template_id
            if template_dir.exists():
                shutil.rmtree(template_dir)
            
            # .template dosyasını sil
            template_file = self.templates_dir / f"{template_id}.template"
            if template_file.exists():
                template_file.unlink()
            
            # Listeden kaldır
            del self.templates[template_id]
            
            self.logger.info(f"Uninstalled template: {template_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error uninstalling template {template_id}: {e}")
            return False
    
    def export_template(self, template_id: str, export_path: Path) -> bool:
        """Template'i dışa aktar"""
        try:
            if template_id not in self.templates:
                self.logger.warning(f"Template not found: {template_id}")
                return False
            
            template_dir = self.templates_dir / template_id
            if not template_dir.exists():
                self.logger.error(f"Template directory not found: {template_dir}")
                return False
            
            # ZIP olarak dışa aktar
            import zipfile
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in template_dir.rglob('*'):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(template_dir)
                        zip_file.write(file_path, arc_name)
            
            self.logger.info(f"Exported template {template_id} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting template: {e}")
            return False 