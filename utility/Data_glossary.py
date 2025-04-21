import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, CSVLoader, PyPDFLoader, UnstructuredExcelLoader
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
import time

load_dotenv()


def process_document():
    index_path = "faiss_index"

    if os.path.exists(index_path):
        print("FAISS index already exists. Loading the existing index.")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        print("FAISS index does not exist. Creating a new index.")
        loader1 = CSVLoader("sap_tables.csv")
        loader2 = CSVLoader("transactional_codes.csv")
        document1 = loader1.load()
        document2 = loader2.load()
        combined_documents = document1 + document2
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(combined_documents)

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vector_store = FAISS.from_documents(splits, embeddings)
        vector_store.save_local(index_path)

    # docs = vector_store.similarity_search("qux")

    return vector_store


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
    start_time = time.perf_counter()
    vectorstore = process_document()
    end_time = time.perf_counter()
    print(f"time taken by the vector store to response {end_time - start_time}")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "Role: You are an SAP Expert"
                   "Task:- Answer the following question based only on the provided context: Context: {context}"
                   "Don't mention the context, Frame it you have done"),
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
        start_time = time.perf_counter()
        response = chat_with_history.invoke(
            {"context": retriever, "input": prompt},
            config={"configurable": {"session_id": "foo"}}
        )
        end_time = time.perf_counter()
        print(f"time taken by the llm to response {end_time - start_time}")
        lightweight_response = {
            "answer": response.get("answer"),
            "metadata": response.get("history")
        }
        return lightweight_response
    except Exception as e:
        print(f"Error generating response: {e}")
