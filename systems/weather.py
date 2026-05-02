# =============================================================================
# WEATHER — Rüzgar ve Yağmur Sistemleri
# =============================================================================
import pygame
import random
from settings import EKRAN_GENISLIK, EKRAN_YUKSEKLIK, ACIK_MAVI


class RuzgarSistemi:
    """Rastgele yön değiştiren rüzgar sistemi."""
    def __init__(self):
        self.siddet = 0.0
        self.hedef = 0.0
        self.degisim_sayaci = 0
        self.degisim_araliği = 180

    def guncelle(self):
        self.degisim_sayaci += 1
        if self.degisim_sayaci >= self.degisim_araliği:
            self.degisim_sayaci = 0
            self.hedef = random.uniform(-2.0, 2.0)
            self.degisim_araliği = random.randint(120, 300)
        self.siddet += (self.hedef - self.siddet) * 0.02
        self.siddet = max(-3.0, min(3.0, self.siddet))

    def ciz(self, ekran, font):
        if self.siddet is None:
            self.siddet = 0.0
        self.siddet = max(-10.0, min(10.0, float(self.siddet)))
        ok_x = int(EKRAN_GENISLIK // 2)
        ok_y = int(EKRAN_YUKSEKLIK - 18)
        uzunluk = int(self.siddet * 15)
        uzunluk = max(-(EKRAN_GENISLIK // 2 - 20), min(EKRAN_GENISLIK // 2 - 20, uzunluk))
        if abs(uzunluk) > 3:
            renk = ACIK_MAVI
            end_x = max(0, min(EKRAN_GENISLIK, int(ok_x + uzunluk)))
            pygame.draw.line(ekran, renk, (int(ok_x), int(ok_y)), (int(end_x), int(ok_y)), 2)
            yon = 1 if uzunluk > 0 else -1
            pygame.draw.polygon(ekran, renk, [
                (int(end_x), int(ok_y)),
                (int(end_x - yon * 6), int(ok_y - 4)),
                (int(end_x - yon * 6), int(ok_y + 4))])
        txt = font.render(f"Rüzgar: {self.siddet:+.1f}", True, ACIK_MAVI)
        ekran.blit(txt, (int(ok_x - txt.get_width() // 2), int(ok_y - 16)))


class YagmurSistemi:
    """Yağmur parçacık efekti ve kaygan zemin kontrolü."""
    def __init__(self):
        self.aktif = False
        self.damlalar = []
        self.zamanlayici = 0
        self.sure = 0
        self.bekleme = 0

    def guncelle(self):
        self.zamanlayici += 1
        if not self.aktif:
            self.bekleme -= 1
            if self.bekleme <= 0:
                self.aktif = True
                self.sure = random.randint(600, 1200)
                self.bekleme = 0
        else:
            self.sure -= 1
            if self.sure <= 0:
                self.aktif = False
                self.bekleme = random.randint(900, 1800)
            if len(self.damlalar) < 60:
                self.damlalar.append([
                    random.randint(0, EKRAN_GENISLIK),
                    random.randint(-20, 0),
                    random.uniform(6, 10)])
        yeni = []
        for d in self.damlalar:
            d[1] += d[2]
            if d[1] < EKRAN_YUKSEKLIK:
                yeni.append(d)
        self.damlalar = yeni

    def ciz(self, ekran):
        if not self.aktif:
            return
        for d in self.damlalar:
            pygame.draw.line(ekran, (120, 160, 220),
                             (int(d[0]), int(d[1])),
                             (int(d[0]) - 1, int(d[1]) + 6), 1)
