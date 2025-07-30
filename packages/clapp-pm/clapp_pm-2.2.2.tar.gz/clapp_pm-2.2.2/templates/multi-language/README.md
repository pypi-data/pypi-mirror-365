# Multi-Language App - clapp Örnek Uygulaması

Bu uygulama, clapp için çoklu dil desteği olan uygulama geliştirme örneğidir.

## 🚀 Özellikler

- Çoklu dil desteği (Python, Node.js, Rust)
- Modüler yapı
- Bağımlılık yönetimi
- Sıralı çalıştırma

## 📦 Kurulum

```bash
# Uygulamayı yükle
clapp install ./multi-language-app

# Uygulamayı çalıştır
clapp run multi-language-app
```

## 🧪 Test

```bash
# Uygulamayı doğrula
clapp validate ./multi-language-app

# Bağımlılıkları kontrol et
clapp dependency check multi-language-app
```

## 📁 Dosya Yapısı

```
multi-language-app/
├── manifest.json          # Çoklu dil manifesti
├── main.py               # Python backend
├── frontend/
│   └── app.js           # Node.js frontend
├── backend/
│   └── main.rs          # Rust microservice
└── README.md            # Bu dosya
```

## 🔧 Manifest Formatı

```json
{
    "name": "app-name",
    "language": "multi",
    "languages": {
        "python": {
            "entry": "main.py",
            "dependencies": ["requests"]
        },
        "javascript": {
            "entry": "frontend/app.js",
            "dependencies": ["express"]
        }
    },
    "run_order": ["python", "javascript"]
}
```

## 📝 Lisans

MIT License 