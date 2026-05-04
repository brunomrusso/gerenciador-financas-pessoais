import { writable } from 'svelte/store'

interface Record {
  id: number
  year: number
  month: string
  saldo_anterior: number
  salario_bruto: number
  discounts: any[]
  expenses: any[]
  card_details: any[]
  investments: any[]
}

interface RecordsState {
  records: Record[]
  currentRecord: Record | null
  loading: boolean
  error: string | null
}

const initialState: RecordsState = {
  records: [],
  currentRecord: null,
  loading: false,
  error: null
}

export const recordsStore = writable<RecordsState>(initialState)

const getAuthHeader = () => {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
}

export const fetchRecords = async (month?: string, year?: string) => {
  recordsStore.update(state => ({ ...state, loading: true, error: null }))
  
  try {
    let url = '/api/records'
    const params = new URLSearchParams()
    if (month) params.append('month', month)
    if (year) params.append('year', year)
    if (params.toString()) url += '?' + params.toString()
    
    const response = await fetch(url, {
      headers: getAuthHeader()
    })
    
    if (!response.ok) throw new Error('Falha ao carregar registros')
    
    const data = await response.json()
    recordsStore.update(state => ({
      ...state,
      records: data,
      loading: false
    }))
  } catch (error: any) {
    recordsStore.update(state => ({
      ...state,
      loading: false,
      error: error.message
    }))
    throw error
  }
}

export const createRecord = async (month: string, year: number) => {
  try {
    const response = await fetch('/api/records', {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ month, year })
    })
    
    if (!response.ok) throw new Error('Falha ao criar registro')
    
    const data = await response.json()
    recordsStore.update(state => ({
      ...state,
      currentRecord: data
    }))
    
    return data
  } catch (error: any) {
    recordsStore.update(state => ({
      ...state,
      error: error.message
    }))
    throw error
  }
}

export const updateRecord = async (recordId: number, updates: any) => {
  try {
    const response = await fetch(`/api/records/${recordId}`, {
      method: 'PUT',
      headers: getAuthHeader(),
      body: JSON.stringify(updates)
    })
    
    if (!response.ok) throw new Error('Falha ao atualizar registro')
    
    const data = await response.json()
    recordsStore.update(state => ({
      ...state,
      currentRecord: data
    }))
    
    return data
  } catch (error: any) {
    recordsStore.update(state => ({
      ...state,
      error: error.message
    }))
  }
}

export const addDiscount = async (recordId: number, descricao: string, valor: number) => {
  try {
    const response = await fetch(`/api/records/${recordId}/discounts`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ descricao, valor })
    })
    
    if (!response.ok) throw new Error('Falha ao adicionar desconto')
    
    await fetchRecords()
  } catch (error: any) {
    recordsStore.update(state => ({
      ...state,
      error: error.message
    }))
  }
}

export const addExpense = async (recordId: number, descricao: string, valor: number, tipo: string = 'Despesa') => {
  try {
    const response = await fetch(`/api/records/${recordId}/expenses`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ descricao, valor, tipo })
    })
    
    if (!response.ok) throw new Error('Falha ao adicionar despesa')
    
    await fetchRecords()
  } catch (error: any) {
    recordsStore.update(state => ({
      ...state,
      error: error.message
    }))
  }
}

export const addInvestment = async (recordId: number, descricao: string, valor: number) => {
  try {
    const response = await fetch(`/api/records/${recordId}/investments`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ descricao, valor })
    })
    
    if (!response.ok) throw new Error('Falha ao adicionar investimento')
    
    await fetchRecords()
  } catch (error: any) {
    recordsStore.update(state => ({
      ...state,
      error: error.message
    }))
  }
}
