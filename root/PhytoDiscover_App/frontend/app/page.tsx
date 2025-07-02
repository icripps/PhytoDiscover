
'use client';

import { useState } from 'react';

interface SearchResult {
    query_id: string;
    match_id: string;
    score: number;
    mz_query: number;
    mz_match: number;
}

export default function Home() {
    const [compoundName, setCompoundName] = useState('Aspirin');
    const [filePath, setFilePath] = useState('data/example_data.mzML');
    const [dbName, setDbName] = useState('clinical_diagnostics.db');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setResults([]);

        try {
            const params = new URLSearchParams({
                compound_name: compoundName,
                file_path: filePath,
                db_name: dbName,
            });

            const response = await fetch(`/api/search?${params.toString()}`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An unknown error occurred');
            }

            const data = await response.json();
            setResults(data.results || []);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch search results.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50 font-sans">
            <div className="w-full max-w-4xl">
                <header className="text-center mb-10">
                    <h1 className="text-5xl font-bold text-gray-800">PhytoDiscover</h1>
                    <p className="text-xl text-gray-500 mt-2">AI-Powered Phytochemical Analysis</p>
                </header>

                <div className="bg-white p-8 rounded-xl shadow-md">
                    <form onSubmit={handleSearch}>
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-lg font-medium text-gray-700 mb-2">1. Select Analysis Module</h3>
                                <div className="flex gap-x-6">
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="dbName"
                                            value="clinical_diagnostics.db"
                                            checked={dbName === 'clinical_diagnostics.db'}
                                            onChange={(e) => setDbName(e.target.value)}
                                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                        />
                                        <span className="text-gray-700">Clinical Diagnostics</span>
                                    </label>
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="dbName"
                                            value="food_safety.db"
                                            checked={dbName === 'food_safety.db'}
                                            onChange={(e) => setDbName(e.target.value)}
                                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                        />
                                        <span className="text-gray-700">Food Safety</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <label htmlFor="compoundName" className="block text-lg font-medium text-gray-700">2. Enter Compound Name</label>
                                <input
                                    id="compoundName"
                                    type="text"
                                    value={compoundName}
                                    onChange={(e) => setCompoundName(e.target.value)}
                                    className="mt-2 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="e.g., Aspirin"
                                />
                            </div>

                            <div>
                                <label htmlFor="filePath" className="block text-lg font-medium text-gray-700">3. Select Data File</label>
                                <select
                                    id="filePath"
                                    value={filePath}
                                    onChange={(e) => setFilePath(e.target.value)}
                                    className="mt-2 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white"
                                >
                                    <option value="data/example_data.mzML">Example Data (General)</option>
                                    <option value="data/synthetic_data.mzML">Synthetic Data (Metabolites)</option>
                                </select>
                            </div>
                        </div>

                        <div className="mt-8">
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed"
                            >
                                {isLoading ? 'Searching...' : 'Search'}
                            </button>
                        </div>
                    </form>
                </div>

                {error && (
                    <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md" role="alert">
                        <strong className="font-bold">Error: </strong>
                        <span className="block sm:inline">{error}</span>
                    </div>
                )}

                {results.length > 0 && (
                    <div className="mt-10 bg-white p-8 rounded-xl shadow-md">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4">Search Results</h2>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Query ID</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Match ID</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Similarity Score</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Query M/Z</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Match M/Z</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {results.map((result, index) => (
                                        <tr key={index}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{result.query_id}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{result.match_id}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{result.score.toFixed(4)}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{result.mz_query.toFixed(4)}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{result.mz_match.toFixed(4)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
