"use client";

import "./medidor.css";
import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";

export default function Medidor({
  veracidade = 0,
  risco = null,
  tamanho = "grande",
}) {
  const cor =
    risco === "ALTO"
      ? "#f44336"
      : risco === "MÉDIO"
        ? "#ff9800"
        : risco === "BAIXO"
          ? "#4CAF50"
          : "#41b8b5";

  const config =
    tamanho === "pequeno"
      ? { width: 160, height: 110, cx: 80, cy: 95, inner: 55, outer: 78 }
      : { width: 220, height: 120, cx: 110, cy: 115, inner: 80, outer: 105 };

  const data = [{ value: veracidade, fill: cor }];

  return (
    <div className="medidor-container">
      <RadialBarChart
        width={config.width}
        height={config.height}
        cx={config.cx}
        cy={config.cy}
        innerRadius={config.inner}
        outerRadius={config.outer}
        startAngle={180}
        endAngle={0}
        data={data}
      >
        <PolarAngleAxis
          type="number"
          domain={[0, 100]}
          angleAxisId={0}
          tick={false}
        />
        <RadialBar
          background={{ fill: "#f0f0f5" }}
          dataKey="value"
          angleAxisId={0}
          cornerRadius={6}
        />
      </RadialBarChart>

      <span className="medidor-valor" style={{ color: cor }}>
        {veracidade}% golpe
      </span>

      {risco && <span className="medidor-risco">Risco: {risco}</span>}
    </div>
  );
}
