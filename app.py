import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load books data
books = pd.read_csv("books_with_emotions.csv")
books["large_thumbnail"] = books["thumbnail"] + "&fife=w800"
books["large_thumbnail"] = np.where(
    books["large_thumbnail"].isna(),
    "cover-not-found.jpg",
    books["large_thumbnail"],
)

# Define the persist directory for storing embeddings
PERSIST_DIRECTORY = "chroma_db"

# Setup embeddings and database
def setup_db():
    # Check if the database already exists
    if os.path.exists(PERSIST_DIRECTORY):
        print("Loading existing embeddings from disk...")
        # Load the existing database from disk
        db_books = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=OpenAIEmbeddings()
        )
    else:
        print("Creating new embeddings database...")
        # Create and persist a new database
        # Use UTF-8 encoding to handle special characters
        raw_documents = TextLoader("tagged_description.txt", encoding="utf-8").load()
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=0, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)
        
        # Create the database with persist_directory specified
        db_books = Chroma.from_documents(
            documents, 
            OpenAIEmbeddings(),
            persist_directory=PERSIST_DIRECTORY
        )
        
    return db_books

# Initialize the database
db_books = setup_db()

# Get all unique categories
categories = ["All"] + sorted(books["simple_categories"].unique().tolist())
tones = ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]

def retrieve_semantic_recommendations(
        query: str,
        category: str = None,
        tone: str = None,
        initial_top_k: int = 50,
        final_top_k: int = 16,
) -> pd.DataFrame:

    recs = db_books.similarity_search(query, k=initial_top_k)
    books_list = [int(rec.page_content.strip('"').split()[0]) for rec in recs]
    book_recs = books[books["isbn13"].isin(books_list)].head(initial_top_k)

    if category != "All":
        book_recs = book_recs[book_recs["simple_categories"] == category].head(final_top_k)
    else:
        book_recs = book_recs.head(final_top_k)

    if tone == "Happy":
        book_recs.sort_values(by="joy", ascending=False, inplace=True)
    elif tone == "Surprising":
        book_recs.sort_values(by="surprise", ascending=False, inplace=True)
    elif tone == "Angry":
        book_recs.sort_values(by="anger", ascending=False, inplace=True)
    elif tone == "Suspenseful":
        book_recs.sort_values(by="fear", ascending=False, inplace=True)
    elif tone == "Sad":
        book_recs.sort_values(by="sadness", ascending=False, inplace=True)

    return book_recs

@app.route('/')
def index():
    # Serve the index.html file from the static directory
    # Pass data to JavaScript by appending it as URL parameters
    categories_str = ','.join(categories)
    tones_str = ','.join(tones)
    return send_from_directory('static', 'index.html')

@app.route('/categories')
def get_categories():
    # Endpoint to provide categories to the frontend
    return jsonify({"categories": categories, "tones": tones})

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    query = data.get('query', '')
    category = data.get('category', 'All')
    tone = data.get('tone', 'All')
    
    recommendations = retrieve_semantic_recommendations(query, category, tone)
    
    # Format the results
    results = []
    for _, row in recommendations.iterrows():
        description = row["description"]
        truncated_desc_split = description.split()
        truncated_description = " ".join(truncated_desc_split[:30]) + "..."

        authors_split = row["authors"].split(";")
        if len(authors_split) == 2:
            authors_str = f"{authors_split[0]} and {authors_split[1]}"
        elif len(authors_split) > 2:
            authors_str = f"{', '.join(authors_split[:-1])}, and {authors_split[-1]}"
        else:
            authors_str = row["authors"]
            
        results.append({
            "isbn13": row["isbn13"],
            "title": row["title"],
            "authors": authors_str,
            "description": truncated_description,
            "full_description": description,
            "thumbnail": row["large_thumbnail"],
            "categories": row["simple_categories"],
            "publication_date": row.get("publication_date", ""),
            "emotional_tones": {
                "joy": float(row.get("joy", 0)),
                "anger": float(row.get("anger", 0)),
                "sadness": float(row.get("sadness", 0)),
                "fear": float(row.get("fear", 0)),
                "surprise": float(row.get("surprise", 0))
            }
        })
    
    return jsonify({"recommendations": results})

if __name__ == '__main__':
    app.run(debug=True) 