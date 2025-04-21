import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langchain_community.document_loaders import CSVLoader

load_dotenv()


class AgentState(BaseModel):
    input: str
    history: List[Dict[str, str]] = []
    context: List[Document] = []
    answer: Optional[str] = ""


def process_document():
    loader = CSVLoader("sap_tables.csv")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore


vectorstore = process_document()
retriever = vectorstore.as_retriever()
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),
               model_name=os.getenv("GROQ_MODEL"))


def retrieve_documents(state: AgentState):
    docs = retriever.invoke(state.input)
    return {"context": docs}


def generate_answer(state: AgentState):
    history_str = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in state.history])
    context_str = "\n".join([doc.page_content for doc in state.context])
    prompt_template = ChatPromptTemplate.from_template(
        """Answer the question based on the context and previous conversation.
Previous conversation: {history}
Context: {context}
Question: {input}
Answer:"""
    )
    formatted_prompt = prompt_template.format(
        history=history_str, context=context_str, input=state.input
    )
    response = llm.invoke(formatted_prompt)
    return {"answer": response.content}


def update_history(state: AgentState):
    new_history = state.history + [
        {"role": "user", "content": state.input},
        {"role": "assistant", "content": state.answer}
    ]
    return {"history": new_history}


# LangGraph workflow
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("update_history", update_history)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate_answer")
workflow.add_edge("generate_answer", "update_history")
workflow.add_edge("update_history", END)
compiled_app = workflow.compile()
