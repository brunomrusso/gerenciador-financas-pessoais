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

const compactMillions = new Intl.NumberFormat('pt-BR', {
  notation: 'compact',
  compactDisplay: 'short',
  maximumFractionDigits: 1,
})

const noSymbolFormatter = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

/**
 * Versao sem "R$" para telas pequenas.
 * - Se >= 1 milhao: notacao compacta (ex: "1,2 mi")
 * - Caso contrario: numero completo com 2 casas (ex: "14.952,30")
 */
export const fmtCompact = (value: number | null | undefined, hidden: boolean): string => {
  if (hidden) return '•••'
  const n = Number(value || 0)
  const abs = Math.abs(n)
  if (abs >= 1_000_000) {
    return compactMillions.format(n)
  }
  return noSymbolFormatter.format(n)
}
