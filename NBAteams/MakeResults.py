import pandas as pd
from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
import time
import requests
from datetime import datetime
import urllib
import numpy as np
import sys

scores = pd.read_csv('AllScores.csv')
odds = pd.read_csv('rawpushedspread.csv')
# odds["timestamp"] = pd.to_datetime(odds["timestamp"])
# odds["timestamp"] = odds["timestamp"].dt.date
odds['timestamp'] = pd.to_datetime(odds['timestamp'], format='%Y-%m-%d %H:%M:%S')

# Define the cutoff date
cutoff_date_earlier = pd.to_datetime('2022-11-05')
cutoff_date_later = pd.to_datetime('2022-11-06')

# Apply the adjustment for dates before 11/5
odds.loc[(odds['timestamp'] < cutoff_date_earlier), 'timestamp'] -= pd.Timedelta(hours=4)

# Apply the adjustment for dates on or after 11/6
odds.loc[(odds['timestamp'] >= cutoff_date_later), 'timestamp'] -= pd.Timedelta(hours=5)

# Now the dates between odds and scores matchup

scores['PLUS_MINUS'] = -scores['PLUS_MINUS']
# This is helpful because now we have a scores column that is in terms of sports betting odds
# If the team won by 3, we have -3. So now in order to check if a team covered the spread, we simply check 
# to see if the value in PLUS_MINUS is greater than the value in handicap

# Create new 'game' column in 'odds' dataframe
odds['game'] = odds['timestamp'].dt.strftime('%Y-%m-%d') + ' ' + odds['name'].astype(str)

# Convert 'GAME_DATE' to datetime format in 'scores' dataframe
scores['GAME_DATE'] = pd.to_datetime(scores['GAME_DATE'], format='%Y-%m-%d')

# Create new 'game' column in 'scores' dataframe
scores['game'] = scores['GAME_DATE'].dt.strftime('%Y-%m-%d') + ' ' + scores['TEAM_NAME'].astype(str)

merged_df = pd.merge(scores, odds, on='game', how='inner')
merged_df['hit'] = 0.5  # Default value for cases where 'handicap' is equal to 'PLUS_MINUS'
merged_df.loc[merged_df['handicap'] > merged_df['PLUS_MINUS'], 'hit'] = 1  # Set 'hit' to 1 for 'handicap' < 'PLUS_MINUS'
merged_df.loc[merged_df['handicap'] < merged_df['PLUS_MINUS'], 'hit'] = 0  # Set 'hit' to 0 for 'handicap' > 'PLUS_MINUS'
columns_to_remove = ["TEAM_NAME","GAME_DATE","WL","timestamp",
]
results = merged_df.drop(columns=columns_to_remove)
results['difference'] = 0

# Group by 'game' and iterate through each group
for _, group in results.groupby('game'):
    # Find rows with 'first' equal to 0.0 and 1.0 within each group
    row_first_0 = group[group['first'] == 0.0]
    row_first_1 = group[group['first'] == 1.0]

    # Calculate the difference and update the 'difference' column
    if not row_first_0.empty and not row_first_1.empty:
        difference_value = row_first_1['handicap'].values[0] - row_first_0['handicap'].values[0]
        results.loc[row_first_0.index, 'difference'] = difference_value

# Display the updated DataFrame


# If first contains a 1, that means it was the pregame odds, a 0 means "halftime"
# If hit contains a 1 that means it hit, 0.5 means push, 0 means miss
#key - fav(favorite), 
# ud(underdog), 
# ag(away - for a favorite this means if they are less favorite)
# to(towards - for an underdog this means if they are less of an underdog)
# no(no shift)
#we should probably do this by team instead of by the underdog and favorite 
#and then take out any teams that are succesful
#there is a lot of duplicate data here.
nba_teams = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
    'Houston Rockets', 'Indiana Pacers', 'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies',
    'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
    'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
]

# Initialize a dictionary with NBA teams as keys and a 14-entry list containing 0s as values
dic = {team: [0] * 19 for team in nba_teams}
#If we are to do this with teams we need to keep track of how often they push, along with 4 statistics
#When they are the favorites, and the line moves against them, how do they fare
#When they are the favorites, and the line moves towards them, how do they fare
#When they are the favorites, and the line does not move , how do they fare
#When they are the underdogs, and the line moves against them, how do they fare
#When they are the underdogs, and the line moves towards them, how do they fare
#When they are the underdogs, and the line does not move, how do they fare
#Combine 1 and 4
#Combine 2 and 5
#Finally just in general how do they do against the live spreads.
# Create a dictionary of the teams as the keys and then 14 double lists for the values.
# So now, if handicap + difference is positive, that means the team was an underdog, opposite means favorite
odic = {team: [0] * 9 for team in nba_teams}
for index, row in results.iterrows():
    # Check conditions and update counters accordingly
    if row['first'] == 0:
        #We are dealing with a halftime entry, which is all we care about
        if row['handicap'] + row['difference'] > 0:
            #Team was the favorite.
            if row['difference'] < 0:
                #Line moved against the spread - they are underperforming in the first half
                if row['hit'] == 1.0:
                    dic[row['name']][0] += 1
                    odic[row['name']][0] += row['odds']
                    dic[row['name']][1] += 1
                    dic[row['name']][12] += 1
                    odic[row['name']][6] += row['odds']
                    dic[row['name']][13] += 1
                    odic[row['name']][8] += row['odds']
                    dic[row['name']][16] += 1
                    dic[row['name']][17] += 1
                elif row['hit'] == 0.0:
                    dic[row['name']][1] += 1
                    dic[row['name']][13] += 1
                    dic[row['name']][17] += 1
                else:
                    dic[row['name']][18] += 1
            elif row['difference'] > 0:
                #Line moved towards the spread - they overperformed in the first half
                if row['hit'] == 1.0:
                    odic[row['name']][1] += row['odds']
                    dic[row['name']][2] += 1
                    dic[row['name']][3] += 1
                    odic[row['name']][7] += row['odds']
                    dic[row['name']][14] += 1
                    dic[row['name']][15] += 1
                    odic[row['name']][8] += row['odds']
                    dic[row['name']][16] += 1
                    dic[row['name']][17] += 1
                elif row['hit'] == 0.0:
                    dic[row['name']][3] += 1
                    dic[row['name']][15] += 1
                    dic[row['name']][17] += 1
                else:
                    dic[row['name']][18] += 1
            else:
                #Line did not move
                if row['hit'] == 1.0:
                    odic[row['name']][2] += row['odds']
                    dic[row['name']][4] += 1
                    dic[row['name']][5] += 1
                    odic[row['name']][8] += row['odds']
                    dic[row['name']][16] += 1
                    dic[row['name']][17] += 1
                elif row['hit'] == 0.0:
                    dic[row['name']][5] += 1
                    dic[row['name']][17] += 1
                else:
                    dic[row['name']][18] += 1
        else:
            #Team was an underdog. No chance of ties because the spread is never -0.0
            if row['difference'] > 0:
                #Line moved against the spread - they are underperforming in the first half
                if row['hit'] == 1.0:
                    odic[row['name']][3] += row['odds']
                    dic[row['name']][6] += 1
                    dic[row['name']][7] += 1
                    odic[row['name']][6] += row['odds']
                    dic[row['name']][12] += 1
                    dic[row['name']][13] += 1
                    odic[row['name']][8] += row['odds']
                    dic[row['name']][16] += 1
                    dic[row['name']][17] += 1
                elif row['hit'] == 0.0:
                    dic[row['name']][7] += 1
                    dic[row['name']][13] += 1
                    dic[row['name']][17] += 1
                else:
                    dic[row['name']][18] += 1
            elif row['difference'] < 0:
                #Line moved towards the spread - they overperformed in the first half
                if row['hit'] == 1.0:
                    odic[row['name']][4] += row['odds']
                    dic[row['name']][8] += 1
                    dic[row['name']][9] += 1
                    odic[row['name']][7] += row['odds']
                    dic[row['name']][14] += 1
                    dic[row['name']][15] += 1
                    odic[row['name']][8] += row['odds']
                    dic[row['name']][16] += 1
                    dic[row['name']][17] += 1
                elif row['hit'] == 0.0:
                    dic[row['name']][9] += 1
                    dic[row['name']][15] += 1
                    dic[row['name']][17] += 1
                else:
                    dic[row['name']][18] += 1
            else:
                #Line did not move
                if row['hit'] == 1.0:
                    odic[row['name']][5] += row['odds']
                    dic[row['name']][10] += 1
                    dic[row['name']][11] += 1
                    odic[row['name']][8] += row['odds']
                    dic[row['name']][16] += 1
                    dic[row['name']][17] += 1
                elif row['hit'] == 0.0:
                    dic[row['name']][11] += 1
                    dic[row['name']][17] += 1
                else:
                    dic[row['name']][18] += 1
def printer(intro, file, hits, total, odds):

    if total > 19 and hits > 0:
        profittotal = ((hits / total) * 100) * (1 + (odds / hits) / 100)
        profit = profittotal - 100
        rounded_profit = round(profit, 2)
        if rounded_profit > 10:
            print(intro)
            file.write(str(hits) + ' / ' + str(total) + '\n')
            file.write(f"Total Sample Size: {total}\n")
            file.write(f"Average odds of hits: {odds / hits}\n")
            file.write(f"You would profit {rounded_profit} if you bet $100 on this trend\n")
            file.write('\n')  
original_stdout = sys.stdout
output_file_path = 'output.txt'
with open(output_file_path, 'w') as f:
    sys.stdout = f
    for key in dic:
        hits = dic[key][16]
        total = dic[key][17]
        odds = odic[key][8]
        printer(key + " Hit percentage for second half spreads" ,f,hits,total,odds)
        hits = dic[key][0]
        total = dic[key][1]
        odds = odic[key][0]
        printer(key + " Hit percentage when favorites and underperform",f,hits,total,odds)
        hits = dic[key][2]
        total = dic[key][3]
        odds = odic[key][1]
        printer(key + " Hit percentage when favorites and overperform",f,hits,total,odds)
        hits = dic[key][4]
        total = dic[key][5]
        odds = odic[key][2]
        printer(key + " Hit percentage when favorites and line doesnt move",f,hits,total,odds)
        hits = dic[key][6]
        total = dic[key][7]
        odds = odic[key][3]
        printer(key + " Hit percentage when underdogs and underperform",f,hits,total,odds)
        hits = dic[key][8]
        total = dic[key][9]
        odds = odic[key][4]
        printer(key + " Hit percentage when underdogs and overperform",f,hits,total,odds)
        hits = dic[key][10]
        total = dic[key][11]
        odds = odic[key][5]
        printer(key + " Hit percentage when underdogs and line doesnt move",f,hits,total,odds)
        hits = dic[key][12]
        total = dic[key][13]
        odds = odic[key][6]
        printer(key + " Hit percentage when they underperform in the first half",f,hits,total,odds)
        hits = dic[key][14]
        total = dic[key][15]
        odds = odic[key][7]
        printer(key + " Hit percentage when they overperform in the first half",f,hits,total,odds)       
    sys.stdout = f  
sys.stdout = original_stdout

