export type AuthUser = {
  id: string;
  name: string;
  email: string;
};

export type AuthSession = {
  accessToken: string;
  refreshToken: string;
  user: AuthUser;
};

const SESSION_KEY = "ecclesia-next-session";

export function saveSession(session: AuthSession) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;

  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    clearSession();
    return null;
  }
}

export function clearSession() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(SESSION_KEY);
  }
}

export function getAccessToken(): string | null {
  return getSession()?.accessToken ?? null;
}

export async function login(email: string, password: string): Promise<AuthSession> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail ?? "Não foi possível entrar.");
  }

  const session: AuthSession = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    user: data.user,
  };

  saveSession(session);
  return session;
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const session = getSession();

  if (!session) {
    throw new Error("Sessão não encontrada");
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const response = await fetch(`${apiUrl}/api/v1/auth/me`, {
    headers: {
      Authorization: `Bearer ${session.accessToken}`,
    },
  });

  if (!response.ok) {
    clearSession();
    throw new Error("Sessão inválida ou expirada");
  }

  return response.json();
}
