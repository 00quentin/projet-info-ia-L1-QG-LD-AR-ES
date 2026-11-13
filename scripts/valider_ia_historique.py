"""
scripts/valider_ia_historique.py
================================
L'IA à l'épreuve de l'histoire : pour chaque crise de
market_data.EVENEMENTS_HISTORIQUES, on décrit l'événement à l'IA sans le nommer
ni le dater, puis on compare ses chocs estimés aux vrais cours (Yahoo Finance,
en euros comme le backtest). Résultat : data/validation_ia.json, servi tel quel
par l'API (aucun appel IA pendant les visites).

Usage (depuis la racine du projet) :
    python scripts/valider_ia_historique.py                  # complète le fichier
    python scripts/valider_ia_historique.py --crise "Brexit (2016)"
    python scripts/valider_ia_historique.py --sans-ia        # cours et scores seulement
    python scripts/valider_ia_historique.py --forcer         # refait tous les appels IA

Une estimation déjà enregistrée est réutilisée tant que le prompt envoyé et le
modèle sont identiques : relancer le script ne coûte rien si rien n'a changé.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from openai import APIError, RateLimitError  # noqa: E402

import ia_bot  # noqa: E402
import market_data  # noqa: E402
from config import (  # noqa: E402
    ACTIF_TAUX_EUR_USD, ACTIFS_DISPONIBLES, DEVISE_ACTIF, IA_ANALYSE, IA_ANALYSE_SECOURS,
    NOM_AFFICHAGE,
)
from core.validation_ia import (  # noqa: E402
    SEUIL_SENS_PTS, agreger, arrondir, comparer_actifs, convertir_estimations_en_euros,
    crise_reconnue, duree_en_mots, indice_date, metriques_ecart, performances_reelles,
    verifier_neutralite,
)
from logger import get_logger  # noqa: E402
from schemas import BORNES_ACTIFS, valider_reponse_ia  # noqa: E402

log = get_logger("validation_ia")

FICHIER_SORTIE = RACINE / "data" / "validation_ia.json"
# Change quand la méthode de ce script change (pas le prompt du simulateur, suivi à part).
VERSION_PROTOCOLE = "validation-v1"
# L'IA n'estime ni la livre ni le yen : ces actifs sont comparés dans leur devise.
DEVISES_COMPAREES_EN_LOCAL = {"GBP", "JPY"}
# Garde-fou de coût : nombre maximal d'appels IA par exécution.
MAX_APPELS_PAR_DEFAUT = 14

# Ce que l'on dit à l'IA : le mécanisme de la crise, sans nom, sans date, sans
# chiffre de marché. Volontairement proche de ce qu'un visiteur taperait.
DESCRIPTIONS_NEUTRES = {
    "COVID-19 (mars 2020)": (
        "Un nouveau virus respiratoire très contagieux, apparu en Asie, se propage en "
        "quelques semaines à l'Europe et aux États-Unis. Les gouvernements ferment les "
        "frontières et imposent des confinements stricts : des pans entiers de l'économie "
        "mondiale s'arrêtent brutalement."
    ),
    "Krach 2008 (Lehman)": (
        "Une crise bancaire américaine : après l'effondrement du marché immobilier et des "
        "crédits hypothécaires à risque, une grande banque d'affaires fait faillite, "
        "d'autres institutions financières doivent être sauvées en urgence et le crédit "
        "se bloque dans le monde entier."
    ),
    "Bulle internet (2000-2002)": (
        "L'éclatement d'une bulle spéculative sur les valeurs technologiques : après des "
        "années d'euphorie autour des jeunes entreprises d'une nouvelle technologie de "
        "communication, leurs valorisations s'effondrent, beaucoup font faillite et "
        "l'investissement des entreprises recule."
    ),
    "Krach pétrolier (2014-2016)": (
        "Un effondrement durable du prix du pétrole : la production américaine de pétrole "
        "de schiste explose, le cartel des pays producteurs refuse de réduire la sienne "
        "pour défendre ses parts de marché, et la croissance chinoise ralentit."
    ),
    "Guerre Russie-Ukraine (2022)": (
        "Une grande puissance militaire, gros exportateur de gaz et de pétrole, envahit un "
        "pays voisin en Europe de l'Est. L'Occident répond par des sanctions économiques "
        "massives et les prix de l'énergie flambent en Europe, alors que l'inflation est "
        "déjà élevée et que la banque centrale américaine s'apprête à remonter fortement "
        "ses taux."
    ),
    "Brexit (2016)": (
        "Un grand pays européen, membre de l'union économique du continent mais doté de "
        "sa propre monnaie, vote par référendum, à la surprise générale, pour quitter "
        "cette union."
    ),
}

# Le prompt du simulateur raisonne sur 100 jours : seule cette consigne change,
# pour que l'IA estime la variation sur toute la durée réelle de la crise.
BLOC_HORIZON = """

    *** PARAMETRE PROPRE A CETTE ANALYSE (PRIORITAIRE SUR L'ETAPE 2) ***
    L'horizon n'est pas de 100 jours : il couvre toute la periode decrite dans le scenario,
    soit {nb_seances} seances de bourse ({duree}). Pour chaque actif, donne la variation
    TOTALE entre le debut et la fin de cette periode, dans sa devise de cotation (en dollars
    pour les actifs americains, les matieres premieres et les cryptos). Adapte les reperes
    d'amplitude a cette duree.
    """

_ORDRE_CATALOGUE = list(NOM_AFFICHAGE)
_CATEGORIE = {cle: cat for cat, actifs in ACTIFS_DISPONIBLES.items() for cle in actifs.values()}


def _nom_court(cle: str) -> str:
    """« VIX (CBOE Volatility Index) » → « VIX » : lisible dans un graphique."""
    return re.sub(r"\s*\(.*\)$", "", NOM_AFFICHAGE.get(cle, cle))


def _jour(iso: str) -> date:
    return datetime.strptime(iso, "%Y-%m-%d").date()


# === Appel IA ==============================================================


class CompteurAppels:
    """Compte les appels IA de l'exécution et refuse d'aller au-delà du plafond."""

    def __init__(self, maximum: int):
        self.maximum = maximum
        self.nb = 0

    def reserver(self) -> None:
        if self.nb >= self.maximum:
            raise RuntimeError(f"Plafond de {self.maximum} appels IA atteint : arrêt.")
        self.nb += 1


def construire_prompt(scenario: str, nb_seances: int, duree: str) -> str:
    """Prompt du simulateur (sans calibration historique, sans conjoncture du jour),
    horizon adapté à la durée de la crise."""
    scenario_propre = ia_bot._sanitize_scenario(scenario)
    prompt = ia_bot._build_prompt_macro(scenario_propre, calibration_historique=False,
                                        custom_tickers=None, conjoncture="")
    return prompt + BLOC_HORIZON.format(nb_seances=nb_seances, duree=duree)


def empreinte(prompt: str) -> str:
    """Identifie un appel : même prompt et mêmes réglages → même estimation réutilisable."""
    contenu = json.dumps({"prompt": prompt, "reglages": IA_ANALYSE}, sort_keys=True)
    return hashlib.sha256(contenu.encode("utf-8")).hexdigest()[:16]


def _choc_normalise(valeur) -> float:
    """Même convention que schemas.py : 25 → 0.25."""
    try:
        v = float(valeur)
    except (TypeError, ValueError):
        return 0.0
    return v / 100 if abs(v) > 5 else v


def appeler_ia(prompt: str, scenario: str, compteur: CompteurAppels) -> dict:
    """Un appel au modèle d'analyse du simulateur (repli sur le modèle de secours
    comme en production), réponse validée par schemas.py."""
    client = ia_bot._get_openai_client()
    messages = [{"role": "user", "content": prompt}]
    reglages = IA_ANALYSE
    compteur.reserver()
    try:
        reponse = client.chat.completions.create(
            messages=messages, response_format={"type": "json_object"}, **IA_ANALYSE)
    except RateLimitError:
        raise
    except APIError as e:
        log.warning("Modèle %s en échec (%s), repli sur %s",
                    IA_ANALYSE["model"], str(e)[:80], IA_ANALYSE_SECOURS["model"])
        reglages = IA_ANALYSE_SECOURS
        compteur.reserver()
        reponse = client.chat.completions.create(
            messages=messages, response_format={"type": "json_object"}, **IA_ANALYSE_SECOURS)

    brut = json.loads(reponse.choices[0].message.content)
    valide = valider_reponse_ia(brut)
    if "erreur" in valide:
        raise RuntimeError(f"Réponse IA rejetée : {valide['erreur']}")
    actifs_bruts = brut.get("actifs", {}) if isinstance(brut, dict) else {}
    return {
        "empreinte": empreinte(prompt),
        "date": datetime.now().isoformat(timespec="seconds"),
        "modele": reponse.model,
        "reglages": reglages,
        "scenario": scenario,
        "chocs": {cle: float(v) for cle, v in valide["actifs"].items() if cle in BORNES_ACTIFS},
        "chocs_bruts": {cle: _choc_normalise(v) for cle, v in actifs_bruts.items()
                        if cle in BORNES_ACTIFS},
        "evenement_cite": valide.get("evenement_reference"),
        "references": valide.get("references_historiques") or [],
        "explication": valide.get("explication_courte") or "",
    }


def obtenir_estimation(prompt: str, scenario: str, ancienne: dict | None,
                       appeler: bool, forcer: bool, compteur: CompteurAppels) -> dict | None:
    """Réutilise l'estimation enregistrée si elle répond au même prompt, sinon appelle l'IA."""
    if ancienne and (not appeler or (not forcer and ancienne.get("empreinte") == empreinte(prompt))):
        return ancienne
    if not appeler:
        return None
    return appeler_ia(prompt, scenario, compteur)


# === Comparaison avec les vrais cours ======================================


def comparer(estimation: dict, reels_eur: dict, reels_local: dict) -> tuple[list, list]:
    """Lignes de comparaison en euros (comme le backtest) et en devise d'origine."""
    chocs = estimation["chocs"]
    en_euros = convertir_estimations_en_euros(chocs, DEVISE_ACTIF, chocs.get(ACTIF_TAUX_EUR_USD, 0.0))
    estimes, reels = {}, {}
    for cle in reels_eur:
        if cle not in chocs:
            continue
        if DEVISE_ACTIF.get(cle) in DEVISES_COMPAREES_EN_LOCAL:
            if cle in reels_local:
                estimes[cle], reels[cle] = chocs[cle] * 100, reels_local[cle]
        else:
            estimes[cle], reels[cle] = en_euros[cle] * 100, reels_eur[cle]
    lignes_eur = comparer_actifs(estimes, reels)
    lignes_local = comparer_actifs({c: v * 100 for c, v in chocs.items()},
                                   {c: v for c, v in reels_local.items() if c in reels_eur})
    return lignes_eur, lignes_local


def _devise_affichee(cle: str):
    devise = DEVISE_ACTIF.get(cle)
    if devise is None:
        return None
    return devise if devise in DEVISES_COMPAREES_EN_LOCAL else "EUR"


def _reconnue(estimation: dict, debut: date, fin: date) -> bool:
    return crise_reconnue([estimation.get("evenement_cite"), estimation.get("explication"),
                           json.dumps(estimation.get("references"), ensure_ascii=False)], debut, fin)


def traiter_crise(nom: str, infos: dict, ancienne: dict | None, appeler: bool,
                  forcer: bool, compteur: CompteurAppels) -> dict | None:
    description = DESCRIPTIONS_NEUTRES.get(nom)
    if description is None:
        raise SystemExit(f"Pas de description neutre pour « {nom} » : ajoutez-la dans DESCRIPTIONS_NEUTRES.")
    probleme = verifier_neutralite(description, nom)
    if probleme:
        raise SystemExit(f"Description de « {nom} » non neutre : {probleme}")

    debut, fin = _jour(infos["debut"]), _jour(infos["fin"])
    cles = list(market_data.TICKERS_YAHOO)
    df_eur = market_data.get_historique(cles, infos["debut"], infos["fin"],
                                        convertir_eur=True, avec_dates=True)
    df_local = market_data.get_historique(cles, infos["debut"], infos["fin"],
                                          convertir_eur=False, avec_dates=True)
    if df_eur.empty or df_local.empty:
        raise SystemExit(f"Cours indisponibles pour « {nom} » (Yahoo ou BCE injoignable) : fichier inchangé.")
    reels_eur = {c: v for c, v in performances_reelles(df_eur).items() if c in _ORDRE_CATALOGUE}
    reels_eur = {c: reels_eur[c] for c in _ORDRE_CATALOGUE if c in reels_eur}
    reels_local = performances_reelles(df_local)

    nb_seances = len(df_eur)
    duree = duree_en_mots(debut, fin)
    scenario = (f"{description} La période étudiée dure {duree} ({nb_seances} séances de bourse), "
                f"à partir du début de la crise.")
    scenario_date = f"{scenario} {indice_date(debut, fin)}"
    anciennes = ancienne or {}

    estimation = obtenir_estimation(construire_prompt(scenario, nb_seances, duree), scenario,
                                    anciennes.get("estimation"), appeler, forcer, compteur)
    if estimation is None:
        log.warning("Aucune estimation enregistrée pour « %s » : crise ignorée.", nom)
        return None
    estimation_date = obtenir_estimation(construire_prompt(scenario_date, nb_seances, duree),
                                         scenario_date, anciennes.get("estimation_avec_date"),
                                         appeler, forcer, compteur)

    lignes, lignes_local = comparer(estimation, reels_eur, reels_local)
    actifs = []
    for ligne in lignes:
        cle = ligne["cle"]
        brut, valide = estimation["chocs_bruts"].get(cle), estimation["chocs"][cle]
        actifs.append({
            **ligne,
            "nom": NOM_AFFICHAGE.get(cle, cle),
            "nom_court": _nom_court(cle),
            "categorie": _CATEGORIE.get(cle),
            "devise": _devise_affichee(cle),
            "estime_devise_pct": valide * 100,
            "ecrete": brut is not None and abs(brut - valide) > 1e-9,
        })

    avec_date = None
    if estimation_date is not None:
        lignes_date, _ = comparer(estimation_date, reels_eur, reels_local)
        avec_date = {
            "indice": indice_date(debut, fin),
            "reconnue": _reconnue(estimation_date, debut, fin),
            "evenement_cite": estimation_date.get("evenement_cite"),
            "metriques": metriques_ecart(lignes_date),
            "estimes_pct": {l["cle"]: l["estime_pct"] for l in lignes_date},
            "_lignes": lignes_date,
        }

    index = [d.strftime("%Y-%m-%d") for d in df_eur.index]
    return {
        "nom": nom,
        "debut": infos["debut"],
        "fin": infos["fin"],
        "premiere_seance": index[0],
        "derniere_seance": index[-1],
        "nb_seances": nb_seances,
        "duree": duree,
        "description_neutre": description,
        "scenario_envoye": scenario,
        "reconnue": _reconnue(estimation, debut, fin),
        "evenement_cite": estimation.get("evenement_cite"),
        "explication": estimation.get("explication"),
        "modele": estimation.get("modele"),
        "metriques": metriques_ecart(lignes),
        "metriques_devise_locale": metriques_ecart(lignes_local),
        "actifs": actifs,
        "actifs_absents": [{"cle": c, "nom": NOM_AFFICHAGE.get(c, c)}
                           for c in _ORDRE_CATALOGUE if c not in reels_eur],
        "avec_date": avec_date,
        "estimation": estimation,
        "estimation_avec_date": estimation_date,
        "_lignes": lignes,
        "_lignes_local": lignes_local,
    }


# === Assemblage du fichier =================================================


def assembler(crises: list[dict]) -> dict:
    avec_variante = [c for c in crises if c["avec_date"]]
    modeles = sorted({c["modele"] for c in crises if c.get("modele")}
                     | {c["estimation_avec_date"]["modele"] for c in avec_variante})
    resultat = {
        "genere_le": datetime.now().isoformat(timespec="seconds"),
        "protocole": {
            "version": VERSION_PROTOCOLE,
            "version_prompt": ia_bot.PROMPT_VERSION,
            "modele": IA_ANALYSE["model"],
            "reglages_ia": IA_ANALYSE,
            "modeles_utilises": modeles,
            "calibration_historique": False,
            "conjoncture_du_jour": False,
            "seuil_sens_pts": SEUIL_SENS_PTS,
            "devise": "EUR",
            "devises_locales": sorted(DEVISES_COMPAREES_EN_LOCAL),
            "source_cours": "Yahoo Finance, convertis en euros au taux de référence BCE",
        },
        "global": agreger(c["_lignes"] for c in crises),
        "global_devise_locale": agreger(c["_lignes_local"] for c in crises),
        "biais_connaissance": {
            "nb_crises": len(avec_variante),
            "sans_date": agreger(c["_lignes"] for c in avec_variante),
            "avec_date": agreger(c["avec_date"]["_lignes"] for c in avec_variante),
            "nb_reconnues_sans_date": sum(1 for c in avec_variante if c["reconnue"]),
            "nb_reconnues_avec_date": sum(1 for c in avec_variante if c["avec_date"]["reconnue"]),
        },
        "crises": [],
    }
    for crise in crises:
        propre = {k: v for k, v in crise.items() if not k.startswith("_")}
        if propre["avec_date"]:
            propre["avec_date"] = {k: v for k, v in propre["avec_date"].items() if not k.startswith("_")}
        resultat["crises"].append(propre)
    # Les chocs (décimaux) gardent 4 décimales, le reste 2 (points de %) ou 3 (corrélations).
    return _arrondir_fichier(resultat)


def _arrondir_fichier(resultat: dict) -> dict:
    for crise in resultat["crises"]:
        for cle in ("estimation", "estimation_avec_date"):
            est = crise.get(cle)
            if est:
                est["chocs"] = arrondir(est["chocs"], 4)
                est["chocs_bruts"] = arrondir(est["chocs_bruts"], 4)
    for bloc in (resultat["global"], resultat["global_devise_locale"],
                 resultat["biais_connaissance"]["sans_date"], resultat["biais_connaissance"]["avec_date"]):
        _arrondir_metriques(bloc)
    for crise in resultat["crises"]:
        _arrondir_metriques(crise["metriques"])
        _arrondir_metriques(crise["metriques_devise_locale"])
        crise["actifs"] = arrondir(crise["actifs"], 2)
        if crise["avec_date"]:
            _arrondir_metriques(crise["avec_date"]["metriques"])
            crise["avec_date"]["estimes_pct"] = arrondir(crise["avec_date"]["estimes_pct"], 2)
    return resultat


def _arrondir_metriques(m: dict) -> None:
    for cle, valeur in list(m.items()):
        if isinstance(valeur, float):
            m[cle] = arrondir(valeur, 3 if cle in ("correlation", "correlation_rangs",
                                                   "part_sens_correct", "ratio_amplitude") else 2)


def _afficher_resume(resultat: dict) -> None:
    def ligne(nom, m):
        corr = m["correlation"]
        part = m["part_sens_correct"]
        print(f"  {nom:<30} erreur {m['erreur_moyenne_pts']:6.1f} pts | bon sens "
              f"{m['nb_sens_corrects']:>2}/{m['nb_sens_comptes']:<2} ({(part or 0) * 100:3.0f} %) | "
              f"corrélation {corr if corr is not None else float('nan'):5.2f} | "
              f"amplitude ×{m['ratio_amplitude'] or 0:.2f}")
    print("\nRésultats (en euros) :")
    for crise in resultat["crises"]:
        ligne(crise["nom"], crise["metriques"])
        if crise["avec_date"]:
            ligne("   … avec la date", crise["avec_date"]["metriques"])
    ligne("GLOBAL", resultat["global"])
    ligne("GLOBAL (devise d'origine)", resultat["global_devise_locale"])
    b = resultat["biais_connaissance"]
    ligne("Biais : sans date", b["sans_date"])
    ligne("Biais : avec date", b["avec_date"])
    print(f"  Crises reconnues sans date : {b['nb_reconnues_sans_date']}/{b['nb_crises']}, "
          f"avec date : {b['nb_reconnues_avec_date']}/{b['nb_crises']}")


def main(arguments=None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parseur.add_argument("--crise", action="append", help="limiter les appels IA à cette crise (répétable)")
    parseur.add_argument("--sans-ia", action="store_true", help="aucun appel IA : réutilise les estimations enregistrées")
    parseur.add_argument("--forcer", action="store_true", help="refait les appels IA même si rien n'a changé")
    parseur.add_argument("--max-appels", type=int, default=MAX_APPELS_PAR_DEFAUT, help="plafond d'appels IA")
    args = parseur.parse_args(arguments)

    inconnues = set(args.crise or []) - set(market_data.EVENEMENTS_HISTORIQUES)
    if inconnues:
        raise SystemExit(f"Crise inconnue : {', '.join(sorted(inconnues))}")
    if not args.sans_ia and not ia_bot._cle_api():
        raise SystemExit("OPENAI_API_KEY absente : utilisez --sans-ia ou renseignez la clé.")

    anciennes = {}
    if FICHIER_SORTIE.exists():
        anciennes = {c["nom"]: c for c in json.loads(FICHIER_SORTIE.read_text(encoding="utf-8"))["crises"]}

    compteur = CompteurAppels(args.max_appels)
    crises = []
    for nom, infos in market_data.EVENEMENTS_HISTORIQUES.items():
        appeler = not args.sans_ia and (not args.crise or nom in args.crise)
        resultat = traiter_crise(nom, infos, anciennes.get(nom), appeler, args.forcer, compteur)
        if resultat:
            crises.append(resultat)
    if not crises:
        raise SystemExit("Aucune crise estimée : rien à écrire.")

    resultat = assembler(crises)
    FICHIER_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    FICHIER_SORTIE.write_text(json.dumps(resultat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _afficher_resume(resultat)
    print(f"\n{compteur.nb} appel(s) IA. Écrit : {FICHIER_SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
