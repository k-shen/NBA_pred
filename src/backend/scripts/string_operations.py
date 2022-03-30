#Contains functions involving string manipulation

import constants
import re
import calendar

def getNBAPerGameurl(type, season, date):
    season_info = '&Season=' + season + '&SeasonType=Regular%20Season'
    
    month, day, year = date.split('/')
    date_info = '&DateFrom=' + month + '%2F' + day +'%2F' + year + \
        '&DateTo=' + month + '%2F' + day + '%2F' + year

    url = constants.BASE_URL + type + constants.BASE_URL_EXTENSION + season_info + date_info

    return url

def getNBALastNGamesurl(type, season, N):
    season_info = '&Season=' + season + '&SeasonType=Regular%20Season'
    
    if N < 1 or N > 15:
        print("Error, can only retrieve last 1-15 game data")

    last_n = '&LastNGames=' + str(N)
    url = constants.BASE_URL + type + constants.LAST_N_EXTENSION + season_info + last_n

    return url

def getBRurl(season, date):
    month, _, _ = date.split('/')
    return "https://www.basketball-reference.com/leagues/NBA_"+ constants.SEASONS_URL_EQ[season] + \
        "_games-" + calendar.month_name[int(month)].lower() + ".html"
    
def matchupByDate(lines, date):
    month, day, year = date.split('/')
    date_ = year+month+day
    games_pattern = '(.*csk="'+date_+'.*)'
    games_ = str(re.findall(games_pattern, lines))
    games_ = removeAtags(games_)
    home = re.findall('home_team_name">([^<]+)', games_)
    away = re.findall('visitor_team_name">([^<]+)', games_)
    assert(len(home) == len(away))
    results = {}
    for i in range(len(home)):
        results[home[i]] = away[i]

    return results


def getCategoriesFromHTML(html):
    pattern = 'data-field="([^"]+)'
    categories = re.findall(pattern, html)
    i = len(categories) - 1

    while i >= 0 and len(categories[i]) > 5 and categories[i][-5:] == '_RANK':
        categories.remove(categories[i])
        i -= 1
    
    return categories

def removeAtags(text):
    a_tag_pattern = '<[/]?a[^>]*>'
    text = re.sub(a_tag_pattern, '', text)
    return text

def removePopUptags(text):
    popup_tag_pattern = '<[/]?stats-popup[^>]*>'
    text = re.sub(popup_tag_pattern, '', text)
    return text

def removeEmpty(text):
    new = text.replace("\n", '')
    new = re.sub('\s+[^A-Z^0-9^a-z]', '', new)
    new = new.replace("\t", '')
    
    return new

def splitTeam(text, category):
    division_pattern = 'sorted">([^!]*)</tr>'
    team_data_ = re.findall(division_pattern, text)
    team_data = {}
    name_pattern = '([^<]+)</td>'
    number_pattern = '<td>([-0-9.]+)<?/td>'

    for team_ in team_data_:
        name = re.findall(name_pattern, team_)[0]
        if name == 'LA Clippers':
            name = 'Los Angeles Clippers'

        data_ = re.findall(number_pattern, team_)
        removing = constants.DATA_CATEGORIES[category]
        shift = 0
        for i in range(len(removing)):
            data_.pop(removing[i]-shift)
            shift += 1
        team_data[name] = data_

    return team_data

def getAllTeamStats(html, category):
    text = removeAtags(html)
    text = removePopUptags(text)
    text = removeEmpty(text)
    team_data = splitTeam(text, category)

    return team_data

def delimiterLoading():
    print(".", end="")