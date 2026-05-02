# =============================================================================
# STATE HANDLERS — Menü, Market, Yetenek ve Bitiş Ekranı Çizimleri
# =============================================================================
import pygame
import math
from settings import (EKRAN_GENISLIK, EKRAN_YUKSEKLIK, BEYAZ, SARI, ALTIN,
                      GRI, KOYU_GRI, KIRMIZI, YESIL, KOYU_YESIL, ACIK_YESIL,
                      MAVI, ACIK_MAVI, TURUNCU, SEPET_RENKLERI, UPGRADE_TANIMLARI,
                      PEMBE)


class StateHandlersMixin:
    """GameManager için oyun durumlarının (menü, market, vb.) ekranlarını çizen mixin sınıfı."""

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

    def _bitti_ekrani_ciz(self):
        """Oyun bittiğinde gösterilen sonuç ve istatistik ekranını çizer."""
        self._arkaplan_ciz()

        overlay = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.ekran.blit(overlay, (0, 0))

        # Genişletilmiş panel
        panel_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 220, 30, 440, 530)
        pygame.draw.rect(self.ekran, (30, 30, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.ekran, BEYAZ, panel_rect, 2, border_radius=15)

        baslik = self.buyuk_font.render("OYUN BİTTİ!", True, KIRMIZI)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 45))

        skor_yazi = self.orta_font.render(f"Skorun: {self.son_skor}", True, BEYAZ)
        self.ekran.blit(skor_yazi, (EKRAN_GENISLIK // 2 - skor_yazi.get_width() // 2, 95))

        # Yeni rekor bildirimi
        if getattr(self, 'son_skor', 0) >= getattr(self, 'en_yuksek_skor', 0) and getattr(self, 'son_skor', 0) > 0:
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

        import settings
        sure_saniye = getattr(self, 'toplam_kare', 0) / max(1, getattr(settings, 'FPS', 60))
        dakika = int(sure_saniye // 60)
        saniye = int(sure_saniye % 60)
        sure_str = f"{dakika}dk {saniye}sn" if dakika > 0 else f"{saniye}sn"

        istatistikler = [
            ("🍎  Toplanan Elma", str(getattr(self, 'toplanan_elma_sayisi', 0))),
            ("⭐  Toplanan Altın", str(getattr(self, 'toplanan_altin_sayisi', 0))),
            ("🔥  En Yüksek Kombo", f"x{getattr(self, 'en_yuksek_kombo', 0)}"),
            ("📈  Ulaşılan Seviye", str(getattr(self, 'zorluk_seviyesi', 1))),
            ("⏱️  Süre", sure_str),
            ("🏆  En Yüksek Skor", str(getattr(self, 'en_yuksek_skor', 0))),
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

        cikis = self.kucuk_font.render("ESC: Menü  |  ENTER: Tekrar  |  R: İzle", True, GRI)
        self.ekran.blit(cikis, (EKRAN_GENISLIK // 2 - cikis.get_width() // 2, stat_y + 130))

        return buton_rect, replay_rect

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

        kutu_rect = pygame.Rect(EKRAN_GENISLIK // 2 - 150, 320, 300, 45)
        pygame.draw.rect(self.ekran, BEYAZ, kutu_rect, border_radius=8)
        pygame.draw.rect(self.ekran, ACIK_MAVI, kutu_rect, 2, border_radius=8)

        self.isim_imlec_zamanlayici += 1
        if self.isim_imlec_zamanlayici >= 30:
            self.isim_imlec_zamanlayici = 0
            self.isim_imlec_gorunsun = not self.isim_imlec_gorunsun

        imlec = "|" if getattr(self, 'isim_imlec_gorunsun', True) else ""
        isim_yazi = self.orta_font.render(getattr(self, 'oyuncu_ismi', "") + imlec, True, (0, 0, 0))
        self.ekran.blit(isim_yazi, (kutu_rect.x + 10, kutu_rect.y + 8))

        ipucu = self.kucuk_font.render("ENTER tuşu ile onayla", True, GRI)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK // 2 - ipucu.get_width() // 2, 380))

    def _replay_ciz(self):
        """Kaydedilmiş oyun karelerini tekrar izleme modunda canlandırır."""
        kare = self.replay.sonraki_kare()
        if kare is None:
            self.durum = "bitti"
            return

        self._arkaplan_ciz()

        zemin_y = EKRAN_YUKSEKLIK - 30
        pygame.draw.rect(self.ekran, KOYU_YESIL, (0, zemin_y, EKRAN_GENISLIK, 30))
        pygame.draw.rect(self.ekran, YESIL, (0, zemin_y, EKRAN_GENISLIK, 5))

        nesne_renkleri = {
            "GoodItem": KIRMIZI,
            "BadItem": (0, 0, 0),
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

        sepet_y = EKRAN_YUKSEKLIK - 70
        sepet_w = 100
        sepet_h = 50
        sepet_x = kare.sepet_x

        govde = pygame.Rect(sepet_x, sepet_y + 10, sepet_w, sepet_h - 10)
        pygame.draw.rect(self.ekran, (139, 90, 43), govde, border_radius=6) # KAHVERENGI
        ic = pygame.Rect(sepet_x + 5, sepet_y + 14, sepet_w - 10, sepet_h - 20)
        pygame.draw.rect(self.ekran, (180, 120, 60), ic, border_radius=4)
        pygame.draw.line(self.ekran, (100, 60, 20),
                         (sepet_x - 8, sepet_y + 10),
                         (sepet_x + sepet_w + 8, sepet_y + 10), 3)

        alt_panel_h = 38
        alt_panel_y = EKRAN_YUKSEKLIK - alt_panel_h
        alt_panel = pygame.Surface((EKRAN_GENISLIK, alt_panel_h), pygame.SRCALPHA)
        alt_panel.fill((0, 0, 0, 180))
        self.ekran.blit(alt_panel, (0, alt_panel_y))

        replay_txt = self.orta_font.render("▶ TEKRAR İZLEME", True, TURUNCU)
        self.ekran.blit(replay_txt, (10, alt_panel_y + 6))

        skor_txt = self.kucuk_font.render(f"Skor: {kare.skor}  |  Can: {kare.can}", True, BEYAZ)
        self.ekran.blit(skor_txt, (EKRAN_GENISLIK // 2 - skor_txt.get_width() // 2, alt_panel_y + 10))

        ipucu = self.mini_font.render("ESC: Geri Dön", True, GRI)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK - ipucu.get_width() - 10, alt_panel_y + 12))

        if len(self.replay.kareler) > 0:
            ilerleme = self.replay.oynatma_indeks / len(self.replay.kareler)
            bar_y = EKRAN_YUKSEKLIK - 4
            pygame.draw.rect(self.ekran, KOYU_GRI, (0, bar_y, EKRAN_GENISLIK, 4))
            pygame.draw.rect(self.ekran, TURUNCU, (0, bar_y, int(EKRAN_GENISLIK * ilerleme), 4))

    def _tutorial_ciz(self):
        """İlk kez oynayan kullanıcıya kontrolleri ve kuralları gösterir."""
        self.ekran.fill((20, 20, 40))

        baslik = self.buyuk_font.render("Nasıl Oynanır?", True, ALTIN)
        self.ekran.blit(baslik, (EKRAN_GENISLIK // 2 - baslik.get_width() // 2, 40))

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

        ipucu = self.orta_font.render("Herhangi bir tuşa bas veya tıkla", True, ACIK_MAVI)
        alpha = int(127 + 128 * abs(math.sin(pygame.time.get_ticks() * 0.003)))
        ipucu.set_alpha(alpha)
        self.ekran.blit(ipucu, (EKRAN_GENISLIK // 2 - ipucu.get_width() // 2, EKRAN_YUKSEKLIK - 70))
