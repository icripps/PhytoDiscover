'use client';

import { useState } from 'react';

interface Match {
  compound_name: string;
  precursor_mz: number;
  score: number;
}

interface SearchResult {
  query: {
    compound_name: string;
    precursor_mz: number;
  };
  matches: Match[];
  error?: string;
}

export default function Home() {
  const [compoundName, setCompoundName] = useState('Caffeine');
  const [filePath, setFilePath] = useState('data/example_data.mzML');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!compoundName || !filePath) {
      setError('Please provide both a compound name and a file path.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(`http://localhost:8001/api/search?compound_name=${encodeURIComponent(compoundName)}&file_path=${encodeURIComponent(filePath)}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'An unknown error occurred.');
      }

      if (data.error) {
        throw new Error(data.error);
      }
      
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50 font-sans">
      <div className="w-full max-w-5xl text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-800">PhytoDiscover</h1>
        <p className="mt-2 text-lg text-gray-600">AI-Powered Phytochemical Analysis</p>
      </div>

      <div className="w-full max-w-2xl bg-white p-8 rounded-lg shadow-lg">
        <div className="space-y-6">
          <div>
            <label htmlFor="compound" className="block text-sm font-medium text-gray-700 mb-1">
              Compound Name
            </label>
            <input
              type="text"
              id="compound"
              value={compoundName}
              onChange={(e) => setCompoundName(e.target.value)}
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              placeholder="e.g., Caffeine"
            />
          </div>

          <div>
            <label htmlFor="filepath" className="block text-sm font-medium text-gray-700 mb-1">
              Data File Path (relative to project root)
            </label>
            <input
              type="text"
              id="filepath"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black"
              placeholder="e.g., data/example_data.mzML"
            />
          </div>
        </div>

        <div className="mt-8">
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-6 w-full max-w-2xl p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
          <p><strong>Error:</strong> {error}</p>
        </div>
      )}

      {results && (
        <div className="mt-8 w-full max-w-4xl">
          <h2 className="text-2xl font-semibold text-gray-700 text-center">Search Results</h2>
          <div className="mt-4 bg-white shadow-lg rounded-lg overflow-hidden">
            <div className="p-6 border-b bg-gray-50">
              <h3 className="text-lg font-medium text-gray-900">Query Spectrum</h3>
              <p className="text-sm text-gray-600">Compound: <span className="font-semibold">{results.query.compound_name}</span></p>
              <p className="text-sm text-gray-600">Precursor m/z: <span className="font-semibold">{results.query.precursor_mz?.toFixed(4)}</span></p>
            </div>
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900">Best Match</h3>
              {results.matches.length > 0 ? (
                <ul className="divide-y divide-gray-200">
                  {results.matches.map((match, index) => (
                    <li key={index} className="py-4 flex justify-between items-center">
                      <div>
                        <p className="text-md font-semibold text-indigo-600">{match.compound_name}</p>
                        <p className="text-sm text-gray-500">Library m/z: {match.precursor_mz.toFixed(4)}</p>
                      </div>
                      <span className={`px-3 py-1 text-sm font-semibold rounded-full ${match.score > 0.8 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        Score: {match.score.toFixed(4)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-gray-500">No matches found in the library.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
