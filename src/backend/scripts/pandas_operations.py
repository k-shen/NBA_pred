import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
from constants import DATAFILE

def getDataAndTargets(deselected):
    data_file = pd.read_csv(DATAFILE)
    targets = list(data_file['PTS'])
    data = combineMatchup(data_file, deselected)

    return data, targets

def combineMatchup(data_file, deselected):
    data = deselectColumns(data_file, deselected)
    combined_data = []

    iterator = 0
    while iterator + 1 < len(data):
        combined_data.append(list(data.iloc[iterator]) + list(data.iloc[iterator + 1]))
        combined_data.append(list(data.iloc[iterator + 1]) + list(data.iloc[iterator]))
        iterator += 2

    return combined_data

def processRows(self_row, opp_row, columns):
    row_dict = {}
    
    for col in columns:
        if col[0:4] == 'OPP_':
            row_dict[col] = opp_row[col[4:]]
        else:
            row_dict[col] = self_row[col]
    
    return row_dict

def deselectColumns(data_file, columns_to_skip):
    data = data_file.drop('PTS', axis=1).drop('TEAM', axis=1)
    for skip in columns_to_skip:
        data = data.drop(skip, axis=1)

    return data

if __name__ == '__main__':
    print()
    getDataAndTargets([])
    