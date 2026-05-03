"""
schemas.py
==========
Schémas Pydantic pour valider strictement les réponses de l'IA macro.

Pourquoi : avant cette validation, l'IA pouvait renvoyer 12 au lieu de 0.12,
ce qui faisait exploser la simulation (Or à +1 222 891%).

Maintenant, toute réponse IA est :
1. Parsée selon un contrat strict
2. Normalisée (pourcentage → décimal si besoin)
3. Bornée mathématiquement par classe d'actifs
4. Rejetée si invalide
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ==========================================
# Bornes par classe d'actif (sur 100 jours, ~5 mois)
# Calibrées sur les pires/meilleurs événements historiques connus
# ==========================================
BORNES_ACTIFS: Dict[str, tuple] = {
    # Actions & indices
    "S&P 500":              (-0.55, 0.45),
    "NASDAQ":               (-0.60, 0.55),
    "CAC 40":               (-0.55, 0.45),
    "MSCI_World":           (-0.50, 0.45),
    "Emerging_Markets":     (-0.60, 0.55),
    # Obligations
    "Bons_Tresor_US_10Y":   (-0.25, 0.20),
    "Bund_10Y":             (-0.20, 0.20),
    "OAT_10Y":              (-0.20, 0.20),
    "JGB_10Y":              (-0.15, 0.15),
    "Gilt_10Y":             (-0.20, 0.20),
    # Devises
    "EUR_USD":              (-0.20, 0.20),
    "Dollar_Index":         (-0.20, 0.20),
    "VIX":                  (-0.50, 5.00),
    # Matières premières
    "Or":                   (-0.25, 0.60),
    "Argent":               (-0.30, 0.70),
    "Petrole":              (-0.70, 1.00),
    "Cuivre":               (-0.40, 0.50),
    "ETF_Terres_Rares":     (-0.40, 0.70),
    # Sectoriels
    "ETF_Defense":          (-0.30, 0.50),
    # Cryptomonnaies
    "Bitcoin":              (-0.80, 3.00),
    "Ethereum":             (-0.80, 3.50),
    "XRP":                  (-0.85, 4.00),
    "Solana":               (-0.85, 4.00),
}


def _normaliser_choc(valeur: float) -> float:
    """
    Si l'IA renvoie 25 au lieu de 0.25, on divise par 100.
    Heuristique : un choc en valeur absolue > 5 est forcément un pourcentage mal formé
    (au-delà de +500% ce n'est plus crédible).
    """
    if valeur is None:
        return 0.0
    try:
        v = float(valeur)
    except (TypeError, ValueError):
        return 0.0
    if abs(v) > 5:
        v = v / 100.0
    return v


class ChocsMacro(BaseModel):
    """Impact macro-économique global du scénario."""
    inflation: float = Field(default=0.0, ge=-10.0, le=30.0,
                              description="Variation inflation en %")
    taux_directeurs: float = Field(default=0.0, ge=-5.0, le=10.0,
                                    description="Variation taux directeurs en %")


class ChocsActifs(BaseModel):
    """
    Chocs par actif sur l'horizon (100 jours).
    Tous les champs en décimal (-0.15 = -15%).
    Validés et bornés selon les plafonds historiques par classe.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    # Actions
    sp500:              float = Field(default=0.0, alias="S&P 500")
    nasdaq:             float = Field(default=0.0, alias="NASDAQ")
    cac40:              float = Field(default=0.0, alias="CAC 40")
    msci_world:         float = Field(default=0.0, alias="MSCI_World")
    emerging:           float = Field(default=0.0, alias="Emerging_Markets")
    # Obligations
    treasury_us:        float = Field(default=0.0, alias="Bons_Tresor_US_10Y")
    bund:               float = Field(default=0.0, alias="Bund_10Y")
    oat:                float = Field(default=0.0, alias="OAT_10Y")
    jgb:                float = Field(default=0.0, alias="JGB_10Y")
    gilt:               float = Field(default=0.0, alias="Gilt_10Y")
    # Devises & vol
    eur_usd:            float = Field(default=0.0, alias="EUR_USD")
    dollar_index:       float = Field(default=0.0, alias="Dollar_Index")
    vix:                float = Field(default=0.0, alias="VIX")
    # Matières premières
    gold:               float = Field(default=0.0, alias="Or")
    silver:             float = Field(default=0.0, alias="Argent")
    oil:                float = Field(default=0.0, alias="Petrole")
    copper:             float = Field(default=0.0, alias="Cuivre")
    rare_earth:         float = Field(default=0.0, alias="ETF_Terres_Rares")
    # Sectoriels
    defense:            float = Field(default=0.0, alias="ETF_Defense")
    # Cryptos
    btc:                float = Field(default=0.0, alias="Bitcoin")
    eth:                float = Field(default=0.0, alias="Ethereum")
    xrp:                float = Field(default=0.0, alias="XRP")
    sol:                float = Field(default=0.0, alias="Solana")

    # Validation : normaliser si l'IA renvoie en pourcentage
    @field_validator("*", mode="before")
    @classmethod
    def _normaliser(cls, v):
        return _normaliser_choc(v)


class ReponseAnalyseIA(BaseModel):
    """
    Réponse complète de l'IA pour un scénario macro.
    Si une erreur est présente, les autres champs sont optionnels.
    """
    model_config = ConfigDict(extra="ignore")

    erreur: Optional[str] = None
    macro: Optional[ChocsMacro] = None
    actifs: Optional[ChocsActifs] = None
    explication_courte: Optional[str] = ""
    evenement_reference: Optional[str] = None

    def to_legacy_dict(self) -> dict:
        """
        Convertit en dictionnaire compatible avec le code existant
        (qui attend les clés 'actifs' avec les noms originaux).
        """
        if self.erreur:
            return {"erreur": self.erreur}

        actifs_dict = {}
        if self.actifs:
            # Re-extraire avec les noms originaux (alias)
            actifs_dict = self.actifs.model_dump(by_alias=True)
            # Borner par classe d'actif selon BORNES_ACTIFS
            for nom, valeur in actifs_dict.items():
                if nom in BORNES_ACTIFS:
                    mn, mx = BORNES_ACTIFS[nom]
                    actifs_dict[nom] = max(mn, min(mx, valeur))

        macro_dict = self.macro.model_dump() if self.macro else {"inflation": 0.0, "taux_directeurs": 0.0}

        return {
            "macro": macro_dict,
            "actifs": actifs_dict,
            "explication_courte": self.explication_courte or "",
            "evenement_reference": self.evenement_reference,
        }


_BORNE_GENERIQUE_CUSTOM = (-0.80, 2.00)
"""Bornes par defaut appliquees aux actifs personnalises (PERSO_*) inconnus
du schema. Couvre tickers actions/ETF/cryptos avec une marge raisonnable."""


def _extraire_extras_actifs(brut: dict) -> Dict[str, float]:
    """Recupere les actifs custom (cles inconnues du schema) en les normalisant.

    Le schema Pydantic a `extra="ignore"`, donc tout ticker custom serait
    perdu. On le recupere ici a partir du JSON brut, on normalise le choc
    et on applique une borne generique pour eviter les valeurs aberrantes.
    """
    if not isinstance(brut, dict):
        return {}
    actifs_brut = brut.get("actifs", {})
    if not isinstance(actifs_brut, dict):
        return {}

    cles_connues = set(BORNES_ACTIFS.keys())
    extras = {}
    mn, mx = _BORNE_GENERIQUE_CUSTOM
    for nom, val in actifs_brut.items():
        if nom in cles_connues:
            continue  # deja gere par le schema
        v = _normaliser_choc(val)
        extras[nom] = max(mn, min(mx, v))
    return extras


def valider_reponse_ia(brut: dict) -> dict:
    """
    Point d'entrée principal. Prend le JSON brut de l'IA, le valide,
    le normalise, le borne, et retourne un dict prêt à l'emploi.

    En cas d'échec total : retourne {"erreur": "..."}
    """
    try:
        reponse = ReponseAnalyseIA.model_validate(brut)
        resultat = reponse.to_legacy_dict()
        # Re-injecter les actifs custom (PERSO_*) que le schema a ignores
        if "actifs" in resultat:
            resultat["actifs"].update(_extraire_extras_actifs(brut))
        return resultat
    except Exception as e:
        # En cas d'erreur de validation, on tente une dernière passe
        # avec uniquement les chocs valides
        try:
            actifs_brut = brut.get("actifs", {}) if isinstance(brut, dict) else {}
            actifs_norm = {}
            mn_default, mx_default = _BORNE_GENERIQUE_CUSTOM
            for nom, val in actifs_brut.items():
                v = _normaliser_choc(val)
                if nom in BORNES_ACTIFS:
                    mn, mx = BORNES_ACTIFS[nom]
                else:
                    mn, mx = mn_default, mx_default
                actifs_norm[nom] = max(mn, min(mx, v))

            macro_brut = brut.get("macro", {}) if isinstance(brut, dict) else {}
            return {
                "macro": {
                    "inflation": float(macro_brut.get("inflation", 0)),
                    "taux_directeurs": float(macro_brut.get("taux_directeurs", 0)),
                },
                "actifs": actifs_norm,
                "explication_courte": brut.get("explication_courte", "") if isinstance(brut, dict) else "",
                "evenement_reference": brut.get("evenement_reference") if isinstance(brut, dict) else None,
            }
        except Exception:
            return {"erreur": f"Réponse IA invalide : {str(e)[:120]}"}