# =============================================================================
# SPECIAL ITEMS — Özel Nesneler (Güdümlü Bomba, Hırsız Kuş)
# =============================================================================
import pygame
import math
import random
from settings import (EKRAN_GENISLIK, EKRAN_YUKSEKLIK, PEMBE, KIRMIZI,
                       BEYAZ, SARI, SIYAH, KAHVERENGI)
from entities.falling_items import FallingItem, GoodItem, GoldenItem


class TakipBomba(FallingItem):
    """Düşerken sepetin X konumuna doğru hafifçe yönelen bomba."""
    def __init__(self, x, hiz, gorsel=None):
        super().__init__(x, -40, 30, 30, hiz * 0.85, PEMBE)
        self.gorsel = gorsel
        self._sayac = 0

    def guncelle(self, sepet_x=None, **kwargs):
        self._sayac += 1
        self.y += self.hiz
        if sepet_x is not None:
            fark = sepet_x - self.x
            self.x += max(-0.8, min(0.8, fark * 0.008))
        self.x = max(0, min(EKRAN_GENISLIK - self.genislik, self.x))
        if self.y > EKRAN_YUKSEKLIK:
            self.aktif = False

    def ciz(self, ekran):
        cx = int(self.x + self.genislik // 2)
        cy = int(self.y + self.yukseklik // 2)
        r = self.genislik // 2
        parlama = abs(math.sin(self._sayac * 0.12)) * 3
        pygame.draw.circle(ekran, (200, 50, 100), (cx, cy), int(r + parlama))
        pygame.draw.circle(ekran, PEMBE, (cx, cy), r - 2)
        pygame.draw.circle(ekran, BEYAZ, (cx - 3, cy - 3), 4)
        pygame.draw.line(ekran, KIRMIZI, (cx - 6, cy), (cx + 6, cy), 2)
        pygame.draw.line(ekran, KIRMIZI, (cx, cy - 6), (cx, cy + 6), 2)


class HirsizKus:
    """Yandan uçarak gelen ve düşen elmaları kapmaya çalışan kuş."""
    def __init__(self):
        self.genislik = 28
        self.yukseklik = 20
        if random.random() < 0.5:
            self.x = float(-self.genislik)
            self.vx = random.uniform(2.0, 3.5)
        else:
            self.x = float(EKRAN_GENISLIK)
            self.vx = random.uniform(-3.5, -2.0)
        self.y = float(random.randint(60, EKRAN_YUKSEKLIK // 2))
        self.aktif = True
        self._kanat = 0
        self.hedef_elma = None

    def guncelle(self, dusen_nesneler):
        self._kanat += 1
        self.x += self.vx
        if self.x < -80 or self.x > EKRAN_GENISLIK + 80:
            self.aktif = False
            return
        min_dist = 999999
        en_yakin = None
        for nesne in dusen_nesneler:
            if isinstance(nesne, (GoodItem, GoldenItem)) and nesne.aktif:
                dist = abs(nesne.x - self.x) + abs(nesne.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    en_yakin = nesne
        self.hedef_elma = en_yakin
        if self.hedef_elma and self.hedef_elma.aktif:
            fark_y = self.hedef_elma.y - self.y
            self.y += max(-2.0, min(2.0, fark_y * 0.04))
            fark_x = self.hedef_elma.x - self.x
            self.x += max(-1.0, min(1.0, fark_x * 0.03))
            if abs(self.x - self.hedef_elma.x) < 20 and abs(self.y - self.hedef_elma.y) < 20:
                self.hedef_elma.aktif = False
                self.hedef_elma = None

    def ciz(self, ekran):
        if not self.aktif:
            return
        ix, iy = int(self.x), int(self.y)
        yon = 1 if self.vx > 0 else -1
        pygame.draw.ellipse(ekran, (80, 60, 40), (ix, iy + 4, self.genislik, self.yukseklik - 6))
        kanat_y = int(math.sin(self._kanat * 0.25) * 6)
        pygame.draw.polygon(ekran, (100, 80, 50), [
            (ix + 14, iy + 8), (ix + 14 + yon * 10, iy + kanat_y), (ix + 14 + yon * 4, iy + 10)])
        gaga_x = ix + (self.genislik if yon > 0 else 0)
        pygame.draw.polygon(ekran, SARI, [(gaga_x, iy + 10), (gaga_x + yon * 8, iy + 12), (gaga_x, iy + 14)])
        goz_x = ix + (self.genislik - 6 if yon > 0 else 6)
        pygame.draw.circle(ekran, BEYAZ, (goz_x, iy + 8), 3)
        pygame.draw.circle(ekran, SIYAH, (goz_x, iy + 8), 1)

    def dikdortgen_al(self):
        return pygame.Rect(int(self.x), int(self.y), self.genislik, self.yukseklik)
