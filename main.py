#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import Config
from gui.main_window import MainWindow

def main():
    print("\n" + "="*50)
    print("  📸 GESTION DES PRÉSENCES")
    print("  Reconnaissance Faciale avec OpenCV")
    print("="*50)
    print(f"  📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*50 + "\n")
    
    Config.ensure_directories()
    
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)

if __name__ == '__main__':
    main()