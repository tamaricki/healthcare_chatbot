### in this file we are contacint OECD API service to pull data 
#%%

import requests
import json
import pandas as pd
import numpy as np
from requests.exceptions import MissingSchema
#%%

url= 'https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/.WAIT_MEAN.............WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'

#below example for Denmark only, average waiting time, only for hip replacement procedure, 
# for data starting from 2018, and with json data format
url_dnk='https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/DNK.WAIT_MEAN..CM8151_8153...........WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'

#to add countries (estonia, denmark example,startPeriod=2018)
#https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/EST+DNK.WAIT_MEAN.............WTSP...?dimensionAtObservation=AllDimensions

response = requests.get(url_dnk)
response=response.json()

# %%
vals=[]
from_api=response['data']['dataSets'][-1]['observations']
for v in from_api.values():
    vals.append(float(v[0]))
r = sum(vals)/len(vals)
print(vals, r)


# %%

dots='.............'
len(dots)
p = '..CM8151_8153...........'
print(len(dots), len(p))
#df_from_api=pd.DataFrame.from_records(from_api)


#%%
data = pd.read_csv('OECD_waiting_time.csv')

data.info()
# %%
#procedure_name=data['Medical procedure'].unique()
procedure_id = data['MEDICAL_PROCEDURE'].unique()
country_name = data['Reference area'].unique()
country_code = data['REF_AREA'].unique()

pro_name=np.array(['Artery bypass', 'Hip replacement', 'Hysterectomy', 'Knee replacement', 'Prostatectomy', 'Cataract surgery'])
c_names = [c.lower() for c in country_name]
country_pairs=list(zip(c_names, country_code))
procedure_pairs=list(zip(pro_name, procedure_id))
#%%
print(procedure_pairs, '\n', country_pairs)
#country_pairs

procedure_pairs1=[('Artery bypass', 'CM361'), ('Hip replacement', 'CM8151_8153'), ('Hysterectomy', 'CM683_687_689'), ('Knee replacement', 'CM8154'), ('Prostatectomy', 'CM603_606'), ('Cataract surgery', 'CM36_TRS')]
country_pairs1=[('chile', 'CHL'), ('costa rica', 'CRI'), ('poland', 'POL'), ('finland', 'FIN'), ('new zealand', 'NZL'), ('united kingdom', 'GBR'), ('netherlands', 'NLD'), ('denmark', 'DNK'), ('italy', 'ITA'), ('hungary', 'HUN'), ('australia', 'AUS'), ('estonia', 'EST'), ('spain', 'ESP'), ('israel', 'ISR'), ('portugal', 'PRT'), ('sweden', 'SWE'), ('norway', 'NOR'), ('lithuania', 'LTU')]

# %%
def get_waiting_time_country_procedure(procedure=str, country=None) -> int | str: 
    result=''
    url=''
    vals=[]
    pro_code=''
    for pro in procedure_pairs:
        if pro[0]==procedure:
            pro_code= pro[1]


    if not country:
        #return url containing only procedure
        url= 'https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/.WAIT_MEAN..{}...........WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'.format(pro_code)

    elif country:
        country_code=''
        for c in country_pairs:
            if c[0]==country.lower():
                country_code=c[1]
                url = 'https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/{}.WAIT_MEAN..{}...........WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'.format(country_code, pro_code)

    print(url)
    try:
        response = requests.get(url)
        response = response.json()
        extract_vals =response['data']['dataSets'][-1]['observations']
        vals=[float(val[0]) for val in extract_vals.values()]
        print(vals)
        result = sum(vals)/len(vals)
    except MissingSchema:
        result = 'URL is incorrect. Please check spelling or if country you entered is part of our database'
    return result



# %%
#there are lot of duplicate columns so we need to reduce 

get_waiting_time_country_procedure('Hysterectomy', 'Costa Rica')
# %%
procedure= 'Hip replacement'
pro_code=''
for pro in procedure_pairs:
    if pro[0]==procedure:
        pro_code= pro[1]
print(pro_code)
url='https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/.WAIT_MEAN..{}...........WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'.format(pro_code)
url
# %%
