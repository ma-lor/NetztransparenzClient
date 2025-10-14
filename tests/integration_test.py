import os
import datetime as dt
import pytest

import netztransparenz as nt

START = dt.datetime(2020, 1, 1, 0, 0)
END = dt.datetime(2020, 2, 1, 0, 0)
HOURS_IN_MONTH = 24*31
QUARTERS_IN_MONTH = HOURS_IN_MONTH * 4

@pytest.fixture
def client():
    id = os.environ.get("IPNT_CLIENT_ID")
    secret = os.environ.get("IPNT_CLIENT_SECRET")
    return nt.NetztransparenzClient(id, secret)

@pytest.mark.api_access
def test_hochrechnung_solar(client):
    result = client.hochrechnung_solar(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH

@pytest.mark.api_access
def test_hochrechnung_wind(client):
    result = client.hochrechnung_wind(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH

@pytest.mark.api_access
def test_online_hochrechnung_windonshore(client):
    result = client.online_hochrechnung_windonshore(START, END, True)
    assert result["bis"].count() == HOURS_IN_MONTH

@pytest.mark.api_access
def test_online_hochrechnung_windoffshore(client):
    result = client.online_hochrechnung_windoffshore(START, END, True)
    assert result["bis"].count() == HOURS_IN_MONTH

@pytest.mark.api_access
def test_online_hochrechnung_solar(client):
    result = client.online_hochrechnung_solar(START, END, True)
    assert result["bis"].count() == HOURS_IN_MONTH

@pytest.mark.api_access
def test_vermarktung_differenz_einspeiseprognose(client):
    result = client.vermarktung_differenz_einspeiseprognose(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH

@pytest.mark.api_access
def test_vermarktung_inanspruchnahme_ausgleichsenergie(client):
    result = client.vermarktung_inanspruchnahme_ausgleichsenergie(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH

@pytest.mark.api_access
def test_vermarktung_untertaegige_strommengen(client):
    result = client.vermarktung_untertaegige_strommengen(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH

@pytest.mark.api_access
def test_redispatch(client):
    result = client.redispatch(dt.datetime(2022, 1, 1, 0 ,0), dt.datetime(2022, 1, 31), True)
    assert result["BEGINN"].count() == 1523

@pytest.mark.api_access
def test_prognose_solar(client):
    result = client.prognose_solar(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH

@pytest.mark.api_access
def test_prognose_wind(client):
    result = client.prognose_wind(START, END, True)
    assert result["bis"].count() == QUARTERS_IN_MONTH




