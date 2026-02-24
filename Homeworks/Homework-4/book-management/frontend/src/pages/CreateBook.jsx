import React, { useState } from "react";

export default function CreateBook({ onAdd }) {
    const [title, setTitle] = useState("");
    const [author, setAuthor] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();
        await onAdd({ title, author });
    }

    return (
        <div className="card">
            <div className="card-header">
                <div className="page-title">Add Book</div>
                <div className="subtitle">Enter the book details below</div>
            </div>

            <div className="card-body">
                <form className="form" onSubmit={handleSubmit}>
                    <label>
                        Book Title
                        <input
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Enter book title"
                        />
                    </label>

                    <label>
                        Author Name
                        <input
                            value={author}
                            onChange={(e) => setAuthor(e.target.value)}
                            placeholder="Enter author name"
                        />
                    </label>

                    <button className="btn primary" type="submit">
                        Add Book
                    </button>
                </form>
            </div>
        </div>
    );
}
