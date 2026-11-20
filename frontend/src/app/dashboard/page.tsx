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
          <button onClick={handleLogout} className="rounded-lg bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700">
            Sair
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-6xl p-6">
        <div className="rounded-xl bg-slate-900 p-6">
          <h2 className="text-2xl font-bold">Bem-vindo, {user?.name}</h2>
          <p className="mt-2 text-slate-300">{user?.email}</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <a href="/profile" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Meu perfil</p>
              <p className="mt-1 font-medium">Editar dados</p>
            </a>

            <a href="/members" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Membros</p>
              <p className="mt-1 font-medium">Listar e aprovar</p>
            </a>

            <a href="/families" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Famílias</p>
              <p className="mt-1 font-medium">Gerenciar famílias</p>
            </a>

            <a href="/ministries" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Ministérios</p>
              <p className="mt-1 font-medium">Gerenciar ministérios</p>
            </a>

            <a href="/events" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Agenda</p>
              <p className="mt-1 font-medium">Eventos e reuniões</p>
            </a>

            <a href="/finance" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Finanças</p>
              <p className="mt-1 font-medium">Lançamentos e contas</p>
            </a>

            <a href="/donations" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Donativos</p>
              <p className="mt-1 font-medium">Registar donativos</p>
            </a>

            <a href="/modelo25" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Modelo 25</p>
              <p className="mt-1 font-medium">Declaração anual</p>
            </a>

            <a href="/media" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Mídia</p>
              <p className="mt-1 font-medium">Álbuns e conteúdos</p>
            </a>

            <a href="/devotionals" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Devocionais</p>
              <p className="mt-1 font-medium">Leituras diárias</p>
            </a>

            <a href="/studies" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Estudos</p>
              <p className="mt-1 font-medium">Lições e quizzes</p>
            </a>

            <a href="/kids" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Área Kids</p>
              <p className="mt-1 font-medium">Atividades infantis</p>
            </a>

            <a href="/admin" className="rounded-lg bg-slate-800 p-4 transition hover:bg-slate-700">
              <p className="text-sm text-slate-400">Administração</p>
              <p className="mt-1 font-medium">Dashboards e relatórios</p>
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}
