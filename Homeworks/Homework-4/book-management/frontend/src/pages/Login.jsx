import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login as apiLogin } from "../api/booksApi.js";

export default function Login({ setAuth }) {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        try {
            const res = await apiLogin(email, password);
            setAuth({ loggedIn: true, userId: res.user_id });
            setEmail("");
            setPassword("");
            navigate("/");
        } catch (err) {
            setError("Invalid email or password. Please try again.");
            console.error("Login failed:", err);
        }
    }

    return (
        <div className="card">
            <div className="card-header">
                <div className="page-title">Login</div>
            </div>

            <div className="card-body">
                {error && <div className="notice" style={{ marginBottom: "16px", color: "#991b1b" }}>{error}</div>}

                <form className="form" onSubmit={handleSubmit}>
                    <label>
                        Email
                        <input
                            type="email"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </label>

                    <label>
                        Password
                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </label>

                    <button className="btn primary" type="submit">
                        Login
                    </button>
                </form>
            </div>
        </div>
    );
}
