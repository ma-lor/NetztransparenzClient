from .context import netztransparenz as nt

import os
import datetime as dt

START = dt.datetime(2024, 1, 1, 0, 0)
END = dt.datetime(2024, 2, 1, 0, 0)
def IntegrationTest():

    def __init__(self):
        id = os.environ.get("IPNT_CLIENT_ID")
        secret = os.environ.get("IPNT_CLIENT_SECRET")
        self.client = nt.NetztransparenzClient(id, secret)
    
    def test_hochrechnung_solar(self):
        result = self.client.hochrechnung_solar(START, END, True)
        assert result["bis"].count() == 2976
    
    def test_hochrechnung_wind(self):
        result = self.client.hochrechnung_wind(START, END, True)
        assert result["bis"].count() == 2976

    def test_online_hochrechnung_windonshore(self):
        result = self.client.online_hochrechnung_windonshore(START, END, True)
        assert result["bis"].count() == 2976

    def test_online_hochrechnung_windoffshore(self):
        result = self.client.online_hochrechnung_windoffshore(START, END, True)
        assert result["bis"].count() == 2976

    def test_online_hochrechnung_solar(self):
        result = self.client.online_hochrechnung_solar(START, END, True)
        assert result["bis"].count() == 2976

    def test_vermarktung_differenz_einspeiseprognose(self):
        result = self.client.vermarktung_differenz_einspeiseprognose(START, END, True)
        assert result["bis"].count() == 2976

    def test_vermarktung_inanspruchnahme_ausgleichsenergie(self):
        result = self.client.vermarktung_inanspruchnahme_ausgleichsenergie(START, END, True)
        assert result["bis"].count() == 2976

    def test_vermarktung_untertaegige_strommengen(self):
        result = self.client.vermarktung_untertaegige_strommengen(START, END, True)
        assert result["bis"].count() == 2976

    def test_prognose_solar(self):
        result = self.client.prognose_solar(START, END, True)
        assert result["bis"].count() == 2976

    def test_prognose_wind(self):
        result = self.client.prognose_wind(START, END, True)
        assert result["bis"].count() == 2976




