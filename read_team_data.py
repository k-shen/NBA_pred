import os
import datetime
YEAR = 2021
NOTINCLUDE = {'team_name', 'attendance_per_g', 'attendance', 'arena_name'}
TEAMS = set()

date = datetime.date.today()
week = str(date)[-5:]


def readWebsite():
    from urllib.request import urlopen
    from bs4 import BeautifulSoup

    url = "https://www.basketball-reference.com/leagues/NBA_{}.html?lid=header_seasons#all_team-stats-per_game".format(
        YEAR)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    with open("{}_{}/data_html_{}.txt".format(YEAR-1, YEAR, week), "w") as dataFile:
        dataFile.write(soup.prettify())
        dataFile.close()

    with open("{}_{}/data_html_{}.txt".format(YEAR-1, YEAR, week), "r") as inFile:
        lines = inFile.readlines()

        trad_start_idx = findInHTML("T", lines)
        opp_start_idx = findInHTML("O", lines)
        misc_start_idx = findInHTML("M", lines)
        traditional_portion = lines[trad_start_idx:trad_start_idx + 30]
        opponent_portion = lines[opp_start_idx:opp_start_idx+30]
        miscellaneous_portion = lines[misc_start_idx:misc_start_idx+30]

        # print(formTable(traditinoal_portion))
        traditional = formTable(traditional_portion)

        opponent = formTable(opponent_portion)
        miscellaneous = formTableM(miscellaneous_portion)
        combineTable(traditional, opponent, miscellaneous)
        inFile.close()

    os.remove("{}_{}/data_html_{}.txt".format(YEAR-1, YEAR, week))


def formTable(html_str):
    import re
    team_stat = {}
    cols = findCols(html_str[0].strip())
    for line in html_str:
        line = line.strip()
        stat_dict = {}
        team_name = re.findall(">(\w*\s\w*|\w*\s\w*\s\w*)</a", line)[0]
        TEAMS.add(team_name)
        categories = re.findall(
            ">(\+\d*\.\d+|\-\d*\.\d+|\.\d+|\d+|\d+\.\d+)</td>", line)

        for col, num in zip(cols, categories):
            stat_dict[col] = [round(float(num), 2)]
        team_stat[team_name] = stat_dict

    return team_stat


def findCols(line):
    import re

    matches = re.findall("data-stat=\"(.{,20})\" >", line)
    col = [gr for gr in matches if gr not in NOTINCLUDE and 'ranker' not in gr]
    return col


def findColsM(line):
    import re

    matches = re.findall("data-stat=\"([^r][^t].{,20})\" >", line)
    col = [gr for gr in matches if gr not in NOTINCLUDE and 'ranker' not in gr]
    return col


def formTableM(html_str):
    import re
    team_stat = {}
    cols = findColsM(html_str[0].strip())
    for line in html_str:
        line = line.strip()
        stat_dict = {}
        team_name = re.findall(">(\w*\s\w*|\w*\s\w*\s\w*)</a", line)[0]
        TEAMS.add(team_name)
        categories = re.findall(
            ">(\+\d*\.\d+|\-\d*\.\d+|\.\d+|\d+|\d+\.\d+)</td>", line)

        for col, num in zip(cols, categories):
            stat_dict[col] = [round(float(num), 2)]
        team_stat[team_name] = stat_dict

    return team_stat


def combineTable(data1, data2, data3):
    import pandas as pd
    all_team_data = pd.DataFrame()

    for team in TEAMS:
        trad_dict = data1[team]
        opp_dict = data2[team]
        misc_dict = data3[team]

        trad_dict.update(opp_dict)
        trad_dict.update(misc_dict)
        trad_dict.update({"team_name": team})
        team_df = pd.DataFrame.from_dict(trad_dict)
        all_team_data = pd.concat([all_team_data, team_df])

    all_team_data.reset_index()
    all_team_data.to_csv("{}_{}/data_{}.csv".format(YEAR-1, YEAR, week))


def findInHTML(symbol, lines):
    tableName = ''
    target_beginning = '<tbody><tr ><th scope="row" class="right " data-stat="ranker"'
    if symbol == 'T':
        tableName = "<caption>Team Per Game Stats Table</caption>"
    elif symbol == 'O':
        tableName = "<caption>Opponent Per Game Stats Table</caption>"
    else:
        tableName = "<caption>Miscellaneous Stats Table</caption>"

    idx = 0
    for line in lines:
        line = line.strip()
        if line == tableName:
            while idx < len(lines) and target_beginning not in lines[idx]:
                idx += 1

            if idx == len(lines):
                raise ValueError("Cannot find {} table", symbol)
            else:
                return idx

        idx += 1

    return 0


def main():
    readWebsite()
    return "{}_{}/data_{}.csv".format(YEAR-1, YEAR, week)


if __name__ == '__main__':
    main()
    print('Generating data at {}_{}/data_{}.csv'.format(YEAR-1, YEAR, week))
