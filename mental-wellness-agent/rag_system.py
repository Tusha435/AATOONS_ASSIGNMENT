"""
RAG System using ChromaDB and OpenAI Embeddings
This module handles document loading, embedding creation, and retrieval.
"""

import os
from typing import List, Dict
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


class RAGSystem:
    """Handles retrieval-augmented generation using ChromaDB."""

    def __init__(self, knowledge_base_path: str = "./knowledge_base",
                 persist_directory: str = "./chroma_db"):
        """
        Initialize the RAG system.

        Args:
            knowledge_base_path: Path to directory containing knowledge base files
            persist_directory: Path where ChromaDB will persist data
        """
        self.knowledge_base_path = knowledge_base_path
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = None
        self.documents = []

    def load_documents(self) -> List:
        """Load documents from the knowledge base directory."""
        print(f"Loading documents from {self.knowledge_base_path}...")

        # Load all text files from the knowledge base directory
        loader = DirectoryLoader(
            self.knowledge_base_path,
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        documents = loader.load()

        print(f"Loaded {len(documents)} documents")
        return documents

    def split_documents(self, documents: List) -> List:
        """Split documents into smaller chunks for better retrieval."""
        print("Splitting documents into chunks...")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        return chunks

    def create_vectorstore(self, force_reload: bool = False):
        """Create or load the vector store."""
        # Check if vectorstore already exists
        if os.path.exists(self.persist_directory) and not force_reload:
            print("Loading existing vectorstore...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("Vectorstore loaded successfully")
        else:
            print("Creating new vectorstore...")

            # Load and split documents
            documents = self.load_documents()
            self.documents = self.split_documents(documents)

            # Create vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )

            print("Vectorstore created and persisted successfully")

    def retrieve_documents(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve relevant documents for a given query.

        Args:
            query: User question
            k: Number of documents to retrieve

        Returns:
            List of relevant document chunks with metadata
        """
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call create_vectorstore() first.")

        print(f"\nRetrieving top {k} relevant documents for query: '{query}'")

        # Perform similarity search
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        retrieved_docs = []
        for i, (doc, score) in enumerate(results):
            print(f"  Document {i+1} (similarity: {1-score:.4f}):")
            print(f"    Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Preview: {doc.page_content[:100]}...")

            retrieved_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": 1 - score  # Convert distance to similarity
            })

        return retrieved_docs

    def format_context(self, documents: List[Dict]) -> str:
        """Format retrieved documents into a context string."""
        context_parts = []
        for i, doc in enumerate(documents):
            context_parts.append(f"[Document {i+1}]\n{doc['content']}\n")

        return "\n".join(context_parts)


def initialize_rag_system(force_reload: bool = False) -> RAGSystem:
    """
    Initialize and return a RAG system instance.

    Args:
        force_reload: If True, recreate the vectorstore from scratch

    Returns:
        Initialized RAGSystem instance
    """
    rag = RAGSystem()
    rag.create_vectorstore(force_reload=force_reload)
    return rag


if __name__ == "__main__":
    # Test the RAG system
    print("Testing RAG System...")
    print("="*50)

    # Initialize
    rag = initialize_rag_system(force_reload=True)

    # Test retrieval
    test_query = "How is your day, tell me all about it"
    docs = rag.retrieve_documents(test_query, k=3)

    print("\n" + "="*50)
    print("Context for LLM:")
    print("="*50)
    print(rag.format_context(docs))
