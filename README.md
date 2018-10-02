# insight_sample
This repository houses selections from my Insight project.

## Project Overview

I tried to find predictors of sleeplessness (as a continuous response variable, minutes sleepless) to help advise changes in behavior. The American Time Use Survey offers by-the-minute data for a particular user for a day (and unfortunately only one day). So I can observe how much time a user spent sleepless (this is a category of activity) and see what other activities throughout the day are associated with higher levels of sleeplessness. I also pulled in data on air quality and temperature from the EPA to see to what degree daily fluctations in these factors can influence a person's sleep. 


### data_assembly
*data_assembly.py* pulls EPA data from the web on daily levels of pollution and temperature and time use data from the BLS.

I've set the defaults in the file to download less data than I used for my project. This is done for speed.

See https://www.bls.gov/tus/ for additional documentation and data on the American Time Use Survey.

See https://www.ipums.org/ for an ATUS data extract system. 

### feature selection
*simplified_feat_selection_function.py* is a function that runs two random forests to give a list of features that meet an importance threshold. I also used lasso regularization on a dataset that dropped the users not experiencing sleeplessness. 

### tobit to accommodate censored data
Because the sleeplessness level for a user is censored from below at zero, I use a tobit regression to predict a latent sleeplessness score. I have provided *tobit_reg.py* for this, but I strongly discourage using Python for running a tobit regression if you are unconstrained. 

## How to Run

*data_assembly.py* is the only input needed. However, more feature engineering/selection will be needed. *simplified_feat_selection_function.py* can help determine important features or off-the-shelf regularization like Lasso or elastic net could be used. Interaction variables should be considered. Once a list of features is selected, this can be input in *tobit_reg.py* to obtain the marginal effects. 
