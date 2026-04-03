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

# Sepet renk seçenekleri (Market sistemi)
SEPET_RENKLERI = {
    "kahverengi": {"renk": (139, 90, 43), "ic": (180, 120, 60), "kenar": (100, 60, 20), "fiyat": 0},
    "kirmizi":    {"renk": (180, 40, 40), "ic": (220, 80, 80), "kenar": (120, 20, 20), "fiyat": 500},
    "mavi":       {"renk": (40, 80, 180), "ic": (80, 120, 220), "kenar": (20, 50, 130), "fiyat": 500},
    "mor":        {"renk": (130, 40, 180), "ic": (170, 80, 220), "kenar": (90, 20, 130), "fiyat": 1000},
    "altin":      {"renk": (200, 170, 40), "ic": (240, 210, 80), "kenar": (160, 130, 20), "fiyat": 2000},
}

# Görev (Achievement) tanımları
GOREV_TANIMLARI = {
    "50_elma": "50 Elma Topla",
    "1000_hasarsiz": "Hiç Can Kaybetmeden 1000 Puan",
    "5_altin": "Tek Oyunda 5 Altın Elma Yakala",
}
KOYU_KIRMIZI = (140, 20, 30)


# =============================================================================
# SINIF: ParalaksKatman (Paralaks Arka Plan Katmanı)
# =============================================================================
class ParalaksKatman:
    """Yatay kayan tek arka plan katmanı."""

    def __init__(self, hiz, gorsel=None, cizim_fonk=None):
        self.hiz = hiz
        self.offset = 0.0
        self.gorsel = gorsel
        self.cizim_fonk = cizim_fonk  # Görsel yoksa fallback çizim

    def guncelle(self):
        """Katmanı yatay olarak kaydırır."""
        self.offset = (self.offset + self.hiz) % EKRAN_GENISLIK

    def ciz(self, ekran, fever_aktif=False):
        """Katmanı çizer (görsel veya geometrik fallback)."""
        if self.gorsel:
            ekran.blit(self.gorsel, (-self.offset, 0))
            ekran.blit(self.gorsel, (EKRAN_GENISLIK - self.offset, 0))
        elif self.cizim_fonk:
            self.cizim_fonk(ekran, self.offset, fever_aktif)


def _bulut_ciz(ekran, offset, fever_aktif):
    """Geometrik bulut katmanı çizer."""
    renk = (255, 200, 220) if fever_aktif else (220, 230, 245)
    bulutlar = [(100, 60, 60), (350, 40, 45), (600, 70, 55), (850, 50, 40)]
    for bx, by, br in bulutlar:
        x = (bx - offset) % (EKRAN_GENISLIK + 100) - 50
        pygame.draw.ellipse(ekran, renk, (int(x), by, br * 2, br))
        pygame.draw.ellipse(ekran, renk, (int(x) + br // 2, by - br // 3, int(br * 1.5), int(br * 0.8)))
        pygame.draw.ellipse(ekran, renk, (int(x) - br // 3, by + br // 5, int(br * 1.3), int(br * 0.7)))


def _dag_ciz(ekran, offset, fever_aktif):
    """Geometrik dağ / ağaç katmanı çizer."""
    dag_renk = (70, 50, 90) if fever_aktif else (50, 70, 50)
    agac_renk = (60, 110, 50) if fever_aktif else (30, 80, 30)
    daglar = [(0, 120), (200, 100), (400, 140), (600, 110), (800, 130)]
    for dx, dh in daglar:
        x = (dx - offset * 2) % (EKRAN_GENISLIK + 200) - 100
        noktalar = [(int(x), EKRAN_YUKSEKLIK - 30),
                     (int(x) + 80, EKRAN_YUKSEKLIK - 30 - dh),
                     (int(x) + 160, EKRAN_YUKSEKLIK - 30)]
        pygame.draw.polygon(ekran, dag_renk, noktalar)
    agaclar = [(50, 35), (250, 28), (450, 40), (650, 32), (850, 38)]
    for ax, ah in agaclar:
        x = int((ax - offset * 2) % (EKRAN_GENISLIK + 100) - 50)
        govde = pygame.Rect(x + 8, EKRAN_YUKSEKLIK - 30 - ah, 6, ah)
        pygame.draw.rect(ekran, KAHVERENGI, govde)
        pygame.draw.polygon(ekran, agac_renk,
                            [(x, EKRAN_YUKSEKLIK - 30 - ah),
                             (x + 11, EKRAN_YUKSEKLIK - 30 - ah - 25),
                             (x + 22, EKRAN_YUKSEKLIK - 30 - ah)])


# =============================================================================
# SINIF: EkranSarsintisi (Screen Shake)
# =============================================================================
class EkranSarsintisi:
    """Bombaya çarpınca veya can gidince ekran titremesi."""

    def __init__(self):
        self.sure = 0  # Kalan kare sayısı
        self.siddet = 0

    def baslat(self, sure_kare=12, siddet=8):
        """Sarsıntı başlatır (varsayılan ~0.2 saniye, 60 FPS)."""
        self.sure = sure_kare
        self.siddet = siddet

    def offset_al(self):
        """Bu karedeki x,y kayma miktarını döndürür."""
        if self.sure <= 0:
            return 0, 0
        self.sure -= 1
        x = random.randint(-self.siddet, self.siddet)
        y = random.randint(-self.siddet, self.siddet)
        return x, y


# =============================================================================
# SINIF: KalpKirilma (Kalp Kırılma Efekti)
# =============================================================================
class KalpKirilma:
    """Can gittiğinde kalbin kırılarak yok olma animasyonu."""

    def __init__(self, x, y, kalp_img=None):
        self.x = float(x)
        self.y = float(y)
        self.kalp_img = kalp_img
        self.parcalar = []
        self.omur = 40
        self.aktif = True
        # 4 parça oluştur
        for _ in range(4):
            self.parcalar.append({
                "dx": random.uniform(-3, 3),
                "dy": random.uniform(-4, -1),
                "boyut": random.randint(5, 10),
                "renk": KIRMIZI,
            })

    def guncelle(self):
        """Parçaları hareket ettirir."""
        self.omur -= 1
        if self.omur <= 0:
            self.aktif = False
            return
        for p in self.parcalar:
            self.x += p["dx"] * 0.1
            p["dy"] += 0.12

    def ciz(self, ekran):
        """Kırılma parçalarını çizer."""
        if not self.aktif:
            return
        alpha = int(255 * (self.omur / 40))
        for p in self.parcalar:
            px = int(self.x + p["dx"] * (40 - self.omur))
            py = int(self.y + p["dy"] * (40 - self.omur))
            boyut = max(2, p["boyut"] * self.omur // 40)
            surf = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
            surf.fill((*p["renk"][:3], alpha))
            ekran.blit(surf, (px, py))


# =============================================================================
# SINIF: Duyuru (Announcer - Animasyonlu Bildirim)
# =============================================================================
class Duyuru:
    """Ekranda büyüyüp küçülen animasyonlu bildirim yazısı."""

    def __init__(self, metin, renk, sure_kare=120, y_pozisyon=None):
        self.metin = metin
        self.renk = renk
        self.sure = sure_kare
        self.max_sure = sure_kare
        self.aktif = True
        self.sayac = 0
        self.y_poz = y_pozisyon or EKRAN_YUKSEKLIK // 3

    def guncelle(self):
        self.sure -= 1
        self.sayac += 1
        if self.sure <= 0:
            self.aktif = False

    def ciz(self, ekran, font):
        if not self.aktif:
            return
        olcek = 1.0 + 0.18 * abs(math.sin(self.sayac * 0.12))
        alpha = int(255 * min(1.0, self.sure / 30.0))
        orijinal = font.render(self.metin, True, self.renk)
        w = max(1, int(orijinal.get_width() * olcek))
        h = max(1, int(orijinal.get_height() * olcek))
        olcekli = pygame.transform.scale(orijinal, (w, h))
        surf = pygame.Surface(olcekli.get_size(), pygame.SRCALPHA)
        surf.blit(olcekli, (0, 0))
        surf.set_alpha(alpha)
        ekran.blit(surf, (EKRAN_GENISLIK // 2 - w // 2, self.y_poz - h // 2))


# =============================================================================
# SINIF: GorevBildirimi (Achievement GOAL! Bildirimi)
# =============================================================================
class GorevBildirimi:
    """Görev tamamlandığında havalı 'GOAL!' bildirimi."""

    def __init__(self, gorev_ismi):
        self.gorev_ismi = gorev_ismi
        self.sure = 180  # 3 saniye
        self.aktif = True
        self.sayac = 0

    def guncelle(self):
        self.sure -= 1
        self.sayac += 1
        if self.sure <= 0:
            self.aktif = False

    def ciz(self, ekran, buyuk_font, kucuk_font):
        if not self.aktif:
            return
        alpha = int(255 * min(1.0, self.sure / 40.0))
        olcek = 1.0 + 0.22 * abs(math.sin(self.sayac * 0.08))
        goal_surf = buyuk_font.render("GOAL!", True, ALTIN)
        w = max(1, int(goal_surf.get_width() * olcek))
        h = max(1, int(goal_surf.get_height() * olcek))
        olcekli = pygame.transform.scale(goal_surf, (w, h))
        goal_alpha = pygame.Surface(olcekli.get_size(), pygame.SRCALPHA)
        goal_alpha.blit(olcekli, (0, 0))
        goal_alpha.set_alpha(alpha)
        x = EKRAN_GENISLIK // 2 - w // 2
        y = EKRAN_YUKSEKLIK // 4 - h // 2
        ekran.blit(goal_alpha, (x, y))
        isim_surf = kucuk_font.render(self.gorev_ismi, True, BEYAZ)
        isim_alpha = pygame.Surface(isim_surf.get_size(), pygame.SRCALPHA)
        isim_alpha.blit(isim_surf, (0, 0))
        isim_alpha.set_alpha(alpha)
        ekran.blit(isim_alpha, (EKRAN_GENISLIK // 2 - isim_surf.get_width() // 2, y + h + 10))


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
# SINIF: Boss (Kötü Meyve - Patron Seviyesi)
# =============================================================================
class Boss:
    """5000 puanda ortaya çıkan dev 'Kötü Meyve' boss."""

    def __init__(self):
        self.genislik = 120
        self.yukseklik = 80
        self.x = float(EKRAN_GENISLIK // 2 - self.genislik // 2)
        self.y = 60.0
        self.hiz = 2.5
        self.yon = 1
        self.max_can = 30
        self.can = self.max_can
        self.aktif = True
        self.bomba_zamanlayici = 0
        self.bomba_bekleme = 50
        self._parlama = 0
        self.hasar_flash = 0

    def guncelle(self):
        self._parlama += 1
        if self.hasar_flash > 0:
            self.hasar_flash -= 1
        self.x += self.hiz * self.yon
        if self.x <= 20:
            self.yon = 1
        elif self.x >= EKRAN_GENISLIK - self.genislik - 20:
            self.yon = -1
        self.bomba_zamanlayici += 1

    def bomba_atabilir(self):
        if self.bomba_zamanlayici >= self.bomba_bekleme:
            self.bomba_zamanlayici = 0
            return True
        return False

    def hasar_al(self, miktar=1):
        self.can -= miktar
        self.hasar_flash = 8
        if self.can <= 0:
            self.can = 0
            self.aktif = False

    def ciz(self, ekran):
        if not self.aktif:
            return
        ix = int(self.x)
        iy = int(self.y)
        cx = ix + self.genislik // 2
        cy = iy + self.yukseklik // 2
        govde_renk = BEYAZ if (self.hasar_flash > 0 and self.hasar_flash % 2 == 0) else KOYU_KIRMIZI
        pygame.draw.ellipse(ekran, govde_renk, (ix, iy, self.genislik, self.yukseklik))
        pygame.draw.ellipse(ekran, (120, 20, 40), (ix + 10, iy + 8, self.genislik - 20, self.yukseklik - 16))
        goz_y = cy - 5
        pygame.draw.circle(ekran, SARI, (cx - 20, goz_y), 10)
        pygame.draw.circle(ekran, SIYAH, (cx - 20, goz_y), 5)
        pygame.draw.circle(ekran, SARI, (cx + 20, goz_y), 10)
        pygame.draw.circle(ekran, SIYAH, (cx + 20, goz_y), 5)
        pygame.draw.arc(ekran, SIYAH, (cx - 15, cy + 5, 30, 15), 3.14, 0, 3)
        for i in range(-2, 3):
            sx = cx + i * 18
            pygame.draw.polygon(ekran, (100, 20, 30), [
                (sx - 5, iy + 5), (sx, iy - 15), (sx + 5, iy + 5)])
        # Can barı
        bar_w = self.genislik
        bar_x = ix
        bar_y = iy - 15
        pygame.draw.rect(ekran, KOYU_GRI, (bar_x, bar_y, bar_w, 8), border_radius=3)
        oran = self.can / self.max_can
        can_renk = YESIL if oran > 0.5 else SARI if oran > 0.25 else KIRMIZI
        pygame.draw.rect(ekran, can_renk, (bar_x, bar_y, int(bar_w * oran), 8), border_radius=3)
        pygame.draw.rect(ekran, BEYAZ, (bar_x, bar_y, bar_w, 8), 1, border_radius=3)

    def dikdortgen_al(self):
        return pygame.Rect(int(self.x), int(self.y), self.genislik, self.yukseklik)


# =============================================================================
# SINIF: BossBomba (Boss'un Fırlattığı Çapraz Bomba)
# =============================================================================
class BossBomba(FallingItem):
    """Boss'un oyuncuya doğru fırlattığı çapraz bomba."""

    def __init__(self, x, y, hedef_x, hedef_y):
        super().__init__(x, y, 20, 20, 0, TURUNCU)
        dx = hedef_x - x
        dy = hedef_y - y
        uzunluk = max(1, math.sqrt(dx * dx + dy * dy))
        self.vx = dx / uzunluk * 4.5
        self.vy = dy / uzunluk * 4.5
        self._sayac = 0

    def guncelle(self):
        self.x += self.vx
        self.y += self.vy
        self._sayac += 1
        if (self.y > EKRAN_YUKSEKLIK + 50 or self.y < -50 or
                self.x < -50 or self.x > EKRAN_GENISLIK + 50):
            self.aktif = False

    def ciz(self, ekran):
        if not self.aktif:
            return
        cx = int(self.x + 10)
        cy = int(self.y + 10)
        parlama = abs(math.sin(self._sayac * 0.15)) * 3
        pygame.draw.circle(ekran, (255, 100, 0), (cx, cy), int(10 + parlama))
        pygame.draw.circle(ekran, SARI, (cx, cy), 6)
        pygame.draw.circle(ekran, BEYAZ, (cx, cy), 3)


# =============================================================================
# SINIF: MermiItem (Boss Savaşında Düşen Mermi)
# =============================================================================
class MermiItem(FallingItem):
    """Boss savaşında düşen mermi - toplayınca boss'a hasar verir."""

    def __init__(self, x, hiz):
        super().__init__(x, -30, 24, 24, hiz, ACIK_MAVI)
        self._sayac = 0

    def guncelle(self):
        super().guncelle()
        self._sayac += 1

    def ciz(self, ekran):
        cx = int(self.x + 12)
        cy = int(self.y + 12)
        parlama = abs(math.sin(self._sayac * 0.1)) * 2
        pygame.draw.circle(ekran, (100, 200, 255), (cx, cy), int(12 + parlama))
        pygame.draw.circle(ekran, BEYAZ, (cx, cy), 8)
        pygame.draw.circle(ekran, ACIK_MAVI, (cx, cy), 5)
        pygame.draw.polygon(ekran, BEYAZ, [
            (cx - 3, cy + 2), (cx, cy - 5), (cx + 3, cy + 2)])


# =============================================================================
# SINIF: Basket (Sepet - Oyuncunun Kontrol Ettiği Nesne)
# =============================================================================
class Basket:
    """
    Oyuncunun klavye ile sağa-sola hareket ettirdiği sepet nesnesi.
    Ok tuşları veya A/D tuşlarıyla kontrol edilir.
    Squash-Stretch animasyonu ve renk özelleştirme destekler.
    """

    def __init__(self, gorsel=None, renk_adi="kahverengi"):
        self.base_genislik = 100
        self.base_yukseklik = 50
        self.genislik = self.base_genislik
        self.yukseklik = self.base_yukseklik
        self.x = EKRAN_GENISLIK // 2 - self.genislik // 2
        self.y = EKRAN_YUKSEKLIK - 70
        self.hiz = 8
        self.gorsel = gorsel
        self.base_gorsel = gorsel

        # Renk bilgileri
        renk_bilgi = SEPET_RENKLERI.get(renk_adi, SEPET_RENKLERI["kahverengi"])
        self.renk = renk_bilgi["renk"]
        self.ic_renk = renk_bilgi["ic"]
        self.kenar_renk = renk_bilgi["kenar"]

        # Squash-Stretch
        self._ss_timer = 0
        self._ss_aktif = False

    def squash_baslat(self):
        """Elma yakalayınca squash-stretch başlatır."""
        self._ss_timer = 12
        self._ss_aktif = True

    def hareket_et(self, tuslar):
        """Basılan tuşlara göre sepeti sağa veya sola hareket ettirir."""
        if (tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]) and self.x > 0:
            self.x -= self.hiz
        if (tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]) and self.x < EKRAN_GENISLIK - self.genislik:
            self.x += self.hiz

        # Squash-Stretch güncelle
        if self._ss_aktif:
            self._ss_timer -= 1
            if self._ss_timer <= 0:
                self._ss_aktif = False
                self.genislik = self.base_genislik
                self.yukseklik = self.base_yukseklik
            else:
                t = self._ss_timer / 12.0
                # İlk yarı squash (geniş-kısa), ikinci yarı stretch (dar-uzun)
                if t > 0.5:
                    s = math.sin((1.0 - t) * math.pi)
                    self.genislik = int(self.base_genislik * (1.0 + s * 0.15))
                    self.yukseklik = int(self.base_yukseklik * (1.0 - s * 0.12))
                else:
                    s = math.sin(t * math.pi)
                    self.genislik = int(self.base_genislik * (1.0 - s * 0.08))
                    self.yukseklik = int(self.base_yukseklik * (1.0 + s * 0.1))

            # Görseli yeniden boyutlandır
            if self.base_gorsel:
                self.gorsel = pygame.transform.scale(
                    self.base_gorsel, (self.genislik, self.yukseklik)
                )

    def ciz(self, ekran):
        """Sepet görselini veya geometrik şeklini ekrana çizer."""
        cx_offset = (self.base_genislik - self.genislik) // 2
        cy_offset = (self.base_yukseklik - self.yukseklik)
        draw_x = self.x + cx_offset
        draw_y = self.y + cy_offset

        if self.gorsel:
            ekran.blit(self.gorsel, (draw_x, draw_y))
            return

        # Fallback: geometrik çizim (custom renklerle)
        govde = pygame.Rect(draw_x, draw_y + 10, self.genislik, self.yukseklik - 10)
        pygame.draw.rect(ekran, self.renk, govde, border_radius=6)

        ic = pygame.Rect(draw_x + 5, draw_y + 14, self.genislik - 10, self.yukseklik - 20)
        pygame.draw.rect(ekran, self.ic_renk, ic, border_radius=4)

        sol_nokta = (draw_x - 8, draw_y + 10)
        sol_alt = (draw_x, draw_y + 10)
        sol_ust = (draw_x + 8, draw_y)
        pygame.draw.polygon(ekran, self.renk, [sol_nokta, sol_alt, sol_ust])

        sag_nokta = (draw_x + self.genislik + 8, draw_y + 10)
        sag_alt = (draw_x + self.genislik, draw_y + 10)
        sag_ust = (draw_x + self.genislik - 8, draw_y)
        pygame.draw.polygon(ekran, self.renk, [sag_nokta, sag_alt, sag_ust])

        pygame.draw.line(ekran, self.kenar_renk,
                         (draw_x - 8, draw_y + 10),
                         (draw_x + self.genislik + 8, draw_y + 10), 3)

        for i in range(1, 3):
            y_cizgi = draw_y + 10 + i * (self.yukseklik - 10) // 3
            pygame.draw.line(ekran, self.kenar_renk,
                             (draw_x + 2, y_cizgi),
                             (draw_x + self.genislik - 2, y_cizgi), 1)

    def dikdortgen_al(self):
        """Çarpışma tespiti için Rect nesnesi döndürür."""
        return pygame.Rect(self.x, self.y, self.base_genislik, self.base_yukseklik)


# =============================================================================
# SINIF: SkorVeritabani (SQLite Veritabanı Yöneticisi)
# =============================================================================
class SkorVeritabani:
    """SQLite ile skor ve market verilerini yöneten sınıf."""

    def __init__(self, db_yolu):
        self.db_yolu = db_yolu
        self._tablo_olustur()

    def _tablo_olustur(self):
        """Skor ve market tablolarını oluşturur (yoksa)."""
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
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS market (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        renk_adi TEXT UNIQUE NOT NULL,
                        satin_alindi INTEGER DEFAULT 0
                    )
                """)
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS oyuncu_veri (
                        anahtar TEXT PRIMARY KEY,
                        deger TEXT NOT NULL
                    )
                """)
                # Varsayılan sepet her zaman açık
                bag.execute(
                    "INSERT OR IGNORE INTO market (renk_adi, satin_alindi) VALUES ('kahverengi', 1)"
                )
                # Varsayılan aktif sepet
                bag.execute(
                    "INSERT OR IGNORE INTO oyuncu_veri (anahtar, deger) VALUES ('aktif_sepet', 'kahverengi')"
                )
                # Varsayılan bakiye
                bag.execute(
                    "INSERT OR IGNORE INTO oyuncu_veri (anahtar, deger) VALUES ('bakiye', '0')"
                )
                # Görev (Achievement) tablosu
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        gorev_id TEXT UNIQUE NOT NULL,
                        tamamlandi INTEGER DEFAULT 0,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Veritabanı tablosu oluşturulamadı: {e}")

    # --- Skor metotları ---
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

    # --- Market / Bakiye metotları ---
    def bakiye_al(self):
        """Oyuncunun toplam bakiyesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT deger FROM oyuncu_veri WHERE anahtar = 'bakiye'"
                )
                sonuc = cursor.fetchone()
                return int(sonuc[0]) if sonuc else 0
        except (sqlite3.Error, ValueError):
            return 0

    def bakiye_guncelle(self, miktar):
        """Bakiyeye miktar ekler (negatif olabilir)."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                mevcut = self.bakiye_al()
                yeni = max(0, mevcut + miktar)
                bag.execute(
                    "UPDATE oyuncu_veri SET deger = ? WHERE anahtar = 'bakiye'",
                    (str(yeni),)
                )
                bag.commit()
                return yeni
        except sqlite3.Error as e:
            print(f"[UYARI] Bakiye güncellenemedi: {e}")
            return self.bakiye_al()

    def sepet_satin_al(self, renk_adi):
        """Bir sepet rengini satın alır. Başarılı ise True döndürür."""
        fiyat = SEPET_RENKLERI.get(renk_adi, {}).get("fiyat", 0)
        bakiye = self.bakiye_al()
        if bakiye < fiyat:
            return False
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT OR REPLACE INTO market (renk_adi, satin_alindi) VALUES (?, 1)",
                    (renk_adi,)
                )
                bag.commit()
            self.bakiye_guncelle(-fiyat)
            return True
        except sqlite3.Error as e:
            print(f"[UYARI] Satın alma başarısız: {e}")
            return False

    def satin_alinan_sepetler(self):
        """Satın alınan sepet renklerinin listesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT renk_adi FROM market WHERE satin_alindi = 1"
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return ["kahverengi"]

    def aktif_sepet_al(self):
        """Aktif sepet rengini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT deger FROM oyuncu_veri WHERE anahtar = 'aktif_sepet'"
                )
                sonuc = cursor.fetchone()
                return sonuc[0] if sonuc else "kahverengi"
        except sqlite3.Error:
            return "kahverengi"

    def aktif_sepet_ayarla(self, renk_adi):
        """Aktif sepet rengini ayarlar."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "UPDATE oyuncu_veri SET deger = ? WHERE anahtar = 'aktif_sepet'",
                    (renk_adi,)
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Aktif sepet ayarlanamadı: {e}")

    # --- Görev (Achievement) metotları ---
    def gorev_tamamlandi_mi(self, gorev_id):
        """Görevin daha önce tamamlanıp tamamlanmadığını kontrol eder."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT tamamlandi FROM achievements WHERE gorev_id = ?",
                    (gorev_id,)
                )
                sonuc = cursor.fetchone()
                return bool(sonuc and sonuc[0])
        except sqlite3.Error:
            return False

    def gorev_tamamla(self, gorev_id):
        """Görevi tamamlandı olarak işaretler."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT OR REPLACE INTO achievements (gorev_id, tamamlandi) VALUES (?, 1)",
                    (gorev_id,)
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Görev kaydedilemedi: {e}")

    def tamamlanan_gorevler(self):
        """Tamamlanan tüm görevlerin ID listesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT gorev_id FROM achievements WHERE tamamlandi = 1"
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []


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
        self.oyun_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        pygame.display.set_caption("🍎 Sepet Oyunu - Catching Game")
        self.saat = pygame.time.Clock()

        # Fontlar
        self.baslik_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.buyuk_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.orta_font = pygame.font.SysFont("Arial", 26)
        self.kucuk_font = pygame.font.SysFont("Arial", 20)
        self.mini_font = pygame.font.SysFont("Arial", 16)

        # --- Arka plan müziği ---
        try:
            ses_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds")
            pygame.mixer.music.load(os.path.join(ses_klasoru, "arkaplan.mp3"))
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[UYARI] Arka plan müziği yüklenemedi: {e}")

        # --- Ses efektleri ---
        self.bomba_ses = None
        self.kombo_ses = None
        self.rekor_ses = None
        self.gorev_ses = None
        self.boss_ses = None
        try:
            self.bomba_ses = pygame.mixer.Sound(os.path.join(ses_klasoru, "bomba.mp3"))
        except Exception:
            pass
        ses_ekstra = {"kombo_ses": "combo.wav", "rekor_ses": "record.wav",
                      "gorev_ses": "goal.wav", "boss_ses": "boss_hit.wav"}
        for attr, dosya in ses_ekstra.items():
            try:
                yol = os.path.join(ses_klasoru, dosya)
                if os.path.exists(yol):
                    setattr(self, attr, pygame.mixer.Sound(yol))
            except Exception:
                pass

        # --- Görsel varlıkları yükleme ---
        self.sepet_img = None
        self.elma_img = None
        self.bomba_img = None
        self.kalp_img = None
        self.bulut_img = None
        self.dag_img = None
        try:
            gorsel_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds", "images")

            gorsel_haritasi = {
                "sepet": ("sepet.png", (100, 50)),
                "elma": ("elma.png", (34, 34)),
                "bomba": ("bomba.png", (34, 34)),
                "kalp": ("kalp.png", (28, 28)),
                "bulut": ("bulut.png", (EKRAN_GENISLIK, EKRAN_YUKSEKLIK)),
                "dag": ("dag.png", (EKRAN_GENISLIK, EKRAN_YUKSEKLIK)),
            }
            for anahtar, (dosya, boyut) in gorsel_haritasi.items():
                yol = os.path.join(gorsel_klasoru, dosya)
                if os.path.exists(yol):
                    setattr(self, f"{anahtar}_img",
                            pygame.transform.scale(
                                pygame.image.load(yol).convert_alpha(), boyut))
                else:
                    print(f"[UYARI] {dosya} görseli bulunamadı: {yol}")

        except Exception as e:
            print(f"[UYARI] Görseller yüklenirken hata oluştu: {e}")
            print("[BİLGİ] Oyun geometrik çizimlerle devam edecek.")
            self.sepet_img = None
            self.elma_img = None
            self.bomba_img = None
            self.kalp_img = None
            self.bulut_img = None
            self.dag_img = None

        # --- Paralaks katmanlar ---
        self.paralaks_katmanlar = [
            ParalaksKatman(0.3, gorsel=self.bulut_img, cizim_fonk=_bulut_ciz),
            ParalaksKatman(0.7, gorsel=self.dag_img, cizim_fonk=_dag_ciz),
        ]

        # --- Ekran sarsıntısı ---
        self.ekran_sarsintisi = EkranSarsintisi()

        # --- Veritabanı ---
        self.veritabani = SkorVeritabani(VERITABANI_YOLU)

        # Oyun durumu: "menu", "oyun", "isim_gir", "bitti", "market"
        self.durum = "menu"
        self.en_yuksek_skor = self.veritabani.en_yuksek_skor()

        # Aktif sepet rengi
        self.aktif_sepet_renk = self.veritabani.aktif_sepet_al()

        # İsim girişi için değişkenler
        self.oyuncu_ismi = ""
        self.isim_imlec_gorunsun = True
        self.isim_imlec_zamanlayici = 0

        # Parçacık yöneticisi
        self.parcacik_yonetici = ParticleManager()

        # Kalp kırılma efektleri
        self.kalp_kirilmalari = []

        # Market scroll pozisyonu
        self.market_scroll = 0

        # --- Duyuru (Announcer) sistemi ---
        self.duyurular = []

        # --- Görev (Achievement) bildirimleri ---
        self.gorev_bildirimleri = []

        # --- Gece/Gündüz döngüsü ---
        self.gece_modu = False
        self.gece_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        self.isik_yaricap = 130

        # --- Boss sistemi ---
        self.boss = None
        self.boss_aktif = False
        self.boss_yenildi = False
        self.boss_bombalar = []
        self.boss_mermi_zamanlayici = 0

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
        self.aktif_sepet_renk = self.veritabani.aktif_sepet_al()
        self.sepet = Basket(gorsel=self.sepet_img, renk_adi=self.aktif_sepet_renk)
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
        self.kalp_kirilmalari = []

        # Kombo sistemi
        self.kombo_sayac = 0
        self.kombo_carpan = 1
        self.kombo_bar = 0.0  # 0.0 - 1.0 (Fever Mode barı)

        # Fever (Öfke) Modu
        self.fever_aktif = False
        self.fever_kalan_kare = 0  # 5 saniye = 300 kare (60 FPS)
        self.fever_parlama = 0

        # Gece/Gündüz
        self.gece_modu = False

        # Boss
        self.boss = None
        self.boss_aktif = False
        self.boss_yenildi = False
        self.boss_bombalar = []
        self.boss_mermi_zamanlayici = 0

        # Duyurular
        self.duyurular = []
        self.gorev_bildirimleri = []

        # Achievement sayaçları (oyun başına)
        self.toplanan_elma_sayisi = 0
        self.toplanan_altin_sayisi = 0
        self.hasar_alindi = False

    # -------------------------------------------------------------------------
    # Nesne Üretimi
    # -------------------------------------------------------------------------
    def _nesne_uret(self):
        """
        Zamanlayıcıya göre yeni düşen nesne üretir.
        Boss modunda mermi, Fever modunda altın elma,
        Normal: %68 elma, %25 bomba, %5 altın elma, %2 can paketi.
        """
        if self.boss_aktif:
            # Boss modunda sadece mermi düşür
            self.boss_mermi_zamanlayici += 1
            if self.boss_mermi_zamanlayici >= 40:
                self.boss_mermi_zamanlayici = 0
                x = random.randint(20, EKRAN_GENISLIK - 54)
                hiz = self.temel_hiz + 0.5
                self.dusen_nesneler.append(MermiItem(x, hiz))
            return

        self.nesne_zamanlayici += 1
        if self.nesne_zamanlayici >= self.nesne_bekleme:
            self.nesne_zamanlayici = 0

            x = random.randint(20, EKRAN_GENISLIK - 54)
            hiz = self.temel_hiz + (self.zorluk_seviyesi - 1) * 0.5
            hiz += random.uniform(-0.3, 0.5)

            if self.fever_aktif:
                # Fever modunda sadece altın elma
                self.dusen_nesneler.append(GoldenItem(x, hiz))
            else:
                sans = random.random()
                if sans < 0.02:
                    self.dusen_nesneler.append(HealItem(x, hiz))
                elif sans < 0.07:
                    self.dusen_nesneler.append(GoldenItem(x, hiz))
                elif sans < 0.32:
                    self.dusen_nesneler.append(BadItem(x, hiz, gorsel=self.bomba_img))
                else:
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

            # Kaçırılan elma kontrolü (ekran dışına çıktı ve yakalanmadı)
            if nesne.y > EKRAN_YUKSEKLIK and isinstance(nesne, (GoodItem, GoldenItem)):
                self.kombo_sayac = 0
                self.kombo_carpan = 1
                continue

            if sepet_rect.colliderect(nesne.dikdortgen_al()):
                nesne.aktif = False

                px = nesne.x + nesne.genislik // 2
                py = nesne.y + nesne.yukseklik // 2

                if isinstance(nesne, MermiItem):
                    # Boss'a hasar ver
                    if self.boss_aktif and self.boss and self.boss.aktif:
                        self.boss.hasar_al()
                        if self.boss_ses:
                            self.boss_ses.play()
                    self.parcacik_yonetici.patlama_ekle(px, py, ACIK_MAVI, 15)
                    self.sepet.squash_baslat()

                elif isinstance(nesne, GoldenItem):
                    kazanilan = nesne.puan * self.kombo_carpan
                    self.skor += kazanilan
                    self.toplanan_elma_sayisi += 1
                    self.toplanan_altin_sayisi += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, ALTIN, 25)
                    self.sepet.squash_baslat()
                    self._kombo_artir()

                elif isinstance(nesne, HealItem):
                    if self.can < MAKS_CAN:
                        self.can += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, ACIK_YESIL, 20)
                    self.sepet.squash_baslat()

                elif isinstance(nesne, GoodItem):
                    kazanilan = nesne.puan * self.kombo_carpan
                    self.skor += kazanilan
                    self.toplanan_elma_sayisi += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, YESIL, 15)
                    self.sepet.squash_baslat()
                    self._kombo_artir()

                elif isinstance(nesne, (BadItem, BossBomba)):
                    eski_can = self.can
                    self.can -= 1
                    self.hasar_alindi = True
                    if self.bomba_ses:
                        self.bomba_ses.play()
                    self.parcacik_yonetici.patlama_ekle(px, py, TURUNCU, 20)
                    self.ekran_sarsintisi.baslat()
                    # Kombo sıfırla
                    self.kombo_sayac = 0
                    self.kombo_carpan = 1
                    # Kalp kırılma efekti
                    if eski_can > self.can:
                        kalp_idx = self.can
                        kalp_x = EKRAN_GENISLIK - 40 - kalp_idx * 35
                        self.kalp_kirilmalari.append(
                            KalpKirilma(kalp_x, 8, self.kalp_img)
                        )

        # Boss bombaları ile sepet çarpışması
        for bomba in self.boss_bombalar:
            if not bomba.aktif:
                continue
            if sepet_rect.colliderect(bomba.dikdortgen_al()):
                bomba.aktif = False
                eski_can = self.can
                self.can -= 1
                self.hasar_alindi = True
                if self.bomba_ses:
                    self.bomba_ses.play()
                px = int(bomba.x + 10)
                py = int(bomba.y + 10)
                self.parcacik_yonetici.patlama_ekle(px, py, TURUNCU, 20)
                self.ekran_sarsintisi.baslat()
                self.kombo_sayac = 0
                self.kombo_carpan = 1
                if eski_can > self.can:
                    kalp_idx = self.can
                    kalp_x = EKRAN_GENISLIK - 40 - kalp_idx * 35
                    self.kalp_kirilmalari.append(
                        KalpKirilma(kalp_x, 8, self.kalp_img)
                    )

    def _kombo_artir(self):
        """Kombo sayacını artırır ve çarpanı günceller."""
        self.kombo_sayac += 1
        if self.kombo_sayac >= 10:
            self.kombo_carpan = 5
            if self.kombo_sayac == 10:
                self.duyurular.append(Duyuru("UNSTOPPABLE!", ALTIN, 90))
                if self.kombo_ses:
                    self.kombo_ses.play()
        elif self.kombo_sayac >= 5:
            self.kombo_carpan = 2
            if self.kombo_sayac == 5:
                self.duyurular.append(Duyuru("COMBO!", SARI, 75, EKRAN_YUKSEKLIK // 3 + 40))
                if self.kombo_ses:
                    self.kombo_ses.play()
        else:
            self.kombo_carpan = 1

        # Kombo barı doldur (%20 oranında dolar, 10 toplamada bar dolar)
        self.kombo_bar = min(1.0, self.kombo_bar + 0.1)

        # Bar dolduysa Fever mode başlat
        if self.kombo_bar >= 1.0 and not self.fever_aktif:
            self.fever_aktif = True
            self.fever_kalan_kare = 300  # 5 saniye
            self.kombo_bar = 1.0

    # -------------------------------------------------------------------------
    # Görev (Achievement) Kontrol
    # -------------------------------------------------------------------------
    def _gorev_kontrol(self):
        """Görevleri kontrol edip tamamlananları veritabanına kaydeder."""
        # 50 Elma Topla
        if self.toplanan_elma_sayisi >= 50:
            if not self.veritabani.gorev_tamamlandi_mi("50_elma"):
                self.veritabani.gorev_tamamla("50_elma")
                self.gorev_bildirimleri.append(GorevBildirimi(GOREV_TANIMLARI["50_elma"]))
                if self.gorev_ses:
                    self.gorev_ses.play()

        # Hiç Can Kaybetmeden 1000 Puan
        if self.skor >= 1000 and not self.hasar_alindi:
            if not self.veritabani.gorev_tamamlandi_mi("1000_hasarsiz"):
                self.veritabani.gorev_tamamla("1000_hasarsiz")
                self.gorev_bildirimleri.append(GorevBildirimi(GOREV_TANIMLARI["1000_hasarsiz"]))
                if self.gorev_ses:
                    self.gorev_ses.play()

        # Tek Oyunda 5 Altın Elma
        if self.toplanan_altin_sayisi >= 5:
            if not self.veritabani.gorev_tamamlandi_mi("5_altin"):
                self.veritabani.gorev_tamamla("5_altin")
                self.gorev_bildirimleri.append(GorevBildirimi(GOREV_TANIMLARI["5_altin"]))
                if self.gorev_ses:
                    self.gorev_ses.play()

    # -------------------------------------------------------------------------
    # Arka Plan Çizimi
    # -------------------------------------------------------------------------
    def _arkaplan_ciz(self, hedef=None):
        """Paralaks katmanlı arka plan çizer."""
        ekran = hedef or self.ekran
        # Gradyan gökyüzü
        fever_mod = getattr(self, 'fever_aktif', False)
        for y in range(EKRAN_YUKSEKLIK):
            oran = y / EKRAN_YUKSEKLIK
            if fever_mod:
                # Fever: kırmızımsı parlak
                pulse = abs(math.sin(getattr(self, 'fever_parlama', 0) * 0.05)) * 30
                r = int(60 + 100 * oran + pulse)
                g = int(20 + 60 * oran)
                b = int(60 + 80 * oran + pulse * 0.5)
            else:
                r = int(30 + 100 * oran)
                g = int(30 + 140 * oran)
                b = int(80 + 120 * oran)
            pygame.draw.line(ekran, (min(255, r), min(255, g), min(255, b)),
                             (0, y), (EKRAN_GENISLIK, y))

        # Paralaks katmanları
        for katman in self.paralaks_katmanlar:
            katman.ciz(ekran, fever_mod)

        # Zemin (yeşil çimen)
        zemin_y = EKRAN_YUKSEKLIK - 30
        zemin_renk = (60, 30, 40) if fever_mod else KOYU_YESIL
        cimen_renk = (100, 50, 60) if fever_mod else YESIL
        pygame.draw.rect(ekran, zemin_renk, (0, zemin_y, EKRAN_GENISLIK, 30))
        pygame.draw.rect(ekran, cimen_renk, (0, zemin_y, EKRAN_GENISLIK, 5))

    # -------------------------------------------------------------------------
    # HUD (Skor, Can, Zorluk Göstergesi)
    # -------------------------------------------------------------------------
    def _hud_ciz(self, hedef=None):
        """Ekranın üstünde skor, can, kombo ve fever bilgisini gösterir."""
        ekran = hedef or self.ekran
        # Yarı saydam üst panel
        panel = pygame.Surface((EKRAN_GENISLIK, 45), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        ekran.blit(panel, (0, 0))

        # Skor (kombo çarpanı ile)
        if self.kombo_carpan > 1:
            skor_yazi = self.orta_font.render(f"Skor: {self.skor} (x{self.kombo_carpan})", True, ALTIN)
        else:
            skor_yazi = self.orta_font.render(f"Skor: {self.skor}", True, BEYAZ)
        ekran.blit(skor_yazi, (15, 8))

        # Zorluk seviyesi
        zorluk_yazi = self.kucuk_font.render(f"Seviye: {self.zorluk_seviyesi}", True, ACIK_MAVI)
        ekran.blit(zorluk_yazi, (250, 12))

        # Kombo barı
        bar_x, bar_y, bar_w, bar_h = 360, 14, 100, 16
        pygame.draw.rect(ekran, KOYU_GRI, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        doluluk = int(bar_w * self.kombo_bar)
        if doluluk > 0:
            bar_renk = ALTIN if self.fever_aktif else TURUNCU
            pygame.draw.rect(ekran, bar_renk, (bar_x, bar_y, doluluk, bar_h), border_radius=4)
        pygame.draw.rect(ekran, BEYAZ, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        kombo_label = self.mini_font.render("FEVER" if self.fever_aktif else f"Kombo: {self.kombo_sayac}", True, BEYAZ)
        ekran.blit(kombo_label, (bar_x + bar_w + 5, bar_y - 1))

        # Fever modu göstergesi
        if self.fever_aktif:
            kalan_sn = self.fever_kalan_kare / 60.0
            fever_txt = self.kucuk_font.render(f"★ FEVER MODE {kalan_sn:.1f}s ★", True, ALTIN)
            ekran.blit(fever_txt, (EKRAN_GENISLIK // 2 - fever_txt.get_width() // 2, 48))

        # Canlar (kalp görseli veya geometrik kalp)
        for i in range(self.can):
            kalp_x = EKRAN_GENISLIK - 40 - i * 35
            kalp_y = 8
            if self.kalp_img:
                ekran.blit(self.kalp_img, (kalp_x - 5, kalp_y))
            else:
                pygame.draw.circle(ekran, KIRMIZI, (kalp_x, kalp_y + 5), 8)
                pygame.draw.circle(ekran, KIRMIZI, (kalp_x + 10, kalp_y + 5), 8)
                pygame.draw.polygon(ekran, KIRMIZI, [
                    (kalp_x - 8, kalp_y + 6),
                    (kalp_x + 18, kalp_y + 6),
                    (kalp_x + 5, kalp_y + 22)
                ])

        # Kalp kırılma efektleri
        for kk in self.kalp_kirilmalari:
            kk.ciz(ekran)

        # Boss durumu göstergesi
        if self.boss_aktif and self.boss:
            boss_txt = self.orta_font.render("💀 BOSS FIGHT!", True, KIRMIZI)
            ekran.blit(boss_txt, (EKRAN_GENISLIK // 2 - boss_txt.get_width() // 2, 48))
        elif self.gece_modu:
            gece_txt = self.mini_font.render("🌙 Gece Modu", True, (150, 150, 200))
            ekran.blit(gece_txt, (10, 48))

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
        buton_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 435, 240, 50)
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

        # Market butonu
        market_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 100, 495, 200, 40)
        if market_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, ALTIN, market_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (160, 130, 20), market_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, market_rect, 2, border_radius=10)
        market_yazi = self.orta_font.render("🛒 Market", True, BEYAZ)
        self.ekran.blit(market_yazi,
                        (market_rect.centerx - market_yazi.get_width() // 2,
                         market_rect.centery - market_yazi.get_height() // 2))

        # Bakiye gösterimi
        bakiye = self.veritabani.bakiye_al()
        bakiye_yazi = self.kucuk_font.render(f"💰 Bakiye: {bakiye} puan", True, ALTIN)
        self.ekran.blit(bakiye_yazi, (EKRAN_GENISLIK // 2 - bakiye_yazi.get_width() // 2, 545))

        # ENTER ipucu
        enter_yazi = self.kucuk_font.render("ENTER: Başlat  |  M: Market", True, GRI)
        self.ekran.blit(enter_yazi, (EKRAN_GENISLIK // 2 - enter_yazi.get_width() // 2, 570))

        return buton_rect, market_rect

    # -------------------------------------------------------------------------
    # Market Ekranı
    # -------------------------------------------------------------------------
    def _market_ciz(self):
        """Sepet renk marketi ekranını çizer."""
        self._arkaplan_ciz()

        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.ekran.blit(overlay, (0, 0))

        # Panel
        panel_rect = pygame.Rect(50, 40, EKRAN_GENISLIK - 100, EKRAN_YUKSEKLIK - 80)
        pygame.draw.rect(self.ekran, (25, 25, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, ALTIN, panel_rect, 2, border_radius=15)

        baslik = self.buyuk_font.render("🛒 Sepet Marketi", True, ALTIN)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 60))

        bakiye = self.veritabani.bakiye_al()
        bakiye_yazi = self.orta_font.render(f"💰 Bakiye: {bakiye} puan", True, BEYAZ)
        self.ekran.blit(bakiye_yazi, (EKRAN_GENISLIK // 2 - bakiye_yazi.get_width() // 2, 105))

        satin_alinanlar = self.veritabani.satin_alinan_sepetler()
        aktif = self.veritabani.aktif_sepet_al()
        fare = pygame.mouse.get_pos()

        buton_rects = {}
        y_baslangic = 150
        for idx, (renk_adi, bilgi) in enumerate(SEPET_RENKLERI.items()):
            y = y_baslangic + idx * 75
            kart = pygame.Rect(100, y, EKRAN_GENISLIK - 200, 65)
            pygame.draw.rect(self.ekran, (40, 40, 70), kart, border_radius=10)
            if kart.collidepoint(fare):
                pygame.draw.rect(self.ekran, ACIK_MAVI, kart, 2, border_radius=10)
            else:
                pygame.draw.rect(self.ekran, GRI, kart, 1, border_radius=10)

            # Sepet önizleme (küçük dikdörtgen)
            preview = pygame.Rect(120, y + 12, 40, 25)
            pygame.draw.rect(self.ekran, bilgi["renk"], preview, border_radius=4)
            pygame.draw.rect(self.ekran, bilgi["ic"], pygame.Rect(124, y + 16, 32, 17), border_radius=3)

            isim_yazi = self.orta_font.render(renk_adi.capitalize(), True, BEYAZ)
            self.ekran.blit(isim_yazi, (180, y + 18))

            # Durum butonu
            if renk_adi == aktif:
                durum_yazi = self.kucuk_font.render("✓ Aktif", True, ACIK_YESIL)
                self.ekran.blit(durum_yazi, (EKRAN_GENISLIK - 230, y + 22))
            elif renk_adi in satin_alinanlar:
                sec_rect = pygame.Rect(EKRAN_GENISLIK - 250, y + 15, 100, 35)
                pygame.draw.rect(self.ekran, KOYU_YESIL, sec_rect, border_radius=6)
                sec_yazi = self.kucuk_font.render("Seç", True, BEYAZ)
                self.ekran.blit(sec_yazi,
                                (sec_rect.centerx - sec_yazi.get_width() // 2,
                                 sec_rect.centery - sec_yazi.get_height() // 2))
                buton_rects[renk_adi] = ("sec", sec_rect)
            else:
                al_rect = pygame.Rect(EKRAN_GENISLIK - 270, y + 15, 120, 35)
                yeterli = bakiye >= bilgi["fiyat"]
                renk = TURUNCU if yeterli else KOYU_GRI
                pygame.draw.rect(self.ekran, renk, al_rect, border_radius=6)
                fiyat_yazi = self.kucuk_font.render(f"🔒 {bilgi['fiyat']}p", True, BEYAZ if yeterli else GRI)
                self.ekran.blit(fiyat_yazi,
                                (al_rect.centerx - fiyat_yazi.get_width() // 2,
                                 al_rect.centery - fiyat_yazi.get_height() // 2))
                if yeterli:
                    buton_rects[renk_adi] = ("al", al_rect)

        # Geri butonu
        geri_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 80, EKRAN_YUKSEKLIK - 65, 160, 40)
        if geri_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, MAVI, geri_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (40, 80, 160), geri_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, geri_rect, 2, border_radius=10)
        geri_yazi = self.orta_font.render("← Geri", True, BEYAZ)
        self.ekran.blit(geri_yazi,
                        (geri_rect.centerx - geri_yazi.get_width() // 2,
                         geri_rect.centery - geri_yazi.get_height() // 2))

        return buton_rects, geri_rect

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
                            if self.durum in ("oyun", "bitti", "market"):
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

                        if olay.key == pygame.K_m and self.durum == "menu":
                            self.durum = "market"

                if olay.type == pygame.MOUSEBUTTONDOWN and olay.button == 1:
                    if self.durum == "menu":
                        basla_buton = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 435, 240, 50)
                        market_buton = pygame.Rect(EKRAN_GENISLIK // 2 - 100, 495, 200, 40)
                        if basla_buton.collidepoint(olay.pos):
                            self._oyunu_sifirla()
                            self.durum = "oyun"
                        elif market_buton.collidepoint(olay.pos):
                            self.durum = "market"
                    elif self.durum == "bitti":
                        buton = pygame.Rect(EKRAN_GENISLIK // 2 - 130, 380, 260, 50)
                        if buton.collidepoint(olay.pos):
                            self._oyunu_sifirla()
                            self.durum = "oyun"
                    elif self.durum == "market":
                        buton_rects, geri_rect = self._market_ciz()
                        if geri_rect.collidepoint(olay.pos):
                            self.durum = "menu"
                        else:
                            for renk_adi, (islem, rect) in buton_rects.items():
                                if rect.collidepoint(olay.pos):
                                    if islem == "al":
                                        self.veritabani.sepet_satin_al(renk_adi)
                                    elif islem == "sec":
                                        self.veritabani.aktif_sepet_ayarla(renk_adi)
                                        self.aktif_sepet_renk = renk_adi
                                    break

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

            elif self.durum == "market":
                self._market_ciz()

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

        # Paralaks katmanları güncelle
        for katman in self.paralaks_katmanlar:
            katman.guncelle()

        # Kalp kırılma efektleri güncelle
        for kk in self.kalp_kirilmalari:
            kk.guncelle()
        self.kalp_kirilmalari = [kk for kk in self.kalp_kirilmalari if kk.aktif]

        # Fever modu zamanlayıcı
        if self.fever_aktif:
            self.fever_kalan_kare -= 1
            self.fever_parlama += 0.1
            if self.fever_kalan_kare <= 0:
                self.fever_aktif = False
                self.kombo_bar = 0.0

        # --- Gece/Gündüz döngüsü (her 1000 puanda bir değişir) ---
        self.gece_modu = (self.skor // 1000) % 2 == 1

        # --- Boss aktivasyonu (5000 puan) ---
        if self.skor >= 5000 and not self.boss_aktif and not self.boss_yenildi:
            self.boss_aktif = True
            self.boss = Boss()
            self.duyurular.append(Duyuru("BOSS FIGHT!", KIRMIZI, 120))

        # --- Boss güncelleme ---
        if self.boss_aktif and self.boss:
            self.boss.guncelle()
            # Boss bomba fırlatsın
            if self.boss.bomba_atabilir():
                bx = int(self.boss.x) + self.boss.genislik // 2
                by = int(self.boss.y) + self.boss.yukseklik
                hedef_x = self.sepet.x + self.sepet.base_genislik // 2
                hedef_y = self.sepet.y + self.sepet.base_yukseklik // 2
                self.boss_bombalar.append(BossBomba(bx, by, hedef_x, hedef_y))
            # Boss bombaları güncelle
            for b in self.boss_bombalar:
                b.guncelle()
            self.boss_bombalar = [b for b in self.boss_bombalar if b.aktif]
            # Boss öldü mü?
            if not self.boss.aktif:
                self.boss_aktif = False
                self.boss_yenildi = True
                self.skor += 500  # Boss ödülü
                self.boss_bombalar.clear()
                self.parcacik_yonetici.patlama_ekle(
                    int(self.boss.x) + 60, int(self.boss.y) + 40, ALTIN, 40)
                self.duyurular.append(Duyuru("BOSS DEFEATED!", ACIK_YESIL, 120))

        # --- Duyuruları güncelle ---
        for d in self.duyurular:
            d.guncelle()
        self.duyurular = [d for d in self.duyurular if d.aktif]

        # --- Görev bildirimlerini güncelle ---
        for g in self.gorev_bildirimleri:
            g.guncelle()
        self.gorev_bildirimleri = [g for g in self.gorev_bildirimleri if g.aktif]

        # --- Görev (Achievement) kontrol ---
        self._gorev_kontrol()

        # Can bittiyse oyunu bitir
        if self.can <= 0:
            self.can = 0
            self.son_skor = self.skor
            eski_en_yuksek = self.en_yuksek_skor
            self.en_yuksek_skor = self.veritabani.en_yuksek_skor()
            # Yeni rekor duyurusu
            if self.son_skor > eski_en_yuksek and self.son_skor > 0:
                self.duyurular.append(Duyuru("NEW RECORD!", ALTIN, 150))
                if self.rekor_ses:
                    self.rekor_ses.play()
            # Kazanılan skoru bakiyeye ekle
            if self.son_skor > 0:
                self.veritabani.bakiye_guncelle(self.son_skor)
            # Skor ilk 5'e giriyorsa isim sor
            if self.son_skor > 0 and self.veritabani.ilk_5e_girer_mi(self.son_skor):
                self.durum = "isim_gir"
            else:
                self.durum = "bitti"

    # -------------------------------------------------------------------------
    # Oyun Çizimi
    # -------------------------------------------------------------------------
    def _oyun_ciz(self):
        """Oyun ekranındaki tüm öğeleri çizer (ekran sarsıntısı destekli)."""
        hedef = self.oyun_surface
        hedef.fill(SIYAH)

        # Arka plan (paralaks)
        self._arkaplan_ciz(hedef=hedef)

        # Düşen nesneler
        for nesne in self.dusen_nesneler:
            nesne.ciz(hedef)

        # Boss bombalar
        for bomba in self.boss_bombalar:
            bomba.ciz(hedef)

        # Boss
        if self.boss_aktif and self.boss:
            self.boss.ciz(hedef)

        # Sepet
        self.sepet.ciz(hedef)

        # Parçacık efektleri
        self.parcacik_yonetici.ciz(hedef)

        # --- Gece modu overlay + spotlight ---
        if self.gece_modu:
            self.gece_surface.fill((0, 0, 0, 160))
            # Spotlight: sepet etrafında aydınlık daire
            sepet_cx = self.sepet.x + self.sepet.base_genislik // 2
            sepet_cy = self.sepet.y + self.sepet.base_yukseklik // 2
            isik = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            pygame.draw.circle(isik, (0, 0, 0, 160), (sepet_cx, sepet_cy), self.isik_yaricap)
            self.gece_surface.blit(isik, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            hedef.blit(self.gece_surface, (0, 0))

        # HUD (skor, can vb.) - gece katmanının üstünde
        self._hud_ciz(hedef=hedef)

        # Duyurular (Announcer)
        for d in self.duyurular:
            d.ciz(hedef, self.buyuk_font)

        # Görev bildirimleri
        for g in self.gorev_bildirimleri:
            g.ciz(hedef, self.buyuk_font, self.kucuk_font)

        # Ekran sarsıntısı offseti ile ana ekrana blit
        ox, oy = self.ekran_sarsintisi.offset_al()
        self.ekran.fill(SIYAH)
        self.ekran.blit(hedef, (ox, oy))


# =============================================================================
# PROGRAMIN GİRİŞ NOKTASI
# =============================================================================
if __name__ == "__main__":
    oyun = GameManager()
    oyun.calistir()
