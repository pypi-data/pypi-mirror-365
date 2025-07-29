import os
import subprocess
import sys

def generate_app(app_name, target_dir='.'):
    # Crée le dossier cible s'il n'existe pas
    os.makedirs(target_dir, exist_ok=True)
    
    # Sauvegarde du répertoire de travail actuel
    original_dir = os.getcwd()
    try:
        # Se placer dans le dossier cible
        os.chdir(target_dir)
        
        # Exécute la commande startapp de Django
        result = subprocess.run(['django-admin', 'startapp', app_name])
        
        # Si la commande échoue, affiche une erreur et quitte
        if result.returncode != 0:
            print("Erreur : la création de l'application a échoué.")
            sys.exit(1)
        
        print(f"✅ Application Django '{app_name}' générée avec succès dans {os.path.abspath(target_dir)}")
    finally:
        # Retour au répertoire initial
        os.chdir(original_dir)
