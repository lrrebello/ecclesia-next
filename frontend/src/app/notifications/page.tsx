"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getSession } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Notification = {
  id: string;
  title: string;
  message: string;
  type: string;
  action_url: string | null;
  created_at: string;
  read: boolean;
};

export default function NotificationsPage() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  async function load(token: string) {
    const response = await fetch(`${API_URL}/api/v1/notifications`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    setNotifications(data.notifications);
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

  async function markAsRead(notificationId: string) {
    const session = getSession();
    if (!session) return;

    await fetch(`${API_URL}/api/v1/notifications/${notificationId}/read`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });

    await load(session.accessToken);
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p>Carregando notificações...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">Notificações</h1>

        <div className="mt-6 space-y-4">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className={`rounded-xl p-5 ${notification.read ? "bg-slate-900" : "bg-indigo-950"}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="font-semibold">{notification.title}</h2>
                  <p className="mt-2 text-slate-300">{notification.message}</p>
                  <p className="mt-3 text-xs text-slate-500">{notification.created_at}</p>
                </div>

                {!notification.read && (
                  <button onClick={() => markAsRead(notification.id)} className="rounded-lg bg-slate-800 px-3 py-2 text-sm">
                    Marcar como lida
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
