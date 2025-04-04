# LLM Semantic Book Recommender

## Overview
This project is a semantic book recommendation system that uses natural language processing and vector search to recommend books based on user queries. The system allows users to search for books using natural language descriptions and filter results by category and emotional tone.

## Features
- **Semantic Search**: Find books based on natural language descriptions using vector embeddings
- **Category Filtering**: Filter book recommendations by genre/category
- **Emotional Tone Sorting**: Sort recommendations by emotional tone (Happy, Sad, Angry, etc.)
- **Modern UI**: Dark-themed, responsive web interface built with Flask
- **Book Details**: View detailed information about each recommended book

## Project Structure
```
mid-sem/
├── app.py                  # Main Flask application entry point
├── src/                    # Source code directory
│   ├── data/               # Data processing modules
│   │   ├── __init__.py
│   │   └── data_processor.py
│   ├── vector_search/      # Vector search functionality
│   │   ├── __init__.py
│   │   └── vector_search.py
│   └── web_interface/      # Web interface components
│       ├── __init__.py
│       └── flask_interface.py
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   │   └── styles.css
│   ├── js/                 # JavaScript files
│   │   └── script.js
│   └── images/             # Image assets
└── templates/              # HTML templates
    └── index.html
```

## Technologies Used
- **Python**: Core programming language
- **Flask**: Web framework for the user interface
- **LangChain**: Framework for working with language models
- **OpenAI Embeddings**: For generating vector embeddings
- **Chroma**: Vector database for similarity search
- **Pandas**: For data manipulation and analysis
- **HTML/CSS/JavaScript**: For the web interface

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/LLM-Semantic-Book-Recommender.git
   cd LLM-Semantic-Book-Recommender
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```
   cd mid-sem
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage
1. Enter a description of the type of book you're looking for in the search box
2. Optionally select a category and emotional tone
3. Click "Find Books" to get recommendations
4. Click on any book card to view more details

## Development Progress
- ✅ Implemented data processing module
- ✅ Implemented vector search functionality
- ✅ Created Flask web interface
- ✅ Designed modern dark-themed UI
- ✅ Added category filtering
- ✅ Added emotional tone sorting
- ✅ Implemented book details modal

## Future Improvements
- Add user accounts and saved recommendations
- Implement more advanced filtering options
- Add pagination for large result sets
- Improve mobile responsiveness
- Add book purchase links

## Author
Shivam Vashishtha
21CS2020
IDD-CSE

