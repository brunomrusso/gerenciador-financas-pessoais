import { writable } from 'svelte/store'

const STORAGE_KEY = 'valuesHidden'

const initial = (() => {
  try { return localStorage.getItem(STORAGE_KEY) === '1' } catch { return false }
})()

export const valuesHidden = writable<boolean>(initial)

valuesHidden.subscribe(v => {
  try { localStorage.setItem(STORAGE_KEY, v ? '1' : '0') } catch {}
})

export const toggleValuesHidden = () => valuesHidden.update(v => !v)
