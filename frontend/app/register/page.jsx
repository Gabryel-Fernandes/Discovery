"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import "../login/auth.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Register() {
  const router = useRouter();
  const [etapa, setEtapa] = useState("cadastro"); // "cadastro" | "verificacao"
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [codigo, setCodigo] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [carregando, setCarregando] = useState(false);

  const handleCadastro = async (e) => {
    e.preventDefault();
    setErro("");

    if (senha !== confirmarSenha) {
      setErro("As senhas não conferem");
      return;
    }
    if (senha.length < 8) {
      setErro("A senha precisa ter no mínimo 8 caracteres");
      return;
    }

    setCarregando(true);
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nome,
          email,
          senha,
          confirmar_senha: confirmarSenha,
        }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Erro ao cadastrar");
      }

      setSucesso("Código enviado para o seu email");
      setEtapa("verificacao");
    } catch (err) {
      setErro(err.message);
    } finally {
      setCarregando(false);
    }
  };

  const handleVerificacao = async (e) => {
    e.preventDefault();
    setErro("");
    setCarregando(true);

    try {
      const res = await fetch(`${API_URL}/auth/verify-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, codigo }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Código inválido");
      }

      router.push("/login");
    } catch (err) {
      setErro(err.message);
    } finally {
      setCarregando(false);
    }
  };

  const handleReenviar = async () => {
    setErro("");
    setSucesso("");
    try {
      const res = await fetch(`${API_URL}/auth/resend-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setSucesso("Novo código enviado");
    } catch (err) {
      setErro(err.message);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-left">
        <h1>
          Junte-se à <strong>rede</strong>
          <br />
          de combate a <strong>fraudes</strong>
        </h1>
      </div>

      <div className="auth-right">
        {etapa === "cadastro" ? (
          <form className="auth-card" onSubmit={handleCadastro}>
            <div className="auth-logo">discovery</div>

            {erro && <div className="auth-banner error">{erro}</div>}

            <div className="auth-field">
              <label>
                Nome de usuário <span className="required">*</span>
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                required
              />
            </div>

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

            <div className="auth-field">
              <label>
                Confirmar senha <span className="required">*</span>
              </label>
              <input
                type={mostrarSenha ? "text" : "password"}
                value={confirmarSenha}
                onChange={(e) => setConfirmarSenha(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={carregando}
            >
              {carregando ? "CADASTRANDO..." : "CADASTRAR"}
            </button>

            <div className="auth-switch">
              Já tem conta?{" "}
              <button type="button" onClick={() => router.push("/login")}>
                Fazer login
              </button>
            </div>
          </form>
        ) : (
          <form className="auth-card" onSubmit={handleVerificacao}>
            <div className="auth-logo">discovery</div>

            <p style={{ color: "#9a9a9a", fontSize: 14 }}>
              Enviamos um código de 6 dígitos para <strong>{email}</strong>
            </p>

            {sucesso && <div className="auth-banner success">{sucesso}</div>}
            {erro && <div className="auth-banner error">{erro}</div>}

            <div className="auth-field">
              <label>Código de verificação</label>
              <input
                type="text"
                maxLength={6}
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
                style={{ textAlign: "center", fontSize: 20, letterSpacing: 4 }}
                required
              />
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={carregando}
            >
              {carregando ? "VERIFICANDO..." : "CONFIRMAR"}
            </button>

            <button type="button" className="auth-link" onClick={handleReenviar}>
              Reenviar código
            </button>
          </form>
        )}
      </div>
    </div>
  );
}