"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import "./searchBar.css";

export default function SearchBar({ placeholder }) {
  const router = useRouter();
  const [busca, setBusca] = useState("");
  const [modalAberto, setModalAberto] = useState(false);
  const [filtroFonte, setFiltroFonte] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");

  const handleEnter = (e) => {
    if (e.key === "Enter" && busca.trim()) {
      const params = new URLSearchParams();
      params.set("busca", busca);
      if (filtroFonte) params.set("fonte", filtroFonte);
      if (filtroTipo) params.set("tipo", filtroTipo);
      if (dataInicio) params.set("data_inicio", dataInicio);
      if (dataFim) params.set("data_fim", dataFim);
      router.push(`/list?${params.toString()}`);
    }
  };

  const aplicarFiltros = () => {
    const params = new URLSearchParams();
    if (busca) params.set("busca", busca);
    if (filtroFonte) params.set("fonte", filtroFonte);
    if (filtroTipo) params.set("tipo", filtroTipo);
    if (dataInicio) params.set("data_inicio", dataInicio);
    if (dataFim) params.set("data_fim", dataFim);
    router.push(`/list?${params.toString()}`);
    setModalAberto(false);
  };

  const limparFiltros = () => {
    setFiltroFonte("");
    setFiltroTipo("");
    setDataInicio("");
    setDataFim("");
    setBusca("");
  };

  return (
    <>
      <div className="search">
        <input
          type="text"
          placeholder={placeholder}
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          onKeyDown={handleEnter}
        />
        <i
          className="fa-solid fa-filter"
          onClick={() => setModalAberto(true)}
          style={{ cursor: "pointer" }}
        ></i>
      </div>

      {modalAberto && (
        <div className="modal-overlay" onClick={() => setModalAberto(false)}>
          <div className="modal-filtro" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Filtrar Casos</h3>
              <i
                className="fa-solid fa-xmark"
                onClick={() => setModalAberto(false)}
              ></i>
            </div>

            <div className="modal-body">
              <label>Período</label>
              <div className="modal-periodo">
                <input
                  type="date"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  placeholder="Data início"
                />
                <span>até</span>
                <input
                  type="date"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  placeholder="Data fim"
                />
              </div>

              <label>Fonte</label>
              <select
                value={filtroFonte}
                onChange={(e) => setFiltroFonte(e.target.value)}
              >
                <option value="">Todas as fontes</option>
                <option value="manual">Manual</option>
                <option value="facebook">Facebook</option>
                <option value="instagram">Instagram</option>
                <option value="whatsapp">WhatsApp</option>
              </select>

              <label>Tipo de golpe</label>
              <input
                type="text"
                placeholder="Ex: phishing, golpe_pix..."
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
              />
            </div>

            <div className="modal-footer">
              <button className="btn-limpar" onClick={limparFiltros}>
                Limpar
              </button>
              <button className="btn-aplicar" onClick={aplicarFiltros}>
                Aplicar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
