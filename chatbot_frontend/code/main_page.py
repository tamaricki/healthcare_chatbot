
import requests
import streamlit as st
import settings as s

chatbot_url = s.SETTINGS["CHATBOT_URL"] 
# this might differ if we deploy as docker image and put in gcp

with st.sidebar:
    st.header("About")
    st.markdown(""" This chatbot interfaces with a
    [LangChain](https://python.langchain.com/docs/get_started/introduction)
    agent designed to answer questions about the hospitals, patients,
    visits, physicians, and insurance payers in a fake hospital system.
    The agent uses retrieval-augment generation (RAG) over both
    structured and unstructured data that has been synthetically generated.
    """)


    #st.header("example quetions") ...


st.title("Hospital System Chatbot")
st.info("Ask me questions about patients, visits, insurance payers, hospitals,"
        "physicians, reviews, and wait times!")

if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])
        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])

if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "output":prompt})

    data={"text":prompt}

    with st.spinner("Searching for an answer. . .  "):
        response = requests.post(chatbot_url, json=data)
        if response.status_code==200:
            output_text=response.json()["output"]
            explanation = response.json()["intermediate_steps"]

        else:
            output_text="""An error occured while processing your message please try again or rephares your message. """
            explanation=output_text

    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated?", state="complete").info(explanation)

    st.session_state.messages.append({"role":"assistant", "output": output_text, "explanation":explanation})
        



