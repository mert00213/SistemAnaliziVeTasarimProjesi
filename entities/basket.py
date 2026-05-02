# =============================================================================
# BASKET — Oyuncu Sepeti
# =============================================================================
import pygame
import math
from settings import EKRAN_GENISLIK, EKRAN_YUKSEKLIK, SEPET_RENKLERI, KAHVERENGI


class Basket:
    """Oyuncunun klavye ile kontrol ettiği sepet nesnesi."""

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
        renk_bilgi = SEPET_RENKLERI.get(renk_adi, SEPET_RENKLERI["kahverengi"])
        self.renk = renk_bilgi["renk"]
        self.ic_renk = renk_bilgi["ic"]
        self.kenar_renk = renk_bilgi["kenar"]
        self._ss_timer = 0
        self._ss_aktif = False

    def squash_baslat(self):
        self._ss_timer = 12
        self._ss_aktif = True

    def hareket_et(self, tuslar, kaygan_zemin=False):
        if not hasattr(self, '_momentum'):
            self._momentum = 0.0
        hedef = 0.0
        if tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]:
            hedef -= self.hiz
        if tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]:
            hedef += self.hiz
        if kaygan_zemin:
            self._momentum += (hedef - self._momentum) * 0.12
        else:
            self._momentum = hedef
        self.x += self._momentum
        self.x = max(0, min(EKRAN_GENISLIK - self.genislik, self.x))
        if self._ss_aktif:
            self._ss_timer -= 1
            if self._ss_timer <= 0:
                self._ss_aktif = False
                self.genislik = self.base_genislik
                self.yukseklik = self.base_yukseklik
            else:
                t = self._ss_timer / 12.0
                if t > 0.5:
                    s = math.sin((1.0 - t) * math.pi)
                    self.genislik = int(self.base_genislik * (1.0 + s * 0.15))
                    self.yukseklik = int(self.base_yukseklik * (1.0 - s * 0.12))
                else:
                    s = math.sin(t * math.pi)
                    self.genislik = int(self.base_genislik * (1.0 - s * 0.08))
                    self.yukseklik = int(self.base_yukseklik * (1.0 + s * 0.1))
            if self.base_gorsel:
                self.gorsel = pygame.transform.scale(self.base_gorsel, (self.genislik, self.yukseklik))

    def ciz(self, ekran):
        cx_offset = (self.base_genislik - self.genislik) // 2
        cy_offset = (self.base_yukseklik - self.yukseklik)
        draw_x = self.x + cx_offset
        draw_y = self.y + cy_offset
        if self.gorsel:
            ekran.blit(self.gorsel, (draw_x, draw_y))
            return
        govde = pygame.Rect(draw_x, draw_y + 10, self.genislik, self.yukseklik - 10)
        pygame.draw.rect(ekran, self.renk, govde, border_radius=6)
        ic = pygame.Rect(draw_x + 5, draw_y + 14, self.genislik - 10, self.yukseklik - 20)
        pygame.draw.rect(ekran, self.ic_renk, ic, border_radius=4)
        pygame.draw.polygon(ekran, self.renk, [(draw_x - 8, draw_y + 10), (draw_x, draw_y + 10), (draw_x + 8, draw_y)])
        pygame.draw.polygon(ekran, self.renk, [(draw_x + self.genislik + 8, draw_y + 10), (draw_x + self.genislik, draw_y + 10), (draw_x + self.genislik - 8, draw_y)])
        pygame.draw.line(ekran, self.kenar_renk, (draw_x - 8, draw_y + 10), (draw_x + self.genislik + 8, draw_y + 10), 3)
        for i in range(1, 3):
            y_cizgi = draw_y + 10 + i * (self.yukseklik - 10) // 3
            pygame.draw.line(ekran, self.kenar_renk, (draw_x + 2, y_cizgi), (draw_x + self.genislik - 2, y_cizgi), 1)

    def dikdortgen_al(self):
        return pygame.Rect(self.x, self.y, self.base_genislik, self.base_yukseklik)
