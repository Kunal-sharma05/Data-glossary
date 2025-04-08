import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from typing import List, Dict

load_dotenv()


def process_document():

    loader = TextLoader("sap.txt", encoding="utf-8")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)

    return vectorstore


class InMessageHistory(BaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        print("Clearing message history")
        self.messages = []


store = {}


def get_session_by_id(session_id: str) -> InMessageHistory:
    if session_id not in store:
        print(f"Initializing new session for ID: {session_id}")
        store[session_id] = InMessageHistory()
    else:
        print(f"Retrieving existing session for ID: {session_id}")
    return store[session_id]


def llm_call(prompt: str) -> Dict:
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("GROQ_MODEL")
    )
    vectorstore=process_document()
    retriever = vectorstore.as_retriever()
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Answer the following question based only on the provided context: Context: {context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    document_chain = create_stuff_documents_chain(llm, prompt_template)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    chat_with_history = RunnableWithMessageHistory(
        retrieval_chain,
        get_session_history=get_session_by_id,
        input_messages_key="input",
        output_messages_key="answer",
        history_messages_key="history"
    )
    try:
        response = chat_with_history.invoke(
                {"context": retriever, "input": prompt},
                config={"configurable": {"session_id": "foo"}}
        )
        print(store)
        return response
    except Exception as e:
        print(f"Error generating response: {e}")



