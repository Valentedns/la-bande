import sqlite3

MOT_DE_PASSE = "motdepasse123"


def jeton_csrf(client, page="/inscription"):
    """Ouvre une page (ce qui crée le jeton dans la session) et renvoie le jeton."""
    client.get(page)
    with client.session_transaction() as session:
        return session["_csrf_token"]


def inscrire(client, username="alice", email="alice@test.fr",
             password=MOT_DE_PASSE, confirm=None, follow=False):
    token = jeton_csrf(client)
    return client.post("/inscription", data={
        "csrf_token": token,
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password if confirm is None else confirm,
    }, follow_redirects=follow)


def connecter(client, email="alice@test.fr", password=MOT_DE_PASSE, follow=True):
    token = jeton_csrf(client, "/connexion")
    return client.post("/connexion", data={
        "csrf_token": token,
        "email": email,
        "password": password,
    }, follow_redirects=follow)


def lire_utilisateurs(app):
    db = sqlite3.connect(app.config["DATABASE"])
    lignes = db.execute("SELECT username, email, password_hash FROM users").fetchall()
    db.close()
    return lignes


def test_pages_inscription_et_connexion_s_affichent(client):
    inscription = client.get("/inscription")
    connexion = client.get("/connexion")
    assert inscription.status_code == 200
    assert "Créer un compte" in inscription.get_data(as_text=True)
    assert connexion.status_code == 200
    assert "Se connecter" in connexion.get_data(as_text=True)


def test_inscription_reussie_connecte_l_utilisateur(client):
    reponse = inscrire(client, follow=True)
    texte = reponse.get_data(as_text=True)
    assert reponse.status_code == 200
    assert "Bienvenue dans La Bande, alice" in texte
    assert "Se déconnecter" in texte  # la barre de navigation a changé


def test_mot_de_passe_jamais_en_clair_dans_la_base(app, client):
    inscrire(client)
    utilisateurs = lire_utilisateurs(app)
    assert len(utilisateurs) == 1
    mot_de_passe_enregistre = utilisateurs[0][2]
    assert mot_de_passe_enregistre != MOT_DE_PASSE
    assert MOT_DE_PASSE not in mot_de_passe_enregistre


def test_email_deja_utilise_refuse(app, client):
    inscrire(client)
    autre = app.test_client()
    reponse = inscrire(autre, username="bob", email="alice@test.fr", follow=True)
    assert "déjà utilisé" in reponse.get_data(as_text=True)
    assert len(lire_utilisateurs(app)) == 1


def test_mot_de_passe_trop_court_refuse(app, client):
    reponse = inscrire(client, password="court", follow=True)
    assert "entre 8 et 128 caractères" in reponse.get_data(as_text=True)
    assert lire_utilisateurs(app) == []


def test_mots_de_passe_differents_refuses(app, client):
    reponse = inscrire(client, confirm="autrechose123", follow=True)
    assert "ne correspondent pas" in reponse.get_data(as_text=True)
    assert lire_utilisateurs(app) == []


def test_mauvais_mot_de_passe_affiche_un_message_clair(app, client):
    inscrire(client)
    autre = app.test_client()
    reponse = connecter(autre, password="mauvaismdp123")
    texte = reponse.get_data(as_text=True)
    assert "Adresse e-mail ou mot de passe incorrect" in texte
    assert "Se connecter" in texte  # toujours déconnecté


def test_connexion_avec_le_bon_mot_de_passe(app, client):
    inscrire(client)
    autre = app.test_client()
    reponse = connecter(autre)
    texte = reponse.get_data(as_text=True)
    assert "Content de vous revoir, alice" in texte
    assert "Se déconnecter" in texte


def test_deconnexion_en_post(client):
    inscrire(client)
    token = jeton_csrf(client, "/")
    reponse = client.post("/deconnexion", data={"csrf_token": token}, follow_redirects=True)
    texte = reponse.get_data(as_text=True)
    assert "Vous êtes déconnecté" in texte
    assert "Créer un compte" in texte  # la barre de navigation est repassée en mode déconnecté


def test_deconnexion_en_get_refusee(client):
    assert client.get("/deconnexion").status_code == 405


def test_post_sans_jeton_csrf_refuse(app, client):
    reponse = client.post("/inscription", data={
        "username": "alice",
        "email": "alice@test.fr",
        "password": MOT_DE_PASSE,
        "password_confirm": MOT_DE_PASSE,
    })
    assert reponse.status_code == 400
    assert lire_utilisateurs(app) == []