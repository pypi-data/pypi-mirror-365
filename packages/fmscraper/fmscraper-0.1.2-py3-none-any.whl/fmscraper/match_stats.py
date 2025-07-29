import requests
import json
from fmscraper.xmas_generator import generate_xmas_header


class MatchStats:
    def __init__(self,league_id):
        self.url = "https://www.fotmob.com/api"
        self.league_id = league_id
        self.matchdetails_url = self.url+f'/matchDetails?matchId='
        self.leagues_url = self.url+f'/leagues?id={self.league_id}'
        self.headers = {
            "x-mas": generate_xmas_header(self.matchdetails_url)
        }
        self.content_types = ['matchFacts','stats','playerStats',
                              'shotmap','lineup']

    def get_json_content(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data

    def get_match_details(self, match_id,content_type:str):
        data = self.get_json_content(url=self.matchdetails_url + str(match_id))
        assert content_type in self.content_types
        return data['content'][content_type]
    #TODO add option for different keys here, machfacts, stats, playerstats, shotmap, lineup

    def get_available_teams(self, season):
        season_formatted = season.replace("-", "%2F")
        data = self.get_json_content(url=self.leagues_url + f"&season={season_formatted}&tab=overview&type=league")
        try:
            teams = data['table'][0]['data']['table']['all']
        except KeyError as e:
            teams = data['table'][0]['data']['tables'][2]['table']['xg']
        teams_dict = {team['name'].lower(): {"name": team['name'].replace(" ", "-").lower(),
                                             "id": team['id']} for team in teams}
        return teams_dict


if __name__ == "__main__":
    klasa = MatchStats(league_id=38)
    print(klasa.get_match_details(4525341,"playerStats"))
    # print(klasa.get_match_details(match_id=4525341,content_type='playerStats'))
#['stats']['Periods']['All']['stats']