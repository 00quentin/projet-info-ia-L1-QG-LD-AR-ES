"""
tests/test_export_csv.py
========================
Verrouille le format CSV produit pour ne pas casser silencieusement les
notebooks ou tableurs des utilisateurs qui re-exploitent l'export.

Invariants critiques :
- BOM UTF-8 en tete (Excel ouvre directement les accents)
- Format europeen : separateur ';' et decimal ','
- Premiere colonne = date ISO (YYYY-MM-DD)
- Somme des colonnes "actif" = colonne "valeur_portefeuille_eur" a chaque date
- Capital initial preserve (jour 0 = capital)
"""

from io import BytesIO
import pandas as pd
import pytest

from core.export_csv import (
    construire_dataframe_export,
    generer_csv_simulation,
    _slugify_colonne,
)


@pytest.fixture
def df_prix():
    """3 actifs, 5 jours, prix qui montent et descendent."""
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "S&P 500": [100.0, 105.0, 102.0, 108.0, 110.0],
            "Or": [50.0, 51.0, 52.0, 50.0, 49.0],
            "Bons_Tresor_US_10Y": [200.0, 201.0, 199.0, 200.0, 202.0],
        },
        index=dates,
    )


@pytest.fixture
def poids_simples():
    return {"S&P 500": 0.5, "Or": 0.3, "Bons_Tresor_US_10Y": 0.2}


# === construire_dataframe_export ==========================================


def test_export_jour_0_egale_capital(df_prix, poids_simples):
    """Au jour 0, valeur portefeuille = capital initial."""
    export = construire_dataframe_export(df_prix, poids_simples, 10_000)
    assert export["valeur_portefeuille_eur"].iloc[0] == pytest.approx(10_000.0)


def test_somme_poches_egale_valeur_portefeuille(df_prix, poids_simples):
    """A chaque date, la somme des poches = valeur du portefeuille."""
    export = construire_dataframe_export(df_prix, poids_simples, 10_000)
    poches = export.drop(columns=["valeur_portefeuille_eur"])
    for date in export.index:
        assert poches.loc[date].sum() == pytest.approx(
            export.loc[date, "valeur_portefeuille_eur"], rel=1e-9
        )


def test_index_preserve(df_prix, poids_simples):
    """L'index date du DataFrame d'origine est preserve."""
    export = construire_dataframe_export(df_prix, poids_simples, 10_000)
    assert list(export.index) == list(df_prix.index)


def test_actif_absent_du_df_ignore(df_prix):
    """Un actif present dans poids mais pas dans df est ignore sans crasher."""
    poids = {"S&P 500": 0.5, "Bitcoin": 0.5}
    export = construire_dataframe_export(df_prix, poids, 10_000)
    # Seule la poche S&P 500 existe; valeur initiale = 5000 (50% du capital)
    poches = [c for c in export.columns if c != "valeur_portefeuille_eur"]
    assert len(poches) == 1
    assert export[poches[0]].iloc[0] == pytest.approx(5000.0)


def test_aucun_actif_present_renvoie_capital_constant(df_prix):
    """Si aucun actif du dict poids n'est dans df, on renvoie le capital constant."""
    export = construire_dataframe_export(df_prix, {"Inexistant": 1.0}, 10_000)
    assert "valeur_portefeuille_eur" in export.columns
    assert (export["valeur_portefeuille_eur"] == 10_000).all()


# === generer_csv_simulation ===============================================


def test_csv_commence_par_bom_utf8(df_prix, poids_simples):
    """Le CSV commence par le BOM UTF-8 pour ouverture directe Excel."""
    csv_bytes = generer_csv_simulation(df_prix, poids_simples, 10_000)
    assert csv_bytes.startswith(b"\xef\xbb\xbf")


def test_csv_format_europeen(df_prix, poids_simples):
    """Separateur ';' et decimal ',' (compatibilite Excel France/Europe)."""
    csv_bytes = generer_csv_simulation(df_prix, poids_simples, 10_000)
    contenu = csv_bytes.decode("utf-8-sig")
    premiere_ligne = contenu.split("\n")[0]
    assert ";" in premiere_ligne
    # Une valeur numerique apparait avec une virgule decimale (ex: 10000,00)
    deuxieme_ligne = contenu.split("\n")[1]
    assert "," in deuxieme_ligne


def test_csv_premiere_colonne_est_date(df_prix, poids_simples):
    """Le CSV commence par une colonne 'date' au format ISO."""
    csv_bytes = generer_csv_simulation(df_prix, poids_simples, 10_000)
    contenu = csv_bytes.decode("utf-8-sig")
    header = contenu.split("\n")[0]
    assert header.startswith("date;")
    deuxieme_ligne = contenu.split("\n")[1]
    assert deuxieme_ligne.startswith("2024-01-01;")


def test_csv_relisible_par_pandas(df_prix, poids_simples):
    """Le CSV produit doit pouvoir etre relu par pd.read_csv sans bricolage."""
    csv_bytes = generer_csv_simulation(df_prix, poids_simples, 10_000)
    relu = pd.read_csv(BytesIO(csv_bytes), sep=";", decimal=",", encoding="utf-8-sig")
    assert "date" in relu.columns
    assert "valeur_portefeuille_eur" in relu.columns
    assert len(relu) == 5
    # Jour 0 = 10000 (a 0.01 pres a cause de l'arrondi)
    assert relu["valeur_portefeuille_eur"].iloc[0] == pytest.approx(10_000.0, abs=0.01)


# === _slugify_colonne =====================================================


@pytest.mark.parametrize("entree,attendu", [
    ("S&P 500", "s_et_p_500"),
    ("EUR/USD (Euro-Dollar)", "eur_usd_euro-dollar"),
    ("Or (Gold Spot, $/oz)", "or_gold_spot_oz"),
    ("MSCI World", "msci_world"),
])
def test_slugify_colonne(entree, attendu):
    assert _slugify_colonne(entree) == attendu
