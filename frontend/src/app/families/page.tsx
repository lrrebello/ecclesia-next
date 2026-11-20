"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Family = {
  id: string;
  name: string;
  address: string | null;
  phone: string | null;
  responsible_id: string | null;
  members: { id: string; name: string; email: string; status: string }[];
};

export default function FamiliesPage() {
  const router = useRouter();
  const [families, setFamilies] = useState<Family[]>([]);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadFamilies(token: string) {
    const response = await fetch(`${API_URL}/api/v1/families`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("Não foi possível carregar as famílias.");
    }

    const data = await response.json();
    setFamilies(data.families);
  }

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        await loadFamilies(session.accessToken);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  async function createFamily(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/families`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({
        name,
        address: address || null,
        phone: phone || null,
        responsible_id: session.user.id,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível criar a família.");
      return;
    }

    setName("");
    setAddress("");
    setPhone("");
    await loadFamilies(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando famílias...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Famílias</h1>

        <form onSubmit={createFamily} className="mt-6 rounded-xl bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Criar família</h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Nome da família" value={name} onChange={(e) => setName(e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Endereço" value={address} onChange={(e) => setAddress(e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Telefone" value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>

          <button className="mt-4 rounded-lg bg-indigo-500 px-5 py-3 font-medium">Criar família</button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </form>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {families.map((family) => (
            <div key={family.id} className="rounded-xl bg-slate-900 p-5">
              <h3 className="text-lg font-semibold">{family.name}</h3>
              <p className="mt-1 text-sm text-slate-400">{family.address || "Sem endereço"}</p>
              <p className="mt-3 text-sm">
                <strong>{family.members.length}</strong> membros
              </p>
            </div>
          ))}
        </div>

        {families.length === 0 && <p className="mt-6 text-slate-400">Nenhuma família criada ainda.</p>}
      </div>
    </main>
  );
}
