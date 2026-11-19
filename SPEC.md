# La Bande — Spécification du projet

## 1. Vision

Aujourd'hui, organiser une sortie entre amis, c'est une conversation de groupe pour
proposer, un sondage pour trouver une date, Tricount pour les comptes, un album
partagé pour les photos… et personne ne se souvient du nom du bar génial d'il y a
six mois.

**La Bande réunit tout le cycle de vie d'une sortie au même endroit :**

```
 Calendrier des dispos ──► Proposer une sortie ──► Chacun répond
 (qui est libre quand)      (resto, bar, vacances)   (oui / non / autre date)
                                                          │
 Carte des lieux notés ◄── Album photo ◄── Dépenses ◄── Sortie confirmée
 (QG, à refaire, à éviter)  de la sortie   (façon Tricount)
```

## 2. Utilisateurs et rôles

| Rôle | Ce qu'il peut faire |
|---|---|
| Visiteur (non connecté) | Voir la page d'accueil, créer un compte, se connecter |
| Membre d'un groupe | Tout voir et tout utiliser dans ses groupes, et seulement ceux-là |
| Créateur du groupe (`owner`) | Comme un membre, plus : renommer le groupe, régénérer le code d'invitation, retirer un membre |
| Organisateur d'une sortie | Celui qui l'a proposée : il peut la modifier, choisir la date finale, l'annuler |

## 3. Fonctionnalités

### 3.1 Comptes et groupes
- Inscription, connexion, déconnexion
- Créer un groupe, rejoindre un groupe avec un code d'invitation
- Une même personne peut faire partie de plusieurs bandes (les potes du lycée, les collègues…)

### 3.2 Calendrier des disponibilités
- Chaque utilisateur remplit **ses** dispos sur un calendrier mensuel : pour chaque jour, il clique pour passer de *libre* à *peut-être*, puis à *pas dispo*, puis à *non renseigné*
- Les dispos sont personnelles : on les remplit une fois, elles s'affichent dans tous ses groupes
- **Vue du groupe** : un calendrier où chaque jour montre combien de membres sont libres (couleur plus foncée = plus de monde dispo). Un clic sur un jour montre qui est libre, qui ne l'est pas, et qui n'a pas répondu
- Les sorties confirmées apparaissent sur ce calendrier

### 3.3 Sorties
- Proposer une sortie : titre, catégorie (restaurant, bar, soirée, activité, week-end/vacances, autre), date et heure de début, date de fin (facultative, utile pour les vacances), lieu (choisi parmi les lieux du groupe, ou nouveau lieu), description
- Au moment de proposer, l'appli affiche combien de membres sont dispos ce jour-là
- Chaque membre répond **Je viens**, **Peut-être** ou **Je ne peux pas**
- Un membre peut **proposer une autre date**. Les autres votent pour les dates proposées, et l'organisateur choisit la date finale
- Statuts d'une sortie : *proposée* → *confirmée* → *passée* (ou *annulée*)
- Page « Mes prochaines sorties » regroupant tous mes groupes

### 3.4 Dépenses (le Tricount intégré)
- Une dépense peut être rattachée à une sortie (l'addition du resto) ou au groupe en général (la location des vacances)
- Montant, description, qui a payé, entre qui on partage : à parts égales, ou montants personnalisés (« je n'ai pas pris de dessert »)
- Par défaut, les participants proposés sont ceux qui ont répondu *Je viens*
- **Soldes** : pour chaque membre, ce qu'il a payé moins ce qu'il doit
- **Remboursements suggérés**, avec le moins de virements possible (« Léa doit 23,40 € à Tom »)
- Bouton **« C'est remboursé »** pour enregistrer un remboursement et remettre les compteurs à jour
- Récapitulatif des dépenses par sortie (« le week-end à Lyon a coûté 187 € par personne »)

### 3.5 Carte des lieux et notes
- Carte interactive (Leaflet + OpenStreetMap, gratuit et sans clé d'API) affichant tous les lieux où la bande est allée
- Ajouter un lieu en cliquant sur la carte, puis en lui donnant un nom, une adresse et une catégorie
- Après une sortie, chaque participant **note le lieu** : une note de 1 à 5, un verdict (**QG**, **À refaire**, **Bof**, **À éviter**) et un commentaire
- Chaque marqueur prend la couleur du verdict majoritaire du groupe
- Filtres : par catégorie et par verdict (« montre-moi nos QG bars »)
- La fiche d'un lieu affiche la note moyenne, les verdicts, et l'historique des sorties qui s'y sont déroulées

### 3.6 Album photo
- Chaque sortie a son album : les participants y ajoutent leurs photos
- Formats JPEG, PNG et WebP, 5 Mo maximum par photo
- Grille de vignettes, affichage en grand au clic, légende facultative
- La première photo sert de couverture à la sortie et à sa fiche sur la carte
- On peut supprimer ses propres photos (l'owner du groupe peut supprimer toutes celles du groupe)

### 3.7 Bonus : fil de discussion par sortie
- Commentaires sous chaque sortie (« je réserve pour 20h ? »), sans temps réel : la page se recharge

### Hors périmètre
Chat en temps réel, notifications push, application mobile, paiement réel.

## 4. Stack technique

- **Python 3.11 + Flask**, pages HTML générées avec Jinja
- **SQLite** pour la base de données (un seul fichier, `la_bande.db`)
- **Werkzeug** (fourni avec Flask) pour hacher les mots de passe et sécuriser les noms de fichiers
- **Leaflet** (chargé depuis un CDN) pour la carte, avec les tuiles OpenStreetMap
- **JavaScript simple, sans framework** pour le calendrier cliquable
- **pytest** pour les tests
- Photos stockées dans le dossier `uploads/` (hors de GitHub)

## 5. Modèle de données

Le schéma complet se trouve dans `schema.sql`. Il est créé dès le lot 0.

| Table | Rôle |
|---|---|
| `users` | Comptes (mot de passe haché uniquement) |
| `friend_groups`, `memberships` | Les bandes et leurs membres |
| `availabilities` | Dispo d'un utilisateur pour un jour donné (libre, peut-être, pas dispo) |
| `places` | Lieux du groupe, avec leurs coordonnées GPS |
| `place_ratings` | Note, verdict et commentaire d'un membre sur un lieu |
| `outings` | Les sorties |
| `outing_responses` | Réponse de chaque membre à une sortie |
| `date_proposals`, `date_proposal_votes` | Autres dates proposées, et votes |
| `expenses`, `expense_shares` | Dépenses et part de chacun |
| `settlements` | Remboursements effectués |
| `photos` | Photos d'une sortie (seules les métadonnées sont en base, le fichier va dans `uploads/`) |
| `outing_comments` | Fil de discussion (bonus) |

**Les montants sont en centimes (entiers)** : 12,50 € devient `1250`, ce qui évite
les erreurs d'arrondi. **Les dates suivent le format ISO** : `2026-10-03` et
`2026-10-03T20:00`.

## 6. Règles de sécurité (à vérifier à chaque code review)

1. Les mots de passe sont hachés (`generate_password_hash` / `check_password_hash`).
2. `SECRET_KEY` est lue depuis une variable d'environnement (sur Replit : onglet « Secrets »), jamais écrite dans le code.
3. **Contrôle d'accès** : toute page d'un groupe, d'une sortie, d'un lieu, d'une dépense ou d'une photo vérifie que l'utilisateur connecté est membre du groupe concerné. Sinon, l'appli renvoie une erreur 404. Il faut tester en changeant l'identifiant dans l'adresse.
4. Les requêtes SQL sont toujours paramétrées (`?`).
5. Toutes les saisies sont validées côté serveur : montants positifs, dates valides, notes entre 1 et 5, longueurs maximales, coordonnées GPS plausibles.
6. Toute action qui modifie des données passe par `POST`, jamais par `GET`.
7. **Photos** :
   - vérifier l'extension **et** le contenu réel du fichier ;
   - renommer chaque fichier avec un nom aléatoire (`uuid4`) ;
   - limiter la taille à 5 Mo (`MAX_CONTENT_LENGTH`) ;
   - servir les photos via une route qui vérifie l'appartenance au groupe, et **pas** depuis `static/`.
8. `la_bande.db`, `.env` et `uploads/` ne sont jamais commités (voir `.gitignore`).
9. Le texte saisi par les utilisateurs est toujours échappé à l'affichage (Jinja le fait par défaut : ne jamais utiliser `|safe` sur ces textes).
10. **Protection CSRF** : chaque formulaire `POST` contient `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`, et les requêtes `fetch` envoient l'en-tête `X-CSRF-Token`. La vérification est faite dans `security.py`.

## 7. Découpage en lots

Chaque lot correspond à un tour complet du ping-pong : Replit → push → GitHub →
pull sur l'ordinateur → code review Claude Code → push → GitHub → pull dans Replit.

Les lots sont classés du plus indispensable au plus « bonus » : si le temps
manque, l'appli reste cohérente à chaque étape.

### Lot 0 — Squelette
Structure du projet, schéma complet de la base, page d'accueil, configuration, premiers tests.
**Critères** : `python main.py` démarre sans erreur, `pytest` passe, la base est créée automatiquement.

### Lot 1 — Comptes utilisateurs
Pages d'inscription et de connexion, route de déconnexion (en POST), session Flask, décorateur `login_required`, barre de navigation qui change selon qu'on est connecté ou non.
**Critères** : le mot de passe n'apparaît jamais en clair dans la base ; un mauvais mot de passe affiche un message clair.

### Lot 2 — Groupes
Mes groupes, créer un groupe, rejoindre un groupe par code (`secrets.token_urlsafe`), page du groupe avec ses membres, fonction `get_group_or_404`.
**Critères** : un non-membre ne peut pas voir un groupe, même en tapant l'adresse à la main.

### Lot 3 — Calendrier des dispos
Calendrier personnel cliquable (mois précédent et suivant), enregistrement des clics en arrière-plan (`fetch` en POST), vue du groupe avec l'intensité des disponibilités, détail d'un jour.
**Critères** : on ne peut modifier que ses propres dispos ; la vue du groupe n'affiche que les membres du groupe.

### Lot 4 — Sorties
Proposer une sortie, répondre, proposer une autre date et voter, choix de la date finale par l'organisateur, gestion des statuts, sorties affichées sur le calendrier du groupe, page « Mes prochaines sorties ».
**Critères** : seul l'organisateur peut confirmer ou annuler ; une seule réponse par membre et par sortie.

### Lot 5 — Dépenses
Ajouter une dépense (répartition égale ou personnalisée), soldes, remboursements suggérés, bouton « C'est remboursé », récapitulatif par sortie.
**Critères** : pour une répartition égale, les centimes restants sont correctement attribués (10 € entre 3 donne 3,34 + 3,33 + 3,33) ; la somme des soldes vaut toujours 0 ; en répartition personnalisée, la somme des parts est égale au montant.

### Lot 6 — Carte et notes des lieux
Carte Leaflet, ajout d'un lieu par clic sur la carte, fiche lieu, notation (note, verdict, commentaire), couleur des marqueurs selon le verdict majoritaire, filtres.
**Critères** : un membre ne peut avoir qu'une note par lieu (il peut la modifier) ; seuls les lieux du groupe apparaissent sur sa carte.

### Lot 7 — Album photo
Envoi de photos, grille de vignettes, affichage en grand, légende, photo de couverture, suppression.
**Critères** : toutes les règles du point 7 de la section 6 sont respectées ; un fichier `.exe` renommé en `.jpg` est refusé.

### Lot 8 (bonus) — Fil de discussion par sortie
Commentaires sous une sortie, 500 caractères maximum.
**Critères** : un commentaire contenant `<script>` s'affiche comme du texte, sans s'exécuter.

## 8. Prompt de code review pour Claude Code

À chaque tour, sur l'ordinateur, dans le dossier du projet :

> Fais la code review du lot N de ce projet (La Bande, voir SPEC.md).
> 1. Vérifie que le code respecte les critères du lot N dans SPEC.md.
> 2. Vérifie chaque règle de la section 6 « Règles de sécurité », en particulier le contrôle d'accès.
> 3. Signale les bugs, le code dupliqué et ce qui est difficile à lire.
> 4. Explique-moi chaque problème simplement, puis corrige-le dans les fichiers.
> 5. Lance `pytest` et ajoute les tests qui manquent pour ce lot.
> Ne touche pas à Git : je fais les commits moi-même.
