"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type EventItem = {
  id: string;
  title: string;
  description: string | null;
  start_at: string;
  end_at: string | null;
  location: string | null;
  ministry: { id: string; name: string } | null;
};

export default function EventsPage() {
  const router = useRouter();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    start_at: "",
    end_at: "",
    location: "",
    ministry_id: "",
    recurrence_type: "none",
    recurrence_interval: 1,
    recurrence_until: "",
    is_public: true,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadEvents(token: string) {
    const response = await fetch(`${API_URL}/api/v1/events`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("Não foi possível carregar os eventos.");
    }

    const data = await response.json();
    setEvents(data.events);
  }

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        await loadEvents(session.accessToken);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  function update(field: string, value: string | number | boolean) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function createEvent(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    const session = getSession();
    if (!session) return;

    const response = await fetch(`${API_URL}/api/v1/events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({
        ...form,
        start_at: form.start_at ? new Date(form.start_at).toISOString() : null,
        end_at: form.end_at ? new Date(form.end_at).toISOString() : null,
        recurrence_until: form.recurrence_until || null,
        ministry_id: form.ministry_id || null,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      setError(data.detail ?? "Não foi possível criar o evento.");
      return;
    }

    setForm({
      title: "",
      description: "",
      start_at: "",
      end_at: "",
      location: "",
      ministry_id: "",
      recurrence_type: "none",
      recurrence_interval: 1,
      recurrence_until: "",
      is_public: true,
    });

    await loadEvents(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando agenda...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Agenda</h1>

        <form onSubmit={createEvent} className="mt-6 rounded-xl bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Criar evento</h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Título" value={form.title} onChange={(e) => update("title", e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Local" value={form.location} onChange={(e) => update("location", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="datetime-local" value={form.start_at} onChange={(e) => update("start_at", e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" type="datetime-local" value={form.end_at} onChange={(e) => update("end_at", e.target.value)} />
            <select className="rounded-lg bg-slate-800 p-3" value={form.recurrence_type} onChange={(e) => update("recurrence_type", e.target.value)}>
              <option value="none">Não recorrente</option>
              <option value="daily">Diário</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensal</option>
            </select>
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.recurrence_until} onChange={(e) => update("recurrence_until", e.target.value)} />
          </div>

          <textarea className="mt-4 w-full rounded-lg bg-slate-800 p-3" placeholder="Descrição" value={form.description} onChange={(e) => update("description", e.target.value)} />

          <button className="mt-4 rounded-lg bg-indigo-500 px-5 py-3 font-medium">Criar evento</button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </form>

        <div className="mt-6 space-y-4">
          {events.map((event, index) => (
            <div key={`${event.id}-${index}`} className="rounded-xl bg-slate-900 p-5">
              <h3 className="text-lg font-semibold">{event.title}</h3>
              <p className="mt-1 text-sm text-slate-400">
                {new Date(event.start_at).toLocaleString("pt-PT")}
                {event.location ? ` • ${event.location}` : ""}
              </p>
              {event.ministry && (
                <p className="mt-2 text-sm text-indigo-300">{event.ministry.name}</p>
              )}
              {event.description && <p className="mt-2 text-slate-300">{event.description}</p>}
            </div>
          ))}
        </div>

        {events.length === 0 && <p className="mt-6 text-slate-400">Nenhum evento agendado.</p>}
      </div>
    </main>
  );
}
