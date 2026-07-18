"use client";

export default function AvisoIA({ onClose }) {
  return (
    <div className="aviso-ia-overlay" onClick={onClose}>
      <div className="aviso-ia-modal" onClick={(e) => e.stopPropagation()}>
        <div className="aviso-ia-icon">⚠️</div>
        <h3>Classificador de IA offline</h3>
        <p>
          Por limitação de custo de hospedagem, o serviço de IA (classificador
          de texto e detecção de golpes) não está rodando em produção neste
          momento.
        </p>
        <p>
          Este é um projeto de portfólio — o código completo do classificador
          está disponível no repositório e funciona normalmente em ambiente
          local.
        </p>
        <button className="aviso-ia-btn" onClick={onClose}>
          Entendi
        </button>
      </div>
    </div>
  );
}