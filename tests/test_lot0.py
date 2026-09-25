import sqlite3

TABLES_ATTENDUES = [
    "users", "friend_groups", "memberships", "availabilities",
    "places", "place_ratings", "outings", "outing_responses",
    "date_proposals", "date_proposal_votes", "expenses", "expense_shares",
    "settlements", "photos", "outing_comments",
]


def test_page_accueil(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "La Bande" in response.get_data(as_text=True)


def test_tables_creees(app):
    db = sqlite3.connect(app.config["DATABASE"])
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    db.close()
    for table in TABLES_ATTENDUES:
        assert table in tables, f"table manquante : {table}"


def test_montant_negatif_refuse(app):
    """La base elle-même refuse une dépense négative (garde-fou en plus du code)."""
    import pytest
    db = sqlite3.connect(app.config["DATABASE"])
    db.execute("INSERT INTO users (username, email, password_hash) VALUES ('a', 'a@a.fr', 'x')")
    db.execute("INSERT INTO friend_groups (name, invite_code, created_by) VALUES ('g', 'c', 1)")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO expenses (group_id, payer_id, description, amount_cents, spent_on, created_by)"
            " VALUES (1, 1, 'test', -500, '2026-10-03', 1)"
        )
    db.close()
