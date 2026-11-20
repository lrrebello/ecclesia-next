"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Donation = {
  id: string;
  amount: string;
  donation_date: string;
  is_tax_relevant: boolean;
  declaration_id: string | null;
  donor: { id: string; name: string; tax_id: string };
};

export default function DonationsPage() {
  const router = useRouter();
  const [donations, setDonations] = useState<Donation[]>([]);
  const [donors, setDonors] = useState<any[]>([]);
  const [form, setForm] = useState({
    donor_id: "",
    amount: "",
    donation_date: "",
    receipt_number: "",
    is_tax_relevant: true,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load(token: string) {
    const donationsResponse = await fetch(`${API_URL}/api/v1/donations`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const donationsData = await donationsResponse.json();
    setDonations(donationsData.donations);

    const donorsResponse = await fetch(`${API_URL}/api/v1/donations/donors`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const donorsData = await donorsResponse.json();
    setDonors(donorsData.donors);
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

  async function createDonation(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/donations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({
        donor_id: form.donor_id,
        amount: form.amount,
        donation_date: form.donation_date,
        receipt_number: form.receipt_number || null,
        is_tax_relevant: form.is_tax_relevant,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível registar o donativo.");
      return;
    }

    setForm({ donor_id: "", amount: "", donation_date: "", receipt_number: "", is_tax_relevant: true });
    await load(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando donativos...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Donativos</h1>

        <form onSubmit={createDonation} className="mt-6 rounded-xl bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Registar donativo</h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <select className="rounded-lg bg-slate-800 p-3" value={form.donor_id} onChange={(e) => setForm({ ...form, donor_id: e.target.value })} required>
              <option value="">Selecione o doador</option>
              {donors.map((donor) => (
                <option key={donor.id} value={donor.id}>
                  {donor.name} — {donor.tax_id}
                </option>
              ))}
            </select>

            <input className="rounded-lg bg-slate-800 p-3" placeholder="Valor" type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.donation_date} onChange={(e) => setForm({ ...form, donation_date: e.target.value })} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Número do recibo" value={form.receipt_number} onChange={(e) => setForm({ ...form, receipt_number: e.target.value })} />
          </div>

          <label className="mt-4 flex items-center gap-3 text-sm">
            <input type="checkbox" checked={form.is_tax_relevant} onChange={(e) => setForm({ ...form, is_tax_relevant: e.target.checked })} />
            Elegível para o Modelo 25
          </label>

          <button className="mt-4 rounded-lg bg-indigo-500 px-5 py-3 font-medium">Registar donativo</button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </form>

        <div className="mt-6 overflow-hidden rounded-xl bg-slate-900">
          <table className="w-full text-left">
            <thead className="bg-slate-800 text-sm text-slate-300">
              <tr>
                <th className="p-4">Data</th>
                <th className="p-4">Doador</th>
                <th className="p-4">NIF</th>
                <th className="p-4">Valor</th>
                <th className="p-4">Modelo 25</th>
              </tr>
            </thead>
            <tbody>
              {donations.map((donation) => (
                <tr key={donation.id} className="border-t border-slate-800">
                  <td className="p-4">{donation.donation_date}</td>
                  <td className="p-4">{donation.donor.name}</td>
                  <td className="p-4">{donation.donor.tax_id}</td>
                  <td className="p-4">{donation.amount}</td>
                  <td className="p-4">{donation.is_tax_relevant ? "Elegível" : "Não elegível"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
