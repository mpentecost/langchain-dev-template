from langchain_openai import ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain import hub

from common.retrievers import WeaviateHybridV4Retriever
from basic_rag.retrievers import WebDocuments, PDFDocuments


model = ChatOpenAI(model="gpt-4-0125-preview", streaming=True)

# 2. Create Tools
web_docs_retriever = WeaviateHybridV4Retriever(vector_model=WebDocuments())
web_docs_tool = create_retriever_tool(
    web_docs_retriever,
    "web_search",
    "Search for information from the web",
)

pdf_docs_retriever = WeaviateHybridV4Retriever(vector_model=PDFDocuments())
pdf_docs_tool = create_retriever_tool(
    pdf_docs_retriever,
    "pdf_search",
    "Search for information from the local library",
)

tools = [web_docs_tool, pdf_docs_tool]


# 3. Create Agent
prompt = hub.pull("hwchase17/openai-functions-agent")
agent = create_openai_tools_agent(model, tools, prompt)
agent_chain = AgentExecutor(agent=agent, tools=tools, verbose=True)
