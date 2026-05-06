import { writable } from 'svelte/store'

type Theme = 'light' | 'dark'

const stored = (typeof localStorage !== 'undefined' && localStorage.getItem('theme')) as Theme | null
const initial: Theme = stored === 'dark' ? 'dark' : 'light'

export const theme = writable<Theme>(initial)

const apply = (t: Theme) => {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', t)
  }
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('theme', t)
  }
}

apply(initial)
theme.subscribe(apply)

export const toggleTheme = () => {
  theme.update(t => (t === 'dark' ? 'light' : 'dark'))
}
