import requests
import urllib
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

BASE_URL = 'https://api.prop-odds.com'
API_KEY = 'dUGoVymuEFB7b1pigNlG6xUkCsAXFpZV21w'


def get_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    print('Request failed with status:', response.status_code)
    return {}


def get_nba_games(date):
    query_params = {
        'date': date.strftime('%Y-%m-%d'),
        'tz': 'America/New_York',
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/games/nba?' + params
    return get_request(url)


def get_game_info(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/game/' + game_id + '?' + params
    return get_request(url)


def get_markets(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/markets/' + game_id + '?' + params
    return get_request(url)


def get_most_recent_odds(game_id, market, end_datetime):
    query_params = {
        'api_key': API_KEY,
        'end_datetime': end_datetime
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/odds/' + game_id + '/' + market + '?' + params
    return get_request(url)


def main():
    start_date = datetime(2023, 10, 24)
    end_date = datetime(2024, 2, 15)
    gamecount = 0
    daycount = 0
    current_date = start_date
    complete_df_list = []
    # games = get_nfl_games(current_date)
    # game = games['games'][0]
    # game_id = game['game_id']
    # start_time_str = game['start_timestamp']
    # start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
    # duration = timedelta(hours=1.5)
    # new_time = start_time + duration
    # odds = get_most_recent_odds(game_id, 'moneyline', start_time_str)
    # barstool_outcomes = [outcome for sportsbook in odds['sportsbooks'] if sportsbook['bookie_key'] == 
    #                                      'barstool' for outcome in sportsbook['market']['outcomes']]
    # result_df = pd.DataFrame(barstool_outcomes)
    # pd.set_option('display.max_rows', None)
    # print(result_df)
    # odds = get_most_recent_odds(game_id, 'moneyline', new_time)
    # barstool_outcomes = [outcome for sportsbook in odds['sportsbooks'] if sportsbook['bookie_key'] == 
    #                                      'barstool' for outcome in sportsbook['market']['outcomes']]
    # result_df = pd.DataFrame(barstool_outcomes)
    # result_df['timestamp'] = pd.to_datetime(result_df['timestamp'])
    # result_df = result_df[result_df['timestamp'] > (new_time - duration - duration)]
    # print(result_df)
    while current_date <= end_date:
        games = get_nba_games(current_date)
        if not games['games']:
            print(f"No games available for {current_date}")
            current_date += timedelta(days=1)
            continue
        final_df_list = []
        for game in games['games']:
            game_id = game['game_id']

            duration = timedelta(hours=1.25)
            start_time_str = game['start_timestamp']
            new_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
            #markets = ["spread", "total_over_under"]
            markets = ["moneyline"]
            team_df = pd.DataFrame({
            'AwayTeam': game['away_team'],
            'HomeTeam': game['home_team']
            }, index=[0])
            team_abbreviations = {
                'Atlanta Hawks': 'ATL',
                'Boston Celtics': 'BOS',
                'Brooklyn Nets': 'BKN',
                'Charlotte Hornets': 'CHA',
                'Chicago Bulls': 'CHI',
                'Cleveland Cavaliers': 'CLE',
                'Dallas Mavericks': 'DAL',
                'Denver Nuggets': 'DEN',
                'Detroit Pistons': 'DET',
                'Golden State Warriors': 'GSW',
                'Houston Rockets': 'HOU',
                'Indiana Pacers': 'IND',
                'LA Clippers': 'LAC',
                'Los Angeles Lakers': 'LAL',
                'Memphis Grizzlies': 'MEM',
                'Miami Heat': 'MIA',
                'Milwaukee Bucks': 'MIL',
                'Minnesota Timberwolves': 'MIN',
                'New Orleans Pelicans': 'NOP',
                'New York Knicks': 'NYK',
                'Oklahoma City Thunder': 'OKC',
                'Orlando Magic': 'ORL',
                'Philadelphia 76ers': 'PHI',
                'Phoenix Suns': 'PHX',
                'Portland Trail Blazers': 'POR',
                'Sacramento Kings': 'SAC',
                'San Antonio Spurs': 'SAS',
                'Toronto Raptors': 'TOR',
                'Utah Jazz': 'UTA',
                'Washington Wizards': 'WAS',
            }
            team_df['AwayTeam'] = team_df['AwayTeam'].map(team_abbreviations)
            team_df['HomeTeam'] = team_df['HomeTeam'].map(team_abbreviations)
            for market in markets:
                bareodds = get_most_recent_odds(game_id, market, new_time)
                if not bareodds:
                    print(market)
                    continue
                fanduel_outcomes = [outcome for sportsbook in bareodds['sportsbooks'] if sportsbook['bookie_key'] == 
                                         'fanduel' for outcome in sportsbook['market']['outcomes']]
                if not fanduel_outcomes:
                    print(market)
                    continue
                result_df = pd.DataFrame(fanduel_outcomes)
                result_df['timestamp'] = pd.to_datetime(result_df['timestamp'])
                result_df['first'] = 1.0
                # # Convert the timestamp to a datetime object
                # Display the resulting DataFrame
                final_df = pd.concat([result_df, team_df], axis=1)
                final_df = final_df.fillna(method='ffill')
                final_df_list.append(final_df)
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
            new_time = start_time + duration
            duration = timedelta(hours=1)
            #markets = ["moneyline", "spread", "total_over_under"]
            for market in markets:
                bareodds = get_most_recent_odds(game_id, market, new_time)
                if not bareodds:
                    continue
                fanduel_outcomes = [outcome for sportsbook in bareodds['sportsbooks'] if sportsbook['bookie_key'] == 
                                         'fanduel' for outcome in sportsbook['market']['outcomes']]
                if not fanduel_outcomes:
                    continue
                result_df = pd.DataFrame(fanduel_outcomes)
                result_df['timestamp'] = pd.to_datetime(result_df['timestamp'])
                result_df = result_df[result_df['timestamp'] > (new_time -duration)]
                result_df['first'] = 0.0
                # # Convert the timestamp to a datetime object
                # Display the resulting DataFrame
                result_df['AwayTeam'] = team_df['AwayTeam'][0]
                result_df['HomeTeam'] = team_df['HomeTeam'][0]
                #print(final_df)
                final_df_list.append(result_df)
                #We can rename final_df to game_df
            gamecount+=1
            print("game " + str(gamecount) + " done")
        complete_df = pd.concat(final_df_list, ignore_index=True)  
        complete_df['timestamp'] = pd.to_datetime(complete_df['timestamp'])
        # complete_df['AwayTeam'].fillna(method='ffill', inplace=True)
        # complete_df['HomeTeam'].fillna(method='ffill', inplace=True)
        # Sort the DataFrame by timestamp in descending order
        complete_df.sort_values(by='timestamp', ascending=False, inplace=True)
        # Drop duplicates based on the specified columns, keeping the last occurrence (highest timestamp)
        complete_df.drop_duplicates(subset=['name', 'description', 'first', 'AwayTeam', 'HomeTeam'], keep='first', inplace=True)
        # If you want to reset the index after dropping rows
        complete_df.reset_index(drop=True, inplace=True)
        complete_df_list.append(complete_df)
        #We can rename complete_df to date_df
        daycount+=1
        print(str(current_date) + " done")
        current_date += timedelta(days=1)
    odds = pd.concat(complete_df_list, ignore_index=True)
    def convert_odds(value):
        if pd.notna(value):
            if value < 0:
                return (100 / abs(int(value))) * 100
            else:
                return int(value)
        else:
            return value

    # # Apply the conversion function to the 'results' column
    odds['odds'] = odds['odds'].apply(convert_odds)
    # # if len(games['games']) == 0:
    # #     print('No games scheduled for today.')
    # #     return

    # # first_game = games['games'][0]
    # # game_id = first_game['game_id']
    columns_to_drop = ['participant','participant_name']
    odds.drop(columns=columns_to_drop, inplace=True)
    odds.to_csv('rawoddspushedml.csv', index=False)
    

    

if __name__ == '__main__':
    main()