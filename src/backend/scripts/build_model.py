from pandas_operations import *
from sklearn.linear_model import Ridge
import tensorflow as tf
from tensorflow.keras.layers import Dense
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def buildModel(train_percent, deselected):
    orig_data, targets = getDataAndTargets(deselected)

    X_train, X_test, y_train, y_test = splitShuffleTrainTest(orig_data, targets, train_percent)

    regression = Ridge()
    regression.fit(X_train, y_train)
    #print("Evaluating Ridge regression... testing results stored in Ridge.txt")
    evaluateModel(regression, X_test, y_test, "Ridge.txt")

    model = tf.keras.Sequential()
    # model.add(
    #     Dense(len(X_train[0]), input_dim=len(X_train[0]),
    #           kernel_initializer='normal', activation='relu'))
    # model.add(Dense(16, activation='relu'))
    # model.add(Dense(1, activation='linear'))
    # model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])

    # model.fit(X_train, y_train, verbose=0)
    # print("evaluating Keras Sequential... testing results stored in Keras_eval.txt")
    # evaluateModel(model, X_test, y_test, "Keras_eval.txt")
    return regression, model


def splitShuffleTrainTest(data, target, train_pct):
    total_matchup = len(data) // 2

    matchup_idx = random.sample(range(total_matchup), total_matchup)
    random.shuffle(matchup_idx)
    split = int(total_matchup * train_pct)
    training_idx = set(matchup_idx[0:split])

    X_train = []
    X_test = []
    y_train = []
    y_test = []
    for idx in matchup_idx:
        if idx in training_idx:
            X_train.append(data[idx*2])
            X_train.append(data[idx*2+1])
            y_train.append(target[idx*2])
            y_train.append(target[idx*2+1])
        else:
            X_test.append(data[idx*2])
            X_test.append(data[idx*2+1])
            y_test.append(target[idx*2])
            y_test.append(target[idx*2+1])

    assert(len(X_train) == len(y_train))
    assert(len(X_test) == len(y_test))
    return X_train, X_test, y_train, y_test

def evaluateModel(model, X_test, y_test, out_file):
    with open(out_file, 'w') as file:
        y_pred = model.predict(X_test)
        
        if isinstance(y_pred[0], np.ndarray):
            y_pred = [x[0] for x in y_pred]
        iterator = 0
        wins = 0
        total = len(y_pred) / 2
        while iterator + 1 < len(y_pred):
            file.write("actual - " + str(y_test[iterator]) + ":" + str(y_test[iterator+1]) + "\t")
            
            file.write("predicted - " + str(round(y_pred[iterator], 3)) + ":" + str(round(y_pred[iterator + 1], 3)) + "\n")
            if (y_pred[iterator] > y_pred[iterator + 1] and y_test[iterator] > y_test[iterator + 1]):
                wins += 1
            elif (y_pred[iterator] < y_pred[iterator + 1] and y_test[iterator] < y_test[iterator + 1]):
                wins += 1
            iterator += 2
        
        file.write("total games evaluated: " + str(total) + "\n")
        file.write("Accuracy is about " + str(round(wins / total * 100, 2)) + "%\n")

if __name__ == '__main__':
    buildModel(0.9998, [])