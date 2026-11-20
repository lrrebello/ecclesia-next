"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type KidsContent = {
  id: string;
  title: string;
  topic: string;
  age_range: string;
  content_type: string;
  content: any;
};

export default function KidsPage() {
  const router = useRouter();
  const [contents, setContents] = useState<KidsContent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/v1/studies/kids`, {
          headers: { Authorization: `Bearer ${session.accessToken}` },
        });
        const data = await response.json();
        setContents(data.contents);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [router]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando área infantil...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">Área Kids</h1>

        <div className="mt-6 space-y-6">
          {contents.map((content) => (
            <div key={content.id} className="rounded-xl bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">{content.title}</h2>
              <p className="mt-1 text-sm text-indigo-300">
                {content.topic} • {content.age_range} anos
              </p>

              {content.content?.objective && (
                <p className="mt-4 text-slate-300">{content.content.objective}</p>
              )}

              {content.content?.instructions && (
                <ul className="mt-4 space-y-2 text-slate-200">
                  {content.content.instructions.map((instruction: string, index: number) => (
                    <li key={index}>• {instruction}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
