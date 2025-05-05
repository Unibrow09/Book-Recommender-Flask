# Semantic Book Recommender

A modern, AI-powered book recommendation system that uses semantic search to find books based on natural language descriptions. The system also filters by category and emotional tone to provide highly personalized recommendations.

![Semantic Book Recommender](https://via.placeholder.com/800x400/121212/5D5FEF?text=Semantic+Book+Recommender)

## Features

- **Semantic Search**: Describe the kind of book you're looking for in natural language
- **Category Filtering**: Filter recommendations by book category
- **Emotional Tone**: Find books with specific emotional tones (Happy, Surprising, Angry, Suspenseful, Sad)
- **Persistent Embeddings**: Save embeddings to disk to reduce API calls and costs
- **Favorites System**: Save books you like to a personal favorites list
- **Multiple Views**: Toggle between grid and list views for book recommendations
- **Responsive UI**: Beautiful dark-themed interface that works on all devices
- **Book Details**: Click on any book to see full details
- **Vercel Deployment**: Ready to deploy to Vercel's serverless platform

## Technologies Used

- **Backend**: Flask, LangChain, OpenAI Embeddings, ChromaDB
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, NumPy
- **Data Persistence**: Browser localStorage for favorites, ChromaDB for embeddings
- **Deployment**: Vercel serverless functions

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API Key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/semantic-book-recommender.git
   cd semantic-book-recommender
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your browser and go to http://127.0.0.1:5000

3. For the Gradio interface, run:
   ```
   python gradio_dashboard.py
   ```

## Deployment

### Local Deployment

The instructions above will run the application locally for development and testing.

### Vercel Deployment

This project includes a ready-to-deploy setup for Vercel's serverless platform:

1. Navigate to the Vercel Deployment folder:
   ```
   cd Vercel\ Deployment
   ```

2. Run the deployment helper script:
   ```
   python deploy.py
   ```

3. Follow the prompts to deploy to Vercel.

For more detailed instructions, see the [Vercel Deployment Guide](Vercel%20Deployment/DEPLOYMENT_GUIDE.md).

## Using the Favorites Feature

The application allows you to save books you're interested in to a favorites list:

1. When browsing book recommendations, click the bookmark icon on any book card to add it to your favorites
2. Click the "Show Favorites" button to view all your saved books
3. Your favorites are stored in your browser and will persist between sessions
4. Click the bookmark icon again to remove a book from your favorites

## Customizing the View

You can choose between two different viewing modes for your book recommendations:

1. **Grid View**: The default view that shows books in a card grid layout
2. **List View**: A more compact view that displays books in a vertical list

Toggle between views using the view selector buttons in the top right of the results section. Your preferred view is saved between sessions.

## Data

The system uses a CSV file (`books_with_emotions.csv`) containing book information and emotional tone scores, and a text file (`tagged_description.txt`) for generating embeddings.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the embedding model
- LangChain for the semantic search framework 