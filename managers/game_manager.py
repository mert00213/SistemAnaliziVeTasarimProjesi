# =============================================================================
# GAME MANAGER — Oyun Yöneticisi ve Ana Döngü
# =============================================================================
import pygame
import os
import random
import math
import sys

from settings import (EKRAN_GENISLIK, EKRAN_YUKSEKLIK, FPS, MAKS_CAN,
                      BEYAZ, SIYAH, KIRMIZI, YESIL, ALTIN, ACIK_YESIL,
                      TURUNCU, ACIK_MAVI, BOLGE_TANIMLARI, SARI)

from database import SkorVeritabani
from resource_path import ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR, DB_PATH

from entities.basket import Basket
from entities.falling_items import GoodItem, BadItem, GoldenItem, HealItem
from entities.boss import Boss, BossBomba, MermiItem
from entities.special_items import TakipBomba, HirsizKus
from entities.ghost import ReplaySystem

from systems.weather import RuzgarSistemi, YagmurSistemi
from systems.difficulty import DinamikZorlukMotoru
from systems.particles import ParticleManager
from systems.effects import EkranSarsintisi, KalpKirilma, Duyuru, GorevBildirimi
from systems.parallax import ParalaksKatman, bulut_ciz, dag_ciz
from systems.api import SkorAPIYoneticisi

from managers.renderer import RendererMixin
from managers.state_handlers import StateHandlersMixin


class GameManager(RendererMixin, StateHandlersMixin):
    """
    Oyunun ana yönetici sınıfı.
    Oyun döngüsü, skor takibi, ekran yönetimi, nesne üretimi
    ve çarpışma tespiti bu sınıf tarafından yönetilir.
    """

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Ekran ve saat ayarları
        self.ekran = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.RESIZABLE | pygame.SCALED)
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
            pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "arkaplan.mp3"))
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
            self.bomba_ses = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "bomba.mp3"))
        except Exception:
            pass
        ses_ekstra = {"kombo_ses": "combo.wav", "rekor_ses": "record.wav",
                      "gorev_ses": "goal.wav", "boss_ses": "boss_hit.wav"}
        for attr, dosya in ses_ekstra.items():
            try:
                yol = os.path.join(SOUNDS_DIR, dosya)
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
            gorsel_haritasi = {
                "sepet": ("sepet.png", (100, 50)),
                "elma": ("elma.png", (34, 34)),
                "bomba": ("bomba.png", (34, 34)),
                "kalp": ("kalp.png", (28, 28)),
                "bulut": ("bulut.png", (EKRAN_GENISLIK, EKRAN_YUKSEKLIK)),
                "dag": ("dag.png", (EKRAN_GENISLIK, EKRAN_YUKSEKLIK)),
            }
            for anahtar, (dosya, boyut) in gorsel_haritasi.items():
                yol = os.path.join(IMAGES_DIR, dosya)
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
            ParalaksKatman(0.3, gorsel=self.bulut_img, cizim_fonk=bulut_ciz),
            ParalaksKatman(0.7, gorsel=self.dag_img, cizim_fonk=dag_ciz),
        ]

        # --- Ekran sarsıntısı ---
        self.ekran_sarsintisi = EkranSarsintisi()

        # --- Veritabanı ---
        self.veritabani = SkorVeritabani(DB_PATH)

        # Oyun durumu: "menu", "oyun", "isim_gir", "bitti", "market", "tutorial", "upgrade"
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
            for i, bolge in enumerate(BOLGE_TANIMLARI):
                yol = os.path.join(IMAGES_DIR, bolge["dosya"])
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


        # --- Dinamik Zorluk Motoru ---
        self.zorluk_motoru = DinamikZorlukMotoru()

        # --- Global API Yöneticisi ---
        self.api_yoneticisi = None  # Veritabanı hazır olduktan sonra oluşturulur

        self._oyunu_sifirla()

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

        # Elastik skor titreşimi ve istatistik izleme
        self._skor_titresim = 0
        self.en_yuksek_kombo = 0

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
        
        # Oyunun mevcut ayarlarında bir görev veya duyuru olabilmesi için
        from settings import GOREV_TANIMLARI
        
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
        from settings import GOREV_TANIMLARI
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
                            self.veritabani.skor_ekle(isim, getattr(self, 'son_skor', 0))
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
                        _stat_y = 160 + 35 + 6 * 28
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
        if getattr(self, 'boss_aktif', False):
            self.gece_modu = False

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
            eski_en_yuksek = getattr(self, 'en_yuksek_skor', 0)
            self.en_yuksek_skor = self.veritabani.en_yuksek_skor()
            # Yeni rekor duyurusu
            if self.son_skor > eski_en_yuksek and self.son_skor > 0:
                self.duyurular.append(Duyuru("NEW RECORD!", ALTIN, 150))
                if self.rekor_ses:
                    self.rekor_ses.play()
            # Kazanılan skoru bakiyeye ekle
            if self.son_skor > 0:
                self.veritabani.bakiye_guncelle(self.son_skor)

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
