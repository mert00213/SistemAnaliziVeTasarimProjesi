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

# --- Pygame başlatma ---
pygame.init()

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

# Skor dosyası yolu (oyun dosyasıyla aynı klasörde)
SKOR_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skor.txt")


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

    def __init__(self, x, hiz):
        # Elma boyutları
        super().__init__(x, -40, 34, 34, hiz, KIRMIZI)
        self.puan = 10  # Her elma 10 puan

        # --- Buraya ileride görsel (image) eklenebilir ---
        # self.gorsel = pygame.image.load("assets/elma.png").convert_alpha()

    def ciz(self, ekran):
        """Elma şeklini Pygame çizim araçlarıyla oluşturur."""
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

    def __init__(self, x, hiz):
        super().__init__(x, -40, 34, 34, hiz, SIYAH)

        # --- Buraya ileride görsel (image) eklenebilir ---
        # self.gorsel = pygame.image.load("assets/bomba.png").convert_alpha()

    def ciz(self, ekran):
        """Bomba şeklini Pygame çizim araçlarıyla oluşturur."""
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
# SINIF: Basket (Sepet - Oyuncunun Kontrol Ettiği Nesne)
# =============================================================================
class Basket:
    """
    Oyuncunun klavye ile sağa-sola hareket ettirdiği sepet nesnesi.
    Ok tuşları veya A/D tuşlarıyla kontrol edilir.
    """

    def __init__(self):
        self.genislik = 100
        self.yukseklik = 50
        self.x = EKRAN_GENISLIK // 2 - self.genislik // 2
        self.y = EKRAN_YUKSEKLIK - 70
        self.hiz = 8
        self.renk = KAHVERENGI

        # --- Buraya ileride sepet görseli eklenebilir ---
        # self.gorsel = pygame.image.load("assets/sepet.png").convert_alpha()

    def hareket_et(self, tuslar):
        """Basılan tuşlara göre sepeti sağa veya sola hareket ettirir."""
        if (tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]) and self.x > 0:
            self.x -= self.hiz
        if (tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]) and self.x < EKRAN_GENISLIK - self.genislik:
            self.x += self.hiz

    def ciz(self, ekran):
        """Sepeti Pygame şekil çizim araçlarıyla ekrana çizer."""
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

        # --- Buraya ileride arka plan müziği eklenebilir ---
        # pygame.mixer.music.load("assets/arkaplan_muzik.mp3")
        # pygame.mixer.music.play(-1)

        # --- Buraya ileride ses efektleri eklenebilir ---
        # self.elma_ses = pygame.mixer.Sound("assets/elma_toplama.wav")
        # self.bomba_ses = pygame.mixer.Sound("assets/patlama.wav")

        # Oyun durumu
        self.durum = "menu"  # "menu", "oyun", "bitti"
        self.en_yuksek_skor = self._skor_oku()

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
        self.sepet = Basket()
        self.dusen_nesneler = []
        self.skor = 0
        self.can = 3
        self.nesne_zamanlayici = 0
        self.nesne_bekleme = 50  # Kaç karede bir nesne üretilecek (başlangıç)
        self.temel_hiz = 3.0  # Nesnelerin başlangıç düşme hızı
        self.zorluk_seviyesi = 1
        self.toplam_kare = 0
        self.son_skor = 0

    # -------------------------------------------------------------------------
    # Veri Kalıcılığı: Skor Okuma / Yazma
    # -------------------------------------------------------------------------
    def _skor_oku(self):
        """
        skor.txt dosyasından en yüksek skoru okur.
        Dosya yoksa veya hatalıysa 0 döndürür.
        """
        try:
            with open(SKOR_DOSYASI, "r", encoding="utf-8") as dosya:
                icerik = dosya.read().strip()
                return int(icerik) if icerik.isdigit() else 0
        except (FileNotFoundError, ValueError, PermissionError):
            return 0

    def _skor_kaydet(self, skor):
        """
        Verilen skor mevcut en yüksek skordan büyükse skor.txt dosyasına kaydeder.
        Dosya yoksa otomatik oluşturur.
        """
        if skor > self.en_yuksek_skor:
            self.en_yuksek_skor = skor
            try:
                with open(SKOR_DOSYASI, "w", encoding="utf-8") as dosya:
                    dosya.write(str(skor))
            except PermissionError:
                pass  # Dosyaya yazılamazsa sessizce geç

    # -------------------------------------------------------------------------
    # Nesne Üretimi
    # -------------------------------------------------------------------------
    def _nesne_uret(self):
        """
        Zamanlayıcıya göre yeni düşen nesne üretir.
        %75 ihtimalle iyi nesne (elma), %25 ihtimalle kötü nesne (bomba) gelir.
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

            # %75 elma, %25 bomba
            if random.random() < 0.75:
                self.dusen_nesneler.append(GoodItem(x, hiz))
            else:
                self.dusen_nesneler.append(BadItem(x, hiz))

    # -------------------------------------------------------------------------
    # Zorluk Ayarlama
    # -------------------------------------------------------------------------
    def _zorluk_ayarla(self):
        """
        Skora bağlı olarak oyun zorluğunu dinamik olarak artırır.
        Her 50 puanda bir seviye atlar.
        """
        yeni_seviye = 1 + self.skor // 50

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

                if isinstance(nesne, GoodItem):
                    # İyi nesne toplandı → skor artır
                    self.skor += nesne.puan
                    # --- Buraya ses efekti eklenebilir ---
                    # self.elma_ses.play()

                elif isinstance(nesne, BadItem):
                    # Kötü nesne çarptı → can azalt
                    self.can -= 1
                    # --- Buraya ses efekti eklenebilir ---
                    # self.bomba_ses.play()

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

        # Canlar (kalp simgeleri)
        for i in range(self.can):
            kalp_x = EKRAN_GENISLIK - 40 - i * 35
            kalp_y = 12
            # Basit kalp çizimi (iki daire + üçgen)
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
        self.ekran.blit(baslik_golge, (bx + 3, 103))
        self.ekran.blit(baslik, (bx, 100))

        # Alt başlık
        alt = self.orta_font.render("Elmaları topla, bombalardan kaçın!", True, SARI)
        self.ekran.blit(alt, (EKRAN_GENISLIK // 2 - alt.get_width() // 2, 180))

        # En yüksek skor
        eys = self.orta_font.render(f"En Yüksek Skor: {self.en_yuksek_skor}", True, BEYAZ)
        self.ekran.blit(eys, (EKRAN_GENISLIK // 2 - eys.get_width() // 2, 240))

        # Kontroller bilgisi
        kontrol_baslik = self.orta_font.render("Kontroller:", True, ACIK_MAVI)
        self.ekran.blit(kontrol_baslik, (EKRAN_GENISLIK // 2 - kontrol_baslik.get_width() // 2, 310))

        kontrol1 = self.kucuk_font.render("← → Ok Tuşları veya A / D ile sepeti hareket ettir", True, BEYAZ)
        self.ekran.blit(kontrol1, (EKRAN_GENISLIK // 2 - kontrol1.get_width() // 2, 345))

        # Elma ve bomba açıklaması
        pygame.draw.circle(self.ekran, KIRMIZI, (280, 400), 12)
        aciklama1 = self.kucuk_font.render("= Elma (+10 Puan)", True, YESIL)
        self.ekran.blit(aciklama1, (300, 390))

        pygame.draw.circle(self.ekran, SIYAH, (280, 435), 12)
        pygame.draw.circle(self.ekran, KOYU_GRI, (280, 435), 10)
        aciklama2 = self.kucuk_font.render("= Bomba (-1 Can)", True, KIRMIZI)
        self.ekran.blit(aciklama2, (300, 425))

        # Başlat butonu
        buton_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 490, 240, 55)
        # Fare üzerindeyse renk değiştir
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
        self.ekran.blit(enter_yazi, (EKRAN_GENISLIK // 2 - enter_yazi.get_width() // 2, 555))

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
            # Yanıp sönen efekt
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
    # Ana Oyun Döngüsü
    # -------------------------------------------------------------------------
    def calistir(self):
        """
        Ana oyun döngüsü. Menü, oyun ve bitiş ekranlarını
        durum makinesine (state machine) göre yönetir.
        """
        calisiyor = True

        while calisiyor:
            # --- OLAY İŞLEME ---
            for olay in pygame.event.get():
                if olay.type == pygame.QUIT:
                    calisiyor = False

                if olay.type == pygame.KEYDOWN:
                    if olay.key == pygame.K_ESCAPE:
                        if self.durum == "oyun":
                            # Oyun sırasında ESC → Menüye dön
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
                        buton = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 490, 240, 55)
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

        # Can bittiyse oyunu bitir
        if self.can <= 0:
            self.can = 0
            self.son_skor = self.skor
            self._skor_kaydet(self.skor)
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

        # HUD (skor, can vb.)
        self._hud_ciz()


# =============================================================================
# PROGRAMIN GİRİŞ NOKTASI
# =============================================================================
if __name__ == "__main__":
    oyun = GameManager()
    oyun.calistir()
