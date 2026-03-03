import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createBook, fetchBooks } from "../features/books/booksSlice";
import { api } from "../api/axios";

export default function CreateBook({ goTo }) {
    const dispatch = useDispatch();
    const { error } = useSelector((s) => s.books);

    const [authors, setAuthors] = useState([]);
    const [authMsg, setAuthMsg] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const [form, setForm] = useState({
        title: "",
        isbn: "",
        publication_year: 2026,
        available_copies: 1,
        author_id: 0
    });

    const loadAuthors = async () => {
        setAuthMsg("");
        try {
            const res = await api.get("/authors?skip=0&limit=50");
            setAuthors(res.data);
            if (res.data.length > 0) setForm((p) => ({ ...p, author_id: res.data[0].id }));
            else setAuthMsg("No authors found. Create one first.");
        } catch (err) {
            setAuthMsg("Could not load authors.");
            setAuthors([]);
            setForm((p) => ({ ...p, author_id: 0 }));
        }
    };

    useEffect(() => {
        loadAuthors();
    }, []);

    const onChange = (e) => {
        setSuccessMsg("");
        const { name, value } = e.target;
        setForm((p) => ({
            ...p,
            [name]: ["publication_year", "available_copies", "author_id"].includes(name) ? Number(value) : value
        }));
    };

    const onSubmit = async (e) => {
        e.preventDefault();
        setSuccessMsg("");
        setSubmitting(true);
        try {
            const created = await dispatch(createBook(form)).unwrap();
            dispatch(fetchBooks());
            setSuccessMsg(`Book created: ${created.isbn} — ${created.title}`);
            setForm((p) => ({
                ...p,
                title: "",
                isbn: "",
                publication_year: 2026,
                available_copies: 1
            }));
            if (goTo) {
                setTimeout(() => goTo("home"), 700);
            }
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="card card-clean">
            <div className="card-header">
                <div className="fw-bold">Create Book</div>
                <div className="small-hint">Add a book linked to an author.</div>
            </div>

            <div className="card-body">
                {authMsg && <div className="alert alert-warning alert-clean py-2 mb-3">{authMsg}</div>}
                {error && <div className="alert alert-danger alert-clean py-2 mb-3">{String(error)}</div>}
                {successMsg && <div className="alert alert-success alert-clean py-2 mb-3">{successMsg}</div>}

                <form onSubmit={onSubmit} className="row g-3">
                    <div className="col-12">
                        <label className="form-label">Title</label>
                        <input className="form-control" name="title" value={form.title} onChange={onChange} required />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">ISBN (unique)</label>
                        <input className="form-control" name="isbn" value={form.isbn} onChange={onChange} required />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">Publication Year</label>
                        <input className="form-control" type="number" name="publication_year" value={form.publication_year} onChange={onChange} required />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">Available Copies</label>
                        <input className="form-control" type="number" name="available_copies" value={form.available_copies} onChange={onChange} required />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">Author</label>
                        <div className="d-flex gap-2">
                            <select
                                className="form-select"
                                name="author_id"
                                value={form.author_id}
                                onChange={onChange}
                                disabled={authors.length === 0}
                            >
                                {authors.length === 0 && <option value={0}>No authors</option>}
                                {authors.map((a) => (
                                    <option key={a.id} value={a.id}>
                                        {a.id} — {a.first_name} {a.last_name}
                                    </option>
                                ))}
                            </select>

                            <button type="button" className="btn btn-soft" onClick={loadAuthors} title="Reload authors">
                                ↻
                            </button>
                        </div>
                    </div>

                    <div className="col-12 d-flex gap-2">
                        <button className="btn btn-brand" disabled={form.author_id === 0 || submitting}>
                            {submitting ? "Creating..." : "Create"}
                        </button>

                        <button
                            type="button"
                            className="btn btn-soft"
                            onClick={() =>
                                setForm((p) => ({
                                    ...p,
                                    title: "",
                                    isbn: "",
                                    publication_year: 2026,
                                    available_copies: 1
                                }))
                            }
                            disabled={submitting}
                        >
                            Clear
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
