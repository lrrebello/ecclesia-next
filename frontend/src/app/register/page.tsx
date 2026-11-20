"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ChurchOption = {
  id: string;
  name: string;
  slug: string;
  branches: { id: string; name: string; slug: string }[];
};

export default function RegisterPage() {
  const router = useRouter();
  const [churches, setChurches] = useState<ChurchOption[]>([]);
  const [selectedChurch, setSelectedChurch] = useState("");
  const [branchSlug, setBranchSlug] = useState("");
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    birth_date: "",
    baptism_date: "",
    conversion_date: "",
    gender: "",
    marital_status: "",
    spouse_name: "",
    documents: "",
    tax_id: "",
    address: "",
    phone: "",
    postal_code: "",
    concelho: "",
    localidade: "",
    education_level: "",
    observations: "",
    data_consent: false,
    marketing_consent: false,
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadChurches() {
      const response = await fetch(`${API_URL}/api/v1/churches/public`);
      const data = await response.json();
      setChurches(data.churches);
    }

    loadChurches();
  }, []);

  function update(field: string, value: string | boolean) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    const payload = {
      ...form,
      branch_slug: branchSlug,
      birth_date: form.birth_date || null,
      baptism_date: form.baptism_date || null,
      conversion_date: form.conversion_date || null,
    };

    const response = await fetch(`${API_URL}/api/v1/members/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      setError(data.detail ?? "Não foi possível concluir o cadastro.");
    } else {
      setMessage("Cadastro realizado. Aguarde a aprovação da liderança.");
      setTimeout(() => router.push("/login"), 2500);
    }

    setLoading(false);
  }

  const selected = churches.find((church) => church.id === selectedChurch);

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-white">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold">Cadastro de membro</h1>
        <p className="mt-2 text-slate-400">
          Escolha a igreja e a filial onde deseja se cadastrar.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-xl bg-slate-900 p-6">
          <select
            className="w-full rounded-lg bg-slate-800 p-3"
            value={selectedChurch}
            onChange={(event) => {
              setSelectedChurch(event.target.value);
              setBranchSlug("");
            }}
            required
          >
            <option value="">Selecione a igreja</option>
            {churches.map((church) => (
              <option key={church.id} value={church.id}>
                {church.name}
              </option>
            ))}
          </select>

          <select
            className="w-full rounded-lg bg-slate-800 p-3"
            value={branchSlug}
            onChange={(event) => setBranchSlug(event.target.value)}
            required
            disabled={!selected}
          >
            <option value="">Selecione a filial</option>
            {selected?.branches.map((branch) => (
              <option key={branch.id} value={branch.slug}>
                {branch.name}
              </option>
            ))}
          </select>

          <div className="grid gap-4 sm:grid-cols-2">
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Nome completo" value={form.name} onChange={(e) => update("name", e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="E-mail" type="email" value={form.email} onChange={(e) => update("email", e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Senha" type="password" value={form.password} onChange={(e) => update("password", e.target.value)} required />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Telefone" value={form.phone} onChange={(e) => update("phone", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.birth_date} onChange={(e) => update("birth_date", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.baptism_date} onChange={(e) => update("baptism_date", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" type="date" value={form.conversion_date} onChange={(e) => update("conversion_date", e.target.value)} />
            <select className="rounded-lg bg-slate-800 p-3" value={form.gender} onChange={(e) => update("gender", e.target.value)}>
              <option value="">Gênero</option>
              <option value="Masculino">Masculino</option>
              <option value="Feminino">Feminino</option>
              <option value="Prefiro não informar">Prefiro não informar</option>
            </select>
            <select className="rounded-lg bg-slate-800 p-3" value={form.marital_status} onChange={(e) => update("marital_status", e.target.value)}>
              <option value="">Estado civil</option>
              <option value="Solteiro(a)">Solteiro(a)</option>
              <option value="Casado(a)">Casado(a)</option>
              <option value="Divorciado(a)">Divorciado(a)</option>
              <option value="Viúvo(a)">Viúvo(a)</option>
            </select>
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Nome do cônjuge" value={form.spouse_name} onChange={(e) => update("spouse_name", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Documento de identificação" value={form.documents} onChange={(e) => update("documents", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="NIF / CPF" value={form.tax_id} onChange={(e) => update("tax_id", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Endereço" value={form.address} onChange={(e) => update("address", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Código postal" value={form.postal_code} onChange={(e) => update("postal_code", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Concelho / município" value={form.concelho} onChange={(e) => update("concelho", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Localidade" value={form.localidade} onChange={(e) => update("localidade", e.target.value)} />
            <input className="rounded-lg bg-slate-800 p-3" placeholder="Escolaridade" value={form.education_level} onChange={(e) => update("education_level", e.target.value)} />
          </div>

          <textarea className="w-full rounded-lg bg-slate-800 p-3" placeholder="Observações, alergias, tamanho de roupa, etc." value={form.observations} onChange={(e) => update("observations", e.target.value)} />

          <label className="flex items-center gap-3 text-sm">
            <input type="checkbox" checked={form.data_consent} onChange={(e) => update("data_consent", e.target.checked)} required />
            Autorizo o tratamento dos meus dados pessoais.
          </label>

          <label className="flex items-center gap-3 text-sm">
            <input type="checkbox" checked={form.marketing_consent} onChange={(e) => update("marketing_consent", e.target.checked)} />
            Autorizo o recebimento de comunicações da igreja.
          </label>

          <button className="w-full rounded-lg bg-indigo-500 p-3 font-medium disabled:opacity-50" disabled={loading}>
            {loading ? "Enviando..." : "Criar cadastro"}
          </button>

          {message && <p className="text-sm text-green-400">{message}</p>}
          {error && <p className="text-sm text-red-400">{error}</p>}
        </form>
      </div>
    </main>
  );
}
