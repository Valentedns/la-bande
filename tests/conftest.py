import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    """Une application de test avec sa propre base, créée dans un dossier temporaire."""
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        "SECRET_KEY": "test",
    })


@pytest.fixture
def client(app):
    return app.test_client()
