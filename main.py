"""La Bande : point d'entrée de l'application."""
import os
import secrets

from flask import Flask, render_template

import database


def create_app(test_config=None):
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        # Pratique pour démarrer, mais les sessions seront perdues à chaque redémarrage.
        # Sur Replit, ajoute SECRET_KEY dans l'onglet "Secrets".
        print("ATTENTION : SECRET_KEY absente, une clé temporaire est utilisée.")
        secret_key = secrets.token_hex(32)

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE=os.environ.get("DATABASE_PATH", "la_bande.db"),
        UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", "uploads"),  # photos (lot 7)
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 Mo max par envoi
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    database.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
