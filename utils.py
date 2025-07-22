from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores.base import VectorStoreRetriever

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter
)
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings


def load_docs(source_code_path: str, file_exts: List[str], parser_threshold: int = 500) -> List[Document]:
    #TODO: validate input file extensions and map to Language enum values
    loader = GenericLoader.from_filesystem(
        source_code_path,
        glob='*',
        suffixes=file_exts,
        parser=LanguageParser(language=Language.TS, parser_threshold=parser_threshold)
    )
    docs = loader.load()
    return docs


def split_code(docs: Document, language: Language, chunk_size:int = 400, chunk_overlap:int = 80) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=language, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    split_docs = splitter.split_documents(documents=docs)
    return split_docs


def create_retriever(split_docs: List[Document]) -> VectorStoreRetriever:
    #TODO: parameterize in future
    embeddings = OllamaEmbeddings(model='llama3.2')

    vectorstore = InMemoryVectorStore.from_documents(
        documents=split_docs, 
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever()
    return retriever