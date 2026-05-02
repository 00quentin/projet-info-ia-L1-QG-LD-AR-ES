"""
tests/test_handlers.py
======================
Tests des helpers internes de handlers.py.

Strategie : on ne teste pas les handlers complets (handler_simulation /
handler_backtest) qui couplent fortement Streamlit + appels reseau OpenAI
+ Yahoo Finance -- ce sont des integrations end-to-end, pas du domaine
unitaire. On teste ici les 3 helpers purs qui contiennent la logique
metier extractible :

- _valider_actifs_et_allocation(config) -> bool
  Garde-fou commun aux 2 modes : actifs vides ou allocation custom != 100%.

- _message_attente_simulation(config) -> str
  Selection du libelle spinner selon le mode (MC / calibration / nb scenarios).

- _enregistrer_historique(...) -> None
  Construction de l'entree d'historique (date, troncature scenario,
  calcul perf%) et ecriture via ajouter_entree.

Mocking : on remplace handlers.st.session_state, handlers.notify_warn et
handlers.ajouter_entree -- pas besoin de Streamlit ni du disque.
"""

import pytest

import handlers


# === Mocks =================================================================


class FakeSessionState:
    """Imite st.session_state : acces par attribut ET par cle."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, key):
        return key in self.__dict__


@pytest.fixture
def warns(monkeypatch):
    """Capture tous les appels a notify_warn."""
    captured = []
    monkeypatch.setattr(handlers, "notify_warn", lambda msg: captured.append(msg))
    return captured


@pytest.fixture
def session(monkeypatch):
    """Fournit un st.session_state vide remplacable par les tests."""
    state = FakeSessionState()
    monkeypatch.setattr(handlers.st, "session_state", state)
    return state


# === _valider_actifs_et_allocation ========================================


def test_valider_actifs_vides_renvoie_false(warns):
    config = {"actifs_selectionnes": [], "profil_risque": "Équilibré (Normal)",
              "allocations_custom": {}}
    assert handlers._valider_actifs_et_allocation(config) is False
    assert len(warns) == 1
    assert "actif" in warns[0].lower()


def test_valider_actifs_ok_profil_predefini(warns):
    """Profil non-personnalise : aucun check sur l'allocation."""
    config = {"actifs_selectionnes": ["S&P 500"],
              "profil_risque": "Équilibré (Normal)",
              "allocations_custom": {"S&P 500": 42}}  # somme bizarre, mais ignoree
    assert handlers._valider_actifs_et_allocation(config) is True
    assert warns == []


def test_valider_personnalise_allocation_pas_a_100(warns):
    config = {"actifs_selectionnes": ["S&P 500", "Or"],
              "profil_risque": "Personnalisé",
              "allocations_custom": {"S&P 500": 60, "Or": 30}}
    assert handlers._valider_actifs_et_allocation(config) is False
    assert "100%" in warns[0]
    assert "90" in warns[0]  # le total actuel apparait dans le message


def test_valider_personnalise_allocation_a_100(warns):
    config = {"actifs_selectionnes": ["S&P 500", "Or"],
              "profil_risque": "Personnalisé",
              "allocations_custom": {"S&P 500": 60, "Or": 40}}
    assert handlers._valider_actifs_et_allocation(config) is True
    assert warns == []


# === _message_attente_simulation ==========================================


def test_message_n_scenarios(session):
    """En mode comparaison, le message annonce le nombre de scenarios."""
    session.nb_scenarios = 3
    config = {"mode_monte_carlo": False, "calibration_historique": False}
    msg = handlers._message_attente_simulation(config)
    assert "3 scénarios" in msg


def test_message_monte_carlo_prioritaire_sur_calibration(session):
    session.nb_scenarios = 1
    config = {"mode_monte_carlo": True, "calibration_historique": True}
    msg = handlers._message_attente_simulation(config)
    assert "Monte-Carlo" in msg


def test_message_calibration(session):
    session.nb_scenarios = 1
    config = {"mode_monte_carlo": False, "calibration_historique": True}
    msg = handlers._message_attente_simulation(config)
    assert "analogies historiques" in msg


def test_message_default(session):
    session.nb_scenarios = 1
    config = {"mode_monte_carlo": False, "calibration_historique": False}
    msg = handlers._message_attente_simulation(config)
    assert "scénario" in msg.lower()


def test_message_comparaison_prioritaire_sur_mc(session):
    """nb_scenarios > 1 prend le pas sur monte_carlo / calibration."""
    session.nb_scenarios = 2
    config = {"mode_monte_carlo": True, "calibration_historique": True}
    msg = handlers._message_attente_simulation(config)
    assert "comparative" in msg
    assert "Monte-Carlo" not in msg


# === _enregistrer_historique ==============================================


@pytest.fixture
def stub_ajouter(monkeypatch):
    """Remplace ajouter_entree (qui ecrit sur disque) par un stub in-memory."""
    captured = []

    def fake_ajouter(historique, entree, taille_max, repertoire=None):
        captured.append({"entree": entree, "taille_max": taille_max,
                          "historique_avant": list(historique)})
        return [entree] + historique

    monkeypatch.setattr(handlers, "ajouter_entree", fake_ajouter)
    return captured


def test_enregistrer_calcule_perf_correctement(session, stub_ajouter):
    session.historique_simus = []
    handlers._enregistrer_historique(
        scenario="Test scenario", profil="Équilibré (Normal)",
        capital=10_000, valeur_finale=12_500,
        monte_carlo=False, nb_actifs=4, type_op="Simulation",
    )
    entree = stub_ajouter[0]["entree"]
    assert entree["perf"] == pytest.approx(25.0)
    assert entree["scenario"] == "Test scenario"
    assert entree["valeur_finale"] == 12_500


def test_enregistrer_perf_negative(session, stub_ajouter):
    session.historique_simus = []
    handlers._enregistrer_historique(
        scenario="Crash", profil="Agressif", capital=10_000,
        valeur_finale=7_500, monte_carlo=True, nb_actifs=3,
        type_op="Simulation", label_compare="A",
    )
    entree = stub_ajouter[0]["entree"]
    assert entree["perf"] == pytest.approx(-25.0)
    assert entree["label_compare"] == "A"
    assert entree["monte_carlo"] is True


def test_enregistrer_capital_zero_ne_divise_pas(session, stub_ajouter):
    """Garde-fou : si capital = 0, perf retombe a 0 sans ZeroDivisionError."""
    session.historique_simus = []
    handlers._enregistrer_historique(
        scenario="Edge", profil="Prudent", capital=0,
        valeur_finale=0, monte_carlo=False, nb_actifs=1,
        type_op="Simulation",
    )
    assert stub_ajouter[0]["entree"]["perf"] == 0.0


def test_enregistrer_tronque_scenario_long(session, stub_ajouter):
    session.historique_simus = []
    long_scenario = "X" * 200
    handlers._enregistrer_historique(
        scenario=long_scenario, profil="Équilibré (Normal)", capital=1000,
        valeur_finale=1100, monte_carlo=False, nb_actifs=1,
        type_op="Simulation",
    )
    entree = stub_ajouter[0]["entree"]
    assert entree["scenario"].endswith("...")
    assert len(entree["scenario"]) == 83  # 80 X + "..."


def test_enregistrer_scenario_court_pas_tronque(session, stub_ajouter):
    session.historique_simus = []
    handlers._enregistrer_historique(
        scenario="Court", profil="Prudent", capital=1000,
        valeur_finale=1050, monte_carlo=False, nb_actifs=1,
        type_op="Simulation",
    )
    entree = stub_ajouter[0]["entree"]
    assert entree["scenario"] == "Court"
    assert "..." not in entree["scenario"]


def test_enregistrer_met_a_jour_session_state(session, stub_ajouter):
    """Apres un appel, st.session_state.historique_simus contient l'entree."""
    session.historique_simus = [{"id": "vieille"}]
    handlers._enregistrer_historique(
        scenario="Nouveau", profil="Équilibré (Normal)", capital=1000,
        valeur_finale=1100, monte_carlo=False, nb_actifs=1,
        type_op="Simulation",
    )
    # Le stub_ajouter retourne [entree] + historique
    assert session.historique_simus[0]["scenario"] == "Nouveau"
    assert session.historique_simus[1] == {"id": "vieille"}


def test_enregistrer_type_backtest(session, stub_ajouter):
    session.historique_simus = []
    handlers._enregistrer_historique(
        scenario="Krach 2008", profil="Prudent", capital=10_000,
        valeur_finale=9_500, monte_carlo=False, nb_actifs=2,
        type_op="Backtest",
    )
    assert stub_ajouter[0]["entree"]["type"] == "Backtest"
    assert stub_ajouter[0]["entree"]["label_compare"] is None
