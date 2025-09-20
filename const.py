"""Constantes du jeu"""

# Sauvegarde par défaut
D_PA = 0  # Points d'âmes de départ
D_CP = 5  # Coût de placement de départ
D_UNITES = ["Goule"]  # Unités de départ (liste de noms de classes)

# Valeurs par défaut
MAX_UNITE = 24 # 8*3 # Nombre maximum d'unités plaçables sur la carte
MAX_TIER = 4 # Les boss sont tier 4
MAX_CP = MAX_UNITE * MAX_TIER  # Coût de placement maximum
MAX_PA = 1000000  # Points d'âmes maximum

D_DISPLAY_MODE = "windowed" # Valeurs possibles : "windowed", "fullscreen"

D_AIDES = {
    "PV": True, # Valeurs possibles : True, False
    "DMG": True, # Valeurs possibles : True, False
    "BOUCLIER": True # Valeurs possibles : True, False
}


# Couleurs
BLANC = (255, 255, 255)
BLEU = (50, 150, 250)
NOIR = (0,0,0)
GRIS = (180,180,180)
VERT = (50,200,50)
ROUGE = (200,50,50)

VERT_VIE = (30, 120, 30)
BLEU_BOUCLIER = (100, 150, 255)
ROUGE_DMG_TOTAL = (255, 100, 100)
JAUNE_CIBLE = (255, 255, 100)