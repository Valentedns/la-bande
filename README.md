# La Bande

Application tout-en-un pour les groupes d'amis : calendrier des dispos, sorties,
dépenses partagées, album photo et carte des lieux notés. Projet d'école (cycle Replit ⇄ GitHub ⇄ ordinateur avec code review).

La spécification complète et le découpage en lots sont dans [SPEC.md](SPEC.md).

## Lancer le projet

```
pip install -r requirements.txt
python main.py
```

Puis ouvrir http://localhost:8080 (sur Replit, l'aperçu s'ouvre tout seul).

**Clé secrète** : définir la variable d'environnement `SECRET_KEY`
(sur Replit : onglet « Secrets »). Sans elle, une clé temporaire est utilisée.

## Lancer les tests

```
pytest
```

## Avancement

- [x] Lot 0 : squelette du projet
- [ ] Lot 1 : comptes utilisateurs
- [ ] Lot 2 : groupes
- [ ] Lot 3 : calendrier des dispos
- [ ] Lot 4 : sorties
- [ ] Lot 5 : dépenses
- [ ] Lot 6 : carte et notes des lieux
- [ ] Lot 7 : album photo
- [ ] Lot 8 (bonus) : fil de discussion par sortie
