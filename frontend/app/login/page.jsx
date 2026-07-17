"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import "./auth.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro("");
    setCarregando(true);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Erro ao fazer login");
      }

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("usuario", JSON.stringify(data.usuario));
      router.push("/dashboard");
    } catch (err) {
      setErro(err.message);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-left">
        <h1>
          Verifique com <strong>confiança</strong>
          <br />
          antes de <strong>compartilhar</strong>
        </h1>
      </div>

      <div className="auth-right">
        <form className="auth-card" onSubmit={handleSubmit}>
          <div className="auth-logo">discovery</div>

          {erro && <div className="auth-banner error">{erro}</div>}

          <div className="auth-field">
            <label>
              Email <span className="required">*</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label>
              Senha <span className="required">*</span>
            </label>
            <div className="auth-input-wrapper">
              <input
                type={mostrarSenha ? "text" : "password"}
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                required
              />
              <button
                type="button"
                className="auth-toggle-visibility"
                onClick={() => setMostrarSenha(!mostrarSenha)}
              >
                {mostrarSenha ? "🙈" : "👁"}
              </button>
            </div>
          </div>

          <button type="submit" className="auth-submit" disabled={carregando}>
            {carregando ? "ENTRANDO..." : "LOGIN"}
          </button>

          <div className="auth-switch">
            Não tem conta?{" "}
            <button type="button" onClick={() => router.push("/register")}>
              Cadastre-se
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}