'use client';

export default function Plans() {
  const tiers = [
    { name: 'Free', price: '$0', desc: 'Plant/Botanical module, 10 searches/mo, 1 user', locked: ['Clinical', 'Food Safety', 'Forensic'], active: false },
    { name: 'Pro', price: '$49/mo', desc: 'All modules unlocked, unlimited searches, 5 users, analytics export', locked: [], active: true },
    { name: 'Enterprise', price: 'Custom', desc: 'SSO, white-label, custom spectral libraries, HIPAA compliance', locked: [], active: false },
  ];

  return (
    <main className="min-h-screen bg-[#0a0e14] text-[#e8e0d0] selection:bg-amber-500/30 font-sans">
      <header className="relative overflow-hidden border-b border-white/10 bg-gradient-to-br from-[#0a0e14] via-[#111827] to-[#0f172a]">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(251,191,36,0.35) 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        <div className="relative max-w-5xl mx-auto px-8 py-16">
          <h1 className="text-5xl md:text-7xl font-serif tracking-tight text-[#f6e2b5] leading-none">Pricing</h1>
          <p className="text-lg text-stone-400 mt-4 max-w-xl">Unlock clinical, food, forensic, and plant modules with a single subscription.</p>
        </div>
      </header>

      <section className="max-w-5xl mx-auto px-8 py-20 grid grid-cols-1 md:grid-cols-3 gap-6">
        {tiers.map((t) => (
          <div key={t.name} className={`rounded-2xl p-8 border shadow-2xl shadow-black/40 transition hover:-translate-y-1 ${t.active ? 'bg-gradient-to-b from-[#111827] to-[#0f1117] border-amber-400/40' : 'bg-[#0f1117]/40 border-white/5'}`}>
            <h2 className="text-3xl font-serif text-[#f6e2b5]">{t.name}</h2>
            <div className="text-amber-300 font-mono text-2xl mt-3">{t.price}<span className="text-stone-500 text-sm">/mo</span></div>
            <p className="text-stone-400 text-sm mt-3">{t.desc}</p>
            <ul className="mt-6 space-y-2 text-sm">
              {['Plant / Botanical', 'Clinical Diagnostics', 'Food Safety', 'Forensic Toxicology'].map((m) => (
                <li key={m} className={`flex items-center gap-2 ${t.locked.includes(m) ? 'text-stone-600' : 'text-amber-200'}`}>
                  <span>{t.locked.includes(m) ? '×' : '✓'}</span> {m}
                </li>
              ))}
            </ul>
            <a href="/" className={`mt-8 block text-center rounded-full py-3 font-bold text-sm transition ${t.active ? 'bg-amber-500 text-[#0a0e14] hover:bg-amber-400' : 'bg-white/5 text-stone-300 hover:bg-white/10 border border-white/10'}`}>{t.active ? 'Upgrade to Pro' : 'Select Plan'}</a>
          </div>
        ))}
      </section>
    </main>
  );
}
