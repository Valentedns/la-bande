"""Accès à la base de données SQLite."""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db():
    """Renvoie la connexion à la base pour la requête en cours (une seule par requête)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # accès aux colonnes par leur nom : row["username"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    """Ferme la connexion à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crée les tables si elles n'existent pas encore."""
    db = get_db()
    db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    db.commit()


def init_app(app):
    """Branche la base de données sur l'application Flask."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
