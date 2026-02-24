import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchBookById } from "../api/booksApi.js";

export default function UpdateBook({ onUpdate }) {
    const { id } = useParams();
    const bookId = Number(id);

    const [title, setTitle] = useState("");
    const [author, setAuthor] = useState("");
    const [loading, setLoading] = useState(true);

    // Fetch current book data so the form is pre-populated
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const book = await fetchBookById(bookId);
                setTitle(book.title);
                setAuthor(book.author);
            } catch (e) {
                console.error("Failed to load book:", e);
            } finally {
                setLoading(false);
            }
        })();
    }, [bookId]);

    async function handleSubmit(e) {
        e.preventDefault();
        await onUpdate(bookId, { title, author });
    }

    if (loading) return <p>Loading book...</p>;

    return (
        <div className="card">
            <div className="card-header">
                <div className="page-title">Update Book (ID: {bookId})</div>
            </div>

            <div className="card-body">
                <form className="form" onSubmit={handleSubmit}>
                    <label>
                        Book Title
                        <input
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </label>

                    <label>
                        Author Name
                        <input
                            value={author}
                            onChange={(e) => setAuthor(e.target.value)}
                        />
                    </label>

                    <button className="btn primary" type="submit">
                        Update Book
                    </button>
                </form>
            </div>
        </div>
    );
}
