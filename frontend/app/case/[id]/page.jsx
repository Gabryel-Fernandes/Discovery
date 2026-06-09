"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import ReturnButton from "../../components/back/ReturnButton";
import Menu from "../../components/menu/Menu";
import SearchBar from "../../components/search/SearchBar";
import "./case.css";
import { PieChart, Pie, Cell } from "recharts";
import jsPDF from "jspdf";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Cases() {
  const { id } = useParams();
  const [caso, setCaso] = useState(null);
  const [analise, setAnalise] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/casos/${id}`)
      .then((res) => res.json())
      .then((data) => setCaso(data))
      .catch(console.error);

    fetch(`${API_URL}/analises/caso/${id}`)
      .then((res) => res.json())
      .then((data) => setAnalise(data[0] || null))
      .catch(console.error);
  }, [id]);

  const dadosRosca = [
    { name: "Links suspeitos", value: analise?.links_suspeitos || 0, color: "#41b8b5" },
    { name: "Erros ortográficos", value: analise?.erros_ortograficos || 0, color: "#4CAF50" },
    { name: "Uso de IA generativa", value: analise?.uso_ia_generativa || 0, color: "#f44336" },
    { name: "Taxonomia repetitiva", value: analise?.taxonomia_repetitiva || 0, color: "#cc00ff" },
  ];

  const totalPontos = dadosRosca.reduce((acc, item) => acc + item.value, 0);
  const veracidade = analise?.veracidade ? Math.round(analise.veracidade * 100) : 0;

  const gerarPDF = () => {
    const doc = new jsPDF();
    const corPrimaria = [65, 184, 181];

    doc.setFillColor(...corPrimaria);
    doc.rect(0, 0, 210, 25, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.text("Discovery - Relatório de Caso", 14, 16);

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text(`Gerado em: ${new Date().toLocaleDateString("pt-BR")}`, 140, 16);

    doc.setTextColor(0, 0, 0);

    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Informações do Caso", 14, 40);

    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    doc.text(`Título: ${caso?.titulo || "N/A"}`, 14, 50);
    doc.text(`Fonte: ${caso?.fonte || "N/A"}`, 14, 58);
    doc.text(`Situação: ${caso?.situacao || "N/A"}`, 14, 66);
    doc.text(`Data: ${caso?.data_publicacao ? new Date(caso.data_publicacao).toLocaleDateString("pt-BR") : "N/A"}`, 14, 74);

    if (caso?.url) {
      doc.text(`URL: ${caso.url}`, 14, 82);
    }

    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Legenda do Post", 14, 96);

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    const legendaLinhas = doc.splitTextToSize(caso?.legenda || "N/A", 180);
    doc.text(legendaLinhas, 14, 106);

    const posYAnalise = 106 + legendaLinhas.length * 6 + 10;

    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Resultado da Análise", 14, posYAnalise);

    doc.setFillColor(...corPrimaria);
    doc.roundedRect(14, posYAnalise + 6, 80, 20, 3, 3, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text(`${veracidade}% Chance de Golpe`, 20, posYAnalise + 19);

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    doc.text(`Pontos totais suspeitos: ${totalPontos}`, 110, posYAnalise + 14);

    const posYIndicadores = posYAnalise + 36;

    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Indicadores", 14, posYIndicadores);

    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    dadosRosca.forEach((item, index) => {
      doc.text(`• ${item.name}: ${item.value}`, 14, posYIndicadores + 10 + index * 8);
    });

    doc.setFillColor(...corPrimaria);
    doc.rect(0, 282, 210, 15, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(9);
    doc.text("Discovery - Sistema de Detecção de Golpes Digitais | Anatel/UFG", 14, 291);

    doc.save(`caso_${id}_${new Date().toLocaleDateString("pt-BR").replace(/\//g, "-")}.pdf`);
  };

  return (
    <div className="dashboard">
      <Menu />
      <div className="case-contente">
        <div className="search-cases">
          <SearchBar placeholder="BUSQUE O CASO AQUI" />
          <ReturnButton />
        </div>

        <div className="case-data">
          <div className="content">
            <div className="content-field">
              <span>Titulo</span>
              <input type="text" value={caso?.titulo || ""} readOnly />
            </div>

            <div className="content-field">
              <span>Link</span>
              <input type="text" value={caso?.url || ""} readOnly />
            </div>

            <div className="content-field legenda">
              <span>Legenda do Post</span>
              <textarea value={caso?.legenda || ""} readOnly></textarea>
            </div>
          </div>

          <div className="result">
            <div className="result-top">
              <div className="grafic-chart">
                <div className="result-chart">
                  <PieChart width={180} height={180}>
                    <Pie data={dadosRosca} dataKey="value" cx="50%" cy="50%">
                      {dadosRosca.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </div>

                <div className="result-info">
                  <span>Pontos totais suspeitos: {totalPontos}</span>
                  <span style={{ color: "#41b8b5" }}>Links suspeitos: {analise?.links_suspeitos || 0}</span>
                  <span style={{ color: "#4CAF50" }}>Erros ortográficos: {analise?.erros_ortograficos || 0}</span>
                  <span style={{ color: "#f44336" }}>Uso de IA generativa: {analise?.uso_ia_generativa || 0}</span>
                </div>
              </div>

              <div className="result-buttons">
                <button className="resultado-golpe">
                  {veracidade}% {caso?.situacao || "ANALISANDO"}
                </button>
                <button className="resultado-pdf" onClick={gerarPDF}>PDF</button>
              </div>
            </div>

            <div className="result-bottom">
              <details className="accordion">
                <summary>Erros Ortográficos: {analise?.erros_ortograficos || 0}</summary>
                <p>Foram encontrados {analise?.erros_ortograficos || 0} erros ortográficos no conteúdo analisado, indicando possível geração automática de texto fraudulento.</p>
              </details>

              <details className="accordion">
                <summary>Uso de IA generativa: {analise?.uso_ia_generativa || 0}</summary>
                <p>Foram detectados {analise?.uso_ia_generativa || 0} indicadores de uso de IA generativa nociva no conteúdo.</p>
              </details>

              <details className="accordion">
                <summary>Links suspeitos: {analise?.links_suspeitos || 0}</summary>
                <p>Foram encontrados {analise?.links_suspeitos || 0} links suspeitos no conteúdo analisado.</p>
                {caso?.url && <p>URL analisada: {caso.url}</p>}
              </details>

              <details className="accordion">
                <summary>Taxonomia repetitiva: {analise?.taxonomia_repetitiva || 0}</summary>
                <p>Foram identificados {analise?.taxonomia_repetitiva || 0} padrões taxonômicos repetitivos característicos de golpes digitais.</p>
              </details>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}