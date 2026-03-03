import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { updateBook } from "../features/books/booksSlice";
import { api } from "../api/axios";

export default function UpdateBook() {
    const dispatch = useDispatch();
    const { error } = useSelector((s) => s.books);

    const [authors, setAuthors] = useState([]);
    const [authMsg, setAuthMsg] = useState("");

    const [id, setId] = useState(1);
    const [payload, setPayload] = useState({
        title: "",
        isbn: "",
        publication_year: "",
        available_copies: "",
        author_id: ""
    });

    const loadAuthors = async () => {
        setAuthMsg("");
        try {
            const res = await api.get("/authors?skip=0&limit=50");
            setAuthors(res.data);
        } catch (err) {
            setAuthMsg("Could not load authors.");
            setAuthors([]);
        }
    };

    useEffect(() => {
        loadAuthors();
    }, []);

    const onChange = (e) => {
        const { name, value } = e.target;
        setPayload((p) => ({ ...p, [name]: value }));
    };

    const onSubmit = (e) => {
        e.preventDefault();
        const clean = {};
        for (const [k, v] of Object.entries(payload)) {
            if (v === "") continue;
            clean[k] = ["publication_year", "available_copies", "author_id"].includes(k) ? Number(v) : v;
        }
        dispatch(updateBook({ id: Number(id), payload: clean }));
    };

    return (
        <div className="card card-clean">
            <div className="card-header">
                <div className="fw-bold">Update Book</div>
                <div className="small-hint">Update fields for a book by ID (only filled fields are sent).</div>
            </div>

            <div className="card-body">
                {authMsg && <div className="alert alert-warning alert-clean py-2 mb-3">{authMsg}</div>}
                {error && <div className="alert alert-danger alert-clean py-2 mb-3">{String(error)}</div>}

                <form onSubmit={onSubmit} className="row g-3">
                    <div className="col-12">
                        <label className="form-label">Book ID</label>
                        <input className="form-control" type="number" value={id} onChange={(e) => setId(e.target.value)} />
                    </div>

                    <div className="col-12">
                        <label className="form-label">New Title (optional)</label>
                        <input className="form-control" name="title" value={payload.title} onChange={onChange} />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">New ISBN (optional, unique)</label>
                        <input className="form-control" name="isbn" value={payload.isbn} onChange={onChange} />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">New Year (optional)</label>
                        <input className="form-control" type="number" name="publication_year" value={payload.publication_year} onChange={onChange} />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">New Copies (optional)</label>
                        <input className="form-control" type="number" name="available_copies" value={payload.available_copies} onChange={onChange} />
                    </div>

                    <div className="col-md-6">
                        <label className="form-label">New Author (optional)</label>
                        <div className="d-flex gap-2">
                            <select className="form-select" name="author_id" value={payload.author_id} onChange={onChange}>
                                <option value="">(no change)</option>
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
                        <button className="btn btn-brand">Update</button>
                        <button
                            type="button"
                            className="btn btn-soft"
                            onClick={() => setPayload({ title: "", isbn: "", publication_year: "", available_copies: "", author_id: "" })}
                        >
                            Clear
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
