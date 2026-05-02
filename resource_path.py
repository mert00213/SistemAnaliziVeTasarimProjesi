# =============================================================================
# RESOURCE PATH — PyInstaller EXE Uyumlu Dosya Yolu Çözümleyici
# =============================================================================
"""
Bu modül, hem geliştirme ortamında hem de PyInstaller ile paketlenmiş
EXE dosyasında doğru dosya yollarını çözmek için kullanılır.

PyInstaller, dosyaları geçici bir _MEIPASS klasörüne çıkarır.
Ancak yazılabilir veriler (veritabanı, skor dosyaları) EXE'nin
bulunduğu dizinde kalmalıdır.
"""

import sys
import os


def resource_path(relative_path):
    """
    Salt okunur kaynaklar (görseller, sesler) için yol çözer.
    PyInstaller EXE: _MEIPASS geçici klasörü kullanılır.
    Geliştirme: Proje kök dizini kullanılır.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def data_path(relative_path):
    """
    Yazılabilir veriler (veritabanı, skor dosyaları) için yol çözer.
    Her zaman EXE'nin / script'in bulunduğu dizini kullanır.
    Bu sayede veritabanı dosyası her zaman yazılabilir konumda olur.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller ile paketlenmiş EXE
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# --- Sık kullanılan yollar (modül seviyesinde önceden hesapla) ---
ASSETS_DIR = resource_path("assets")
IMAGES_DIR = resource_path(os.path.join("assets", "images"))
SOUNDS_DIR = resource_path(os.path.join("assets", "sounds"))
DB_PATH = data_path("skorlar.db")
SKOR_DOSYASI = data_path("skor.txt")
