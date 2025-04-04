"""Data Processing Module

This module handles data loading, cleaning, and preprocessing for the book recommender system.
"""

import pandas as pd
import numpy as np
import os
from typing import Optional, List, Dict, Any, Union


class DataProcessor:
    """Class for loading and processing book data.
    
    This class provides methods for loading book data from CSV files,
    cleaning the data, and preparing it for vector search and sentiment analysis.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the DataProcessor.
        
        Args:
            data_path: Path to the directory containing the data files.
                       If None, uses the current working directory.
        """
        self.data_path = data_path or os.getcwd()
        self.books_df = None
    
    def load_data(self, file_name: str = "books_cleaned.csv") -> pd.DataFrame:
        """Load book data from a CSV file.
        
        Args:
            file_name: Name of the CSV file containing book data.
            
        Returns:
            DataFrame containing book data.
        """
        file_path = os.path.join(self.data_path, file_name)
        self.books_df = pd.read_csv(file_path)
        return self.books_df
    
    def create_tagged_descriptions(self, output_file: str = "tagged_description.txt") -> None:
        """Create a text file with tagged descriptions for vector search.
        
        This method extracts the tagged_description column from the books DataFrame
        and saves it to a text file, with each description on a new line.
        
        Args:
            output_file: Name of the output text file.
        """
        if self.books_df is None:
            raise ValueError("No data loaded. Call load_data() first.")
            
        output_path = os.path.join(self.data_path, output_file)
        self.books_df["tagged_description"].to_csv(
            output_path,
            sep="\n",
            index=False,
            header=False
        )
        print(f"Tagged descriptions saved to {output_path}")
    
    def prepare_for_web_display(self, books_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Prepare book data for web display.
        
        This method adds large thumbnail URLs and handles missing values.
        
        Args:
            books_df: DataFrame containing book data. If None, uses self.books_df.
            
        Returns:
            DataFrame with prepared data for web display.
        """
        df = books_df if books_df is not None else self.books_df
        if df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Create large thumbnail URLs
        df["large_thumbnail"] = df["thumbnail"] + "&fife=w800"
        
        # Handle missing thumbnail URLs
        df["large_thumbnail"] = np.where(
            df["large_thumbnail"].isna(),
            "cover-not-found.jpg",
            df["large_thumbnail"]
        )
        
        return df
    
    def filter_by_category(self, category: str, books_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Filter books by category.
        
        Args:
            category: Category to filter by.
            books_df: DataFrame containing book data. If None, uses self.books_df.
            
        Returns:
            DataFrame with filtered books.
        """
        df = books_df if books_df is not None else self.books_df
        if df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if category == "All" or category is None:
            return df
        
        return df[df["simple_categories"] == category]
    
    def sort_by_emotion(self, emotion: str, books_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Sort books by emotion score.
        
        Args:
            emotion: Emotion to sort by (e.g., "joy", "sadness", "fear").
            books_df: DataFrame containing book data. If None, uses self.books_df.
            
        Returns:
            DataFrame with sorted books.
        """
        df = books_df if books_df is not None else self.books_df
        if df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        emotion_map = {
            "Happy": "joy",
            "Surprising": "surprise",
            "Angry": "anger",
            "Suspenseful": "fear",
            "Sad": "sadness"
        }
        
        column = emotion_map.get(emotion, None)
        if column and column in df.columns:
            return df.sort_values(by=column, ascending=False)
        
        return df
    
    def format_author_string(self, authors: str) -> str:
        """Format author string for display.
        
        Args:
            authors: String containing author names separated by semicolons.
            
        Returns:
            Formatted author string.
        """
        authors_split = authors.split(';')
        if len(authors_split) == 1:
            return authors
        elif len(authors_split) == 2:
            return f"{authors_split[0]} and {authors_split[1]}"
        else:
            return f"{', '.join(authors_split[:-1])}, and {authors_split[-1]}"
    
    def truncate_description(self, description: str, max_words: int = 30) -> str:
        """Truncate description to a specified number of words.
        
        Args:
            description: Book description to truncate.
            max_words: Maximum number of words to include.
            
        Returns:
            Truncated description.
        """
        words = description.split()
        if len(words) <= max_words:
            return description
        
        return " ".join(words[:max_words]) + "..."