"use client"
import "./returnButton.css"
import { useRouter } from "next/navigation"

export default function ReturnButton() {
  const router = useRouter()

  return (
    <button className="return" onClick={() => router.back()}>
      <i className="fa-solid fa-right-from-bracket"></i>
      RETORNAR
    </button>
  )
}