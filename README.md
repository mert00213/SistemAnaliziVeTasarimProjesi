# 🍎 Sepet Oyunu (Catching Game) 💣

Python ve Pygame kütüphanesi kullanılarak geliştirilmiş, 2D nesne yakalama (arcade) oyunu. Bu proje, **Nesne Yönelimli Programlama (OOP)** prensiplerine uygun, modüler ve genişletilebilir bir mimari ile tasarlanmıştır.

## 🎮 Oyunun Amacı
Oyuncunun temel amacı, ekranın üst kısmından rastgele düşen elmaları (+) toplayarak skor elde etmek ve bombalardan (-) kaçarak hayatta kalmaktır. Oyun, skor arttıkça dinamik olarak zorlaşmaktadır.

## ✨ Detaylı Oyun Özellikleri ve Mekanikleri

Oyun, klasik bir yakalama oyununun çok ötesine geçerek gelişmiş mekanikler sunar:

### 🌍 Bölgeler (Biomes) ve Etkileri
Oyun ilerledikçe her 2000 puanda bir bölge değişir ve fizik kuralları bu bölgeye göre yeniden şekillenir:
* **🌲 Orman (Seviye 1):** Normal yerçekimi (1.0x). Başlangıç için idealdir.
* **🏜️ Çöl (Seviye 2):** Yüksek yerçekimi (1.15x). Nesneler daha hızlı düşer, tepki süreniz azalır.
* **❄️ Buz (Seviye 3):** Düşük yerçekimi (0.95x). Ancak **zemin kaygandır!** Sepeti hareket ettirdiğinizde anında duramazsınız, sepet kaymaya devam eder.
* **🌌 Uzay (Seviye 4):** Çok düşük yerçekimi (0.60x). Nesneler adeta süzülerek düşer.

### 🌦️ Dinamik Hava Durumu
* **Rüzgar:** Rüzgar rastgele yönlere eserek düşen nesnelerin (elma, bomba) yatayda kaymasına neden olur. Sepetinizin konumunu rüzgara göre ayarlamanız gerekir.
* **Yağmur:** Yağmurlu havalarda (Buz bölgesinde olmasanız bile) zemin kayganlaşır ve kontrol zorlaşır.
* **Gece/Gündüz Döngüsü:** Her 1000 puanda bir hava kararır. Gece olduğunda ekran kararır ve sadece sepetinizin etrafını görebilirsiniz, ancak düşen nesnelerin parlak haleleri onlara yerlerini belli eder.

### 🔥 Kombo ve Fever (Öfke) Modu
* Peş peşe elma topladıkça kombo sayacınız artar. Kombo büyüdükçe kazandığınız puanlar (x2, x3... x10) katlanır.
* Bir bomba yerseniz veya bir elma kaçırırsanız kombonuz sıfırlanır.
* Kombo barı tamamen dolduğunda **Fever Modu** başlar. Bu modda sadece çok değerli **Altın Elmalar** düşer ve arka plan renklenir.

### 💀 Boss Savaşları
* Skorunuz **5000**'e ulaştığında devasa bir Boss ortaya çıkar!
* Boss, tepeden size doğru bombalar fırlatır. Boss'u yenebilmek için ondan düşen **Mermileri** yakalamanız gerekir. Yakaladığınız her mermi Boss'a hasar verir.

### 🦅 Hırsız Kuşlar
* İlerleyen seviyelerde ekranın yanlarından Hırsız Kuşlar uçar. Bu kuşlar, havada düşen değerli elmalara çarpıp onları sizden önce çalabilirler!

### 🛒 Market ve ⚡ Yetenek Ağacı
* Oyun sonunda kazandığınız puanlar bakiyenize eklenir.
* **Market:** Bakiyenizle sepetinize yeni renkler ve görünümler satın alabilirsiniz.
* **Yetenekler:** Kazandığınız puanlarla sepetinizin *hızını* artırabilir, *maksimum can* kapasitenizi yükseltebilirsiniz.

### 🏆 Görevler (Achievements) ve Veritabanı
* *50 Elma Topla*, *Hiç Hasar Almadan 1000 Puan Yap* gibi görevleri tamamlayarak ekstra ödüller kazanırsınız.
* Bütün ilerlemeniz (skorlar, bakiyeler, yetenekler) yerel **SQLite** veritabanına otomatik kaydedilir.

### ▶️ Ölüm ve Replay (Tekrar İzleme) Modu
* Oyun içinde yaptığınız her hareket, her düşen elma ve bomba saniye saniye kaydedilir.
* Eğer canınız biter ve oyunu kaybederseniz, bitiş ekranındaki **"Tekrar İzle"** butonuna basarak tüm oyununuzu baştan sona bir video gibi tekrar izleyebilir, nerede hata yaptığınızı analiz edebilirsiniz!
* Ayrıca en iyi skorunuza ait oynanışınız kaydedilir ve veritabanında saklanır.

## 🛠️ Kullanılan Teknolojiler
* **Programlama Dili:** Python 3.x
* **Oyun Motoru:** Pygame
* **Veritabanı:** SQLite3
* **Geliştirme Ortamı:** Visual Studio Code

## 🚀 Kurulum ve Çalıştırma

Oyunu kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1.  **Python Kurulumu:** Bilgisayarınızda Python'un yüklü olduğundan emin olun (Yüklerken *Add to PATH* seçeneğinin işaretli olduğundan emin olun).
2.  **Depoyu Klonlayın veya İndirin:**
    ```bash
    git clone https://github.com/mert00213/SistemAnaliziVeTasarimProjesi.git
    cd SistemAnaliziVeTasarimProjesi
    ```
3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Oyunu Başlatın:**
    ```bash
    python main.py
    ```
    *(Not: Bazı sistemlerde `python` yerine `py` komutunu kullanmanız gerekebilir.)*

## 🕹️ Kontroller
* **Sol Ok (←) / A Tuşu:** Sepeti sola hareket ettirir.
* **Sağ Ok (→) / D Tuşu:** Sepeti sağa hareket ettirir.
* **M Tuşu:** Menüde Market'i açar.
* **U Tuşu:** Menüde Yetenekler'i açar.
* **R Tuşu:** Oyun bitişinde tekrar (replay) izlemeyi başlatır.
* **Enter:** Menülerde oyunu başlatır veya yeniden başlatır.
* **ESC:** Menüye dönmeyi veya oyundan çıkmayı sağlar.

## 📂 Dosya ve Sınıf Yapısı
* `main.py`: Oyunun giriş noktasıdır.
* `settings.py`: Oyun içi ayarlar, sabitler ve renklerin tutulduğu yer.
* `database.py`: SQLite bağlantıları ve işlemlerini yönetir.
* `resource_path.py`: Pyinstaller vb. EXE dönüştürmeleri için doğru dosya yollarını sağlar.
* `managers/`:
  * `game_manager.py`: Oyunun ana döngüsü (GameManager).
  * `renderer.py`: Oyun içi görsel çizim işlemleri.
  * `state_handlers.py`: Menü, oyun sonu vb. state arayüzleri.
* `entities/`: Basket, FallingItem, Boss gibi oyun nesneleri bulunur.
* `systems/`: Zorluk, efektler, particle sistemleri ve API işlemleri yer alır.

---
*Geliştirici: [Mert İlhan Dündar]*