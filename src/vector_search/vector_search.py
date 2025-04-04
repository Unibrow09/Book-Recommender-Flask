"""Vector Search Module

This module handles embedding generation and vector search functionality for semantic book recommendations.
"""

import os
from typing import List, Dict, Any, Optional, Union

import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv


class VectorSearch:
    """Class for performing vector search on book descriptions.
    
    This class provides methods for creating embeddings from book descriptions
    and performing semantic similarity searches.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the VectorSearch.
        
        Args:
            data_path: Path to the directory containing the data files.
                       If None, uses the current working directory.
        """
        self.data_path = data_path or os.getcwd()
        self.db = None
        load_dotenv()  # Load environment variables (for OpenAI API key)
    
    def create_vector_db(self, description_file: str = "tagged_description.txt") -> None:
        """Create a vector database from book descriptions.
        
        Args:
            description_file: Name of the file containing tagged book descriptions.
        """
        file_path = os.path.join(self.data_path, description_file)
        
        # Load documents
        raw_documents = TextLoader(file_path).load()
        
        # Split documents
        text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
        documents = text_splitter.split_documents(raw_documents)
        
        # Create vector database
        self.db = Chroma.from_documents(documents, OpenAIEmbeddings())
        print(f"Vector database created with {len(documents)} documents")
    
    def similarity_search(self, query: str, k: int = 50) -> List[Dict[str, Any]]:
        """Perform a similarity search on the vector database.
        
        Args:
            query: The search query.
            k: Number of results to return.
            
        Returns:
            List of search results.
        """
        if self.db is None:
            raise ValueError("Vector database not created. Call create_vector_db() first.")
        
        results = self.db.similarity_search(query, k=k)
        return results
    
    def get_book_recommendations(self, 
                                query: str, 
                                books_df: pd.DataFrame, 
                                k: int = 50) -> pd.DataFrame:
        """Get book recommendations based on a semantic query.
        
        Args:
            query: The search query.
            books_df: DataFrame containing book data.
            k: Number of results to return.
            
        Returns:
            DataFrame containing recommended books.
        """
        if self.db is None:
            raise ValueError("Vector database not created. Call create_vector_db() first.")
        
        # Perform similarity search
        results = self.similarity_search(query, k=k)
        
        # Extract ISBN13 values from search results
        isbn_list = [int(result.page_content.strip('"').split()[0]) for result in results]
        
        # Filter books DataFrame by ISBN13 values
        recommendations = books_df[books_df["isbn13"].isin(isbn_list)].head(k)
        
        return recommendations