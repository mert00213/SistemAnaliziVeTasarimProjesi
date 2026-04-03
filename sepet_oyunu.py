# =============================================================================
# SEPET OYUNU (Catching Game) - Pygame ile 2D Oyun
# =============================================================================
# Kurulum ve Çalıştırma (VS Code terminali):
#   pip install pygame
#   python sepet_oyunu.py
# =============================================================================

import pygame
import random
import sys
import os
import math
import sqlite3

# --- Pygame başlatma ---
pygame.init()
pygame.mixer.init()

# =============================================================================
# SABITLER
# =============================================================================
EKRAN_GENISLIK = 800
EKRAN_YUKSEKLIK = 600
FPS = 60

# Renkler
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
KIRMIZI = (220, 40, 40)
YESIL = (50, 180, 50)
MAVI = (40, 100, 220)
SARI = (255, 220, 0)
TURUNCU = (255, 140, 0)
GRI = (180, 180, 180)
KOYU_GRI = (60, 60, 60)
ACIK_MAVI = (135, 206, 235)
KAHVERENGI = (139, 90, 43)
KOYU_YESIL = (34, 120, 34)
PEMBE = (255, 105, 180)
ALTIN = (255, 215, 0)
ACIK_YESIL = (0, 255, 127)

# Dosya yolları
OYUN_KLASORU = os.path.dirname(os.path.abspath(__file__))
SKOR_DOSYASI = os.path.join(OYUN_KLASORU, "skor.txt")
VERITABANI_YOLU = os.path.join(OYUN_KLASORU, "skorlar.db")
MAKS_CAN = 3


# =============================================================================
# SINIF: Particle (Parçacık Efekti)
# =============================================================================
class Particle:
    """Çarpışma efektleri için küçük renkli kare parçacık."""

    def __init__(self, x, y, renk):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, -1)
        self.boyut = random.randint(3, 7)
        self.renk = renk
        self.omur = random.randint(30, 60)  # 0.5 - 1 saniye (60 FPS'de)
        self.max_omur = self.omur
        self.aktif = True

    def guncelle(self):
        """Parçacığı hareket ettirir ve ömrünü azaltır."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # Yerçekimi
        self.omur -= 1
        if self.omur <= 0:
            self.aktif = False

    def ciz(self, ekran):
        """Parçacığı solarak çizer."""
        if not self.aktif:
            return
        alpha = int(255 * (self.omur / self.max_omur))
        boyut = max(1, int(self.boyut * (self.omur / self.max_omur)))
        surf = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        surf.fill((*self.renk[:3], alpha))
        ekran.blit(surf, (int(self.x), int(self.y)))


# =============================================================================
# SINIF: ParticleManager (Parçacık Yöneticisi)
# =============================================================================
class ParticleManager:
    """Tüm parçacıkları yöneten sınıf."""

    def __init__(self):
        self.parcaciklar = []

    def patlama_ekle(self, x, y, renk, adet=15):
        """Belirtilen noktada parçacık patlaması oluşturur."""
        for _ in range(adet):
            self.parcaciklar.append(Particle(x, y, renk))

    def guncelle(self):
        """Tüm parçacıkları günceller ve ölüleri temizler."""
        for p in self.parcaciklar:
            p.guncelle()
        self.parcaciklar = [p for p in self.parcaciklar if p.aktif]

    def ciz(self, ekran):
        """Tüm parçacıkları çizer."""
        for p in self.parcaciklar:
            p.ciz(ekran)


# =============================================================================
# SINIF: FallingItem (Düşen Nesnelerin Temel Sınıfı)
# =============================================================================
class FallingItem:
    """
    Düşen tüm nesnelerin miras alacağı temel (base) sınıf.
    Konum, boyut, hız ve çizim gibi ortak özellikleri barındırır.
    """

    def __init__(self, x, y, genislik, yukseklik, hiz, renk):
        self.x = x
        self.y = y
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.hiz = hiz
        self.renk = renk
        self.aktif = True  # Nesne ekranda mı?

    def guncelle(self):
        """Nesneyi her karede aşağı doğru hareket ettirir."""
        self.y += self.hiz
        # Ekranın altına ulaştıysa pasif yap
        if self.y > EKRAN_YUKSEKLIK:
            self.aktif = False

    def ciz(self, ekran):
        """Temel çizim metodu - alt sınıflar bunu override eder."""
        pygame.draw.rect(ekran, self.renk, (self.x, self.y, self.genislik, self.yukseklik))

    def dikdortgen_al(self):
        """Çarpışma tespiti için Rect nesnesi döndürür."""
        return pygame.Rect(self.x, self.y, self.genislik, self.yukseklik)


# =============================================================================
# SINIF: GoodItem (İyi Nesne - Elma)
# =============================================================================
class GoodItem(FallingItem):
    """
    Toplandığında oyuncuya puan kazandıran nesne.
    Şekil olarak kırmızı bir elma çizilir.
    """

    def __init__(self, x, hiz, gorsel=None):
        # Elma boyutları
        super().__init__(x, -40, 34, 34, hiz, KIRMIZI)
        self.puan = 10  # Her elma 10 puan
        self.gorsel = gorsel

    def ciz(self, ekran):
        """Elma görselini veya geometrik şeklini ekrana çizer."""
        if self.gorsel:
            ekran.blit(self.gorsel, (self.x, self.y))
            return

        # Fallback: geometrik çizim
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        # Elma gövdesi (kırmızı daire)
        pygame.draw.circle(ekran, KIRMIZI, (merkez_x, merkez_y + 2), yaricap)
        # Parlaklık efekti
        pygame.draw.circle(ekran, (255, 100, 100), (merkez_x - 5, merkez_y - 4), yaricap // 3)
        # Sap (kahverengi çizgi)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 3, merkez_y - yaricap - 8), 3)
        # Yaprak (küçük yeşil elips)
        yaprak_rect = pygame.Rect(merkez_x + 2, merkez_y - yaricap - 10, 10, 6)
        pygame.draw.ellipse(ekran, KOYU_YESIL, yaprak_rect)


# =============================================================================
# SINIF: BadItem (Kötü Nesne - Bomba)
# =============================================================================
class BadItem(FallingItem):
    """
    Sepete çarptığında oyuncunun canını azaltan nesne.
    Şekil olarak siyah bir bomba çizilir.
    """

    def __init__(self, x, hiz, gorsel=None):
        super().__init__(x, -40, 34, 34, hiz, SIYAH)
        self.gorsel = gorsel

    def ciz(self, ekran):
        """Bomba görselini veya geometrik şeklini ekrana çizer."""
        if self.gorsel:
            ekran.blit(self.gorsel, (self.x, self.y))
            return

        # Fallback: geometrik çizim
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        # Bomba gövdesi (koyu gri / siyah daire)
        pygame.draw.circle(ekran, KOYU_GRI, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, SIYAH, (merkez_x, merkez_y + 2), yaricap - 3)
        # Parlaklık efekti
        pygame.draw.circle(ekran, (80, 80, 80), (merkez_x - 5, merkez_y - 3), yaricap // 4)
        # Fitil (üstte kısa çizgi)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 4, merkez_y - yaricap - 10), 3)
        # Kıvılcım (fitil ucunda turuncu/sarı nokta)
        pygame.draw.circle(ekran, TURUNCU, (merkez_x + 4, merkez_y - yaricap - 12), 4)
        pygame.draw.circle(ekran, SARI, (merkez_x + 4, merkez_y - yaricap - 12), 2)


# =============================================================================
# SINIF: GoldenItem (Altın Elma - Çok Değerli)
# =============================================================================
class GoldenItem(FallingItem):
    """
    Nadir düşen, hızlı hareket eden altın elma.
    Yakalanınca 100 puan kazandırır.
    """

    def __init__(self, x, hiz):
        super().__init__(x, -40, 34, 34, hiz * 1.8, ALTIN)
        self.puan = 100
        self._parlama_sayac = 0

    def guncelle(self):
        """Altın elmayı hareket ettirir ve parlama sayacını artırır."""
        super().guncelle()
        self._parlama_sayac += 1

    def ciz(self, ekran):
        """Altın elma - parlayan altın rengi ile çizer."""
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        # Parlama efekti (yanıp sönen dış halka)
        parlama = abs(math.sin(self._parlama_sayac * 0.1)) * 4
        pygame.draw.circle(ekran, (255, 255, 150),
                           (merkez_x, merkez_y + 2), int(yaricap + parlama))
        # Altın gövde
        pygame.draw.circle(ekran, ALTIN, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, (255, 240, 100), (merkez_x - 4, merkez_y - 3), yaricap // 3)
        # Sap
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 3, merkez_y - yaricap - 8), 3)
        # Yıldız işareti
        yildiz_font = pygame.font.SysFont("Arial", 14, bold=True)
        yildiz = yildiz_font.render("★", True, BEYAZ)
        ekran.blit(yildiz, (merkez_x - 6, merkez_y - 8))


# =============================================================================
# SINIF: HealItem (Can Paketi)
# =============================================================================
class HealItem(FallingItem):
    """
    Çok nadir düşen can paketi.
    Yakalanınca mevcut canı +1 artırır (maksimum MAKS_CAN).
    """

    def __init__(self, x, hiz):
        super().__init__(x, -40, 30, 30, hiz * 0.8, ACIK_YESIL)
        self._parlama_sayac = 0

    def guncelle(self):
        """Can paketini hareket ettirir ve parlama sayacını artırır."""
        super().guncelle()
        self._parlama_sayac += 1

    def ciz(self, ekran):
        """Yeşil artı (+) şeklinde can paketi çizer."""
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2

        # Dış parlama
        parlama = abs(math.sin(self._parlama_sayac * 0.08)) * 3
        pygame.draw.circle(ekran, (150, 255, 200),
                           (merkez_x, merkez_y), int(self.genislik // 2 + parlama))
        # Beyaz daire zemin
        pygame.draw.circle(ekran, BEYAZ, (merkez_x, merkez_y), self.genislik // 2)
        pygame.draw.circle(ekran, ACIK_YESIL, (merkez_x, merkez_y), self.genislik // 2, 2)

        # Yeşil artı işareti
        kalinlik = 6
        pygame.draw.rect(ekran, YESIL,
                         (merkez_x - kalinlik // 2, merkez_y - 8, kalinlik, 16))
        pygame.draw.rect(ekran, YESIL,
                         (merkez_x - 8, merkez_y - kalinlik // 2, 16, kalinlik))


# =============================================================================
# SINIF: Basket (Sepet - Oyuncunun Kontrol Ettiği Nesne)
# =============================================================================
class Basket:
    """
    Oyuncunun klavye ile sağa-sola hareket ettirdiği sepet nesnesi.
    Ok tuşları veya A/D tuşlarıyla kontrol edilir.
    """

    def __init__(self, gorsel=None):
        self.genislik = 100
        self.yukseklik = 50
        self.x = EKRAN_GENISLIK // 2 - self.genislik // 2
        self.y = EKRAN_YUKSEKLIK - 70
        self.hiz = 8
        self.renk = KAHVERENGI
        self.gorsel = gorsel

    def hareket_et(self, tuslar):
        """Basılan tuşlara göre sepeti sağa veya sola hareket ettirir."""
        if (tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]) and self.x > 0:
            self.x -= self.hiz
        if (tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]) and self.x < EKRAN_GENISLIK - self.genislik:
            self.x += self.hiz

    def ciz(self, ekran):
        """Sepet görselini veya geometrik şeklini ekrana çizer."""
        if self.gorsel:
            ekran.blit(self.gorsel, (self.x, self.y))
            return

        # Fallback: geometrik çizim
        # Sepet gövdesi (ana dikdörtgen)
        govde = pygame.Rect(self.x, self.y + 10, self.genislik, self.yukseklik - 10)
        pygame.draw.rect(ekran, KAHVERENGI, govde, border_radius=6)

        # Sepet iç kısmı (daha açık renk)
        ic = pygame.Rect(self.x + 5, self.y + 14, self.genislik - 10, self.yukseklik - 20)
        pygame.draw.rect(ekran, (180, 120, 60), ic, border_radius=4)

        # Sepet ağzı (üstte geniş trapez efekti - iki yan üçgen)
        sol_nokta = (self.x - 8, self.y + 10)
        sol_alt = (self.x, self.y + 10)
        sol_ust = (self.x + 8, self.y)
        pygame.draw.polygon(ekran, KAHVERENGI, [sol_nokta, sol_alt, sol_ust])

        sag_nokta = (self.x + self.genislik + 8, self.y + 10)
        sag_alt = (self.x + self.genislik, self.y + 10)
        sag_ust = (self.x + self.genislik - 8, self.y)
        pygame.draw.polygon(ekran, KAHVERENGI, [sag_nokta, sag_alt, sag_ust])

        # Üst kenar çizgisi
        pygame.draw.line(ekran, (100, 60, 20),
                         (self.x - 8, self.y + 10),
                         (self.x + self.genislik + 8, self.y + 10), 3)

        # Yatay örgü çizgileri
        for i in range(1, 3):
            y_cizgi = self.y + 10 + i * (self.yukseklik - 10) // 3
            pygame.draw.line(ekran, (100, 60, 20),
                             (self.x + 2, y_cizgi),
                             (self.x + self.genislik - 2, y_cizgi), 1)

    def dikdortgen_al(self):
        """Çarpışma tespiti için Rect nesnesi döndürür."""
        return pygame.Rect(self.x, self.y, self.genislik, self.yukseklik)


# =============================================================================
# SINIF: SkorVeritabani (SQLite Veritabanı Yöneticisi)
# =============================================================================
class SkorVeritabani:
    """SQLite ile skor verilerini yöneten sınıf."""

    def __init__(self, db_yolu):
        self.db_yolu = db_yolu
        self._tablo_olustur()

    def _tablo_olustur(self):
        """Skor tablosunu oluşturur (yoksa)."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS skorlar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        isim TEXT NOT NULL,
                        skor INTEGER NOT NULL,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Veritabanı tablosu oluşturulamadı: {e}")

    def skor_ekle(self, isim, skor):
        """Yeni bir skor kaydı ekler."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT INTO skorlar (isim, skor) VALUES (?, ?)",
                    (isim, skor)
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Skor kaydedilemedi: {e}")

    def en_iyi_5_al(self):
        """En yüksek 5 skoru döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT isim, skor FROM skorlar ORDER BY skor DESC LIMIT 5"
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[UYARI] Skorlar okunamadı: {e}")
            return []

    def ilk_5e_girer_mi(self, skor):
        """Verilen skorun ilk 5'e girip girmediğini kontrol eder."""
        if skor <= 0:
            return False
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT COUNT(*) FROM skorlar WHERE skor >= ?",
                    (skor,)
                )
                return cursor.fetchone()[0] < 5
        except sqlite3.Error as e:
            print(f"[UYARI] Skor kontrolü yapılamadı: {e}")
            return False

    def en_yuksek_skor(self):
        """En yüksek skoru döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute("SELECT MAX(skor) FROM skorlar")
                sonuc = cursor.fetchone()[0]
                return sonuc if sonuc else 0
        except sqlite3.Error as e:
            print(f"[UYARI] En yüksek skor okunamadı: {e}")
            return 0


# =============================================================================
# SINIF: GameManager (Oyun Yöneticisi)
# =============================================================================
class GameManager:
    """
    Oyunun ana yönetici sınıfı.
    Oyun döngüsü, skor takibi, ekran yönetimi, nesne üretimi
    ve çarpışma tespiti bu sınıf tarafından yönetilir.
    """

    def __init__(self):
        # Ekran ve saat ayarları
        self.ekran = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        pygame.display.set_caption("🍎 Sepet Oyunu - Catching Game")
        self.saat = pygame.time.Clock()

        # Fontlar
        self.baslik_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.buyuk_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.orta_font = pygame.font.SysFont("Arial", 26)
        self.kucuk_font = pygame.font.SysFont("Arial", 20)

        # --- Arka plan müziği ---
        try:
            ses_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds")
            pygame.mixer.music.load(os.path.join(ses_klasoru, "arkaplan.mp3"))
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[UYARI] Arka plan müziği yüklenemedi: {e}")

        # --- Ses efektleri ---
        self.bomba_ses = None
        try:
            self.bomba_ses = pygame.mixer.Sound(os.path.join(ses_klasoru, "bomba.mp3"))
        except Exception as e:
            print(f"[UYARI] Bomba ses efekti yüklenemedi: {e}")

        # --- Görsel varlıkları yükleme ---
        self.sepet_img = None
        self.elma_img = None
        self.bomba_img = None
        self.kalp_img = None
        try:
            gorsel_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds", "images")

            sepet_yol = os.path.join(gorsel_klasoru, "sepet.png")
            elma_yol = os.path.join(gorsel_klasoru, "elma.png")
            bomba_yol = os.path.join(gorsel_klasoru, "bomba.png")
            kalp_yol = os.path.join(gorsel_klasoru, "kalp.png")

            if os.path.exists(sepet_yol):
                self.sepet_img = pygame.transform.scale(
                    pygame.image.load(sepet_yol).convert_alpha(), (100, 50)
                )
            else:
                print(f"[UYARI] Sepet görseli bulunamadı: {sepet_yol}")

            if os.path.exists(elma_yol):
                self.elma_img = pygame.transform.scale(
                    pygame.image.load(elma_yol).convert_alpha(), (34, 34)
                )
            else:
                print(f"[UYARI] Elma görseli bulunamadı: {elma_yol}")

            if os.path.exists(bomba_yol):
                self.bomba_img = pygame.transform.scale(
                    pygame.image.load(bomba_yol).convert_alpha(), (34, 34)
                )
            else:
                print(f"[UYARI] Bomba görseli bulunamadı: {bomba_yol}")

            if os.path.exists(kalp_yol):
                self.kalp_img = pygame.transform.scale(
                    pygame.image.load(kalp_yol).convert_alpha(), (28, 28)
                )
            else:
                print(f"[UYARI] Kalp görseli bulunamadı: {kalp_yol}")

        except Exception as e:
            print(f"[UYARI] Görseller yüklenirken hata oluştu: {e}")
            print("[BİLGİ] Oyun geometrik çizimlerle devam edecek.")
            self.sepet_img = None
            self.elma_img = None
            self.bomba_img = None
            self.kalp_img = None

        # --- Veritabanı ---
        self.veritabani = SkorVeritabani(VERITABANI_YOLU)

        # Oyun durumu: "menu", "oyun", "isim_gir", "bitti"
        self.durum = "menu"
        self.en_yuksek_skor = self.veritabani.en_yuksek_skor()

        # İsim girişi için değişkenler
        self.oyuncu_ismi = ""
        self.isim_imlec_gorunsun = True
        self.isim_imlec_zamanlayici = 0

        # Parçacık yöneticisi
        self.parcacik_yonetici = ParticleManager()

        # Arka plan yıldızları (dekoratif)
        self.yildizlar = [(random.randint(0, EKRAN_GENISLIK),
                           random.randint(0, EKRAN_YUKSEKLIK // 2),
                           random.randint(1, 3)) for _ in range(40)]

        self._oyunu_sifirla()

    # -------------------------------------------------------------------------
    # Oyun Durumu Yönetimi
    # -------------------------------------------------------------------------
    def _oyunu_sifirla(self):
        """Oyunu başlangıç durumuna sıfırlar."""
        self.sepet = Basket(gorsel=self.sepet_img)
        self.dusen_nesneler = []
        self.skor = 0
        self.can = MAKS_CAN
        self.nesne_zamanlayici = 0
        self.nesne_bekleme = 50
        self.temel_hiz = 3.0
        self.zorluk_seviyesi = 1
        self.toplam_kare = 0
        self.son_skor = 0
        self.parcacik_yonetici = ParticleManager()
        self.oyuncu_ismi = ""

    # -------------------------------------------------------------------------
    # Nesne Üretimi
    # -------------------------------------------------------------------------
    def _nesne_uret(self):
        """
        Zamanlayıcıya göre yeni düşen nesne üretir.
        %68 elma, %25 bomba, %5 altın elma, %2 can paketi.
        """
        self.nesne_zamanlayici += 1
        if self.nesne_zamanlayici >= self.nesne_bekleme:
            self.nesne_zamanlayici = 0

            # Rastgele X konumu (nesne ekran sınırları içinde kalacak şekilde)
            x = random.randint(20, EKRAN_GENISLIK - 54)

            # Mevcut düşme hızı (zorluk seviyesiyle artar)
            hiz = self.temel_hiz + (self.zorluk_seviyesi - 1) * 0.5
            # Hafif rastgelelik ekle
            hiz += random.uniform(-0.3, 0.5)

            sans = random.random()
            if sans < 0.02:
                # %2 can paketi
                self.dusen_nesneler.append(HealItem(x, hiz))
            elif sans < 0.07:
                # %5 altın elma
                self.dusen_nesneler.append(GoldenItem(x, hiz))
            elif sans < 0.32:
                # %25 bomba
                self.dusen_nesneler.append(BadItem(x, hiz, gorsel=self.bomba_img))
            else:
                # %68 elma
                self.dusen_nesneler.append(GoodItem(x, hiz, gorsel=self.elma_img))

    # -------------------------------------------------------------------------
    # Zorluk Ayarlama
    # -------------------------------------------------------------------------
    def _zorluk_ayarla(self):
        """
        Skora bağlı olarak oyun zorluğunu dinamik olarak artırır.
        Her 500 puanda bir seviye atlar.
        """
        yeni_seviye = 1 + self.skor // 500

        if yeni_seviye != self.zorluk_seviyesi:
            self.zorluk_seviyesi = yeni_seviye

            # Nesnelerin ekranda belirme sıklığını artır (minimum 15 kare)
            self.nesne_bekleme = max(15, 50 - (self.zorluk_seviyesi - 1) * 5)

            # Temel düşme hızını artır (minimum güvenli üst sınır)
            self.temel_hiz = min(8.0, 3.0 + (self.zorluk_seviyesi - 1) * 0.5)

    # -------------------------------------------------------------------------
    # Çarpışma Tespiti
    # -------------------------------------------------------------------------
    def _carpismalari_kontrol_et(self):
        """Düşen nesneler ile sepet arasındaki çarpışmaları kontrol eder."""
        sepet_rect = self.sepet.dikdortgen_al()

        for nesne in self.dusen_nesneler:
            if not nesne.aktif:
                continue

            if sepet_rect.colliderect(nesne.dikdortgen_al()):
                nesne.aktif = False

                # Parçacık efekti merkez noktası
                px = nesne.x + nesne.genislik // 2
                py = nesne.y + nesne.yukseklik // 2

                if isinstance(nesne, GoldenItem):
                    # Altın elma toplandı → yüksek skor
                    self.skor += nesne.puan
                    self.parcacik_yonetici.patlama_ekle(px, py, ALTIN, 25)

                elif isinstance(nesne, HealItem):
                    # Can paketi toplandı → can artır
                    if self.can < MAKS_CAN:
                        self.can += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, ACIK_YESIL, 20)

                elif isinstance(nesne, GoodItem):
                    # Elma toplandı → skor artır
                    self.skor += nesne.puan
                    self.parcacik_yonetici.patlama_ekle(px, py, YESIL, 15)

                elif isinstance(nesne, BadItem):
                    # Bomba çarptı → can azalt
                    self.can -= 1
                    if self.bomba_ses:
                        self.bomba_ses.play()
                    self.parcacik_yonetici.patlama_ekle(px, py, TURUNCU, 20)

    # -------------------------------------------------------------------------
    # Arka Plan Çizimi
    # -------------------------------------------------------------------------
    def _arkaplan_ciz(self):
        """Gradyan arka plan ve dekoratif öğeler çizer."""
        # Gradyan gökyüzü
        for y in range(EKRAN_YUKSEKLIK):
            oran = y / EKRAN_YUKSEKLIK
            r = int(30 + 100 * oran)
            g = int(30 + 140 * oran)
            b = int(80 + 120 * oran)
            pygame.draw.line(self.ekran, (r, g, b), (0, y), (EKRAN_GENISLIK, y))

        # Zemin (yeşil çimen)
        zemin_y = EKRAN_YUKSEKLIK - 30
        pygame.draw.rect(self.ekran, KOYU_YESIL, (0, zemin_y, EKRAN_GENISLIK, 30))
        pygame.draw.rect(self.ekran, YESIL, (0, zemin_y, EKRAN_GENISLIK, 5))

    # -------------------------------------------------------------------------
    # HUD (Skor, Can, Zorluk Göstergesi)
    # -------------------------------------------------------------------------
    def _hud_ciz(self):
        """Ekranın üstünde skor, can ve zorluk bilgisini gösterir."""
        # Yarı saydam üst panel
        panel = pygame.Surface((EKRAN_GENISLIK, 45), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        self.ekran.blit(panel, (0, 0))

        # Skor
        skor_yazi = self.orta_font.render(f"Skor: {self.skor}", True, BEYAZ)
        self.ekran.blit(skor_yazi, (15, 8))

        # En yüksek skor
        eys_yazi = self.kucuk_font.render(f"En Yüksek: {self.en_yuksek_skor}", True, SARI)
        self.ekran.blit(eys_yazi, (200, 12))

        # Zorluk seviyesi
        zorluk_yazi = self.kucuk_font.render(f"Seviye: {self.zorluk_seviyesi}", True, ACIK_MAVI)
        self.ekran.blit(zorluk_yazi, (420, 12))

        # Canlar (kalp görseli veya geometrik kalp)
        for i in range(self.can):
            kalp_x = EKRAN_GENISLIK - 40 - i * 35
            kalp_y = 8
            if self.kalp_img:
                self.ekran.blit(self.kalp_img, (kalp_x - 5, kalp_y))
            else:
                pygame.draw.circle(self.ekran, KIRMIZI, (kalp_x, kalp_y + 5), 8)
                pygame.draw.circle(self.ekran, KIRMIZI, (kalp_x + 10, kalp_y + 5), 8)
                pygame.draw.polygon(self.ekran, KIRMIZI, [
                    (kalp_x - 8, kalp_y + 6),
                    (kalp_x + 18, kalp_y + 6),
                    (kalp_x + 5, kalp_y + 22)
                ])

    # -------------------------------------------------------------------------
    # Ana Menü Ekranı
    # -------------------------------------------------------------------------
    def _menu_ciz(self):
        """Oyunun başlangıç menüsünü ekrana çizer."""
        self._arkaplan_ciz()

        # Başlık
        baslik = self.baslik_font.render("Sepet Oyunu", True, BEYAZ)
        baslik_golge = self.baslik_font.render("Sepet Oyunu", True, (0, 0, 0))
        bx = EKRAN_GENISLIK // 2 - baslik.get_width() // 2
        self.ekran.blit(baslik_golge, (bx + 3, 43))
        self.ekran.blit(baslik, (bx, 40))

        # Alt başlık
        alt = self.orta_font.render("Elmaları topla, bombalardan kaçın!", True, SARI)
        self.ekran.blit(alt, (EKRAN_GENISLIK // 2 - alt.get_width() // 2, 110))

        # --- Top 5 Liderlik Tablosu ---
        top5_baslik = self.orta_font.render("En İyi 5 Skor", True, ALTIN)
        self.ekran.blit(top5_baslik, (EKRAN_GENISLIK // 2 - top5_baslik.get_width() // 2, 155))

        top5 = self.veritabani.en_iyi_5_al()
        if top5:
            for sira, (isim, skor) in enumerate(top5, 1):
                renk = ALTIN if sira == 1 else BEYAZ
                satir = self.kucuk_font.render(f"{sira}. {isim} - {skor} puan", True, renk)
                self.ekran.blit(satir, (EKRAN_GENISLIK // 2 - satir.get_width() // 2, 180 + sira * 25))
        else:
            bos_yazi = self.kucuk_font.render("Henüz skor kaydı yok", True, GRI)
            self.ekran.blit(bos_yazi, (EKRAN_GENISLIK // 2 - bos_yazi.get_width() // 2, 205))

        # Kontroller bilgisi
        kontrol1 = self.kucuk_font.render("← → Ok Tuşları veya A / D ile sepeti hareket ettir", True, BEYAZ)
        self.ekran.blit(kontrol1, (EKRAN_GENISLIK // 2 - kontrol1.get_width() // 2, 365))

        # Nesne açıklamaları (tek satır, ikonlarla)
        y_ikon = 400
        pygame.draw.circle(self.ekran, KIRMIZI, (170, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("Elma +10", True, YESIL), (188, y_ikon - 8))

        pygame.draw.circle(self.ekran, ALTIN, (310, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("Altın +100", True, ALTIN), (328, y_ikon - 8))

        pygame.draw.circle(self.ekran, KOYU_GRI, (465, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("Bomba -1\u2665", True, KIRMIZI), (483, y_ikon - 8))

        pygame.draw.circle(self.ekran, ACIK_YESIL, (610, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("+1\u2665", True, ACIK_YESIL), (628, y_ikon - 8))

        # Başlat butonu
        buton_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 445, 240, 55)
        fare = pygame.mouse.get_pos()
        if buton_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, YESIL, buton_rect, border_radius=12)
        else:
            pygame.draw.rect(self.ekran, KOYU_YESIL, buton_rect, border_radius=12)
        pygame.draw.rect(self.ekran, BEYAZ, buton_rect, 2, border_radius=12)

        buton_yazi = self.buyuk_font.render("BAŞLAT", True, BEYAZ)
        self.ekran.blit(buton_yazi,
                        (buton_rect.centerx - buton_yazi.get_width() // 2,
                         buton_rect.centery - buton_yazi.get_height() // 2))

        # ENTER ipucu
        enter_yazi = self.kucuk_font.render("veya ENTER tuşuna bas", True, GRI)
        self.ekran.blit(enter_yazi, (EKRAN_GENISLIK // 2 - enter_yazi.get_width() // 2, 510))

        return buton_rect

    # -------------------------------------------------------------------------
    # Oyun Bitti Ekranı
    # -------------------------------------------------------------------------
    def _bitti_ekrani_ciz(self):
        """Oyun bittiğinde gösterilen sonuç ekranını çizer."""
        self._arkaplan_ciz()

        # Yarı saydam karartma
        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.ekran.blit(overlay, (0, 0))

        # Panel
        panel_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 200, 100, 400, 380)
        pygame.draw.rect(self.ekran, (30, 30, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, BEYAZ, panel_rect, 2, border_radius=15)

        # Başlık
        baslik = self.buyuk_font.render("OYUN BİTTİ!", True, KIRMIZI)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 130))

        # Skor
        skor_yazi = self.orta_font.render(f"Skorun: {self.son_skor}", True, BEYAZ)
        self.ekran.blit(skor_yazi, (EKRAN_GENISLIK // 2 - skor_yazi.get_width() // 2, 200))

        # Zorluk
        seviye_yazi = self.orta_font.render(f"Ulaşılan Seviye: {self.zorluk_seviyesi}", True, ACIK_MAVI)
        self.ekran.blit(seviye_yazi, (EKRAN_GENISLIK // 2 - seviye_yazi.get_width() // 2, 240))

        # En yüksek skor
        eys_yazi = self.orta_font.render(f"En Yüksek Skor: {self.en_yuksek_skor}", True, SARI)
        self.ekran.blit(eys_yazi, (EKRAN_GENISLIK // 2 - eys_yazi.get_width() // 2, 290))

        # Yeni rekor bildirimi
        if self.son_skor >= self.en_yuksek_skor and self.son_skor > 0:
            if (pygame.time.get_ticks() // 400) % 2 == 0:
                rekor = self.orta_font.render("★ YENİ REKOR! ★", True, SARI)
                self.ekran.blit(rekor, (EKRAN_GENISLIK // 2 - rekor.get_width() // 2, 330))

        # Tekrar oyna butonu
        buton_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 130, 380, 260, 50)
        fare = pygame.mouse.get_pos()
        if buton_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, MAVI, buton_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (40, 80, 160), buton_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, buton_rect, 2, border_radius=10)

        tekrar_yazi = self.orta_font.render("Tekrar Oyna", True, BEYAZ)
        self.ekran.blit(tekrar_yazi,
                        (buton_rect.centerx - tekrar_yazi.get_width() // 2,
                         buton_rect.centery - tekrar_yazi.get_height() // 2))

        # Çıkış ipucu
        cikis = self.kucuk_font.render("ESC: Menüye Dön  |  ENTER: Tekrar Oyna", True, GRI)
        self.ekran.blit(cikis, (EKRAN_GENISLIK // 2 - cikis.get_width() // 2, 450))

        return buton_rect

    # -------------------------------------------------------------------------
    # İsim Giriş Ekranı (Top 5'e Girenler İçin)
    # -------------------------------------------------------------------------
    def _isim_gir_ciz(self):
        """Top 5'e giren oyuncunun ismini girmesi için ekran."""
        self._arkaplan_ciz()

        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.ekran.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 220, 150, 440, 300)
        pygame.draw.rect(self.ekran, (30, 30, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, ALTIN, panel_rect, 2, border_radius=15)

        tebrik = self.buyuk_font.render("Tebrikler!", True, ALTIN)
        self.ekran.blit(tebrik, (EKRAN_GENISLIK // 2 - tebrik.get_width() // 2, 175))

        bilgi = self.orta_font.render(f"Skorun: {self.son_skor} - Top 5'e girdin!", True, BEYAZ)
        self.ekran.blit(bilgi, (EKRAN_GENISLIK // 2 - bilgi.get_width() // 2, 225))

        isim_label = self.orta_font.render("İsmini gir:", True, ACIK_MAVI)
        self.ekran.blit(isim_label, (EKRAN_GENISLIK // 2 - isim_label.get_width() // 2, 280))

        # İsim giriş kutusu
        kutu_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 150, 320, 300, 45)
        pygame.draw.rect(self.ekran, BEYAZ, kutu_rect, border_radius=8)
        pygame.draw.rect(self.ekran, ACIK_MAVI, kutu_rect, 2, border_radius=8)

        # İmleç yanıp sönme
        self.isim_imlec_zamanlayici += 1
        if self.isim_imlec_zamanlayici >= 30:
            self.isim_imlec_zamanlayici = 0
            self.isim_imlec_gorunsun = not self.isim_imlec_gorunsun

        imlec = "|" if self.isim_imlec_gorunsun else ""
        isim_yazi = self.orta_font.render(self.oyuncu_ismi + imlec, True, SIYAH)
        self.ekran.blit(isim_yazi, (kutu_rect.x + 10, kutu_rect.y + 8))

        ipucu = self.kucuk_font.render("ENTER tuşu ile onayla", True, GRI)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK // 2 - ipucu.get_width() // 2, 380))

    # -------------------------------------------------------------------------
    # Ana Oyun Döngüsü
    # -------------------------------------------------------------------------
    def calistir(self):
        """
        Ana oyun döngüsü. Menü, oyun, isim girişi ve bitiş ekranlarını
        durum makinesine (state machine) göre yönetir.
        """
        calisiyor = True

        while calisiyor:
            # --- OLAY İŞLEME ---
            for olay in pygame.event.get():
                if olay.type == pygame.QUIT:
                    calisiyor = False

                if olay.type == pygame.KEYDOWN:
                    # --- İsim giriş durumu (özel klavye işleme) ---
                    if self.durum == "isim_gir":
                        if olay.key == pygame.K_RETURN:
                            isim = self.oyuncu_ismi.strip() or "Anonim"
                            self.veritabani.skor_ekle(isim, self.son_skor)
                            self.en_yuksek_skor = self.veritabani.en_yuksek_skor()
                            self.durum = "bitti"
                        elif olay.key == pygame.K_BACKSPACE:
                            self.oyuncu_ismi = self.oyuncu_ismi[:-1]
                        elif len(self.oyuncu_ismi) < 15:
                            if olay.unicode.isprintable() and olay.unicode:
                                self.oyuncu_ismi += olay.unicode
                    else:
                        # --- Diğer durumlar ---
                        if olay.key == pygame.K_ESCAPE:
                            if self.durum == "oyun":
                                self.durum = "menu"
                            elif self.durum == "bitti":
                                self.durum = "menu"
                            else:
                                calisiyor = False

                        if olay.key == pygame.K_RETURN:
                            if self.durum == "menu":
                                self._oyunu_sifirla()
                                self.durum = "oyun"
                            elif self.durum == "bitti":
                                self._oyunu_sifirla()
                                self.durum = "oyun"

                if olay.type == pygame.MOUSEBUTTONDOWN and olay.button == 1:
                    if self.durum == "menu":
                        buton = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 445, 240, 55)
                        if buton.collidepoint(olay.pos):
                            self._oyunu_sifirla()
                            self.durum = "oyun"
                    elif self.durum == "bitti":
                        buton = pygame.Rect(EKRAN_GENISLIK // 2 - 130, 380, 260, 50)
                        if buton.collidepoint(olay.pos):
                            self._oyunu_sifirla()
                            self.durum = "oyun"

            # --- DURUM MAKİNESİ ---
            if self.durum == "menu":
                self._menu_ciz()

            elif self.durum == "oyun":
                self._oyun_guncelle()
                self._oyun_ciz()

            elif self.durum == "isim_gir":
                self._isim_gir_ciz()

            elif self.durum == "bitti":
                self._bitti_ekrani_ciz()

            pygame.display.flip()
            self.saat.tick(FPS)

        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------------------
    # Oyun Güncelleme (Her Karede Çalışır)
    # -------------------------------------------------------------------------
    def _oyun_guncelle(self):
        """
        Oyunun her karesinde çağrılır.
        Sepet hareketi, nesne üretimi, güncelleme, çarpışma ve
        zorluk ayarını yönetir.
        """
        self.toplam_kare += 1

        # Sepet hareketi
        tuslar = pygame.key.get_pressed()
        self.sepet.hareket_et(tuslar)

        # Yeni nesne üretimi
        self._nesne_uret()

        # Nesneleri güncelle
        for nesne in self.dusen_nesneler:
            nesne.guncelle()

        # Çarpışma kontrolü
        self._carpismalari_kontrol_et()

        # Aktif olmayan nesneleri listeden kaldır
        self.dusen_nesneler = [n for n in self.dusen_nesneler if n.aktif]

        # Zorluğu ayarla
        self._zorluk_ayarla()

        # Parçacıkları güncelle
        self.parcacik_yonetici.guncelle()

        # Can bittiyse oyunu bitir
        if self.can <= 0:
            self.can = 0
            self.son_skor = self.skor
            self.en_yuksek_skor = self.veritabani.en_yuksek_skor()
            # Skor ilk 5'e giriyorsa isim sor
            if self.son_skor > 0 and self.veritabani.ilk_5e_girer_mi(self.son_skor):
                self.durum = "isim_gir"
            else:
                self.durum = "bitti"

    # -------------------------------------------------------------------------
    # Oyun Çizimi
    # -------------------------------------------------------------------------
    def _oyun_ciz(self):
        """Oyun ekranındaki tüm öğeleri çizer."""
        # Arka plan
        self._arkaplan_ciz()

        # Düşen nesneler
        for nesne in self.dusen_nesneler:
            nesne.ciz(self.ekran)

        # Sepet
        self.sepet.ciz(self.ekran)

        # Parçacık efektleri
        self.parcacik_yonetici.ciz(self.ekran)

        # HUD (skor, can vb.)
        self._hud_ciz()


# =============================================================================
# PROGRAMIN GİRİŞ NOKTASI
# =============================================================================
if __name__ == "__main__":
    oyun = GameManager()
    oyun.calistir()
