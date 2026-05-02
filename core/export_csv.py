"""
core/export_csv.py
==================
Export CSV des series journalieres d'une simulation ou d'un backtest.

Pourquoi : le PDF est parfait pour partager une analyse, mais l'utilisateur
qui veut re-traiter les chiffres dans Excel ou un notebook Python a besoin
des series brutes. Ce module produit un CSV "tidy" exploitable directement
par pandas.read_csv ou Excel.

Format produit :
    date,valeur_portefeuille_eur,<actif_1>_eur,<actif_2>_eur,...

- date : ISO 8601 (YYYY-MM-DD)
- valeur_portefeuille_eur : valeur totale du portefeuille en euros
- <actif_n>_eur : valeur en euros de la poche allouee a cet actif
  (capital * poids_initial * (prix_t / prix_0))

La somme des colonnes actifs egale la valeur du portefeuille a chaque date.
"""

from io import StringIO
from typing import Dict

import pandas as pd

from config import NOM_AFFICHAGE


def _slugify_colonne(nom: str) -> str:
    """Transforme un nom d'affichage en suffixe de colonne CSV propre."""
    s = nom.lower().replace("&", " et ").replace("/", " ")
    for c in "()[]{}'\",.$":
        s = s.replace(c, "")
    s = "_".join(s.split())  # tout whitespace -> "_", collapse multiple
    return s.strip("_")


def construire_dataframe_export(
    df: pd.DataFrame,
    poids: Dict[str, float],
    capital: float,
) -> pd.DataFrame:
    """
    Construit le DataFrame jour-par-jour : valeur portefeuille + poches.

    Args:
        df: prix par actif (colonnes = sim_keys, index = dates)
        poids: dict {sim_key: poids_normalise}, somme = 1.0
        capital: capital initial en euros

    Returns:
        DataFrame indexe par date avec :
        - colonne "valeur_portefeuille_eur"
        - une colonne "<nom>_eur" par actif present dans poids ET dans df
    """
    actifs_presents = [sk for sk in poids if sk in df.columns]

    if not actifs_presents:
        return pd.DataFrame(
            {"valeur_portefeuille_eur": [capital] * len(df)},
            index=df.index,
        )

    sub = df[actifs_presents]
    base = sub.iloc[0]
    poids_serie = pd.Series({sk: poids[sk] for sk in actifs_presents})

    # Valeur en euros de chaque poche jour par jour
    valeurs_poches = (sub / base) * poids_serie * capital

    # Renommage en colonnes lisibles
    valeurs_poches.columns = [
        f"{_slugify_colonne(NOM_AFFICHAGE.get(sk, sk))}_eur"
        for sk in actifs_presents
    ]

    valeurs_poches.insert(
        0, "valeur_portefeuille_eur", valeurs_poches.sum(axis=1)
    )
    return valeurs_poches


def generer_csv_simulation(
    df: pd.DataFrame,
    poids: Dict[str, float],
    capital: float,
) -> bytes:
    """
    Genere le CSV complet pret a etre passe a st.download_button.

    Args:
        df: prix par actif (colonnes = sim_keys, index = dates)
        poids: dict {sim_key: poids_normalise}
        capital: capital initial en euros

    Returns:
        Contenu CSV encode en UTF-8 avec BOM (pour ouverture directe Excel),
        format europeen : separateur ';' et decimal ','.
    """
    export = construire_dataframe_export(df, poids, capital)
    export = export.round(2)

    # Index converti en colonne "date" au format ISO
    if isinstance(export.index, pd.DatetimeIndex):
        export.index = export.index.strftime("%Y-%m-%d")
    export.index.name = "date"

    buf = StringIO()
    export.to_csv(buf, sep=";", decimal=",", encoding="utf-8")
    # BOM UTF-8 : Excel detecte alors correctement l'encodage et les accents
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")
