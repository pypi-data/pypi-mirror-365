
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from fmscraper.match_stats import MatchStats
import time


LEAGUE_ID = 38
LEAGUE = "bundesliga"
SEASON = "2024-2025"


class MatchLinks:
    def __init__(self, league_id:int,league:str, season:str):
        self.base_url = "https://www.fotmob.com/leagues"
        self.league_id = str(league_id)
        self.league = league
        self.season = season
        self.final_url = ""
        # Setting up selenium driver
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)


    def _url_to_scrape(self):
        try:
            matches_url = "/".join([self.base_url, self.league_id,
                                    'matches',self.league])
            url_to_scrape = "?".join([matches_url, f"season={self.season}"])
            self.final_url = url_to_scrape
        except:
            return f"Please pick correct league's id or season (in format 20xx-20xx)"

    def _consent_fotmob(self):
        wait = WebDriverWait(self.driver, 5)
        consent_button = wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-button.fc-cta-consent.fc-primary-button"))
        )
        consent_button.click()
        
    def get_match_links(self,rounds):
        self._url_to_scrape()
        games_list = []
        self.driver.get(self.final_url)
        self._consent_fotmob()
        for i in range(rounds):
            round_i = self.final_url +f"&group=by-round&round={i}"
            self.driver.get(round_i)
            try:
                time.sleep(2)
                hrefs = [a.get_attribute("href") for a in
                         self.driver.find_elements(By.CSS_SELECTOR,
                                              "a.css-1ajdexg-MatchWrapper.e1mxmq6p0")]
                if not hrefs:
                    return "You have exceeded the number of rounds in the league"
                else:
                    games_list.extend(hrefs)
            except:
                print(f"Error: stale element reference for match {i}")
        self.driver.quit()
        return games_list


    def get_one_team_games(self,rounds,team_name):
        games_list = self.get_match_links(rounds=rounds)
        team_games = [game for game in games_list if team_name in game]
        return team_games


    def get_games_ids(self,rounds,team_or_all):
        if team_or_all == "all":
            games_list = self.get_match_links(rounds=rounds)
        else:
            assert team_or_all in MatchStats(league_id=LEAGUE_ID).get_available_teams(season=SEASON)
            games_list = self.get_one_team_games(rounds=rounds,team_name=team_or_all)
        games_ids = [game.split("#")[-1].replace("\n","") for game in games_list]
        return games_ids

    def write_to_file(self,file_name,to_write):
        with open(f"{file_name}.txt","w") as file:
            for thing in to_write:
                file.write(f'{thing}\n')