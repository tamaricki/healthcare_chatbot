
#%%

from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage


# %%
#define model , 
chat_model=ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0)

# %%

#test if model only sticks to healtcare related questions 
messages=[SystemMessage(content="""You're an assistant knowledgeable about
healthcare. Only answer healthcare-related questions. """),
        HumanMessage(content="How do I change a tire?")]

chat_model.invoke(messages)
#we used here .invoke but there are other methods like .stream() returns the response one token at time
#.batch() list of message which  llm responds in one call

#you’ll learn a modular way to guide your model’s response, as you did with the SystemMessage, making it easier to
#customize your chatbot, this is possible with prompt templates, or predefined recipes for generating prompts for 
# language models.

#%%
from langchain.prompts import ChatPromptTemplate

review_template_str= """Your job is to use patient reviews to answer questions about their experience at a hospital.\
        Use the following context to answer questions. Be as detailed
        as possible, but don't make up any information that's not
        from the context. If you don't know an answer, say you don't know.
        {context}\
        {question}"""

review_template=ChatPromptTemplate.from_template(review_template_str)

c="I had a great day"
q="Did anyone had a positive experience?"

review_template=review_template.format(context=c, question=q)


#%%

review_template
#however main advantage of langchain is LangChain Expression Language declarative way to compose chains
#https://python.langchain.com/docs/expression_language/

from langchain.prompts import (
PromptTemplate,
SystemMessagePromptTemplate,
HumanMessagePromptTemplate,
ChatPromptTemplate,)

review_template_str = """Your job is to use patient

reviews to answer questions about their experience at
a hospital. Use the following context to answer questions.

Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.

{context}
"""
review_system_prompt = SystemMessagePromptTemplate(
prompt=PromptTemplate(
input_variables=["context"],
template=review_template_str,))

review_human_prompt = HumanMessagePromptTemplate(

prompt=PromptTemplate(
input_variables=["question"],
template="{question}",))

messages = [review_system_prompt, review_human_prompt]
review_prompt_template = ChatPromptTemplate(input_variables=["context", "question"],messages=messages,)
chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

review_chain = review_prompt_template | chat_model


# %%

#this review_chain can be used as follows, and we are adding to chain Strparser to make message more readable
from langchain_core.output_parsers import StrOutputParser

out_parser=StrOutputParser()

review_chain= review_prompt_template | chat_model | out_parser

# %%
c='I had a great day'
q='Did anyone had a positive experience? '

review_chain.invoke({'context': c, 'question':q})
# %%
#BELOW IS TEST RETRIEVER


#%%
#chromadb is vector DB it is similar to AstraDB(DataStax) except DataStax offers db as a service

#now we are building retriever, we will use reviews csv

from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

review_path = "../data/reviews.csv"

#this is folder where vectordb sill store data, if I add relative path then it takes venv location (check notes)
reviews_chroma_path = os.path.expanduser('~') + "/chroma"

# %%
loader = CSVLoader(file_path=review_path, source_column='review')

reviews = loader.load()
#print(reviews)

reviews_vector_db= Chroma.from_documents(reviews, OpenAIEmbeddings(), persist_directory=reviews_chroma_path)

q=""" Has anyone complained about communication with the hospital staff?"""

relevant_docs = reviews_vector_db.similarity_search(q, k=3)


# %%

#next step is to add reviews retriever to review_chain so that relevant reviews are passed to prompt as context 

from langchain.schema.runnable import RunnablePassthrough

review_retriever=reviews_vector_db.as_retriever(k=10)

review_chain= ({'context': review_retriever, 'question': RunnablePassthrough()} | review_prompt_template | chat_model |out_parser)

#%%
#And this is patient review chain retriever 
review_chain.invoke(q)

#now we want to equipt chat to answer questions about other things related to healthcare , so we are distinguishing here
#questions about waiting times and questions related to patient reviews 

#%%

# waiting times will be in the tools where we create function which produces random times, depending on the type of surgery
#data are from OECD.stats 
from tools.waiting_data import get_waiting_time_country_procedure
from langchain.agents import create_openai_functions_agent, Tool, AgentExecutor
from langchain import hub

#tool is a interface which agent uses to interact with the function 
tools = [Tool(name="Reviews",
        func= review_chain.invoke,
        description="""Useful when you need to answer questions
about patient reviews or experiences at the hospital.
Not useful for answering questions about specific visit
details such as payer, billing, treatment, diagnosis,
chief complaint, hospital, or physician information.
Pass the entire question as input to the tool. For instance,
if the question is "What do patients think about the triage system?",
the input should be "What do patients think about the triage system?"
"""),
        Tool("Waits",
        func=get_waiting_time_country_procedure,
        description="""Use when asked about current wait times
for specific procedure. This tool can only answer average waiting time
for specific procedures and average waiting time for specific procedure 
in some countries. Waiting times are available for 
following procedures: Artery bypass, Hip replacement, Hysterectomy, Knee replacement, 
Prostatectomy, Cataract surgery. Information are available from 
following countries: Chile, Costa Rica, Poland, Finland, New Zealand,
Unighted Kingdom, Netherlands, Denmark, Italy, Hungary, Australia,
Estonia, Spain, Portugal, Sweden, Norway, Lithuania.
If country is not asked, then it just returns 
average waiting time. This tool returns wait times in
days. Do not pass the word "hospital" as input,
only the hospital name itself. For instance, if the question is
"What is the wait time at hospital A?", the input should be "A".
""")
        ]

hospital_agent_prompt= hub.pull("hwchase17/openai-functions-agent")

#this agent interacts with the functions, and returns json object with function inputs and their value 
hospital_agent= create_openai_functions_agent(llm=chat_model,prompt= hospital_agent_prompt,tools=tools)
hospital_agent_executor=AgentExecutor(agent=hospital_agent, tools=tools, return_intermidiate_steps=True, verbose=True)


#%%
hospital_agent_executor.invoke({"input":"What is current waiting time for artery bypass?"})

#%%
hospital_agent_executor.invoke({"input":"What did patients say about their comfort at the hospital?"})
#%%






#%%

#SANDBOX
import os
current_location=os.getcwd()
#current_location
#relevant_docs[0].page_content
#with open(review_path, 'r') as f:
#        text=f.readlines()
c= os.path.abspath(os.path.sep)
h = os.path.expanduser('~')+'/chroma'
h

#text
# %%
