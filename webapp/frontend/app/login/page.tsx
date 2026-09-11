'use client';
import { useState } from 'react';
export default function Login() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');
  return (
    <main className="min-h-screen bg-[#0a0e14] text-[#e8e0d0] flex items-center justify-center p-8 font-sans">
      <div className="w-full max-w-md bg-[#111827] border border-amber-500/20 rounded-2xl p-10 shadow-2xl">
        <h1 className="text-4xl font-serif text-[#f6e2b5] mb-2">PhytoDiscover</h1>
        <p className="text-stone-400 text-sm mb-6">Sign in to access spectral analysis modules.</p>
        <form onSubmit={(e) => { e.preventDefault(); setStatus('Supabase Auth session started — complete browser auth at https://mcp.supabase.com/mcp'); }} className="space-y-4">
          <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@lab.com" className="w-full px-4 py-3 rounded-lg bg-[#0f1117] border border-white/10 text-stone-200 focus:outline-none focus:border-amber-400" />
          <button type="submit" className="w-full py-3 rounded-lg bg-amber-500 text-[#0a0e14] font-bold hover:bg-amber-400 transition">Continue with Supabase</button>
        </form>
        {status && <div className="mt-4 text-amber-200 text-sm">{status}</div>}
      </div>
    </main>
  );
}
