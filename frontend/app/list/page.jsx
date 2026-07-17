"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Menu from "../components/menu/Menu";
import ReturnButton from "../components/back/ReturnButton";
import SearchBar from "../components/search/SearchBar";
import "./list.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function List() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [casos, setCasos] = useState([]);
  const [pagina, setPagina] = useState(1);
  const itensPorPagina = 10;

  useEffect(() => {
    const busca = searchParams.get("busca") || "";
    const fonte = searchParams.get("fonte") || "";
    const tipo = searchParams.get("tipo") || "";
    const dataInicio = searchParams.get("data_inicio") || "";
    const dataFim = searchParams.get("data_fim") || "";

    const params = new URLSearchParams();
    if (busca) params.set("titulo", busca);
    if (fonte) params.set("fonte", fonte);
    if (tipo) params.set("tipo_golpe", tipo);
    if (dataInicio) params.set("data_inicio", dataInicio);
    if (dataFim) params.set("data_fim", dataFim);

    const url = `${API_URL}/casos${params.toString() ? `?${params.toString()}` : ""}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        setCasos(data);
        setPagina(1);
      })
      .catch(console.error);
  }, [searchParams]);

  const totalPaginas = Math.ceil(casos.length / itensPorPagina);
  const casosPagina = casos.slice(
    (pagina - 1) * itensPorPagina,
    pagina * itensPorPagina,
  );

  const formatarData = (dataStr) => {
    const data = new Date(dataStr);
    return `${String(data.getDate()).padStart(2, "0")}/${String(data.getMonth() + 1).padStart(2, "0")}\n${data.getFullYear()}`;
  };

  const corFonte = (fonte) => {
    const cores = {
      facebook: "facebook",
      instagram: "instagram",
      whatsapp: "whatsapp",
      telegram: "telegram",
      tiktok: "tiktok",
      manual: "manual",
    };
    return cores[fonte?.toLowerCase()] || "manual";
  };

  const busca = searchParams.get("busca");
  const fonte = searchParams.get("fonte");
  const dataInicio = searchParams.get("data_inicio");
  const dataFim = searchParams.get("data_fim");
  const temFiltro = busca || fonte || dataInicio || dataFim;

  return (
    <div className="dashboard-list">
      <Menu />
      <div className="list-contente">
        <div className="search-cases">
          <SearchBar placeholder="BUSQUE O CASO AQUI" />
          <ReturnButton />
        </div>

        {temFiltro && (
          <div className="filtros-ativos">
            <span>Filtros ativos:</span>
            {busca && <span className="tag-filtro">Busca: {busca}</span>}
            {fonte && <span className="tag-filtro">Fonte: {fonte}</span>}
            {dataInicio && <span className="tag-filtro">De: {dataInicio}</span>}
            {dataFim && <span className="tag-filtro">Até: {dataFim}</span>}
            <button onClick={() => router.push("/list")}>Limpar filtros</button>
          </div>
        )}

        <div className="list-data">
          <table className="cases-table">
            <thead>
              <tr>
                <th>DATA</th>
                <th>FONTE</th>
                <th>TITULO</th>
                <th>ESTIMATIVA</th>
              </tr>
            </thead>
            <tbody>
              {casosPagina.length > 0 ? (
                casosPagina.map((caso) => (
                  <tr
                    key={caso.id}
                    onClick={() => router.push(`/case/${caso.id}`)}
                    style={{ cursor: "pointer" }}
                  >
                    <td>
                      {formatarData(caso.data_publicacao)
                        .split("\n")
                        .map((linha, i) => (
                          <span key={i}>
                            {linha}
                            {i === 0 && <br />}
                          </span>
                        ))}
                    </td>
                    <td>
                      <span className={`fonte ${corFonte(caso.fonte)}`}>
                        {caso.fonte?.toUpperCase()}
                      </span>
                    </td>
                    <td>{caso.titulo?.substring(0, 30)}...</td>
                    <td>
                      <span className="situacao">{caso.situacao}</span>
                    </td>
                    <td></td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={5}
                    style={{
                      textAlign: "center",
                      padding: "20px",
                      color: "#838383",
                    }}
                  >
                    Nenhum caso encontrado
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          <div className="pagination">
            <button onClick={() => setPagina(1)} disabled={pagina === 1}>
              ⏮
            </button>
            <select
              value={pagina}
              onChange={(e) => setPagina(Number(e.target.value))}
            >
              {Array.from({ length: totalPaginas || 1 }, (_, i) => (
                <option key={i + 1} value={i + 1}>
                  Pag. {i + 1}
                </option>
              ))}
            </select>
            <button
              onClick={() => setPagina(totalPaginas)}
              disabled={pagina === totalPaginas}
            >
              ⏭
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
