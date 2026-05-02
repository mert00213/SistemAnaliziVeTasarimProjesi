# =============================================================================
# GHOST — Hayalet Sepet ve Tekrar İzleme Sistemi
# =============================================================================
import pygame
import json
from collections import deque


class ReplayFrame:
    """Tek bir oyun karesinin anlık görüntüsünü saklayan veri yapısı."""
    __slots__ = ['sepet_x', 'nesneler', 'skor', 'can', 'kombo', 'fever']

    def __init__(self, sepet_x, nesneler, skor, can, kombo, fever):
        self.sepet_x = sepet_x
        self.nesneler = nesneler
        self.skor = skor
        self.can = can
        self.kombo = kombo
        self.fever = fever


class ReplaySystem:
    """Oyunun son 10 saniyesini kaydeder. Deque ile sabit bellek."""
    MAKS_KARE = 600

    def __init__(self):
        self.kareler = deque(maxlen=self.MAKS_KARE)
        self.oynatma_indeks = 0
        self.oynatiliyor = False

    def kare_kaydet(self, sepet, dusen_nesneler, skor, can, kombo, fever):
        nesne_listesi = []
        for n in dusen_nesneler:
            if n.aktif:
                tip = type(n).__name__
                nesne_listesi.append((n.x, n.y, n.genislik, n.yukseklik, tip))
        frame = ReplayFrame(sepet.x, nesne_listesi, skor, can, kombo, fever)
        self.kareler.append(frame)

    def oynatma_baslat(self):
        self.oynatma_indeks = 0
        self.oynatiliyor = True

    def oynatma_durdur(self):
        self.oynatiliyor = False
        self.oynatma_indeks = 0

    def sonraki_kare(self):
        if self.oynatma_indeks >= len(self.kareler):
            self.oynatiliyor = False
            return None
        kare = self.kareler[self.oynatma_indeks]
        self.oynatma_indeks += 1
        return kare

    def sifirla(self):
        self.kareler.clear()
        self.oynatma_indeks = 0
        self.oynatiliyor = False


class GhostSepet:
    """En yüksek skorlu oyunun sepet hareketlerini kaydeder ve şeffaf gösterir."""
    def __init__(self):
        self.hareketler = []
        self.aktif = False
        self.kare_sayaci = 0

    def hareketi_kaydet(self, kare_no, x):
        self.hareketler.append((kare_no, x))

    def pozisyon_al(self, kare_no):
        if not self.hareketler or kare_no >= len(self.hareketler):
            return None
        return self.hareketler[kare_no][1]

    def ciz(self, ekran, kare_no, sepet_genislik, sepet_yukseklik, y_poz):
        x = self.pozisyon_al(kare_no)
        if x is None:
            return
        ghost_surf = pygame.Surface((sepet_genislik, sepet_yukseklik), pygame.SRCALPHA)
        ghost_surf.fill((100, 180, 255, 70))
        pygame.draw.rect(ghost_surf, (150, 200, 255, 100),
                         (5, 10, sepet_genislik - 10, sepet_yukseklik - 15), border_radius=4)
        pygame.draw.rect(ghost_surf, (200, 230, 255, 120),
                         (0, 0, sepet_genislik, sepet_yukseklik), 2, border_radius=6)
        ekran.blit(ghost_surf, (x, y_poz))
        etiket_font = pygame.font.SysFont("Arial", 10)
        etiket = etiket_font.render("GHOST", True, (150, 200, 255))
        etiket_alpha = pygame.Surface(etiket.get_size(), pygame.SRCALPHA)
        etiket_alpha.blit(etiket, (0, 0))
        etiket_alpha.set_alpha(100)
        ekran.blit(etiket_alpha, (x + sepet_genislik // 2 - etiket.get_width() // 2, y_poz - 12))

    def veriyi_json_al(self):
        return json.dumps(self.hareketler)

    @staticmethod
    def json_den_yukle(json_str):
        ghost = GhostSepet()
        try:
            ghost.hareketler = json.loads(json_str)
            ghost.aktif = len(ghost.hareketler) > 0
        except (json.JSONDecodeError, TypeError):
            ghost.hareketler = []
            ghost.aktif = False
        return ghost
