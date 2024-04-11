#%%
import settings as s
import polars as pl
#we will simply used files which are in data folder, .env.default and settings will not be used 
#in reality these are all tables of db and it is not recommended that are publicly accessible

hospitals_path='../data/hospitals.csv'
patients_path ='../data/patients.csv'
payers_path='../data/payers.csv'
physicians_path= '../data/physicians.csv'
reviews_path='../data/reviews.csv'
visits_path='../data/visits.csv'


# %%
#example of dimension table =small tables containing info about attributes that provide
#context data in the fact tables. dimension and fact tables are part of star schema when working with
#sql dbs

hosp = pl.read_csv(hospitals_path)
print(hosp.shape) #(30,3)

#similarly physicians is also dimension table

physic = pl.read_csv(physicians_path)
print(physic.shape)
print(physic.sample(6))

# %%
#example of dimension table =small tables containing info about attributes that provide
#context data in the fact tables

# %%
