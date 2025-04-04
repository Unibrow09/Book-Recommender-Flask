"""LLM Semantic Book Recommender Flask Application

This is the main entry point for the Flask-based LLM Semantic Book Recommender application.
It provides a modern web interface for semantic book recommendations.
"""

import os
import argparse
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify

from src.data.data_processor import DataProcessor
from src.vector_search.vector_search import VectorSearch
from src.web_interface.flask_interface import FlaskInterface

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')

# Initialize components
data_path = os.getcwd()
data_processor = DataProcessor(data_path)
vector_search = VectorSearch(data_path)
interface = FlaskInterface(data_path)

# Load data and initialize vector search
books_file = "books_with_emotions.csv"
descriptions_file = "tagged_description.txt"

@app.before_first_request
def initialize():
    """Initialize data and vector search before first request."""
    print(f"Loading book data from {books_file}...")
    interface.load_data(books_file)
    
    print(f"Creating vector database from {descriptions_file}...")
    interface.initialize_vector_search(descriptions_file)
    print("Initialization complete!")

@app.route('/')
def index():
    """Render the main page."""
    # Get unique categories and add "All" option
    categories = ["All"] + sorted(interface.books_df["simple_categories"].unique().tolist())
    
    # Define emotional tones
    tones = ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]
    
    return render_template('index.html', categories=categories, tones=tones)

@app.route('/recommend', methods=['POST'])
def recommend():
    """Get book recommendations based on query, category, and tone."""
    data = request.json
    query = data.get('query', '')
    category = data.get('category', 'All')
    tone = data.get('tone', 'All')
    
    recommendations = interface.get_recommendations(query, category, tone)
    
    return jsonify(recommendations)

def main():
    """Main function to run the Flask application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="LLM Semantic Book Recommender")
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1",
        help="Host to run the Flask server on"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port to run the Flask server on"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Whether to run the Flask server in debug mode"
    )
    args = parser.parse_args()
    
    # Run the Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()