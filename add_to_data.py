import pred_model
import datetime
import pandas as pd
import numpy as np
import re
import os
from os import path
import read_team_data

TEAMS = {'Los Angeles Clippers', 'Charlotte Hornets', 'Chicago Bulls', 'San Antonio Spurs',
         'New Orleans Pelicans', 'Golden State Warriors', 'Oklahoma City Thunder', 'Memphis Grizzlies',
         'New York Knicks', 'Houston Rockets', 'Indiana Pacers', 'Toronto Raptors', 'Minnesota Timberwolves',
         'Dallas Mavericks', 'Portland Trail Blazers', 'Denver Nuggets', 'Orlando Magic', 'Boston Celtics',
         'Phoenix Suns', 'Sacramento Kings', 'Milwaukee Bucks', 'Washington Wizards', 'Los Angeles Lakers',
         'Miami Heat', 'Utah Jazz', 'Brooklyn Nets', 'Detroit Pistons', 'Cleveland Cavaliers', 'Atlanta Hawks',
         'Philadelphia 76ers'}


YEAR = 2021
CONSIDER_DATE = True
date_ = datetime.date.today()
month = date_.strftime("%B").lower()
week = str(date_)[-5:]
month_ = str(date_)[-5:-3]


def readWebsite(prev_date):
    from urllib.request import urlopen
    from bs4 import BeautifulSoup

    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(
        YEAR, month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    with open("{}_{}/record_html_{}.txt".format(YEAR-1, YEAR, month), "w") as dataFile:
        dataFile.write(soup.prettify())
        dataFile.close()

    with open("{}_{}/record_html_{}.txt".format(YEAR-1, YEAR, month), "r") as inFile:
        lines = inFile.readlines()
        records = getRecords(lines, prev_date)

        with open("{}_{}/record_{}.csv".format(YEAR-1, YEAR, week), "w") as outFile:
            outFile.write('Away, Away_Score, Home, Home_Score\n')
            for game in records:
                outFile.write('{}, {}, {}, {}\n'.format(
                    game[0], game[1], game[2], game[3]))

            outFile.close()

        inFile.close()

    os.remove("{}_{}/record_html_{}.txt".format(YEAR-1, YEAR, month))
    return "{}_{}/record_{}.csv".format(YEAR-1, YEAR, week)


def getRecords(lines, prev_date):
    played = True
    idx = 0
    records = []
    while idx < len(lines) and played:
        line = lines[idx].strip()
        result = []
        if (re.findall('<td class=\"left\" csk=\"\D{3}\.\d{9}\D{3}\" data-stat="visitor_team_name">', line)):
            try:
                points = int(lines[idx + 6].strip())
            except ValueError:
                played = False
                break
            played = True

            if CONSIDER_DATE:
                game_day = lines[idx].strip()[32:34]
                if game_day[0] == '0':
                    game_day = game_day[1]
                if int(game_day) < int(prev_date):
                    idx += 16
                    continue

            result = processGame(lines[idx:idx + 16])

            if result != []:
                records.append(result)
            else:
                raise TypeError(
                    "Something went wrong in reading game process")
            idx += 16
            continue

        else:
            idx += 1
    return records


def processGame(lines):
    visitingTeam = lines[2].strip()
    if not re.findall("\w*\s\w*|\w*\s\w*\s\w*", visitingTeam):
        raise ValueError("Something went wrong, look at record html")

    try:
        visitPts = int(lines[6].strip())
        homeTeam = lines[10].strip()
        if not re.findall("\w*\s\w*|\w*\s\w*\s\w*", homeTeam):
            raise ValueError("Something went wrong, look at record html")

        homePts = int(lines[14].strip())
        return [visitingTeam, visitPts, homeTeam, homePts]
    except ValueError:
        return []


def addData(recordFile):
    print("Retrieving most recent data...")
    new_data_file = read_team_data.main()

    if not (path.exists("home_data.csv") and path.exists("away_data.csv")
            and path.exists("home_scores.csv") and path.exists("away_scores.csv")):
        pred_model.buildData()

    away_data = []
    home_data = []
    away_scores = []
    home_scores = []

    teamData = pd.read_csv(new_data_file)
    with open(recordFile, 'r') as recFile:
        games = recFile.readlines()
        games.pop(0)
        for game in games:
            stats = []
            visit, visitPts, home, homePts = game.split(',')
            visitPts = int(visitPts)
            homePts = int(homePts)

            row_ = teamData.loc[teamData['team_name']
                                == visit.strip()].values[0]
            row_ = list(row_)
            row_.pop(0)
            row_.pop(0)
            row_.pop()
            stats.extend(list(row_))

            row_ = teamData.loc[teamData['team_name']
                                == home.strip()].values[0]

            row_ = list(row_)
            row_.pop(0)
            row_.pop(0)
            row_.pop()
            stats.extend(list(row_))
            away_data.append(stats)
            away_scores.append(visitPts)

            stats = []
            row_ = teamData.loc[teamData['team_name']
                                == home.strip()].values[0]
            row_ = list(row_)
            row_.pop(0)
            row_.pop(0)
            row_.pop()
            stats.extend(list(row_))
            row_ = teamData.loc[teamData['team_name']
                                == visit.strip()].values[0]
            row_ = list(row_)
            row_.pop(0)
            row_.pop(0)
            row_.pop()
            stats.extend(list(row_))
            home_data.append(stats)

            home_scores.append(homePts)

    home_data = np.array(home_data)
    away_data = np.array(away_data)
    home_scores = np.array(home_scores)
    away_scores = np.array(away_scores)

    with open("home_data.csv", "a") as inFile:
        np.savetxt(inFile, home_data, delimiter=',')

    with open("away_data.csv", "a") as inFile:
        np.savetxt(inFile, away_data, delimiter=',')

    with open("home_scores.csv", "a") as inFile:
        np.savetxt(inFile, home_scores, delimiter=',')

    with open("away_scores.csv", "a") as inFile:
        np.savetxt(inFile, away_scores, delimiter=',')


if __name__ == '__main__':
    last_date = ''

    with open('last_added.txt', 'r') as dateFile:
        last_date = dateFile.readlines()
        last_date = str(last_date[0])
        dateFile.close()
    if last_date == '':
        print("Cannot find last adding date, use read_record.py")
        exit()

    last_month = last_date[-5:-3]
    last_day = last_date[-2:]

    if last_day[0] == '0':
        last_day = last_day[1]

    if last_month != month_:
        CONSIDER_DATE = False

    recordFile = readWebsite(last_day)
    addData(recordFile)

    with open('last_added.txt', 'w') as dateFile:
        dateFile.write(str(date_))
        dateFile.close()
