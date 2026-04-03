# =============================================================================
# SEPET OYUNU (Catching Game) - Pygame ile 2D Oyun
# =============================================================================
# Kurulum ve Çalıştırma (VS Code terminali):
#   pip install pygame
#   python sepet_oyunu.py
# =============================================================================

import pygame
import random
import sys
import os
import math
import sqlite3
import json
import time
from collections import deque

# --- Pygame başlatma ---
pygame.init()
pygame.mixer.init()

# =============================================================================
# SABITLER
# =============================================================================
EKRAN_GENISLIK = 800
EKRAN_YUKSEKLIK = 600
FPS = 60

# Renkler
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
KIRMIZI = (220, 40, 40)
YESIL = (50, 180, 50)
MAVI = (40, 100, 220)
SARI = (255, 220, 0)
TURUNCU = (255, 140, 0)
GRI = (180, 180, 180)
KOYU_GRI = (60, 60, 60)
ACIK_MAVI = (135, 206, 235)
KAHVERENGI = (139, 90, 43)
KOYU_YESIL = (34, 120, 34)
PEMBE = (255, 105, 180)
ALTIN = (255, 215, 0)
ACIK_YESIL = (0, 255, 127)

# Dosya yolları
OYUN_KLASORU = os.path.dirname(os.path.abspath(__file__))
SKOR_DOSYASI = os.path.join(OYUN_KLASORU, "skor.txt")
VERITABANI_YOLU = os.path.join(OYUN_KLASORU, "skorlar.db")
MAKS_CAN = 3

# Sepet renk seçenekleri (Market sistemi)
SEPET_RENKLERI = {
    "kahverengi": {"renk": (139, 90, 43), "ic": (180, 120, 60), "kenar": (100, 60, 20), "fiyat": 0},
    "kirmizi":    {"renk": (180, 40, 40), "ic": (220, 80, 80), "kenar": (120, 20, 20), "fiyat": 500},
    "mavi":       {"renk": (40, 80, 180), "ic": (80, 120, 220), "kenar": (20, 50, 130), "fiyat": 500},
    "mor":        {"renk": (130, 40, 180), "ic": (170, 80, 220), "kenar": (90, 20, 130), "fiyat": 1000},
    "altin":      {"renk": (200, 170, 40), "ic": (240, 210, 80), "kenar": (160, 130, 20), "fiyat": 2000},
}

# Görev (Achievement) tanımları
GOREV_TANIMLARI = {
    "50_elma": "50 Elma Topla",
    "1000_hasarsiz": "Hiç Can Kaybetmeden 1000 Puan",
    "5_altin": "Tek Oyunda 5 Altın Elma Yakala",
}
KOYU_KIRMIZI = (140, 20, 30)

# Geliştirme (Upgrade) tanımları
UPGRADE_TANIMLARI = {
    "sepet_hizi":    {"isim": "Sepet Hızı",     "maks_seviye": 5, "baz_fiyat": 300,  "artis": 200},
    "miknatıs_sure": {"isim": "Mıknatıs Süresi", "maks_seviye": 5, "baz_fiyat": 400,  "artis": 250},
    "ekstra_can":    {"isim": "Ekstra Can",      "maks_seviye": 3, "baz_fiyat": 600,  "artis": 400},
}

# Bölge (Biome) tanımları
BOLGE_TANIMLARI = [
    {"isim": "Orman",  "dosya": "orman.png",  "yercekim": 1.0, "zemin": KOYU_YESIL,  "cimen": YESIL,
     "gokyuzu": (30, 100, 30)},
    {"isim": "Çöl",    "dosya": "col.png",    "yercekim": 1.15, "zemin": (180, 140, 60), "cimen": (200, 170, 80),
     "gokyuzu": (100, 70, 20)},
    {"isim": "Buz",    "dosya": "buz.png",    "yercekim": 0.95, "zemin": (180, 200, 220), "cimen": (200, 220, 240),
     "gokyuzu": (40, 60, 100)},
    {"isim": "Uzay",   "dosya": "uzay.png",   "yercekim": 0.6,  "zemin": (40, 20, 60),   "cimen": (60, 30, 80),
     "gokyuzu": (5, 5, 20)},
]


# =============================================================================
# SINIF: ParalaksKatman (Paralaks Arka Plan Katmanı)
# =============================================================================
class ParalaksKatman:
    """Yatay kayan tek arka plan katmanı."""

    def __init__(self, hiz, gorsel=None, cizim_fonk=None):
        self.hiz = hiz
        self.offset = 0.0
        self.gorsel = gorsel
        self.cizim_fonk = cizim_fonk  # Görsel yoksa fallback çizim

    def guncelle(self):
        """Katmanı yatay olarak kaydırır."""
        self.offset = (self.offset + self.hiz) % EKRAN_GENISLIK

    def ciz(self, ekran, fever_aktif=False, ruzgar_siddet=0.0):
        """Katmanı çizer (görsel veya geometrik fallback)."""
        if self.gorsel:
            ekran.blit(self.gorsel, (-self.offset, 0))
            ekran.blit(self.gorsel, (EKRAN_GENISLIK - self.offset, 0))
        elif self.cizim_fonk:
            try:
                self.cizim_fonk(ekran, self.offset, fever_aktif, ruzgar_siddet)
            except TypeError:
                self.cizim_fonk(ekran, self.offset, fever_aktif)


def _bulut_ciz(ekran, offset, fever_aktif):
    """Geometrik bulut katmanı çizer."""
    renk = (255, 200, 220) if fever_aktif else (220, 230, 245)
    bulutlar = [(100, 60, 60), (350, 40, 45), (600, 70, 55), (850, 50, 40)]
    for bx, by, br in bulutlar:
        x = (bx - offset) % (EKRAN_GENISLIK + 100) - 50
        pygame.draw.ellipse(ekran, renk, (int(x), by, br * 2, br))
        pygame.draw.ellipse(ekran, renk, (int(x) + br // 2, by - br // 3, int(br * 1.5), int(br * 0.8)))
        pygame.draw.ellipse(ekran, renk, (int(x) - br // 3, by + br // 5, int(br * 1.3), int(br * 0.7)))


def _dag_ciz(ekran, offset, fever_aktif, ruzgar_siddet=0.0):
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
    # Rüzgar sallanma miktarı (±6 piksel maks, rüzgara orantılı)
    if ruzgar_siddet is None:
        ruzgar_siddet = 0.0
    sallanma = max(-6, min(6, ruzgar_siddet * 2.0))
    agaclar = [(50, 35), (250, 28), (450, 40), (650, 32), (850, 38)]
    for ax, ah in agaclar:
        x = int((ax - offset * 2) % (EKRAN_GENISLIK + 100) - 50)
        govde = pygame.Rect(x + 8, EKRAN_YUKSEKLIK - 30 - ah, 6, ah)
        pygame.draw.rect(ekran, KAHVERENGI, govde)
        # Ağaç tepesi rüzgarla sallansın
        tepe_x = x + 11 + int(sallanma)
        pygame.draw.polygon(ekran, agac_renk,
                            [(x, EKRAN_YUKSEKLIK - 30 - ah),
                             (tepe_x, EKRAN_YUKSEKLIK - 30 - ah - 25),
                             (x + 22, EKRAN_YUKSEKLIK - 30 - ah)])


# =============================================================================
# SINIF: EkranSarsintisi (Screen Shake)
# =============================================================================
class EkranSarsintisi:
    """Bombaya çarpınca veya can gidince ekran titremesi (0.3s decay)."""

    def __init__(self):
        self.sure = 0
        self.max_sure = 0
        self.siddet = 0

    def baslat(self, sure_kare=18, siddet=10):
        """Sarsıntı başlatır (varsayılan 0.3 saniye, 60 FPS)."""
        self.sure = sure_kare
        self.max_sure = sure_kare
        self.siddet = siddet

    def offset_al(self):
        """Bu karedeki x,y kayma miktarını azalan şiddetle döndürür."""
        if self.sure <= 0:
            return 0, 0
        self.sure -= 1
        oran = self.sure / max(1, self.max_sure)
        gercek_siddet = max(1, int(self.siddet * oran))
        x = random.randint(-gercek_siddet, gercek_siddet)
        y = random.randint(-gercek_siddet, gercek_siddet)
        return x, y


# =============================================================================
# SINIF: ReplayFrame (Tekrar İzleme Kare Verisi)
# =============================================================================
class ReplayFrame:
    """Tek bir oyun karesinin anlık görüntüsünü saklayan veri yapısı."""
    __slots__ = ['sepet_x', 'nesneler', 'skor', 'can', 'kombo', 'fever']

    def __init__(self, sepet_x, nesneler, skor, can, kombo, fever):
        self.sepet_x = sepet_x
        self.nesneler = nesneler  # [(x, y, tip_str), ...]
        self.skor = skor
        self.can = can
        self.kombo = kombo
        self.fever = fever


# =============================================================================
# SINIF: ReplaySystem (Tekrar İzleme Sistemi)
# =============================================================================
class ReplaySystem:
    """
    Oyunun son 10 saniyesini (600 kare @ 60 FPS) kaydeder.
    Oyun bitince 'Tekrar İzle' moduyla bu kareleri canlandırır.
    Deque veri yapısı ile sabit bellek kullanımı sağlanır.
    """
    MAKS_KARE = 600  # 10 saniye @ 60 FPS

    def __init__(self):
        self.kareler = deque(maxlen=self.MAKS_KARE)
        self.oynatma_indeks = 0
        self.oynatiliyor = False

    def kare_kaydet(self, sepet, dusen_nesneler, skor, can, kombo, fever):
        """Mevcut kareyi kayıt listesine ekler."""
        nesne_listesi = []
        for n in dusen_nesneler:
            if n.aktif:
                tip = type(n).__name__
                nesne_listesi.append((n.x, n.y, n.genislik, n.yukseklik, tip))
        frame = ReplayFrame(sepet.x, nesne_listesi, skor, can, kombo, fever)
        self.kareler.append(frame)

    def oynatma_baslat(self):
        """Tekrar izleme modunu başlatır."""
        self.oynatma_indeks = 0
        self.oynatiliyor = True

    def oynatma_durdur(self):
        """Tekrar izleme modunu durdurur."""
        self.oynatiliyor = False
        self.oynatma_indeks = 0

    def sonraki_kare(self):
        """Sıradaki kareyi döndürür. Bitince None döner."""
        if self.oynatma_indeks >= len(self.kareler):
            self.oynatiliyor = False
            return None
        kare = self.kareler[self.oynatma_indeks]
        self.oynatma_indeks += 1
        return kare

    def sifirla(self):
        """Kayıtları temizler."""
        self.kareler.clear()
        self.oynatma_indeks = 0
        self.oynatiliyor = False


# =============================================================================
# SINIF: GhostSepet (Hayalet Sepet - En İyi Skor Yarışması)
# =============================================================================
class GhostSepet:
    """
    En yüksek skorlu oyunun sepet hareketlerini kaydeden ve
    yeni oyunda şeffaf bir 'Hayalet Sepet' olarak gösteren sınıf.
    """

    def __init__(self):
        self.hareketler = []      # [(kare_no, x_pozisyon), ...]
        self.aktif = False
        self.kare_sayaci = 0

    def hareketi_kaydet(self, kare_no, x):
        """Sepet pozisyonunu kayıt listesine ekler."""
        self.hareketler.append((kare_no, x))

    def pozisyon_al(self, kare_no):
        """Belirli bir karedeki ghost sepet X pozisyonunu döndürür."""
        if not self.hareketler or kare_no >= len(self.hareketler):
            return None
        return self.hareketler[kare_no][1]

    def ciz(self, ekran, kare_no, sepet_genislik, sepet_yukseklik, y_poz):
        """Şeffaf hayalet sepeti ekrana çizer."""
        x = self.pozisyon_al(kare_no)
        if x is None:
            return
        ghost_surf = pygame.Surface((sepet_genislik, sepet_yukseklik), pygame.SRCALPHA)
        # Yarı saydam mavi-beyaz tonlarında sepet
        ghost_surf.fill((100, 180, 255, 70))
        pygame.draw.rect(ghost_surf, (150, 200, 255, 100),
                         (5, 10, sepet_genislik - 10, sepet_yukseklik - 15), border_radius=4)
        pygame.draw.rect(ghost_surf, (200, 230, 255, 120),
                         (0, 0, sepet_genislik, sepet_yukseklik), 2, border_radius=6)
        ekran.blit(ghost_surf, (x, y_poz))
        # "GHOST" etiketi
        etiket_font = pygame.font.SysFont("Arial", 10)
        etiket = etiket_font.render("GHOST", True, (150, 200, 255))
        etiket_alpha = pygame.Surface(etiket.get_size(), pygame.SRCALPHA)
        etiket_alpha.blit(etiket, (0, 0))
        etiket_alpha.set_alpha(100)
        ekran.blit(etiket_alpha, (x + sepet_genislik // 2 - etiket.get_width() // 2, y_poz - 12))

    def veriyi_json_al(self):
        """Ghost verilerini JSON-serileştirilebilir formata dönüştürür."""
        return json.dumps(self.hareketler)

    @staticmethod
    def json_den_yukle(json_str):
        """JSON string'den ghost verilerini yükler."""
        ghost = GhostSepet()
        try:
            ghost.hareketler = json.loads(json_str)
            ghost.aktif = len(ghost.hareketler) > 0
        except (json.JSONDecodeError, TypeError):
            ghost.hareketler = []
            ghost.aktif = False
        return ghost


# =============================================================================
# SINIF: DinamikZorlukMotoru (Dynamic Difficulty Engine)
# =============================================================================
class DinamikZorlukMotoru:
    """
    Oyuncunun performansına göre (kaçırma oranı) rüzgar şiddetini
    ve nesne hızlarını anlık olarak optimize eden algoritma.
    Kayar pencere (sliding window) ile son 60 nesneyi takip eder.
    """
    PENCERE_BOYUTU = 60  # Son 60 nesne üzerinden hesaplama

    def __init__(self):
        self.toplam_uretilen = 0
        self.toplam_yakalanan = 0
        self.toplam_kacirilan = 0
        # Kayar pencere: True=yakalandı, False=kaçırıldı
        self.pencere = deque(maxlen=self.PENCERE_BOYUTU)
        self.kacirma_orani = 0.0        # 0.0 - 1.0
        self.ruzgar_carpan = 1.0        # Rüzgar şiddeti çarpanı
        self.hiz_carpan = 1.0           # Nesne hızı çarpanı
        self.son_guncelleme = 0

    def nesne_yakalandi(self):
        """Bir nesne yakalandığında çağrılır."""
        self.toplam_yakalanan += 1
        self.toplam_uretilen += 1
        self.pencere.append(True)

    def nesne_kacirildi(self):
        """Bir nesne kaçırıldığında çağrılır."""
        self.toplam_kacirilan += 1
        self.toplam_uretilen += 1
        self.pencere.append(False)

    def guncelle(self):
        """
        Kaçırma oranına göre zorluk parametrelerini optimize eder.
        - Yüksek kaçırma oranı (>%50): Zorluk azalır (yavaş hız, düşük rüzgar)
        - Düşük kaçırma oranı (<%20): Zorluk artar (hızlı nesneler, güçlü rüzgar)
        - Orta bant (%20-%50): Normal zorluk
        """
        if len(self.pencere) < 10:
            return  # Yeterli veri yok

        # Kaçırma oranı hesapla (kayar pencere)
        kacirilan = sum(1 for x in self.pencere if not x)
        self.kacirma_orani = kacirilan / len(self.pencere)

        # Zorluk eğrisi (sigmoid benzeri yumuşak geçiş)
        if self.kacirma_orani > 0.60:
            # Oyuncu zorlanıyor: kolaylaştır
            self.hiz_carpan = max(0.7, 1.0 - (self.kacirma_orani - 0.60) * 1.5)
            self.ruzgar_carpan = max(0.4, 1.0 - (self.kacirma_orani - 0.60) * 2.0)
        elif self.kacirma_orani < 0.15:
            # Oyuncu çok iyi: zorlaştır
            self.hiz_carpan = min(1.5, 1.0 + (0.15 - self.kacirma_orani) * 3.0)
            self.ruzgar_carpan = min(1.8, 1.0 + (0.15 - self.kacirma_orani) * 4.0)
        else:
            # Normal bant: yumuşak geçiş
            self.hiz_carpan += (1.0 - self.hiz_carpan) * 0.05
            self.ruzgar_carpan += (1.0 - self.ruzgar_carpan) * 0.05

    def hiz_al(self, temel_hiz):
        """Dinamik zorluk çarpanıyla düzeltilmiş hız döndürür."""
        return temel_hiz * self.hiz_carpan

    def ruzgar_siddeti_al(self, temel_siddet):
        """Dinamik zorluk çarpanıyla düzeltilmiş rüzgar şiddeti döndürür."""
        return temel_siddet * self.ruzgar_carpan

    def sifirla(self):
        """Tüm sayaçları sıfırlar."""
        self.toplam_uretilen = 0
        self.toplam_yakalanan = 0
        self.toplam_kacirilan = 0
        self.pencere.clear()
        self.kacirma_orani = 0.0
        self.ruzgar_carpan = 1.0
        self.hiz_carpan = 1.0


# =============================================================================
# SINIF: SkorAPIYoneticisi (Global API Score Manager)
# =============================================================================
class SkorAPIYoneticisi:
    """
    Skorları JSON formatında dışarıya aktaran ve hayali bir
    API'ye göndermeye hazır bir yapı sağlayan sınıf.
    requests kütüphanesi hazırlığı içerir.
    """
    API_URL = "https://api.sepetoyunu.example.com/v1/skorlar"

    def __init__(self, veritabani):
        self.veritabani = veritabani
        self._requests_mevcut = False
        try:
            import requests as _req
            self._requests_mevcut = True
        except ImportError:
            self._requests_mevcut = False

    def skor_json_olustur(self, isim, skor, seviye, sure_saniye, ekstra=None):
        """Tek bir skor kaydını JSON formatına dönüştürür."""
        veri = {
            "oyuncu": isim,
            "skor": skor,
            "seviye": seviye,
            "sure_saniye": round(sure_saniye, 2),
            "tarih": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "oyun_versiyon": "2.0",
            "platform": sys.platform,
        }
        if ekstra and isinstance(ekstra, dict):
            veri["ekstra"] = ekstra
        return veri

    def liderlik_tablosu_json(self):
        """Veritabanındaki top 5 skoru JSON formatında döndürür."""
        top5 = self.veritabani.en_iyi_5_al()
        sonuc = {
            "liderlik_tablosu": [
                {"sira": i + 1, "isim": isim, "skor": skor}
                for i, (isim, skor) in enumerate(top5)
            ],
            "guncelleme_tarihi": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "toplam_kayit": len(top5),
        }
        return sonuc

    def json_dosyaya_aktar(self, dosya_yolu=None):
        """Liderlik tablosunu JSON dosyasına aktarır."""
        if dosya_yolu is None:
            dosya_yolu = os.path.join(OYUN_KLASORU, "skorlar_export.json")
        veri = self.liderlik_tablosu_json()
        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                json.dump(veri, f, ensure_ascii=False, indent=2)
            return True, dosya_yolu
        except IOError as e:
            print(f"[UYARI] JSON dışa aktarma hatası: {e}")
            return False, None

    def api_ye_gonder(self, skor_verisi):
        """
        Skor verisini hayali API'ye gönderir.
        requests kütüphanesi yüklüyse gerçek HTTP isteği yapar,
        yoksa simüle eder ve sonucu döndürür.
        """
        json_payload = json.dumps(skor_verisi, ensure_ascii=False)

        if self._requests_mevcut:
            try:
                import requests
                yanit = requests.post(
                    self.API_URL,
                    data=json_payload,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                    timeout=5
                )
                return {
                    "basarili": yanit.status_code == 200,
                    "durum_kodu": yanit.status_code,
                    "yanit": yanit.text[:200],
                }
            except Exception as e:
                return {
                    "basarili": False,
                    "hata": str(e),
                    "not": "API bağlantısı kurulamadı"
                }
        else:
            # requests yüklü değil: simülasyon modu
            return {
                "basarili": True,
                "simülasyon": True,
                "gonderilen_veri": skor_verisi,
                "not": "requests kütüphanesi yüklü değil, simülasyon modu aktif. "
                       "'pip install requests' ile yükleyebilirsiniz.",
            }

    def toplu_aktar(self):
        """Tüm skorları JSON dosyasına aktarır ve API'ye gönderir."""
        basarili, yol = self.json_dosyaya_aktar()
        api_sonuc = self.api_ye_gonder(self.liderlik_tablosu_json())
        return {
            "dosya_aktarimi": {"basarili": basarili, "yol": yol},
            "api_sonucu": api_sonuc,
        }


# =============================================================================
# SINIF: KalpKirilma (Kalp Kırılma Efekti)
# =============================================================================
class KalpKirilma:
    """Can gittiğinde kalbin kırılarak yok olma animasyonu."""

    def __init__(self, x, y, kalp_img=None):
        self.x = float(x)
        self.y = float(y)
        self.kalp_img = kalp_img
        self.parcalar = []
        self.omur = 40
        self.aktif = True
        # 4 parça oluştur
        for _ in range(4):
            self.parcalar.append({
                "dx": random.uniform(-3, 3),
                "dy": random.uniform(-4, -1),
                "boyut": random.randint(5, 10),
                "renk": KIRMIZI,
            })

    def guncelle(self):
        """Parçaları hareket ettirir."""
        self.omur -= 1
        if self.omur <= 0:
            self.aktif = False
            return
        for p in self.parcalar:
            self.x += p["dx"] * 0.1
            p["dy"] += 0.12

    def ciz(self, ekran):
        """Kırılma parçalarını çizer."""
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


# =============================================================================
# SINIF: Duyuru (Announcer - Animasyonlu Bildirim)
# =============================================================================
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


# =============================================================================
# SINIF: GorevBildirimi (Achievement GOAL! Bildirimi)
# =============================================================================
class GorevBildirimi:
    """Görev tamamlandığında havalı 'GOAL!' bildirimi."""

    def __init__(self, gorev_ismi):
        self.gorev_ismi = gorev_ismi
        self.sure = 180  # 3 saniye
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


# =============================================================================
# SINIF: RuzgarSistemi (Wind System)
# =============================================================================
class RuzgarSistemi:
    """Rastgele yön değiştiren rüzgar sistemi."""

    def __init__(self):
        self.siddet = 0.0       # -3.0 .. +3.0  (negatif=sol, pozitif=sağ)
        self.hedef = 0.0
        self.degisim_sayaci = 0
        self.degisim_araliği = 180  # ~3 sn

    def guncelle(self):
        self.degisim_sayaci += 1
        if self.degisim_sayaci >= self.degisim_araliği:
            self.degisim_sayaci = 0
            self.hedef = random.uniform(-2.0, 2.0)
            self.degisim_araliği = random.randint(120, 300)
        # Yumuşak geçiş
        self.siddet += (self.hedef - self.siddet) * 0.02
        # Şiddet sınırı: asla ±3'ü geçemez
        self.siddet = max(-3.0, min(3.0, self.siddet))

    def ciz(self, ekran, font):
        """Rüzgar ok göstergesini çizer."""
        # Güvenlik: siddet None veya aşırı değer kontrolü
        if self.siddet is None:
            self.siddet = 0.0
        self.siddet = max(-10.0, min(10.0, float(self.siddet)))

        ok_x = int(EKRAN_GENISLIK // 2)
        ok_y = int(EKRAN_YUKSEKLIK - 18)
        # Ok uzunluğu rüzgar şiddetiyle orantılı
        uzunluk = int(self.siddet * 15)
        # Ekran sınırları içinde tut (clamp)
        uzunluk = max(-(EKRAN_GENISLIK // 2 - 20), min(EKRAN_GENISLIK // 2 - 20, uzunluk))
        if abs(uzunluk) > 3:
            renk = ACIK_MAVI
            end_x = int(ok_x + uzunluk)
            end_x = max(0, min(EKRAN_GENISLIK, end_x))
            pygame.draw.line(ekran, renk, (int(ok_x), int(ok_y)), (int(end_x), int(ok_y)), 2)
            yon = 1 if uzunluk > 0 else -1
            pygame.draw.polygon(ekran, renk, [
                (int(end_x), int(ok_y)),
                (int(end_x - yon * 6), int(ok_y - 4)),
                (int(end_x - yon * 6), int(ok_y + 4))])
        txt = font.render(f"Rüzgar: {self.siddet:+.1f}", True, ACIK_MAVI)
        ekran.blit(txt, (int(ok_x - txt.get_width() // 2), int(ok_y - 16)))


# =============================================================================
# SINIF: YagmurSistemi (Rain Effect)
# =============================================================================
class YagmurSistemi:
    """Yağmur parçacık efekti ve kaygan zemin kontrolü."""

    def __init__(self):
        self.aktif = False
        self.damlalar = []
        self.zamanlayici = 0
        self.sure = 0          # Yağmur kalan kare
        self.bekleme = 0       # Sonraki yağmura kalan kare

    def guncelle(self):
        self.zamanlayici += 1
        if not self.aktif:
            self.bekleme -= 1
            if self.bekleme <= 0:
                self.aktif = True
                self.sure = random.randint(600, 1200)  # 10-20 sn
                self.bekleme = 0
        else:
            self.sure -= 1
            if self.sure <= 0:
                self.aktif = False
                self.bekleme = random.randint(900, 1800)  # 15-30 sn
            # Yeni damla ekle (optimize: max 60)
            if len(self.damlalar) < 60:
                self.damlalar.append([
                    random.randint(0, EKRAN_GENISLIK),
                    random.randint(-20, 0),
                    random.uniform(6, 10)])
        # Damlaları güncelle
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


# =============================================================================
# SINIF: Particle (Parçacık Efekti)
# =============================================================================
class Particle:
    """Çarpışma efektleri için küçük renkli kare parçacık (optimize)."""
    # Önceden oluşturulmuş Surface havuzu (boyut -> Surface)
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
        """Parçacığı hareket ettirir ve ömrünü azaltır."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.omur -= 1
        if self.omur <= 0:
            self.aktif = False

    def ciz(self, ekran):
        """Parçacığı solarak çizer (Surface havuzlu)."""
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


# =============================================================================
# SINIF: ParticleManager (Parçacık Yöneticisi - Optimize)
# =============================================================================
class ParticleManager:
    """Tüm parçacıkları yöneten sınıf. Maks 200 parçacık sınırı."""
    MAKS_PARCACIK = 200

    def __init__(self):
        self.parcaciklar = []

    def patlama_ekle(self, x, y, renk, adet=15):
        """Belirtilen noktada parçacık patlaması oluşturur."""
        bos_yer = ParticleManager.MAKS_PARCACIK - len(self.parcaciklar)
        ekle = min(adet, bos_yer)
        for _ in range(ekle):
            self.parcaciklar.append(Particle(x, y, renk))

    def guncelle(self):
        """Tüm parçacıkları günceller ve ölüleri temizler."""
        for p in self.parcaciklar:
            p.guncelle()
        self.parcaciklar = [p for p in self.parcaciklar if p.aktif]

    def ciz(self, ekran):
        """Tüm parçacıkları çizer."""
        for p in self.parcaciklar:
            p.ciz(ekran)


# =============================================================================
# SINIF: FallingItem (Düşen Nesnelerin Temel Sınıfı)
# =============================================================================
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

        # Yatay hız hesapla: rüzgar çarpanı 0.25'e düşürüldü (eski: 0.5)
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

        # Ekran sınırı: taşarsa geri it ve hızı sıfırla
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


# =============================================================================
# SINIF: GoodItem (İyi Nesne - Elma)
# =============================================================================
class GoodItem(FallingItem):
    """
    Toplandığında oyuncuya puan kazandıran nesne.
    Şekil olarak kırmızı bir elma çizilir.
    """

    def __init__(self, x, hiz, gorsel=None):
        # Elma boyutları
        super().__init__(x, -40, 34, 34, hiz, KIRMIZI)
        self.puan = 10  # Her elma 10 puan
        self.gorsel = gorsel

    def ciz(self, ekran):
        """Elma görselini veya geometrik şeklini ekrana çizer."""
        if self.gorsel:
            ekran.blit(self.gorsel, (self.x, self.y))
            return

        # Fallback: geometrik çizim
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        # Elma gövdesi (kırmızı daire)
        pygame.draw.circle(ekran, KIRMIZI, (merkez_x, merkez_y + 2), yaricap)
        # Parlaklık efekti
        pygame.draw.circle(ekran, (255, 100, 100), (merkez_x - 5, merkez_y - 4), yaricap // 3)
        # Sap (kahverengi çizgi)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 3, merkez_y - yaricap - 8), 3)
        # Yaprak (küçük yeşil elips)
        yaprak_rect = pygame.Rect(merkez_x + 2, merkez_y - yaricap - 10, 10, 6)
        pygame.draw.ellipse(ekran, KOYU_YESIL, yaprak_rect)


# =============================================================================
# SINIF: BadItem (Kötü Nesne - Bomba)
# =============================================================================
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

        # Fallback: geometrik çizim
        merkez_x = self.x + self.genislik // 2
        merkez_y = self.y + self.yukseklik // 2
        yaricap = self.genislik // 2

        # Bomba gövdesi (koyu gri / siyah daire)
        pygame.draw.circle(ekran, KOYU_GRI, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, SIYAH, (merkez_x, merkez_y + 2), yaricap - 3)
        # Parlaklık efekti
        pygame.draw.circle(ekran, (80, 80, 80), (merkez_x - 5, merkez_y - 3), yaricap // 4)
        # Fitil (üstte kısa çizgi)
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 4, merkez_y - yaricap - 10), 3)
        # Kıvılcım (fitil ucunda turuncu/sarı nokta)
        pygame.draw.circle(ekran, TURUNCU, (merkez_x + 4, merkez_y - yaricap - 12), 4)
        pygame.draw.circle(ekran, SARI, (merkez_x + 4, merkez_y - yaricap - 12), 2)


# =============================================================================
# SINIF: GoldenItem (Altın Elma - Çok Değerli)
# =============================================================================
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

        # Surface tabanlı yumuşak altın parlama (glow)
        parlama_alpha = int(80 + abs(math.sin(self._parlama_sayac * 0.08)) * 100)
        glow_r = yaricap * 3
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, parlama_alpha // 2),
                           (glow_r, glow_r), glow_r)
        pygame.draw.circle(glow_surf, (255, 230, 80, parlama_alpha),
                           (glow_r, glow_r), glow_r // 2)
        ekran.blit(glow_surf, (merkez_x - glow_r, merkez_y - glow_r))

        # Parlama efekti (yanıp sönen dış halka)
        parlama = abs(math.sin(self._parlama_sayac * 0.1)) * 4
        pygame.draw.circle(ekran, (255, 255, 150),
                           (merkez_x, merkez_y + 2), int(yaricap + parlama))
        # Altın gövde
        pygame.draw.circle(ekran, ALTIN, (merkez_x, merkez_y + 2), yaricap)
        pygame.draw.circle(ekran, (255, 240, 100), (merkez_x - 4, merkez_y - 3), yaricap // 3)
        # Sap
        pygame.draw.line(ekran, KAHVERENGI, (merkez_x, merkez_y - yaricap),
                         (merkez_x + 3, merkez_y - yaricap - 8), 3)
        # Yıldız işareti
        yildiz_font = pygame.font.SysFont("Arial", 14, bold=True)
        yildiz = yildiz_font.render("★", True, BEYAZ)
        ekran.blit(yildiz, (merkez_x - 6, merkez_y - 8))


# =============================================================================
# SINIF: HealItem (Can Paketi)
# =============================================================================
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

        # Dış parlama
        parlama = abs(math.sin(self._parlama_sayac * 0.08)) * 3
        pygame.draw.circle(ekran, (150, 255, 200),
                           (merkez_x, merkez_y), int(self.genislik // 2 + parlama))
        # Beyaz daire zemin
        pygame.draw.circle(ekran, BEYAZ, (merkez_x, merkez_y), self.genislik // 2)
        pygame.draw.circle(ekran, ACIK_YESIL, (merkez_x, merkez_y), self.genislik // 2, 2)

        # Yeşil artı işareti
        kalinlik = 6
        pygame.draw.rect(ekran, YESIL,
                         (merkez_x - kalinlik // 2, merkez_y - 8, kalinlik, 16))
        pygame.draw.rect(ekran, YESIL,
                         (merkez_x - 8, merkez_y - kalinlik // 2, 16, kalinlik))


# =============================================================================
# SINIF: Boss (Kötü Meyve - Patron Seviyesi)
# =============================================================================
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
        ix = int(self.x)
        iy = int(self.y)
        cx = ix + self.genislik // 2
        cy = iy + self.yukseklik // 2
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
            pygame.draw.polygon(ekran, (100, 20, 30), [
                (sx - 5, iy + 5), (sx, iy - 15), (sx + 5, iy + 5)])
        # Can barı
        bar_w = self.genislik
        bar_x = ix
        bar_y = iy - 15
        pygame.draw.rect(ekran, KOYU_GRI, (bar_x, bar_y, bar_w, 8), border_radius=3)
        oran = self.can / self.max_can
        can_renk = YESIL if oran > 0.5 else SARI if oran > 0.25 else KIRMIZI
        pygame.draw.rect(ekran, can_renk, (bar_x, bar_y, int(bar_w * oran), 8), border_radius=3)
        pygame.draw.rect(ekran, BEYAZ, (bar_x, bar_y, bar_w, 8), 1, border_radius=3)

    def dikdortgen_al(self):
        return pygame.Rect(int(self.x), int(self.y), self.genislik, self.yukseklik)


# =============================================================================
# SINIF: BossBomba (Boss'un Fırlattığı Çapraz Bomba)
# =============================================================================
class BossBomba(FallingItem):
    """Boss'un oyuncuya doğru fırlattığı çapraz bomba."""

    def __init__(self, x, y, hedef_x, hedef_y):
        super().__init__(x, y, 20, 20, 0, TURUNCU)
        dx = hedef_x - x
        dy = hedef_y - y
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
        cx = int(self.x + 10)
        cy = int(self.y + 10)
        parlama = abs(math.sin(self._sayac * 0.15)) * 3
        pygame.draw.circle(ekran, (255, 100, 0), (cx, cy), int(10 + parlama))
        pygame.draw.circle(ekran, SARI, (cx, cy), 6)
        pygame.draw.circle(ekran, BEYAZ, (cx, cy), 3)


# =============================================================================
# SINIF: MermiItem (Boss Savaşında Düşen Mermi)
# =============================================================================
class MermiItem(FallingItem):
    """Boss savaşında düşen mermi - toplayınca boss'a hasar verir."""

    def __init__(self, x, hiz):
        super().__init__(x, -30, 24, 24, hiz, ACIK_MAVI)
        self._sayac = 0

    def guncelle(self, ruzgar_siddet=0, yercekim_carpan=1.0):
        super().guncelle(ruzgar_siddet, yercekim_carpan)
        self._sayac += 1

    def ciz(self, ekran):
        cx = int(self.x + 12)
        cy = int(self.y + 12)
        parlama = abs(math.sin(self._sayac * 0.1)) * 2
        pygame.draw.circle(ekran, (100, 200, 255), (cx, cy), int(12 + parlama))
        pygame.draw.circle(ekran, BEYAZ, (cx, cy), 8)
        pygame.draw.circle(ekran, ACIK_MAVI, (cx, cy), 5)
        pygame.draw.polygon(ekran, BEYAZ, [
            (cx - 3, cy + 2), (cx, cy - 5), (cx + 3, cy + 2)])


# =============================================================================
# SINIF: TakipBomba (Homing Bomb - Güdümlü Bomba)
# =============================================================================
class TakipBomba(FallingItem):
    """Düşerken sepetin X konumuna doğru hafifçe yönelen bomba."""

    def __init__(self, x, hiz, gorsel=None):
        super().__init__(x, -40, 30, 30, hiz * 0.85, PEMBE)
        self.gorsel = gorsel
        self._sayac = 0

    def guncelle(self, sepet_x=None):
        """Sepetin X pozisyonuna doğru hafifçe kayar (düşük lerp)."""
        self._sayac += 1
        self.y += self.hiz
        if sepet_x is not None:
            fark = sepet_x - self.x
            # Düşük lerp hızı (0.008) ve sınırlı maksimum kayma (0.8 px/kare)
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
        # Hedef simgesi
        pygame.draw.line(ekran, KIRMIZI, (cx - 6, cy), (cx + 6, cy), 2)
        pygame.draw.line(ekran, KIRMIZI, (cx, cy - 6), (cx, cy + 6), 2)


# =============================================================================
# SINIF: HirsizKus (Thief Bird - Elma Çalan Kuş)
# =============================================================================
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
        # Ekrandan çıktıysa kaldır
        if self.x < -80 or self.x > EKRAN_GENISLIK + 80:
            self.aktif = False
            return
        # En yakın elmayı hedefle
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
            # Dikey olarak elmaya doğru hafifçe yaklaş
            fark_y = self.hedef_elma.y - self.y
            self.y += max(-2.0, min(2.0, fark_y * 0.04))
            # Yatay olarak da hafifçe yaklaş
            fark_x = self.hedef_elma.x - self.x
            self.x += max(-1.0, min(1.0, fark_x * 0.03))
            # Elmaya yeterince yakınsa kap
            if abs(self.x - self.hedef_elma.x) < 20 and abs(self.y - self.hedef_elma.y) < 20:
                self.hedef_elma.aktif = False
                self.hedef_elma = None

    def ciz(self, ekran):
        if not self.aktif:
            return
        ix = int(self.x)
        iy = int(self.y)
        yon = 1 if self.vx > 0 else -1
        # Gövde
        pygame.draw.ellipse(ekran, (80, 60, 40), (ix, iy + 4, self.genislik, self.yukseklik - 6))
        # Kanat
        kanat_y = int(math.sin(self._kanat * 0.25) * 6)
        pygame.draw.polygon(ekran, (100, 80, 50), [
            (ix + 14, iy + 8),
            (ix + 14 + yon * 10, iy + kanat_y),
            (ix + 14 + yon * 4, iy + 10)])
        # Gaga
        gaga_x = ix + (self.genislik if yon > 0 else 0)
        pygame.draw.polygon(ekran, SARI, [
            (gaga_x, iy + 10),
            (gaga_x + yon * 8, iy + 12),
            (gaga_x, iy + 14)])
        # Göz
        goz_x = ix + (self.genislik - 6 if yon > 0 else 6)
        pygame.draw.circle(ekran, BEYAZ, (goz_x, iy + 8), 3)
        pygame.draw.circle(ekran, SIYAH, (goz_x, iy + 8), 1)

    def dikdortgen_al(self):
        return pygame.Rect(int(self.x), int(self.y), self.genislik, self.yukseklik)


# =============================================================================
# SINIF: Basket (Sepet - Oyuncunun Kontrol Ettiği Nesne)
# =============================================================================
class Basket:
    """
    Oyuncunun klavye ile sağa-sola hareket ettirdiği sepet nesnesi.
    Ok tuşları veya A/D tuşlarıyla kontrol edilir.
    Squash-Stretch animasyonu ve renk özelleştirme destekler.
    """

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

        # Renk bilgileri
        renk_bilgi = SEPET_RENKLERI.get(renk_adi, SEPET_RENKLERI["kahverengi"])
        self.renk = renk_bilgi["renk"]
        self.ic_renk = renk_bilgi["ic"]
        self.kenar_renk = renk_bilgi["kenar"]

        # Squash-Stretch
        self._ss_timer = 0
        self._ss_aktif = False

    def squash_baslat(self):
        """Elma yakalayınca squash-stretch başlatır."""
        self._ss_timer = 12
        self._ss_aktif = True

    def hareket_et(self, tuslar, kaygan_zemin=False):
        """Basılan tuşlara göre sepeti sağa veya sola hareket ettirir."""
        if not hasattr(self, '_momentum'):
            self._momentum = 0.0
        hedef = 0.0
        if tuslar[pygame.K_LEFT] or tuslar[pygame.K_a]:
            hedef -= self.hiz
        if tuslar[pygame.K_RIGHT] or tuslar[pygame.K_d]:
            hedef += self.hiz
        if kaygan_zemin:
            # Yağmurda kaygan zemin: momentum tabanlı hareket
            self._momentum += (hedef - self._momentum) * 0.12
        else:
            self._momentum = hedef
        self.x += self._momentum
        self.x = max(0, min(EKRAN_GENISLIK - self.genislik, self.x))

        # Squash-Stretch güncelle
        if self._ss_aktif:
            self._ss_timer -= 1
            if self._ss_timer <= 0:
                self._ss_aktif = False
                self.genislik = self.base_genislik
                self.yukseklik = self.base_yukseklik
            else:
                t = self._ss_timer / 12.0
                # İlk yarı squash (geniş-kısa), ikinci yarı stretch (dar-uzun)
                if t > 0.5:
                    s = math.sin((1.0 - t) * math.pi)
                    self.genislik = int(self.base_genislik * (1.0 + s * 0.15))
                    self.yukseklik = int(self.base_yukseklik * (1.0 - s * 0.12))
                else:
                    s = math.sin(t * math.pi)
                    self.genislik = int(self.base_genislik * (1.0 - s * 0.08))
                    self.yukseklik = int(self.base_yukseklik * (1.0 + s * 0.1))

            # Görseli yeniden boyutlandır
            if self.base_gorsel:
                self.gorsel = pygame.transform.scale(
                    self.base_gorsel, (self.genislik, self.yukseklik)
                )

    def ciz(self, ekran):
        """Sepet görselini veya geometrik şeklini ekrana çizer."""
        cx_offset = (self.base_genislik - self.genislik) // 2
        cy_offset = (self.base_yukseklik - self.yukseklik)
        draw_x = self.x + cx_offset
        draw_y = self.y + cy_offset

        if self.gorsel:
            ekran.blit(self.gorsel, (draw_x, draw_y))
            return

        # Fallback: geometrik çizim (custom renklerle)
        govde = pygame.Rect(draw_x, draw_y + 10, self.genislik, self.yukseklik - 10)
        pygame.draw.rect(ekran, self.renk, govde, border_radius=6)

        ic = pygame.Rect(draw_x + 5, draw_y + 14, self.genislik - 10, self.yukseklik - 20)
        pygame.draw.rect(ekran, self.ic_renk, ic, border_radius=4)

        sol_nokta = (draw_x - 8, draw_y + 10)
        sol_alt = (draw_x, draw_y + 10)
        sol_ust = (draw_x + 8, draw_y)
        pygame.draw.polygon(ekran, self.renk, [sol_nokta, sol_alt, sol_ust])

        sag_nokta = (draw_x + self.genislik + 8, draw_y + 10)
        sag_alt = (draw_x + self.genislik, draw_y + 10)
        sag_ust = (draw_x + self.genislik - 8, draw_y)
        pygame.draw.polygon(ekran, self.renk, [sag_nokta, sag_alt, sag_ust])

        pygame.draw.line(ekran, self.kenar_renk,
                         (draw_x - 8, draw_y + 10),
                         (draw_x + self.genislik + 8, draw_y + 10), 3)

        for i in range(1, 3):
            y_cizgi = draw_y + 10 + i * (self.yukseklik - 10) // 3
            pygame.draw.line(ekran, self.kenar_renk,
                             (draw_x + 2, y_cizgi),
                             (draw_x + self.genislik - 2, y_cizgi), 1)

    def dikdortgen_al(self):
        """Çarpışma tespiti için Rect nesnesi döndürür."""
        return pygame.Rect(self.x, self.y, self.base_genislik, self.base_yukseklik)


# =============================================================================
# SINIF: SkorVeritabani (SQLite Veritabanı Yöneticisi)
# =============================================================================
class SkorVeritabani:
    """SQLite ile skor ve market verilerini yöneten sınıf."""

    def __init__(self, db_yolu):
        self.db_yolu = db_yolu
        self._tablo_olustur()

    def _tablo_olustur(self):
        """Skor ve market tablolarını oluşturur (yoksa)."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS skorlar (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        isim TEXT NOT NULL,
                        skor INTEGER NOT NULL,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS market (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        renk_adi TEXT UNIQUE NOT NULL,
                        satin_alindi INTEGER DEFAULT 0
                    )
                """)
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS oyuncu_veri (
                        anahtar TEXT PRIMARY KEY,
                        deger TEXT NOT NULL
                    )
                """)
                # Varsayılan sepet her zaman açık
                bag.execute(
                    "INSERT OR IGNORE INTO market (renk_adi, satin_alindi) VALUES ('kahverengi', 1)"
                )
                # Varsayılan aktif sepet
                bag.execute(
                    "INSERT OR IGNORE INTO oyuncu_veri (anahtar, deger) VALUES ('aktif_sepet', 'kahverengi')"
                )
                # Varsayılan bakiye
                bag.execute(
                    "INSERT OR IGNORE INTO oyuncu_veri (anahtar, deger) VALUES ('bakiye', '0')"
                )
                # Görev (Achievement) tablosu
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        gorev_id TEXT UNIQUE NOT NULL,
                        tamamlandi INTEGER DEFAULT 0,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Upgrade (Yetenek) tablosu
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS upgrades (
                        upgrade_id TEXT PRIMARY KEY,
                        seviye INTEGER DEFAULT 0
                    )
                """)
                # Ghost (Hayalet Sepet) veri tablosu
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS ghost_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        skor INTEGER NOT NULL,
                        hareketler TEXT NOT NULL,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Envanter (Skin) tablosu
                bag.execute("""
                    CREATE TABLE IF NOT EXISTS envanter (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        skin_adi TEXT UNIQUE NOT NULL,
                        satin_alindi INTEGER DEFAULT 0,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # İlk çalıştırma kontrolü
                bag.execute(
                    "INSERT OR IGNORE INTO oyuncu_veri (anahtar, deger) VALUES ('ilk_calistirma', '1')"
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Veritabanı tablosu oluşturulamadı: {e}")

    # --- Skor metotları ---
    def skor_ekle(self, isim, skor):
        """Yeni bir skor kaydı ekler."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT INTO skorlar (isim, skor) VALUES (?, ?)",
                    (isim, skor)
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Skor kaydedilemedi: {e}")

    def en_iyi_5_al(self):
        """En yüksek 5 skoru döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT isim, skor FROM skorlar ORDER BY skor DESC LIMIT 5"
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[UYARI] Skorlar okunamadı: {e}")
            return []

    def ilk_5e_girer_mi(self, skor):
        """Verilen skorun ilk 5'e girip girmediğini kontrol eder."""
        if skor <= 0:
            return False
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT COUNT(*) FROM skorlar WHERE skor >= ?",
                    (skor,)
                )
                return cursor.fetchone()[0] < 5
        except sqlite3.Error as e:
            print(f"[UYARI] Skor kontrolü yapılamadı: {e}")
            return False

    def en_yuksek_skor(self):
        """En yüksek skoru döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute("SELECT MAX(skor) FROM skorlar")
                sonuc = cursor.fetchone()[0]
                return sonuc if sonuc else 0
        except sqlite3.Error as e:
            print(f"[UYARI] En yüksek skor okunamadı: {e}")
            return 0

    # --- Market / Bakiye metotları ---
    def bakiye_al(self):
        """Oyuncunun toplam bakiyesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT deger FROM oyuncu_veri WHERE anahtar = 'bakiye'"
                )
                sonuc = cursor.fetchone()
                return int(sonuc[0]) if sonuc else 0
        except (sqlite3.Error, ValueError):
            return 0

    def bakiye_guncelle(self, miktar):
        """Bakiyeye miktar ekler (negatif olabilir)."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                mevcut = self.bakiye_al()
                yeni = max(0, mevcut + miktar)
                bag.execute(
                    "UPDATE oyuncu_veri SET deger = ? WHERE anahtar = 'bakiye'",
                    (str(yeni),)
                )
                bag.commit()
                return yeni
        except sqlite3.Error as e:
            print(f"[UYARI] Bakiye güncellenemedi: {e}")
            return self.bakiye_al()

    def sepet_satin_al(self, renk_adi):
        """Bir sepet rengini satın alır. Başarılı ise True döndürür."""
        fiyat = SEPET_RENKLERI.get(renk_adi, {}).get("fiyat", 0)
        bakiye = self.bakiye_al()
        if bakiye < fiyat:
            return False
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT OR REPLACE INTO market (renk_adi, satin_alindi) VALUES (?, 1)",
                    (renk_adi,)
                )
                bag.commit()
            self.bakiye_guncelle(-fiyat)
            return True
        except sqlite3.Error as e:
            print(f"[UYARI] Satın alma başarısız: {e}")
            return False

    def satin_alinan_sepetler(self):
        """Satın alınan sepet renklerinin listesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT renk_adi FROM market WHERE satin_alindi = 1"
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return ["kahverengi"]

    def aktif_sepet_al(self):
        """Aktif sepet rengini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT deger FROM oyuncu_veri WHERE anahtar = 'aktif_sepet'"
                )
                sonuc = cursor.fetchone()
                return sonuc[0] if sonuc else "kahverengi"
        except sqlite3.Error:
            return "kahverengi"

    def aktif_sepet_ayarla(self, renk_adi):
        """Aktif sepet rengini ayarlar."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "UPDATE oyuncu_veri SET deger = ? WHERE anahtar = 'aktif_sepet'",
                    (renk_adi,)
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Aktif sepet ayarlanamadı: {e}")

    # --- Görev (Achievement) metotları ---
    def gorev_tamamlandi_mi(self, gorev_id):
        """Görevin daha önce tamamlanıp tamamlanmadığını kontrol eder."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT tamamlandi FROM achievements WHERE gorev_id = ?",
                    (gorev_id,)
                )
                sonuc = cursor.fetchone()
                return bool(sonuc and sonuc[0])
        except sqlite3.Error:
            return False

    def gorev_tamamla(self, gorev_id):
        """Görevi tamamlandı olarak işaretler."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT OR REPLACE INTO achievements (gorev_id, tamamlandi) VALUES (?, 1)",
                    (gorev_id,)
                )
                bag.commit()
        except sqlite3.Error as e:
            print(f"[UYARI] Görev kaydedilemedi: {e}")

    def tamamlanan_gorevler(self):
        """Tamamlanan tüm görevlerin ID listesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT gorev_id FROM achievements WHERE tamamlandi = 1"
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    # --- Upgrade (Yetenek) metotları ---
    def upgrade_seviye_al(self, upgrade_id):
        """Belirtilen upgrade'ın mevcut seviyesini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT seviye FROM upgrades WHERE upgrade_id = ?",
                    (upgrade_id,)
                )
                sonuc = cursor.fetchone()
                return sonuc[0] if sonuc else 0
        except sqlite3.Error:
            return 0

    def upgrade_satin_al(self, upgrade_id):
        """Upgrade seviyesini artırır. Başarılı ise True döndürür."""
        tanim = UPGRADE_TANIMLARI.get(upgrade_id)
        if not tanim:
            return False
        mevcut = self.upgrade_seviye_al(upgrade_id)
        if mevcut >= tanim["maks_seviye"]:
            return False
        fiyat = tanim["baz_fiyat"] + mevcut * tanim["artis"]
        bakiye = self.bakiye_al()
        if bakiye < fiyat:
            return False
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT OR REPLACE INTO upgrades (upgrade_id, seviye) VALUES (?, ?)",
                    (upgrade_id, mevcut + 1)
                )
                bag.commit()
            self.bakiye_guncelle(-fiyat)
            return True
        except sqlite3.Error:
            return False

    def tum_upgradeler(self):
        """Tüm upgrade'ların seviyelerini dict olarak döndürür."""
        sonuc = {}
        for uid in UPGRADE_TANIMLARI:
            sonuc[uid] = self.upgrade_seviye_al(uid)
        return sonuc

    # --- Ghost (Hayalet Sepet) metotları ---
    def ghost_kaydet(self, skor, hareketler_json):
        """En yüksek skorlu oyunun ghost verisini kaydeder."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                # Sadece en yüksek skoru sakla (eski veriyi sil)
                mevcut = bag.execute("SELECT MAX(skor) FROM ghost_data").fetchone()[0]
                if mevcut is None or skor >= mevcut:
                    bag.execute("DELETE FROM ghost_data")
                    bag.execute(
                        "INSERT INTO ghost_data (skor, hareketler) VALUES (?, ?)",
                        (skor, hareketler_json)
                    )
                    bag.commit()
                    return True
            return False
        except sqlite3.Error as e:
            print(f"[UYARI] Ghost verisi kaydedilemedi: {e}")
            return False

    def ghost_yukle(self):
        """En yüksek skorlu ghost verisini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT skor, hareketler FROM ghost_data ORDER BY skor DESC LIMIT 1"
                )
                sonuc = cursor.fetchone()
                if sonuc:
                    return {"skor": sonuc[0], "hareketler": sonuc[1]}
            return None
        except sqlite3.Error as e:
            print(f"[UYARI] Ghost verisi yüklenemedi: {e}")
            return None

    # --- Envanter (Skin) metotları ---
    def skin_satin_al(self, skin_adi):
        """Bir skin'i envantere ekler."""
        fiyat = SEPET_RENKLERI.get(skin_adi, {}).get("fiyat", 0)
        bakiye = self.bakiye_al()
        if bakiye < fiyat:
            return False
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "INSERT OR REPLACE INTO envanter (skin_adi, satin_alindi) VALUES (?, 1)",
                    (skin_adi,)
                )
                bag.commit()
            self.bakiye_guncelle(-fiyat)
            return True
        except sqlite3.Error:
            return False

    def sahip_olunan_skinler(self):
        """Envanterdeki tüm skin isimlerini döndürür."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT skin_adi FROM envanter WHERE satin_alindi = 1"
                )
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return ["kahverengi"]

    # --- İlk çalıştırma kontrolü ---
    def ilk_calistirma_mi(self):
        """Oyun ilk kez mi açılıyor kontrol eder."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                cursor = bag.execute(
                    "SELECT deger FROM oyuncu_veri WHERE anahtar = 'ilk_calistirma'"
                )
                sonuc = cursor.fetchone()
                return sonuc is not None and sonuc[0] == '1'
        except sqlite3.Error:
            return False

    def ilk_calistirma_tamam(self):
        """İlk çalıştırma bayrağını kapatır."""
        try:
            with sqlite3.connect(self.db_yolu) as bag:
                bag.execute(
                    "UPDATE oyuncu_veri SET deger = '0' WHERE anahtar = 'ilk_calistirma'"
                )
                bag.commit()
        except sqlite3.Error:
            pass


# =============================================================================
# SINIF: GameManager (Oyun Yöneticisi)
# =============================================================================
class GameManager:
    """
    Oyunun ana yönetici sınıfı.
    Oyun döngüsü, skor takibi, ekran yönetimi, nesne üretimi
    ve çarpışma tespiti bu sınıf tarafından yönetilir.
    """

    def __init__(self):
        # Ekran ve saat ayarları
        self.ekran = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        self.oyun_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        pygame.display.set_caption("🍎 Sepet Oyunu - Catching Game")
        self.saat = pygame.time.Clock()

        # Fontlar
        self.baslik_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.buyuk_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.orta_font = pygame.font.SysFont("Arial", 26)
        self.kucuk_font = pygame.font.SysFont("Arial", 20)
        self.mini_font = pygame.font.SysFont("Arial", 16)

        # --- Arka plan müziği ---
        try:
            ses_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds")
            pygame.mixer.music.load(os.path.join(ses_klasoru, "arkaplan.mp3"))
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[UYARI] Arka plan müziği yüklenemedi: {e}")

        # --- Ses efektleri ---
        self.bomba_ses = None
        self.kombo_ses = None
        self.rekor_ses = None
        self.gorev_ses = None
        self.boss_ses = None
        try:
            self.bomba_ses = pygame.mixer.Sound(os.path.join(ses_klasoru, "bomba.mp3"))
        except Exception:
            pass
        ses_ekstra = {"kombo_ses": "combo.wav", "rekor_ses": "record.wav",
                      "gorev_ses": "goal.wav", "boss_ses": "boss_hit.wav"}
        for attr, dosya in ses_ekstra.items():
            try:
                yol = os.path.join(ses_klasoru, dosya)
                if os.path.exists(yol):
                    setattr(self, attr, pygame.mixer.Sound(yol))
            except Exception:
                pass

        # --- Görsel varlıkları yükleme ---
        self.sepet_img = None
        self.elma_img = None
        self.bomba_img = None
        self.kalp_img = None
        self.bulut_img = None
        self.dag_img = None
        try:
            gorsel_klasoru = os.path.join(OYUN_KLASORU, "assets", "images")
            # Yedek yol: assets/sounds/images (görseller oradaysa)
            if not os.path.isdir(gorsel_klasoru):
                gorsel_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds", "images")

            gorsel_haritasi = {
                "sepet": ("sepet.png", (100, 50)),
                "elma": ("elma.png", (34, 34)),
                "bomba": ("bomba.png", (34, 34)),
                "kalp": ("kalp.png", (28, 28)),
                "bulut": ("bulut.png", (EKRAN_GENISLIK, EKRAN_YUKSEKLIK)),
                "dag": ("dag.png", (EKRAN_GENISLIK, EKRAN_YUKSEKLIK)),
            }
            for anahtar, (dosya, boyut) in gorsel_haritasi.items():
                yol = os.path.join(gorsel_klasoru, dosya)
                if os.path.exists(yol):
                    setattr(self, f"{anahtar}_img",
                            pygame.transform.scale(
                                pygame.image.load(yol).convert_alpha(), boyut))
                else:
                    print(f"[UYARI] {dosya} görseli bulunamadı: {yol}")

        except Exception as e:
            print(f"[UYARI] Görseller yüklenirken hata oluştu: {e}")
            print("[BİLGİ] Oyun geometrik çizimlerle devam edecek.")
            self.sepet_img = None
            self.elma_img = None
            self.bomba_img = None
            self.kalp_img = None
            self.bulut_img = None
            self.dag_img = None

        # --- Paralaks katmanlar ---
        self.paralaks_katmanlar = [
            ParalaksKatman(0.3, gorsel=self.bulut_img, cizim_fonk=_bulut_ciz),
            ParalaksKatman(0.7, gorsel=self.dag_img, cizim_fonk=_dag_ciz),
        ]

        # --- Ekran sarsıntısı ---
        self.ekran_sarsintisi = EkranSarsintisi()

        # --- Veritabanı ---
        self.veritabani = SkorVeritabani(VERITABANI_YOLU)

        # Oyun durumu: "menu", "oyun", "isim_gir", "bitti", "market", "tutorial"
        if self.veritabani.ilk_calistirma_mi():
            self.durum = "tutorial"
        else:
            self.durum = "menu"
        self.en_yuksek_skor = self.veritabani.en_yuksek_skor()

        # Aktif sepet rengi
        self.aktif_sepet_renk = self.veritabani.aktif_sepet_al()

        # İsim girişi için değişkenler
        self.oyuncu_ismi = ""
        self.isim_imlec_gorunsun = True
        self.isim_imlec_zamanlayici = 0

        # Parçacık yöneticisi
        self.parcacik_yonetici = ParticleManager()

        # Kalp kırılma efektleri
        self.kalp_kirilmalari = []

        # Market scroll pozisyonu
        self.market_scroll = 0

        # --- Duyuru (Announcer) sistemi ---
        self.duyurular = []

        # --- Görev (Achievement) bildirimleri ---
        self.gorev_bildirimleri = []

        # --- Gece/Gündüz döngüsü ---
        self.gece_modu = False
        self.gece_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        self.isik_yaricap = 130

        # --- Boss sistemi ---
        self.boss = None
        self.boss_aktif = False
        self.boss_yenildi = False
        self.boss_bombalar = []
        self.boss_mermi_zamanlayici = 0

        # Arka plan yıldızları (dekoratif)
        self.yildizlar = [(random.randint(0, EKRAN_GENISLIK),
                           random.randint(0, EKRAN_YUKSEKLIK // 2),
                           random.randint(1, 3)) for _ in range(40)]

        # --- Rüzgar ve Yağmur sistemleri ---
        self.ruzgar = RuzgarSistemi()
        self.yagmur = YagmurSistemi()

        # --- Bölge (Biome) sistemi ---
        self.aktif_bolge = 0
        self.bolge_gorselleri = {}
        try:
            gorsel_klasoru = os.path.join(OYUN_KLASORU, "assets", "images")
            if not os.path.isdir(gorsel_klasoru):
                gorsel_klasoru = os.path.join(OYUN_KLASORU, "assets", "sounds", "images")
            for i, bolge in enumerate(BOLGE_TANIMLARI):
                yol = os.path.join(gorsel_klasoru, bolge["dosya"])
                if os.path.exists(yol):
                    self.bolge_gorselleri[i] = pygame.transform.scale(
                        pygame.image.load(yol).convert_alpha(),
                        (EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
        except Exception as e:
            print(f"[UYARI] Bölge görselleri yüklenemedi: {e}")

        # --- Hırsız kuşlar ---
        self.hirsiz_kuslar = []
        self.hirsiz_kus_zamanlayici = 0

        # --- Replay (Tekrar İzleme) Sistemi ---
        self.replay = ReplaySystem()

        # --- Ghost (Hayalet Sepet) Sistemi ---
        self.ghost = GhostSepet()
        self.ghost_kayit = []  # Mevcut oyundaki sepet hareketlerini kaydet
        self._ghost_yukle()

        # --- Dinamik Zorluk Motoru ---
        self.zorluk_motoru = DinamikZorlukMotoru()

        # --- Global API Yöneticisi ---
        self.api_yoneticisi = None  # Veritabanı hazır olduktan sonra oluşturulur

        self._oyunu_sifirla()

    # -------------------------------------------------------------------------
    # Ghost Veri Yükleme
    # -------------------------------------------------------------------------
    def _ghost_yukle(self):
        """Veritabanından en yüksek skorun ghost verisini yükler."""
        veri = self.veritabani.ghost_yukle()
        if veri:
            self.ghost = GhostSepet.json_den_yukle(veri["hareketler"])
        else:
            self.ghost = GhostSepet()

    # -------------------------------------------------------------------------
    # Oyun Durumu Yönetimi
    # -------------------------------------------------------------------------
    def _oyunu_sifirla(self):
        """Oyunu başlangıç durumuna sıfırlar."""
        self.aktif_sepet_renk = self.veritabani.aktif_sepet_al()
        self.sepet = Basket(gorsel=self.sepet_img, renk_adi=self.aktif_sepet_renk)
        self.dusen_nesneler = []
        self.skor = 0
        self.can = MAKS_CAN
        self.nesne_zamanlayici = 0
        self.nesne_bekleme = 50
        self.temel_hiz = 3.0
        self.zorluk_seviyesi = 1
        self.toplam_kare = 0
        self.son_skor = 0
        self.parcacik_yonetici = ParticleManager()
        self.oyuncu_ismi = ""
        self.kalp_kirilmalari = []

        # Kombo sistemi
        self.kombo_sayac = 0
        self.kombo_carpan = 1
        self.kombo_bar = 0.0  # 0.0 - 1.0 (Fever Mode barı)

        # Fever (Öfke) Modu
        self.fever_aktif = False
        self.fever_kalan_kare = 0  # 5 saniye = 300 kare (60 FPS)
        self.fever_parlama = 0

        # Gece/Gündüz
        self.gece_modu = False

        # Boss
        self.boss = None
        self.boss_aktif = False
        self.boss_yenildi = False
        self.boss_bombalar = []
        self.boss_mermi_zamanlayici = 0

        # Duyurular
        self.duyurular = []
        self.gorev_bildirimleri = []

        # Achievement sayaçları (oyun başına)
        self.toplanan_elma_sayisi = 0
        self.toplanan_altin_sayisi = 0
        self.hasar_alindi = False

        # Rüzgar / yağmur / bölge sıfırla
        self.ruzgar.siddet = 0.0
        self.ruzgar.hedef = 0.0
        self.yagmur.aktif = False
        self.yagmur.damlalar.clear()
        self.yagmur.bekleme = random.randint(600, 1200)
        self.aktif_bolge = 0
        self.hirsiz_kuslar = []
        self.hirsiz_kus_zamanlayici = 0

        # Bölge geçiş (fade) efekti
        self.bolge_fade_alpha = 0
        self.bolge_fade_durum = None  # None / "karart" / "aydinlat"
        self.bolge_fade_hedef = 0     # Geçilecek bölge indeksi

        # Upgrade'ları uygula
        upgrades = self.veritabani.tum_upgradeler()
        hiz_bonus = upgrades.get("sepet_hizi", 0)
        self.sepet.hiz = 8 + hiz_bonus  # Her seviye +1 hız
        can_bonus = upgrades.get("ekstra_can", 0)
        self.can = MAKS_CAN + can_bonus
        self.miknatıs_bonus = upgrades.get("miknatıs_sure", 0)  # İleride kullanılabilir

        # Replay sistemi sıfırla
        self.replay.sifirla()

        # Ghost kayıt sıfırla (yeni oyun başlıyor)
        self.ghost_kayit = []

        # Elastik skor titreşimi ve istatistik izleme
        self._skor_titresim = 0
        self.en_yuksek_kombo = 0
        self._ghost_yukle()

        # Dinamik zorluk motoru sıfırla
        self.zorluk_motoru.sifirla()

        # API yöneticisini oluştur
        self.api_yoneticisi = SkorAPIYoneticisi(self.veritabani)

    # -------------------------------------------------------------------------
    # Nesne Üretimi
    # -------------------------------------------------------------------------
    def _nesne_uret(self):
        """
        Zamanlayıcıya göre yeni düşen nesne üretir.
        Boss modunda mermi, Fever modunda altın elma,
        Normal: %68 elma, %25 bomba, %5 altın elma, %2 can paketi.
        """
        if self.boss_aktif:
            # Boss modunda sadece mermi düşür
            self.boss_mermi_zamanlayici += 1
            if self.boss_mermi_zamanlayici >= 40:
                self.boss_mermi_zamanlayici = 0
                x = random.randint(50, EKRAN_GENISLIK - 50)
                hiz = self.temel_hiz + 0.5
                self.dusen_nesneler.append(MermiItem(x, hiz))
            return

        self.nesne_zamanlayici += 1
        if self.nesne_zamanlayici >= self.nesne_bekleme:
            self.nesne_zamanlayici = 0

            # Nesneler kenarlardan 50 px uzakta doğar
            x = random.randint(50, EKRAN_GENISLIK - 50)
            hiz = self.temel_hiz + (self.zorluk_seviyesi - 1) * 0.5
            hiz += random.uniform(-0.3, 0.5)
            # Dinamik zorluk motoru hız düzeltmesi
            hiz = self.zorluk_motoru.hiz_al(hiz)

            if self.fever_aktif:
                # Fever modunda sadece altın elma
                self.dusen_nesneler.append(GoldenItem(x, hiz))
            else:
                sans = random.random()
                if sans < 0.02:
                    self.dusen_nesneler.append(HealItem(x, hiz))
                elif sans < 0.05:
                    # Güdümlü bomba (%3)
                    self.dusen_nesneler.append(TakipBomba(x, hiz))
                elif sans < 0.10:
                    self.dusen_nesneler.append(GoldenItem(x, hiz))
                elif sans < 0.35:
                    self.dusen_nesneler.append(BadItem(x, hiz, gorsel=self.bomba_img))
                else:
                    self.dusen_nesneler.append(GoodItem(x, hiz, gorsel=self.elma_img))

        # Hırsız kuş üretimi (her ~8 saniyede bir, seviye 3+)
        if self.zorluk_seviyesi >= 3 and not self.boss_aktif:
            self.hirsiz_kus_zamanlayici += 1
            if self.hirsiz_kus_zamanlayici >= 480:
                self.hirsiz_kus_zamanlayici = 0
                if len(self.hirsiz_kuslar) < 2:
                    self.hirsiz_kuslar.append(HirsizKus())

    # -------------------------------------------------------------------------
    # Zorluk Ayarlama
    # -------------------------------------------------------------------------
    def _zorluk_ayarla(self):
        """
        Skora bağlı olarak oyun zorluğunu dinamik olarak artırır.
        Her 500 puanda bir seviye atlar.
        """
        yeni_seviye = 1 + self.skor // 500

        if yeni_seviye != self.zorluk_seviyesi:
            self.zorluk_seviyesi = yeni_seviye

            # Nesnelerin ekranda belirme sıklığını artır (minimum 15 kare)
            self.nesne_bekleme = max(15, 50 - (self.zorluk_seviyesi - 1) * 5)

            # Temel düşme hızını artır (minimum güvenli üst sınır)
            self.temel_hiz = min(8.0, 3.0 + (self.zorluk_seviyesi - 1) * 0.5)

    # -------------------------------------------------------------------------
    # Çarpışma Tespiti
    # -------------------------------------------------------------------------
    def _carpismalari_kontrol_et(self):
        """Düşen nesneler ile sepet arasındaki çarpışmaları kontrol eder."""
        sepet_rect = self.sepet.dikdortgen_al()

        for nesne in self.dusen_nesneler:
            if not nesne.aktif:
                continue

            # Kaçırılan elma kontrolü (ekran dışına çıktı ve yakalanmadı)
            if nesne.y > EKRAN_YUKSEKLIK and isinstance(nesne, (GoodItem, GoldenItem)):
                self.kombo_sayac = 0
                self.kombo_carpan = 1
                self.zorluk_motoru.nesne_kacirildi()
                continue

            if sepet_rect.colliderect(nesne.dikdortgen_al()):
                nesne.aktif = False

                px = nesne.x + nesne.genislik // 2
                py = nesne.y + nesne.yukseklik // 2

                if isinstance(nesne, MermiItem):
                    # Boss'a hasar ver
                    if self.boss_aktif and self.boss and self.boss.aktif:
                        self.boss.hasar_al()
                        if self.boss_ses:
                            self.boss_ses.play()
                    self.parcacik_yonetici.patlama_ekle(px, py, ACIK_MAVI, 15)
                    self.sepet.squash_baslat()

                elif isinstance(nesne, GoldenItem):
                    kazanilan = nesne.puan * self.kombo_carpan
                    self.skor += kazanilan
                    self.toplanan_elma_sayisi += 1
                    self.toplanan_altin_sayisi += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, ALTIN, 25)
                    self.sepet.squash_baslat()
                    self._kombo_artir()
                    self.zorluk_motoru.nesne_yakalandi()

                elif isinstance(nesne, HealItem):
                    if self.can < MAKS_CAN:
                        self.can += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, ACIK_YESIL, 20)
                    self.sepet.squash_baslat()

                elif isinstance(nesne, GoodItem):
                    kazanilan = nesne.puan * self.kombo_carpan
                    self.skor += kazanilan
                    self.toplanan_elma_sayisi += 1
                    self.parcacik_yonetici.patlama_ekle(px, py, YESIL, 15)
                    self.sepet.squash_baslat()
                    self._kombo_artir()
                    self.zorluk_motoru.nesne_yakalandi()

                elif isinstance(nesne, (BadItem, BossBomba, TakipBomba)):
                    eski_can = self.can
                    self.can -= 1
                    self.hasar_alindi = True
                    if self.bomba_ses:
                        self.bomba_ses.play()
                    self.parcacik_yonetici.patlama_ekle(px, py, TURUNCU, 20)
                    self.ekran_sarsintisi.baslat()
                    # Kombo sıfırla
                    self.kombo_sayac = 0
                    self.kombo_carpan = 1
                    # Kalp kırılma efekti
                    if eski_can > self.can:
                        kalp_idx = self.can
                        kalp_x = EKRAN_GENISLIK - 40 - kalp_idx * 35
                        self.kalp_kirilmalari.append(
                            KalpKirilma(kalp_x, 8, self.kalp_img)
                        )

        # Boss bombaları ile sepet çarpışması
        for bomba in self.boss_bombalar:
            if not bomba.aktif:
                continue
            if sepet_rect.colliderect(bomba.dikdortgen_al()):
                bomba.aktif = False
                eski_can = self.can
                self.can -= 1
                self.hasar_alindi = True
                if self.bomba_ses:
                    self.bomba_ses.play()
                px = int(bomba.x + 10)
                py = int(bomba.y + 10)
                self.parcacik_yonetici.patlama_ekle(px, py, TURUNCU, 20)
                self.ekran_sarsintisi.baslat()
                self.kombo_sayac = 0
                self.kombo_carpan = 1
                if eski_can > self.can:
                    kalp_idx = self.can
                    kalp_x = EKRAN_GENISLIK - 40 - kalp_idx * 35
                    self.kalp_kirilmalari.append(
                        KalpKirilma(kalp_x, 8, self.kalp_img)
                    )

    def _kombo_artir(self):
        """Kombo sayacını artırır, çarpanı günceller ve görsel efekt ekler."""
        self.kombo_sayac += 1
        # Elastik skor titreşimi tetikle ve en yüksek komboyu güncelle
        self._skor_titresim = 15
        if self.kombo_sayac > self.en_yuksek_kombo:
            self.en_yuksek_kombo = self.kombo_sayac
        if self.kombo_sayac >= 20:
            self.kombo_carpan = 10
            if self.kombo_sayac == 20:
                self.duyurular.append(Duyuru("LEGENDARY!", (255, 50, 255), 120))
                if self.kombo_ses:
                    self.kombo_ses.play()
        elif self.kombo_sayac >= 15:
            self.kombo_carpan = 7
            if self.kombo_sayac == 15:
                self.duyurular.append(Duyuru("FANTASTIC!", (0, 255, 200), 100))
                if self.kombo_ses:
                    self.kombo_ses.play()
        elif self.kombo_sayac >= 10:
            self.kombo_carpan = 5
            if self.kombo_sayac == 10:
                self.duyurular.append(Duyuru("UNSTOPPABLE!", ALTIN, 90))
                if self.kombo_ses:
                    self.kombo_ses.play()
        elif self.kombo_sayac >= 7:
            self.kombo_carpan = 3
            if self.kombo_sayac == 7:
                self.duyurular.append(Duyuru("AMAZING!", TURUNCU, 80, EKRAN_YUKSEKLIK // 3 + 60))
                if self.kombo_ses:
                    self.kombo_ses.play()
        elif self.kombo_sayac >= 5:
            self.kombo_carpan = 2
            if self.kombo_sayac == 5:
                self.duyurular.append(Duyuru("COMBO!", SARI, 75, EKRAN_YUKSEKLIK // 3 + 40))
                if self.kombo_ses:
                    self.kombo_ses.play()
        else:
            self.kombo_carpan = 1

        # Kombo barı doldur
        self.kombo_bar = min(1.0, self.kombo_bar + 0.1)

        # Bar dolduysa Fever mode başlat
        if self.kombo_bar >= 1.0 and not self.fever_aktif:
            self.fever_aktif = True
            self.fever_kalan_kare = 300  # 5 saniye
            self.kombo_bar = 1.0

    # -------------------------------------------------------------------------
    # Görev (Achievement) Kontrol
    # -------------------------------------------------------------------------
    def _gorev_kontrol(self):
        """Görevleri kontrol edip tamamlananları veritabanına kaydeder."""
        # 50 Elma Topla
        if self.toplanan_elma_sayisi >= 50:
            if not self.veritabani.gorev_tamamlandi_mi("50_elma"):
                self.veritabani.gorev_tamamla("50_elma")
                self.gorev_bildirimleri.append(GorevBildirimi(GOREV_TANIMLARI["50_elma"]))
                if self.gorev_ses:
                    self.gorev_ses.play()

        # Hiç Can Kaybetmeden 1000 Puan
        if self.skor >= 1000 and not self.hasar_alindi:
            if not self.veritabani.gorev_tamamlandi_mi("1000_hasarsiz"):
                self.veritabani.gorev_tamamla("1000_hasarsiz")
                self.gorev_bildirimleri.append(GorevBildirimi(GOREV_TANIMLARI["1000_hasarsiz"]))
                if self.gorev_ses:
                    self.gorev_ses.play()

        # Tek Oyunda 5 Altın Elma
        if self.toplanan_altin_sayisi >= 5:
            if not self.veritabani.gorev_tamamlandi_mi("5_altin"):
                self.veritabani.gorev_tamamla("5_altin")
                self.gorev_bildirimleri.append(GorevBildirimi(GOREV_TANIMLARI["5_altin"]))
                if self.gorev_ses:
                    self.gorev_ses.play()

    # -------------------------------------------------------------------------
    # Arka Plan Çizimi
    # -------------------------------------------------------------------------
    def _arkaplan_ciz(self, hedef=None):
        """Paralaks katmanlı arka plan çizer (bölge desteği)."""
        ekran = hedef or self.ekran
        # Bölge görseli varsa önce onu çiz
        bolge_idx = getattr(self, 'aktif_bolge', 0)
        if bolge_idx in getattr(self, 'bolge_gorselleri', {}):
            ekran.blit(self.bolge_gorselleri[bolge_idx], (0, 0))
        else:
            # Gradyan gökyüzü (bölge renklerine göre)
            fever_mod = getattr(self, 'fever_aktif', False)
            bolge = BOLGE_TANIMLARI[bolge_idx]
            gk = bolge["gokyuzu"]
            for y in range(EKRAN_YUKSEKLIK):
                oran = y / EKRAN_YUKSEKLIK
                if fever_mod:
                    pulse = abs(math.sin(getattr(self, 'fever_parlama', 0) * 0.05)) * 30
                    r = int(60 + 100 * oran + pulse)
                    g = int(20 + 60 * oran)
                    b = int(60 + 80 * oran + pulse * 0.5)
                else:
                    r = int(gk[0] + (130 - gk[0]) * oran)
                    g = int(gk[1] + (170 - gk[1]) * oran)
                    b = int(gk[2] + (200 - gk[2]) * oran)
                pygame.draw.line(ekran, (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))),
                                 (0, y), (EKRAN_GENISLIK, y))

        # Paralaks katmanları
        fever_mod = getattr(self, 'fever_aktif', False)
        ruzgar_s = getattr(self.ruzgar, 'siddet', 0.0) if hasattr(self, 'ruzgar') else 0.0
        for katman in self.paralaks_katmanlar:
            katman.ciz(ekran, fever_mod, ruzgar_s)

        # Zemin (bölge renklerine göre)
        zemin_y = EKRAN_YUKSEKLIK - 30
        bolge = BOLGE_TANIMLARI[bolge_idx]
        zemin_renk = (60, 30, 40) if fever_mod else bolge["zemin"]
        cimen_renk = (100, 50, 60) if fever_mod else bolge["cimen"]
        pygame.draw.rect(ekran, zemin_renk, (0, zemin_y, EKRAN_GENISLIK, 30))
        pygame.draw.rect(ekran, cimen_renk, (0, zemin_y, EKRAN_GENISLIK, 5))

    # -------------------------------------------------------------------------
    # HUD (Skor, Can, Zorluk Göstergesi)
    # -------------------------------------------------------------------------
    def _hud_ciz(self, hedef=None):
        """Ekranın üstünde skor, can, kombo ve fever bilgisini gösterir."""
        ekran = hedef or self.ekran
        # Yarı saydam üst panel
        panel = pygame.Surface((EKRAN_GENISLIK, 45), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        ekran.blit(panel, (0, 0))

        # Skor (kombo çarpanı ile - renk kombo seviyesine göre değişir)
        if self.kombo_sayac >= 20:
            # Gökkuşağı efekti
            t = pygame.time.get_ticks() * 0.003
            sr = int(127 + 128 * math.sin(t))
            sg = int(127 + 128 * math.sin(t + 2.1))
            sb = int(127 + 128 * math.sin(t + 4.2))
            skor_renk = (sr, sg, sb)
        elif self.kombo_sayac >= 15:
            skor_renk = (0, 255, 200)
        elif self.kombo_sayac >= 10:
            skor_renk = ALTIN
        elif self.kombo_sayac >= 7:
            skor_renk = TURUNCU
        elif self.kombo_sayac >= 5:
            skor_renk = SARI
        elif self.kombo_carpan > 1:
            skor_renk = ALTIN
        else:
            skor_renk = BEYAZ
        if self.kombo_carpan > 1:
            skor_yazi = self.orta_font.render(f"Skor: {self.skor} (x{self.kombo_carpan})", True, skor_renk)
        else:
            skor_yazi = self.orta_font.render(f"Skor: {self.skor}", True, skor_renk)

        # Elastik titreşim efekti (kombo artışında tetiklenir)
        titresim = getattr(self, '_skor_titresim', 0)
        if titresim > 0:
            self._skor_titresim = titresim - 1
            t = titresim / 15.0
            olcek = 1.0 + 0.15 * t * abs(math.sin(titresim * 0.8))
            kaydirma_y = int(3 * math.sin(titresim * 1.2) * t)
            orijinal_boyut = skor_yazi.get_size()
            yeni_w = int(orijinal_boyut[0] * olcek)
            yeni_h = int(orijinal_boyut[1] * olcek)
            skor_yazi = pygame.transform.smoothscale(skor_yazi, (yeni_w, yeni_h))
            ekran.blit(skor_yazi, (15, 8 + kaydirma_y - (yeni_h - orijinal_boyut[1]) // 2))
        else:
            ekran.blit(skor_yazi, (15, 8))

        # Zorluk seviyesi
        zorluk_yazi = self.kucuk_font.render(f"Seviye: {self.zorluk_seviyesi}", True, ACIK_MAVI)
        ekran.blit(zorluk_yazi, (250, 12))

        # Kombo barı
        bar_x, bar_y, bar_w, bar_h = 360, 14, 100, 16
        pygame.draw.rect(ekran, KOYU_GRI, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        doluluk = int(bar_w * self.kombo_bar)
        if doluluk > 0:
            bar_renk = ALTIN if self.fever_aktif else TURUNCU
            pygame.draw.rect(ekran, bar_renk, (bar_x, bar_y, doluluk, bar_h), border_radius=4)
        pygame.draw.rect(ekran, BEYAZ, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        kombo_label = self.mini_font.render("FEVER" if self.fever_aktif else f"Kombo: {self.kombo_sayac}", True, BEYAZ)
        ekran.blit(kombo_label, (bar_x + bar_w + 5, bar_y - 1))

        # Fever modu göstergesi
        if self.fever_aktif:
            kalan_sn = self.fever_kalan_kare / 60.0
            fever_txt = self.kucuk_font.render(f"★ FEVER MODE {kalan_sn:.1f}s ★", True, ALTIN)
            ekran.blit(fever_txt, (EKRAN_GENISLIK // 2 - fever_txt.get_width() // 2, 48))

        # Canlar (kalp görseli veya geometrik kalp)
        for i in range(self.can):
            kalp_x = EKRAN_GENISLIK - 40 - i * 35
            kalp_y = 8
            if self.kalp_img:
                ekran.blit(self.kalp_img, (kalp_x - 5, kalp_y))
            else:
                pygame.draw.circle(ekran, KIRMIZI, (kalp_x, kalp_y + 5), 8)
                pygame.draw.circle(ekran, KIRMIZI, (kalp_x + 10, kalp_y + 5), 8)
                pygame.draw.polygon(ekran, KIRMIZI, [
                    (kalp_x - 8, kalp_y + 6),
                    (kalp_x + 18, kalp_y + 6),
                    (kalp_x + 5, kalp_y + 22)
                ])

        # Kalp kırılma efektleri
        for kk in self.kalp_kirilmalari:
            kk.ciz(ekran)

        # Boss durumu göstergesi
        if self.boss_aktif and self.boss:
            boss_txt = self.orta_font.render("💀 BOSS FIGHT!", True, KIRMIZI)
            ekran.blit(boss_txt, (EKRAN_GENISLIK // 2 - boss_txt.get_width() // 2, 48))
        elif self.gece_modu:
            gece_txt = self.mini_font.render("🌙 Gece Modu", True, (150, 150, 200))
            ekran.blit(gece_txt, (10, 48))

        # Bölge göstergesi
        bolge_idx = getattr(self, 'aktif_bolge', 0)
        bolge_isim = BOLGE_TANIMLARI[bolge_idx]["isim"]
        bolge_txt = self.mini_font.render(f"🌍 {bolge_isim}", True, BEYAZ)
        ekran.blit(bolge_txt, (EKRAN_GENISLIK - bolge_txt.get_width() - 10, 48))

        # Dinamik Zorluk Göstergesi
        kacirma = self.zorluk_motoru.kacirma_orani
        if kacirma > 0.50:
            zorluk_renk = ACIK_YESIL
            zorluk_etiket = "Kolay"
        elif kacirma < 0.20:
            zorluk_renk = KIRMIZI
            zorluk_etiket = "Zor"
        else:
            zorluk_renk = SARI
            zorluk_etiket = "Normal"
        dz_txt = self.mini_font.render(f"⚙ {zorluk_etiket} ({kacirma:.0%})", True, zorluk_renk)
        ekran.blit(dz_txt, (10, 65))

    # -------------------------------------------------------------------------
    # Ana Menü Ekranı
    # -------------------------------------------------------------------------
    def _menu_ciz(self):
        """Oyunun başlangıç menüsünü ekrana çizer."""
        self._arkaplan_ciz()

        # Başlık
        baslik = self.baslik_font.render("Sepet Oyunu", True, BEYAZ)
        baslik_golge = self.baslik_font.render("Sepet Oyunu", True, (0, 0, 0))
        bx = EKRAN_GENISLIK // 2 - baslik.get_width() // 2
        self.ekran.blit(baslik_golge, (bx + 3, 43))
        self.ekran.blit(baslik, (bx, 40))

        # Alt başlık
        alt = self.orta_font.render("Elmaları topla, bombalardan kaçın!", True, SARI)
        self.ekran.blit(alt, (EKRAN_GENISLIK // 2 - alt.get_width() // 2, 110))

        # --- Top 5 Liderlik Tablosu ---
        top5_baslik = self.orta_font.render("En İyi 5 Skor", True, ALTIN)
        self.ekran.blit(top5_baslik, (EKRAN_GENISLIK // 2 - top5_baslik.get_width() // 2, 155))

        top5 = self.veritabani.en_iyi_5_al()
        if top5:
            for sira, (isim, skor) in enumerate(top5, 1):
                renk = ALTIN if sira == 1 else BEYAZ
                satir = self.kucuk_font.render(f"{sira}. {isim} - {skor} puan", True, renk)
                self.ekran.blit(satir, (EKRAN_GENISLIK // 2 - satir.get_width() // 2, 180 + sira * 25))
        else:
            bos_yazi = self.kucuk_font.render("Henüz skor kaydı yok", True, GRI)
            self.ekran.blit(bos_yazi, (EKRAN_GENISLIK // 2 - bos_yazi.get_width() // 2, 205))

        # Kontroller bilgisi
        kontrol1 = self.kucuk_font.render("← → Ok Tuşları veya A / D ile sepeti hareket ettir", True, BEYAZ)
        self.ekran.blit(kontrol1, (EKRAN_GENISLIK // 2 - kontrol1.get_width() // 2, 365))

        # Nesne açıklamaları (tek satır, ikonlarla)
        y_ikon = 400
        pygame.draw.circle(self.ekran, KIRMIZI, (170, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("Elma +10", True, YESIL), (188, y_ikon - 8))

        pygame.draw.circle(self.ekran, ALTIN, (310, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("Altın +100", True, ALTIN), (328, y_ikon - 8))

        pygame.draw.circle(self.ekran, KOYU_GRI, (465, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("Bomba -1\u2665", True, KIRMIZI), (483, y_ikon - 8))

        pygame.draw.circle(self.ekran, ACIK_YESIL, (610, y_ikon), 10)
        self.ekran.blit(self.kucuk_font.render("+1\u2665", True, ACIK_YESIL), (628, y_ikon - 8))

        # Başlat butonu
        buton_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 435, 240, 50)
        fare = pygame.mouse.get_pos()
        if buton_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, YESIL, buton_rect, border_radius=12)
        else:
            pygame.draw.rect(self.ekran, KOYU_YESIL, buton_rect, border_radius=12)
        pygame.draw.rect(self.ekran, BEYAZ, buton_rect, 2, border_radius=12)

        buton_yazi = self.buyuk_font.render("BAŞLAT", True, BEYAZ)
        self.ekran.blit(buton_yazi,
                        (buton_rect.centerx - buton_yazi.get_width() // 2,
                         buton_rect.centery - buton_yazi.get_height() // 2))

        # Market butonu
        market_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 200, 495, 180, 40)
        if market_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, ALTIN, market_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (160, 130, 20), market_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, market_rect, 2, border_radius=10)
        market_yazi = self.orta_font.render("🛒 Market", True, BEYAZ)
        self.ekran.blit(market_yazi,
                        (market_rect.centerx - market_yazi.get_width() // 2,
                         market_rect.centery - market_yazi.get_height() // 2))

        # Upgrade butonu
        upgrade_rect = pygame.Rect(EKRAN_GENISLIK // 2 + 20, 495, 180, 40)
        if upgrade_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, ACIK_YESIL, upgrade_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (30, 120, 60), upgrade_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, upgrade_rect, 2, border_radius=10)
        upgrade_yazi = self.orta_font.render("⚡ Yetenekler", True, BEYAZ)
        self.ekran.blit(upgrade_yazi,
                        (upgrade_rect.centerx - upgrade_yazi.get_width() // 2,
                         upgrade_rect.centery - upgrade_yazi.get_height() // 2))

        # Bakiye gösterimi
        bakiye = self.veritabani.bakiye_al()
        bakiye_yazi = self.kucuk_font.render(f"💰 Bakiye: {bakiye} puan", True, ALTIN)
        self.ekran.blit(bakiye_yazi, (EKRAN_GENISLIK // 2 - bakiye_yazi.get_width() // 2, 545))

        # ENTER ipucu
        enter_yazi = self.kucuk_font.render("ENTER: Başlat | M: Market | U: Yetenekler", True, GRI)
        self.ekran.blit(enter_yazi, (EKRAN_GENISLIK // 2 - enter_yazi.get_width() // 2, 570))

        return buton_rect, market_rect, upgrade_rect

    # -------------------------------------------------------------------------
    # Market Ekranı
    # -------------------------------------------------------------------------
    def _market_ciz(self):
        """Sepet renk marketi ekranını çizer."""
        self._arkaplan_ciz()

        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.ekran.blit(overlay, (0, 0))

        # Panel
        panel_rect = pygame.Rect(50, 40, EKRAN_GENISLIK - 100, EKRAN_YUKSEKLIK - 80)
        pygame.draw.rect(self.ekran, (25, 25, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, ALTIN, panel_rect, 2, border_radius=15)

        baslik = self.buyuk_font.render("🛒 Sepet Marketi", True, ALTIN)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 60))

        bakiye = self.veritabani.bakiye_al()
        bakiye_yazi = self.orta_font.render(f"💰 Bakiye: {bakiye} puan", True, BEYAZ)
        self.ekran.blit(bakiye_yazi, (EKRAN_GENISLIK // 2 - bakiye_yazi.get_width() // 2, 105))

        satin_alinanlar = self.veritabani.satin_alinan_sepetler()
        aktif = self.veritabani.aktif_sepet_al()
        fare = pygame.mouse.get_pos()

        buton_rects = {}
        y_baslangic = 150
        for idx, (renk_adi, bilgi) in enumerate(SEPET_RENKLERI.items()):
            y = y_baslangic + idx * 75
            kart = pygame.Rect(100, y, EKRAN_GENISLIK - 200, 65)
            pygame.draw.rect(self.ekran, (40, 40, 70), kart, border_radius=10)
            if kart.collidepoint(fare):
                pygame.draw.rect(self.ekran, ACIK_MAVI, kart, 2, border_radius=10)
            else:
                pygame.draw.rect(self.ekran, GRI, kart, 1, border_radius=10)

            # Sepet önizleme (küçük dikdörtgen)
            preview = pygame.Rect(120, y + 12, 40, 25)
            pygame.draw.rect(self.ekran, bilgi["renk"], preview, border_radius=4)
            pygame.draw.rect(self.ekran, bilgi["ic"], pygame.Rect(124, y + 16, 32, 17), border_radius=3)

            isim_yazi = self.orta_font.render(renk_adi.capitalize(), True, BEYAZ)
            self.ekran.blit(isim_yazi, (180, y + 18))

            # Durum butonu
            if renk_adi == aktif:
                durum_yazi = self.kucuk_font.render("✓ Aktif", True, ACIK_YESIL)
                self.ekran.blit(durum_yazi, (EKRAN_GENISLIK - 230, y + 22))
            elif renk_adi in satin_alinanlar:
                sec_rect = pygame.Rect(EKRAN_GENISLIK - 250, y + 15, 100, 35)
                pygame.draw.rect(self.ekran, KOYU_YESIL, sec_rect, border_radius=6)
                sec_yazi = self.kucuk_font.render("Seç", True, BEYAZ)
                self.ekran.blit(sec_yazi,
                                (sec_rect.centerx - sec_yazi.get_width() // 2,
                                 sec_rect.centery - sec_yazi.get_height() // 2))
                buton_rects[renk_adi] = ("sec", sec_rect)
            else:
                al_rect = pygame.Rect(EKRAN_GENISLIK - 270, y + 15, 120, 35)
                yeterli = bakiye >= bilgi["fiyat"]
                renk = TURUNCU if yeterli else KOYU_GRI
                pygame.draw.rect(self.ekran, renk, al_rect, border_radius=6)
                fiyat_yazi = self.kucuk_font.render(f"🔒 {bilgi['fiyat']}p", True, BEYAZ if yeterli else GRI)
                self.ekran.blit(fiyat_yazi,
                                (al_rect.centerx - fiyat_yazi.get_width() // 2,
                                 al_rect.centery - fiyat_yazi.get_height() // 2))
                if yeterli:
                    buton_rects[renk_adi] = ("al", al_rect)

        # Geri butonu
        geri_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 80, EKRAN_YUKSEKLIK - 65, 160, 40)
        if geri_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, MAVI, geri_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (40, 80, 160), geri_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, geri_rect, 2, border_radius=10)
        geri_yazi = self.orta_font.render("← Geri", True, BEYAZ)
        self.ekran.blit(geri_yazi,
                        (geri_rect.centerx - geri_yazi.get_width() // 2,
                         geri_rect.centery - geri_yazi.get_height() // 2))

        return buton_rects, geri_rect

    # -------------------------------------------------------------------------
    # Upgrade (Yetenek Ağacı) Ekranı
    # -------------------------------------------------------------------------
    def _upgrade_ciz(self):
        """Kalıcı geliştirme satın alma ekranını çizer."""
        self._arkaplan_ciz()

        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.ekran.blit(overlay, (0, 0))

        # Panel
        panel_rect = pygame.Rect(50, 40, EKRAN_GENISLIK - 100, EKRAN_YUKSEKLIK - 80)
        pygame.draw.rect(self.ekran, (20, 30, 50), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, ACIK_YESIL, panel_rect, 2, border_radius=15)

        baslik = self.buyuk_font.render("⚡ Yetenek Ağacı", True, ACIK_YESIL)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 60))

        bakiye = self.veritabani.bakiye_al()
        bakiye_yazi = self.orta_font.render(f"💰 Bakiye: {bakiye} puan", True, BEYAZ)
        self.ekran.blit(bakiye_yazi, (EKRAN_GENISLIK // 2 - bakiye_yazi.get_width() // 2, 105))

        fare = pygame.mouse.get_pos()
        buton_rects = {}
        y_baslangic = 155

        for idx, (uid, tanim) in enumerate(UPGRADE_TANIMLARI.items()):
            y = y_baslangic + idx * 100
            kart = pygame.Rect(100, y, EKRAN_GENISLIK - 200, 85)
            pygame.draw.rect(self.ekran, (35, 45, 70), kart, border_radius=10)
            if kart.collidepoint(fare):
                pygame.draw.rect(self.ekran, ACIK_YESIL, kart, 2, border_radius=10)
            else:
                pygame.draw.rect(self.ekran, GRI, kart, 1, border_radius=10)

            mevcut_seviye = self.veritabani.upgrade_seviye_al(uid)
            maks = tanim["maks_seviye"]

            # İsim
            isim_yazi = self.orta_font.render(tanim["isim"], True, BEYAZ)
            self.ekran.blit(isim_yazi, (120, y + 10))

            # Seviye barı
            bar_x = 120
            bar_y = y + 45
            bar_w = 200
            bar_h = 14
            pygame.draw.rect(self.ekran, KOYU_GRI, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            if mevcut_seviye > 0:
                doluluk = int(bar_w * (mevcut_seviye / maks))
                pygame.draw.rect(self.ekran, ACIK_YESIL, (bar_x, bar_y, doluluk, bar_h), border_radius=4)
            pygame.draw.rect(self.ekran, BEYAZ, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
            seviye_txt = self.mini_font.render(f"Seviye {mevcut_seviye}/{maks}", True, BEYAZ)
            self.ekran.blit(seviye_txt, (bar_x + bar_w + 10, bar_y - 1))

            # Satın al butonu
            if mevcut_seviye < maks:
                fiyat = tanim["baz_fiyat"] + mevcut_seviye * tanim["artis"]
                yeterli = bakiye >= fiyat
                al_rect = pygame.Rect(EKRAN_GENISLIK - 270, y + 25, 130, 38)
                renk = ACIK_YESIL if yeterli else KOYU_GRI
                pygame.draw.rect(self.ekran, renk, al_rect, border_radius=8)
                fiyat_yazi = self.kucuk_font.render(f"⬆ {fiyat}p", True, BEYAZ if yeterli else GRI)
                self.ekran.blit(fiyat_yazi,
                                (al_rect.centerx - fiyat_yazi.get_width() // 2,
                                 al_rect.centery - fiyat_yazi.get_height() // 2))
                if yeterli:
                    buton_rects[uid] = al_rect
            else:
                maks_yazi = self.kucuk_font.render("✓ MAKS", True, ALTIN)
                self.ekran.blit(maks_yazi, (EKRAN_GENISLIK - 240, y + 32))

        # Geri butonu
        geri_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 80, EKRAN_YUKSEKLIK - 65, 160, 40)
        if geri_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, MAVI, geri_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (40, 80, 160), geri_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, geri_rect, 2, border_radius=10)
        geri_yazi = self.orta_font.render("← Geri", True, BEYAZ)
        self.ekran.blit(geri_yazi,
                        (geri_rect.centerx - geri_yazi.get_width() // 2,
                         geri_rect.centery - geri_yazi.get_height() // 2))

        return buton_rects, geri_rect

    # -------------------------------------------------------------------------
    # Oyun Bitti Ekranı
    # -------------------------------------------------------------------------
    def _bitti_ekrani_ciz(self):
        """Oyun bittiğinde gösterilen sonuç ve istatistik ekranını çizer."""
        self._arkaplan_ciz()

        # Yarı saydam karartma
        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.ekran.blit(overlay, (0, 0))

        # Genişletilmiş panel
        panel_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 220, 30, 440, 530)
        pygame.draw.rect(self.ekran, (30, 30, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, BEYAZ, panel_rect, 2, border_radius=15)

        # Başlık
        baslik = self.buyuk_font.render("OYUN BİTTİ!", True, KIRMIZI)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 45))

        # Skor
        skor_yazi = self.orta_font.render(f"Skorun: {self.son_skor}", True, BEYAZ)
        self.ekran.blit(skor_yazi, (EKRAN_GENISLIK // 2 - skor_yazi.get_width() // 2, 95))

        # Yeni rekor bildirimi
        if self.son_skor >= self.en_yuksek_skor and self.son_skor > 0:
            if (pygame.time.get_ticks() // 400) % 2 == 0:
                rekor = self.orta_font.render("★ YENİ REKOR! ★", True, SARI)
                self.ekran.blit(rekor, (EKRAN_GENISLIK // 2 - rekor.get_width() // 2, 125))

        # --- İstatistik Paneli ---
        stat_y = 160
        ayirici_renk = (80, 80, 120)
        pygame.draw.line(self.ekran, ayirici_renk,
                         (EKRAN_GENISLIK // 2 - 180, stat_y),
                         (EKRAN_GENISLIK // 2 + 180, stat_y), 1)
        stat_baslik = self.orta_font.render("İstatistikler", True, ACIK_MAVI)
        self.ekran.blit(stat_baslik, (EKRAN_GENISLIK // 2 - stat_baslik.get_width() // 2, stat_y + 5))

        # Süre hesaplama
        sure_saniye = getattr(self, 'toplam_kare', 0) / max(1, FPS)
        dakika = int(sure_saniye // 60)
        saniye = int(sure_saniye % 60)
        sure_str = f"{dakika}dk {saniye}sn" if dakika > 0 else f"{saniye}sn"

        istatistikler = [
            ("🍎  Toplanan Elma", str(getattr(self, 'toplanan_elma_sayisi', 0))),
            ("⭐  Toplanan Altın", str(getattr(self, 'toplanan_altin_sayisi', 0))),
            ("🔥  En Yüksek Kombo", f"x{getattr(self, 'en_yuksek_kombo', 0)}"),
            ("📈  Ulaşılan Seviye", str(self.zorluk_seviyesi)),
            ("⏱️  Süre", sure_str),
            ("🏆  En Yüksek Skor", str(self.en_yuksek_skor)),
        ]

        stat_y += 35
        sol_x = EKRAN_GENISLIK // 2 - 170
        sag_x = EKRAN_GENISLIK // 2 + 170
        for etiket, deger in istatistikler:
            etiket_yazi = self.kucuk_font.render(etiket, True, GRI)
            deger_yazi = self.kucuk_font.render(deger, True, BEYAZ)
            self.ekran.blit(etiket_yazi, (sol_x, stat_y))
            self.ekran.blit(deger_yazi, (sag_x - deger_yazi.get_width(), stat_y))
            stat_y += 28

        # Alt ayırıcı
        pygame.draw.line(self.ekran, ayirici_renk,
                         (EKRAN_GENISLIK // 2 - 180, stat_y + 5),
                         (EKRAN_GENISLIK // 2 + 180, stat_y + 5), 1)

        # Tekrar oyna butonu
        buton_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 130, stat_y + 20, 260, 50)
        fare = pygame.mouse.get_pos()
        if buton_rect.collidepoint(fare):
            pygame.draw.rect(self.ekran, MAVI, buton_rect, border_radius=10)
        else:
            pygame.draw.rect(self.ekran, (40, 80, 160), buton_rect, border_radius=10)
        pygame.draw.rect(self.ekran, BEYAZ, buton_rect, 2, border_radius=10)

        tekrar_yazi = self.orta_font.render("Tekrar Oyna", True, BEYAZ)
        self.ekran.blit(tekrar_yazi,
                        (buton_rect.centerx - tekrar_yazi.get_width() // 2,
                         buton_rect.centery - tekrar_yazi.get_height() // 2))

        # Tekrar İzle butonu (Replay)
        replay_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 130, stat_y + 78, 260, 42)
        replay_var = len(self.replay.kareler) > 0
        if replay_var:
            if replay_rect.collidepoint(fare):
                pygame.draw.rect(self.ekran, TURUNCU, replay_rect, border_radius=10)
            else:
                pygame.draw.rect(self.ekran, (160, 100, 20), replay_rect, border_radius=10)
            pygame.draw.rect(self.ekran, BEYAZ, replay_rect, 2, border_radius=10)
            replay_yazi = self.orta_font.render("▶ Tekrar İzle", True, BEYAZ)
        else:
            pygame.draw.rect(self.ekran, KOYU_GRI, replay_rect, border_radius=10)
            replay_yazi = self.orta_font.render("▶ Tekrar İzle", True, GRI)
        self.ekran.blit(replay_yazi,
                        (replay_rect.centerx - replay_yazi.get_width() // 2,
                         replay_rect.centery - replay_yazi.get_height() // 2))

        # Çıkış ipucu
        cikis = self.kucuk_font.render("ESC: Menü  |  ENTER: Tekrar  |  R: İzle", True, GRI)
        self.ekran.blit(cikis, (EKRAN_GENISLIK // 2 - cikis.get_width() // 2, stat_y + 130))

        return buton_rect, replay_rect

    # -------------------------------------------------------------------------
    # İsim Giriş Ekranı (Top 5'e Girenler İçin)
    # -------------------------------------------------------------------------
    def _isim_gir_ciz(self):
        """Top 5'e giren oyuncunun ismini girmesi için ekran."""
        self._arkaplan_ciz()

        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.ekran.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 220, 150, 440, 300)
        pygame.draw.rect(self.ekran, (30, 30, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, ALTIN, panel_rect, 2, border_radius=15)

        tebrik = self.buyuk_font.render("Tebrikler!", True, ALTIN)
        self.ekran.blit(tebrik, (EKRAN_GENISLIK // 2 - tebrik.get_width() // 2, 175))

        bilgi = self.orta_font.render(f"Skorun: {self.son_skor} - Top 5'e girdin!", True, BEYAZ)
        self.ekran.blit(bilgi, (EKRAN_GENISLIK // 2 - bilgi.get_width() // 2, 225))

        isim_label = self.orta_font.render("İsmini gir:", True, ACIK_MAVI)
        self.ekran.blit(isim_label, (EKRAN_GENISLIK // 2 - isim_label.get_width() // 2, 280))

        # İsim giriş kutusu
        kutu_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 150, 320, 300, 45)
        pygame.draw.rect(self.ekran, BEYAZ, kutu_rect, border_radius=8)
        pygame.draw.rect(self.ekran, ACIK_MAVI, kutu_rect, 2, border_radius=8)

        # İmleç yanıp sönme
        self.isim_imlec_zamanlayici += 1
        if self.isim_imlec_zamanlayici >= 30:
            self.isim_imlec_zamanlayici = 0
            self.isim_imlec_gorunsun = not self.isim_imlec_gorunsun

        imlec = "|" if self.isim_imlec_gorunsun else ""
        isim_yazi = self.orta_font.render(self.oyuncu_ismi + imlec, True, SIYAH)
        self.ekran.blit(isim_yazi, (kutu_rect.x + 10, kutu_rect.y + 8))

        ipucu = self.kucuk_font.render("ENTER tuşu ile onayla", True, GRI)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK // 2 - ipucu.get_width() // 2, 380))

    # -------------------------------------------------------------------------
    # Tekrar İzleme (Replay) Ekranı
    # -------------------------------------------------------------------------
    def _replay_ciz(self):
        """Kaydedilmiş oyun karelerini tekrar izleme modunda canlandırır.
        Yeni nesne üretmez — yalnızca kaydedilen kareleri oynatır."""
        kare = self.replay.sonraki_kare()
        if kare is None:
            self.durum = "bitti"
            return

        self._arkaplan_ciz()

        # Zemin (oyun alanı altta kalacak şekilde)
        zemin_y = EKRAN_YUKSEKLIK - 30
        pygame.draw.rect(self.ekran, KOYU_YESIL, (0, zemin_y, EKRAN_GENISLIK, 30))
        pygame.draw.rect(self.ekran, YESIL, (0, zemin_y, EKRAN_GENISLIK, 5))

        # Düşen nesneleri çiz (sadece kaydedilen pozisyonlardan, yeni nesne yok)
        nesne_renkleri = {
            "GoodItem": KIRMIZI,
            "BadItem": SIYAH,
            "GoldenItem": ALTIN,
            "HealItem": ACIK_YESIL,
            "TakipBomba": PEMBE,
            "MermiItem": ACIK_MAVI,
            "BossBomba": TURUNCU,
        }
        for (nx, ny, nw, nh, tip) in kare.nesneler:
            renk = nesne_renkleri.get(tip, GRI)
            merkez_x = int(nx + nw // 2)
            merkez_y = int(ny + nh // 2)
            yaricap = nw // 2
            if tip in ("GoodItem", "GoldenItem"):
                pygame.draw.circle(self.ekran, renk, (merkez_x, merkez_y), yaricap)
                pygame.draw.circle(self.ekran, (255, 255, 255), (merkez_x - 3, merkez_y - 3), yaricap // 4)
            elif tip in ("BadItem", "BossBomba", "TakipBomba"):
                pygame.draw.circle(self.ekran, KOYU_GRI, (merkez_x, merkez_y), yaricap)
                pygame.draw.circle(self.ekran, renk, (merkez_x, merkez_y), yaricap - 2)
            else:
                pygame.draw.circle(self.ekran, renk, (merkez_x, merkez_y), yaricap)

        # Sepetin pozisyonu (kaydedilen X ile)
        sepet_y = EKRAN_YUKSEKLIK - 70
        sepet_w = 100
        sepet_h = 50
        sepet_x = kare.sepet_x

        # Sepet çizimi (basit geometrik)
        govde = pygame.Rect(sepet_x, sepet_y + 10, sepet_w, sepet_h - 10)
        pygame.draw.rect(self.ekran, KAHVERENGI, govde, border_radius=6)
        ic = pygame.Rect(sepet_x + 5, sepet_y + 14, sepet_w - 10, sepet_h - 20)
        pygame.draw.rect(self.ekran, (180, 120, 60), ic, border_radius=4)
        pygame.draw.line(self.ekran, (100, 60, 20),
                         (sepet_x - 8, sepet_y + 10),
                         (sepet_x + sepet_w + 8, sepet_y + 10), 3)

        # --- Replay HUD (alt kısımda, oyun alanına binmez) ---
        # Alt bilgi paneli (zemin üstünde)
        alt_panel_h = 38
        alt_panel_y = EKRAN_YUKSEKLIK - alt_panel_h
        alt_panel = pygame.Surface((EKRAN_GENISLIK, alt_panel_h), pygame.SRCALPHA)
        alt_panel.fill((0, 0, 0, 180))
        self.ekran.blit(alt_panel, (0, alt_panel_y))

        # Replay etiketi (sol)
        replay_txt = self.orta_font.render("▶ TEKRAR İZLEME", True, TURUNCU)
        self.ekran.blit(replay_txt, (10, alt_panel_y + 6))

        # Skor ve can bilgisi (orta)
        skor_txt = self.kucuk_font.render(f"Skor: {kare.skor}  |  Can: {kare.can}", True, BEYAZ)
        self.ekran.blit(skor_txt, (EKRAN_GENISLIK // 2 - skor_txt.get_width() // 2, alt_panel_y + 10))

        # ESC ipucu (sağ)
        ipucu = self.mini_font.render("ESC: Geri Dön", True, GRI)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK - ipucu.get_width() - 10, alt_panel_y + 12))

        # İlerleme barı (en altta ince çubuk)
        if len(self.replay.kareler) > 0:
            ilerleme = self.replay.oynatma_indeks / len(self.replay.kareler)
            bar_y = EKRAN_YUKSEKLIK - 4
            pygame.draw.rect(self.ekran, KOYU_GRI, (0, bar_y, EKRAN_GENISLIK, 4))
            pygame.draw.rect(self.ekran, TURUNCU, (0, bar_y, int(EKRAN_GENISLIK * ilerleme), 4))

    # -------------------------------------------------------------------------
    # Tutorial (İlk Çalıştırma) Ekranı
    # -------------------------------------------------------------------------
    def _tutorial_ciz(self):
        """İlk kez oynayan kullanıcıya kontrolleri ve kuralları gösterir."""
        self.ekran.fill((20, 20, 40))

        # Başlık
        baslik = self.buyuk_font.render("Nasıl Oynanır?", True, ALTIN)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 40))

        # Talimatlar
        talimatlar = [
            ("← → / A D", "Sepeti sağa-sola hareket ettir"),
            ("🍎  Yeşil Elma", "+10 puan kazandırır"),
            ("⭐  Altın Elma", "+100 puan (nadir, hızlı düşer)"),
            ("💣  Bomba", "Can kaybedersin, kaçın!"),
            ("❤️  Can Paketi", "+1 can (çok nadir)"),
            ("🌬️  Rüzgar", "Nesneleri sağa-sola iter"),
            ("🔥  Kombo", "Art arda yakala → çarpan artar"),
            ("⚡  Fever Modu", "Kombo barı dolunca aktif olur"),
        ]

        y = 110
        for sembol, aciklama in talimatlar:
            sembol_yazi = self.orta_font.render(sembol, True, SARI)
            self.ekran.blit(sembol_yazi, (60, y))
            aciklama_yazi = self.kucuk_font.render(aciklama, True, BEYAZ)
            self.ekran.blit(aciklama_yazi, (280, y + 4))
            y += 42

        # İpucu
        ipucu = self.orta_font.render("Herhangi bir tuşa bas veya tıkla", True, ACIK_MAVI)
        alpha = int(127 + 128 * abs(math.sin(pygame.time.get_ticks() * 0.003)))
        ipucu.set_alpha(alpha)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK // 2 - ipucu.get_width() // 2, EKRAN_YUKSEKLIK - 70))

    # -------------------------------------------------------------------------
    # Ana Oyun Döngüsü
    # -------------------------------------------------------------------------
    def calistir(self):
        """
        Ana oyun döngüsü. Menü, oyun, isim girişi ve bitiş ekranlarını
        durum makinesine (state machine) göre yönetir.
        """
        calisiyor = True

        while calisiyor:
            # --- OLAY İŞLEME ---
            for olay in pygame.event.get():
                if olay.type == pygame.QUIT:
                    calisiyor = False

                if olay.type == pygame.KEYDOWN:
                    # --- İsim giriş durumu (özel klavye işleme) ---
                    if self.durum == "isim_gir":
                        if olay.key == pygame.K_RETURN:
                            isim = self.oyuncu_ismi.strip() or "Anonim"
                            self.veritabani.skor_ekle(isim, self.son_skor)
                            self.en_yuksek_skor = self.veritabani.en_yuksek_skor()
                            self.durum = "bitti"
                        elif olay.key == pygame.K_BACKSPACE:
                            self.oyuncu_ismi = self.oyuncu_ismi[:-1]
                        elif len(self.oyuncu_ismi) < 15:
                            if olay.unicode.isprintable() and olay.unicode:
                                self.oyuncu_ismi += olay.unicode
                    else:
                        # --- Diğer durumlar ---
                        if self.durum == "tutorial":
                            self.veritabani.ilk_calistirma_tamam()
                            self.durum = "menu"
                            continue

                        if olay.key == pygame.K_ESCAPE:
                            if self.durum in ("oyun", "bitti", "market", "upgrade", "replay"):
                                self.durum = "menu"
                                self.replay.oynatma_durdur()
                            else:
                                calisiyor = False

                        if olay.key == pygame.K_RETURN:
                            if self.durum == "menu":
                                self._oyunu_sifirla()
                                self.durum = "oyun"
                            elif self.durum == "bitti":
                                self._oyunu_sifirla()
                                self.durum = "oyun"

                        if olay.key == pygame.K_r and self.durum == "bitti":
                            if len(self.replay.kareler) > 0:
                                self.replay.oynatma_baslat()
                                self.durum = "replay"

                        if olay.key == pygame.K_m and self.durum == "menu":
                            self.durum = "market"

                        if olay.key == pygame.K_u and self.durum == "menu":
                            self.durum = "upgrade"

                if olay.type == pygame.MOUSEBUTTONDOWN and olay.button == 1:
                    if self.durum == "tutorial":
                        self.veritabani.ilk_calistirma_tamam()
                        self.durum = "menu"
                    elif self.durum == "menu":
                        basla_buton = pygame.Rect(EKRAN_GENISLIK // 2 - 120, 435, 240, 50)
                        market_buton = pygame.Rect(EKRAN_GENISLIK // 2 - 200, 495, 180, 40)
                        upgrade_buton = pygame.Rect(EKRAN_GENISLIK // 2 + 20, 495, 180, 40)
                        if basla_buton.collidepoint(olay.pos):
                            self._oyunu_sifirla()
                            self.durum = "oyun"
                        elif market_buton.collidepoint(olay.pos):
                            self.durum = "market"
                        elif upgrade_buton.collidepoint(olay.pos):
                            self.durum = "upgrade"
                    elif self.durum == "bitti":
                        # İstatistik paneli sonrasındaki buton pozisyonları
                        _stat_y = 160 + 35 + 6 * 28  # 363
                        buton = pygame.Rect(EKRAN_GENISLIK // 2 - 130, _stat_y + 20, 260, 50)
                        replay_buton = pygame.Rect(EKRAN_GENISLIK // 2 - 130, _stat_y + 78, 260, 42)
                        if buton.collidepoint(olay.pos):
                            self._oyunu_sifirla()
                            self.durum = "oyun"
                        elif replay_buton.collidepoint(olay.pos) and len(self.replay.kareler) > 0:
                            self.replay.oynatma_baslat()
                            self.durum = "replay"
                    elif self.durum == "market":
                        buton_rects, geri_rect = self._market_ciz()
                        if geri_rect.collidepoint(olay.pos):
                            self.durum = "menu"
                        else:
                            for renk_adi, (islem, rect) in buton_rects.items():
                                if rect.collidepoint(olay.pos):
                                    if islem == "al":
                                        self.veritabani.sepet_satin_al(renk_adi)
                                    elif islem == "sec":
                                        self.veritabani.aktif_sepet_ayarla(renk_adi)
                                        self.aktif_sepet_renk = renk_adi
                                    break
                    elif self.durum == "upgrade":
                        buton_rects, geri_rect = self._upgrade_ciz()
                        if geri_rect.collidepoint(olay.pos):
                            self.durum = "menu"
                        else:
                            for uid, rect in buton_rects.items():
                                if rect.collidepoint(olay.pos):
                                    self.veritabani.upgrade_satin_al(uid)
                                    break

            # --- DURUM MAKİNESİ ---
            if self.durum == "tutorial":
                self._tutorial_ciz()

            elif self.durum == "menu":
                self._menu_ciz()

            elif self.durum == "oyun":
                self._oyun_guncelle()
                self._oyun_ciz()

            elif self.durum == "isim_gir":
                self._isim_gir_ciz()

            elif self.durum == "bitti":
                self._bitti_ekrani_ciz()

            elif self.durum == "market":
                self._market_ciz()

            elif self.durum == "upgrade":
                self._upgrade_ciz()

            elif self.durum == "replay":
                self._replay_ciz()

            pygame.display.flip()
            self.saat.tick(FPS)

        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------------------
    # Oyun Güncelleme (Her Karede Çalışır)
    # -------------------------------------------------------------------------
    def _oyun_guncelle(self):
        """
        Oyunun her karesinde çağrılır.
        Sepet hareketi, nesne üretimi, güncelleme, çarpışma ve
        zorluk ayarını yönetir.
        """
        self.toplam_kare += 1

        # --- Rüzgar ve yağmur güncelle ---
        self.ruzgar.guncelle()
        self.yagmur.guncelle()

        # --- Dinamik zorluk motoru güncelle ---
        self.zorluk_motoru.guncelle()
        # Rüzgar hedefini dinamik zorluk motoruyla düzelt (±3 sınırı)
        hedef_duzeltilmis = self.zorluk_motoru.ruzgar_siddeti_al(self.ruzgar.hedef)
        if hedef_duzeltilmis is not None:
            self.ruzgar.hedef = max(-3.0, min(3.0, float(hedef_duzeltilmis)))

        # --- Bölge (Biome) güncelle (her 2000 puanda değişir, fade geçiş) ---
        yeni_bolge = min(len(BOLGE_TANIMLARI) - 1, self.skor // 2000)
        if yeni_bolge != self.aktif_bolge and self.bolge_fade_durum is None:
            self.bolge_fade_durum = "karart"
            self.bolge_fade_hedef = yeni_bolge
            self.bolge_fade_alpha = 0

        # Fade animasyonu güncelle
        if self.bolge_fade_durum == "karart":
            self.bolge_fade_alpha = min(255, self.bolge_fade_alpha + 8)
            if self.bolge_fade_alpha >= 255:
                self.aktif_bolge = self.bolge_fade_hedef
                bolge_isim = BOLGE_TANIMLARI[self.aktif_bolge]["isim"]
                self.duyurular.append(Duyuru(f"BÖLGE: {bolge_isim}!", ACIK_MAVI, 100))
                self.bolge_fade_durum = "aydinlat"
        elif self.bolge_fade_durum == "aydinlat":
            self.bolge_fade_alpha = max(0, self.bolge_fade_alpha - 6)
            if self.bolge_fade_alpha <= 0:
                self.bolge_fade_durum = None
                self.bolge_fade_alpha = 0

        yercekim = BOLGE_TANIMLARI[self.aktif_bolge]["yercekim"]

        # Sepet hareketi (kaygan zemin: yağmurda veya buz bölgesinde)
        tuslar = pygame.key.get_pressed()
        kaygan = self.yagmur.aktif or self.aktif_bolge == 2  # Buz bölgesi
        self.sepet.hareket_et(tuslar, kaygan_zemin=kaygan)

        # Yeni nesne üretimi
        self._nesne_uret()

        # Nesneleri güncelle (rüzgar + yerçekimi)
        sepet_x = self.sepet.x + self.sepet.base_genislik // 2
        for nesne in self.dusen_nesneler:
            if isinstance(nesne, TakipBomba):
                nesne.guncelle(sepet_x=sepet_x)
            else:
                nesne.guncelle(ruzgar_siddet=self.ruzgar.siddet, yercekim_carpan=yercekim)

        # Çarpışma kontrolü
        self._carpismalari_kontrol_et()

        # Aktif olmayan nesneleri listeden kaldır
        self.dusen_nesneler = [n for n in self.dusen_nesneler if n.aktif]

        # Zorluğu ayarla
        self._zorluk_ayarla()

        # --- Replay kaydı: her kareyi kaydet ---
        self.replay.kare_kaydet(
            self.sepet, self.dusen_nesneler,
            self.skor, self.can, self.kombo_sayac, self.fever_aktif
        )

        # --- Ghost kayıt: sepet X pozisyonunu kaydet ---
        self.ghost_kayit.append((self.toplam_kare, self.sepet.x))

        # Parçacıkları güncelle
        self.parcacik_yonetici.guncelle()

        # Paralaks katmanları güncelle
        for katman in self.paralaks_katmanlar:
            katman.guncelle()

        # Kalp kırılma efektleri güncelle
        for kk in self.kalp_kirilmalari:
            kk.guncelle()
        self.kalp_kirilmalari = [kk for kk in self.kalp_kirilmalari if kk.aktif]

        # Fever modu zamanlayıcı
        if self.fever_aktif:
            self.fever_kalan_kare -= 1
            self.fever_parlama += 0.1
            if self.fever_kalan_kare <= 0:
                self.fever_aktif = False
                self.kombo_bar = 0.0

        # --- Gece/Gündüz döngüsü (her 1000 puanda bir değişir) ---
        self.gece_modu = (self.skor // 1000) % 2 == 1

        # --- Boss aktivasyonu (5000 puan) ---
        if self.skor >= 5000 and not self.boss_aktif and not self.boss_yenildi:
            self.boss_aktif = True
            self.boss = Boss()
            self.duyurular.append(Duyuru("BOSS FIGHT!", KIRMIZI, 120))

        # --- Boss güncelleme ---
        if self.boss_aktif and self.boss:
            self.boss.guncelle()
            # Boss bomba fırlatsın
            if self.boss.bomba_atabilir():
                bx = int(self.boss.x) + self.boss.genislik // 2
                by = int(self.boss.y) + self.boss.yukseklik
                hedef_x = self.sepet.x + self.sepet.base_genislik // 2
                hedef_y = self.sepet.y + self.sepet.base_yukseklik // 2
                self.boss_bombalar.append(BossBomba(bx, by, hedef_x, hedef_y))
            # Boss bombaları güncelle
            for b in self.boss_bombalar:
                b.guncelle()
            self.boss_bombalar = [b for b in self.boss_bombalar if b.aktif]
            # Boss öldü mü?
            if not self.boss.aktif:
                self.boss_aktif = False
                self.boss_yenildi = True
                self.skor += 500  # Boss ödülü
                self.boss_bombalar.clear()
                self.parcacik_yonetici.patlama_ekle(
                    int(self.boss.x) + 60, int(self.boss.y) + 40, ALTIN, 40)
                self.duyurular.append(Duyuru("BOSS DEFEATED!", ACIK_YESIL, 120))

        # --- Duyuruları güncelle ---
        for d in self.duyurular:
            d.guncelle()
        self.duyurular = [d for d in self.duyurular if d.aktif]

        # --- Hırsız kuşları güncelle ---
        for kus in self.hirsiz_kuslar:
            kus.guncelle(self.dusen_nesneler)
        self.hirsiz_kuslar = [k for k in self.hirsiz_kuslar if k.aktif]

        # --- Görev bildirimlerini güncelle ---
        for g in self.gorev_bildirimleri:
            g.guncelle()
        self.gorev_bildirimleri = [g for g in self.gorev_bildirimleri if g.aktif]

        # --- Görev (Achievement) kontrol ---
        self._gorev_kontrol()

        # Can bittiyse oyunu bitir
        if self.can <= 0:
            self.can = 0
            self.son_skor = self.skor
            eski_en_yuksek = self.en_yuksek_skor
            self.en_yuksek_skor = self.veritabani.en_yuksek_skor()
            # Yeni rekor duyurusu
            if self.son_skor > eski_en_yuksek and self.son_skor > 0:
                self.duyurular.append(Duyuru("NEW RECORD!", ALTIN, 150))
                if self.rekor_ses:
                    self.rekor_ses.play()
            # Kazanılan skoru bakiyeye ekle
            if self.son_skor > 0:
                self.veritabani.bakiye_guncelle(self.son_skor)

            # --- Ghost verisini kaydet (rekor ise) ---
            if self.son_skor > 0:
                ghost_temp = GhostSepet()
                ghost_temp.hareketler = self.ghost_kayit
                ghost_json = ghost_temp.veriyi_json_al()
                self.veritabani.ghost_kaydet(self.son_skor, ghost_json)

            # --- API'ye skor gönder ---
            if self.api_yoneticisi and self.son_skor > 0:
                sure_saniye = self.toplam_kare / FPS
                skor_veri = self.api_yoneticisi.skor_json_olustur(
                    isim="Oyuncu",
                    skor=self.son_skor,
                    seviye=self.zorluk_seviyesi,
                    sure_saniye=sure_saniye,
                    ekstra={
                        "toplanan_elma": self.toplanan_elma_sayisi,
                        "toplanan_altin": self.toplanan_altin_sayisi,
                        "kacirma_orani": round(self.zorluk_motoru.kacirma_orani, 3),
                    }
                )
                self.api_yoneticisi.api_ye_gonder(skor_veri)
                self.api_yoneticisi.json_dosyaya_aktar()

            # Skor ilk 5'e giriyorsa isim sor
            if self.son_skor > 0 and self.veritabani.ilk_5e_girer_mi(self.son_skor):
                self.durum = "isim_gir"
            else:
                self.durum = "bitti"

    # -------------------------------------------------------------------------
    # Oyun Çizimi
    # -------------------------------------------------------------------------
    def _oyun_ciz(self):
        """Oyun ekranındaki tüm öğeleri çizer (ekran sarsıntısı destekli)."""
        hedef = self.oyun_surface
        hedef.fill(SIYAH)

        # Arka plan (paralaks)
        self._arkaplan_ciz(hedef=hedef)

        # Düşen nesneler
        for nesne in self.dusen_nesneler:
            nesne.ciz(hedef)

        # Boss bombalar
        for bomba in self.boss_bombalar:
            bomba.ciz(hedef)

        # Boss
        if self.boss_aktif and self.boss:
            self.boss.ciz(hedef)

        # Sepet
        self.sepet.ciz(hedef)

        # --- Ghost (Hayalet) Sepet ---
        if self.ghost.aktif:
            self.ghost.ciz(
                hedef, self.toplam_kare,
                self.sepet.base_genislik, self.sepet.base_yukseklik,
                self.sepet.y
            )

        # Hırsız kuşlar
        for kus in self.hirsiz_kuslar:
            kus.ciz(hedef)

        # Yağmur efekti
        self.yagmur.ciz(hedef)

        # Rüzgar göstergesi
        self.ruzgar.ciz(hedef, self.mini_font)

        # Parçacık efektleri
        self.parcacik_yonetici.ciz(hedef)

        # --- Gece modu: Dinamik ışık haleleri + spotlight ---
        if self.gece_modu:
            # Önce nesnelerin ışık halelerini additif blend ile çiz
            isik_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            isik_surface.fill((0, 0, 0, 0))
            for nesne in self.dusen_nesneler:
                if not nesne.aktif:
                    continue
                cx = int(nesne.x + nesne.genislik // 2)
                cy = int(nesne.y + nesne.yukseklik // 2)
                # Her nesne türüne farklı renk hale
                if isinstance(nesne, GoldenItem):
                    hale_renk = (60, 50, 10, 50)
                    hale_r = 30
                elif isinstance(nesne, GoodItem):
                    hale_renk = (50, 15, 15, 40)
                    hale_r = 24
                elif isinstance(nesne, HealItem):
                    hale_renk = (10, 50, 20, 45)
                    hale_r = 26
                elif isinstance(nesne, (BadItem, TakipBomba)):
                    hale_renk = (50, 20, 0, 35)
                    hale_r = 22
                else:
                    hale_renk = (30, 30, 40, 30)
                    hale_r = 20
                pygame.draw.circle(isik_surface, hale_renk, (cx, cy), hale_r)
            # Sepet ışığı
            scx = int(self.sepet.x + self.sepet.base_genislik // 2)
            scy = int(self.sepet.y + self.sepet.base_yukseklik // 2)
            pygame.draw.circle(isik_surface, (40, 35, 20, 50), (scx, scy), 50)
            hedef.blit(isik_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # Karanlık katmanı + spotlight
            self.gece_surface.fill((0, 0, 0, 160))
            sepet_cx = self.sepet.x + self.sepet.base_genislik // 2
            sepet_cy = self.sepet.y + self.sepet.base_yukseklik // 2
            isik = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            pygame.draw.circle(isik, (0, 0, 0, 160), (sepet_cx, sepet_cy), self.isik_yaricap)
            self.gece_surface.blit(isik, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            hedef.blit(self.gece_surface, (0, 0))

        # HUD (skor, can vb.) - gece katmanının üstünde
        self._hud_ciz(hedef=hedef)

        # Duyurular (Announcer)
        for d in self.duyurular:
            d.ciz(hedef, self.buyuk_font)

        # Görev bildirimleri
        for g in self.gorev_bildirimleri:
            g.ciz(hedef, self.buyuk_font, self.kucuk_font)

        # --- Bölge geçiş fade efekti ---
        fade_alpha = getattr(self, 'bolge_fade_alpha', 0)
        if fade_alpha > 0:
            fade_surf = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, min(255, fade_alpha)))
            hedef.blit(fade_surf, (0, 0))

        # Ekran sarsıntısı offseti ile ana ekrana blit
        ox, oy = self.ekran_sarsintisi.offset_al()
        self.ekran.fill(SIYAH)
        self.ekran.blit(hedef, (ox, oy))


# =============================================================================
# PROGRAMIN GİRİŞ NOKTASI
# =============================================================================
if __name__ == "__main__":
    oyun = GameManager()
    oyun.calistir()
