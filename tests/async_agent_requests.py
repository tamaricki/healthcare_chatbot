import asyncio
import time
import httpx


chatbot_url="http://localhost:8000/hospital-rag-agent"

async def make_async_post(url, data):
    timeout=httpx.Timeout(timeout=120)
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, timeout=timeout)
        return response

async def make_bulk_requests(url, data):
    tasks=[make_async_post(url, payload) for payload in data]
    response= await asyncio.gather(*tasks)
    outputs = [r.json()["output"] for r in response]
    return outputs



questions = [
    "What is the current wait time for hip replacement in Chile?",
#"Which hospital has the shortest wait time?",
#"At which hospitals are patients complaining about billing and insurance issues?",
#"What are patients saying about the nursing staff at Castaneda-Hardy?",
#"What was the total billing amount charged to each payer for 2023?",
#"Which physician has the lowest average visit duration in days?",
#"How much was billed for patient 789's stay?",
#"Which physician has billed the most to cigna?"
]

req_bodies = [{"text":q} for q in questions]

start_time = time.perf_counter()
outputs=asyncio.run(make_bulk_requests(chatbot_url, req_bodies))
end_time = time.perf_counter()

print(f"run time {end_time-start_time} seconds")

