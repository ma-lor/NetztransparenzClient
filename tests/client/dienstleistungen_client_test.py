import datetime as dt
import pandas as pd
import pytest

import netztransparenz as nt

START = dt.datetime(2024, 1, 1, 0, 0)
END = dt.datetime(2024, 2, 1, 0, 0)
_API_BASE_URL = "https://ds.netztransparenz.de/api/v1"

@pytest.fixture(autouse=True)
def token(requests_mock):
    requests_mock.post("https://identity.netztransparenz.de/users/connect/token", json= {"access_token": "placeholder_token"})

@pytest.fixture
def client(token):
    id = "PLACEHOLDER_ID"
    secret = "PLACEHOLDER_SECRET"
    return nt.DienstleistungenClient(id, secret)

def test_redispatch(client, requests_mock):
    body="""BEGINN_DATUM;BEGINN_UHRZEIT;ZEITZONE_VON;ENDE_DATUM;ENDE_UHRZEIT;ZEITZONE_BIS;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART
31.12.2024;23:00;UTC;01.01.2025;05:00;UTC;Strombedingter Redispatch;Wirkleistungseinspeisung reduzieren;41;56;166;50Hertz;50Hertz & Amprion & TenneT DE & TransnetBW;50H UW Putlitz;Erneuerbar
"""

    requests_mock.get(f"{_API_BASE_URL}/data/redispatch/2024-01-01T00:00:00/2024-02-01T00:00:00", text=body)
    result = client.redispatch(START, END, True)
    assert result["MITTLERE_LEISTUNG_MW"].iloc[0] == 41
    assert result["BEGINN"].iloc[0] == pd.Timestamp(2024, 12, 31, 23, 0)

def test_kapazitaetsreserve(client, requests_mock):
    #uses data from redispatch, since there is no data as of writing
    body="""BEGINN_DATUM;BEGINN_UHRZEIT;ZEITZONE_VON;ENDE_DATUM;ENDE_UHRZEIT;ZEITZONE_BIS;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART
31.12.2024;23:00;UTC;01.01.2025;05:00;UTC;Strombedingter Redispatch;Wirkleistungseinspeisung reduzieren;41;56;166;50Hertz;50Hertz & Amprion & TenneT DE & TransnetBW;50H UW Putlitz;Erneuerbar
"""

    requests_mock.get(f"{_API_BASE_URL}/data/Kapazitaetsreserve/2024-01-01T00:00:00/2024-02-01T00:00:00", text=body)
    result = client.kapazitaetsreserve(START, END, True)
    assert result["MITTLERE_LEISTUNG_MW"].iloc[0] == 41
    assert result["BEGINN"].iloc[0] == pd.Timestamp(2024, 12, 31, 23, 0)

def test_vorhaltung_krd(client, requests_mock):
    #uses data from redispatch, since there is no data as of writing
    body="""BEGINN_DATUM;BEGINN_UHRZEIT;ZEITZONE_VON;ENDE_DATUM;ENDE_UHRZEIT;ZEITZONE_BIS;GRUND_DER_MASSNAHME;RICHTUNG;MITTLERE_LEISTUNG_MW;MAXIMALE_LEISTUNG_MW;GESAMTE_ARBEIT_MWH;ANWEISENDER_UENB;ANFORDERNDER_UENB;BETROFFENE_ANLAGE;PRIMAERENERGIEART
31.12.2024;23:00;UTC;01.01.2025;05:00;UTC;Strombedingter Redispatch;Wirkleistungseinspeisung reduzieren;41;56;166;50Hertz;50Hertz & Amprion & TenneT DE & TransnetBW;50H UW Putlitz;Erneuerbar
"""

    requests_mock.get(f"{_API_BASE_URL}/data/VorhaltungkRD/2024-01-01T00:00:00/2024-02-01T00:00:00", text=body)
    result = client.vorhaltung_krd(START, END, True)
    assert result["MITTLERE_LEISTUNG_MW"].iloc[0] == 41
    assert result["BEGINN"].iloc[0] == pd.Timestamp(2024, 12, 31, 23, 0)

def test_ausgewiesene_absm(client, requests_mock):
    body="""Datum;Zeitzone;von;bis;Datenkategorie;Einheit;H1;H2;T1;T2;T3;T4;T5;T6
30.09.2024;UTC;22:00;22:15;ausgewiesene Abregelungsstrommenge;MW;139,160;185,840;0,000;804,650;295,400;321,360;284,000;101,000
"""
    requests_mock.get(f"{_API_BASE_URL}/data/AusgewieseneABSM/2024-10-01T00:00:00/2024-11-01T00:00:00", text=body)
    result = client.ausgewiesene_absm(dt.datetime(2024, 10, 1), dt.datetime(2024, 11, 1), True)
    assert result["H1"].iloc[0] == 139.16
    assert result["von"].iloc[0] == pd.Timestamp(2024, 9, 30, 22, 0)

def test_zugeteilte_absm(client, requests_mock):
    body="""Datum;Zeitzone;von;bis;Datenkategorie;Einheit;H1;H2;T1;T2;T3;T4;T5;T6
19.01.2025;UTC;13:00;13:15;zugeteilte Abregelungsstrommenge;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000"""

    requests_mock.get(f"{_API_BASE_URL}/data/ZugeteilteABSM/2024-10-01T00:00:00/2024-11-01T00:00:00", text=body)
    result = client.zugeteilte_absm(dt.datetime(2024, 10, 1), dt.datetime(2024, 11, 1), True)
    assert result["H1"].iloc[0] == 0
    assert result["von"].iloc[0] == pd.Timestamp(2025, 1, 19, 13, 0)

def test_erzeugungsverbot(client, requests_mock):
    body="""Datum;Zeitzone;von;bis;Datenkategorie;H1;H2;T1;T2;T3;T4;T5;T6
19.01.2025;UTC;13:00;13:15;Erzeugungsverbot;0;0;0;0;0;0;0;0"""

    requests_mock.get(f"{_API_BASE_URL}/data/AusgewieseneABSM/2024-10-01T00:00:00/2024-11-01T00:00:00", text=body)
    result = client.ausgewiesene_absm(dt.datetime(2024, 10, 1), dt.datetime(2024, 11, 1), True)
    assert result["H1"].iloc[0] == 0
    assert result["von"].iloc[0] == pd.Timestamp(2025, 1, 19, 13, 0)