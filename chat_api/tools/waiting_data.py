### in this file we are contacint OECD API service to pull data 

import requests
import json
import pandas as pd
import numpy as np
from requests.exceptions import MissingSchema
from langchain_community.graphs import Neo4jGraph
import settings as s




#EXAMPLE of OECD API Query. We want to be able to select medical procedure and country and calculate average waiting time
# from specialist assessment to treatment. Data used is from period between 2018 and 2022
url_no_country= 'https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/.WAIT_MEAN.............WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'

#below example for Denmark only, average waiting time, only for hip replacement procedure, 
# for data starting from 2018, and with json data format
url_dnk='https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/DNK.WAIT_MEAN..CM8151_8153...........WTSP...?format=jsondata&startPeriod=2018&dimensionAtObservation=AllDimensions'

#to add countries (estonia, denmark example,startPeriod=2018)
#https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,DSD_HEALTH_PROC@DF_WAITING,1.0/EST+DNK.WAIT_MEAN.............WTSP...?dimensionAtObservation=AllDimensions



#medical prcedure names are long, therefore we will rename it 
pro_name=np.array(['Artery bypass', 'Hip replacement', 'Hysterectomy', 'Knee replacement', 'Prostatectomy', 'Cataract surgery'])


procedure_pairs=[('Artery bypass', 'CM361'), ('Hip replacement', 'CM8151_8153'), ('Hysterectomy', 'CM683_687_689'), ('Knee replacement', 'CM8154'), ('Prostatectomy', 'CM603_606'), ('Cataract surgery', 'CM36_TRS')]
country_pairs=[('chile', 'CHL'), ('costa rica', 'CRI'), ('poland', 'POL'), ('finland', 'FIN'), ('new zealand', 'NZL'), ('united kingdom', 'GBR'), ('netherlands', 'NLD'), ('denmark', 'DNK'), ('italy', 'ITA'), ('hungary', 'HUN'), ('australia', 'AUS'), ('estonia', 'EST'), ('spain', 'ESP'), ('portugal', 'PRT'), ('sweden', 'SWE'), ('norway', 'NOR'), ('lithuania', 'LTU')]
#%%

def get_waiting_time_country_procedure(procedure=str, country=None) -> int | str: 
    result=''
    url=''
    vals=[]
    procedure_pairs=[('Artery bypass', 'CM361'), ('Hip replacement', 'CM8151_8153'), ('Hysterectomy', 'CM683_687_689'), ('Knee replacement', 'CM8154'), ('Prostatectomy', 'CM603_606'), ('Cataract surgery', 'CM36_TRS')]
    country_pairs=[('chile', 'CHL'), ('costa rica', 'CRI'), ('poland', 'POL'), ('finland', 'FIN'), ('new zealand', 'NZL'), ('united kingdom', 'GBR'), ('netherlands', 'NLD'), ('denmark', 'DNK'), ('italy', 'ITA'), ('hungary', 'HUN'), ('australia', 'AUS'), ('estonia', 'EST'), ('spain', 'ESP'), ('portugal', 'PRT'), ('sweden', 'SWE'), ('norway', 'NOR'), ('lithuania', 'LTU')]
    pro_code=''
    for pro in procedure_pairs:
        if pro[0].lower()==procedure.lower():
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

    #print(url)
    try:
        response = requests.get(url)
        response = response.json()
        extract_vals =response['data']['dataSets'][-1]['observations']
        vals=[float(val[0]) for val in extract_vals.values()]
        #print(vals)
        result = sum(vals)/len(vals)
    except MissingSchema:
        print('URL is incorrect. Please check spelling or if country you entered is part of our database')
        result=0.0
    except json.decoder.JSONDecodeError:
    #we need to round up the number since days cannot be in decimals 
        print(f"There is no available data for {country}")
        result = 0.0
    return f"{round(result,0)} days"



def _get_current_hospitals() ->list[str]:
    graph = Neo4jGraph(url=s.SETTINGS["NEO4J_URI"], username=s.SETTINGS["NEO4J_USERNAME"], password=s.SETTINGS["NEO4J_PASSWORD"])

    current_hospitals = graph.query(""" MATCH (h:Hospital)
                                    RETURN h.name AS hospital_name
                                     """)

    return [h['hospital_name'].lower() for h in current_hospitals]



def _get_current_wait_times_minutes(hospital):
    current_hospitals =_get_current_hospitals()
    if hospital.lower() not in current_hospitals:
        return -1
    return np.random.randint(0, 600)


def get_current_wait_times(hospital: str) ->str:
    wait_time = _get_current_wait_times_minutes(hospital)
    if wait_time==-1:
        return f"{hospital} does not exists"

    hours, minutes = divmod(wait_time, 60)

    if hours>0:
        return f"{hours} hours and {minutes} minutes"
    else:
        return f"{minutes} minutes"


def get_most_available_hospital() -> dict[str, float]:
    current_hospitals=_get_current_hospitals()

    current_wait_time = [_get_current_wait_times_minutes(h) for h in current_hospitals]

    best_idx = np.argmin(current_wait_time)
    best_hospital = current_hospitals[best_idx]
    best_wait_time = current_wait_time[best_idx]

    return {best_hospital: best_wait_time}

#test
#get_current_wait_times('fake hospital')



#get_waiting_time_country_procedure('knee replacement', 'poland')

#get_most_available_hospital()

