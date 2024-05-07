
from fastapi import FastAPI
from hospital_rag_agent import hospital_rag_agent_executor
from api_models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from utils.async_utils import async_retry

app=FastAPI(title="Hospital Chatbot", description="Endpoints for a hospital system Graph RAG chatbot")


@async_retry(max_retries=3, delay=1)
async def invoke_agent_with_retry(query:str):
    """Retry the agent if a tool fails to run.
        This can help when there are intermittent connection issues
        to external APIs.
        """ 
    return await hospital_rag_agent_executor.ainvoke({"input": query})

#htere is .invoke and .ainvoke (invoke call the chain on the input) (ainvoke call chain on input async)

@app.get("/")
async def get_status():
    return {"status":"runing"}


@app.post("/hospital-rag-agent") # changed from post to get, with post get error 405 method not allowed 
async def query_hospital_agent(query:HospitalQueryInput) ->HospitalQueryOutput:
    query_response= await invoke_agent_with_retry(query.text)
    query_response["intermediate_steps"] = [str(s) for s in query_response["intermediate_steps"]]
    return query_response


