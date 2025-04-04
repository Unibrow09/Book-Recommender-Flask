/**
 * Semantic Book Recommender - Frontend JavaScript
 * 
 * This script handles the user interactions, API calls, and dynamic content rendering
 * for the Semantic Book Recommender web application.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchButton = document.getElementById('search-button');
    const queryInput = document.getElementById('query');
    const categorySelect = document.getElementById('category');
    const toneSelect = document.getElementById('tone');
    const resultsContainer = document.getElementById('results');
    const loadingIndicator = document.getElementById('loading');
    const modal = document.getElementById('book-modal');
    const closeModal = document.querySelector('.close');
    
    // Event Listeners
    searchButton.addEventListener('click', handleSearch);
    closeModal.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });
    
    // Also allow search on Enter key in the query textarea
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSearch();
        }
    });
    
    /**
     * Handle the search button click
     */
    async function handleSearch() {
        const query = queryInput.value.trim();
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.style.display = 'flex';
        resultsContainer.innerHTML = '';
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    category: categorySelect.value,
                    tone: toneSelect.value
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const recommendations = await response.json();
            displayResults(recommendations);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            resultsContainer.innerHTML = `
                <div class="error-message">
                    <p>Sorry, there was an error fetching recommendations. Please try again.</p>
                    <p>Error: ${error.message}</p>
                </div>
            `;
        } finally {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
        }
    }
    
    /**
     * Display search results in the grid
     */
    function displayResults(books) {
        resultsContainer.innerHTML = '';
        
        if (books.length === 0) {
            resultsContainer.innerHTML = '<p class="no-results">No books found matching your criteria. Try a different search.</p>';
            return;
        }
        
        books.forEach(book => {
            const bookCard = document.createElement('div');
            bookCard.className = 'book-card';
            bookCard.innerHTML = `
                <div class="book-image">
                    <img src="${book.thumbnail}" alt="${book.title}">
                </div>
                <div class="book-info">
                    <div class="book-title">${book.title}</div>
                    <div class="book-authors">${book.authors}</div>
                    <div class="book-description">${book.description}</div>
                </div>
            `;
            
            // Add click event to show modal with book details
            bookCard.addEventListener('click', () => showBookDetails(book));
            
            resultsContainer.appendChild(bookCard);
        });
    }
    
    /**
     * Show book details in modal
     */
    function showBookDetails(book) {
        // Set modal content
        document.getElementById('modal-thumbnail').src = book.thumbnail;
        document.getElementById('modal-title').textContent = book.title;
        document.getElementById('modal-authors').textContent = `by ${book.authors}`;
        document.getElementById('modal-category').textContent = book.categories;
        document.getElementById('modal-description').textContent = book.full_description || book.description;
        
        // Set emotions
        const emotionsContainer = document.getElementById('modal-emotions');
        emotionsContainer.innerHTML = '';
        
        const emotions = [
            { name: 'joy', icon: 'fa-smile', label: 'Happy' },
            { name: 'sadness', icon: 'fa-sad-tear', label: 'Sad' },
            { name: 'anger', icon: 'fa-angry', label: 'Angry' },
            { name: 'fear', icon: 'fa-ghost', label: 'Suspenseful' },
            { name: 'surprise', icon: 'fa-surprise', label: 'Surprising' }
        ];
        
        // Sort emotions by score (descending)
        emotions.sort((a, b) => book.emotions[b.name] - book.emotions[a.name]);
        
        // Display top 3 emotions with highest scores
        emotions.slice(0, 3).forEach(emotion => {
            if (book.emotions[emotion.name] > 0.1) { // Only show if score is significant
                const emotionTag = document.createElement('div');
                emotionTag.className = 'emotion-tag';
                emotionTag.innerHTML = `
                    <i class="fas ${emotion.icon}"></i>
                    ${emotion.label}: ${Math.round(book.emotions[emotion.name] * 100)}%
                `;
                emotionsContainer.appendChild(emotionTag);
            }
        });
        
        // Show modal
        modal.style.display = 'block';
    }
});