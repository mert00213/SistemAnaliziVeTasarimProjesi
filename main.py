# =============================================================================
# MAIN — Programın Giriş Noktası
# =============================================================================
"""
Modüler Sepet Oyunu başlatıcı.
Kullanım:
    python main.py
"""

from managers.game_manager import GameManager


def main():
    """Oyunu başlatır."""
    oyun = GameManager()
    oyun.calistir()


if __name__ == "__main__":
    main()
