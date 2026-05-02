# =============================================================================
# FALLING ITEMS — Düşen Nesnelerin Sınıf Hiyerarşisi
# =============================================================================
"""
Oyunda yukarıdan aşağı düşen tüm nesnelerin temel sınıfı ve türevleri.
Kalıtım (inheritance) ile ortak davranışlar paylaşılır, her türev
kendi çizim ve puan mantığına sahiptir.
"""

import pygame
import math
import random
from settings import (
    EKRAN_GENISLIK, EKRAN_YUKSEKLIK,
    KIRMIZI, SIYAH, KOYU_GRI, KAHVERENGI, KOYU_YESIL,
    TURUNCU, SARI, ALTIN, BEYAZ, ACIK_YESIL, YESIL,
)


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

    def guncelle(self, ruzgar_siddet=0, yercekim_carpan=1.0):
        """Nesneyi her karede aşağı doğru hareket ettirir (rüzgar + yerçekimi)."""
        self.y += self.hiz * yercekim_carpan

        # Rüzgar güvenlik kontrolü
        if ruzgar_siddet is None:
            ruzgar_siddet = 0
        ruzgar_siddet = float(ruzgar_siddet)

        # Yatay hız hesapla: rüzgar çarpanı 0.25
        x_hizi = ruzgar_siddet * 0.25

        # Velocity clamping: yatay hız asla ±5'i geçemez
        x_hizi = max(-5.0, min(5.0, x_hizi))

        # Kenar sönümleme: nesne kenara yaklaştıkça rüzgar etkisi azalır
        kenar_esik = 80.0
        kenar_mesafe_sol = max(0.0, self.x)
        kenar_mesafe_sag = max(0.0, EKRAN_GENISLIK - self.genislik - self.x)
        if x_hizi < 0 and kenar_mesafe_sol < kenar_esik:
            x_hizi *= kenar_mesafe_sol / kenar_esik
        elif x_hizi > 0 and kenar_mesafe_sag < kenar_esik:
            x_hizi *= kenar_mesafe_sag / kenar_esik

        self.x += x_hizi

        # Ekran sınırı: taşarsa geri it
        if self.x < 0:
            self.x = 0
        elif self.x > EKRAN_GENISLIK - self.genislik:
            self.x = EKRAN_GENISLIK - self.genislik

        # Ekranın altına ulaştıysa pasif yap
        if self.y > EKRAN_YUKSEKLIK:
            self.aktif = False

    def ciz(self, ekran):
        """Temel çizim metodu - alt sınıflar bunu override eder."""
        pygame.draw.rect(ekran, self.renk, (self.x, self.y, self.genislik, self.yukseklik))

    def dikdortgen_al(self):
        """Çarpışma tespiti için Rect nesnesi döndürür."""
        return pygame.Rect(self.x, self.y, self.genislik, self.yukseklik)


class GoodItem(FallingItem):
    """
    Toplandığında oyuncuya puan kazandıran nesne.
    Şekil olarak kırmızı bir elma çizilir.
    """

    def __init__(self, x, hiz, gorsel=None):
        super().__init__(x, -40, 34, 34, hiz, KIRMIZI)
        self.puan = 10
        self.gorsel = gorsel

    def ciz(self, ekran):
        """Elma görselini veya geometrik şeklini ekrana çizer."""
        if self.gorsel:
            ekran.blit(self.gorsel, (self.x, self.y))
            return

        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        pygame.draw.circle(ekran, KIRMIZI, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, (255, 100, 100), (merkez_x - 5, merkez_y - 4), yaricap // 3)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 3, merkez_y - yaricap - 8), 3)
        yaprak_rect = pygame.Rect(merkez_x + 2, merkez_y - yaricap - 10, 10, 6)
        pygame.draw.ellipse(ekran, KOYU_YESIL, yaprak_rect)


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

        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        pygame.draw.circle(ekran, KOYU_GRI, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, SIYAH, (merkez_x, merkez_y + 2), yaricap - 3)
        pygame.draw.circle(ekran, (80, 80, 80), (merkez_x - 5, merkez_y - 3), yaricap // 4)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 4, merkez_y - yaricap - 10), 3)
        pygame.draw.circle(ekran, TURUNCU, (merkez_x + 4, merkez_y - yaricap - 12), 4)
        pygame.draw.circle(ekran, SARI, (merkez_x + 4, merkez_y - yaricap - 12), 2)


class GoldenItem(FallingItem):
    """
    Nadir düşen, hızlı hareket eden altın elma.
    Yakalanınca 100 puan kazandırır.
    """

    def __init__(self, x, hiz):
        super().__init__(x, -40, 34, 34, hiz * 1.8, ALTIN)
        self.puan = 100
        self._parlama_sayac = 0

    def guncelle(self, ruzgar_siddet=0, yercekim_carpan=1.0):
        """Altın elmayı hareket ettirir ve parlama sayacını artırır."""
        super().guncelle(ruzgar_siddet, yercekim_carpan)
        self._parlama_sayac += 1

    def ciz(self, ekran):
        """Altın elma - Surface tabanlı parlama efekti ile çizer."""
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        parlama_alpha = int(80 + abs(math.sin(self._parlama_sayac * 0.08)) * 100)
        glow_r = yaricap * 3
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, parlama_alpha // 2),
                           (glow_r, glow_r), glow_r)
        pygame.draw.circle(glow_surf, (255, 230, 80, parlama_alpha),
                           (glow_r, glow_r), glow_r // 2)
        ekran.blit(glow_surf, (merkez_x - glow_r, merkez_y - glow_r))

        parlama = abs(math.sin(self._parlama_sayac * 0.1)) * 4
        pygame.draw.circle(ekran, (255, 255, 150),
                           (merkez_x, merkez_y + 2), int(yaricap + parlama))
        pygame.draw.circle(ekran, ALTIN, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, (255, 240, 100), (merkez_x - 4, merkez_y - 3), yaricap // 3)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 3, merkez_y - yaricap - 8), 3)
        yildiz_font = pygame.font.SysFont("Arial", 14, bold=True)
        yildiz = yildiz_font.render("★", True, BEYAZ)
        ekran.blit(yildiz, (merkez_x - 6, merkez_y - 8))


class HealItem(FallingItem):
    """
    Çok nadir düşen can paketi.
    Yakalanınca mevcut canı +1 artırır (maksimum MAKS_CAN).
    """

    def __init__(self, x, hiz):
        super().__init__(x, -40, 30, 30, hiz * 0.8, ACIK_YESIL)
        self._parlama_sayac = 0

    def guncelle(self, ruzgar_siddet=0, yercekim_carpan=1.0):
        """Can paketini hareket ettirir ve parlama sayacını artırır."""
        super().guncelle(ruzgar_siddet, yercekim_carpan)
        self._parlama_sayac += 1

    def ciz(self, ekran):
        """Yeşil artı (+) şeklinde can paketi çizer."""
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2

        parlama = abs(math.sin(self._parlama_sayac * 0.08)) * 3
        pygame.draw.circle(ekran, (150, 255, 200),
                           (merkez_x, merkez_y), int(self.genislik // 2 + parlama))
        pygame.draw.circle(ekran, BEYAZ, (merkez_x, merkez_y), self.genislik // 2)
        pygame.draw.circle(ekran, ACIK_YESIL, (merkez_x, merkez_y), self.genislik // 2, 2)

        kalinlik = 6
        pygame.draw.rect(ekran, YESIL,
                         (merkez_x - kalinlik // 2, merkez_y - 8, kalinlik, 16))
        pygame.draw.rect(ekran, YESIL,
                         (merkez_x - 8, merkez_y - kalinlik // 2, 16, kalinlik))
