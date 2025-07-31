"""
Filename: brainstorming_agent/utils/rag_utils.py
Date: 2025-07-30
Version: 1.0
Description: This script defines utility functions for Retrieval Augmented Generation (RAG).
"""
import json
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

RETRIEVAL_SOURCES_PATH = 'brainstorming_agent/constants/retrieval_sources.json'

def _get_src_urls(src_path: str = RETRIEVAL_SOURCES_PATH):
    with open(src_path) as retrieval_src_file:
        retrieval_srcs = json.load(retrieval_src_file)
        urls = retrieval_srcs['bsky'] + retrieval_srcs['skyware']
        return urls
    
# TODO needs optimization
def preprocess_docs():
    # Load documents
    urls = _get_src_urls()
    docs = [WebBaseLoader(url).load() for url in urls]

    # Split documents
    docs_list = [item for sublist in docs for item in sublist]
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100,
        chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(docs_list)
    return doc_splits

# TODO: use other embeddings
def initialize_retriever(doc_splits):
    vectorstore = InMemoryVectorStore.from_documents(
        documents=doc_splits,
        embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    return retriever