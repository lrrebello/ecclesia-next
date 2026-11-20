"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Overview = {
  church: { name: string; branches: number };
  members: { total: number; pending: number };
  families: number;
  ministries: number;
  events: number;
  finance: {
    income: string;
    expense: string;
    balance: string;
    pending_bills: string;
    overdue_bills: number;
  };
  donations: { tax_relevant_total: string };
};

export default function AdminPage() {
  const router = useRouter();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [branches, setBranches] = useState<any[]>([]);
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
        const overviewResponse = await fetch(`${API_URL}/api/v1/admin/overview`, {
          headers: { Authorization: `Bearer ${session.accessToken}` },
        });

        if (!overviewResponse.ok) {
          throw new Error("Acesso negado");
        }

        setOverview(await overviewResponse.json());

        const branchesResponse = await fetch(`${API_URL}/api/v1/admin/branches`, {
          headers: { Authorization: `Bearer ${session.accessToken}` },
        });
        const branchesData = await branchesResponse.json();
        setBranches(branchesData.branches);
      } catch (err: any) {
        setError(err.message ?? "Não foi possível carregar o painel.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando administração...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Administração</h1>

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

        {overview && (
          <>
            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Membros</p>
                <p className="mt-2 text-2xl font-bold">{overview.members.total}</p>
                <p className="mt-1 text-sm text-slate-400">{overview.members.pending} pendentes</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Famílias</p>
                <p className="mt-2 text-2xl font-bold">{overview.families}</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Ministérios</p>
                <p className="mt-2 text-2xl font-bold">{overview.ministries}</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Eventos</p>
                <p className="mt-2 text-2xl font-bold">{overview.events}</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Receitas</p>
                <p className="mt-2 text-2xl font-bold">{overview.finance.income}</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Despesas</p>
                <p className="mt-2 text-2xl font-bold">{overview.finance.expense}</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Saldo</p>
                <p className="mt-2 text-2xl font-bold">{overview.finance.balance}</p>
              </div>

              <div className="rounded-xl bg-slate-900 p-5">
                <p className="text-sm text-slate-400">Donativos elegíveis</p>
                <p className="mt-2 text-2xl font-bold">{overview.donations.tax_relevant_total}</p>
              </div>
            </div>

            <div className="mt-6 overflow-hidden rounded-xl bg-slate-900">
              <table className="w-full text-left">
                <thead className="bg-slate-800 text-sm text-slate-300">
                  <tr>
                    <th className="p-4">Filial</th>
                    <th className="p-4">Membros</th>
                    <th className="p-4">Pendentes</th>
                    <th className="p-4">Famílias</th>
                    <th className="p-4">Ministérios</th>
                    <th className="p-4">Saldo</th>
                  </tr>
                </thead>
                <tbody>
                  {branches.map((branch) => (
                    <tr key={branch.id} className="border-t border-slate-800">
                      <td className="p-4">{branch.name}</td>
                      <td className="p-4">{branch.members}</td>
                      <td className="p-4">{branch.pending_members}</td>
                      <td className="p-4">{branch.families}</td>
                      <td className="p-4">{branch.ministries}</td>
                      <td className="p-4">{branch.balance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
