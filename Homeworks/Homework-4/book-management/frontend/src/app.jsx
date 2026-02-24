import React, { useEffect, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";

import Navbar from "./components/Navbar.jsx";

import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import CreateBook from "./pages/CreateBook.jsx";
import UpdateBook from "./pages/UpdateBook.jsx";
import DeleteBook from "./pages/DeleteBook.jsx";

import { fetchBooks, createBook, updateBook, deleteBook, me, logout as apiLogout } from "./api/booksApi.js";

export default function App() {
  const navigate = useNavigate();

  // Auth guard — renders children only when logged in
  function RequireAuth({ auth, children }) {
    if (!auth.loggedIn) {
      return (
        <div className="card">
          <div className="card-header">
            <div className="page-title">Login Required</div>
          </div>
          <div className="card-body">
            <div className="notice">Please login to access this page.</div>
          </div>
        </div>
      );
    }
    return children;
  }

  // Auth state — the cookie session is verified via /auth/me on page load
  const [auth, setAuth] = useState({ loggedIn: false, userId: null });

  // Books data
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);

  // Check if user already has a valid session (e.g. page refresh)
  useEffect(() => {
    (async () => {
      try {
        const data = await me();
        setAuth({ loggedIn: true, userId: data.user_id });
      } catch {
        setAuth({ loggedIn: false, userId: null });
      }
    })();
  }, []);

  // Fetch books whenever login state changes
  useEffect(() => {
    (async () => {
      if (!auth.loggedIn) {
        setBooks([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await fetchBooks();
        setBooks(data);
      } catch (e) {
        console.error("fetchBooks failed:", e);
      } finally {
        setLoading(false);
      }
    })();
  }, [auth.loggedIn]);

  // Create book (passed as prop to CreateBook)
  async function onAdd(newBook) {
    const created = await createBook(newBook);
    setBooks((prev) => [...prev, created]);
    navigate("/");
  }

  // Update book (passed as prop to UpdateBook)
  async function onUpdate(id, updatedBook) {
    const updated = await updateBook(id, updatedBook);
    setBooks((prev) => prev.map((b) => (b.id === id ? updated : b)));
    navigate("/");
  }

  // Delete book (passed as prop to DeleteBook)
  async function onDelete(id) {
    await deleteBook(id);
    setBooks((prev) => prev.filter((b) => b.id !== id));
    navigate("/");
  }

  // Logout handler
  async function handleLogout() {
    try {
      await apiLogout();
    } finally {
      setAuth({ loggedIn: false, userId: null });
    }
  }

  return (
    <div className="container">
      <Navbar auth={auth} />

      {/* Login / Logout bar */}
      <div className="loginbar">
        {auth.loggedIn ? (
          <>
            <div className="loginbar-text">
              ✅ Logged in as <b>User ID {auth.userId}</b>
            </div>
            <button className="btn danger" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <div className="loginbar-text">
            🔒 Not logged in — use the Login page below.
          </div>
        )}
      </div>

      <Routes>
        <Route path="/" element={<Home books={books} loading={loading} auth={auth} />} />
        <Route path="/login" element={<Login setAuth={setAuth} />} />
        <Route path="/create" element={<RequireAuth auth={auth}><CreateBook onAdd={onAdd} /></RequireAuth>} />
        <Route path="/update/:id" element={<RequireAuth auth={auth}><UpdateBook onUpdate={onUpdate} /></RequireAuth>} />
        <Route path="/delete/:id" element={<RequireAuth auth={auth}><DeleteBook onDelete={onDelete} /></RequireAuth>} />
      </Routes>
    </div>
  );
}