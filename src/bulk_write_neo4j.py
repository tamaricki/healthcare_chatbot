
import settings as s
import polars as pl

hospitals_path='../data/hospitals.csv'
patients_path ='../data/patients.csv'
payers_path='../data/payers.csv'
physicians_path= '../data/physicians.csv'
reviews_path='../data/reviews.csv'
visits_path='../data/visits.csv'

#example of dimension table =small tables containing info about attributes that provide
#context data in the fact tables. dimension and fact tables are part of star schema when working with
#sql dbs

#hosp = pl.read_csv(hospitals_path)
#print(hosp.shape) #(30,3)

#similarly physicians is also dimension table

#physic = pl.read_csv(physicians_path)
#print(physic.shape)
#print(physic.sample(6))


#oposite of dimensio are fact tables :
#visits = pl.read_csv(visits_path)
#print(visits.shape)
#print(visits.sample(6))
#print(visits.columns)

#SEtup Neo4J DB graph databases Neo4j AuraDB. then move the hospital system into it and then 
#query it 
#we add uri username and password as  our venv variable 

import os 
from neo4j import GraphDatabase
import logging
from retry import retry

URI=os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4jpass = os.getenv("NEO4J_PASSWORD")
AUTH = (neo4j_user, neo4jpass)


with GraphDatabase.driver(neo4juri, auth=AUTH) as driver:
    driver.verify_connectivity()


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

LOGGER= logging.getLogger(__name__)

NODES=["Hospital", "Payer", "Physician", "Patient", "Visit", "Review"]


def set_uniqueness_constrains(tx,node):
    query =f"""CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node}) REQUIRE n.id IS UNIQUE;"""
    _= tx.run(query,{})

@retry(tries=100, delay=10)
def load_hospital_graph_from_csv() -> None:
    """ Load structured hospital csv data following a specific ontology into Neo4j"""

    driver = GraphDatabase.driver(URI, auth=AUTH)

    LOGGER.info('Setting uniqueness constrains on nodes')
    with driver.sesion(database="neo4j") as session:
        for node in NODES:
            session.execute_write(set_uniqueness_constrains, node)

    LOGGER.info("Loading hospital nodes")
    with driver.session(database="neo4j") as session:
        query=f"""LOAD CSV WITH HEADERS
                FROM {hospitals_path} AS hospitals
                MERGE (h:Hospital {{id: toInteger(hostpitals.hostpital_id),
                                    name: hospitals.hospital_name,
                                    state: hospitals.hospital_state}});"""

        _ = session.run(query, {})

    LOGGER.info("loading payer nodes")
    with driver.session(database="neo4j") as session:
        query=f""" LOAD CSV WITH HEADERS
                FROM {patients_path} AS payers
                MERGE (p:Payer {{id: toInteger(payers.payer_id),
                                name: payers.payer_name}});"""
        _=session.run(query, {})

    LOGGER.info("loading physicians nodes")


    #...

    LOGGER.info("loading visit nodes")

    #...

    LOGGER.info('loading patient nodes')

    #...


    LOGGER.info('Loading review nodes')

    #...

    LOGGER.info('loading AT relationships')

    #... 

    LOGGER.info('Loading WRITES relationships')

    #....

    LOGGER.info("loading 'TREATS' relationships ")

    #...

    LOGGER.info("loading 'COVERED_BY' relationships ")

    #...

    LOGGER.info("loading 'HAS' relationships ")

    #...

    LOGGER.info("loading 'EMPLOYS' relationships ")

    #...


if __name__=='__main__':
    load_hospital_graph_from_csv()






