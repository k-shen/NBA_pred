from numpy.lib.function_base import average
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.layers import Dense
from sklearn.metrics import accuracy_score
from sklearn.linear_model import Ridge
import pandas as pd
import numpy as np
import os
import re
from os import path
import glob
import read_team_data
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

seasons = ['2019_2020/', '2020_2021/']
TEAMS = {'Los Angeles Clippers', 'Charlotte Hornets', 'Chicago Bulls', 'San Antonio Spurs',
         'New Orleans Pelicans', 'Golden State Warriors', 'Oklahoma City Thunder', 'Memphis Grizzlies',
         'New York Knicks', 'Houston Rockets', 'Indiana Pacers', 'Toronto Raptors', 'Minnesota Timberwolves',
         'Dallas Mavericks', 'Portland Trail Blazers', 'Denver Nuggets', 'Orlando Magic', 'Boston Celtics',
         'Phoenix Suns', 'Sacramento Kings', 'Milwaukee Bucks', 'Washington Wizards', 'Los Angeles Lakers',
         'Miami Heat', 'Utah Jazz', 'Brooklyn Nets', 'Detroit Pistons', 'Cleveland Cavaliers', 'Atlanta Hawks',
         'Philadelphia 76ers'}


def buildData():
    print("Retrieving most recent data...")
    new_data_file = read_team_data.main()
    away_data = []
    home_data = []
    away_scores = []
    home_scores = []

    for directory in seasons:
        for allFiles in os.listdir(directory):
            RecordFile = re.findall('record_.{,12}\.csv', allFiles)
            teamData = pd.read_csv(new_data_file)
            if (RecordFile):
                with open('{}{}'.format(directory, RecordFile[0]), 'r') as recFile:
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

                    recFile.close()

    home_data = np.array(home_data)
    away_data = np.array(away_data)
    home_scores = np.array(home_scores)
    away_scores = np.array(away_scores)

    np.savetxt("home_data.csv", home_data, delimiter=',')
    np.savetxt("away_data.csv", away_data, delimiter=',')
    np.savetxt("home_scores.csv", home_scores, delimiter=',')
    np.savetxt("away_scores.csv", away_scores, delimiter=',')


def createModel(train_percentage):
    home_data = np.genfromtxt('home_data.csv', delimiter=',', dtype=float)
    away_data = np.genfromtxt('away_data.csv', delimiter=',', dtype=float)
    home_scores = np.genfromtxt('home_scores.csv', delimiter=',', dtype=float)
    away_scores = np.genfromtxt('away_scores.csv', delimiter=',', dtype=float)

    X_train1, X_test_home, y_train1, y_test_home = train_test_split(
        home_data, home_scores, test_size=(1-train_percentage), shuffle=True)
    X_train2, X_test_away, y_train2, y_test_away = train_test_split(
        away_data, away_scores, test_size=(1-train_percentage), shuffle=True)

    train_matrix = np.concatenate((X_train1, X_train2), axis=0)
    train_target = np.concatenate((y_train1, y_train2), axis=None)
    win_loss = []
    for home, away in zip(y_test_home, y_test_away):
        if (home > away):
            win_loss.append(1)
        else:
            win_loss.append(0)

    # ridge model
    regression = Ridge()
    regression.fit(train_matrix, train_target)
    test_home = regression.predict(X_test_home)
    test_away = regression.predict(X_test_away)

    pred_win_loss = []
    for home, away in zip(test_home, test_away):
        if (home > away):
            pred_win_loss.append(1)
        else:
            pred_win_loss.append(0)

    acc1 = accuracy_score(win_loss, pred_win_loss)

    # NN model
    model = tf.keras.Sequential()
    model.add(
        Dense(len(home_data[0]), input_dim=len(home_data[0]),
              kernel_initializer='normal', activation='relu'))
    model.add(Dense(19, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])

    history = model.fit(train_matrix, train_target,
                        verbose=0, validation_split=0.2)

    test_home = model.predict(X_test_home)
    test_away = model.predict(X_test_away)

    pred_win_loss = []
    for home, away in zip(test_home, test_away):
        if (home > away):
            pred_win_loss.append(1)
        else:
            pred_win_loss.append(0)

    acc2 = accuracy_score(win_loss, pred_win_loss)
    return regression, model, acc1, acc2


def predicting(AwayTeam, HomeTeam, new_data_file):
    if not (path.exists("home_data.csv") and path.exists("away_data.csv")
            and path.exists("home_scores.csv") and path.exists("away_scores.csv")):
        buildData()

    reg_h = []
    reg_a = []
    nn_h = []
    nn_a = []

    teamData = pd.read_csv(new_data_file)
    HomeTeam_data = teamData.loc[teamData['team_name']
                                 == HomeTeam.strip()].values[0]
    AwayTeam_data = teamData.loc[teamData['team_name']
                                 == AwayTeam.strip()].values[0]

    HomeTeam_win = int(HomeTeam_data[-21])
    HomeTeam_proj_win = int(HomeTeam_data[-19])
    HomeTeam_data_value = list(HomeTeam_data)
    HomeTeam_data_value.pop()
    HomeTeam_data_value.pop(0)
    HomeTeam_data_value.pop(0)

    AwayTeam_win = int(AwayTeam_data[-21])
    AwayTeam_proj_win = int(AwayTeam_data[-19])
    AwayTeam_data_value = list(AwayTeam_data)
    AwayTeam_data_value.pop()
    AwayTeam_data_value.pop(0)
    AwayTeam_data_value.pop(0)

    stat_home = []
    stat_home.extend(HomeTeam_data_value)
    stat_home.extend(AwayTeam_data_value)
    stat_away = []
    stat_away.extend(AwayTeam_data_value)
    stat_away.extend(HomeTeam_data_value)
    stat_home = np.array(stat_home).reshape((1, len(stat_home)))
    stat_away = np.array(stat_away).reshape((1, len(stat_away)))

    train_percentage = 0.7
    acc1 = []
    acc2 = []
    print("Running Models", end='')
    for i in range(3):
        regression, model, acc1_, acc2_ = createModel(train_percentage)

        home_score_r = regression.predict(stat_home)
        away_score_r = regression.predict(stat_away)
        home_score_n = model.predict(stat_home)
        away_score_n = model.predict(stat_away)
        reg_h.append(home_score_r[0])
        reg_a.append(away_score_r[0])
        nn_h.append(home_score_n[0][0])
        nn_a.append(away_score_n[0][0])
        acc1.append(acc1_)
        acc2.append(acc2_)
        print('.', end='')

    print('\n')
    avg_acc1 = average(acc1)
    avg_acc2 = average(acc2)
    print("With Train Test Split = {:d}:{:d}".format(
        int(100*train_percentage), int(100*(1-train_percentage))))
    print(
        "Average Ridge Regression accuracy on testing sets: {:.2f}%".format(avg_acc1*100))
    print("Average NN accuracy on testing sets: {:.2f}%".format(avg_acc2*100))

    home_score_r = average(reg_h)
    away_score_r = average(reg_a)
    if home_score_r > away_score_r:
        print("With the {} being the home team, regression predicts that they beat the {} by {:.2f} pts".format(
            HomeTeam, AwayTeam, round(home_score_r-away_score_r, 2)))
    else:
        print("With the {} being the home team, regression predicts that they lose to the {} by {:.2f} pts".format(
            HomeTeam, AwayTeam, round(away_score_r-home_score_r, 2)))

    home_score_n = average(nn_h)
    away_score_n = average(nn_a)
    if home_score_n > away_score_n:
        print("With the {} being the home team, NN predicts that they beat the {} by {:.2f} pts".format(
            HomeTeam, AwayTeam, round(home_score_n-away_score_n, 2)))
    else:
        print("With the {} being the home team, NN predicts that they lose to the {} by {:.2f} pts".format(
            HomeTeam, AwayTeam, round(away_score_n-home_score_n, 2)))

    if home_score_r > away_score_r and home_score_n > away_score_n:
        print("The average win margin for {} is {:.2f} pts".format(HomeTeam,
                                                                   avg(home_score_r-away_score_r, home_score_n-away_score_n)))

    if home_score_r < away_score_r and home_score_n < away_score_n:
        print("The average win margin for {} is {:.2f} pts".format(AwayTeam,
                                                                   avg(away_score_r-home_score_r, away_score_n-home_score_n)))

    if HomeTeam_win > HomeTeam_proj_win:
        print("The {} is exceeding expectations by {} wins".format(
            HomeTeam, HomeTeam_win - HomeTeam_proj_win))
    elif HomeTeam_proj_win > HomeTeam_win:
        print("The {} is short of the expectations by {} wins".format(
            HomeTeam, -HomeTeam_win + HomeTeam_proj_win))

    if AwayTeam_win > AwayTeam_proj_win:
        print("The {} is exceeding expectations by {} wins".format(
            AwayTeam, AwayTeam_win - AwayTeam_proj_win))
    elif AwayTeam_proj_win > AwayTeam_win:
        print("The {} is short of the expectations by {} wins".format(
            AwayTeam, -AwayTeam_win + AwayTeam_proj_win))


def avg(num1, num2):
    return (num1 + num2)/2


if __name__ == '__main__':
    print("Retrieving most recent data...")
    new_data_file = read_team_data.main()

    AwayTeam = ''
    while AwayTeam not in TEAMS:
        AwayTeam = input(
            'Enter Away Team (Full Name, Check Spelling & Capitalization): ')
        AwayTeam = AwayTeam.strip()

    HomeTeam = ''
    while HomeTeam not in TEAMS:
        HomeTeam = input(
            'Enter Home Team (Full Name, Check Spelling & Capitalization): ')
        HomeTeam = HomeTeam.strip()

    predicting(AwayTeam, HomeTeam, new_data_file)
    print("Thank you for using the model, hope it helps!")
    print()
    os.remove(new_data_file)
