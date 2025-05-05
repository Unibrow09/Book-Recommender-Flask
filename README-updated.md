# Semantic Book Recommender

A semantic book recommendation system powered by AI to help users discover books based on their preferences and interests.

## Overview

This application uses OpenAI embeddings and Pinecone vector database to provide semantic search capabilities for book recommendations. Users can describe what kind of book they're looking for, and the system will recommend books that semantically match their query.

Key features:
- Semantic search using natural language processing
- Category-based filtering
- Emotional tone filtering (Happy, Surprising, Angry, Suspenseful, Sad)
- Responsive UI with grid and list views
- Favorites system (stored in browser's localStorage)

## Project Structure

```
LLM-Semantic-Book-Recommender/
├── app.py                     # Main Flask application
├── books_with_emotions.csv    # Book data with emotional analysis
├── cover-not-found.jpg        # Default image for books without covers
├── requirements.txt           # Project dependencies
├── static/                    # Static web assets
│   └── index.html             # Frontend interface (HTML, CSS, JS)
├── tagged_description.txt     # Preprocessed book descriptions with ISBNs
└── Vercel_Deployment/         # Files for Vercel deployment
    ├── api/
    │   └── index.py           # Vercel serverless function entry point
    ├── data/
    │   └── cover-not-found.jpg # Fallback cover image
    ├── static/
    │   └── index.html         # Frontend interface
    ├── requirements.txt       # Python dependencies for Vercel
    ├── vercel.json           # Vercel configuration
    └── env.example            # Example environment variables
```

## Local Development

### Prerequisites

- Python 3.9+
- OpenAI API key
- Pinecone account and API key

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/LLM-Semantic-Book-Recommender.git
   cd LLM-Semantic-Book-Recommender
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys
   ```
   OPENAI_API_KEY=your-openai-api-key
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX_NAME=book-recommendations
   ```

4. Run the application
   ```bash
   python app.py
   ```

5. Open http://localhost:5000 in your browser

## Deploying to Vercel

See the [Vercel Deployment README](./Vercel_Deployment/README.md) for detailed instructions on deploying this application to Vercel.

## Data Processing

The application uses a dataset of books with the following processing steps:

1. **EDA and Cleaning**: Initial exploration and cleaning of the raw data
2. **Vector Search**: Creating embeddings for semantic search
3. **Text Classification**: Categorizing books into simple categories
4. **Sentiment Analysis**: Analyzing emotional tones of book descriptions

## Acknowledgments

- Book data is sourced from a public books dataset
- Emotional analysis is powered by OpenAI's embeddings
- Vector search is implemented using Pinecone

## License

This project is licensed under the MIT License - see the LICENSE file for details. 