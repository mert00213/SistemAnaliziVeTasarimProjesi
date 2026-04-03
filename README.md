# 🍎 Sepet Oyunu (Catching Game) 💣

Python ve Pygame kütüphanesi kullanılarak geliştirilmiş, 2D nesne yakalama (arcade) oyunu. Bu proje, **Nesne Yönelimli Programlama (OOP)** prensiplerine uygun, modüler ve genişletilebilir bir mimari ile tasarlanmıştır.

## 🎮 Oyunun Amacı
Oyuncunun temel amacı, ekranın üst kısmından rastgele düşen elmaları (+) toplayarak skor elde etmek ve bombalardan (-) kaçarak hayatta kalmaktır. Oyun, skor arttıkça dinamik olarak zorlaşmaktadır.

## ✨ Temel Özellikler
* **Temiz ve Modüler Mimari (OOP):** Proje; `GameManager`, `Basket`, `GoodItem` ve `BadItem` gibi birbirinden bağımsız ancak birbiriyle haberleşen sınıflardan (class) oluşmaktadır.
* **Dinamik Zorluk Seviyesi:** Skor yükseldikçe nesnelerin düşme hızı kademeli olarak artar, bu da oyunun tekdüze olmasını engeller.
* **Veri Kalıcılığı (Data Persistence):** Ulaşılan en yüksek skor yerel bir `skor.txt` dosyasına kaydedilir. Oyun kapatılıp açılsa dahi en yüksek skor hafızada tutulur.
* **Durum Yönetimi (State Machine):** Başlangıç menüsü, oyun döngüsü ve oyun sonu ekranları arasında akıcı geçişler sağlanmıştır.

## 🛠️ Kullanılan Teknolojiler
* **Programlama Dili:** Python 3.x
* **Oyun Motoru:** Pygame (Pygame-CE)
* **Geliştirme Ortamı:** Visual Studio Code

## 🚀 Kurulum ve Çalıştırma

Oyunu kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1.  **Python Kurulumu:** Bilgisayarınızda Python'un yüklü olduğundan emin olun (Yüklerken *Add to PATH* seçeneğinin işaretli olduğundan emin olun).
2.  **Depoyu Klonlayın veya İndirin:**
    ```bash
    git clone [https://github.com/KULLANICI_ADIN/sepet_oyunu.git](https://github.com/KULLANICI_ADIN/sepet_oyunu.git)
    cd sepet_oyunu
    ```
3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install pygame-ce
    ```
4.  **Oyunu Başlatın:**
    ```bash
    python sepet_oyunu.py
    ```
    *(Not: Bazı sistemlerde `python` yerine `py` komutunu kullanmanız gerekebilir.)*

## 🕹️ Kontroller
* **Sol Ok (←) / A Tuşu:** Sepeti sola hareket ettirir.
* **Sağ Ok (→) / D Tuşu:** Sepeti sağa hareket ettirir.
* **Enter:** Menülerde oyunu başlatır veya yeniden başlatır.

## 📂 Sınıf (Class) Yapısı Özeti
* `GameManager`: Oyunun ana döngüsünü, FPS ayarlarını, ekran çizimlerini ve skor kayıt işlemlerini yönetir.
* `Basket`: Oyuncunun kontrol ettiği karakter sınıfıdır.
* `FallingItem`: Yukarıdan düşen nesnelerin miras aldığı (inheritance) temel sınıftır. Hız ve koordinat özelliklerini barındırır.
* `GoodItem` / `BadItem`: `FallingItem` sınıfından türerler. Çarpışma anında skoru artırmak veya can azaltmak gibi spesifik davranışlara sahiptirler.

## 🗺️ Gelecek Güncellemeler (Yol Haritası)
- [ ] Pygame çizimleri yerine özel .png görsellerin (assets/images) entegre edilmesi.
- [ ] Arka plan müziği ve ses efektlerinin (assets/sounds) eklenmesi.
- [ ] SQLite kullanılarak Gelişmiş Liderlik Tablosu (Leaderboard) sistemine geçilmesi.
- [ ] PyInstaller ile .exe sürümünün derlenip dağıtıma sunulması.

---
*Geliştirici: [Mert İlhan Dündar]*