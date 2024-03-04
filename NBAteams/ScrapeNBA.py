import pandas as pd
from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
import time
import requests
from datetime import datetime
import urllib
import numpy as np


urlScores23 = 'https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&DateTo=&Direction=DESC&ISTRound=&LeagueID=00&PlayerOrTeam=T&Season=2023-24&SeasonType=Regular%20Season&Sorter=DATE'

headers  = {
    'Host': 'stats.nba.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-token': 'true',
    'X-NewRelic-ID': 'VQECWF5UChAHUlNTBwgBVw==',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

responseScores23 = requests.get(url=urlScores23,headers = headers).json()

scores23 = responseScores23['resultSets'][0]['rowSet']

columns_list_scores = [ "SEASON_ID",
    "TEAM_ID","TEAM_ABBREVIATION","TEAM_NAME","GAME_ID","GAME_DATE",
    "MATCHUP","WL","MIN","FGM","FGA","FG_PCT","FG3M","FG3A",
    "FG3_PCT", "FTM","FTA","FT_PCT","OREB","DREB","REB","AST",
    "STL","BLK","TOV", "PF", "PTS","PLUS_MINUS","VIDEO_AVAILABLE"
]
Scores2023_df = pd.DataFrame(scores23, columns = columns_list_scores)
columns_to_remove = ["SEASON_ID",
    "TEAM_ID","TEAM_ABBREVIATION","GAME_ID",
    "MATCHUP","MIN","FGM","FGA","FG_PCT","FG3M","FG3A",
    "FG3_PCT", "FTM","FTA","FT_PCT","OREB","DREB","REB","AST",
    "STL","BLK","TOV", "PF", "PTS","VIDEO_AVAILABLE"
]
Scores = Scores2023_df.drop(columns=columns_to_remove)
# Convert the "GAME_DATE" column to datetime format
Scores["GAME_DATE"] = pd.to_datetime(Scores["GAME_DATE"])

# Define the cutoff date
cutoff_date = pd.to_datetime("2024-02-17")

# Use boolean indexing to filter rows
FScores = Scores[Scores["GAME_DATE"] <= cutoff_date]
FScores.to_csv('AllScores.csv', index=False)
# We have now created a csv that contains all of the 


