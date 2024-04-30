
#chat agent needs to decide depending on the query if it will use cypher chain,  reviews chain or wait time functions. 
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, Tool, AgentExecutor
from langchain import hub
from chains.hospital_review_chain import reviews_vector_chain
from chains.hospital_cypher_chain import hospital_cypher_chain
from tools.waiting_data import get_current_wait_times, get_most_available_hospital, get_waiting_time_country_procedure
import settings as s

HOSPITAL_AGENT_MODEL = s.SETTINGS["HOSPITAL_AGENT_MODEL"]

#we could define our own prompt for the agent or we can load predefined prompt from LangChain Hub

hospital_agent_prompts=hub.pull("hwchase17/openai-functions-agent")

#definition of tools which agent will use when he receives the query

tools = [Tool(name="Experiences", 
        func= reviews_vector_chain.invoke,
        description=""" Useful when you need to answer questions
about patient experiences, feelings, or any other qualitative
question that could be answered about a patient using semantic
search. Not useful for answering objective questions that involve
counting, percentages, aggregations, or listing facts. Use the
entire prompt as input to the tool. For instance, if the prompt is
"Are patients satisfied with their care?", the input should be
"Are patients satisfied with their care?".""" ),
        Tool(name="graph",
        func=hospital_cypher_chain.invoke, 
        description= """Useful for answering questions about patients,
physicians, hospitals, insurance payers, patient review
statistics, and hospital visit details. Use the entire prompt as
input to the tool. For instance, if the prompt is "How many visits
have there been?", the input should be "How many visits have
there been?"""),
        Tool(name="waits",
        func=get_current_wait_times,
        description=""" Use when asked about current wait times
at a specific hospital. This tool can only get the current
wait time at a hospital and does not have any information about
aggregate or historical wait times. Do not pass the word "hospital"
as input, only the hospital name itself. For example, if the prompt
is "What is the current wait time at Jordan Inc Hospital?", the
input should be "Jordan Inc"
"""),
        Tool(name="availability",
        func = get_most_available_hospital,
        description=""" Use when you need to find out which hospital has the shortest
wait time. This tool does not have any information about aggregate
or historical wait times. This tool returns a dictionary with the
hospital name as the key and the wait time in minutes as the value.
        """),
        Tool(name="operation",
        func = get_waiting_time_country_procedure,
        description= """ Use when asked about current wait times
for specific opration. This tool can only answer average waiting time
for specific operations and average waiting time for specific operations
in some countries. Waiting times are available for 
following operations: Artery bypass, Hip replacement, Hysterectomy, Knee replacement, 
Prostatectomy, Cataract surgery. Information are available from 
following countries: Chile, Costa Rica, Poland, Finland, New Zealand,
Unighted Kingdom, Netherlands, Denmark, Italy, Hungary, Australia,
Estonia, Spain, Portugal, Sweden, Norway, Lithuania.
If country is not asked, then it just returns 
average waiting time for specific operations . This tool returns wait times in
days. """)
        ]


#now we are instantinating the agent:

chat_model=ChatOpenAI(model=HOSPITAL_AGENT_MODEL, temperature=0)

hospital_rag_agent= create_openai_functions_agent(llm=chat_model, prompt=hospital_agent_prompts, tools=tools)

hospital_rag_agent_executor=AgentExecutor(agent=hospital_rag_agent, tools=tools, return_intermediate_steps=True, verbose=True)

#test
#r1 = hospital_rag_agent_executor.invoke({"input":"What is the wait time for Wallace-Hamilton?"})

#r2=hospital_rag_agent_executor.invoke({"input":"What is current waiting time for artery bypass in Finland?"})

#r3=hospital_rag_agent_executor.invoke({"input":"Which hospital has the shortest wait time?"}) #pay attention to Any input 

#r4= hospital_rag_agent_executor.invoke({"input": "What's the average billing amount for emergency visits by hospital?"})


#now one where we need to help the llm find the correct answer 
#r5= hospital_rag_agent_executor.invoke({"input":"Show me reviews written by patient 7674."})
#r5.get("output")

#now same question but re-formulated
#r51=hospital_rag_agent_executor.invoke({"input":"Query the graph database to show me the reviews written by patient 7674."})


