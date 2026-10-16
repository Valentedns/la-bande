"""Protection CSRF : chaque formulaire POST doit renvoyer le jeton de la session.

Sans ça, un site malveillant pourrait faire envoyer un formulaire à La Bande
à la place d'un utilisateur connecté (par exemple le déconnecter, ou pire plus tard).
"""
import secrets

from flask import abort, request, session

SESSION_KEY = "_csrf_token"


def generate_csrf_token():
    """Renvoie le jeton CSRF de la session (en crée un s'il n'existe pas encore)."""
    if SESSION_KEY not in session:
        session[SESSION_KEY] = secrets.token_hex(32)
    return session[SESSION_KEY]


def check_csrf():
    """Refuse toute requête POST dont le jeton ne correspond pas à celui de la session."""
    if request.method != "POST":
        return
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
    expected = session.get(SESSION_KEY, "")
    if not expected or not secrets.compare_digest(sent, expected):
        abort(400)


def init_app(app):
    # Dans les templates : <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    app.jinja_env.globals["csrf_token"] = generate_csrf_token
    app.before_request(check_csrf)