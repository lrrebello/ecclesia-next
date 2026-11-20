"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchCurrentUser, getSession, type AuthUser } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Ministry = {
  id: string;
  name: string;
  description: string | null;
  leader_id: string | null;
  vice_leader_id: string | null;
  extra_leaders: string[];
  is_kids_ministry: boolean;
  members: { id: string; name: string; email: string }[];
};

export default function MinistriesPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ministries, setMinistries] = useState<Ministry[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadMinistries(token: string) {
    const response = await fetch(`${API_URL}/api/v1/ministries`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("Não foi possível carregar os ministérios.");
    }

    const data = await response.json();
    setMinistries(data.ministries);
  }

  useEffect(() => {
    async function load() {
      const session = getSession();

      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        const currentUser = await fetchCurrentUser();
        setUser(currentUser);
        await loadMinistries(session.accessToken);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  async function createMinistry(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/ministries`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({
        name,
        description: description || null,
        leader_id: session.user.id,
        extra_leader_ids: [],
        is_kids_ministry: false,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível criar o ministério.");
      return;
    }

    setName("");
    setDescription("");
    await loadMinistries(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando ministérios...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between p-4">
          <h1 className="text-xl font-bold">Ministérios</h1>
          <a className="text-sm text-slate-300 hover:text-white" href="/dashboard">
            Voltar ao painel
          </a>
        </div>
      </header>

      <div className="mx-auto max-w-6xl space-y-6 p-6">
        <form onSubmit={createMinistry} className="rounded-xl bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Criar ministério</h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <input
              className="rounded-lg bg-slate-800 p-3"
              placeholder="Nome do ministério"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />

            <input
              className="rounded-lg bg-slate-800 p-3"
              placeholder="Descrição"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>

          <button className="mt-4 rounded-lg bg-indigo-500 px-5 py-3 font-medium">
            Criar ministério
          </button>

          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </form>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ministries.map((ministry) => (
            <div key={ministry.id} className="rounded-xl bg-slate-900 p-5">
              <h3 className="text-lg font-semibold">{ministry.name}</h3>
              <p className="mt-1 text-sm text-slate-400">
                {ministry.description || "Sem descrição"}
              </p>
              <p className="mt-3 text-sm">
                <strong>{ministry.members.length}</strong> membros
              </p>
              {ministry.is_kids_ministry && (
                <span className="mt-3 inline-block rounded-full bg-indigo-500/20 px-3 py-1 text-xs text-indigo-300">
                  Ministério infantil
                </span>
              )}
            </div>
          ))}
        </div>

        {ministries.length === 0 && (
          <p className="text-slate-400">Nenhum ministério criado ainda.</p>
        )}
      </div>
    </main>
  );
}
