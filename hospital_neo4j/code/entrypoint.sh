#! /bin/bash

echo "Running ETL to move hospital data from csv to neo4j"

python bulk_write_neo4j.py
