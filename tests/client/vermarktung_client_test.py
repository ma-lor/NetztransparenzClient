import datetime as dt
import pandas as pd
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
    return nt.VermarktungClient(id, secret)


def test_vermarktung_differenz_einspeiseprognose(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2024-01-01;22:00;UTC;22:15;UTC;N.A.;N.A.;-2,800;-13,000"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/DifferenzEinspeiseprognose/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_differenz_einspeiseprognose(START, END, True)
    assert pd.isnull(result["50Hertz (MW)"].iloc[0])
    assert result["TransnetBW (MW)"].iloc[0] == -13


def test_vermarktung_inanspruchnahme_ausgleichsenergie(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (kWh);Amprion (kWh);TenneT TSO (kWh);TransnetBW (kWh)
2024-01-01;22:00;UTC;22:15;UTC;-10110,672;60947,210;-49345,798;N.A."""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/InanspruchnahmeAusgleichsenergie/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_inanspruchnahme_ausgleichsenergie(START, END, True)
    assert result["50Hertz (kWh)"].iloc[0] == -10110.672
    assert pd.isnull(result["TransnetBW (kWh)"].iloc[0])


def test_vermarktung_untertaegige_strommengen(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2011-03-31;22:00;UTC;22:15;UTC;-156,000;0,000;165,000;90,000"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/UntertaegigeStrommengen/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_untertaegige_strommengen(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == -156


def test_vermarktung_epex(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2024-01-01;00:00;UTC;00:15;UTC;0,000;0,000;-1,000;-1,200"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/VermarktungEpex/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_epex(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 0
    assert result["TransnetBW (MW)"].iloc[0] == -1.2


def test_vermarktung_exaa(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2011-12-31;23:00;UTC;23:15;UTC;N.A.;0,000;N.A.;0,000"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/VermarktungExaa/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_exaa(START, END, True)
    assert pd.isnull(result["50Hertz (MW)"].iloc[0])
    assert result["TransnetBW (MW)"].iloc[0] == 0


def test_vermarktung_solar(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2013-12-31;23:00;UTC;23:15;UTC;0,000;0,000;0,000;0,000"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/VermarktungsSolar/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_solar(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 0


def test_vermarktung_wind(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2013-12-31;23:00;UTC;23:15;UTC;267,900;437,080;402,380;184,000"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/VermarktungsWind/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_wind(START, END, True)
    assert result["50Hertz (MW)"].iloc[0] == 267.9


def test_vermarktung_sonstige(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;50Hertz (MW);Amprion (MW);TenneT TSO (MW);TransnetBW (MW)
2013-12-31;23:00;UTC;23:15;UTC;N.A.;54,672;123,038;39,400"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/vermarktung/VermarktungsSonstige/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.vermarktung_sonstige(START, END, True)
    assert pd.isnull(result["50Hertz (MW)"].iloc[0])
    assert result["TransnetBW (MW)"].iloc[0] == 39.4


def test_spotmarktpreise(client, requests_mock):
    body = """Datum;von;Zeitzone von;bis;Zeitzone bis;Spotmarktpreis in ct/kWh
31.12.2024;23:00;UTC;00:00;UTC;5,087"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/Spotmarktpreise/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.spotmarktpreise(START, END, True)
    assert result["Spotmarktpreis in ct/kWh"].iloc[0] == 5.087


def test_negative_preise(client, requests_mock):
    body = """Datum;Stunde1;Stunde3;Stunde4;Stunde6
2024-10-10 13:00;1;N.A.;N.A.;1
2024-10-10 14:00;1;N.A.;N.A.;1"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.negative_preise(START, END, True)
    assert result["Stunde1"].iloc[0] == 1
    assert result["Datum"].iloc[0] == pd.Timestamp(2024, 10, 10, 13, 0)


def test_negative_preise_1h(client, requests_mock):
    body = """Datum;Negativ
2024-01-01 00:00;Ja
2024-01-01 01:00;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/1/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.negative_preise_1h(START, END, True)
    assert result["Negativ"].iloc[0] == "Ja"
    assert result["Datum"].iloc[0] == pd.Timestamp(2024, 1, 1, 0, 0)


def test_negative_preise_2h(client, requests_mock):
    body = """Datum;Negativ
2026-01-01 00:00;Ja
2026-01-01 01:00;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/2/2026-01-01T00:00:00/2026-02-01T00:00:00",
        text=body,
    )
    result = client.negative_preise_2h(
        dt.datetime(2026, 1, 1, tzinfo=dt.UTC), dt.datetime(2026, 2, 1), True
    )
    assert result["Negativ"].iloc[1] == "Nein"
    assert result["Datum"].iloc[0] == pd.Timestamp(2026, 1, 1, 0, 0)


def test_negative_preise_3h(client, requests_mock):
    body = """Datum;Negativ
2024-01-01 00:00;Ja
2024-01-01 01:00;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/3/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.negative_preise_3h(START, END, True)
    assert result["Negativ"].iloc[0] == "Ja"
    assert result["Datum"].iloc[0] == pd.Timestamp(2024, 1, 1, 0, 0)


def test_negative_preise_4h(client, requests_mock):
    body = """Datum;Negativ
2024-01-01 00:00;Ja
2024-01-01 01:00;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/4/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.negative_preise_4h(START, END, True)
    assert result["Negativ"].iloc[0] == "Ja"
    assert result["Datum"].iloc[0] == pd.Timestamp(2024, 1, 1, 0, 0)


def test_negative_preise_6h(client, requests_mock):
    body = """Datum;Negativ
2024-01-01 00:00;Ja
2024-01-01 01:00;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/6/2024-01-01T00:00:00/2024-02-01T00:00:00",
        text=body,
    )
    result = client.negative_preise_6h(START, END, True)
    assert result["Negativ"].iloc[0] == "Ja"
    assert result["Datum"].iloc[0] == pd.Timestamp(2024, 1, 1, 0, 0)


def test_negative_preise_15m(client, requests_mock):
    body = """Datum;Negativ
2025-10-01 00:00;Ja
2025-10-01 00:15;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/NegativePreise/15/2025-10-01T00:00:00/2025-11-01T00:00:00",
        text=body,
    )
    result = client.negative_preise_15m(
        dt.datetime(2025, 10, 1, tzinfo=dt.UTC), dt.datetime(2025, 11, 1), True
    )
    assert result["Negativ"].iloc[0] == "Ja"
    assert result["Datum"].iloc[0] == pd.Timestamp(2025, 10, 1, 0, 0)


def test_negative_preise_before_first_data(client):
    client.set_strict(False)
    result = client.negative_preise_15m(START, END, True)
    assert result.empty
    assert list(result.columns) == ["Datum", "Negativ"]


def test_jahresmarktpraemie(client, requests_mock):
    body = """Alle Werte in ct/kWh;2024;2021;2022;2023;2024
JW;3,047;9,685;23,545;9,518;7,946
JW Wind an Land;2,384;7,854;16,272;7,621;6,293
JW Wind auf See;2,684;9,017;18,349;8,187;6,777
JW Solar;2,458;7,552;22,306;7,2;4,624
"""

    requests_mock.get(f"{_API_BASE_URL}/data/Jahresmarktpraemie/", text=body)
    result = client.jahresmarktpraemie()
    assert result["2024"].iloc[0] == 3.047


def test_jahresmarktpraemie_with_year(client, requests_mock):
    body = """Alle Werte in ct/kWh;2023
JW;9,518
JW Wind an Land;7,621
JW Wind auf See;8,187
JW Solar;7,2
"""

    requests_mock.get(f"{_API_BASE_URL}/data/Jahresmarktpraemie/2023", text=body)
    result = client.jahresmarktpraemie(2023)
    assert result["2023"].iloc[0] == 9.518


def test_jahresmarktpraemie_transposed(client, requests_mock):
    body = """Alle Werte in ct/kWh;2024;2021;2022;2023;2024
JW;3,047;9,685;23,545;9,518;7,946
JW Wind an Land;2,384;7,854;16,272;7,621;6,293
JW Wind auf See;2,684;9,017;18,349;8,187;6,777
JW Solar;2,458;7,552;22,306;7,2;4,624
"""

    requests_mock.get(f"{_API_BASE_URL}/data/Jahresmarktpraemie/", text=body)
    result = client.jahresmarktpraemie(transpose=True)
    assert result["JW"].iloc[0] == 3.047


def test_marktpraemie(client, requests_mock):
    body = """Monat;MW-EPEX in ct/kWh;MW Wind Onshore in ct/kWh;PM Wind Onshore fernsteuerbar in ct/kWh;MW Wind Offshore in ct/kWh;PM Wind Offshore fernsteuerbar in ct/kWh;MW Solar in ct/kWh;PM Solar fernsteuerbar in ct/kWh;MW steuerbar in ct/kWh;PM steuerbar in ct/kWh;Negative Stunden (6H);Negative Stunden (4H);Negative Stunden (3H);Negative Stunden (1H);Negative Stunden (15MIN)
1/2025;11,414;8,506;;9,702;;11,511;;11,414;;Ja;Ja;Ja;Ja;
"""
    requests_mock.get(f"{_API_BASE_URL}/data/marktpraemie/1/2025/1/2025", text=body)
    result = client.marktpraemie(dt.date(2025, 1, 1), dt.date(2025, 1, 1))
    assert result["MW-EPEX in ct/kWh"].iloc[0] == 11.414


def test_id_aep(client, requests_mock):
    body = """Datum von;(Uhrzeit) von;Zeitzone;(Uhrzeit) bis;Zeitzone;ID AEP in €/MWh
2025-01-01;23:45;UTC;00:00;UTC;-7,940"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/IdAep/2024-01-01T00:00:00/2024-02-01T00:00:00", text=body
    )
    result = client.id_aep(START, END, transform_dates=True)
    assert result["ID AEP in €/MWh"].iloc[0] == -7.94
    assert result["bis"].iloc[0] == pd.Timestamp(
        2025, 1, 2, 0, 0, tz="UTC"
    )  # check if day turnover works correctly


def test_anspruch_verguetung_eeg(client, requests_mock):
    body = """Datum;Zeitzone;von;bis;AnspruchVerguetung
31.12.2025;UTC;23:00;00:00;Ja
01.01.2026;UTC;00:00;01:00;Nein"""

    requests_mock.get(
        f"{_API_BASE_URL}/data/anspruchverguetungeeg/2hour/2025-12-31T23:00:00/2026-01-01T01:00:00",
        text=body,
    )
    result = client.anspruch_verguetung_eeg(
        dt.datetime(2025, 12, 31, 23), dt.datetime(2026, 1, 1, 1), True, "2hour"
    )
    assert list(result["AnspruchVerguetung"]) == ["Ja", "Nein"]
    assert result.index[0] == pd.Timestamp(2025, 12, 31, 23, tz="UTC")
    # 00:00 as the end of a period is the next day
    assert result["bis"].iloc[0] == pd.Timestamp(2026, 1, 1, 0, tz="UTC")


def test_anspruch_verguetung_kwkg_splits_long_ranges(client, requests_mock):
    client.set_max_query_distance(dt.timedelta(days=1))
    for day, answer in ((1, "Ja"), (2, "Nein")):
        requests_mock.get(
            f"{_API_BASE_URL}/data/anspruchverguetungkwkg/1hour/2024-01-0{day}T00:00:00/2024-01-0{day + 1}T00:00:00",
            text=f"""Datum;Zeitzone;von;bis;AnspruchVerguetung
0{day}.01.2024;UTC;00:00;01:00;{answer}""",
        )
    result = client.anspruch_verguetung_kwkg(
        dt.datetime(2024, 1, 1), dt.datetime(2024, 1, 3), True
    )
    assert list(result["AnspruchVerguetung"]) == ["Ja", "Nein"]


def test_anspruch_verguetung_unknown_logic(client):
    with pytest.raises(ValueError):
        client.anspruch_verguetung_kwkg(START, END, logic="2hour")


def test_spotmarktpreise_splits_long_ranges(client, requests_mock):
    client.set_max_query_distance(dt.timedelta(days=1))
    for day in (1, 2):
        requests_mock.get(
            f"{_API_BASE_URL}/data/Spotmarktpreise/2024-01-0{day}T00:00:00/2024-01-0{day + 1}T00:00:00",
            text=f"""Datum;von;Zeitzone von;bis;Zeitzone bis;Spotmarktpreis in ct/kWh
0{day}.01.2024;00:00;UTC;01:00;UTC;7,7""",
        )
    result = client.spotmarktpreise(
        dt.datetime(2024, 1, 1, tzinfo=dt.UTC), dt.datetime(2024, 1, 3), True
    )
    assert list(result.index) == [
        pd.Timestamp(2024, 1, 1, tz="UTC"),
        pd.Timestamp(2024, 1, 2, tz="UTC"),
    ]
