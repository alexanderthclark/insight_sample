
# coding: utf-8

# In[52]:


###This file gather 


# In[53]:


import pandas as pd
import requests, zipfile, io


# In[54]:


#first year to be considered
t0 = 2003 

#last year to be considered
T = 2004 + 1 

#We will gather daily pollution data for these years
years = range(t0, T) 

#this is a list for naming dataframes giving the daily levels of a pollutant/particulate
#pollutant_list = ['NO2', 'Ozone', 'SO2', 'CO', 'PMFRM', 'PMnonFRM', 'PM10', 'PM25S', 'PM10S']

#here we create a dictionary that gives the corresponding name for the pollutant per EPA URL naming conventions
Pollutants = { "NO2":42602, "Ozone":44201,"SO2":42401,"CO":42101,
              "PMFRM":88101, "PMnonFRM":88502,"PM10":81102,
              "PM25S":"SPEC", "PM10S":"PM10SPEC", "Temperature":"TEMP"}


# In[57]:


#we create empty dictionaries for every pollutant and assemble into a list
NO2, Ozone, SO2, CO, PMFRM, PMnonFRM, PM10, PM25S, PM10S, Temperature = [{} for _ in range(10)]
pollutant_dicts = [NO2, Ozone, SO2, CO, PMFRM, PMnonFRM, PM10, PM25S, PM10S, Temperature]
#must stay in the same order as in the Pollutants dictionary


# In[58]:


##creates pollution dataframes
for dicti, pollutant in zip(pollutant_dicts, Pollutants): 
    
    for y in years:
        url = 'https://aqs.epa.gov/aqsweb/airdata/daily_' + str(Pollutants[str(pollutant)]) + '_' + str(y)+ '.zip'
        ending = 'daily_' + str(Pollutants[pollutant]) + '_' + str(y) + '.csv'
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall()
        dicti[y] = pd.read_csv(z.open(ending))
        dicti[y] = dict[y][dict[y]['City Name']=='Los Angeles']
        
    for y in range((t0+1),T):
        dicti['total'] = dicti[2003]
        dicti['total'] = dicti['total'].append(dict[y])


# In[59]:


#we only need to pick two variables
pick = ['Date Local', 'Arithmetic Mean']

for dict in pollutant_dicts:
    #Just need two variables, the pollution reading and the date
    dict['total'] = dict['total'][pick]
    
    #convert to date time
    dict['total']['Date Local'] = pd.to_datetime(dict['total']['Date Local'])
    
    #sort for merge
    dict['total'] = dict['total'].sort_values('Date Local')


# In[61]:


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

df_pollution.to_csv('df_pollution.csv')


# In[8]:


#Downloaded from IPUMS
#this tells me who is in LA
df_LA = pd.read_csv('atux_LA.csv')

#we only need the ID numbers to link to the other dataset. 
df_LA = df_LA[['caseid']]


# In[72]:


##Import time use data from 2003 to 2016

#these are the names of the datasets available from ATUS
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


# In[73]:


#merge to reduce to LA people
sum_LA = pd.merge(df_LA, ATUS['sum'], left_on='caseid', right_on='TUCASEID')
resp_LA = pd.merge(df_LA, ATUS['resp'],left_on='caseid', right_on='TUCASEID')
act_LA = pd.merge(df_LA, ATUS['act'], left_on='caseid', right_on='TUCASEID')

#select ID, date, and wage information
resp_LA = resp_LA[['TUCASEID', 'TUDIARYDATE', 'TUMONTH', 'TRERNHLY']]

nrow= resp_LA.shape[0]
#get diary date as datetime
for row in range(0,nrow):
    string = str(resp_LA.loc[resp_LA.index[row],'TUDIARYDATE'])
    new = string[0:4]+'-'+string[4:6]+'-'+string[6:8]
    resp_LA.loc[resp_LA.index[row],'Date2'] = new
    
resp_LA['Date2'] = pd.to_datetime(resp_LA['Date2'])


# In[19]:


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


# In[116]:


#Get a list of all the people in LA
LA_people = set(resp_LA['TUCASEID']) #get a list of the unique case IDs
LA_list = list(LA_people)

#Pivot the activity dataframe by user
#This is necessary toward goal of identifying activities before bed
Piv_act = {}

for person in LA_list:
    Piv_act[person] = act_LA[act_LA['TUCASEID']==person].pivot(columns='TRCODEP', values=['TUSTARTTIM','TUACTDUR'])


# In[101]:


## Because we are concerned with time use that affects
## sleep and sleeplessness, we identify users who slept, etc

#no sleep
no_sleep = sum_LA['t010101']==0
no_sleepers = list( sum_LA[no_sleep]['TUCASEID'])

#slept
LA_sleepers = list(set(LA_list)-set(no_sleepers))


# In[114]:


#tried to sleep
no_sleep_or_sleepless = sum_LA['t010101'] + sum_LA['t010102'] > 0

#tried to sleep list
LA_universe = list( sum_LA[no_sleep_or_sleepless]['TUCASEID'] )


# In[107]:


#could not sleep but tried
only_sleepless = sum_LA['t010102'] > 0
only_sleepless_list = list( sum_LA[no_sleep & only_sleepless]['TUCASEID'])


# In[102]:


#I want to identify the time use across various activities that precede sleeping
#I find how_far_back many activities that precede the final event of sleeping

how_far_back = 4
Flat_act = {}

for person in sorted(LA_sleepers):
    idx = Piv_act[person]['TUSTARTTIM'].index.get_loc(Piv_act[person]['TUSTARTTIM'][[10101]].last_valid_index())
    # slice rows (with some minor bounds checking)
    XX = Piv_act[person]['TUACTDUR'].iloc[max(0, idx - how_far_back):idx + 1]
    XX['dummy'] = 1
    XX = XX.fillna(0)
    Flat_act[person] =  XX.groupby('dummy').max()


# In[109]:


#same as above but for people who tried but couldn't sleep

for person in sorted(only_sleepless_list):
    idx = Piv_act[person]['TUSTARTTIM'].index.get_loc(Piv_act[person]['TUSTARTTIM'][[10102]].last_valid_index())
    # slice rows (with some minor bounds checking)
    XX = Piv_act[person]['TUACTDUR'].iloc[max(0, idx - how_far_back):idx + 1]
    XX['dummy'] = 1
    XX = XX.fillna(0)
    Flat_act[person] =  XX.groupby('dummy').max()


# In[120]:


#put this activity into a new df

sum_before_bed = Flat_act[LA_universe[0]]

for person in sorted(LA_universe):
    Flat_act[person]['TUCASEID'] = person
    sum_before_bed = sum_before_bed.append(Flat_act[person])


# In[121]:


#create the df we will run the model with 
#combines time use throughout the day and before bed + demographics
df_run = pd.merge(resp_LA, sum_LA[relevant_sum_features],on='TUCASEID')
df_run = pd.merge(df_run, sum_before_bed, on='TUCASEID')


# In[122]:


df_run.to_csv('df_run.csv')

