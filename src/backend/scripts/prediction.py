from build_data import *
from build_model import *
from constants import *
from datetime import datetime
from datetime import timedelta

THIS_SEASON = SEASONS_LIST[-1]
GAME_ESTIMATE = 4
TTSPLIT_RATIO = 0.7
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

    if last < SEASON_DURATION[THIS_SEASON][0] and last >= SEASON_DURATION[SEASONS_LIST[-2]][1]:
        last = SEASON_DURATION[THIS_SEASON][0]
    
    if now < SEASON_DURATION[THIS_SEASON][0]:
        print("Season has yet to start, check back later")
        return
    if now < last:
        print("There are no games since last recorded data")
        return

    if last == now:
        print("It seems like the last update was today, do you still wish to collect today's data? Any duplicated data \
            collection will need to be manually deleted.")
        collect = input("(y/n): ")
    
    if last == now - timedelta(days=1):
        print("The last data update was yesterday and under the current set up, not collecting same day data. ")
        return

    if collect == 'y':
        print("Updating the database... Ignore browser popups")
        appendData(THIS_SEASON, last+timedelta(days=1), now)

def predictUsingLastNGameData(N, away_team, home_team, data, model_):
    if data == None:
        #print("Retriving new data, ignore browser pop-ups")
        addNewData()
        data = getTeamsLastNGameData(THIS_SEASON, N)
    
    
    print(away_team + " @ " + home_team)
    results = predictionHelper(home_team, away_team, model_, data)
    print("The Ridge regression model predicts that " + home_team + " " + str(round(results[0], 1)) + 
    ": " + away_team + " " + str(round(results[1], 1)))
    print("The total is " + str(round(results[0] + results[1], 1)))

    # results = predictionHelper(home_team, away_team, model, data)
    # print("The Keras Sequential model predicts that " + home_team + " " + str(round(results[0], 1)) + 
    # ": " + away_team + " " + str(round(results[1], 1)))

    print()
    return data

def predictionHelper(home_team, away_team, model, data):
    matchup = []
    matchup.append(data[home_team] + data[away_team])
    matchup.append(data[away_team] + data[home_team])
    result = model.predict(matchup)
    if isinstance(result[0], np.ndarray):
        result = [x[0] for x in result]
    return result

def predicting(data):
    print("This is manual predicting mode")
    if data == None:
        print("Retriving new data, ignore browser pop-ups")
        addNewData()
        data = getTeamsLastNGameData(THIS_SEASON, GAME_ESTIMATE)
    
    away_team = ''
    second = False
    while away_team not in ALL_TEAM_NAMES and away_team not in SHORT_CUTS:
        if (second):
            print('Wrong team name, please check your spelling!')
        away_team = input('Enter Away Team: ')
        away_team = away_team.capitalize()
        second = True
    away_team = SHORT_CUTS_DICT[away_team]
    
    home_team = ''
    second = False
    while home_team not in ALL_TEAM_NAMES and home_team not in SHORT_CUTS:
        if (second):
            print('Wrong team name, please check your spelling!')
        home_team = input('Enter Home Team: ')
        home_team = home_team.capitalize()
        second = True
    home_team = SHORT_CUTS_DICT[home_team]
    regression, model = buildModel(TTSPLIT_RATIO, [])
    data = predictUsingLastNGameData(GAME_ESTIMATE, away_team, home_team, data, regression)
    again = input(
        'Would you like to predict another game (y/n)?: '
    ).strip().capitalize()
    while again != 'Y' and again != 'N':
        print('Please enter either y or n!!')
        again = input(
            'Would you like to predict another game (y/n)?: ').strip().capitalize()
        
    second = True if again == 'Y' else False
    while second:
        away_team = ''
        second = False
        while away_team not in ALL_TEAM_NAMES and away_team not in SHORT_CUTS:
            if (second):
                print('Wrong team name, please check your spelling!')
            away_team = input('Enter Away Team: ')
            away_team = away_team.capitalize()
            
            second = True
        away_team = SHORT_CUTS_DICT[away_team]
        
        home_team = ''
        second = False
        while home_team not in ALL_TEAM_NAMES and home_team not in SHORT_CUTS:
            if (second):
                print('Wrong team name, please check your spelling!')
            home_team = input('Enter Home Team: ')
            home_team = home_team.capitalize()
            second = True
        home_team = SHORT_CUTS_DICT[home_team]
        
        regression, model = buildModel(TTSPLIT_RATIO, [])
        data = predictUsingLastNGameData(GAME_ESTIMATE, away_team, home_team, data, regression)
        again = input(
            'Would you like to predict another game (y/n)?: '
        ).strip().capitalize()
        while again != 'Y' and again != 'N':
            print('Please enter either y or n!!')
            again = input(
                'Would you like to predict another game (y/n)?: ').strip().capitalize()
            
        second = True if again == 'Y' else False

def auto_predict(data):
    print("This is auto predicting mode")
    now = datetime.today().date()
    matchups = getScheduleOfDate(THIS_SEASON, now.strftime("%m/%d/%Y"))
    
    if matchups == None or len(matchups) == 0:
        print("There are no games today... Entering manual predicting mode")
        predicting(None)
        
    if data == None:
        addNewData()
        
    data = getTeamsLastNGameData(THIS_SEASON, GAME_ESTIMATE)
    
    print("")
    regression, model = buildModel(TTSPLIT_RATIO, [])
    for home_team, away_team in matchups.items():
    
        data = predictUsingLastNGameData(GAME_ESTIMATE, away_team, home_team, data, regression)
    
    return data

def home():
    print("Welcome to Kaiwen's NBA prediction")
    current = datetime.today().date()
    
    # Asking for auto prediction
    custom = input(
            'Would you like to automatically predict today\'s game (y/n)?: '
        ).strip().capitalize()
    while custom != 'Y' and custom != 'N':
        print('Please enter either y or n!!')
        custom = input(
            'Would you like to automatically predict today\'s game (y/n)?: ').strip().capitalize()
    
    # Prediction
    data = None
    if custom == 'Y':
        data = auto_predict(None)
    else:
        data = predicting(None)

    # Ask to stay in
    again = input("Would you like to stay in the prediction app (y/n)?: ").strip().capitalize()
    while again != 'Y' and again != 'N':
        print('Please enter either y or n!!')
        again = input(
            'Would you like to stay in the prediction app (y/n)?: ').strip().capitalize()
    again = True if again == 'Y' else False
    while again:
        
        # Asking for auto prediction
        custom = input(
            'Would you like to automatically predict today\'s game (y/n)?: '
        ).strip().capitalize()
        while custom != 'Y' and custom != 'N':
            print('Please enter either y or n!!')
            custom = input(
                'Would you like to automatically predict today\'s game (y/n)?: ').strip().capitalize()
        
        # If model is left unexited overnight 
        new_date = datetime.today().date()
        if new_date > current:
            print("Retriving new data, ignore browser pop-ups")
            addNewData()
            data = getTeamsLastNGameData(THIS_SEASON, GAME_ESTIMATE)
        current = new_date
        
        if custom == 'Y':
            data = auto_predict(data)
        else:
            data = predicting(data)
        
        # Ask to stay in
        again = input("Would you like to stay in the prediction app (y/n)?: ").strip().capitalize()
        while again != 'Y' and again != 'N':
            print('Please enter either y or n!!')
            again = input(
                'Would you like to stay in the prediction app (y/n)?: ').strip().capitalize()
        
        again = True if again == 'Y' else False

    print("Thank you for using the prediction model!!")
    

if __name__ == '__main__':
    home()
