# =============================================================================
# DIFFICULTY — Dinamik Zorluk Motoru
# =============================================================================
from collections import deque


class DinamikZorlukMotoru:
    """Oyuncunun performansına göre zorluk parametrelerini optimize eder."""
    PENCERE_BOYUTU = 60

    def __init__(self):
        self.toplam_uretilen = 0
        self.toplam_yakalanan = 0
        self.toplam_kacirilan = 0
        self.pencere = deque(maxlen=self.PENCERE_BOYUTU)
        self.kacirma_orani = 0.0
        self.ruzgar_carpan = 1.0
        self.hiz_carpan = 1.0
        self.son_guncelleme = 0

    def nesne_yakalandi(self):
        self.toplam_yakalanan += 1
        self.toplam_uretilen += 1
        self.pencere.append(True)

    def nesne_kacirildi(self):
        self.toplam_kacirilan += 1
        self.toplam_uretilen += 1
        self.pencere.append(False)

    def guncelle(self):
        if len(self.pencere) < 10:
            return
        kacirilan = sum(1 for x in self.pencere if not x)
        self.kacirma_orani = kacirilan / len(self.pencere)
        if self.kacirma_orani > 0.60:
            self.hiz_carpan = max(0.7, 1.0 - (self.kacirma_orani - 0.60) * 1.5)
            self.ruzgar_carpan = max(0.4, 1.0 - (self.kacirma_orani - 0.60) * 2.0)
        elif self.kacirma_orani < 0.15:
            self.hiz_carpan = min(1.5, 1.0 + (0.15 - self.kacirma_orani) * 3.0)
            self.ruzgar_carpan = min(1.8, 1.0 + (0.15 - self.kacirma_orani) * 4.0)
        else:
            self.hiz_carpan += (1.0 - self.hiz_carpan) * 0.05
            self.ruzgar_carpan += (1.0 - self.ruzgar_carpan) * 0.05

    def hiz_al(self, temel_hiz):
        return temel_hiz * self.hiz_carpan

    def ruzgar_siddeti_al(self, temel_siddet):
        return temel_siddet * self.ruzgar_carpan

    def sifirla(self):
        self.toplam_uretilen = 0
        self.toplam_yakalanan = 0
        self.toplam_kacirilan = 0
        self.pencere.clear()
        self.kacirma_orani = 0.0
        self.ruzgar_carpan = 1.0
        self.hiz_carpan = 1.0
