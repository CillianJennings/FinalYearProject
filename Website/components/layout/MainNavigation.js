import classes from './MainNavigation.module.css'
import Link from 'next/link'
import { useContext } from 'react'
import { useRouter } from 'next/router'

function MainNavigation() {
 
  const router = useRouter()
  const contents = []
  
  return (
    <header className={classes.header}>
      <nav>
        <ul>
          <li><Link href='/subtitle-generation'>Subtitle Generation</Link></li>
          <li><Link href='/image-search'>Image Movie Search</Link></li>
          <li><Link href='/movie-upscaling'>Movie Upscaling</Link></li>
          <li><Link href='/movie-recommend'>Movie Recommendation</Link></li>
        </ul>
      </nav>
    </header>
  )
}

export default MainNavigation
