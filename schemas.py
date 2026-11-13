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

Chaque actif peut arriver sous deux formes : un nombre (le choc central, ancien
format) ou une fourchette {"bas", "central", "haut"} qui traduit le doute de l'IA.
"""

import math
from typing import Optional, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, ValidationError

from config import (
    FOURCHETTE_AMPLITUDE_REF_MAX,
    FOURCHETTE_DEMI_LARGEUR_MIN,
    FOURCHETTE_ELARGISSEMENT_AGGRAVATION,
    FOURCHETTE_ELARGISSEMENT_ATTENUATION,
)
from logger import get_logger

log = get_logger("schemas")


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


class FourchetteChoc(BaseModel):
    """
    Doute de l'IA sur un actif : choc bas <= central <= haut (décimaux).
    Le central est obligatoire ; sans bas ni haut, la fourchette se réduit au central.
    """
    model_config = ConfigDict(extra="ignore")

    central: float
    bas: Optional[float] = None
    haut: Optional[float] = None

    @field_validator("central")
    @classmethod
    def _central_fini(cls, v):
        if not math.isfinite(v):
            raise ValueError("choc central non fini")
        return v

    @field_validator("bas", "haut", mode="before")
    @classmethod
    def _borne_lisible(cls, v):
        # Une borne illisible est ignorée : le central suffit à simuler.
        try:
            v = float(v)
        except (TypeError, ValueError):
            return None
        return v if math.isfinite(v) else None

    @model_validator(mode="after")
    def _normaliser_et_ordonner(self):
        valeurs = [v for v in (self.bas, self.central, self.haut) if v is not None]
        # Les trois valeurs sont dans la même unité : si l'une est manifestement un
        # pourcentage (25 au lieu de 0.25), toutes le sont.
        diviseur = 100.0 if any(abs(v) > 5 for v in valeurs) else 1.0
        c = self.central / diviseur
        b = self.bas / diviseur if self.bas is not None else c
        h = self.haut / diviseur if self.haut is not None else c
        if b > h:  # bornes inversées par l'IA
            b, h = h, b
        self.central, self.bas, self.haut = c, min(b, c), max(h, c)
        return self

    def encadrer(self, central: float, mn: float, mx: float) -> Dict[str, float]:
        """Fourchette autour du central final (déjà borné), bornée par classe d'actif."""
        return {
            "bas": max(mn, min(self.bas, central)),
            "central": central,
            "haut": min(mx, max(self.haut, central)),
        }


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


class ReferenceHistorique(BaseModel):
    """Un evenement historique pondere pour la calibration en mix."""
    model_config = ConfigDict(extra="ignore")
    evenement: str = ""
    annee: Optional[int] = None
    poids: float = 0.0
    raison: str = ""

    @field_validator("poids", mode="before")
    @classmethod
    def _normaliser_poids(cls, v):
        # Clamp dans [0, 1]. Si l'IA renvoie 60 (au lieu de 0.6), on divise par 100.
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0.0
        if v > 1.0:
            v = v / 100.0
        return max(0.0, min(1.0, v))


class FiabiliteCalibration(BaseModel):
    """Score de confiance qualitatif sur la calibration."""
    model_config = ConfigDict(extra="ignore")
    niveau: Literal["elevee", "moyenne", "faible"] = "moyenne"
    raison: str = ""


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
    references_historiques: List[ReferenceHistorique] = Field(default_factory=list)
    fiabilite_calibration: Optional[FiabiliteCalibration] = None

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

        # Normalise les references : limite a 3, renormalise les poids a 1.0 si besoin
        refs = [r.model_dump() for r in self.references_historiques[:3] if r.poids > 0]
        total_poids = sum(r["poids"] for r in refs)
        if total_poids > 0 and abs(total_poids - 1.0) > 0.05:
            for r in refs:
                r["poids"] = r["poids"] / total_poids

        return {
            "macro": macro_dict,
            "actifs": actifs_dict,
            "explication_courte": self.explication_courte or "",
            "evenement_reference": self.evenement_reference,
            "references_historiques": refs,
            "fiabilite_calibration": (
                self.fiabilite_calibration.model_dump()
                if self.fiabilite_calibration else None
            ),
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


def _separer_fourchettes(brut) -> tuple:
    """Remplace chaque fourchette {"bas", "central", "haut"} de brut["actifs"] par
    son central (le reste de la validation ne voit que des nombres).

    Returns:
        (brut avec des chocs centraux, {actif: FourchetteChoc})
    """
    if not isinstance(brut, dict) or not isinstance(brut.get("actifs"), dict):
        return brut, {}
    centraux, fourchettes = {}, {}
    for nom, valeur in brut["actifs"].items():
        if not isinstance(valeur, dict):
            centraux[nom] = valeur  # ancien format : le nombre est le central
            continue
        try:
            fourchettes[nom] = FourchetteChoc.model_validate(valeur)
        except ValidationError:
            log.warning("Fourchette IA sans choc central lisible pour %s : actif ignoré", nom)
            continue
        centraux[nom] = fourchettes[nom].central
    return {**brut, "actifs": centraux}, fourchettes


def bornes_actif(nom: str) -> tuple:
    """Bornes (min, max) du choc d'un actif : catalogue, sinon borne des actifs perso."""
    return BORNES_ACTIFS.get(nom, _BORNE_GENERIQUE_CUSTOM)


def elargir_fourchette(fourchette: Dict[str, float], mn: float, mx: float) -> Dict[str, float]:
    """Recale une fourchette de l'IA sur les crises passées (voir config.py) :
    élargit le côté aggravation (loin de zéro) et le côté atténuation, impose une
    demi-largeur minimale proportionnelle à l'amplitude de l'actif, puis reborne.
    Une fourchette réduite au central (pas de doute exprimé) reste telle quelle."""
    bas, central, haut = fourchette["bas"], fourchette["central"], fourchette["haut"]
    if bas == central == haut:
        return dict(fourchette)
    minimum = FOURCHETTE_DEMI_LARGEUR_MIN * min(mx - mn, FOURCHETTE_AMPLITUDE_REF_MAX)
    baisse = central < 0
    ecart_aggravation = (central - bas) if baisse else (haut - central)
    ecart_attenuation = (haut - central) if baisse else (central - bas)
    ecart_aggravation = max(ecart_aggravation * FOURCHETTE_ELARGISSEMENT_AGGRAVATION, minimum)
    ecart_attenuation = max(ecart_attenuation * FOURCHETTE_ELARGISSEMENT_ATTENUATION, minimum)
    if baisse:
        bas, haut = central - ecart_aggravation, central + ecart_attenuation
    else:
        bas, haut = central - ecart_attenuation, central + ecart_aggravation
    return {"bas": max(mn, bas), "central": central, "haut": min(mx, haut)}


def _encadrer_actifs(actifs: Dict[str, float],
                     fourchettes: Dict[str, FourchetteChoc]) -> Dict[str, Dict[str, float]]:
    """Fourchette bas / central / haut donnée par l'IA, autour du choc final de chaque actif."""
    sortie = {}
    for nom, central in actifs.items():
        mn, mx = bornes_actif(nom)
        fourchette = fourchettes.get(nom)
        sortie[nom] = (fourchette.encadrer(central, mn, mx) if fourchette
                       else {"bas": central, "central": central, "haut": central})
    return sortie


def elargir_fourchettes(fourchettes_ia: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Applique elargir_fourchette à chaque actif (fourchettes simulées et affichées)."""
    return {nom: elargir_fourchette(f, *bornes_actif(nom)) for nom, f in fourchettes_ia.items()}


def valider_reponse_ia(brut: dict) -> dict:
    """
    Point d'entrée principal. Prend le JSON brut de l'IA, le valide,
    le normalise, le borne, et retourne un dict prêt à l'emploi.

    "actifs" garde un choc central par actif ; "fourchettes_ia" donne pour
    chaque actif {"bas", "central", "haut"} tel que l'IA l'a estimé (bas = haut
    = central si elle n'a pas donné de fourchette) ; "fourchettes" est la même
    fourchette recalée sur les crises passées, celle que la simulation utilise.

    En cas d'échec total : retourne {"erreur": "..."}
    """
    brut, fourchettes = _separer_fourchettes(brut)
    resultat = _valider_centraux(brut)
    if "actifs" in resultat:
        resultat["fourchettes_ia"] = _encadrer_actifs(resultat["actifs"], fourchettes)
        resultat["fourchettes"] = elargir_fourchettes(resultat["fourchettes_ia"])
    return resultat


def _valider_centraux(brut: dict) -> dict:
    """Validation des chocs centraux, de la macro et des textes de l'IA."""
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
                "references_historiques": brut.get("references_historiques", []) if isinstance(brut, dict) else [],
                "fiabilite_calibration": brut.get("fiabilite_calibration") if isinstance(brut, dict) else None,
            }
        except Exception:
            return {"erreur": f"Réponse IA invalide : {str(e)[:120]}"}