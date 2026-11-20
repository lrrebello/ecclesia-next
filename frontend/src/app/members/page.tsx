"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Member = {
  id: string;
  name: string;
  email: string;
  status: string;
  phone: string | null;
  birth_date: string | null;
};

export default function MembersPage() {
  const router = useRouter();
  const [members, setMembers] = useState<Member[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadMembers(token: string) {
    const response = await fetch(`${API_URL}/api/v1/members`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("Não foi possível carregar os membros.");
    }

    const data = await response.json();
    setMembers(data.members);
  }

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        await loadMembers(session.accessToken);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro inesperado.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  async function approve(memberId: string, action: "approve" | "reject") {
    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/members/${memberId}/approval`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({ action }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível atualizar o membro.");
      return;
    }

    await loadMembers(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando membros...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Membros</h1>

        <div className="mt-6 overflow-hidden rounded-xl bg-slate-900">
          <table className="w-full text-left">
            <thead className="bg-slate-800 text-sm text-slate-300">
              <tr>
                <th className="p-4">Nome</th>
                <th className="p-4">E-mail</th>
                <th className="p-4">Status</th>
                <th className="p-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id} className="border-t border-slate-800">
                  <td className="p-4">{member.name}</td>
                  <td className="p-4">{member.email}</td>
                  <td className="p-4">{member.status}</td>
                  <td className="p-4">
                    {member.status === "pending" && (
                      <div className="flex gap-2">
                        <button onClick={() => approve(member.id, "approve")} className="rounded-lg bg-green-600 px-3 py-2 text-sm">Aprovar</button>
                        <button onClick={() => approve(member.id, "reject")} className="rounded-lg bg-red-600 px-3 py-2 text-sm">Rejeitar</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
      </div>
    </main>
  );
}
