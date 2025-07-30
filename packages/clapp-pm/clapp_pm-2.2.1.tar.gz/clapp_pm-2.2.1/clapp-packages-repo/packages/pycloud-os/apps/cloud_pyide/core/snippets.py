"""
Cloud PyIDE - Kod Parçacığı Yöneticisi
Snippet sistemi ve yönetimi
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class CodeSnippet:
    """Kod parçacığı"""
    name: str
    trigger: str
    code: str
    description: str
    language: str = "python"
    category: str = "general"

class SnippetManager:
    """Snippet yöneticisi"""
    
    def __init__(self, snippets_dir: Optional[Path] = None):
        self.logger = logging.getLogger("SnippetManager")
        
        # Snippet dizini
        if snippets_dir:
            self.snippets_dir = snippets_dir
        else:
            self.snippets_dir = Path("snippets")
        
        self.snippets_dir.mkdir(exist_ok=True)
        
        # Snippet'ler
        self.snippets: Dict[str, CodeSnippet] = {}
        
        # Yükle
        self.load_snippets()
    
    def load_snippets(self):
        """Snippet'leri yükle"""
        try:
            # Varsayılan snippet'leri yükle
            self.load_default_snippets()
            
            # Kullanıcı snippet'lerini yükle
            self.load_user_snippets()
            
            self.logger.info(f"Loaded {len(self.snippets)} snippets")
            
        except Exception as e:
            self.logger.error(f"Error loading snippets: {e}")
    
    def load_default_snippets(self):
        """Varsayılan snippet'leri yükle"""
        default_snippets = [
            CodeSnippet(
                name="Main Function",
                trigger="main",
                code='if __name__ == "__main__":\n    main()',
                description="Ana fonksiyon şablonu",
                category="structure"
            ),
            CodeSnippet(
                name="Class Definition",
                trigger="class",
                code='class ${1:ClassName}:\n    def __init__(self):\n        pass',
                description="Sınıf tanımı şablonu",
                category="structure"
            ),
            CodeSnippet(
                name="Function Definition",
                trigger="def",
                code='def ${1:function_name}(${2:args}):\n    """${3:Description}"""\n    pass',
                description="Fonksiyon tanımı şablonu",
                category="structure"
            ),
            CodeSnippet(
                name="Try-Except Block",
                trigger="try",
                code='try:\n    ${1:code}\nexcept ${2:Exception} as e:\n    ${3:handle_exception}',
                description="Try-except bloku",
                category="control"
            ),
            CodeSnippet(
                name="For Loop",
                trigger="for",
                code='for ${1:item} in ${2:iterable}:\n    ${3:code}',
                description="For döngüsü",
                category="control"
            ),
            CodeSnippet(
                name="While Loop",
                trigger="while",
                code='while ${1:condition}:\n    ${2:code}',
                description="While döngüsü",
                category="control"
            ),
            CodeSnippet(
                name="If Statement",
                trigger="if",
                code='if ${1:condition}:\n    ${2:code}',
                description="If ifadesi",
                category="control"
            ),
            CodeSnippet(
                name="List Comprehension",
                trigger="lc",
                code='[${1:expression} for ${2:item} in ${3:iterable}]',
                description="Liste anlama",
                category="data"
            ),
            CodeSnippet(
                name="Dictionary Comprehension",
                trigger="dc",
                code='{${1:key}: ${2:value} for ${3:item} in ${4:iterable}}',
                description="Sözlük anlama",
                category="data"
            ),
            CodeSnippet(
                name="Import Statement",
                trigger="imp",
                code='import ${1:module}',
                description="Import ifadesi",
                category="import"
            ),
            CodeSnippet(
                name="From Import",
                trigger="from",
                code='from ${1:module} import ${2:name}',
                description="From import ifadesi",
                category="import"
            ),
            CodeSnippet(
                name="With Statement",
                trigger="with",
                code='with ${1:expression} as ${2:variable}:\n    ${3:code}',
                description="With ifadesi",
                category="control"
            ),
            CodeSnippet(
                name="Lambda Function",
                trigger="lambda",
                code='lambda ${1:args}: ${2:expression}',
                description="Lambda fonksiyonu",
                category="function"
            ),
            CodeSnippet(
                name="Property Decorator",
                trigger="prop",
                code='@property\ndef ${1:name}(self):\n    return self._${1:name}',
                description="Property decorator",
                category="decorator"
            ),
            CodeSnippet(
                name="Static Method",
                trigger="static",
                code='@staticmethod\ndef ${1:method_name}(${2:args}):\n    """${3:Description}"""\n    pass',
                description="Static method",
                category="method"
            ),
            CodeSnippet(
                name="Class Method",
                trigger="classmethod",
                code='@classmethod\ndef ${1:method_name}(cls${2:, args}):\n    """${3:Description}"""\n    pass',
                description="Class method",
                category="method"
            ),
            CodeSnippet(
                name="Docstring",
                trigger="doc",
                code='"""\n${1:Description}\n\nArgs:\n    ${2:arg}: ${3:description}\n\nReturns:\n    ${4:return_description}\n"""',
                description="Docstring şablonu",
                category="documentation"
            ),
            CodeSnippet(
                name="Print Debug",
                trigger="pdb",
                code='print(f"DEBUG: ${1:variable} = {${1:variable}}")',
                description="Debug print",
                category="debug"
            ),
            CodeSnippet(
                name="File Read",
                trigger="fread",
                code='with open("${1:filename}", "r", encoding="utf-8") as f:\n    ${2:content} = f.read()',
                description="Dosya okuma",
                category="file"
            ),
            CodeSnippet(
                name="File Write",
                trigger="fwrite",
                code='with open("${1:filename}", "w", encoding="utf-8") as f:\n    f.write(${2:content})',
                description="Dosya yazma",
                category="file"
            ),
            CodeSnippet(
                name="JSON Load",
                trigger="jload",
                code='with open("${1:filename}", "r", encoding="utf-8") as f:\n    ${2:data} = json.load(f)',
                description="JSON yükleme",
                category="json"
            ),
            CodeSnippet(
                name="JSON Save",
                trigger="jsave",
                code='with open("${1:filename}", "w", encoding="utf-8") as f:\n    json.dump(${2:data}, f, indent=2, ensure_ascii=False)',
                description="JSON kaydetme",
                category="json"
            )
        ]
        
        for snippet in default_snippets:
            self.snippets[snippet.trigger] = snippet
    
    def load_user_snippets(self):
        """Kullanıcı snippet'lerini yükle"""
        snippets_file = self.snippets_dir / "user_snippets.json"
        
        if not snippets_file.exists():
            return
        
        try:
            with open(snippets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for snippet_data in data:
                snippet = CodeSnippet(**snippet_data)
                self.snippets[snippet.trigger] = snippet
                
        except Exception as e:
            self.logger.error(f"Error loading user snippets: {e}")
    
    def save_user_snippets(self):
        """Kullanıcı snippet'lerini kaydet"""
        try:
            # Sadece kullanıcı snippet'lerini kaydet (varsayılanları değil)
            user_snippets = []
            
            for snippet in self.snippets.values():
                if snippet.category not in ["structure", "control", "data", "import", "function", "decorator", "method", "documentation", "debug", "file", "json"]:
                    user_snippets.append(asdict(snippet))
            
            snippets_file = self.snippets_dir / "user_snippets.json"
            
            with open(snippets_file, 'w', encoding='utf-8') as f:
                json.dump(user_snippets, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved {len(user_snippets)} user snippets")
            
        except Exception as e:
            self.logger.error(f"Error saving user snippets: {e}")
    
    def get_snippet_by_trigger(self, trigger: str) -> Optional[CodeSnippet]:
        """Trigger'a göre snippet bul"""
        return self.snippets.get(trigger)
    
    def get_snippets_by_category(self, category: str) -> List[CodeSnippet]:
        """Kategoriye göre snippet'leri al"""
        return [snippet for snippet in self.snippets.values() if snippet.category == category]
    
    def get_all_snippets(self) -> List[CodeSnippet]:
        """Tüm snippet'leri al"""
        return list(self.snippets.values())
    
    def get_categories(self) -> List[str]:
        """Tüm kategorileri al"""
        categories = set(snippet.category for snippet in self.snippets.values())
        return sorted(categories)
    
    def search_snippets(self, query: str) -> List[CodeSnippet]:
        """Snippet ara"""
        query = query.lower()
        results = []
        
        for snippet in self.snippets.values():
            if (query in snippet.name.lower() or 
                query in snippet.trigger.lower() or 
                query in snippet.description.lower() or
                query in snippet.code.lower()):
                results.append(snippet)
        
        return results
    
    def add_snippet(self, snippet: CodeSnippet) -> bool:
        """Snippet ekle"""
        try:
            if snippet.trigger in self.snippets:
                self.logger.warning(f"Snippet with trigger '{snippet.trigger}' already exists")
                return False
            
            self.snippets[snippet.trigger] = snippet
            self.save_user_snippets()
            
            self.logger.info(f"Added snippet: {snippet.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding snippet: {e}")
            return False
    
    def update_snippet(self, old_trigger: str, snippet: CodeSnippet) -> bool:
        """Snippet güncelle"""
        try:
            if old_trigger in self.snippets:
                del self.snippets[old_trigger]
            
            self.snippets[snippet.trigger] = snippet
            self.save_user_snippets()
            
            self.logger.info(f"Updated snippet: {snippet.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating snippet: {e}")
            return False
    
    def delete_snippet(self, trigger: str) -> bool:
        """Snippet sil"""
        try:
            if trigger not in self.snippets:
                self.logger.warning(f"Snippet with trigger '{trigger}' not found")
                return False
            
            snippet = self.snippets[trigger]
            
            # Varsayılan snippet'leri silmeye izin verme
            if snippet.category in ["structure", "control", "data", "import", "function", "decorator", "method", "documentation", "debug", "file", "json"]:
                self.logger.warning(f"Cannot delete default snippet: {trigger}")
                return False
            
            del self.snippets[trigger]
            self.save_user_snippets()
            
            self.logger.info(f"Deleted snippet: {snippet.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting snippet: {e}")
            return False
    
    def expand_snippet(self, snippet: CodeSnippet, variables: Dict[str, str] = None) -> str:
        """Snippet'i genişlet"""
        code = snippet.code
        
        if variables:
            # Değişkenleri değiştir
            for var, value in variables.items():
                code = code.replace(f"${{{var}}}", value)
        
        # Placeholder'ları temizle
        import re
        code = re.sub(r'\$\{\d+:[^}]*\}', '', code)
        code = re.sub(r'\$\{\d+\}', '', code)
        
        return code
    
    def export_snippets(self, file_path: Path) -> bool:
        """Snippet'leri dışa aktar"""
        try:
            snippets_data = [asdict(snippet) for snippet in self.snippets.values()]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(snippets_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(snippets_data)} snippets to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting snippets: {e}")
            return False
    
    def import_snippets(self, file_path: Path) -> bool:
        """Snippet'leri içe aktar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                snippets_data = json.load(f)
            
            imported_count = 0
            
            for snippet_data in snippets_data:
                snippet = CodeSnippet(**snippet_data)
                
                # Çakışma kontrolü
                if snippet.trigger in self.snippets:
                    self.logger.warning(f"Skipping duplicate snippet: {snippet.trigger}")
                    continue
                
                self.snippets[snippet.trigger] = snippet
                imported_count += 1
            
            self.save_user_snippets()
            
            self.logger.info(f"Imported {imported_count} snippets from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing snippets: {e}")
            return False 