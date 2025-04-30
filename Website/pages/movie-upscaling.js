import { useState, useEffect } from 'react'
import styles from '../styles/MovieUpscaling.module.css'

export default function UpscalePage() {
    const [movies, setMovies] = useState([])
    const [selected, setSelected] = useState("")
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState(null)
    const [error, setError] = useState(null)

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
        setError(null)
        setMessage(null)
        try {
            const res = await fetch(`${base}/upscale`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ movie: selected }),
            })
            if (!res.ok) throw new Error(await res.text())
            const { message } = await res.json()
            setMessage(message)
        } catch {
            setError("Upscaling failed")
        } finally {
            setLoading(false)
        }
    }

    return (
        <main className={styles.main}>
            <h1 className={styles.title}>Movie Upscaling</h1>
            {error && <p className={styles.error}>{error}</p>}
            {message && <p className={styles.message}>{message}</p>}

            <form onSubmit={handleSubmit} className={styles.searchForm}>
                <select
                    className={styles.searchInput}
                    value={selected}
                    onChange={e => setSelected(e.target.value)}
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
                    {loading ? "Upscaling…" : "Start Upscale"}
                </button>
            </form>
        </main>
    )
}
