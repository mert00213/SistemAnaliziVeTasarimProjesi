# =============================================================================
# PARALLAX — Paralaks Arka Plan Katmanları
# =============================================================================
import pygame
from settings import EKRAN_GENISLIK, EKRAN_YUKSEKLIK, KAHVERENGI


class ParalaksKatman:
    """Yatay kayan tek arka plan katmanı."""
    def __init__(self, hiz, gorsel=None, cizim_fonk=None):
        self.hiz = hiz
        self.offset = 0.0
        self.gorsel = gorsel
        self.cizim_fonk = cizim_fonk

    def guncelle(self):
        self.offset = (self.offset + self.hiz) % EKRAN_GENISLIK

    def ciz(self, ekran, fever_aktif=False, ruzgar_siddet=0.0):
        if self.gorsel:
            ekran.blit(self.gorsel, (-self.offset, 0))
            ekran.blit(self.gorsel, (EKRAN_GENISLIK - self.offset, 0))
        elif self.cizim_fonk:
            try:
                self.cizim_fonk(ekran, self.offset, fever_aktif, ruzgar_siddet)
            except TypeError:
                self.cizim_fonk(ekran, self.offset, fever_aktif)


def bulut_ciz(ekran, offset, fever_aktif, ruzgar_siddet=0.0):
    """Geometrik bulut katmanı çizer."""
    renk = (255, 200, 220) if fever_aktif else (220, 230, 245)
    bulutlar = [(100, 60, 60), (350, 40, 45), (600, 70, 55), (850, 50, 40)]
    for bx, by, br in bulutlar:
        x = (bx - offset) % (EKRAN_GENISLIK + 100) - 50
        pygame.draw.ellipse(ekran, renk, (int(x), by, br * 2, br))
        pygame.draw.ellipse(ekran, renk, (int(x) + br // 2, by - br // 3, int(br * 1.5), int(br * 0.8)))
        pygame.draw.ellipse(ekran, renk, (int(x) - br // 3, by + br // 5, int(br * 1.3), int(br * 0.7)))


def dag_ciz(ekran, offset, fever_aktif, ruzgar_siddet=0.0):
    """Geometrik dağ / ağaç katmanı çizer. Ağaçlar rüzgara göre sallanır."""
    dag_renk = (70, 50, 90) if fever_aktif else (50, 70, 50)
    agac_renk = (60, 110, 50) if fever_aktif else (30, 80, 30)
    daglar = [(0, 120), (200, 100), (400, 140), (600, 110), (800, 130)]
    for dx, dh in daglar:
        x = (dx - offset * 2) % (EKRAN_GENISLIK + 200) - 100
        noktalar = [(int(x), EKRAN_YUKSEKLIK - 30),
                     (int(x) + 80, EKRAN_YUKSEKLIK - 30 - dh),
                     (int(x) + 160, EKRAN_YUKSEKLIK - 30)]
        pygame.draw.polygon(ekran, dag_renk, noktalar)
    if ruzgar_siddet is None:
        ruzgar_siddet = 0.0
    sallanma = max(-6, min(6, ruzgar_siddet * 2.0))
    agaclar = [(50, 35), (250, 28), (450, 40), (650, 32), (850, 38)]
    for ax, ah in agaclar:
        x = int((ax - offset * 2) % (EKRAN_GENISLIK + 100) - 50)
        govde = pygame.Rect(x + 8, EKRAN_YUKSEKLIK - 30 - ah, 6, ah)
        pygame.draw.rect(ekran, KAHVERENGI, govde)
        tepe_x = x + 11 + int(sallanma)
        pygame.draw.polygon(ekran, agac_renk,
                            [(x, EKRAN_YUKSEKLIK - 30 - ah),
                             (tepe_x, EKRAN_YUKSEKLIK - 30 - ah - 25),
                             (x + 22, EKRAN_YUKSEKLIK - 30 - ah)])
