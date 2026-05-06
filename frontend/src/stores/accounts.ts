import { writable, get } from 'svelte/store'

export type Account = {
  id: number
  nome: string
  tipo: string
  saldo_inicial: number
  cor: string
  icone: string
  padrao: boolean
  ativa: boolean
  saldo: number
}

export const accountsStore = writable<Account[]>([])

const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })

export const fetchAccounts = async () => {
  try {
    const r = await fetch('/api/accounts', { headers: auth() })
    if (r.ok) {
      const data: Account[] = await r.json()
      accountsStore.set(data)
      return data
    }
  } catch (e) {
    console.error('Erro ao carregar contas:', e)
  }
  return []
}

export const getDefaultAccount = (): Account | null => {
  const list = get(accountsStore)
  return list.find(a => a.padrao) || list[0] || null
}
