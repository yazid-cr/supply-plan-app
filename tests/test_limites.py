"""TP4 — 8 cas limites + 2 proprietes (hypothesis)."""
from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tests.conftest import CONTRAT

BLANCS = " \t\n\r\x0b\x0c         "


@pytest.mark.parametrize(
    "texte",
    ["", " ", "   ", "\t\n", "x" * 2001, 42, None, "x" * 5000],
)
def test_cas_limites_refuses(client, texte):
    r = client.post("/predict", json={"text": texte})
    assert r.status_code == 422
    assert r.status_code != 500


def test_limite_exacte_2000_acceptee(client):
    r = client.post("/predict", json={"text": "demande " + "x" * 1992})
    # 2000 chars exactly (8 + 1992) gets through the contract
    assert len("demande " + "x" * 1992) == 2000
    assert r.status_code == 200


@settings(
    max_examples=150,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(texte=st.text(min_size=1, max_size=2000).filter(lambda s: s.strip()))
def test_tout_texte_non_blanc_recoit_une_reponse(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    assert reponse.json()["label"] in CONTRAT


@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    texte=st.text(
        alphabet=st.sampled_from(BLANCS), min_size=1, max_size=50
    ).filter(lambda s: not s.strip())
)
def test_tout_texte_blanc_est_refuse(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 422
