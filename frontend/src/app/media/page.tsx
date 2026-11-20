"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Album = {
  id: string;
  title: string;
  description: string | null;
  items: {
    id: string;
    title: string;
    media_type: string;
    external_url: string | null;
  }[];
};

export default function MediaPage() {
  const router = useRouter();
  const [albums, setAlbums] = useState<Album[]>([]);
  const [form, setForm] = useState({ title: "", description: "" });
  const [loading, setLoading] = useState(true);

  async function load(token: string) {
    const response = await fetch(`${API_URL}/api/v1/media/albums`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setAlbums(data.albums);
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

  async function createAlbum(event: React.FormEvent) {
    event.preventDefault();

    const session = getSession();
    if (!session) return;

    await fetch(`${API_URL}/api/v1/media/albums`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify(form),
    });

    setForm({ title: "", description: "" });
    await load(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando mídia...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Mídia</h1>

        <form onSubmit={createAlbum} className="mt-6 rounded-xl bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Novo álbum</h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Título" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>

          <button className="mt-4 rounded-lg bg-indigo-500 px-5 py-3 font-medium">Criar álbum</button>
        </form>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {albums.map((album) => (
            <div key={album.id} className="rounded-xl bg-slate-900 p-5">
              <h2 className="font-semibold">{album.title}</h2>
              <p className="mt-2 text-sm text-slate-400">{album.description || "Sem descrição"}</p>
              <p className="mt-3 text-sm text-slate-300">{album.items.length} itens</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
