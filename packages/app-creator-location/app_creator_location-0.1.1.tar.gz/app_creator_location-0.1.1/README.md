# App Creator Location 🌍

Une application Django + CLI pour récupérer la géolocalisation de l'utilisateur via son adresse IP (`https://ipinfo.io`).

## 📦 Installation

```bash
pip install app-creator-location
Utilisation CLI
get-location
Utilisation Django
'app_creator',
Depuis PyPI (si publié) :
    pip install app-creator-location
▶️ Utilisation en ligne de commande :
------------------------------------------------------------

Tape simplement :
    get-location

Résultat :
   IP: 255.255. 255.255
    Ville: Abidjan
    Région: Abidjan
    Pays: CIV
    Localisation: Région des lagunes au sud de la Côte d'Ivoire
    Fournisseur: Orange.CI

------------------------------------------------------------
🌐 Intégration dans un projet Django :
------------------------------------------------------------

1. Ajouter `app_creator` dans `INSTALLED_APPS` :
    INSTALLED_APPS = [
        ...
        'app_creator',
    ]

2. Inclure les routes dans `urls.py` du projet :
    from django.urls import include, path

    urlpatterns = [
        ...
        path('', include('app_creator.urls')),
    ]

3. Accéder à la route `/ip/` dans votre navigateur :
    http://localhost:8000/ip/

    Exemple de réponse JSON :
    {
        "ip": "255.255. 255.255",
        "city": "Abidjan",
        "region": "Abidjan",
        "country": "CIV",
        "loc": "Région des lagunes au sud de la Côte d'Ivoire",
        "org": "Orange.CI."
    }

------------------------------------------------------------
📂 Structure du package :
------------------------------------------------------------

app_creator/
├── __init__.py
├── cli.py             → Script CLI
├── views.py           → Vue Django (JSON)
├── urls.py            → Routes Django

setup.py               → Configuration package
README.txt             → Ce fichier
LICENSE                → Licence MIT ou autre
MANIFEST.in            → (si fichiers statiques)
pyproject.toml         → (facultatif, version moderne)

------------------------------------------------------------
📤 Publication sur PyPI (rappel) :
------------------------------------------------------------

1. Installer les outils :
    pip install build twine

2. Créer les fichiers :
    python setup.py sdist bdist_wheel

3. Publier :
    twine upload dist/*

------------------------------------------------------------
👤 Auteur :
------------------------------------------------------------
Nom : Traoré Souleymane Almami
Email : trasouleymane980@gmail.com
GitHub : https://github.com/

------------------------------------------------------------
📝 Licence :
------------------------------------------------------------
Ce projet est sous licence MIT. Voir le fichier LICENSE.
