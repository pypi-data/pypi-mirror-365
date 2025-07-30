# Universal App - clapp Örnek Uygulaması

Bu uygulama, clapp'in evrensel dil desteği örneğidir.

## 🚀 Özellikler

- Herhangi bir programlama dilini destekler
- Otomatik dil tespiti
- Dosya uzantısına göre çalıştırma
- Shebang desteği

## 📦 Kurulum

```bash
# Uygulamayı yükle
clapp install ./hello-universal

# Uygulamayı çalıştır
clapp run hello-universal
```

## 🧪 Test

```bash
# Uygulamayı doğrula
clapp validate ./hello-universal

# Bağımlılıkları kontrol et
clapp dependency check hello-universal
```

## 📁 Dosya Yapısı

```
hello-universal/
├── manifest.json    # Uygulama manifesti (language: "universal")
├── main.c          # Herhangi bir dilde dosya
└── README.md       # Bu dosya
```

## 🔧 Desteklenen Diller

Evrensel runner şu dilleri otomatik tespit eder:

- **Python** (.py)
- **JavaScript** (.js)
- **TypeScript** (.ts)
- **Lua** (.lua)
- **Dart** (.dart)
- **Go** (.go)
- **Rust** (.rs)
- **Java** (.java)
- **C/C++** (.c, .cpp)
- **C#** (.cs)
- **PHP** (.php)
- **Ruby** (.rb)
- **Perl** (.pl)
- **Bash** (.sh)
- **PowerShell** (.ps1)
- **R** (.r)
- **Swift** (.swift)
- **Kotlin** (.kt)
- **Scala** (.scala)
- **Clojure** (.clj)
- **Haskell** (.hs)
- **OCaml** (.ml)
- **Fortran** (.f90)
- **Pascal** (.pas)
- **Basic** (.bas)
- **VBScript** (.vbs)
- **Batch** (.bat)
- **Executable** (.exe)
- **macOS App** (.app)
- **Java JAR** (.jar)
- **Java Class** (.class)

## 📝 Lisans

MIT License 