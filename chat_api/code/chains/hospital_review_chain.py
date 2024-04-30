
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
import os 
import settings as s 



neo4j_vector_index=Neo4jVector.from_existing_graph(embedding=OpenAIEmbeddings(),
                    url=s.SETTINGS['NEO4J_URI'],
                    username=s.SETTINGS['NEO4J_USERNAME'],
                    password=s.SETTINGS['NEO4J_PASSWORD'],
                    index_name='reviews',
                    node_label='Review',
                    text_node_properties=['physician_name', 'hospital_name', 'patient_name','text'],
                    embedding_node_property='embedding')

review_template=""" Your job is to use patient
                    reviews to answer questions about their experience at a hospital. Use
                    the following context to answer questions. Be as detailed as possible, but
                    don't make up any information that's not from the context. If you don't know an answer, say you don't know.
{context}
"""

review_system_prompt= SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context'], template= review_template))
review_human_prompt= HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=["question"], template='{question}'))

messages=[review_system_prompt, review_human_prompt]

review_prompt=ChatPromptTemplate(input_variables=['context', 'question'], messages=messages)
#this will be used by agent 
reviews_vector_chain=RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0),
                    chain_type='stuff', retriever=neo4j_vector_index.as_retriever(k=12))
#stuff is telling to chain to pass all 12 reviews to the prompt

reviews_vector_chain.combine_documents_chain.llm_chain.prompt=review_prompt


#testing 
#query="""What have patients said about hospital efficiency? Mention details from specific reviews."""

#response=reviews_vector_chain.invoke(query)

#response.get('result')


#q1="""What have patients said about hospital environment?"""

#r1= reviews_vector_chain.invoke(q1)
#r1.get('result')

