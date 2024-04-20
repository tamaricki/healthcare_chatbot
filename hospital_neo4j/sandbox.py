
import os
import settings as s
from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI")
p = os.getenv("NEO4J_PASSWORD")

#print(uri)
#this works but did not work os.getenv("PATIENTS_CSV_PATH")
path = s.SETTINGS["PATIENTS_CSV_PATH"]
print(path)

#driver = GraphDatabase.driver(uri, auth=("neo4j", p))
#drint(driver.verify_connectivity()) #returned none but no error message os it might work
h = s.SETTINGS["HOSPITALS_CSV_PATH"]
print(h)