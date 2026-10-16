"""Lot 1 : comptes utilisateurs (inscription, connexion, déconnexion)."""
import functools
import re
import sqlite3

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db

bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN = 8
PASSWORD_MAX = 128


@bp.before_app_request
def load_logged_in_user():
    """Avant chaque requête, g.user contient l'utilisateur connecté (ou None)."""
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    """Décorateur à mettre sur toute page réservée aux personnes connectées."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Connectez-vous pour accéder à cette page.", "error")
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


def _log_in(user_id):
    # On vide la session avant d'y mettre l'utilisateur (protection contre la fixation de session).
    session.clear()
    session["user_id"] = user_id


@bp.route("/inscription", methods=("GET", "POST"))
def register():
    if g.user:
        return redirect(url_for("index"))

    form = {"username": "", "email": ""}
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("password_confirm", "")
        form = {"username": username, "email": email}

        errors = []
        if not USERNAME_RE.match(username):
            errors.append("Le pseudo doit faire de 3 à 30 caractères : lettres, chiffres, point, tiret ou tiret bas.")
        if len(email) > 254 or not EMAIL_RE.match(email):
            errors.append("Cette adresse e-mail n'est pas valide.")
        if not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
            errors.append(f"Le mot de passe doit faire entre {PASSWORD_MIN} et {PASSWORD_MAX} caractères.")
        elif password != confirm:
            errors.append("Les deux mots de passe ne correspondent pas.")

        if not errors:
            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                errors.append("Ce pseudo ou cette adresse e-mail est déjà utilisé.")
            else:
                _log_in(cursor.lastrowid)
                flash(f"Bienvenue dans La Bande, {username} !", "success")
                return redirect(url_for("index"))

        for error in errors:
            flash(error, "error")

    return render_template("inscription.html", form=form)


@bp.route("/connexion", methods=("GET", "POST"))
def login():
    if g.user:
        return redirect(url_for("index"))

    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, username, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

        # Même message dans les deux cas : on ne révèle pas si l'e-mail existe.
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Adresse e-mail ou mot de passe incorrect.", "error")
        else:
            _log_in(user["id"])
            flash(f"Content de vous revoir, {user['username']} !", "success")
            return redirect(url_for("index"))

    return render_template("connexion.html", email=email)


@bp.route("/deconnexion", methods=("POST",))
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("index"))