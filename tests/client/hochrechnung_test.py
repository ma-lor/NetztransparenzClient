import datetime as dt
import pandas as pd
import pytest

import netztransparenz as nt

START = dt.datetime(2020, 1, 1, 0, 0)
END = dt.datetime(2020, 2, 1, 0, 0)
_API_BASE_URL = "https://ds.netztransparenz.de/api/v1"

@pytest.fixture(autouse=True)
def token(requests_mock):
    requests_mock.post("https://identity.netztransparenz.de/users/connect/token", json= {"access_token": "placeholder_token"})

@pytest.fixture
def client(token):
    id = "PLACEHOLDER_ID"
    secret = "PLACEHOLDER_SECRET"
    return nt.NetztransparenzClient(id, secret)

def test_hochrechnung_solar(client, requests_mock):
    body="""Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2020-01-01;07:45;UTC;08:00;UTC;18,990;13,292;87,903;24,228"""

    requests_mock.get(f"{_API_BASE_URL}/data/hochrechnung/Solar/2020-01-01T00:00:00/2020-02-01T00:00:00", text=body)
    result = client.hochrechnung_solar(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 18.99

def test_hochrechnung_wind(client, requests_mock):
    body="""Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2020-01-01;00:00;UTC;00:15;UTC;99,070;53,000;25,600;9,778"""

    requests_mock.get(f"{_API_BASE_URL}/data/hochrechnung/Wind/2020-01-01T00:00:00/2020-02-01T00:00:00", text=body)
    result = client.hochrechnung_wind(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 99.07

def test_online_hochrechnung_windonshore(client, requests_mock):
    body="""Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2020-01-01;00:00;UTC;01:00;UTC;3573,990;1108,750;1165,210;130,408"""

    requests_mock.get(f"{_API_BASE_URL}/data/OnlineHochrechnung/Windonshore/2020-01-01T00:00:00/2020-02-01T00:00:00", text=body)
    result = client.online_hochrechnung_windonshore(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 3573.99

def test_online_hochrechnung_windoffshore(client, requests_mock):
    body="""Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2020-01-01;00:00;UTC;01:00;UTC;641,670;N.E.;526,230;N.E."""

    requests_mock.get(f"{_API_BASE_URL}/data/OnlineHochrechnung/Windoffshore/2020-01-01T00:00:00/2020-02-01T00:00:00", text=body)
    result = client.online_hochrechnung_windoffshore(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 641.67
    assert pd.isnull(result["TransnetBW (MW)"].iloc[0])

def test_online_hochrechnung_solar(client, requests_mock):
    body="""Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2020-01-01;08:00;UTC;09:00;UTC;727,210;514,160;1308,210;567,246"""

    requests_mock.get(f"{_API_BASE_URL}/data/OnlineHochrechnung/Solar/2020-01-01T00:00:00/2020-02-01T00:00:00", text=body)
    result = client.online_hochrechnung_solar(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 727.21