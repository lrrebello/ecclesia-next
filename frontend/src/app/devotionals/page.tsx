"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Devotional = {
  id: string;
  title: string;
  scripture_reference: string | null;
  scripture_text: string | null;
  content: string;
  prayer: string | null;
  publish_date: string | null;
  read: boolean;
};

export default function DevotionalsPage() {
  const router = useRouter();
  const [devotionals, setDevotionals] = useState<Devotional[]>([]);
  const [loading, setLoading] = useState(true);

  async function load(token: string) {
    const response = await fetch(`${API_URL}/api/v1/media/devotionals`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setDevotionals(data.devotionals);
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

  async function markAsRead(devotionalId: string) {
    const session = getSession();
    if (!session) return;

    await fetch(`${API_URL}/api/v1/media/devotionals/${devotionalId}/read`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });

    await load(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando devocionais...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">Devocionais</h1>

        <div className="mt-6 space-y-6">
          {devotionals.map((devotional) => (
            <article key={devotional.id} className="rounded-xl bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">{devotional.title}</h2>

              {devotional.scripture_reference && (
                <p className="mt-1 text-sm text-indigo-300">{devotional.scripture_reference}</p>
              )}

              {devotional.scripture_text && (
                <blockquote className="mt-4 border-l-4 border-indigo-500 pl-4 text-slate-300">
                  {devotional.scripture_text}
                </blockquote>
              )}

              <p className="mt-4 whitespace-pre-line text-slate-200">{devotional.content}</p>

              {devotional.prayer && (
                <div className="mt-4 rounded-lg bg-slate-800 p-4">
                  <p className="text-sm font-semibold text-slate-300">Oração</p>
                  <p className="mt-2 whitespace-pre-line">{devotional.prayer}</p>
                </div>
              )}

              <button
                onClick={() => markAsRead(devotional.id)}
                disabled={devotional.read}
                className={`mt-4 rounded-lg px-4 py-2 text-sm ${devotional.read ? "bg-slate-800 text-slate-400" : "bg-green-600"}`}
              >
                {devotional.read ? "Já lido" : "Marcar como lido"}
              </button>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
