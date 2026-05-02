# =============================================================================
# API — Skor API Yöneticisi (JSON Export + Simülasyon)
# =============================================================================
import json
import time
import sys
import os
from resource_path import data_path


class SkorAPIYoneticisi:
    """Skorları JSON formatında dışarıya aktaran ve API simülasyonu sağlayan sınıf."""
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
        veri = {
            "oyuncu": isim, "skor": skor, "seviye": seviye,
            "sure_saniye": round(sure_saniye, 2),
            "tarih": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "oyun_versiyon": "2.0", "platform": sys.platform,
        }
        if ekstra and isinstance(ekstra, dict):
            veri["ekstra"] = ekstra
        return veri

    def liderlik_tablosu_json(self):
        top5 = self.veritabani.en_iyi_5_al()
        return {
            "liderlik_tablosu": [
                {"sira": i + 1, "isim": isim, "skor": skor}
                for i, (isim, skor) in enumerate(top5)
            ],
            "guncelleme_tarihi": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "toplam_kayit": len(top5),
        }

    def json_dosyaya_aktar(self, dosya_yolu=None):
        if dosya_yolu is None:
            dosya_yolu = data_path("skorlar_export.json")
        veri = self.liderlik_tablosu_json()
        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                json.dump(veri, f, ensure_ascii=False, indent=2)
            return True, dosya_yolu
        except IOError as e:
            print(f"[UYARI] JSON dışa aktarma hatası: {e}")
            return False, None

    def api_ye_gonder(self, skor_verisi):
        json_payload = json.dumps(skor_verisi, ensure_ascii=False)
        if self._requests_mevcut:
            try:
                import requests
                yanit = requests.post(
                    self.API_URL, data=json_payload,
                    headers={"Content-Type": "application/json; charset=utf-8"}, timeout=5)
                return {"basarili": yanit.status_code == 200, "durum_kodu": yanit.status_code}
            except Exception as e:
                return {"basarili": False, "hata": str(e)}
        else:
            return {"basarili": True, "simülasyon": True, "gonderilen_veri": skor_verisi}

    def toplu_aktar(self):
        basarili, yol = self.json_dosyaya_aktar()
        api_sonuc = self.api_ye_gonder(self.liderlik_tablosu_json())
        return {"dosya_aktarimi": {"basarili": basarili, "yol": yol}, "api_sonucu": api_sonuc}
