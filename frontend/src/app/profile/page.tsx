"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchCurrentUser, getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ProfilePage() {
  const router = useRouter();
  const [form, setForm] = useState<any>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        const user = await fetchCurrentUser();
        setForm(user);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  function update(field: string, value: string) {
    setForm((current: any) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/members/me`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify(form),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível salvar o perfil.");
      return;
    }

    setMessage("Perfil atualizado com sucesso.");
  }

  if (loading || !form) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando perfil...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold">Meu perfil</h1>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-xl bg-slate-900 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Nome" value={form.name} onChange={(e) => update("name", e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Telefone" value={form.phone || ""} onChange={(e) => update("phone", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.birth_date || ""} onChange={(e) => update("birth_date", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.baptism_date || ""} onChange={(e) => update("baptism_date", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.conversion_date || ""} onChange={(e) => update("conversion_date", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Documento" value={form.documents || ""} onChange={(e) => update("documents", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="NIF / CPF" value={form.tax_id || ""} onChange={(e) => update("tax_id", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Endereço" value={form.address || ""} onChange={(e) => update("address", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Código postal" value={form.postal_code || ""} onChange={(e) => update("postal_code", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Concelho" value={form.concelho || ""} onChange={(e) => update("concelho", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Localidade" value={form.localidade || ""} onChange={(e) => update("localidade", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Escolaridade" value={form.education_level || ""} onChange={(e) => update("education_level", e.target.value)} />
          </div>

          <textarea className="w-full rounded-lg bg-slate-800 p-3" placeholder="Observações" value={form.observations || ""} onChange={(e) => update("observations", e.target.value)} />

          <button className="w-full rounded-lg bg-indigo-500 p-3 font-medium">Salvar alterações</button>

          {message && <p className="text-sm text-green-400">{message}</p>}
          {error && <p className="text-sm text-red-400">{error}</p>}
        </form>
      </div>
    </main>
  );
}
