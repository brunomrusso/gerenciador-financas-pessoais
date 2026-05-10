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
