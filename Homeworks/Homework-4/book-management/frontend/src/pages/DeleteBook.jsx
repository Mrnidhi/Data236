import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchBookById } from "../api/booksApi.js";

export default function DeleteBook({ onDelete }) {
    const { id } = useParams();
    const bookId = Number(id);

    const [book, setBook] = useState(null);

    useEffect(() => {
        (async () => {
            try {
                const data = await fetchBookById(bookId);
                setBook(data);
            } catch {
                setBook(null);
            }
        })();
    }, [bookId]);

    async function handleDelete() {
        await onDelete(bookId);
    }

    return (
        <div className="card">
            <div className="card-header">
                <div className="page-title">Delete Book</div>
            </div>

            <div className="card-body">
                {book ? (
                    <>
                        <p style={{ fontSize: "18px", marginBottom: "24px" }}>
                            Are you sure you want to delete <strong>"{book.title}"</strong> by {book.author}?
                        </p>

                        <button className="btn danger" onClick={handleDelete}>
                            Delete Book
                        </button>
                    </>
                ) : (
                    <div className="notice">
                        Book not found (or already deleted).
                    </div>
                )}
            </div>
        </div>
    );
}
