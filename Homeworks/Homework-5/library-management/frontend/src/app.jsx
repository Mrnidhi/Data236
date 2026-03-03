import React, { useState } from "react";
import Home from "./pages/Home";
import CreateBook from "./pages/CreateBook";
import UpdateBook from "./pages/UpdateBook";

export default function App() {
  const [tab, setTab] = useState("home");

  const goTo = (nextTab) => setTab(nextTab);

  return (
    <div className="container py-4 app-shell">
      <div className="hero mb-3">
        <div className="d-flex align-items-start justify-content-between flex-wrap gap-2">
          <div>
            <h2 className="brand-title mb-1">Library Manager</h2>
            <p className="brand-subtitle">Manage books and authors in the library.</p>
          </div>
        </div>

        <div className="mt-3">
          <ul className="nav nav-pills gap-2">
            <li className="nav-item">
              <button className={`nav-link ${tab === "home" ? "active" : ""}`} onClick={() => goTo("home")}>
                Books
              </button>
            </li>
            <li className="nav-item">
              <button className={`nav-link ${tab === "create" ? "active" : ""}`} onClick={() => goTo("create")}>
                Create Book
              </button>
            </li>
            <li className="nav-item">
              <button className={`nav-link ${tab === "update" ? "active" : ""}`} onClick={() => goTo("update")}>
                Update Book
              </button>
            </li>
          </ul>
        </div>
      </div>

      {tab === "home" && <Home />}
      {tab === "create" && <CreateBook goTo={goTo} />}
      {tab === "update" && <UpdateBook />}

      <div className="mt-4 footer-note">
      </div>
    </div>
  );
}