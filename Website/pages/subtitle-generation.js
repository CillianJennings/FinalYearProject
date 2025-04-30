import { useState, useEffect } from 'react'
import styles from '../styles/SubtitleGen.module.css'

export default function SubtitleGenerator() {
  const [movies, setMovies]     = useState([])
  const [selected, setSelected] = useState("")
  const [loading, setLoading]   = useState(false)
  const [message, setMessage]   = useState("")
  const [error, setError]       = useState("")

  const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'

  useEffect(() => {
    fetch(`${base}/movies`)
      .then(r => r.json())
      .then(setMovies)
      .catch(() => setError("Could not load movie list"))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!selected) return
    setLoading(true)
    setError("")
    setMessage("")

    try {
      const res = await fetch(`${base}/generate-subs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ movie: selected }),
      })
      if (!res.ok) throw new Error(await res.text())
      const { message: msg } = await res.json()
      setMessage(msg)
    } catch {
      setError("Subtitle generation failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Subtitle Generator</h1>

      <form onSubmit={handleSubmit} className={styles.searchForm}>
        <select
          className={styles.searchInput}
          value={selected}
          onChange={e => setSelected(e.target.value)}
          disabled={loading}
          required
        >
          <option value="">— pick a movie —</option>
          {movies.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        <button
          type="submit"
          className={styles.searchButton}
          disabled={loading || !selected}
        >
          {loading ? "Generating…" : "Generate SRT"}
        </button>
      </form>

      {message && <p className={styles.message}>{message}</p>}
      {error   && <p className={styles.error}>{error}</p>}
    </main>
  )
}
