"use client";

import { useState } from "react";
import ReturnButton from "../components/back/ReturnButton";
import Menu from "../components/menu/Menu";
import { analisarTexto, analisarURL } from "../services/api";
import "./manual_analysis.css";
import Medidor from "../components/medidor/Medidor";

export default function ManualAnalysis() {
  const [modoLink, setModoLink] = useState(false);
  const [texto, setTexto] = useState("");
  const [links, setLinks] = useState([""]);
  const [resultado, setResultado] = useState(null);
  const [carregando, setCarregando] = useState(false);

  const adicionarLink = () => setLinks([...links, ""]);

  const atualizarLink = (index, valor) => {
    const novosLinks = [...links];
    novosLinks[index] = valor;
    setLinks(novosLinks);
  };

  const analisar = async () => {
    setCarregando(true);
    try {
      if (modoLink) {
        const resultados = await Promise.all(
          links.map((url) => analisarURL(url)),
        );
        setResultado(resultados[0]?.data);
      } else {
        const data = await analisarTexto(texto);
        console.log("RESULTADO TEXTO:", data);
        setResultado(data?.data);
      }
    } catch (error) {
      console.error("Erro na análise:", error);
    } finally {
      setCarregando(false);
    }
  };

  const veracidade = resultado
    ? resultado?.is_suspicious
      ? Math.round((resultado?.confidence || 0) * 100)
      : Math.round((1 - (resultado?.confidence || 0)) * 100)
    : 0;

  const risco = resultado
    ? veracidade >= 60
      ? "ALTO"
      : veracidade >= 30
        ? "MÉDIO"
        : "BAIXO"
    : null;

  const erros = resultado?.ml_classification?.probabilities?.phishing
    ? Math.round(resultado.ml_classification.probabilities.phishing * 100)
    : 0;

  const iaGenerativa = resultado?.ml_classification?.probabilities
    ?.falso_investimento
    ? Math.round(
        resultado.ml_classification.probabilities.falso_investimento * 100,
      )
    : 0;

  const linksS = resultado?.suspicious_links?.length || 0;

  const taxonomia = resultado?.ml_classification?.probabilities
    ?.engenharia_social
    ? Math.round(
        resultado.ml_classification.probabilities.engenharia_social * 100,
      )
    : 0;

  return (
    <div className="dashboard">
      <Menu />
      <div className="contente-geral">
        <div className="interactions-verify">
          <div className="select-verify">
            <div className="mark-verify">
              <input
                type="checkbox"
                checked={!modoLink}
                onChange={() => setModoLink(false)}
              />
              <span>VERIFIQUE UM TEXTO</span>
            </div>
            <div className="mark-verify">
              <input
                type="checkbox"
                checked={modoLink}
                onChange={() => setModoLink(true)}
              />
              <span>VERIFIQUE UM LINK</span>
            </div>
          </div>
          <ReturnButton />
        </div>

        <div className="data-ma">
          <div className="inspection">
            <div className="put-text">
              {!modoLink ? (
                <textarea
                  placeholder="Cole aqui texto suspeito..."
                  value={texto}
                  onChange={(e) => setTexto(e.target.value)}
                />
              ) : (
                <div className="links-container">
                  {links.map((link, index) => (
                    <input
                      key={index}
                      type="text"
                      placeholder="Cole o link suspeito aqui..."
                      value={link}
                      onChange={(e) => atualizarLink(index, e.target.value)}
                      className="link-input"
                    />
                  ))}
                  <button className="add-link" onClick={adicionarLink}>
                    + Adicionar outro link
                  </button>
                </div>
              )}
            </div>

            <button
              className="btn-analisar"
              onClick={analisar}
              disabled={carregando}
            >
              {carregando ? "ANALISANDO..." : "ANALISAR"}
            </button>

            <div className="medidor">
              <Medidor veracidade={veracidade} risco={risco} />
            </div>
          </div>

          <div className="details">
            <div className="container-detais">
              <div className="list-details">
                <div className="detail-item">
                  <span className="detail-label">Erros ortográficos</span>
                  <div className="detail-bar">
                    <div
                      className="detail-fill"
                      style={{ width: `${erros}%` }}
                    ></div>
                    <span>{erros} Ocorrências</span>
                  </div>
                </div>

                <div className="detail-item">
                  <span className="detail-label">
                    Uso de IA generativa nociva
                  </span>
                  <div className="detail-bar">
                    <div
                      className="detail-fill"
                      style={{ width: `${iaGenerativa}%` }}
                    ></div>
                    <span>{iaGenerativa} Ocorrências</span>
                  </div>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Links Suspeitos</span>
                  <div className="detail-bar">
                    <div
                      className="detail-fill"
                      style={{ width: `${linksS * 10}%` }}
                    ></div>
                    <span>{linksS} Ocorrências</span>
                  </div>
                </div>

                <div className="detail-item">
                  <span className="detail-label">
                    Padrão taxonômico repetitivo
                  </span>
                  <div className="detail-bar">
                    <div
                      className="detail-fill"
                      style={{ width: `${taxonomia}%` }}
                    ></div>
                    <span>{taxonomia} Ocorrências</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="result-details">
              <details className="accordion">
                <summary>Casos de erros Ortográficos</summary>
                <p>
                  {resultado?.explanation ||
                    "Analise um texto para ver os detalhes"}
                </p>
              </details>

              <details className="accordion">
                <summary>Casos do uso de IA generativa</summary>
                <p>
                  {resultado?.ml_classification?.label === "falso_investimento"
                    ? `Tipo detectado: ${resultado.ml_classification.label} com ${Math.round(resultado.ml_classification.confidence * 100)}% de confiança`
                    : "Nenhuma ocorrência detectada"}
                </p>
              </details>

              <details className="accordion">
                <summary>Casos de taxonomia repetitiva</summary>
                <p>
                  {resultado?.fraud_type
                    ? `Padrão identificado: ${resultado.fraud_type}`
                    : "Nenhuma ocorrência detectada"}
                </p>
              </details>

              <details className="accordion">
                <summary>Casos de Links Suspeitos</summary>
                {resultado?.suspicious_links?.length > 0 ? (
                  resultado.suspicious_links.map((link, i) => (
                    <p key={i}>
                      {link.url} — Risco: {link.risk_level}
                    </p>
                  ))
                ) : (
                  <p>Nenhum link suspeito detectado</p>
                )}
              </details>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
