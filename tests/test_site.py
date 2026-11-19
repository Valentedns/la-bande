"""Vérifie la page vitrine publiée sur GitHub Pages : HTML bien formé, pas de lien ou d'image cassés."""
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
VOID_TAGS = {"meta", "link", "img", "br", "hr", "input", "source", "wbr"}


class Analyse(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pile = []
        self.erreurs = []
        self.liens = []
        self.images_sans_alt = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img" and not attrs.get("alt"):
            self.images_sans_alt.append(attrs.get("src"))
        for nom in ("href", "src"):
            if attrs.get(nom):
                self.liens.append(attrs[nom])
        if tag not in VOID_TAGS:
            self.pile.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.pile or self.pile[-1] != tag:
            self.erreurs.append(f"balise </{tag}> inattendue")
        else:
            self.pile.pop()


def analyser():
    analyse = Analyse()
    analyse.feed((SITE / "index.html").read_text(encoding="utf-8"))
    return analyse


def test_html_bien_forme():
    analyse = analyser()
    assert analyse.erreurs == []
    assert analyse.pile == [], f"balises non fermées : {analyse.pile}"


def test_aucun_lien_local_casse():
    for lien in analyser().liens:
        if lien.startswith(("http://", "https://", "#", "mailto:")):
            continue
        cible = SITE / lien.split("#")[0]
        if lien in ("./", ""):
            cible = SITE / "index.html"
        assert cible.exists(), f"lien cassé : {lien}"


def test_toutes_les_images_ont_un_texte_alternatif():
    assert analyser().images_sans_alt == []
