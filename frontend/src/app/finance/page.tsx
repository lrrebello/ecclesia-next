"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Transaction = {
  id: string;
  type: string;
  amount: string;
  description: string | null;
  transaction_date: string;
};

export default function FinancePage() {
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [form, setForm] = useState({
    type: "income",
    amount: "",
    description: "",
    transaction_date: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadTransactions(token: string) {
    const response = await fetch(`${API_URL}/api/v1/finance/transactions`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("Não foi possível carregar os lançamentos.");
    }

    const data = await response.json();
    setTransactions(data.transactions);
  }

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        await loadTransactions(session.accessToken);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  async function createTransaction(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/finance/transactions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({
        type: form.type,
        amount: form.amount,
        description: form.description || null,
        transaction_date: form.transaction_date,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível criar o lançamento.");
      return;
    }

    setForm({ type: "income", amount: "", description: "", transaction_date: "" });
    await loadTransactions(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando finanças...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Finanças</h1>

        <form onSubmit={createTransaction} className="mt-6 rounded-xl bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Novo lançamento</h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-4">
            <select className="rounded-lg bg-slate-800 p-3" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
              <option value="income">Receita</option>
              <option value="expense">Despesa</option>
            </select>

            <input className="rounded-lg bg-slate-800 p-3" placeholder="Valor" type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.transaction_date} onChange={(e) => setForm({ ...form, transaction_date: e.target.value })} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>

          <button className="mt-4 rounded-lg bg-indigo-500 px-5 py-3 font-medium">Registrar lançamento</button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </form>

        <div className="mt-6 overflow-hidden rounded-xl bg-slate-900">
          <table className="w-full text-left">
            <thead className="bg-slate-800 text-sm text-slate-300">
              <tr>
                <th className="p-4">Data</th>
                <th className="p-4">Tipo</th>
                <th className="p-4">Valor</th>
                <th className="p-4">Descrição</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id} className="border-t border-slate-800">
                  <td className="p-4">{transaction.transaction_date}</td>
                  <td className="p-4">{transaction.type === "income" ? "Receita" : "Despesa"}</td>
                  <td className="p-4">{transaction.amount}</td>
                  <td className="p-4">{transaction.description || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
