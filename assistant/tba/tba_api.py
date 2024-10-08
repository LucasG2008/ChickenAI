import requests
import datetime as dt
from typing import Dict

class TheBlueAllianceAPI:

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.thebluealliance.com/api/v3"

    def request(self, endpoint: str, params: Dict = None) -> Dict:
        headers = {
            "X-TBA-Auth-Key": self.api_key
        }
        request_url = self.base_url + endpoint
        response = requests.get(request_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    # ---------------- TEAM ENDPOINTS ---------------- #

    def get_team_info(self, team_number: int) -> Dict:
        endpoint = f"/team/frc{team_number}"
        return self.request(endpoint)
    
    def get_team_events(self, team_number: int, year: int) -> Dict:

        endpoint = f"/team/frc{team_number}/events/{year}"
        return self.request(endpoint)
    
    def get_team_awards(self, team_number: int, year: int = None) -> Dict:

        if year is None:
            endpoint = f"/team/frc{team_number}/awards"
        else:
            endpoint = f"/team/frc{team_number}/awards/{year}"

        return self.request(endpoint)
    
    def get_team_matches(self, team_number: int, year: int = None) -> Dict:

        if year is None:
            year = dt.datetime.now().year

        endpoint = f"/team/frc{team_number}/matches/{year}/simple"
        return self.request(endpoint)
    
    # ---------------- EVENT ENDPOINTS ---------------- #

    def get_events_in_year(self, year: int) -> Dict:
        endpoint = f"/events/{year}/simple"
        return self.request(endpoint)
    
    # --------------- DISTRICT ENDPOINTS -------------- #

    def get_district_rankings(self, district_code: str) -> Dict:
        endpoint = f"/district/{district_code}/rankings"
        return self.request(endpoint)