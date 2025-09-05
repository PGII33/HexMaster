import json
import os

def create_campaign_structure():
    """Crée la structure de campagne avec les niveaux au format JSON"""
    
    # Créer la structure de dossiers
    base_path = "Campagne"
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # Tutoriel (chapitre 0)
    tutorial_path = os.path.join(base_path, "00_Tutoriel")
    if not os.path.exists(tutorial_path):
        os.makedirs(tutorial_path)
    
    tutorial_level = {
        "nom": "Apprentissage du Combat",
        "description": "Apprenez les bases du combat dans HexaMaster",
        "unites_ennemis": [
            ("Squelette", (5, 4)),
            ("Goule", (6, 5))
        ],
        "contraintes_joueur": {
            "max_units": 2,
            "cp_disponible": 3,
            "faction_unique": True,
            "faction_requise": "Morts-Vivants"
        },
        "recompenses": {
            "cp": 1,
            "unites_debloquees": [],
            "autres": []
        },
        "unites_predefinies": [
            ("Squelette", (0, 0)),
            ("Vampire", (1, 0))
        ]
    }
    
    with open(os.path.join(tutorial_path, "niveau.json"), 'w', encoding='utf-8') as f:
        json.dump(tutorial_level, f, indent=2, ensure_ascii=False)
    
    # Chapitre 1: La grande église
    church_path = os.path.join(base_path, "01_La_Grande_Eglise")
    if not os.path.exists(church_path):
        os.makedirs(church_path)
    
    # Niveau 1: Les cryptes
    level1_path = os.path.join(church_path, "01_Les_Cryptes")
    if not os.path.exists(level1_path):
        os.makedirs(level1_path)
    
    level1 = {
        "nom": "Les cryptes",
        "description": "Explorez les cryptes abandonnées",
        "unites_ennemis": [
            ("Goule", (5, 5)),
            ("Goule", (6, 5))
        ],
        "contraintes_joueur": {
            "max_units": 2,
            "cp_disponible": 3,
            "faction_unique": True,
            "faction_requise": "Morts-Vivants"
        },
        "recompenses": {
            "cp": 1,
            "unites_debloquees": ["Spectre"],
            "autres": []
        },
        "unites_predefinies": [
            ("Squelette", (0, 0)),
            ("Goule", (1, 0))
        ]
    }
    
    with open(os.path.join(level1_path, "niveau.json"), 'w', encoding='utf-8') as f:
        json.dump(level1, f, indent=2, ensure_ascii=False)
    
    # Niveau 2: Le sanctuaire
    level2_path = os.path.join(church_path, "02_Le_Sanctuaire")
    if not os.path.exists(level2_path):
        os.makedirs(level2_path)
    
    level2 = {
        "nom": "Le sanctuaire",
        "description": "Pénétrez dans le sanctuaire",
        "unites_ennemis": [
            ("Vampire", (5, 5)),
            ("Goule", (6, 5)),
            ("Spectre", (5, 6))
        ],
        "contraintes_joueur": {
            "max_units": 3,
            "cp_disponible": 5,
            "faction_unique": True,
            "faction_requise": "Morts-Vivants"
        },
        "recompenses": {
            "cp": 1,
            "unites_debloquees": ["Zombie"],
            "autres": []
        },
        "unites_predefinies": [
            ("Squelette", (0, 0)),
            ("Goule", (1, 0)),
            ("Spectre", (0, 1))
        ]
    }
    
    with open(os.path.join(level2_path, "niveau.json"), 'w', encoding='utf-8') as f:
        json.dump(level2, f, indent=2, ensure_ascii=False)
    
    # Niveau 3: L'autel maudit
    level3_path = os.path.join(church_path, "03_Autel_Maudit")
    if not os.path.exists(level3_path):
        os.makedirs(level3_path)
    
    level3 = {
        "nom": "L'autel maudit",
        "description": "Confrontez-vous au mal ancien",
        "unites_ennemis": [
            ("Archliche", (5, 5)),
            ("Vampire", (6, 5)),
            ("Liche", (5, 6))
        ],
        "contraintes_joueur": {
            "max_units": 3,
            "cp_disponible": 8,
            "faction_unique": True,
            "faction_requise": "Morts-Vivants"
        },
        "recompenses": {
            "cp": 2,
            "unites_debloquees": ["Liche"],
            "autres": []
        },
        "unites_predefinies": [
            ("Vampire", (0, 0)),
            ("Zombie", (1, 0)),
            ("Liche", (0, 1))
        ]
    }
    
    with open(os.path.join(level3_path, "niveau.json"), 'w', encoding='utf-8') as f:
        json.dump(level3, f, indent=2, ensure_ascii=False)
    
    print("Structure de campagne créée avec succès!")

if __name__ == "__main__":
    create_campaign_structure()