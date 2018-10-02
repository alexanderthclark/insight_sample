import numpy as np
import pandas as pd
import tobit 

#tobit from https://github.com/jamesdj/tobit/blob/master/tobit.py



#read data from data_assembly.py
df = pd.read_csv('master_df.csv')

#from feature_selection
features = ['TEAGE', 't120303', 'PMFRM', 'PM25S', 'PMnonFRM', 'Ozone', 'NO2', 'SO2', 'CO',
 'PM10','PEEDUCA', 'Temperature','Temp_x_Age']

##add interactions to df
df['Temp_x_Age'] = df['Temperature']*df['TEAGE']

##prepare data for regression
x = df[features]

#predict sleeplessness
y = df['t010102']



#Per tobit.py from jamesdj

#Sleeplessness is censored at zero
censored_at=0

cens = pd.Series(np.zeros((len(y),)))
cens[y==censored_at] = -1
cens.value_counts()

#Run a tobit regression
tr = tobit.TobitModel()
tr = tr.fit(x, y, cens, verbose=False)

#print(tr.coef_)




#coefficients!
list( zip(features,list(tr.coef_)) )


print(coefficients)

print('Warning to user: Python does not have a well supported tobit package. \
	What I use here does not allow for (correct) retrieval of the intercept.')

print('Use R or Stata for a final model.')
