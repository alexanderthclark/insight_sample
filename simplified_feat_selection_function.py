
# coding: utf-8

# In[ ]:


### Use random forests to select important features
### Iterative feature selection is used based on var importance

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV


#finds important features according to an importance threshold
#runs two trees iteratively

def get_important_ft(df, x_columns, y_column, thresh1, thresh2):
    
    X_train, X_test, y_train, y_test = train_test_split(df[x_columns], df[y_column], test_size=0.28)

    param_grid1 = {
    'bootstrap': [True],
    'max_depth': [5,10,20],
    #'max_features': [],
    'min_samples_leaf': [4,8],
    'min_samples_split': [3,8],
    'n_estimators': [90]}
    
    # Create a model
    rf1 = RandomForestRegressor()
    # Instantiate the grid search model
    grid_search1 = GridSearchCV(estimator = rf1, param_grid = param_grid1, 
                          cv = 3, n_jobs = -1, verbose = 2)

    grid_search1.fit(X_train, y_train)
    best_param1 = grid_search1.best_params_ 
    
    #train with best params for best features
    forest = RandomForestRegressor(max_depth = best_param1['max_depth'], 
                                   min_samples_split=best_param1['min_samples_split'],
                                   min_samples_leaf=best_param1['min_samples_leaf'], 
                                   n_estimators = best_param1['n_estimators'], 
                                   random_state = 1)

    my_forest = forest.fit(X_train, y_train)
    Xfeat = np.asarray(x_columns)
    x_columns2 = Xfeat[[my_forest.feature_importances_> thresh1]]

    #tune and run a second tree

    X_train2, X_test2, y_train2, y_test2 = train_test_split(df[x_columns2], df[y_column], test_size=0.28)

    
    # Create a model
    rf2 = RandomForestRegressor()
    # Instantiate the grid search model
    grid_search2 = GridSearchCV(estimator = rf2, param_grid = param_grid1, 
                          cv = 3, n_jobs = -1, verbose = 2)

    grid_search2.fit(X_train2, y_train2)
    best_param2 = grid_search2.best_params_
    
    forest2 = RandomForestRegressor(max_depth = best_param2['max_depth'], 
                                   min_samples_split=best_param2['min_samples_split'],
                                   min_samples_leaf=best_param2['min_samples_leaf'], 
                                   n_estimators = best_param2['n_estimators'], 
                                   random_state = 1)

    my_forest2 = forest2.fit(X_train2, y_train2)
    Xfeat2 = np.asarray(x_columns2)
    Xfeat2[[my_forest2.feature_importances_> thresh2]]
    return list(Xfeat2)

