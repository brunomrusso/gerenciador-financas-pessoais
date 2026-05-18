import { writable } from 'svelte/store'

const STORAGE_KEY = 'cashflow:collapsed_sections'

function load(): Record<string, boolean> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function save(value: Record<string, boolean>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
  } catch {}
}

export const collapsedSections = writable<Record<string, boolean>>(load())

collapsedSections.subscribe(save)

export function toggleSection(key: string) {
  collapsedSections.update((c) => ({ ...c, [key]: !c[key] }))
}

export function setSectionCollapsed(key: string, collapsed: boolean) {
  collapsedSections.update((c) => ({ ...c, [key]: collapsed }))
}

export function collapseAll(keys: string[]) {
  collapsedSections.update((c) => {
    const next = { ...c }
    for (const k of keys) next[k] = true
    return next
  })
}

export function expandAll(keys: string[]) {
  collapsedSections.update((c) => {
    const next = { ...c }
    for (const k of keys) next[k] = false
    return next
  })
}

// Lista canonica de chaves de secao (para usar no atalho global)
export const SECTION_KEYS = [
  'accounts',
  'quickstats',
  'budget',
  'tagbudget',
  'saldoanterior',
  'salario',
  'salaries',
  'discounts',
  'transfers',
  'expenses',
  'cards',
  'investments',
]
