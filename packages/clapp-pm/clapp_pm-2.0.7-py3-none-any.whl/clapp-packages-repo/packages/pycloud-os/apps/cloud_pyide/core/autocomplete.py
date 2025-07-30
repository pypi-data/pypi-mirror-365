"""
Cloud PyIDE - Kod Tamamlama Motoru
Python kod tamamlama ve önerileri
"""

import re
import keyword
import builtins
import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class CompletionItem:
    """Tamamlama öğesi"""
    text: str
    kind: str  # keyword, function, class, variable, module, snippet
    detail: str = ""
    documentation: str = ""
    insert_text: str = ""
    priority: int = 0

class AutoCompleteEngine:
    """Kod tamamlama motoru"""
    
    def __init__(self):
        self.logger = logging.getLogger("AutoCompleteEngine")
        
        # Python anahtar kelimeleri
        self.keywords = set(keyword.kwlist)
        
        # Built-in fonksiyonlar
        self.builtins = set(dir(builtins))
        
        # Yaygın modüller
        self.common_modules = {
            'os', 'sys', 'json', 're', 'math', 'random', 'datetime',
            'pathlib', 'collections', 'itertools', 'functools',
            'typing', 'dataclasses', 'enum', 'abc', 'logging',
            'sqlite3', 'requests', 'numpy', 'pandas', 'matplotlib',
            'PyQt6', 'tkinter', 'flask', 'django'
        }
        
        # Snippet'ler
        self.snippets = self._load_default_snippets()
        
        # Cache
        self.import_cache: Dict[str, Set[str]] = {}
        self.class_cache: Dict[str, Set[str]] = {}
        self.function_cache: Dict[str, Set[str]] = {}
    
    def _load_default_snippets(self) -> Dict[str, CompletionItem]:
        """Varsayılan snippet'leri yükle"""
        snippets = {}
        
        # Temel yapılar
        snippets['if'] = CompletionItem(
            text='if',
            kind='snippet',
            detail='if statement',
            insert_text='if ${1:condition}:\n    ${2:pass}',
            priority=10
        )
        
        snippets['for'] = CompletionItem(
            text='for',
            kind='snippet', 
            detail='for loop',
            insert_text='for ${1:item} in ${2:iterable}:\n    ${3:pass}',
            priority=10
        )
        
        snippets['while'] = CompletionItem(
            text='while',
            kind='snippet',
            detail='while loop',
            insert_text='while ${1:condition}:\n    ${2:pass}',
            priority=10
        )
        
        snippets['def'] = CompletionItem(
            text='def',
            kind='snippet',
            detail='function definition',
            insert_text='def ${1:function_name}(${2:args}):\n    """${3:docstring}"""\n    ${4:pass}',
            priority=10
        )
        
        snippets['class'] = CompletionItem(
            text='class',
            kind='snippet',
            detail='class definition',
            insert_text='class ${1:ClassName}:\n    """${2:docstring}"""\n    \n    def __init__(self${3:, args}):\n        ${4:pass}',
            priority=10
        )
        
        snippets['try'] = CompletionItem(
            text='try',
            kind='snippet',
            detail='try-except block',
            insert_text='try:\n    ${1:code}\nexcept ${2:Exception} as e:\n    ${3:handle_exception}',
            priority=10
        )
        
        snippets['with'] = CompletionItem(
            text='with',
            kind='snippet',
            detail='with statement',
            insert_text='with ${1:expression} as ${2:variable}:\n    ${3:code}',
            priority=10
        )
        
        snippets['main'] = CompletionItem(
            text='main',
            kind='snippet',
            detail='main function',
            insert_text='if __name__ == "__main__":\n    ${1:main()}',
            priority=10
        )
        
        # Import'lar
        snippets['import'] = CompletionItem(
            text='import',
            kind='snippet',
            detail='import statement',
            insert_text='import ${1:module}',
            priority=8
        )
        
        snippets['from'] = CompletionItem(
            text='from',
            kind='snippet',
            detail='from import statement',
            insert_text='from ${1:module} import ${2:name}',
            priority=8
        )
        
        return snippets
    
    def get_completions(self, text: str, cursor_pos: int, file_content: str = "") -> List[CompletionItem]:
        """Tamamlama önerilerini al"""
        try:
            # Cursor pozisyonundaki kelimeyi bul
            word_start, word_end, current_word = self._get_current_word(text, cursor_pos)
            
            if not current_word:
                return []
            
            completions = []
            
            # Snippet'ler
            completions.extend(self._get_snippet_completions(current_word))
            
            # Anahtar kelimeler
            completions.extend(self._get_keyword_completions(current_word))
            
            # Built-in fonksiyonlar
            completions.extend(self._get_builtin_completions(current_word))
            
            # Modül önerileri
            completions.extend(self._get_module_completions(current_word))
            
            # Dosya içeriğinden çıkarılan öneriler
            if file_content:
                completions.extend(self._get_context_completions(current_word, file_content))
            
            # Sırala ve döndür
            completions.sort(key=lambda x: (-x.priority, x.text))
            
            return completions[:50]  # En fazla 50 öneri
            
        except Exception as e:
            self.logger.error(f"Error getting completions: {e}")
            return []
    
    def _get_current_word(self, text: str, cursor_pos: int) -> Tuple[int, int, str]:
        """Cursor pozisyonundaki kelimeyi bul"""
        if cursor_pos > len(text):
            cursor_pos = len(text)
        
        # Kelime karakterleri
        word_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        
        # Başlangıç pozisyonu
        start = cursor_pos
        while start > 0 and text[start - 1] in word_chars:
            start -= 1
        
        # Bitiş pozisyonu
        end = cursor_pos
        while end < len(text) and text[end] in word_chars:
            end += 1
        
        current_word = text[start:cursor_pos]
        
        return start, end, current_word
    
    def _get_snippet_completions(self, prefix: str) -> List[CompletionItem]:
        """Snippet tamamlamaları"""
        completions = []
        
        for trigger, snippet in self.snippets.items():
            if trigger.startswith(prefix.lower()):
                completions.append(snippet)
        
        return completions
    
    def _get_keyword_completions(self, prefix: str) -> List[CompletionItem]:
        """Anahtar kelime tamamlamaları"""
        completions = []
        
        for keyword_name in self.keywords:
            if keyword_name.startswith(prefix):
                completions.append(CompletionItem(
                    text=keyword_name,
                    kind='keyword',
                    detail='Python keyword',
                    priority=8
                ))
        
        return completions
    
    def _get_builtin_completions(self, prefix: str) -> List[CompletionItem]:
        """Built-in fonksiyon tamamlamaları"""
        completions = []
        
        for builtin_name in self.builtins:
            if builtin_name.startswith(prefix) and not builtin_name.startswith('_'):
                # Fonksiyon mu kontrol et
                try:
                    obj = getattr(builtins, builtin_name)
                    if callable(obj):
                        kind = 'function'
                        detail = 'built-in function'
                    else:
                        kind = 'variable'
                        detail = 'built-in variable'
                except:
                    kind = 'variable'
                    detail = 'built-in'
                
                completions.append(CompletionItem(
                    text=builtin_name,
                    kind=kind,
                    detail=detail,
                    priority=7
                ))
        
        return completions
    
    def _get_module_completions(self, prefix: str) -> List[CompletionItem]:
        """Modül tamamlamaları"""
        completions = []
        
        for module_name in self.common_modules:
            if module_name.startswith(prefix):
                completions.append(CompletionItem(
                    text=module_name,
                    kind='module',
                    detail='Python module',
                    priority=6
                ))
        
        return completions
    
    def _get_context_completions(self, prefix: str, file_content: str) -> List[CompletionItem]:
        """Dosya içeriğinden bağlamsal tamamlamalar"""
        completions = []
        
        # Fonksiyon tanımları
        function_pattern = r'def\s+(\w+)\s*\('
        for match in re.finditer(function_pattern, file_content):
            func_name = match.group(1)
            if func_name.startswith(prefix) and func_name != prefix:
                completions.append(CompletionItem(
                    text=func_name,
                    kind='function',
                    detail='function (local)',
                    priority=9
                ))
        
        # Sınıf tanımları
        class_pattern = r'class\s+(\w+)\s*[:\(]'
        for match in re.finditer(class_pattern, file_content):
            class_name = match.group(1)
            if class_name.startswith(prefix) and class_name != prefix:
                completions.append(CompletionItem(
                    text=class_name,
                    kind='class',
                    detail='class (local)',
                    priority=9
                ))
        
        # Değişken atamaları
        variable_pattern = r'(\w+)\s*='
        for match in re.finditer(variable_pattern, file_content):
            var_name = match.group(1)
            if (var_name.startswith(prefix) and 
                var_name != prefix and 
                not var_name in self.keywords):
                completions.append(CompletionItem(
                    text=var_name,
                    kind='variable',
                    detail='variable (local)',
                    priority=5
                ))
        
        # Import'lar
        import_pattern = r'(?:from\s+\w+\s+)?import\s+([^,\n]+)'
        for match in re.finditer(import_pattern, file_content):
            imports = match.group(1).split(',')
            for imp in imports:
                imp_name = imp.strip().split(' as ')[0].strip()
                if imp_name.startswith(prefix) and imp_name != prefix:
                    completions.append(CompletionItem(
                        text=imp_name,
                        kind='module',
                        detail='imported module',
                        priority=8
                    ))
        
        return completions
    
    def get_function_signature(self, function_name: str, file_content: str = "") -> Optional[str]:
        """Fonksiyon imzasını al"""
        try:
            # Built-in fonksiyon kontrolü
            if hasattr(builtins, function_name):
                obj = getattr(builtins, function_name)
                if callable(obj):
                    return f"{function_name}(...)"
            
            # Dosya içeriğinde ara
            if file_content:
                pattern = rf'def\s+{re.escape(function_name)}\s*\(([^)]*)\)'
                match = re.search(pattern, file_content)
                if match:
                    params = match.group(1)
                    return f"{function_name}({params})"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting function signature: {e}")
            return None
    
    def get_hover_info(self, word: str, file_content: str = "") -> Optional[str]:
        """Hover bilgisi al"""
        try:
            # Built-in kontrolü
            if hasattr(builtins, word):
                obj = getattr(builtins, word)
                doc = getattr(obj, '__doc__', None)
                if doc:
                    return f"**{word}** (built-in)\n\n{doc[:200]}..."
            
            # Dosya içeriğinde fonksiyon/sınıf ara
            if file_content:
                # Fonksiyon
                func_pattern = rf'def\s+{re.escape(word)}\s*\([^)]*\):\s*"""([^"]+)"""'
                match = re.search(func_pattern, file_content, re.DOTALL)
                if match:
                    docstring = match.group(1).strip()
                    return f"**{word}** (function)\n\n{docstring}"
                
                # Sınıf
                class_pattern = rf'class\s+{re.escape(word)}\s*[:\(][^:]*:\s*"""([^"]+)"""'
                match = re.search(class_pattern, file_content, re.DOTALL)
                if match:
                    docstring = match.group(1).strip()
                    return f"**{word}** (class)\n\n{docstring}"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting hover info: {e}")
            return None
    
    def add_custom_completion(self, item: CompletionItem):
        """Özel tamamlama ekle"""
        if item.kind == 'snippet':
            self.snippets[item.text] = item
    
    def clear_cache(self):
        """Cache'i temizle"""
        self.import_cache.clear()
        self.class_cache.clear()
        self.function_cache.clear() 