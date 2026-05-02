# =============================================================================
# BOSS — Boss Savaş Sistemi
# =============================================================================
import pygame
import math
from settings import (EKRAN_GENISLIK, EKRAN_YUKSEKLIK, KOYU_KIRMIZI, SARI,
                       SIYAH, BEYAZ, KOYU_GRI, YESIL, KIRMIZI, TURUNCU, ACIK_MAVI)
from entities.falling_items import FallingItem


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
        ix, iy = int(self.x), int(self.y)
        cx, cy = ix + self.genislik // 2, iy + self.yukseklik // 2
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
            pygame.draw.polygon(ekran, (100, 20, 30), [(sx - 5, iy + 5), (sx, iy - 15), (sx + 5, iy + 5)])
        bar_w, bar_x, bar_y = self.genislik, ix, iy - 15
        pygame.draw.rect(ekran, KOYU_GRI, (bar_x, bar_y, bar_w, 8), border_radius=3)
        oran = self.can / self.max_can
        can_renk = YESIL if oran > 0.5 else SARI if oran > 0.25 else KIRMIZI
        pygame.draw.rect(ekran, can_renk, (bar_x, bar_y, int(bar_w * oran), 8), border_radius=3)
        pygame.draw.rect(ekran, BEYAZ, (bar_x, bar_y, bar_w, 8), 1, border_radius=3)

    def dikdortgen_al(self):
        return pygame.Rect(int(self.x), int(self.y), self.genislik, self.yukseklik)


class BossBomba(FallingItem):
    """Boss'un oyuncuya doğru fırlattığı çapraz bomba."""
    def __init__(self, x, y, hedef_x, hedef_y):
        super().__init__(x, y, 20, 20, 0, TURUNCU)
        dx, dy = hedef_x - x, hedef_y - y
        uzunluk = max(1, math.sqrt(dx * dx + dy * dy))
        self.vx = dx / uzunluk * 4.5
        self.vy = dy / uzunluk * 4.5
        self._sayac = 0

    def guncelle(self, ruzgar_siddet=0, yercekim_carpan=1.0):
        self.x += self.vx
        self.y += self.vy
        self._sayac += 1
        if (self.y > EKRAN_YUKSEKLIK + 50 or self.y < -50 or
                self.x < -50 or self.x > EKRAN_GENISLIK + 50):
            self.aktif = False

    def ciz(self, ekran):
        if not self.aktif:
            return
        cx, cy = int(self.x + 10), int(self.y + 10)
        parlama = abs(math.sin(self._sayac * 0.15)) * 3
        pygame.draw.circle(ekran, (255, 100, 0), (cx, cy), int(10 + parlama))
        pygame.draw.circle(ekran, SARI, (cx, cy), 6)
        pygame.draw.circle(ekran, BEYAZ, (cx, cy), 3)


class MermiItem(FallingItem):
    """Boss savaşında düşen mermi - toplayınca boss'a hasar verir."""
    def __init__(self, x, hiz):
        super().__init__(x, -30, 24, 24, hiz, ACIK_MAVI)
        self._sayac = 0

    def guncelle(self, ruzgar_siddet=0, yercekim_carpan=1.0):
        super().guncelle(ruzgar_siddet, yercekim_carpan)
        self._sayac += 1

    def ciz(self, ekran):
        cx, cy = int(self.x + 12), int(self.y + 12)
        parlama = abs(math.sin(self._sayac * 0.1)) * 2
        pygame.draw.circle(ekran, (100, 200, 255), (cx, cy), int(12 + parlama))
        pygame.draw.circle(ekran, BEYAZ, (cx, cy), 8)
        pygame.draw.circle(ekran, ACIK_MAVI, (cx, cy), 5)
        pygame.draw.polygon(ekran, BEYAZ, [(cx - 3, cy + 2), (cx, cy - 5), (cx + 3, cy + 2)])
