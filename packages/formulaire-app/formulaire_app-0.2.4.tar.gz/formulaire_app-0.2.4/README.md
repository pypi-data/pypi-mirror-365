# formulaire_app

Une application Django prête à l'emploi pour créer, afficher et gérer des formulaires personnalisés.

============
# formulaire_app
============

`formulaire_app` est une application Django réutilisable permettant d'ajouter rapidement des formulaires dynamiques à n'importe quel projet Django.

## Fonctionnalités

- 📄 Création de formulaires personnalisés
- 🖼️ Templates prêts à l'emploi pour affichage rapide
- 🗃️ Sauvegarde des réponses utilisateur
- 🧩 Intégration simple via `INSTALLED_APPS`
- 🎨 Fichiers `static/` et `templates/` inclus pour personnalisation facile

## Installation

```bash
pip install formulaire-app

Quick start
-----------

1. Add "formulaire_app" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        'formulaire_app',
    ]


2. Include the formulaire_app URLconf in your project urls.py like this::

    from django.urls import path, include

    urlpatterns = [
            ...,
            path('', include('formulaire_app.urls')),
]


3. Run ``python manage.py migrate`` to create the models.


4. Start the development server and visit the formular
    python manage.py runserver
