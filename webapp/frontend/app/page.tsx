
'use client';

import { useState } from 'react';

interface SearchResult {
  id: number;
  name: string;
  mz: number;
  score: number;
}

export default function Home() {
  const [module, setModule] = useState('Clinical Diagnostics');
  const [compoundName, setCompoundName] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch('http://localhost:8001/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ module, compound_name: compoundName }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An unknown error occurred');
      }

      const data = await response.json();
      setResults(data.results);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-12 bg-gray-50">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center w-full">PhytoDiscover</h1>
      </div>

      <div className="w-full max-w-2xl bg-white p-8 rounded-lg shadow-md">
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">1. Select Analysis Module</label>
          <div className="flex flex-col space-y-2">
            <label className="inline-flex items-center">
              <input type="radio" className="form-radio" name="module" value="Clinical Diagnostics" checked={module === 'Clinical Diagnostics'} onChange={(e) => setModule(e.target.value)} />
              <span className="ml-2">Clinical Diagnostics</span>
            </label>
            <label className="inline-flex items-center">
              <input type="radio" className="form-radio" name="module" value="Food Safety" checked={module === 'Food Safety'} onChange={(e) => setModule(e.target.value)} />
              <span className="ml-2">Food Safety</span>
            </label>
            <label className="inline-flex items-center">
              <input type="radio" className="form-radio" name="module" value="Forensic Toxicology" checked={module === 'Forensic Toxicology'} onChange={(e) => setModule(e.target.value)} />
              <span className="ml-2">Forensic Toxicology</span>
            </label>
          </div>
        </div>

        <div className="mb-6">
          <label htmlFor="compoundName" className="block text-gray-700 text-sm font-bold mb-2">2. Enter Compound Name</label>
          <input
            id="compoundName"
            type="text"
            value={compoundName}
            onChange={(e) => setCompoundName(e.target.value)}
            placeholder="e.g., Aspirin, Caffeine..."
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>

        <div className="flex items-center justify-center">
          <button
            onClick={handleSearch}
            disabled={isLoading || !compoundName}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-8 w-full max-w-2xl bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-8 w-full max-w-4xl">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Search Results</h2>
          <div className="overflow-x-auto bg-white rounded-lg shadow">
            <table className="min-w-full leading-normal">
              <thead>
                <tr>
                  <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">ID</th>
                  <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Compound Name</th>
                  <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">m/z</th>
                  <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Similarity Score</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result) => (
                  <tr key={result.id}>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{result.id}</td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{result.name}</td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{result.mz.toFixed(4)}</td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{result.score.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  );
}
