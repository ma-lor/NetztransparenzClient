from .context import ntclient

import os
import datetime as dt

START = dt.datetime(2024, 1, 1, 0, 0)
END = dt.datetime(2024, 2, 1, 0, 0)
def IntegrationTest():

    def __init__(self):
        id = os.environ.get("IPNT_CLIENT_ID")
        secret = os.environ.get("IPNT_CLIENT_SECRET")
        self.client = NetztransparenzClient(id, secret)
    
    def test_hochrechnung_solar(self):
        result = self.client.hochrechnung_solar(START, END, True)
        assert result["bis"].count() == 2976
    
    def test_hochrechnung_wind(self):
        result = self.client.hochrechnung_wind(START, END, True)
        assert result["bis"].count() == 2976




