# =============================================================================
# PARTICLES — Parçacık Efekt Sistemi
# =============================================================================
import pygame
import random


class Particle:
    """Çarpışma efektleri için küçük renkli kare parçacık."""
    _surf_cache = {}

    def __init__(self, x, y, renk):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, -1)
        self.boyut = random.randint(3, 7)
        self.renk = renk
        self.omur = random.randint(25, 50)
        self.max_omur = self.omur
        self.aktif = True

    def guncelle(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.omur -= 1
        if self.omur <= 0:
            self.aktif = False

    def ciz(self, ekran):
        if not self.aktif:
            return
        oran = self.omur / self.max_omur
        boyut = max(1, int(self.boyut * oran))
        alpha = int(255 * oran)
        anahtar = boyut
        if anahtar not in Particle._surf_cache:
            Particle._surf_cache[anahtar] = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        surf = Particle._surf_cache[anahtar].copy()
        surf.fill((*self.renk[:3], alpha))
        ekran.blit(surf, (int(self.x), int(self.y)))


class ParticleManager:
    """Tüm parçacıkları yöneten sınıf. Maks 200 parçacık sınırı."""
    MAKS_PARCACIK = 200

    def __init__(self):
        self.parcaciklar = []

    def patlama_ekle(self, x, y, renk, adet=15):
        bos_yer = ParticleManager.MAKS_PARCACIK - len(self.parcaciklar)
        ekle = min(adet, bos_yer)
        for _ in range(ekle):
            self.parcaciklar.append(Particle(x, y, renk))

    def guncelle(self):
        for p in self.parcaciklar:
            p.guncelle()
        self.parcaciklar = [p for p in self.parcaciklar if p.aktif]

    def ciz(self, ekran):
        for p in self.parcaciklar:
            p.ciz(ekran)
