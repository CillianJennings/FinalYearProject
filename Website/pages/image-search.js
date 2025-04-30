import { useState, useCallback } from 'react'
import MainNavigation from '../components/layout/MainNavigation'
import styles from '../styles/ImageSearch.module.css'

export default function ImageSearch() {
    const [file, setFile] = useState(null)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)

    const uploadImage = async (file) => {
        setLoading(true)
        setError(null)
        setResult(null)

        const formData = new FormData()
        formData.append('file', file)

        const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'
        try {
            const res = await fetch(`${base}/search-image`, {
                method: 'POST',
                body: formData,
            })
            if (!res.ok) {
                const msg = await res.text()
                throw new Error(msg || 'Upload failed')
            }
            const json = await res.json()
            setResult(json)
        } catch (err) {
            console.error(err)
            setError('Sorry, could not process that image.')
        } finally {
            setLoading(false)
        }
    }

    const handleDrop = useCallback(
        (e) => {
            e.preventDefault()
            if (e.dataTransfer.files?.[0]) {
                const f = e.dataTransfer.files[0]
                setFile(f)
                uploadImage(f)
            }
        },
        []
    )

    const handleDragOver = useCallback((e) => {
        e.preventDefault()
    }, [])

    const handleChange = useCallback(
        (e) => {
            if (e.target.files?.[0]) {
                const f = e.target.files[0]
                setFile(f)
                uploadImage(f)
            }
        },
        []
    )

    return (
        <>
            <main className={styles.main}>
                <h1 className={styles.title}>Image Movie Search</h1>

                <div
                    className={styles.dropzone}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onClick={() => document.getElementById('fileInput').click()}
                >
                    {file ? (
                        <p>Uploading: {file.name}…</p>
                    ) : (
                        <p>Drag your image here, or click to select</p>
                    )}
                    <input
                        id="fileInput"
                        type="file"
                        accept="image/*"
                        onChange={handleChange}
                        className={styles.fileInput}
                    />
                </div>

                {loading && <p className={styles.status}>Analyzing image…</p>}
                {error && <p className={styles.error}>{error}</p>}

                {result && (
                    <div className={styles.result}>
                        <h2>Best match</h2>
                        <p>
                            <strong>Movie:</strong> {result.movie}
                        </p>
                        <p>
                            <strong>Timestamp:</strong> {result.seconds}
                        </p>
                        <p>
                            <strong>Score:</strong> {result.score.toFixed(3)}
                        </p>
                    </div>
                )}
            </main>
        </>
    )
}
