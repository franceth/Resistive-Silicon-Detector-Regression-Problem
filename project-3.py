import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics.pairwise import paired_distances
from sklearn.preprocessing import StandardScaler
import csv
from sklearn.model_selection import GridSearchCV
from sklearn.metrics._scorer import make_scorer
from sklearn.svm import SVR
from sklearn.multioutput import MultiOutputRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import KFold
from sklearn.model_selection import ParameterGrid
from scipy.stats import zscore

def custom_loss_func(ground_truth, predictions):
    return np.sum(paired_distances(ground_truth, predictions))/len(ground_truth)


def main():
    df = pd.read_csv('development.csv', sep=',')

    # print(df.dtypes)
    # print(df.isna().any(axis=0)) # no null values
    # positions = df[['x', 'y']]
    # x_values = positions['x'].unique()
    # y_values = positions['y'].unique()
    # fig, ax = plt.subplots(figsize = (8,8))
    # ax.scatter(x_values, y_values)
    # plt.show()
    # print(len(x_values))
    # print(len(y_values))

    #Data preprocessing
    pmax = [f'pmax[{i}]' for i in range(18)]
    means = df[pmax].mean(axis=0)

    for i in range(6):
        means.drop(means.index[means.argmax()], inplace=True)

    negpmax = [f'negpmax[{i}]' for i in range(18)]
    means = df[negpmax].mean(axis=0)

    for i in range(6):
        means.drop(means.index[means.argmin()], inplace=True)

    area = [f'area[{i}]' for i in range(18)]
    means = df[area].mean(axis=0)
    for i in range(6):
        means.drop(means.index[means.argmax()], inplace=True)

    tmax = [f'tmax[{i}]' for i in range(18)] 
    means = df[tmax].mean(axis=0)
    # print(means)  # the readings 5, 10, 13, 15, 16, 17 occur with the same delay, which seems suspect as pads are in different positions 
    # print(std)                # in the sensor, so we expect that they detect the positive peak at different times
    
    rms = [f'rms[{i}]' for i in range(18)] # maybe remove rms
    means = df[rms].mean(axis=0)
    # print(means) # apart from readings 16 and 17, there are not noticeable differences, maybe because of the impulsive nature of the noise
                    # as seen with the large values of pmax on the suspect readings
    
    # try to plot graphs to show outliers as noise
    
    #Detecting noise fiels
    noise_pmax = []
    noise_negpmax = []
    noise_area = []
    noise_tmax = []
    noise_rms = []
    for i in [0, 7, 12, 15, 16, 17]: 
        noise_pmax.append(f'pmax[{i}]')
        noise_negpmax.append(f'negpmax[{i}]')
        noise_area.append(f'area[{i}]')
        # noise_tmax.append(f'tmax[{i}]')
       
    for i in range(0, 18): 
        noise_rms.append(f'rms[{i}]')
        noise_tmax.append(f'tmax[{i}]')

    # for i in [0, 2, 5, 7, 10, 11, 12, 13 , 14, 15, 16, 17]: 
    #     noise_tmax.append(f'tmax[{i}]')

    noise = noise_pmax + noise_negpmax + noise_area + noise_tmax + noise_rms
    df.drop(columns=noise, inplace=True)

    #custom_scorer = make_scorer(custom_loss_func, greater_is_better=False)
    #param_grid = {'n_estimators': [50, 75, 100],
    #          'criterion': ['squared_error'],
    #          'max_features': ['sqrt', 'log2'],
    #          'random_state': [42],
    #          'n_jobs': [-1]      
    #}

    df_eval = pd.read_csv('evaluation.csv', sep=',')
    df_eval.drop(columns=noise, inplace=True)
    #creation of train set and test set 
    X_train = df.drop(columns=['x', 'y']).values
    y_train = df[['x', 'y']].values
    X_test = df_eval.drop(columns='Id').values

    #creation Regressor
    reg = RandomForestRegressor(n_estimators = 200, criterion='squared_error', max_features='sqrt', random_state=42, n_jobs=-1)
    reg.fit(X_train, y_train)                    
    y_pred = reg.predict(X_test)                         

    #output
    header = ['Id', 'Predicted']
    with open("submission.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in df_eval['Id']:
            writer.writerow([i, ''.join((str(y_pred[i, 0]), '|', str(y_pred[i, 1])))])  # str(round(y_pred[i, 0], 1)
    
if __name__ == "__main__":
    main()
