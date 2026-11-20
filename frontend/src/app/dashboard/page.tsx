"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearSession, fetchCurrentUser, getSession, type AuthUser } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      if (!getSession()) {
        router.replace("/login");
        return;
      }

      try {
        const currentUser = await fetchCurrentUser();
        setUser(currentUser);
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [router]);

  function handleLogout() {
    clearSession();
    router.replace("/login");
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between p-4">
          <h1 className="text-xl font-bold">Ecclesia Next</h1>
          <button
            onClick={handleLogout}
            className="rounded-lg bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700"
          >
            Sair
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-6xl p-6">
        <div className="rounded-xl bg-slate-900 p-6">
          <h2 className="text-2xl font-bold">Bem-vindo, {user?.name}</h2>
          <p className="mt-2 text-slate-300">{user?.email}</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">Perfil</p>
              <p className="mt-1 font-medium">Ativo</p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">Módulos</p>
              <p className="mt-1 font-medium">Em construção</p>
            </div>

            <div className="rounded-lg bg-slate-800 p-4">
              <p className="text-sm text-slate-400">Próximo passo</p>
              <p className="mt-1 font-medium">Membros e ministérios</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
