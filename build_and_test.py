"""
Script pour construire et tester l'EXE avec les sauvegardes
"""

import subprocess
import sys
import os
import time

def build_exe():
    """Construit l'EXE avec PyInstaller"""
    print("=== Construction de l'EXE ===")
    
    # S'assurer que les dossiers existent
    if not os.path.exists("custom_levels"):
        os.makedirs("custom_levels")
    
    if not os.path.exists("custom_levels/.keep"):
        with open("custom_levels/.keep", "w") as f:
            f.write("# Placeholder file")
    
    # Construire avec PyInstaller
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", "main.spec"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Construction réussie!")
            
            # Vérifier que l'EXE existe
            exe_path = "dist/HexMaster.exe"
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path)
                print(f"✅ EXE créé: {size // (1024*1024)} MB")
                return exe_path
            else:
                print("❌ EXE non trouvé")
                return None
        else:
            print("❌ Erreur de construction:")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_exe_sauvegarde(exe_path):
    """Lance l'EXE en mode test pour vérifier les sauvegardes"""
    print("\\n=== Test EXE - Instructions ===")
    print("1. L'EXE va se lancer")
    print("2. Cliquez sur 'Options' en haut à droite")
    print("3. Cliquez sur 'Debug Sauvegarde' pour voir les infos")
    print("4. Notez le chemin de sauvegarde affiché")
    print("5. Testez quelques actions dans le jeu")
    print("6. Fermez et relancez pour vérifier la persistance")
    
    input("\\nAppuyez sur Entrée pour lancer l'EXE...")
    
    try:
        # Lancer l'EXE
        subprocess.Popen([exe_path])
        print(f"✅ EXE lancé: {exe_path}")
        print("\\nTEST MANUEL:")
        print("- Vérifiez que le menu Options fonctionne")
        print("- Vérifiez que Debug Sauvegarde affiche les infos")
        print("- Testez les sauvegardes dans le jeu")
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")

def main():
    print("Script de construction et test des sauvegardes EXE")
    print("=" * 50)
    
    # Construire l'EXE
    exe_path = build_exe()
    
    if exe_path:
        # Proposer de tester
        response = input("\\nVoulez-vous tester l'EXE maintenant? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            test_exe_sauvegarde(exe_path)
    
    print("\\n=== Rappel des améliorations ===")
    print("1. Sauvegarde dans le dossier utilisateur (~\\HexMaster\\)")
    print("2. Gestion des erreurs améliorée")
    print("3. Debug menu intégré")
    print("4. Messages de log détaillés")

if __name__ == "__main__":
    main()
