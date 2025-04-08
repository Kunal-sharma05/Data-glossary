import os

from langchain import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_openai import AzureChatOpenAI
from db.database import database_url
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # Your secure key
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")

db = SQLDatabase.from_uri(database_url)

llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    model=AZURE_OPENAI_MODEL,
    temperature=0)

sql_chain = create_sql_query_chain(llm=llm, db=db)

question = "What is this differed tax rules?"
result = sql_chain.invoke({"question": "What is this differed tax rules?"})

print(result)
