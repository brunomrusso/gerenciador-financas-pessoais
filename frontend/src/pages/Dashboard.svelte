<script lang="ts">
  import { onMount } from 'svelte'
  import { recordsStore, fetchRecords, createRecord, updateRecord } from '../stores/records'
  import { authStore } from '../stores/auth'
  import { logout, loadUser } from '../stores/auth'
  import MonthSelector from '../components/MonthSelector.svelte'
  import SummaryCards from '../components/SummaryCards.svelte'
  import DataTable from '../components/DataTable.svelte'
  import ExpenseTable from '../components/ExpenseTable.svelte'
  import CardSection from '../components/CardSection.svelte'
  import BudgetSection from '../components/BudgetSection.svelte'
  import InvestmentSection from '../components/InvestmentSection.svelte'
  import QuickStats from '../components/QuickStats.svelte'
  import HistoryChart from '../components/HistoryChart.svelte'
  import AccountsSection from '../components/AccountsSection.svelte'
  import { theme, toggleTheme } from '../stores/theme'
  import { fetchAccounts } from '../stores/accounts'

  const months = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
  // Nota: nomes sem acentos para compatibilidade com URL params e banco de dados
  let selectedMonth = months[new Date().getMonth()]
  let selectedYear = new Date().getFullYear()
  let currentRecord: any = null
  let showHistory = false
  let loading = false
  let errorMsg = ''
  let cardFaturas: any[] = []
  let userName = ''
  let investmentSummary = { saldo_total: 0, aportes_mes: 0, saques_mes: 0, rendimentos_mes: 0, liquido_mes: 0 }

  // chave reativa para recarregar BudgetSection quando despesas/faturas mudam
  $: budgetRefreshKey = (currentRecord?.expenses?.length || 0) +
    (currentRecord?.expenses?.reduce((s: number, e: any) => s + (e.valor || 0), 0) || 0) +
    cardFaturas.reduce((s, f) => s + (f.expenses?.length || 0) + (f.total || 0), 0)

  // Força reatividade do SummaryCards quando currentRecord muda
  $: summaryKey = currentRecord?.id + (currentRecord?.discounts?.length || 0) + (currentRecord?.expenses?.length || 0)

  onMount(() => {
    loadUser()
    fetchAccounts()
    loadCurrentMonth()
    authStore.subscribe(state => {
      if (state.user) {
        userName = state.user.nome && state.user.nome.trim() ? state.user.nome : (state.user.email?.split('@')[0] || 'Usuário')
      }
    })
  })

  // Atualiza currentRecord quando o store muda (ex: apos adicionar/remover item)
  const unsubscribeRecords = recordsStore.subscribe(state => {
    if (state.records && state.records.length > 0) {
      currentRecord = state.records[0]
    }
  })

  const loadCurrentMonth = async () => {
    loading = true
    errorMsg = ''
    currentRecord = null
    try {
      await fetchRecords(selectedMonth, selectedYear.toString())
      let state: any
      const unsub = recordsStore.subscribe(s => { state = s })
      unsub()
      if (state.records && state.records.length > 0) {
        currentRecord = state.records[0]
      } else {
        currentRecord = await createRecord(selectedMonth, selectedYear)
      }
    } catch (e: any) {
      errorMsg = e.message || 'Erro ao carregar dados'
    } finally {
      loading = false
    }
  }

  const handleMonthChange = (event: CustomEvent) => {
    selectedMonth = event.detail.month
    selectedYear = event.detail.year
    loadCurrentMonth()
  }

  const handleSalaryChange = async (newValue: number) => {
    if (currentRecord) {
      await updateRecord(currentRecord.id, { salario_bruto: newValue })
      currentRecord.salario_bruto = newValue
    }
  }

  const handleBalanceChange = async (newValue: number) => {
    if (currentRecord) {
      await updateRecord(currentRecord.id, { saldo_anterior: newValue })
      currentRecord.saldo_anterior = newValue
    }
  }

  const handleLogout = () => {
    logout()
  }

  const copyRecurring = async () => {
    if (!currentRecord) return
    if (!confirm('Copiar descontos e despesas recorrentes do mês anterior?')) return
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/records/${currentRecord.id}/copy-recurring`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      if (response.ok) {
        const msg = `${result.copiadas || 0} despesa(s) e ${result.descontos_copiados || 0} desconto(s) copiados!`
        alert(msg)
        await loadCurrentMonth()
      } else {
        alert(result.error || 'Erro ao copiar recorrentes')
      }
    } catch (e: any) {
      alert('Erro: ' + (e.message || 'Falha ao copiar'))
    }
  }
</script>

<div class="dashboard">
  <header class="dashboard-header">
    <div class="header-left">
      <img src="/assets/logo.png" alt="CashFlow" class="header-logo" />
      <div>
        <h1>CashFlow</h1>
        <p class="greeting">Olá, {userName}</p>
      </div>
    </div>
    <div class="header-actions">
      <button on:click={toggleTheme} class="btn-theme" title="Alternar tema">
        {$theme === 'dark' ? '☀️' : '🌙'}
      </button>
      <button on:click={handleLogout} class="btn-logout">Sair</button>
    </div>
  </header>

  <div class="container">
    <MonthSelector on:change={handleMonthChange} onCopyRecurring={copyRecurring} />

    {#if loading}
      <p style="text-align:center;padding:2rem;color:#666">Carregando...</p>
    {:else if errorMsg}
      <p style="text-align:center;padding:2rem;color:red">{errorMsg}</p>
    {:else if currentRecord}
      <SummaryCards key={summaryKey} record={currentRecord} {cardFaturas} {investmentSummary} />

      <AccountsSection refreshKey={budgetRefreshKey} on:change={() => fetchAccounts()} />

      <QuickStats record={currentRecord} {cardFaturas} />

      <BudgetSection recordId={currentRecord.id} refreshKey={budgetRefreshKey} />

      <div class="tabs">
        <button
          class={`tab-btn ${!showHistory ? 'active' : ''}`}
          on:click={() => (showHistory = false)}
        >
          Detalhes
        </button>
        <button
          class={`tab-btn ${showHistory ? 'active' : ''}`}
          on:click={() => (showHistory = true)}
        >
          Histórico
        </button>
      </div>

      {#if !showHistory}
        <div class="details-section">
          <div class="input-group">
            <label>Saldo Anterior</label>
            <input
              type="number"
              value={currentRecord.saldo_anterior}
              on:change={(e) => handleBalanceChange(parseFloat(e.target.value))}
              step="0.01"
            />
          </div>

          <div class="input-group">
            <label>Salário Bruto</label>
            <input
              type="number"
              value={currentRecord.salario_bruto}
              on:change={(e) => handleSalaryChange(parseFloat(e.target.value))}
              step="0.01"
            />
          </div>

          <DataTable title="Descontos e Creditos" items={currentRecord?.discounts || []} recordId={currentRecord.id} type="discounts" month={selectedMonth} year={selectedYear} />
          <ExpenseTable items={currentRecord?.expenses || []} recordId={currentRecord.id} month={selectedMonth} year={selectedYear} {cardFaturas} refreshKey={budgetRefreshKey} />
          <CardSection recordId={currentRecord.id} month={selectedMonth} year={selectedYear} refreshKey={budgetRefreshKey}
            on:faturasLoaded={(e) => cardFaturas = e.detail} />
          <InvestmentSection recordId={currentRecord.id} on:summary={(e) => investmentSummary = e.detail} />
        </div>
      {:else}
        <HistoryChart month={selectedMonth} year={selectedYear} />
      {/if}
    {/if}
    {#if !loading && !currentRecord && !errorMsg}
      <p style="text-align:center;padding:2rem;color:#666">Nenhum registro encontrado para este mes.</p>
    {/if}
  </div>
</div>

<style>
  .dashboard {
    min-height: 100vh;
    background-color: #f5f5f5;
  }

  .dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .dashboard-header h1 {
    margin: 0;
    font-size: clamp(1rem, 4vw, 1.8rem);
  }

  .btn-logout {
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid white;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .btn-logout:hover {
    background-color: rgba(255, 255, 255, 0.3);
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .btn-theme {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid white;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.05rem;
    color: white;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.3s, transform 0.3s;
  }
  .btn-theme:hover { background-color: rgba(255, 255, 255, 0.3); transform: rotate(20deg); }

  .header-left {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.75rem;
  }

  .header-logo {
    width: 60px;
    height: 60px;
    object-fit: contain;
  }

  .greeting {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0.9;
    font-weight: 400;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem;
  }

  .tabs {
    display: flex;
    gap: 1rem;
    margin: 2rem 0 1rem;
    border-bottom: 2px solid #ddd;
  }

  .tab-btn {
    background: none;
    border: none;
    padding: 1rem;
    cursor: pointer;
    font-size: 1rem;
    color: #666;
    border-bottom: 3px solid transparent;
    transition: all 0.3s;
  }

  .tab-btn.active {
    color: #667eea;
    border-bottom-color: #667eea;
  }

  .details-section {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow-x: hidden;
  }

  @media (max-width: 640px) {
    .container { padding: 0.5rem; }
    .details-section { padding: 0.5rem; overflow-x: hidden; }
    .tabs { gap: 0.5rem; margin: 1rem 0 0.5rem; }
    .tab-btn { padding: 0.6rem; font-size: 0.9rem; }
    .input-group input { padding: 0.5rem; font-size: 0.9rem; }
  }

  .input-group {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .input-group label {
    font-weight: 600;
    color: #333;
  }

  .input-group input {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
  }

  .input-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
</style>
