"""Flask Interface Module

This module provides a Flask-based user interface for the book recommendation system.
"""

import os
from typing import List, Dict, Any, Optional, Tuple, Union

import pandas as pd

from src.vector_search.vector_search import VectorSearch
from src.data.data_processor import DataProcessor


class FlaskInterface:
    """Class for creating and managing the Flask web interface.
    
    This class provides methods for setting up and launching a Flask-based
    user interface for the book recommendation system.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the FlaskInterface.
        
        Args:
            data_path: Path to the directory containing the data files.
                       If None, uses the current working directory.
        """
        self.data_path = data_path or os.getcwd()
        self.data_processor = DataProcessor(self.data_path)
        self.vector_search = VectorSearch(self.data_path)
        self.books_df = None
    
    def load_data(self, file_name: str = "books_with_emotions.csv") -> None:
        """Load book data from a CSV file.
        
        Args:
            file_name: Name of the CSV file containing book data.
        """
        file_path = os.path.join(self.data_path, file_name)
        self.books_df = pd.read_csv(file_path)
        self.books_df = self.data_processor.prepare_for_web_display(self.books_df)
    
    def initialize_vector_search(self, description_file: str = "tagged_description.txt") -> None:
        """Initialize the vector search database.
        
        Args:
            description_file: Name of the file containing tagged book descriptions.
        """
        self.vector_search.create_vector_db(description_file)
    
    def retrieve_recommendations(self,
                               query: str,
                               category: str = "All",
                               tone: str = "All",
                               initial_top_k: int = 50,
                               final_top_k: int = 16) -> pd.DataFrame:
        """Retrieve book recommendations based on query, category, and tone.
        
        Args:
            query: The search query.
            category: Category to filter by.
            tone: Emotional tone to sort by.
            initial_top_k: Initial number of results to retrieve.
            final_top_k: Final number of results to return.
            
        Returns:
            DataFrame containing recommended books.
        """
        if self.books_df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Get recommendations from vector search
        recommendations = self.vector_search.get_book_recommendations(
            query, self.books_df, k=initial_top_k
        )
        
        # Filter by category
        if category != "All":
            recommendations = self.data_processor.filter_by_category(
                category, recommendations
            ).head(final_top_k)
        else:
            recommendations = recommendations.head(final_top_k)
        
        # Sort by emotion
        if tone != "All":
            recommendations = self.data_processor.sort_by_emotion(
                tone, recommendations
            )
        
        return recommendations
    
    def format_recommendations(self, recommendations: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format recommendations for display in Flask interface.
        
        Args:
            recommendations: DataFrame containing recommended books.
            
        Returns:
            List of dictionaries containing book information.
        """
        results = []
        
        for _, row in recommendations.iterrows():
            # Format author string
            authors_str = self.data_processor.format_author_string(row["authors"])
            
            # Truncate description
            truncated_description = self.data_processor.truncate_description(
                row["description"], max_words=30
            )
            
            # Create book info dictionary
            book_info = {
                "title": row["title"],
                "authors": authors_str,
                "description": truncated_description,
                "full_description": row["description"],
                "thumbnail": row["large_thumbnail"],
                "isbn13": row["isbn13"],
                "categories": row["simple_categories"],
                "rating": row["average_rating"] if "average_rating" in row else None,
                "emotions": {
                    "joy": float(row["joy"]) if "joy" in row else 0,
                    "sadness": float(row["sadness"]) if "sadness" in row else 0,
                    "anger": float(row["anger"]) if "anger" in row else 0,
                    "fear": float(row["fear"]) if "fear" in row else 0,
                    "surprise": float(row["surprise"]) if "surprise" in row else 0
                }
            }
            
            # Add to results
            results.append(book_info)
        
        return results
    
    def get_recommendations(self, query: str, category: str, tone: str) -> List[Dict[str, Any]]:
        """Get and format book recommendations.
        
        Args:
            query: The search query.
            category: Category to filter by.
            tone: Emotional tone to sort by.
            
        Returns:
            List of dictionaries containing book information.
        """
        recommendations = self.retrieve_recommendations(query, category, tone)
        return self.format_recommendations(recommendations)