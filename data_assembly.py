###This file gather daily air data and time use data.
###We match air data to time use on date.
###Produces a dataframe of a user's time use on a diary day.
###Features include
        #Pollution levels and temp on a day
        #Time spent on activities throughout a day
        #Time spent on activities before bed



import pandas as pd
import requests, zipfile, io



#first year to be considered
#between 2003 and 2016
t0 = 2003 

#last year to be considered 
#set to 2004 to make this run faster
#can go to 2016
T = 2004 + 1 

#We will gather daily pollution data for these years
years = range(t0, T) 

#this is a list for naming dataframes giving the daily levels of a pollutant/particulate
#I know Temperature isn't a pollutant
pollutant_list = ['NO2', 'Ozone', 'SO2', 'CO', 'PMFRM', 'PMnonFRM', 'PM10', 'PM25S', 'PM10S', 'Temperature']

#here we create a dictionary that gives the corresponding name for the pollutant per EPA URL naming conventions
Pollutants = { "NO2":42602, "Ozone":44201,"SO2":42401,"CO":42101,
              "PMFRM":88101, "PMnonFRM":88502,"PM10":81102,
              "PM25S":"SPEC", "PM10S":"PM10SPEC", "Temperature":"TEMP"}




#we create empty dictionaries for every pollutant and assemble into a list
NO2, Ozone, SO2, CO, PMFRM, PMnonFRM, PM10, PM25S, PM10S, Temperature = [{} for _ in range(10)]
pollutant_dicts = [NO2, Ozone, SO2, CO, PMFRM, PMnonFRM, PM10, PM25S, PM10S, Temperature]
#must stay in the same order as in the Pollutants dictionary




##creates pollution dataframes
for dicti, pollutant in zip(pollutant_dicts, Pollutants): 
    
    for y in years:
        url = 'https://aqs.epa.gov/aqsweb/airdata/daily_' + str(Pollutants[str(pollutant)]) + '_' + str(y)+ '.zip'
        ending = 'daily_' + str(Pollutants[pollutant]) + '_' + str(y) + '.csv'
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall()
        dicti[y] = pd.read_csv(z.open(ending))
        dicti[y] = dicti[y][dicti[y]['City Name']=='Los Angeles']
        
    for y in range((t0+1),T):
        dicti['total'] = dicti[2003]
        dicti['total'] = dicti['total'].append(dicti[y])




#we only need to pick two variables
pick = ['Date Local', 'Arithmetic Mean']

for dicti, name in zip(pollutant_dicts, pollutant_list):
    #Just need two variables, the pollution reading and the date
    dicti['total'] = dicti['total'][pick]
    
    #convert to date time
    dicti['total']['Date Local'] = pd.to_datetime(dicti['total']['Date Local'])
    
    #sort for merge
    dicti['total'] = dicti['total'].sort_values('Date Local')
    
    #rename to preserve identity in merge
    dicti['total'] = dicti['total'].rename(columns={'Arithmetic Mean': name})




#Merge all pollution data into one df. 
#Readings are near daily, so I use a nearest date merge

df_pollution = pd.merge_asof(CO['total'], NO2['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, Ozone['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, PM10['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, PM10S['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, PM25S['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, PMFRM['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, PMnonFRM['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, SO2['total'], on='Date Local', direction='nearest')
df_pollution = pd.merge_asof(df_pollution, Temperature['total'], on='Date Local', direction='nearest')

#pollution by itself
#df_pollution.to_csv('df_pollution.csv')



#Downloaded from IPUMS
#this tells me who is in LA
url = 'https://sites.google.com/site/alexanderthclark/ATUX_LA.csv?attredirects=0&d=1'
df_LA = pd.read_csv(url)
#df_LA = pd.read_csv('atux_LA.csv') local

#we only need the ID numbers to link to the other dataset. 
df_LA = df_LA[['caseid']]




##Import time use data from 2003 to 2016

#these are the names of the datasets available from ATUS
#respondent, summary, and activity files
files = ['resp', 'sum', 'act']
#["resp", "rost", "sum", "act", "cps", "who"]

ATUS = {}

for file in files:
    url = 'https://www.bls.gov/tus/special.requests/atus'+ str(file)+ '_0316.zip'
    ending = 'atus' + str(file) + '_0316' + '.dat'
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()
    ATUS[file] = pd.read_csv(z.open(ending))



#merge to reduce to LA people
sum_LA = pd.merge(df_LA, ATUS['sum'], left_on='caseid', right_on='TUCASEID')
resp_LA = pd.merge(df_LA, ATUS['resp'],left_on='caseid', right_on='TUCASEID')
act_LA = pd.merge(df_LA, ATUS['act'], left_on='caseid', right_on='TUCASEID')

#select ID, date, and wage information
resp_LA = resp_LA[['TUCASEID', 'TUDIARYDATE', 'TUMONTH', 'TRERNHLY', 'TUYEAR']]

nrow= resp_LA.shape[0]
#get diary date as datetime
for row in range(0,nrow):
    string = str(resp_LA.loc[resp_LA.index[row],'TUDIARYDATE'])
    new = string[0:4]+'-'+string[4:6]+'-'+string[6:8]
    resp_LA.loc[resp_LA.index[row],'Date2'] = new
    
resp_LA['Date2'] = pd.to_datetime(resp_LA['Date2'])




#The summary file is of interest because it gives total time
#spent on activities throughout the day
#we drop unnecessary features

summary_features = list(sum_LA)
unnec_sum_features = ['Unnamed: 0',
                     'caseid',
                     'county',
                     'GEMETSTA',
                     'GTMETSTA',
                     'PEHSPNON',
                     'PTDTRACE',
                     'TELFS',
                     'TEMJOT',
                     'TESCHENR',
                     'TESCHLVL',
                     'TESEX',
                     'TESPEMPNOT',
                     'TRCHILDNUM',
                     'TRDPFTPT',
                     'TRHOLIDAY',
                     'TRSPFTPT',
                     'TRSPPRES',
                     'TRYHHCHILD',
                     'TUDIARYDAY',
                     'TUFNWGTP',
                     'TEHRUSLT',
                     'TUYEAR']

relevant_sum_features = list ( set(summary_features) - set(unnec_sum_features) )
#now this only includes basic controls and time use activities




#Get a list of all the people in LA
LA_people = set(resp_LA['TUCASEID']) #get a list of the unique case IDs
LA_list = list(LA_people)

#Pivot the activity dataframe by user
#This is necessary toward goal of identifying activities before bed
Piv_act = {}

for person in LA_list:
    Piv_act[person] = act_LA[act_LA['TUCASEID']==person].pivot(columns='TRCODEP', values=['TUSTARTTIM','TUACTDUR'])




## Because we are concerned with time use that affects
## sleep and sleeplessness, we identify users who slept, etc

#no sleep
no_sleep = sum_LA['t010101']==0
no_sleepers = list( sum_LA[no_sleep]['TUCASEID'] )

#slept
LA_sleepers = list( set(LA_list)-set(no_sleepers) )




#tried to sleep
no_sleep_or_sleepless = sum_LA['t010101'] + sum_LA['t010102'] > 0

#tried to sleep list
LA_universe = list( sum_LA[no_sleep_or_sleepless]['TUCASEID'] )




#could not sleep but tried
only_sleepless = sum_LA['t010102'] > 0
only_sleepless_list = list( sum_LA[no_sleep & only_sleepless]['TUCASEID'] )




#I want to identify the time use across various activities that precede sleeping
#I find how_far_back many activities that precede the final event of sleeping
#we are flattening the activity file insofar as this produces a new 
#dataframe with one row for each user instead of multiple per user


#Activities before bed are not prefixed with a 't'
#Activity throughout the day is prefixed with a 't'
#See BLS documentation for variable dictionary

how_far_back = 4
Flat_act = {}

for person in sorted(LA_sleepers):
    idx = Piv_act[person]['TUSTARTTIM'].index.get_loc(Piv_act[person]['TUSTARTTIM'][[10101]].last_valid_index())
    # slice rows (with some minor bounds checking)
    activities_before_bed = Piv_act[person]['TUACTDUR'].iloc[max(0, idx - how_far_back):idx + 1]
    activities_before_bed['dummy'] = 1
    activities_before_bed = activities_before_bed.fillna(0)
    Flat_act[person] =  activities_before_bed.groupby('dummy').max()




#same as above but for people who tried but couldn't sleep

for person in sorted(only_sleepless_list):
    idx = Piv_act[person]['TUSTARTTIM'].index.get_loc(Piv_act[person]['TUSTARTTIM'][[10102]].last_valid_index())
    # slice rows (with some minor bounds checking)
    activities_before_bed = Piv_act[person]['TUACTDUR'].iloc[max(0, idx - how_far_back):idx + 1]
    activities_before_bed['dummy'] = 1
    activities_before_bed = activities_before_bed.fillna(0)
    Flat_act[person] =  activities_before_bed.groupby('dummy').max()



#put this activity into a new df

sum_before_bed = Flat_act[LA_universe[0]]

for person in sorted(LA_universe):
    Flat_act[person]['TUCASEID'] = person
    sum_before_bed = sum_before_bed.append(Flat_act[person])




#create the df we will run the model with 
#combines time use throughout the day and before bed + demographics
df_run = pd.merge(resp_LA, sum_LA[relevant_sum_features],on='TUCASEID')
df_run = pd.merge(df_run, sum_before_bed, on='TUCASEID')




#time use by itself
#df_run.to_csv('df_run.csv')




#sort for a merge
df_run = df_run.sort_values('Date2')

#now we can merge these for pollution+time use
master_df = pd.merge_asof(df_run[df_run['TUYEAR'] < T], df_pollution, left_on='Date2', right_on='Date Local', direction='nearest')




master_df.to_csv('master_df.csv')
