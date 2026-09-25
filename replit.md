# La Bande sur Replit

- Projet Flask en Python 3.12 avec base SQLite locale.
- Dépendances : `requirements.txt` (`Flask` et `pytest`). Pour les réinstaller : `python -m pip install -r requirements.txt`.
- Le workflow « Start application » lance `PORT=5000 python main.py` ; l’application écoute sur toutes les interfaces et apparaît dans l’aperçu Replit.
- Ajouter `SECRET_KEY` dans les Secrets Replit pour conserver les sessions entre redémarrages. Sans cette variable, l’application utilise une clé temporaire. Ne pas placer cette valeur dans les fichiers du projet.
- Tests : `pytest`.
- Le projet est actuellement un squelette ; les fonctionnalités annoncées dans `README.md` restent à développer.