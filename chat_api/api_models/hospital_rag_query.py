
from pydantic import BaseModel

#this model verifies if POST request includes a text field - this is query to chatbot, on which bot respons
class HospitalQueryInput(BaseModel):
    text:str

#this model verifies if response back to user includes input string, output and list of intermidiate steps 
class HospitalQueryOutput(BaseModel):
    input: str
    output: str
    #intermediate_steps: list[str]

