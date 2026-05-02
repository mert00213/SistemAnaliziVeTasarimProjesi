# =============================================================================
# DATABASE — SQLite Veritabanı Yöneticisi
# =============================================================================
"""
Skor, market, görev, upgrade, ghost ve envanter verilerini
SQLite veritabanı üzerinden yöneten kalıcı veri katmanı.
"""

import sqlite3
from settings import SEPET_RENKLERI, UPGRADE_TANIMLARI
from resource_path import DB_PATH


class SkorVeritabani:
    """SQLite ile skor ve market verilerini yöneten sınıf."""

    def __init__(self, db_yolu=None):
        self.db_yolu = db_yolu or DB_PATH
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
