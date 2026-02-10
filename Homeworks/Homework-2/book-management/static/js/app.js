const API_URL = '/api/books';

document.addEventListener('DOMContentLoaded', () => {
    loadBooks();
});

async function loadBooks() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Failed to fetch books');
        const books = await response.json();
        displayBooks(books);
    } catch (error) {
        console.error('Error loading books:', error);
        alert('Failed to load books');
    }
}

function displayBooks(books) {
    const tbody = document.getElementById('bookTableBody');
    tbody.innerHTML = '';

    if (books.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="3" style="text-align:center; color:#888;">No books found</td>';
        tbody.appendChild(row);
        return;
    }

    books.forEach(book => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${book.id}</td>
            <td>${book.title}</td>
            <td>${book.author}</td>
        `;
        tbody.appendChild(row);
    });
}

async function addBook() {
    const titleInput = document.getElementById('createTitle');
    const authorInput = document.getElementById('createAuthor');
    const title = titleInput.value.trim();
    const author = authorInput.value.trim();

    if (!title || !author) {
        alert('Please enter both title and author');
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, author })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add book');
        }

        const newBook = await response.json();
        titleInput.value = '';
        authorInput.value = '';
        await loadBooks();
        alert(`Book "${newBook.title}" added successfully!`);
    } catch (error) {
        console.error('Error adding book:', error);
        alert('Failed to add book: ' + error.message);
    }
}

async function updateBookOne() {
    try {
        const response = await fetch(`${API_URL}/1`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update book');
        }

        await loadBooks();
        alert('Book ID 1 updated to "Harry Potter" by "J.K Rowling"!');
    } catch (error) {
        console.error('Error updating book:', error);
        alert('Failed to update book: ' + error.message);
    }
}

async function deleteMaxBook() {
    try {
        const response = await fetch(`${API_URL}/max`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            let msg = 'Failed to delete book';
            try { const err = await response.json(); msg = err.detail || msg; } catch (e) { }
            throw new Error(msg);
        }

        await loadBooks();
        alert('Book with highest ID deleted!');
    } catch (error) {
        console.error('Error deleting book:', error);
        alert('Failed to delete book: ' + error.message);
    }
}

async function searchBooks() {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) {
        await loadBooks();
        return;
    }

    try {
        const response = await fetch(`${API_URL}?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Search failed');
        const books = await response.json();
        displayBooks(books);
    } catch (error) {
        console.error('Error searching books:', error);
        alert('Search failed');
    }
}

async function clearSearch() {
    document.getElementById('searchQuery').value = '';
    await loadBooks();
}
