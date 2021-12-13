from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from string_operations import *
from constants import *
from webdriver_manager.chrome import ChromeDriverManager
import csv

CHROME_OPTION = Options()
CHROME_OPTION.add_argument("--window-size=2000,0")
CHROME_OPTION.add_argument("--start-maximized")
# CHROME_OPTION.add_argument("--headless")


def getGameDataOfDate(season, date):
    
    #data_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=CHROME_OPTION)
    DRIVER = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=CHROME_OPTION)
    team_data = {}
    columns = ['TEAM']
    sanity = 0
    
    for data_category in constants.DATA_CATEGORIES.keys(): #loop through different types of data
        url = getNBAPerGameurl(data_category, season, date)
        DRIVER.get(url)
        
        time.sleep(1)
        html = DRIVER.page_source
        soup = BeautifulSoup(html, 'html.parser')
        if soup.title.text == "404 Not Found":
            print("Oops, seems like the URL formation went wrong")
            return None, None

        column_ = getCategoriesFromHTML(str(soup.find('thead')))
        if len(column_) == 0:
            print("error in getting data from " + date + ", skipped")
            return None, None
        column_.pop(0)
        teams_ = getAllTeamStats(str(soup.find('tbody')), data_category)
        removing = constants.DATA_CATEGORIES[data_category]
        shift = 0
        for i in range(len(removing)):
            column_.pop(removing[i]-shift)
            shift += 1

        columns = columns + column_
        sample_team = list(teams_.keys())[0]
        assert(len(column_) == len(teams_[sample_team]))
        sanity+= len(teams_[sample_team])

        for k, v in teams_.items():
            if k not in team_data.keys():
                team_data[k] = v
            else:
                team_data[k] = team_data[k] + teams_[k]
        
        print("collected the "+data_category+" data of "+date)

    #data_driver.close()
    DRIVER.close()
    return team_data, columns

def getTeamsLastNGameData(season, N):
    
    #data_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=CHROME_OPTION)
    #data_driver = webdriver.Chrome(ChromeDriverManager().install())
    DRIVER = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=CHROME_OPTION)
    team_data = {}
    columns = ['TEAM']
    sanity = 0
    
    for data_category in constants.DATA_CATEGORIES.keys(): #loop through different types of data
        url = getNBALastNGamesurl(data_category, season, N)
        DRIVER.get(url)
        
        time.sleep(1)
        html = DRIVER.page_source
        soup = BeautifulSoup(html, 'html.parser')
        if soup.title.text == "404 Not Found":
            print("Oops, seems like the URL formation went wrong")
            return None, None

        column_ = getCategoriesFromHTML(str(soup.find('thead')))
        column_.pop(0)
        teams_ = getAllTeamStats(str(soup.find('tbody')), data_category)
        removing = constants.DATA_CATEGORIES[data_category]
        shift = 0
        for i in range(len(removing)):
            column_.pop(removing[i]-shift)
            shift += 1

        columns = columns + column_
        sample_team = list(teams_.keys())[0]
        assert(len(column_) == len(teams_[sample_team]))
        sanity += len(teams_[sample_team])

        for k in teams_.keys():
            teams_[k] = [float(x) for x in teams_[k]]
            if k not in team_data.keys():
                teams_[k].pop(0)
                team_data[k] = teams_[k]
            else:
                team_data[k] = team_data[k] + teams_[k]
        
        print("collected the "+data_category+" data of the last " + str(N) + " games")

    #data_driver.close()
    DRIVER.close()
    return team_data

def getScheduleOfDate(season, date):
    url = getBRurl(season, date)
    
    DRIVER = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=CHROME_OPTION)
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    DRIVER.get(url)
        
    time.sleep(1)
    html = DRIVER.page_source
    soup = BeautifulSoup(html, 'html.parser')
    if soup.title.text == "404 Not Found":
        print("Oops, seems like the URL formation went wrong")
        return None
    
    results = matchupByDate(str(soup.get_text), date)
    #driver.close()
    DRIVER.close()
    return results


# get performance data & error handling
def buildDataOfDate(season, date):
    team_data_, columns = getGameDataOfDate(season, date)
    '''
    writeColumn(columns) #only on the data file creation 
    return 
    '''

    if team_data_ == None:
        print("error in getting data from " + date + ", skipped")
        return None
    
    matchups = getScheduleOfDate(season, date)
    if matchups == None:
        print("error in getting matchups from " + date + ", skipped")
        return None

    team_data = {}
    for home, away in matchups.items():
        team_data[home] = team_data_[home]
        team_data[away] = team_data_[away]
    
    return team_data

# writes the column of the csv file, only on the data file creation 
def writeColumn(columns):
    with open(DATAFILE, "w") as file:
        writer = csv.writer(file)
        writer.writerow(columns)

# appends rows of data to the csv file
def addDataToCSV(data, date):
    with open(DATAFILE, "a") as file:
        writer = csv.writer(file)
        for team in data.keys():
            name = team + " " + date
            to_write = [name]
            to_write = to_write + data[team]
            writer.writerow(to_write)

    with open(LASTRECORD, 'w') as infile:
            infile.write(date)
            
# writes full season data to file
def writeDataOfSeason(season):
    start_date = constants.SEASON_DURATION[season][0]
    end_date = constants.SEASON_DURATION[season][1]
    delta = datetime.timedelta(days=1)
    while start_date <= end_date:
        date = start_date.strftime("%m/%d/%Y")
        start_date += delta
        data = buildDataOfDate(season, date)
        if data == None:
            continue
        #return
        addDataToCSV(data, date)

def appendData(season, from_date, to_date):
    delta = datetime.timedelta(days=1)
    while from_date < to_date:
        date = from_date.strftime("%m/%d/%Y")
        from_date += delta
        data = buildDataOfDate(season, date)
        if data == None:
            continue
        addDataToCSV(data, date)

def buildData():
    for season in constants.SEASON_DURATION.keys():
        writeDataOfSeason(season)

if __name__ == '__main__':
    #getScheduleOfDate("2019-20", "01/01/2020")
    #buildData()
    print()