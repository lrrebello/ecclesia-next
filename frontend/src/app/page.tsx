export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-8">
      <div className="max-w-xl text-center space-y-4">
        <h1 className="text-4xl font-bold">Ecclesia Next</h1>
        <p className="text-slate-300">Nova plataforma segura e moderna para gestão eclesiástica.</p>
        <a className="inline-block rounded-lg bg-indigo-500 px-5 py-3 font-medium" href="/login">Entrar</a>
      </div>
    </main>
  );
}
