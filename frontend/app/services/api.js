const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function analisarTexto(text, useSabia = true) {
  const response = await fetch(`${API_URL}/analise-manual/texto`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, use_sabia: useSabia }),
  })
  if (!response.ok) throw new Error("Erro ao analisar texto")
  return response.json()
}

export async function analisarURL(url, useSabia = true) {
  const response = await fetch(`${API_URL}/analise-manual/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, use_sabia: useSabia }),
  })
  if (!response.ok) throw new Error("Erro ao analisar URL")
  return response.json()
}

export async function buscarCasosRecentes() {
  const response = await fetch(`${API_URL}/casos/recentes`)
  if (!response.ok) throw new Error("Erro ao buscar casos")
  return response.json()
}

export async function buscarCaso(id) {
  const response = await fetch(`${API_URL}/casos/${id}`)
  if (!response.ok) throw new Error("Erro ao buscar caso")
  return response.json()
}

export async function buscarAnaliseDoCaso(casoId) {
  const response = await fetch(`${API_URL}/analises/caso/${casoId}`)
  if (!response.ok) throw new Error("Erro ao buscar análise")
  return response.json()
}