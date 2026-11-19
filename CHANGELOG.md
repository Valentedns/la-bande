# Changelog

Toutes les évolutions notables de La Bande sont listées ici.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et les versions suivent le [versionnage sémantique](https://semver.org/lang/fr/).

## [1.0.0] - 2026-11-19

### Ajouté

- Squelette de l'application Flask, schéma complet de la base SQLite et page d'accueil (lot 0).
- Comptes utilisateurs : inscription, connexion, déconnexion, mots de passe hachés (lot 1).
- Protection CSRF sur tous les formulaires et cookie de session sécurisé.
- Style des formulaires et de la navigation.
- Chaîne CI/CD GitHub Actions : tests automatiques à chaque push et pull request, déploiement de la page vitrine sur GitHub Pages.
- Page vitrine du projet (dossier `site/`).
- README complet, CHANGELOG et schéma de l'architecture Git.

### Corrigé

- Dépendances en double dans `requirements.txt`.

[1.0.0]: https://github.com/Valentedns/la-bande/releases/tag/v1.0.0
