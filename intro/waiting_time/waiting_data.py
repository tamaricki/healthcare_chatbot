### in this file we are contacint OECD API service to pull data 
#%%

import requests
import json
import pandas as pd
#%%

url= 'https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/.WAIT_MEAN.............WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'


#to add countries (estonia, denmark example,startPeriod=2018)
#https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/EST+DNK.WAIT_MEAN.............WTSP...?dimensionAtObservation=AllDimensions

response = requests.get(url)
response=response.json()

# %%
response['data']['structures'] #['dimensions']['observation']
# %%
data = pd.read_csv('OECD_waiting_time.csv')

data.info()
# %%
response.status_code
# %%
data.sample(6)
# %%
#there are lot of duplicate columns so we need to reduce 