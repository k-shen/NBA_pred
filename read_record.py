import datetime
import pandas as pd
import re

YEAR = 2021
month = 'january'
week = datetime.date.today()
week = str(week)[-5:]
TEAMS = {'Los Angeles Clippers', 'Charlotte Hornets', 'Chicago Bulls', 'San Antonio Spurs',
         'New Orleans Pelicans', 'Golden State Warriors', 'Oklahoma City Thunder', 'Memphis Grizzlies',
         'New York Knicks', 'Houston Rockets', 'Indiana Pacers', 'Toronto Raptors', 'Minnesota Timberwolves',
         'Dallas Mavericks', 'Portland Trail Blazers', 'Denver Nuggets', 'Orlando Magic', 'Boston Celtics',
         'Phoenix Suns', 'Sacramento Kings', 'Milwaukee Bucks', 'Washington Wizards', 'Los Angeles Lakers',
         'Miami Heat', 'Utah Jazz', 'Brooklyn Nets', 'Detroit Pistons', 'Cleveland Cavaliers', 'Atlanta Hawks',
         'Philadelphia 76ers'}


def readWebsite():
    from urllib.request import urlopen
    from bs4 import BeautifulSoup

    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(
        YEAR, month)
    html = urlopen(url)
    soup = BeautifulSoup(html)

    with open("{}_{}/record_html_{}.txt".format(YEAR-1, YEAR, month), "w") as dataFile:
        dataFile.write(soup.prettify())
        dataFile.close()

    with open("{}_{}/record_html_{}.txt".format(YEAR-1, YEAR, month), "r") as inFile:
        lines = inFile.readlines()
        records = getRecords(lines)
        with open("{}_{}/record_{}.csv".format(YEAR-1, YEAR, month), "w") as outFile:
            outFile.write('Away, Away_Score, Home, Home_Score\n')
            for game in records:
                outFile.write('{}, {}, {}, {}\n'.format(
                    game[0], game[1], game[2], game[3]))

            outFile.close()
        inFile.close()


def getRecords(lines):

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


if __name__ == '__main__':
    readWebsite()
