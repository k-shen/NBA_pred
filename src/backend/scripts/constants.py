###########################################################################
#   STORE URL RELATED CONTANTS
#   EXAMPLE:
#   url = BASE_URL + CATEGORY + BASE_URL_EXTENSION_1 + SEASON + DATE_RANGE
#   SEAON = '&Season=2019-20&SeasonType=Regular%20Season'
#   DATE_RANGE = '&DateFrom=12%2F30%2F2019&DateTo=12%2F31%2F2019'
#   Special note:   on nba.com - it is LA Clippers
#                   on basketballreference.com - it is Los Angeles Clippers
#                   the defense category have already been included in others, 
#                       therefore not included in the data gathering process.
#                   to add full future seasons, append to the SEASONS dict & season 
###########################################################################
import datetime
SEASONS_URL_EQ = {'2019-20':'2020', '2020-21':'2021', '2021-22':'2022'}
SEASONS_LIST = ['2019-20', '2020-21', '2021-22']
SEASON_DURATION = {'2019-20':[datetime.date(2019, 10, 22), datetime.date(2020, 3, 10)],
    '2020-21':[datetime.date(2020, 12, 22), datetime.date(2021, 5, 16)],
    '2021-22':[datetime.date(2021, 10, 19), datetime.date(2022, 4, 10)]}
DATAFILE = "../../../data/data.csv"
LASTRECORD = "../../../data/lastRecord.txt"
BASE_URL = "https://www.nba.com/stats/teams/"
DATA_CATEGORIES = {'traditional':[0, 1, 2, 3, 4], 'advanced':[0, 1, 2, 3], 'four-factors':[0, 1, 2, 3, 4, 9, 10, 11, 12], 
'misc':[0, 1, 2, 3, 8, 9, 10, 11], 'scoring':[0, 1, 2, 3]}
BASE_URL_EXTENSION = "/?PerMode=Totals&sort=TEAM_NAME&dir=1"
LAST_N_EXTENSION = "/?sort=TEAM_NAME&dir=1"

NBAWEB_TEAM_NAMES = {'LA Clippers', 'Charlotte Hornets', 'Chicago Bulls', 'San Antonio Spurs',
         'New Orleans Pelicans', 'Golden State Warriors', 'Oklahoma City Thunder', 'Memphis Grizzlies',
         'New York Knicks', 'Houston Rockets', 'Indiana Pacers', 'Toronto Raptors', 'Minnesota Timberwolves',
         'Dallas Mavericks', 'Portland Trail Blazers', 'Denver Nuggets', 'Orlando Magic', 'Boston Celtics',
         'Phoenix Suns', 'Sacramento Kings', 'Milwaukee Bucks', 'Washington Wizards', 'Los Angeles Lakers',
         'Miami Heat', 'Utah Jazz', 'Brooklyn Nets', 'Detroit Pistons', 'Cleveland Cavaliers', 'Atlanta Hawks',
         'Philadelphia 76ers'}

ALL_TEAM_NAMES = {'Los Angeles Clippers', 'Charlotte Hornets', 'Chicago Bulls', 'San Antonio Spurs',
         'New Orleans Pelicans', 'Golden State Warriors', 'Oklahoma City Thunder', 'Memphis Grizzlies',
         'New York Knicks', 'Houston Rockets', 'Indiana Pacers', 'Toronto Raptors', 'Minnesota Timberwolves',
         'Dallas Mavericks', 'Portland Trail Blazers', 'Denver Nuggets', 'Orlando Magic', 'Boston Celtics',
         'Phoenix Suns', 'Sacramento Kings', 'Milwaukee Bucks', 'Washington Wizards', 'Los Angeles Lakers',
         'Miami Heat', 'Utah Jazz', 'Brooklyn Nets', 'Detroit Pistons', 'Cleveland Cavaliers', 'Atlanta Hawks',
         'Philadelphia 76ers'}
