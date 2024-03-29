
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