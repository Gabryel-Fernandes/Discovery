"use client";
import "./menu.css";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function Menu({ usuario }) {
  const pathname = usePathname();
  const [aberto, setAberto] = useState(false);

  return (
    <>
      {}
      <div className="mobile-topbar">
        <img className="logo-mobile" src="/discovery_logo.svg" alt="Logo" />
        <button
          className="hamburger"
          onClick={() => setAberto(!aberto)}
          aria-label="Abrir menu"
        >
          <i className={`fa-solid ${aberto ? "fa-xmark" : "fa-bars"}`}></i>
        </button>
      </div>

      {}
      {aberto && (
        <div className="menu-overlay" onClick={() => setAberto(false)} />
      )}

      <div className={`container-menu ${aberto ? "menu-open" : ""}`}>
        <nav className="menu">
          <div className="container-logo">
            <img className="logo" src="/discovery_logo.svg" alt="" />
          </div>

          <div className="profile">
            <img src="/icon_profile.svg" alt="" />
            <h1>{usuario?.nome || "NOME DO USUARIO"}</h1>
            <span>{usuario?.email || "Função"}</span>
          </div>

          <div className="bloc">
            <div className="dashboard-container">
              <h2>DASHBOARD</h2>
              <Link
                href="/dashboard"
                className={`local ${pathname === "/dashboard" ? "ativo" : ""}`}
                onClick={() => setAberto(false)}
              >
                <i className="fa-solid fa-gauge"></i>
                <span>Visão Geral</span>
              </Link>
            </div>
            <h2>SERVICES</h2>
            <Link
              href="/manual_analysis"
              className={`local ${pathname === "/manual_analysis" ? "ativo" : ""}`}
              onClick={() => setAberto(false)}
            >
              <i className="fa-solid fa-robot"></i>
              <span>Analise Manual</span>
            </Link>
            <Link
              href="/list"
              className={`local ${pathname === "/list" ? "ativo" : ""}`}
              onClick={() => setAberto(false)}
            >
              <i className="fa-solid fa-list"></i>
              <span>Lista de Casos</span>
            </Link>
          </div>

          <footer className="rodape">
            <img src="/UFG_ICON.svg" alt="" />
            <img src="/ANATEL.svg" alt="" />
          </footer>
        </nav>
      </div>
    </>
  );
}