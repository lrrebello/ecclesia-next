"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Declaration = {
  id: string;
  fiscal_year: number;
  status: string;
  total_amount: string;
  donation_count: number;
  donations: { id: string; amount: string; donor: { name: string; tax_id: string } }[];
};

export default function Modelo25Page() {
  const router = useRouter();
  const [declarations, setDeclarations] = useState<Declaration[]>([]);
  const [fiscalYear, setFiscalYear] = useState(new Date().getFullYear() - 1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load(token: string) {
    const response = await fetch(`${API_URL}/api/v1/donations/declarations`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setDeclarations(data.declarations);
  }

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        await load(session.accessToken);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  async function createDeclaration(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/donations/declarations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({ fiscal_year: fiscalYear }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível criar a declaração.");
      return;
    }

    await load(session.accessToken);
  }

  async function addDonation(declarationId: string, donationId: string) {
    const session = getSession();
    if (!session) return;

    await fetch(`${API_URL}/api/v1/donations/declarations/${declarationId}/donations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({ donation_id: donationId }),
    });

    await load(session.accessToken);
  }

  async function submitDeclaration(declarationId: string) {
    const session = getSession();
    if (!session) return;

    await fetch(`${API_URL}/api/v1/donations/declarations/${declarationId}/submit`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });

    await load(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando Modelo 25...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Modelo 25 — Donativos recebidos</h1>

        <form onSubmit={createDeclaration} className="mt-6 flex gap-4 rounded-xl bg-slate-900 p-6">
          <input className="rounded-lg bg-slate-800 p-3" type="number" value={fiscalYear} onChange={(e) => setFiscalYear(Number(e.target.value))} required />
          <button className="rounded-lg bg-indigo-500 px-5 py-3 font-medium">Criar declaração</button>
        </form>

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

        <div className="mt-6 space-y-6">
          {declarations.map((declaration) => (
            <div key={declaration.id} className="rounded-xl bg-slate-900 p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Ano fiscal {declaration.fiscal_year}</h2>
                <span className="rounded-full bg-slate-800 px-3 py-1 text-sm">{declaration.status}</span>
              </div>

              <p className="mt-2 text-slate-300">
                {declaration.donation_count} donativos • Total: {declaration.total_amount}
              </p>

              <div className="mt-4 space-y-2">
                {declaration.donations.map((donation) => (
                  <div key={donation.id} className="rounded-lg bg-slate-800 p-3">
                    {donation.donor.name} — {donation.donor.tax_id} — {donation.amount}
                  </div>
                ))}
              </div>

              <div className="mt-4 flex gap-3">
                <a
                  className="rounded-lg bg-slate-800 px-4 py-2 text-sm"
                  href={`${API_URL}/api/v1/donations/declarations/${declaration.id}/export`}
                  target="_blank"
                >
                  Exportar ficheiro
                </a>

                {declaration.status === "draft" && (
                  <button onClick={() => submitDeclaration(declaration.id)} className="rounded-lg bg-green-600 px-4 py-2 text-sm">
                    Marcar como enviada
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
