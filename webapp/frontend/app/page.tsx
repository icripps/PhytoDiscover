'use client';

import { useState, useEffect } from 'react';

// Define the structure for a single search result
interface SearchResult {
  id: number;
  name: string;
  mz: number;
  score: number;
}

export default function Home() {
  // State management from both versions, merged
  const [module, setModule] = useState('Clinical Diagnostics');
  const [compoundName, setCompoundName] = useState('');
  const [mzmlFile, setMzmlFile] = useState('');
  const [dataFiles, setDataFiles] = useState<string[]>([]);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch the list of available .mzML files from the backend on component mount
  useEffect(() => {
    const fetchMzmlFiles = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/data-files');
        if (!response.ok) {
          throw new Error('Failed to fetch data files');
        }
        const data = await response.json();
        setDataFiles(data.files);
        if (data.files.length > 0) {
          setMzmlFile(data.files[0]);
        }
      } catch (err) {
        setError('Could not connect to the backend to get data files. Is the server running?');
        console.error(err);
      }
    };
    fetchMzmlFiles();
  }, []);

  // Handle the search form submission
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await fetch('http://localhost:8001/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ module, compound_name: compoundName, mzml_file: mzmlFile }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'An unknown error occurred');
      }

      const data = await response.json();
      // The backend returns a string, which might be JSON. Let's parse it.
      try {
        const parsedResults = JSON.parse(data.results);
        setResults(parsedResults.results || []);
      } catch (parseError) {
        // If it's not JSON, it might be a simple message or an error.
        console.error('Failed to parse results JSON:', parseError);
        setError('Received malformed results from the backend.');
      }

    } catch (err) {
        if (err instanceof Error) {
            setError(`Failed to fetch: ${err.message}`);
        } else {
            setError('An unknown error occurred.');
        }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center w-full">PhytoDiscover</h1>
      </div>

      <div className="w-full max-w-3xl bg-white p-8 rounded-lg shadow-md">
        <form onSubmit={handleSearch}>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">1. Select Analysis Module</label>
            <div className="flex flex-col sm:flex-row sm:space-x-4 space-y-2 sm:space-y-0">
              <label className="flex items-center">
                <input type="radio" name="module" value="Clinical Diagnostics" checked={module === 'Clinical Diagnostics'} onChange={(e) => setModule(e.target.value)} className="form-radio h-4 w-4 text-indigo-600" />
                <span className="ml-2 text-gray-700">Clinical Diagnostics</span>
              </label>
              <label className="flex items-center">
                <input type="radio" name="module" value="Food Safety" checked={module === 'Food Safety'} onChange={(e) => setModule(e.target.value)} className="form-radio h-4 w-4 text-indigo-600" />
                <span className="ml-2 text-gray-700">Food Safety</span>
              </label>
              <label className="flex items-center">
                <input type="radio" name="module" value="Forensic Toxicology" checked={module === 'Forensic Toxicology'} onChange={(e) => setModule(e.target.value)} className="form-radio h-4 w-4 text-indigo-600" />
                <span className="ml-2 text-gray-700">Forensic Toxicology</span>
              </label>
            </div>
          </div>

          <div className="mb-6">
            <label htmlFor="compoundName" className="block text-gray-700 text-sm font-bold mb-2">2. Enter Compound Name</label>
            <input id="compoundName" type="text" value={compoundName} onChange={(e) => setCompoundName(e.target.value)} placeholder="e.g., Aspirin, Cocaine..." className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
          </div>

          <div className="mb-6">
            <label htmlFor="mzmlFile" className="block text-gray-700 text-sm font-bold mb-2">3. Select Sample Data File</label>
            <select id="mzmlFile" value={mzmlFile} onChange={(e) => setMzmlFile(e.target.value)} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required disabled={dataFiles.length === 0}>
              {dataFiles.length > 0 ? (dataFiles.map((file) => (<option key={file} value={file}>{file}</option>))) : (<option>Loading data files...</option>)}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400" disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && <div className="mt-6 p-4 bg-red-100 text-red-700 rounded">{error}</div>}

        {results.length > 0 && (
          <div className="mt-8 overflow-x-auto">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Search Results</h3>
            <table className="min-w-full leading-normal">
              <thead>
                <tr>
                  <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">ID</th>
                  <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Name</th>
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
        )}
      </div>
    </main>
  );
}
