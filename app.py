import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import time

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

# Convert isbn13 to string type to ensure matching works properly
books['isbn13'] = books['isbn13'].astype(str)

# Define the index name for Pinecone
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "book-recommendations")

# Setup embeddings and database
def setup_db():
    # Initialize Pinecone
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    
    # Check if index exists
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Index {INDEX_NAME} not found. Please create it in the Pinecone dashboard.")
    
    # Create the embedding model
    embeddings = OpenAIEmbeddings()
    
    # Check if the index is empty
    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    vector_count = stats['total_vector_count']
    
    if vector_count > 0:
        print(f"Loading existing embeddings from Pinecone ({vector_count} vectors)...")
        # Connect to the existing database
        db_books = PineconeVectorStore(
            index_name=INDEX_NAME,
            embedding=embeddings
        )
    else:
        print("Creating new embeddings database...")
        # Create and persist a new database
        # Use UTF-8 encoding to handle special characters
        raw_documents = TextLoader("tagged_description.txt", encoding="utf-8").load()
        # Important: Keep the same chunking settings as in the Chroma version
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=0, chunk_overlap=0)
        documents = text_splitter.split_documents(raw_documents)
        
        print(f"Split into {len(documents)} chunks")
        
        # Process in batches to avoid hitting message size limits
        batch_size = 50
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            current_batch = documents[i:end_idx]
            print(f"Processing batch {(i//batch_size)+1}/{total_batches} (chunks {i}-{end_idx-1})...")
            
            try:
                if i == 0:
                    # First batch - create vector store
                    db_books = PineconeVectorStore.from_documents(
                        current_batch,
                        embeddings,
                        index_name=INDEX_NAME
                    )
                else:
                    # Subsequent batches - add to existing store
                    db_books.add_documents(current_batch)
                
                # Add a small delay between batches to avoid rate limits
                time.sleep(1)
            except Exception as e:
                print(f"Error processing batch: {e}")
                # If error occurs on first batch, raise it
                if i == 0:
                    raise e
                # Otherwise continue with next batch
                time.sleep(2)
                continue
    
    return db_books

# Helper function to safely extract ISBN from text
def safe_extract_isbn(text):
    try:
        # Extract first token from text which should be the ISBN
        isbn_text = text.strip('"').split()[0]
        
        # Return the ISBN as a string to match the dataframe's data type
        return str(isbn_text)
    except (ValueError, IndexError):
        # If we can't parse the ISBN, return None
        print(f"Warning: Could not extract ISBN from: {text[:50]}...")
        return None

# Initialize the database
db_books = setup_db()

# Get all unique categories
categories = ["All"] + sorted(books["simple_categories"].unique().tolist())
tones = ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]

def retrieve_semantic_recommendations(
        query: str,
        category: str = None,
        tone: str = None,
        initial_top_k: int = 100,  # Increased from 50 to get more potential matches
        final_top_k: int = 16,
) -> pd.DataFrame:

    # Get semantic search results
    recs = db_books.similarity_search(query, k=initial_top_k)
    
    # Extract ISBNs with error handling
    books_list = []
    for rec in recs:
        isbn = safe_extract_isbn(rec.page_content)
        if isbn is not None:
            books_list.append(isbn)
    
    print(f"Query: '{query}', Found {len(books_list)} potential ISBNs")
    
    # Filter book recommendations - ensure we get books
    book_recs = books[books["isbn13"].isin(books_list)]
    
    # If no books found, print debug info
    if len(book_recs) == 0:
        print(f"No books found for query: {query}")
        print(f"ISBNs extracted: {books_list[:10]}...")
        # Debug: Print a sample of ISBNs from the database for comparison
        print(f"Sample ISBNs in database: {books['isbn13'].head(5).tolist()}")
        return pd.DataFrame()  # Return empty dataframe
    
    print(f"Found {len(book_recs)} matching books in database")
    
    # Apply category filter if specified
    if category != "All" and not book_recs.empty:
        category_filtered = book_recs[book_recs["simple_categories"] == category]
        # Only use the category filter if it didn't filter out all books
        if not category_filtered.empty:
            book_recs = category_filtered
            print(f"After category filter '{category}': {len(book_recs)} books")
        else:
            print(f"Category filter '{category}' would remove all books, ignoring filter")

    # Limit to final_top_k books
    book_recs = book_recs.head(final_top_k)
    
    # Sort by emotional tone if specified
    if not book_recs.empty:
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
    
    print(f"Processing recommendation request: query='{query}', category='{category}', tone='{tone}'")
    
    recommendations = retrieve_semantic_recommendations(query, category, tone)
    
    # Debug output for empty results
    if recommendations.empty:
        print("No recommendations found!")
        return jsonify({"recommendations": []})
    
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
    
    print(f"Returning {len(results)} recommendations")
    return jsonify({"recommendations": results})

if __name__ == '__main__':
    app.run(debug=True) 