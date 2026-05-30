import { get } from 'svelte/store'
import { valuesHidden } from '../stores/privacy'

const MASK = 'R$ •••••'

const formatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

/**
 * Formata um valor como moeda BRL.
 * Se o store valuesHidden estiver ativo, retorna máscara.
 */
export const fmt = (value: number | null | undefined): string => {
  if (get(valuesHidden)) return MASK
  return formatter.format(Number(value || 0))
}

/**
 * Versão reativa: precisa receber o valor atual do store como argumento.
 * Uso em templates: $: maskedValue = fmtMasked(value, $valuesHidden)
 */
export const fmtMasked = (value: number | null | undefined, hidden: boolean): string => {
  if (hidden) return MASK
  return formatter.format(Number(value || 0))
}

const compactFormatter = new Intl.NumberFormat('pt-BR', {
  notation: 'compact',
  compactDisplay: 'short',
  maximumFractionDigits: 1,
})

/**
 * Versao compacta sem "R$" para uso em telas pequenas.
 * Ex: 14952 -> "15 mil", 1234567 -> "1,2 mi", 450 -> "450"
 */
export const fmtCompact = (value: number | null | undefined, hidden: boolean): string => {
  if (hidden) return '•••'
  const n = Number(value || 0)
  const abs = Math.abs(n)
  if (abs < 1000) {
    return n.toLocaleString('pt-BR', { maximumFractionDigits: 0 })
  }
  return compactFormatter.format(n)
}
