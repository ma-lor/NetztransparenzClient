import pytest
import datetime as dt
import pandas as pd
import netztransparenz as nt

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
    return nt.DienstleistungenClient(id, secret)

def test_check_preconditions_strict(client):
    client.set_strict(True)
    assert client._check_preconditions(dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))
    with pytest.raises(ValueError):
        client._check_preconditions(dt.datetime(2000, 1, 1), dt.datetime(2002, 1, 1), dt.datetime(2001, 1, 1))
    with pytest.raises(ValueError):
        client._check_preconditions(dt.datetime(2002, 1, 1), dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))
    with pytest.raises(ValueError):
        client._check_preconditions(dt.datetime(2001, 1, 1), dt.datetime(2000, 1, 1), None)
    with pytest.raises(ValueError):
        client._check_preconditions(None, dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))
    
def test_check_preconditions_not_strict(client):
    client.set_strict(False)
    assert client._check_preconditions(dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))
    assert not client._check_preconditions(dt.datetime(2000, 1, 1), dt.datetime(2002, 1, 1), dt.datetime(2001, 1, 1))
    assert not client._check_preconditions(dt.datetime(2002, 1, 1), dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))
    assert not client._check_preconditions(dt.datetime(2001, 1, 1), dt.datetime(2000, 1, 1), None)
    assert not client._check_preconditions(None, dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))

def test_return_empty_frame(client):
    result = client._return_empty_frame("/Spotmarktpreise", False)
    expected_result = pd.DataFrame(columns=['Datum', 'von', 'Zeitzone von', 'bis', 'Zeitzone bis', 'Spotmarktpreis in ct/kWh']) #type: ignore
    assert expected_result.equals(result)

    result = client._return_empty_frame("/Spotmarktpreise", True)
    expected_result = pd.DataFrame(columns=['von', 'bis', 'Spotmarktpreis in ct/kWh']) #type: ignore
    assert expected_result.equals(result)

def test_split_timeframe(client):
    client.set_max_query_distance(dt.timedelta(days=365))
    result = client._split_timeframe(dt.datetime(2001, 1, 1), dt.datetime(2003, 1 ,1))
    assert result[0][1] == dt.datetime(2002, 1, 1)
    assert result[1][0] == dt.datetime(2002, 1, 1)
    assert result[1][1] == dt.datetime(2003, 1, 1)
    assert len(result) == 2

    result = client._split_timeframe(dt.datetime(2001, 1, 1), dt.datetime(2002, 6 ,19))
    assert result[1][1] == dt.datetime(2002, 6, 19)