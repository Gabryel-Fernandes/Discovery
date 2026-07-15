"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Menu from "../components/menu/Menu";
import SearchBar from "../components/search/SearchBar";
import Medidor from "../components/medidor/Medidor";
import "./dashboard.css";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const router = useRouter();
  const [casos, setCasos] = useState([]);
  const [casoAtivo, setCasoAtivo] = useState(0);
  const [analise, setAnalise] = useState(null);
  const [estatisticas, setEstatisticas] = useState([]);
  const [tiposGolpe, setTiposGolpe] = useState([]);
  const [filtroFonte, setFiltroFonte] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  const [filtroAno, setFiltroAno] = useState("2026");
  const [filtroMes, setFiltroMes] = useState("01");
  const [filtroDia, setFiltroDia] = useState("01");
  const [fontes, setFontes] = useState({
    facebook: 0,
    instagram: 0,
    whatsapp: 0,
    telegram: 0,
    tiktok: 0,
    web: 0,
    manual: 0,
  });

  const buscarTudo = (
    fonte = filtroFonte,
    tipo = filtroTipo,
    ano = filtroAno,
    mes = filtroMes,
    dia = filtroDia,
  ) => {
    const dataInicio = `${ano}-${mes}-${dia}`;
    const params = new URLSearchParams();
    params.set("data_inicio", dataInicio);
    if (fonte) params.set("fonte", fonte);
    if (tipo) params.set("tipo_golpe", tipo);

    // Busca estatísticas
    fetch(`${API_URL}/casos/estatisticas?${params.toString()}`)
      .then((res) => res.json())
      .then((data) => setEstatisticas(Array.isArray(data) ? data : []))
      .catch(console.error);

    fetch(`${API_URL}/casos/recentes?data_inicio=${dataInicio}`)
      .then((res) => res.json())
      .then((data) => {
        setCasos(data);
        setCasoAtivo(0);
        if (data.length > 0) carregarAnalise(data[0].id);
        else setAnalise(null);
      })
      .catch(console.error);

    fetch(`${API_URL}/casos?data_inicio=${dataInicio}`)
      .then((res) => res.json())
      .then((data) => {
        const contagem = {
          facebook: 0,
          instagram: 0,
          whatsapp: 0,
          telegram: 0,
          tiktok: 0,
          web: 0,
          manual: 0,
        };
        data.forEach((caso) => {
          const f = caso.fonte?.toLowerCase();
          if (contagem[f] !== undefined) contagem[f]++;
        });
        setFontes(contagem);
      })
      .catch(console.error);
  };

  useEffect(() => {
    buscarTudo();
    fetch(`${API_URL}/casos/tipos-golpe`)
      .then((res) => res.json())
      .then((data) => setTiposGolpe(Array.isArray(data) ? data : []))
      .catch(console.error);
  }, []);

  const carregarAnalise = async (casoId) => {
    try {
      const res = await fetch(`${API_URL}/analises/caso/${casoId}`);
      const data = await res.json();
      setAnalise(data[0] || null);
    } catch (e) {
      setAnalise(null);
    }
  };

  const selecionarCaso = (index) => {
    setCasoAtivo(index);
    carregarAnalise(casos[index].id);
  };

  const casoSelecionado = casos[casoAtivo] || null;
  const veracidade = analise?.veracidade
    ? Math.round(analise.veracidade * 100)
    : 0;
  const risco =
    veracidade >= 60 ? "ALTO" : veracidade >= 30 ? "MÉDIO" : "BAIXO";

  const dadosRosca = [
    {
      name: "Links suspeitos",
      value: analise?.links_suspeitos || 0,
      fill: "#41b8b5",
    },
    {
      name: "Erros ortográficos",
      value: analise?.erros_ortograficos || 0,
      fill: "#4CAF50",
    },
    {
      name: "Uso de IA",
      value: analise?.uso_ia_generativa || 0,
      fill: "#f44336",
    },
    {
      name: "Taxonomia",
      value: analise?.taxonomia_repetitiva || 0,
      fill: "#cc00ff",
    },
  ];

  const totalCasos = Array.isArray(estatisticas)
    ? estatisticas.reduce((acc, e) => acc + e.total, 0)
    : 0;
  const totalGolpe =
    estatisticas.find((e) => e.situacao === "Alta chance de golpe")?.total || 0;
  const porcentagemGolpe =
    totalCasos > 0 ? Math.round((totalGolpe / totalCasos) * 100) : 0;

  return (
    <div className="dashboard">
      <Menu />
      <div className="contente-geral">
        <div className="search-interactions">
          <div className="periodo">
            <span>Casos a partir de:</span>
            <div className="periodo-selects">
              <select
                value={filtroDia}
                onChange={(e) => {
                  setFiltroDia(e.target.value);
                  buscarTudo(
                    filtroFonte,
                    filtroTipo,
                    filtroAno,
                    filtroMes,
                    e.target.value,
                  );
                }}
              >
                {Array.from({ length: 31 }, (_, i) =>
                  String(i + 1).padStart(2, "0"),
                ).map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
              <select
                value={filtroMes}
                onChange={(e) => {
                  setFiltroMes(e.target.value);
                  buscarTudo(
                    filtroFonte,
                    filtroTipo,
                    filtroAno,
                    e.target.value,
                    filtroDia,
                  );
                }}
              >
                {Array.from({ length: 12 }, (_, i) =>
                  String(i + 1).padStart(2, "0"),
                ).map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
              <select
                value={filtroAno}
                onChange={(e) => {
                  setFiltroAno(e.target.value);
                  buscarTudo(
                    filtroFonte,
                    filtroTipo,
                    e.target.value,
                    filtroMes,
                    filtroDia,
                  );
                }}
              >
                <option value="2025">2025</option>
                <option value="2026">2026</option>
              </select>
            </div>
          </div>
          <SearchBar placeholder="BUSQUE SEU CASO AQUI" />
          <button className="sair">
            <i className="fa-solid fa-right-from-bracket"></i>
            SAIR
          </button>
        </div>

        <div className="data-dashboard">
          <div className="casos-rapidos">
            <div className="casos-tabs">
              <div>
                <span>Casos analisados</span>
              </div>
              <div className="tabs">
                {casos.length > 0 ? (
                  casos.map((caso, index) => (
                    <button
                      key={caso.id}
                      className={index === casoAtivo ? "active" : "inativo"}
                      onClick={() => selecionarCaso(index)}
                    >
                      Caso {index + 1}
                    </button>
                  ))
                ) : (
                  <>
                    <button className="active">Caso 1</button>
                    <button className="inativo">Caso 2</button>
                    <button className="inativo">Caso 3</button>
                  </>
                )}
                <button
                  className="inativo"
                  onClick={() => router.push("/list")}
                >
                  MAIS &gt;
                </button>
              </div>
            </div>

            <div className="result-graficos">
              <div className="card-grafico">
                <Medidor
                  veracidade={veracidade}
                  risco={analise ? risco : null}
                  tamanho="pequeno"
                />
              </div>
              <div className="card-grafico">
                {analise ? (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <PieChart width={100} height={100}>
                      <Pie
                        data={dadosRosca}
                        cx={45}
                        cy={45}
                        innerRadius={25}
                        outerRadius={45}
                        dataKey="value"
                      >
                        {dadosRosca.map((entry, index) => (
                          <Cell key={index} fill={entry.fill} />
                        ))}
                      </Pie>
                    </PieChart>
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "4px",
                        fontSize: "11px",
                      }}
                    >
                      {dadosRosca.map((item, index) => (
                        <span
                          key={index}
                          style={{ color: item.fill, fontWeight: "bold" }}
                        >
                          {item.value} {item.name}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <span style={{ color: "#838383", fontSize: 13 }}>
                    Sem análise
                  </span>
                )}
              </div>
            </div>

            <div className="descricao-caso">
              <h3>Descrição de caso</h3>
              <label>Caminho da publicação</label>
              <input type="text" value={casoSelecionado?.url || ""} readOnly />
              <label>Fonte da publicação</label>
              <input
                type="text"
                value={casoSelecionado?.fonte || ""}
                readOnly
              />
              <label>Legenda usada</label>
              <textarea
                rows={6}
                value={casoSelecionado?.legenda || ""}
                readOnly
              ></textarea>
            </div>
          </div>

          <div className="grafics">
            <ul className="distribution">
              <li className="Manual">
                <span>MANUAL</span>
                <span>
                  {fontes.manual > 0
                    ? `${fontes.manual} casos`
                    : "Fonte vazia • 0 casos"}
                </span>
              </li>
              <li  className="telegram ">
                <span>TELEGRAM</span>
                <span>
                  {fontes.telegram > 0
                    ? `${fontes.telegram} casos`
                    : "Fonte vazia • 0 casos"}
                </span>
              </li>
              <li>
                <span className="x">Twitter(X)</span>
                <span>Fonte vazia • 0 casos</span>
              </li>
              <li>
                <span>FONTE 4</span>
                <span>Fonte vazia • 0 casos</span>
              </li>
              <li>
                <span>FONTE 5</span>
                <span>Fonte vazia • 0 casos</span>
              </li>
              <li>
                <span>FONTE 6</span>
                <span>Fonte vazia • 0 casos</span>
              </li>
            </ul>

            <div className="grafic-bar">
              <BarChart width={300} height={200} data={estatisticas}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="situacao"
                  tick={{ fontSize: 10 }}
                  interval={0}
                />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total">
                  {Array.isArray(estatisticas) &&
                    estatisticas.map((entry, index) => (
                      <Cell key={index} fill={entry.cor} />
                    ))}
                </Bar>
              </BarChart>

              <div className="filter">
                <div className="filter-data">
                  <select
                    value={filtroDia}
                    onChange={(e) => {
                      setFiltroDia(e.target.value);
                      buscarTudo(
                        filtroFonte,
                        filtroTipo,
                        filtroAno,
                        filtroMes,
                        e.target.value,
                      );
                    }}
                  >
                    {Array.from({ length: 31 }, (_, i) =>
                      String(i + 1).padStart(2, "0"),
                    ).map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                  <select
                    value={filtroMes}
                    onChange={(e) => {
                      setFiltroMes(e.target.value);
                      buscarTudo(
                        filtroFonte,
                        filtroTipo,
                        filtroAno,
                        e.target.value,
                        filtroDia,
                      );
                    }}
                  >
                    {Array.from({ length: 12 }, (_, i) =>
                      String(i + 1).padStart(2, "0"),
                    ).map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                  <select
                    value={filtroAno}
                    onChange={(e) => {
                      setFiltroAno(e.target.value);
                      buscarTudo(
                        filtroFonte,
                        filtroTipo,
                        e.target.value,
                        filtroMes,
                        filtroDia,
                      );
                    }}
                  >
                    <option value="2025">2025</option>
                    <option value="2026">2026</option>
                  </select>
                </div>

                <select
                  className="filter-option"
                  value={filtroFonte}
                  onChange={(e) => {
                    setFiltroFonte(e.target.value);
                    buscarTudo(e.target.value, filtroTipo);
                  }}
                >
                  <option value="">Fonte Analisada</option>
                  <option value="manual">Manual</option>
                </select>

                <select
                  className="filter-option"
                  value={filtroTipo}
                  onChange={(e) => {
                    setFiltroTipo(e.target.value);
                    buscarTudo(filtroFonte, e.target.value);
                  }}
                >
                  <option value="">Tipo de golpe</option>
                  {tiposGolpe.map((tipo, index) => (
                    <option key={index} value={tipo}>
                      {tipo}
                    </option>
                  ))}
                </select>

                <button className="verocimio">{porcentagemGolpe}% GOLPE</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
