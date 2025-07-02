'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [module, setModule] = useState('clinical');
  const [compoundName, setCompoundName] = useState('');
  const [mzmlFile, setMzmlFile] = useState('');
  const [dataFiles, setDataFiles] = useState([]);
  const [results, setResults] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

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

  const handleSearch = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResults('');

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
      setResults(data.results);

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
        <h1 className="text-4xl font-bold text-gray-800 mb-8">PhytoDiscover</h1>
      </div>

      <div className="w-full max-w-3xl bg-white p-8 rounded-lg shadow-md">
        <form onSubmit={handleSearch}>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">1. Select Analysis Module</label>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="module"
                  value="clinical"
                  checked={module === 'clinical'}
                  onChange={(e) => setModule(e.target.value)}
                  className="form-radio h-4 w-4 text-indigo-600"
                />
                <span className="ml-2 text-gray-700">Clinical Diagnostics</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="module"
                  value="food_safety"
                  checked={module === 'food_safety'}
                  onChange={(e) => setModule(e.target.value)}
                  className="form-radio h-4 w-4 text-indigo-600"
                />
                <span className="ml-2 text-gray-700">Food Safety</span>
              </label>
            </div>
          </div>

          <div className="mb-6">
            <label htmlFor="compoundName" className="block text-gray-700 text-sm font-bold mb-2">
              2. Enter Compound Name to Search
            </label>
            <input
              id="compoundName"
              type="text"
              value={compoundName}
              onChange={(e) => setCompoundName(e.target.value)}
              placeholder="e.g., Aspirin, Glyphosate..."
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>

          <div className="mb-6">
            <label htmlFor="mzmlFile" className="block text-gray-700 text-sm font-bold mb-2">
              3. Select Sample Data File
            </label>
            <select
              id="mzmlFile"
              value={mzmlFile}
              onChange={(e) => setMzmlFile(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
              disabled={dataFiles.length === 0}
            >
              {dataFiles.length > 0 ? (
                dataFiles.map((file) => (
                  <option key={file} value={file}>
                    {file}
                  </option>
                ))
              ) : (
                <option>Loading data files...</option>
              )}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400"
              disabled={isLoading}
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && <div className="mt-6 p-4 bg-red-100 text-red-700 rounded">{error}</div>}
        {results && (
          <div className="mt-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Search Results</h2>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm">
              {results}
            </pre>
          </div>
        )}
      </div>
    </main>
  );
}
