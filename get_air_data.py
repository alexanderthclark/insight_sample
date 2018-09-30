
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


# In[60]:


list(CO['total'])
Pollutants


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

