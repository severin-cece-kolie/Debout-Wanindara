import os
from pathlib import Path

# Configuration pour WeasyPrint
# Assurez-vous que ces chemins sont corrects pour votre système

# Chemin vers les polices personnalisées (si nécessaire)
FONTS_DIR = os.path.join(Path(__file__).parent.absolute(), 'static', 'fonts')

# Configuration de WeasyPrint
WEASYPRINT_CONFIG = {
    'font_config': {
        'font_family': 'Poppins',  # Police par défaut
        'sans_serif_family': 'Arial, sans-serif',
        'serif_family': 'Times New Roman, serif',
        'monospace_family': 'Courier New, monospace',
    },
    'font_dirs': [FONTS_DIR] if os.path.exists(FONTS_DIR) else [],
    'font_cache': os.path.join(Path(__file__).parent.absolute(), 'static', 'font_cache'),
}
