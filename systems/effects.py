# =============================================================================
# EFFECTS — Ekran Efektleri (Sarsıntı, Kalp Kırılma, Duyuru, Görev)
# =============================================================================
import pygame
import random
import math
from settings import EKRAN_GENISLIK, EKRAN_YUKSEKLIK, KIRMIZI, ALTIN, BEYAZ


class EkranSarsintisi:
    """Bombaya çarpınca veya can gidince ekran titremesi."""
    def __init__(self):
        self.sure = 0
        self.max_sure = 0
        self.siddet = 0

    def baslat(self, sure_kare=18, siddet=10):
        self.sure = sure_kare
        self.max_sure = sure_kare
        self.siddet = siddet

    def offset_al(self):
        if self.sure <= 0:
            return 0, 0
        self.sure -= 1
        oran = self.sure / max(1, self.max_sure)
        gercek_siddet = max(1, int(self.siddet * oran))
        x = random.randint(-gercek_siddet, gercek_siddet)
        y = random.randint(-gercek_siddet, gercek_siddet)
        return x, y


class KalpKirilma:
    """Can gittiğinde kalbin kırılarak yok olma animasyonu."""
    def __init__(self, x, y, kalp_img=None):
        self.x = float(x)
        self.y = float(y)
        self.kalp_img = kalp_img
        self.parcalar = []
        self.omur = 40
        self.aktif = True
        for _ in range(4):
            self.parcalar.append({
                "dx": random.uniform(-3, 3), "dy": random.uniform(-4, -1),
                "boyut": random.randint(5, 10), "renk": KIRMIZI,
            })

    def guncelle(self):
        self.omur -= 1
        if self.omur <= 0:
            self.aktif = False
            return
        for p in self.parcalar:
            self.x += p["dx"] * 0.1
            p["dy"] += 0.12

    def ciz(self, ekran):
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


class GorevBildirimi:
    """Görev tamamlandığında havalı 'GOAL!' bildirimi."""
    def __init__(self, gorev_ismi):
        self.gorev_ismi = gorev_ismi
        self.sure = 180
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
