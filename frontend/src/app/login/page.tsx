"use client";
import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();

    // Mostra no console do navegador qual URL está sendo usada
    console.log("API URL:", process.env.NEXT_PUBLIC_API_URL);

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    setMessage(response.ok ? "Login realizado." : data.detail || "Erro no login.");
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-xl bg-slate-900 p-6">
        <h1 className="text-2xl font-bold">Entrar</h1>
        <input className="w-full rounded-lg bg-slate-800 p-3" placeholder="E-mail" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full rounded-lg bg-slate-800 p-3" type="password" placeholder="Senha" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button className="w-full rounded-lg bg-indigo-500 p-3 font-medium">Entrar</button>
        {message && <p className="text-sm text-slate-300">{message}</p>}
      </form>
    </main>
  );
}