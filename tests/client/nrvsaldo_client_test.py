import datetime as dt
import pytest

import netztransparenz as nt

START = dt.datetime(2024, 1, 1, 0, 0, tzinfo=dt.UTC)
END = dt.datetime(2024, 2, 1, 0, 0)
_API_BASE_URL = "https://ds.netztransparenz.de/api/v1"


@pytest.fixture(autouse=True)
def token(requests_mock):
    requests_mock.post(
        "https://identity.netztransparenz.de/users/connect/token",
        json={"access_token": "placeholder_token"},
    )


@pytest.fixture
def client(token):
    id = "PLACEHOLDER_ID"
    secret = "PLACEHOLDER_SECRET"
    return nt.NrvSaldoClient(id, secret)

def test_basic_read_nrvsaldo(client, requests_mock):
    client.set_max_query_distance(dt.timedelta(days=1))
    body1 = """Datum;Zeitzone;von;bis;Data
10.10.2020;UTC;13:00;13:15;Test
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/NRVSaldo/Betrieblich/2025-01-01T00:00:00/2025-01-02T00:00:00",
        text=body1,
    )

    body2 = """Datum;Zeitzone;von;bis;Data
11.10.2020;UTC;13:00;13:15;Test2
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/NRVSaldo/Betrieblich/2025-01-02T00:00:00/2025-01-03T00:00:00",
        text=body2,
    )
    result = client._basic_read_nrvsaldo("NrvSaldo/NRVSaldo/Betrieblich", dt.datetime(2025, 1, 1, tzinfo=dt.UTC), dt.datetime(2025, 1, 3), True)
    assert result["Data"].iloc[0] == "Test"
    assert result["Data"].iloc[1] == "Test2"

def test_traffic_light(client, requests_mock):
    body = """[{"From":"2024-10-10T13:00:00Z","To":"2024-10-10T13:01:00Z","Value":"GREEN"},{"From":"2024-10-10T13:01:00Z","To":"2024-10-10T13:02:00Z","Value":"GREEN"}]"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/TrafficLight/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.traffic_light(START, END)
    assert result["Value"].iloc[0] == "GREEN"


def test_nrvsaldo_nrvsaldo_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland;AEP Knappheitskomponente;Mrl-Mol-Abweichung;Srl-Mol-Abweichung
10.10.2020;UTC;13:00;13:15;NRV-Saldo;Betrieblich;MW;-1142,535;N.A.;0;0
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/NRVSaldo/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_nrvsaldo_betrieblich(START, END, True)
    assert result["Deutschland"].iloc[0] == -1142.535


def test_nrvsaldo_nrvsaldo_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland
10.10.2020;UTC;13:00;13:15;NRV-Saldo;Qualitätsgesichert;MW;-1143,048
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/NRVSaldo/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_nrvsaldo_qualitaetsgesichert(START, END, True)
    assert result["Deutschland"].iloc[0] == -1143.048


def test_nrvsaldo_rzsaldo_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz;Amprion;TenneT TSO;TransnetBW
10.10.2020;UTC;13:00;13:15;RZ-Saldo;Betrieblich;MW;-422,000;668,426;-1664,563;275,602
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/RZSaldo/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_rzsaldo_betrieblich(START, END, True)
    assert result["50Hertz"].iloc[0] == -422


def test_nrvsaldo_rzsaldo_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz;Amprion;TenneT TSO;TransnetBW
10.10.2020;UTC;13:00;13:15;RZ-Saldo;Qualitätsgesichert;MW;-422,188;668,390;-1665,968;276,208
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/RZSaldo/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_rzsaldo_qualitaetsgesichert(START, END, True)
    assert result["50Hertz"].iloc[0] == -422.188


def test_nrvsaldo_prl_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2023;UTC;13:00;13:15;PRL;Betrieblich;MW;9,436;10,765;8,727;2,048;30,976;18,755;14,819;12,761;2,933;49,268
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/PRL/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_prl_betrieblich(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 9.436


def test_nrvsaldo_prl_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2023;UTC;13:00;13:15;PRL;Qualitätsgesichert;MW;0,000;0,000;0,000;0,000;0,000;5,180;4,880;4,136;0,996;15,192
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/PRL/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_prl_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_aktivierte_srl_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ);MOL-Abweichung
10.10.2020;UTC;13:00;13:15;Aktivierte SRL;Betrieblich;MW;0,000;0,000;0,000;0,000;0,000;133,135;148,796;91,563;565,170;938,664;0
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AktivierteSRL/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_aktivierte_srl_betrieblich(START, END, True)
    assert result["50Hertz (Negativ)"].iloc[0] == 133.135


def test_nrvsaldo_aktivierte_srl_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2020;UTC;13:00;13:15;Aktivierte SRL;Qualitätsgesichert;MW;0,000;0,864;0,012;1,588;2,464;133,240;149,696;92,792;566,196;941,924
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AktivierteSRL/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_aktivierte_srl_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_aktivierte_mrl_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ);MOL-Abweichung
10.10.2020;UTC;17:15;17:30;Aktivierte MRL;Betrieblich;MW;0,000;0,000;0,000;0,000;0,000;0,000;10,000;5,000;29,000;44,000;0
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AktivierteMRL/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_aktivierte_mrl_betrieblich(START, END, True)
    assert result["Deutschland (Negativ)"].iloc[0] == 44


def test_nrvsaldo_aktivierte_mrl_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2020;UTC;17:15;17:30;Aktivierte MRL;Qualitätsgesichert;MW;0,000;0,000;0,000;0,000;0,000;0,000;10,000;5,000;29,000;44,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AktivierteMRL/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_aktivierte_mrl_qualitaetsgesichert(START, END, True)
    assert result["Deutschland (Negativ)"].iloc[0] == 44


def test_nrvsaldo_srl_optimierung_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;SRL Optimierung;Betrieblich;MW;122,745;997,173;0,000;0,389;1120,307;2,664;0,000;612,909;324,374;939,947
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/SRLOptimierung/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_srl_optimierung_betrieblich(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 122.745


def test_nrvsaldo_srl_optimierung_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;SRL Optimierung;Qualitätsgesichert;MW;124,308;997,072;1,680;0,000;1123,060;4,224;0,000;614,592;323,836;942,652
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/SRLOptimierung/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_srl_optimierung_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 124.308


def test_nrvsaldo_mrl_optimierung_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;MRL Optimierung;Betrieblich;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/MRLOptimierung/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_mrl_optimierung_betrieblich(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_mrl_optimierung_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;MRL Optimierung;Qualitätsgesichert;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/MRLOptimierung/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_mrl_optimierung_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_mrl__mol_abweichung_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Netzengpass;Technische Störung Abrufsystem;Technische Störung Anbieter;Test Aktivierung
10.10.2024;UTC;13:00;13:15;MRL MOL Abweichung;Betrieblich;0;0;0;0
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/MrlMolAbweichungen/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_mrl_mol_abweichungen_betrieblich(START, END, True)
    assert result["Netzengpass"].iloc[0] == 0


def test_nrvsaldo_srl_mol_abweichungen_betrieblich(client, requests_mock):
    body = """Datum von;Zeitzone von;Uhrzeit von;Datum bis;Zeitzone bis;Uhrzeit bis;Datenkategorie;Datentyp;Abruf-ÜNB;Störung in der MOL-Verarbeitung;Trennung von SRL-Kooperation;Sonstiges
02.01.2025;UTC;19:00;02.01.2025;UTC;19:45;SRL MOL Abweichung;Betrieblich;TransnetBW GmbH;;;1
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/SrlMolAbweichungen/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_srl_mol_abweichungen_betrieblich(START, END, True)
    assert result["Sonstiges"].iloc[0] == 1


def test_nrvsaldo_difference_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;Difference;Betrieblich;MW;28,209;0,000;0,000;77,035;105,244;42,466;7,449;14,924;1,042;65,881
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/Difference/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_difference_betrieblich(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 28.209


def test_nrvsaldo_difference_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;Difference;Qualitätsgesichert;MW;7,116;0,000;36,268;66,800;110,184;22,004;3,160;16,872;0,000;42,036
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/Difference/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_difference_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 7.116


def test_nrvsaldo_abschaltbare_lasten_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland (Positiv);50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv)
10.10.2024;UTC;13:00;13:15;Abschaltbare Lasten;Betrieblich;MW;N.A.;0,000;0,000;0,000;N.A.
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AbschaltbareLasten/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_abschaltbare_lasten_betrieblich(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_abschaltbare_lasten_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;Deutschland (Positiv);50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv)
10.10.2024;UTC;13:00;13:15;Abschaltbare Lasten;Qualitätsgesichert;MW;N.A.;0,000;0,000;0,000;N.A.
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AbschaltbareLasten/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_abschaltbare_lasten_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_zusatzmassnahmen_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;Zusatzmassnahmen;Betrieblich;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/Zusatzmassnahmen/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_zusatzmassnahmen_betrieblich(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_zusatzmassnahmen_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;Zusatzmassnahmen;Qualitätsgesichert;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/Zusatzmassnahmen/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_zusatzmassnahmen_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_nothilfe_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2025;UTC;13:00;13:15;Nothilfe;Betrieblich;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/Nothilfe/Betrieblich/2025-06-01T00:00:00/2025-07-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_nothilfe_betrieblich(dt.datetime(2025, 6, 1), dt.datetime(2025, 7, 1), True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_nothilfe_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;50Hertz (Positiv);Amprion (Positiv);TenneT TSO (Positiv);TransnetBW (Positiv);Deutschland (Positiv);50Hertz (Negativ);Amprion (Negativ);TenneT TSO (Negativ);TransnetBW (Negativ);Deutschland (Negativ)
10.10.2024;UTC;13:00;13:15;Nothilfe;Qualitätsgesichert;MW;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000;0,000
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/Nothilfe/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_nothilfe_qualitaetsgesichert(START, END, True)
    assert result["50Hertz (Positiv)"].iloc[0] == 0


def test_nrvsaldo_rebap_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;reBAP unterdeckt;reBAP ueberdeckt
10.01.2025;UTC;13:00;13:15;reBAP;Qualitätsgesichert;EUR/MWh;63,26;63,26
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/reBAP/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_rebap_qualitaetsgesichert(START, END, True)
    assert result["reBAP unterdeckt"].iloc[0] == 63.26


def test_nrvsaldo_aep_module_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;AEP Modul 1;AEP Modul 2;AEP Modul 3
10.10.2024;UTC;13:00;13:15;AEP Module;Qualitätsgesichert;EUR/MWh;25,81;2,29;N.E.
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AEPModule/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_aep_module_qualitaetsgesichert(START, END, True)
    assert result["AEP Modul 1"].iloc[0] == 25.81


def test_nrvsaldo_aep_schaetzer_betrieblich(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;AEP-Schätzer;Status
10.10.2024;UTC;13:00;13:15;AEP-Schätzer;Betrieblich;EUR/MWh;25,72;0,00
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/AepSchaetzer/Betrieblich/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_aep_schaetzer_betrieblich(START, END, True)
    assert result["AEP-Schätzer"].iloc[0] == 25.72


def test_nrvsaldo_finanzielle_wirkung_aep_module_qualitaetsgesichert(
    client, requests_mock
):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;AEP Modul 1;AEP Modul 2;AEP Modul 3
10.10.2024;UTC;13:00;13:15;Finanzielle Wirkung AEP Module;Qualitätsgesichert;EUR;-2296,07;0,00;0,00
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/FinanzielleWirkungAEPModule/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_finanzielle_wirkung_aep_module_qualitaetsgesichert(
        START, END, True
    )
    assert result["AEP Modul 1"].iloc[0] == -2296.07


def test_nrvsaldo_voaa_qualitaetsgesichert(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;Datenkategorie;Datentyp;Einheit;VoAA (Positiv);VoAA (Negativ)
10.10.2024;UTC;13:00;13:15;VoAA;Qualitätsgesichert;EUR/MWh;21,69;23,14
"""
    requests_mock.get(
        f"{_API_BASE_URL}/data/NrvSaldo/VoAA/Qualitaetsgesichert/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.nrvsaldo_voaa_qualitaetsgesichert(START, END, True)
    assert result["VoAA (Positiv)"].iloc[0] == 21.69
