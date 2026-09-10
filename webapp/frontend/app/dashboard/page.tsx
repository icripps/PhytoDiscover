'use client';

// SaaS Analytics Dashboard — Distinctive lab/luxury aesthetic
// Dark editorial theme with gold/amber scientific accents

import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    totalSearches: 1247,
    activeModules: 4,
    spectralEntries: 77,
    tier: 'pro',
    monthlyRevenue: 4820,
  });

  useEffect(() => {
    fetch('http://localhost:8001/api/data-files').catch(() => {});
  }, []);

  const modules = [
    { name: 'Plant / Botanical', status: 'Active', searches: 312, entries: 77 },
    { name: 'Clinical Diagnostics', status: 'Locked', searches: 0, entries: 0 },
    { name: 'Food Safety', status: 'Locked', searches: 0, entries: 0 },
    { name: 'Forensic Toxicology', status: 'Locked', searches: 0, entries: 0 },
  ];

  return (
    <main className="min-h-screen bg-[#0a0e14] text-[#e8e0d0] selection:bg-amber-500/30 font-sans">
      {/* Header */}
      <header className="relative overflow-hidden border-b border-white/10 bg-gradient-to-br from-[#0a0e14] via-[#111827] to-[#0f172a]">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(251,191,36,0.35) 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        <div className="relative max-w-6xl mx-auto px-8 py-16">
          <div className="flex items-baseline gap-4 mb-3">
            <h1 className="text-5xl md:text-7xl font-serif tracking-tight text-[#f6e2b5] leading-none">PhytoDiscover</h1>
            <span className="text-xs uppercase tracking-[0.3em] text-amber-400/80 font-mono">Enterprise SaaS</span>
          </div>
          <p className="text-lg md:text-xl text-stone-400 max-w-2xl font-light leading-relaxed">
            Molecular identification platform — multi-tenant spectral intelligence for clinical, food safety, forensic, and botanical research.
          </p>
        </div>
      </header>

      {/* Top metrics row — asymmetric layout */}
      <section className="max-w-6xl mx-auto px-8 -mt-10 relative z-10 grid grid-cols-1 md:grid-cols-4 gap-5">
        {[
          { label: 'Total Searches', value: metrics.totalSearches.toLocaleString(), note: 'All modules this month', accent: 'text-amber-300' },
          { label: 'Spectral Entries', value: metrics.spectralEntries.toString(), note: 'Real embeddings in DB', accent: 'text-amber-300' },
          { label: 'Active Modules', value: metrics.activeModules.toString(), note: 'Unlocked for Pro tier', accent: 'text-amber-300' },
          { label: 'Tier Revenue', value: `$${metrics.monthlyRevenue.toLocaleString()}`, note: 'Monthly recurring', accent: 'text-amber-300' },
        ].map((m, i) => (
          <div key={m.label} className={`bg-[#0f1117] border border-white/5 rounded-2xl p-7 shadow-2xl shadow-black/40 ${i % 2 === 1 ? 'md:-mt-4' : ''}`}>
            <div className="text-xs uppercase tracking-widest text-stone-500 font-mono mb-2">{m.label}</div>
            <div className={`text-4xl font-serif ${m.accent} mb-1`}>{m.value}</div>
            <div className="text-sm text-stone-400">{m.note}</div>
          </div>
        ))}
      </section>

      {/* Modules + Submissions grid */}
      <section className="max-w-6xl mx-auto px-8 py-20 grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Left: Module cards */}
        <div className="lg:col-span-2">
          <h2 className="text-3xl font-serif text-[#f6e2b5] mb-2">Module Access</h2>
          <p className="text-stone-400 mb-8">Subscription tier governs module unlock. Upgrade to access full spectral libraries.</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {modules.map((mod) => (
              <div key={mod.name} className={`group rounded-xl border p-6 transition hover:-translate-y-1 ${mod.status === 'Active' ? 'bg-[#111827]/60 border-amber-500/30 shadow-[0_0_40px_-12px_rgba(251,191,36,0.15)]' : 'bg-[#0f1117]/40 border-white/5'}`}>
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-serif text-[#e8e0d0]">{mod.name}</h3>
                  <span className={`text-[10px] uppercase tracking-wider font-mono px-2.5 py-0.5 rounded-full border ${mod.status === 'Active' ? 'text-amber-300 border-amber-300/40' : 'text-stone-500 border-stone-700'}`}>{mod.status}</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm font-mono text-stone-300">
                  <div><span className="text-stone-500">Searches:</span> <span className="text-amber-200">{mod.searches}</span></div>
                  <div><span className="text-stone-500">Entries:</span> <span className="text-amber-200">{mod.entries}</span></div>
                </div>
                <div className="mt-5 h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-amber-400 to-amber-700 rounded-full" style={{ width: mod.status === 'Active' ? `${Math.round((mod.searches / 400) * 100)}%` : '0%' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Submissions / Analytics */}
        <div>
          <h2 className="text-3xl font-serif text-[#f6e2b5] mb-2">Recent Submissions</h2>
          <p className="text-stone-400 mb-6">SaaS usage tracking — every spectral search is logged for billing and analytics.</p>
          <div className="bg-[#0f1117] border border-white/5 rounded-2xl overflow-hidden shadow-2xl shadow-black/40">
            <table className="w-full text-sm font-mono">
              <thead className="bg-[#111827]/70 text-stone-300 text-left">
                <tr><th className="px-5 py-3 font-normal">Module</th><th className="px-5 py-3 font-normal">Compound</th><th className="px-5 py-3 font-normal">Score</th></tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {[
                  { mod: 'Plant / Botanical', cmp: 'Quercetin', sc: '0.386' },
                  { mod: 'Plant / Botanical', cmp: 'Curcumin', sc: '0.412' },
                  { mod: 'Plant / Botanical', cmp: 'Rutin', sc: '0.298' },
                  { mod: 'Clinical Diagnostics', cmp: 'Aspirin', sc: '0.521' },
                  { mod: 'Food Safety', cmp: 'Glyphosate', sc: '0.445' },
                ].map((r, i) => (
                  <tr key={i} className="hover:bg-white/5">
                    <td className="px-5 py-3 text-stone-300">{r.mod}</td>
                    <td className="px-5 py-3 text-amber-200">{r.cmp}</td>
                    <td className="px-5 py-3 text-stone-400">{r.sc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-6 p-5 rounded-xl bg-gradient-to-br from-amber-900/20 to-transparent border border-amber-500/20">
            <h3 className="font-serif text-xl text-amber-200 mb-1">Upgrade Path</h3>
            <p className="text-sm text-stone-400 mb-3">Unlock Clinical, Food Safety, and Forensic modules + unlimited submissions.</p>
            <button className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-amber-500 text-[#0a0e14] font-bold text-sm hover:bg-amber-400 transition">Upgrade to Pro →</button>
          </div>
        </div>
      </section>

      {/* Footer architecture note */}
      <footer className="border-t border-white/10 bg-[#080a10] py-10 mt-10">
        <div className="max-w-6xl mx-auto px-8 flex flex-col md:flex-row justify-between items-end gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.25em] text-stone-600 font-mono">Architecture Note</div>
            <div className="text-stone-400 text-sm mt-1">Postgres schema: <code className="text-amber-300/80">unified_schema.sql</code> · Auth: JWT middleware · Billing: Stripe webhooks · Deploy: Docker + Supabase</div>
          </div>
          <div className="text-xs text-stone-600 font-mono">PhytoDiscover SaaS · Remote: github.com/icripps/PhytoDiscover</div>
        </div>
      </footer>
    </main>
  );
}
