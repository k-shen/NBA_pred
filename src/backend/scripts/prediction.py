from build_data import *
from build_model import *
from constants import *
from datetime import datetime

def readLastUpdate():
    with open(LASTRECORD, 'r') as infile:
        last = infile.readline()
        format_str = '%m/%d/%Y'
        last_date = datetime.strptime(last, format_str).date()
        return last_date

def addNewData():
    now = datetime.today().date()
    last = readLastUpdate()
    collect = 'y'

    if last < SEASON_DURATION[SEASONS_LIST[-1]][0] and last >= SEASON_DURATION[SEASONS_LIST[-2]][1]:
        last = SEASON_DURATION[SEASONS_LIST[-1]][0]
    
    if now < SEASON_DURATION[SEASONS_LIST[-1]][0]:
        print("Season has yet to start, check back later")
        return
    if now < last:
        print("There are no games since last recorded data")
        return

    if last == now:
        print("It seems like the last update was today, do you still wish to collect today's data? Any duplicated data \
            collection will need to be manually deleted.")
        collect = input("(y/n): ")
    
    if collect == 'y':
        appendData(SEASON_DURATION[-1], last, now)
        with open(LASTRECORD, 'w') as infile:
            format_str = '%m/%d/%Y'
            this_date = datetime.strptime(now, format_str).date()
            infile.write(this_date)

def predictUsingLastNGameData(N, away_team, home_team):
    addNewData()
    print("Retriving new data, ignore browser pop-ups")
    data = getTeamsLastNGameData(SEASONS_LIST[-2], N)
    regression, model = buildModel(0.7, [])
    print("Estimating the team's performance based on the previous 3 games...")
    
    results = predictionHelper(home_team, away_team, regression, data)
    print("The Ridge regression model predicts that " + home_team + " " + str(round(results[0], 1)) + 
    ": " + away_team + " " + str(round(results[1], 1)))

    results = predictionHelper(home_team, away_team, model, data)
    print("The Keras Sequential model predicts that " + home_team + " " + str(round(results[0], 1)) + 
    ": " + away_team + " " + str(round(results[1], 1)))

def predictionHelper(home_team, away_team, model, data):
    matchup = []
    matchup.append(data[home_team] + data[away_team])
    matchup.append(data[away_team] + data[home_team])
    result = model.predict(matchup)
    if isinstance(result[0], np.ndarray):
        result = [x[0] for x in result]
    return result

if __name__ == '__main__':
    away_team = ''
    while away_team not in ALL_TEAM_NAMES:
        away_team = input(
            'Enter Away Team (Full Name, Check Spelling & Capitalization): ')
        away_team = away_team.strip()

    home_team = ''
    while home_team not in ALL_TEAM_NAMES:
        home_team = input(
            'Enter Home Team (Full Name, Check Spelling & Capitalization): ')
        home_team = home_team.strip()
    predictUsingLastNGameData(3, away_team, home_team)
    #predictUsingLastNGameData(3, 'Houston Rockets', 'Atlanta Hawks')
    