import React, { useState } from 'react'

export default function App() {
  const [query, setQuery] = useState('attempted murder with intent')
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handlePredict(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ crime_description: query, top_k: Number(topK) })
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || res.statusText)
      }

      const data = await res.json()
      setResults(data)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>IPC RAG Predictor</h1>
      <form onSubmit={handlePredict} className="form">
        <label>Crime description</label>
        <textarea value={query} onChange={e => setQuery(e.target.value)} rows={4} />

        <label>Top K</label>
        <input type="number" value={topK} min={1} max={20} onChange={e => setTopK(e.target.value)} />

        <button type="submit" disabled={loading}>{loading ? 'Searching...' : 'Predict'}</button>
      </form>

      {error && <div className="error">{error}</div>}

      {results && (
        <div className="results">
          <h2>Results (total: {results.total_retrieved})</h2>
          <ul>
            {results.predictions.map((p, i) => (
              <li key={i}>
                <strong>{p.section} — {p.title}</strong>
                <div>Score: {p.score} · Confidence: {p.confidence}</div>
                <p>{p.excerpt}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
