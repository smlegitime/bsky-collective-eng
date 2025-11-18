"""
Indexer for RAG.

The code below will load, split, and store documents in a vector store.
"""

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

def build_index():
    # Load docs from blog. Only keep post title, headers, and content from the full HTML
    bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
    loader = WebBaseLoader(
        web_paths=("https://mackuba.eu/2024/02/21/bluesky-guide/",),
        bs_kwargs={"parse_only": bs4_strainer}
    )
    docs = loader.load()

    # Split docs for embedding and vector storage
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, 
        add_start_index=True, # track index in original document
    )
    all_splits = text_splitter.split_documents(docs)

    # Store docs
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)
    ids = vector_store.add_documents(documents=all_splits)

    return vector_store


