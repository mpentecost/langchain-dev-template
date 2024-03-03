from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from basic_rag.retrievers import WebDocuments, PDFDocuments
from common.retrievers import WeaviateHybridV4Retriever


model = ChatOpenAI(model="gpt-4-0125-preview")

# RAG prompt
template = """
Answer the question based only on the following context:
{context}

Make sure when answering to provide the unique source links as citations in 
the format of: "Source: <location>, Page: <page number>".
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# Retriever for Web Docs
# retriever = WeaviateHybridV4Retriever(vector_model=WebDocuments())

# Retriever for PDF Docs
retriever = WeaviateHybridV4Retriever(vector_model=PDFDocuments())

# Chain
chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | model
    | StrOutputParser()
)
