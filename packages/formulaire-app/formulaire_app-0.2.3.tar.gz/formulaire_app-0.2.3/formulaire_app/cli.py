import argparse
from .generate import generate_app

def main():
    parser = argparse.ArgumentParser(
        description="Génère une application Django réutilisable à partir de votre package."
    )
    parser.add_argument(
        "app_name",
        help="Nom de l'application Django à générer"
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Répertoire cible dans lequel créer l'application (par défaut, le répertoire courant)"
    )
    
    args = parser.parse_args()
    generate_app(args.app_name, args.target)
