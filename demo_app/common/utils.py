from langchain_community.document_loaders import WebBaseLoader, PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from common.retrievers import VectorModel


def add_webpage_to_kb(
    url: str, retriever_class: VectorModel, return_uuids: bool = False
):
    """Add a webpage to the knowledge base"""
    # Load
    loader = WebBaseLoader(url)
    data = loader.load()

    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_splits = text_splitter.split_documents(data)

    # Add to vectorDB
    retriever = retriever_class()
    uuids = retriever.add_documents(all_splits)

    print(f"Loaded {url} into vector store")

    if return_uuids:
        return uuids
    return None


def add_pdfs_to_kb(path: str, retriever_class: VectorModel, return_uuids: bool = False):
    """Add a PDF to the knowledge base"""
    # Load
    loader = PyPDFDirectoryLoader(path)
    data = loader.load()

    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_splits = text_splitter.split_documents(data)

    # Add to vectorDB
    retriever = retriever_class()
    uuids = retriever.add_documents(all_splits)

    print(f"Loaded pdfs at {path} into vector store")

    if return_uuids:
        return uuids
