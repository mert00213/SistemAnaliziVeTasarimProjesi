# =============================================================================
# SETTINGS — Tüm Oyun Sabitleri ve Konfigürasyonu
# =============================================================================
"""
Oyunun tüm sabit değerleri, renk tanımları, nesne konfigürasyonları
ve bölge tanımları bu modülde merkezi olarak yönetilir.
"""

# =============================================================================
# EKRAN AYARLARI
# =============================================================================
EKRAN_GENISLIK = 800
EKRAN_YUKSEKLIK = 600
FPS = 60

# =============================================================================
# RENK PALETI
# =============================================================================
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
KOYU_KIRMIZI = (140, 20, 30)

# =============================================================================
# OYUN MEKANİKLERİ
# =============================================================================
MAKS_CAN = 3

# =============================================================================
# SEPET RENK SEÇENEKLERİ (Market Sistemi)
# =============================================================================
SEPET_RENKLERI = {
    "kahverengi": {"renk": (139, 90, 43), "ic": (180, 120, 60), "kenar": (100, 60, 20), "fiyat": 0},
    "kirmizi":    {"renk": (180, 40, 40), "ic": (220, 80, 80), "kenar": (120, 20, 20), "fiyat": 500},
    "mavi":       {"renk": (40, 80, 180), "ic": (80, 120, 220), "kenar": (20, 50, 130), "fiyat": 500},
    "mor":        {"renk": (130, 40, 180), "ic": (170, 80, 220), "kenar": (90, 20, 130), "fiyat": 1000},
    "altin":      {"renk": (200, 170, 40), "ic": (240, 210, 80), "kenar": (160, 130, 20), "fiyat": 2000},
}

# =============================================================================
# GÖREV (ACHIEVEMENT) TANIMLARI
# =============================================================================
GOREV_TANIMLARI = {
    "50_elma": "50 Elma Topla",
    "1000_hasarsiz": "Hiç Can Kaybetmeden 1000 Puan",
    "5_altin": "Tek Oyunda 5 Altın Elma Yakala",
}

# =============================================================================
# GELİŞTİRME (UPGRADE) TANIMLARI
# =============================================================================
UPGRADE_TANIMLARI = {
    "sepet_hizi":    {"isim": "Sepet Hızı",     "maks_seviye": 5, "baz_fiyat": 300,  "artis": 200},
    "miknatıs_sure": {"isim": "Mıknatıs Süresi", "maks_seviye": 5, "baz_fiyat": 400,  "artis": 250},
    "ekstra_can":    {"isim": "Ekstra Can",      "maks_seviye": 3, "baz_fiyat": 600,  "artis": 400},
}

# =============================================================================
# BÖLGE (BİOME) TANIMLARI
# =============================================================================
BOLGE_TANIMLARI = [
    {"isim": "Orman",  "dosya": "orman.png",  "yercekim": 1.0, "zemin": KOYU_YESIL,      "cimen": YESIL,
     "gokyuzu": (30, 100, 30)},
    {"isim": "Çöl",    "dosya": "col.png",    "yercekim": 1.15, "zemin": (180, 140, 60),  "cimen": (200, 170, 80),
     "gokyuzu": (100, 70, 20)},
    {"isim": "Buz",    "dosya": "buz.png",    "yercekim": 0.95, "zemin": (180, 200, 220), "cimen": (200, 220, 240),
     "gokyuzu": (40, 60, 100)},
    {"isim": "Uzay",   "dosya": "uzay.png",   "yercekim": 0.6,  "zemin": (40, 20, 60),    "cimen": (60, 30, 80),
     "gokyuzu": (5, 5, 20)},
]
