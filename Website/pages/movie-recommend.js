import { useState } from 'react'
import styles from '../styles/MovieRecommend.module.css'

export default function Home() {
  const [query, setQuery] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    setError(null)
    setRecommendations([])

    const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'
    try {
      const res = await fetch(`${base}/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: query }),
      })
      const { recommendations: recs } = await res.json()

      if (recs.length === 1 && recs[0] === 'Error') {
        setError('Sorry, something went wrong – please try again.')
      } else {
        setRecommendations(recs)
      }
    } catch (err) {
      console.error(err)
      setError('Network error – please check your connection.')
    }
  }

  return (
    <>
      <main className={styles.main}>
        <h1 className={styles.title}>Movie Recommendation</h1>

        <form className={styles.searchForm} onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search for movies…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className={styles.searchInput}
          />
          <button type="submit" className={styles.searchButton}>
            Search
          </button>
        </form>
        {error && <p className={styles.error}>{error}</p>}
        {recommendations.length > 0 && (
          <ul className={styles.resultsList}>
            {recommendations.map((movie, idx) => (
              <li key={idx}>{movie}</li>
            ))}
          </ul>
        )}
      </main>
    </>
  )
}
