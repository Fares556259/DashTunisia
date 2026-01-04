# Carte de la Pauvreté en Tunisie 2015 - Dashboard

Ce projet est une application interactive développée avec Streamlit pour visualiser les données de la pauvreté en Tunisie (2015).

## Prérequis

- Python 3.7 ou version ultérieure installé sur votre machine.

## Installation

1.  Ouvrez un terminal ou une invite de commande.
2.  Naviguez vers le dossier contenant ce fichier (le dossier `poverty_dashboard`).
3.  Installez les dépendances nécessaires en exécutant la commande suivante :

    ```bash
    pip install -r requirements.txt
    ```

## Lancement de l'application

Une fois l'installation terminée, lancez l'application avec la commande :

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut. Si ce n'est pas le cas, ouvrez le lien affiché dans le terminal (généralement `http://localhost:8501`).

## Structure du projet

- `app.py` : Le code principal de l'application.
- `data/` : Contient les données CSV (`poverty_tunisia.csv`).
- `geo/` : Contient les fichiers géographiques pour la carte (`tunisia_governorates.geojson`).
- `requirements.txt` : Liste des bibliothèques Python requises.
