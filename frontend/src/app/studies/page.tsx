"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Study = {
  id: string;
  title: string;
  description: string | null;
  difficulty: string;
  is_kids_content: boolean;
  modules: {
    id: string;
    title: string;
    lessons: { id: string; title: string }[];
  }[];
};

export default function StudiesPage() {
  const router = useRouter();
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const session = getSession();
      if (!session) {
        router.replace("/login");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/v1/studies`, {
          headers: { Authorization: `Bearer ${session.accessToken}` },
        });
        const data = await response.json();
        setStudies(data.studies);
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
        <p>Carregando estudos...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-3xl font-bold">Estudos</h1>

        <div className="mt-6 space-y-6">
          {studies.map((study) => (
            <div key={study.id} className="rounded-xl bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">{study.title}</h2>
              <p className="mt-2 text-slate-400">{study.description || "Sem descrição"}</p>

              <div className="mt-4 space-y-3">
                {study.modules.map((module) => (
                  <div key={module.id} className="rounded-lg bg-slate-800 p-4">
                    <p className="font-medium">{module.title}</p>

                    <div className="mt-2 space-y-1">
                      {module.lessons.map((lesson) => (
                        <p key={lesson.id} className="text-sm text-slate-300">• {lesson.title}</p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
