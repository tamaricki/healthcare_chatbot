
import polars as pl
import settings as s

hospitals_path=s.SETTINGS["HOSPITALS_CSV_PATH"]
patients_path =s.SETTINGS["PATIENTS_CSV_PATH"]
payers_path=s.SETTINGS["PAYERS_CSV_PATH"]
physicians_path= s.SETTINGS["PHYSICIANS_CSV_PATH"]
reviews_path=s.SETTINGS["REVIEWS_CSV_PATH"]
visits_path=s.SETTINGS["VISITS_CSV_PATH"]


#data = pl.read_csv(patients_path)


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


#with GraphDatabase.driver(neo4juri, auth=AUTH) as driver:
 #   driver.verify_connectivity()


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
    with driver.session(database="neo4j") as session:
        for node in NODES:
            session.execute_write(set_uniqueness_constrains, node)

    LOGGER.info("Loading hospital nodes")
    with driver.session(database="neo4j") as session:
        query=f"""LOAD CSV WITH HEADERS
                FROM '{hospitals_path}' AS hospitals
                MERGE (h:Hospital {{id: toInteger(hospitals.hospital_id),
                                    name: hospitals.hospital_name,
                                    state: hospitals.hospital_state}});"""

        _ = session.run(query, {})

    LOGGER.info("loading payer nodes")
    with driver.session(database="neo4j") as session:
        query=f""" LOAD CSV WITH HEADERS
                FROM '{payers_path}' AS payers
                MERGE (p:Payer {{id: toInteger(payers.payer_id),
                                name: payers.payer_name}});"""
        _=session.run(query, {})

    LOGGER.info("loading physicians nodes")
    with driver.session(database="neo4j") as session:
        query=f"""LOAD CSV WITH HEADERS
                FROM '{physicians_path}' AS physicians
                MERGE (p:Physician {{id: toInteger(physicians.physician_id),
                                    name: physicians.physician_name,
                                    dob: physicians.physician_dob,
                                    grad_year: physicians.physician_grad_year,
                                    school: physicians.medical_school,
                                    salary: physicians.salary}});
                """

        _=session.run(query, {})

    LOGGER.info("loading visit nodes")
    with driver.session(database="neo4j") as session:
        query=f"""LOAD CSV WITH HEADERS
            FROM '{visits_path}' AS visits
            MERGE (v: Visit{{id: toInteger(visits.visit_id),
                            room_number: toInteger(visits.room_number),
                            admission_type:visits.admission_type,
                            admission_date: visits.date_of_admission,
                            test_results: visits.test_results,
                            status: visits.visit_status}})
                ON CREATE SET v.chief_complaint = visits.chief_complaint
                ON MATCH SET  v.chief_complaint = visits.chief_complaint
                ON CREATE SET v.treatment_description= visits.treatment_description
                ON MATCH SET v.treatment_description= visits.treatment_description
                ON CREATE SET v.diagnosis = visits.primary_diagnosis
                ON MATCH SET v.diagnosis = visits.primary_diagnosis
                ON CREATE SET v.discharge_date = visits.discharge_date
                ON MATCH SET v.discharge_date = visits.discharge_date
        """

        _= session.run(query, {})

    LOGGER.info('loading patient nodes')
    with driver.session(database="neo4j") as session:
        query=f"""LOAD CSV WITH HEADERS
            FROM '{patients_path}' AS patients
            MERGE (p: Patient{{id: toInteger(patients.patient_id),
                    sex: patients.patient_sex,
                    dob: patients.patient_dob,
                    blood_type: patients.patient_blood_type}});
                    """
        _=session.run(query, {})
    


    LOGGER.info('Loading review nodes')
    with driver.session(database="neo4j") as session:
        query=f""" LOAD CSV WITH HEADERS
            FROM '{reviews_path}' AS reviews
            MERGE (r: Review{{id: toInteger(reviews.review_id),
                    text: reviews.review,
                    physician_name: reviews.physician_name,
                    hospital_name: reviews.hospital_name}})"""


        _=session.run(query, {})
    

    LOGGER.info('loading AT relationships')
    with driver.session(database="neo4j") as session:
        query=f"""LOAD CSV WITH HEADERS FROM '{visits_path}' AS row
                MATCH (source: Visit {{id: toInteger(trim(row.visit_id))}})
                MATCH (target: Hospital {{id: toInteger(trim(row.hospital_id))}})
                MERGE (source)-[r:AT]->(target) 
                """

        _=session.run(query, {})

    LOGGER.info('Loading WRITES relationships')
    with driver.session(database="neo4j") as session:
        query= f""" LOAD CSV WITH HEADERS FROM '{reviews_path}' AS reviews
                MATCH (v:Visit {{id: toInteger(reviews.visit_id)}})
                MATCH (r: Review {{id: toInteger(reviews.review_id)}})
                MERGE (v)-[writes:WRITES] ->(r) """

        _=session.run(query, {})

    LOGGER.info("loading 'TREATS' relationships ")
    with driver.session(database="neo4j") as session:
        query = f""" LOAD CSV WITH HEADERS FROM '{visits_path}' AS visits
                MATCH (p: Physician {{id: toInteger(visits.physician_id)}})
                MATCH (v: Visit {{id: toInteger(visits.visit_id)}})
                MERGE (p)-[treats:THREATS] ->(v)
                """
        _=session.run(query, {})
    

    LOGGER.info("loading 'COVERED_BY' relationships ")
    with driver.session(database="neo4j") as session:
        query = f""" LOAD CSV WITH HEADERS FROM '{visits_path}' AS visits
                MATCH (v: Visit {{id: toInteger(visits.visit_id)}}) 
                MATCH (p: Payer {{id: toInteger(visits.payer_id)}})
                MERGE (v)-[covered_by: COVERED_BY]->(p)
                ON CREATE SET
                    covered_by.service_date = visits.discharge_date,
                    covered_by.billing_amount= toFloat(visits.billing_amount)
                """
        _=session.run(query, {})

    LOGGER.info("loading 'HAS' relationships ")
    with driver.session(database="neo4j") as session:
        query=f""" LOAD CSV WITH HEADERS FROM '{visits_path}' AS visits
                MATCH (p: Patient {{id: toInteger(visits.patient_id)}})
                MATCH (v: Visit {{ id:toInteger(visits.visit_id)}}) 
                MERGE (p)-[has:HAS]->(v)
                """
        _=session.run(query, {})

    LOGGER.info("loading 'EMPLOYS' relationships ")
    with driver.session(database="neo4j") as session:
        query = f""" LOAD CSV WITH HEADERS FROM '{visits_path}' AS visits
                MATCH (h: Hospital {{id: toInteger(visits.hospital_id)}})
                MATCH (p: Physician {{id: toInteger(visits.physician_id)}})
                MERGE (h)-[employs:EMPLOYS]->(p)
                 """
        _=session.run(query, {})


if __name__=='__main__':
    load_hospital_graph_from_csv()






