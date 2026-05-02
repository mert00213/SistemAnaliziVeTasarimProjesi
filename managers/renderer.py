# =============================================================================
# RENDERER — Çizim Mixin'i (Arka Plan, HUD, Oyun Ekranı)
# =============================================================================
import pygame
import math
from settings import *
from entities.falling_items import GoodItem, BadItem, GoldenItem, HealItem
from entities.special_items import TakipBomba


class RendererMixin:
    """GameManager için çizim metotlarını sağlayan mixin sınıfı."""

    def _arkaplan_ciz(self, hedef=None):
        ekran = hedef or self.ekran
        bolge_idx = getattr(self, 'aktif_bolge', 0)
        if bolge_idx in getattr(self, 'bolge_gorselleri', {}):
            ekran.blit(self.bolge_gorselleri[bolge_idx], (0, 0))
        else:
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
        fever_mod = getattr(self, 'fever_aktif', False)
        ruzgar_s = getattr(self.ruzgar, 'siddet', 0.0) if hasattr(self, 'ruzgar') else 0.0
        for katman in self.paralaks_katmanlar:
            katman.ciz(ekran, fever_mod, ruzgar_s)
        zemin_y = EKRAN_YUKSEKLIK - 30
        bolge = BOLGE_TANIMLARI[bolge_idx]
        zemin_renk = (60, 30, 40) if fever_mod else bolge["zemin"]
        cimen_renk = (100, 50, 60) if fever_mod else bolge["cimen"]
        pygame.draw.rect(ekran, zemin_renk, (0, zemin_y, EKRAN_GENISLIK, 30))
        pygame.draw.rect(ekran, cimen_renk, (0, zemin_y, EKRAN_GENISLIK, 5))

    def _hud_ciz(self, hedef=None):
        ekran = hedef or self.ekran
        panel = pygame.Surface((EKRAN_GENISLIK, 45), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        ekran.blit(panel, (0, 0))

        if self.kombo_sayac >= 20:
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

        zorluk_yazi = self.kucuk_font.render(f"Seviye: {self.zorluk_seviyesi}", True, ACIK_MAVI)
        ekran.blit(zorluk_yazi, (250, 12))

        bar_x, bar_y, bar_w, bar_h = 360, 14, 100, 16
        pygame.draw.rect(ekran, KOYU_GRI, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        doluluk = int(bar_w * self.kombo_bar)
        if doluluk > 0:
            bar_renk = ALTIN if self.fever_aktif else TURUNCU
            pygame.draw.rect(ekran, bar_renk, (bar_x, bar_y, doluluk, bar_h), border_radius=4)
        pygame.draw.rect(ekran, BEYAZ, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        kombo_label = self.mini_font.render("FEVER" if self.fever_aktif else f"Kombo: {self.kombo_sayac}", True, BEYAZ)
        ekran.blit(kombo_label, (bar_x + bar_w + 5, bar_y - 1))

        if self.fever_aktif:
            kalan_sn = self.fever_kalan_kare / 60.0
            fever_txt = self.kucuk_font.render(f"★ FEVER MODE {kalan_sn:.1f}s ★", True, ALTIN)
            ekran.blit(fever_txt, (EKRAN_GENISLIK // 2 - fever_txt.get_width() // 2, 48))

        for i in range(self.can):
            kalp_x = EKRAN_GENISLIK - 40 - i * 35
            kalp_y = 8
            if self.kalp_img:
                ekran.blit(self.kalp_img, (kalp_x - 5, kalp_y))
            else:
                pygame.draw.circle(ekran, KIRMIZI, (kalp_x, kalp_y + 5), 8)
                pygame.draw.circle(ekran, KIRMIZI, (kalp_x + 10, kalp_y + 5), 8)
                pygame.draw.polygon(ekran, KIRMIZI, [
                    (kalp_x - 8, kalp_y + 6), (kalp_x + 18, kalp_y + 6), (kalp_x + 5, kalp_y + 22)])

        for kk in self.kalp_kirilmalari:
            kk.ciz(ekran)

        if self.boss_aktif and self.boss:
            boss_txt = self.orta_font.render("💀 BOSS FIGHT!", True, KIRMIZI)
            ekran.blit(boss_txt, (EKRAN_GENISLIK // 2 - boss_txt.get_width() // 2, 48))
        elif self.gece_modu:
            gece_txt = self.mini_font.render("🌙 Gece Modu", True, (150, 150, 200))
            ekran.blit(gece_txt, (10, 48))

        bolge_idx = getattr(self, 'aktif_bolge', 0)
        bolge_isim = BOLGE_TANIMLARI[bolge_idx]["isim"]
        bolge_txt = self.mini_font.render(f"🌍 {bolge_isim}", True, BEYAZ)
        ekran.blit(bolge_txt, (EKRAN_GENISLIK - bolge_txt.get_width() - 10, 48))

        kacirma = self.zorluk_motoru.kacirma_orani
        if kacirma > 0.50:
            zorluk_renk, zorluk_etiket = ACIK_YESIL, "Kolay"
        elif kacirma < 0.20:
            zorluk_renk, zorluk_etiket = KIRMIZI, "Zor"
        else:
            zorluk_renk, zorluk_etiket = SARI, "Normal"
        dz_txt = self.mini_font.render(f"⚙ {zorluk_etiket} ({kacirma:.0%})", True, zorluk_renk)
        ekran.blit(dz_txt, (10, 65))

    def _oyun_ciz(self):
        hedef = self.oyun_surface
        hedef.fill(SIYAH)
        self._arkaplan_ciz(hedef=hedef)
        for nesne in self.dusen_nesneler:
            nesne.ciz(hedef)
        for bomba in self.boss_bombalar:
            bomba.ciz(hedef)
        if self.boss_aktif and self.boss:
            self.boss.ciz(hedef)
        self.sepet.ciz(hedef)
        for kus in self.hirsiz_kuslar:
            kus.ciz(hedef)
        self.yagmur.ciz(hedef)
        self.ruzgar.ciz(hedef, self.mini_font)
        self.parcacik_yonetici.ciz(hedef)

        if self.gece_modu:
            isik_surface = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            isik_surface.fill((0, 0, 0, 0))
            for nesne in self.dusen_nesneler:
                if not nesne.aktif:
                    continue
                cx = int(nesne.x + nesne.genislik // 2)
                cy = int(nesne.y + nesne.yukseklik // 2)
                if isinstance(nesne, GoldenItem):
                    hale_renk, hale_r = (60, 50, 10, 50), 30
                elif isinstance(nesne, GoodItem):
                    hale_renk, hale_r = (50, 15, 15, 40), 24
                elif isinstance(nesne, HealItem):
                    hale_renk, hale_r = (10, 50, 20, 45), 26
                elif isinstance(nesne, (BadItem, TakipBomba)):
                    hale_renk, hale_r = (50, 20, 0, 35), 22
                else:
                    hale_renk, hale_r = (30, 30, 40, 30), 20
                pygame.draw.circle(isik_surface, hale_renk, (cx, cy), hale_r)
            scx = int(self.sepet.x + self.sepet.base_genislik // 2)
            scy = int(self.sepet.y + self.sepet.base_yukseklik // 2)
            pygame.draw.circle(isik_surface, (40, 35, 20, 50), (scx, scy), 50)
            hedef.blit(isik_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.gece_surface.fill((0, 0, 0, 160))
            sepet_cx = self.sepet.x + self.sepet.base_genislik // 2
            sepet_cy = self.sepet.y + self.sepet.base_yukseklik // 2
            isik = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            pygame.draw.circle(isik, (0, 0, 0, 160), (sepet_cx, sepet_cy), self.isik_yaricap)
            self.gece_surface.blit(isik, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            hedef.blit(self.gece_surface, (0, 0))

        self._hud_ciz(hedef=hedef)
        for d in self.duyurular:
            d.ciz(hedef, self.buyuk_font)
        for g in self.gorev_bildirimleri:
            g.ciz(hedef, self.buyuk_font, self.kucuk_font)

        fade_alpha = getattr(self, 'bolge_fade_alpha', 0)
        if fade_alpha > 0:
            fade_surf = pygame.Surface((EKRAN_GENISLIK, EKRAN_YUKSEKLIK), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, min(255, fade_alpha)))
            hedef.blit(fade_surf, (0, 0))

        ox, oy = self.ekran_sarsintisi.offset_al()
        self.ekran.fill(SIYAH)
        self.ekran.blit(hedef, (ox, oy))
