<script lang="ts">
  import { onMount } from 'svelte'
  import { recordsStore, fetchRecords, createRecord, updateRecord, syncSaldoAnterior } from '../stores/records'
  import { authStore } from '../stores/auth'
  import { logout, loadUser } from '../stores/auth'
  import MonthSelector from '../components/MonthSelector.svelte'
  import SummaryCards from '../components/SummaryCards.svelte'
  import DataTable from '../components/DataTable.svelte'
  import ExpenseTable from '../components/ExpenseTable.svelte'
  import CardSection from '../components/CardSection.svelte'
  import BudgetSection from '../components/BudgetSection.svelte'
  import TagBudgetSection from '../components/TagBudgetSection.svelte'
  import InvestmentSection from '../components/InvestmentSection.svelte'
  import QuickStats from '../components/QuickStats.svelte'
  import HistoryChart from '../components/HistoryChart.svelte'
  import AccountsSection from '../components/AccountsSection.svelte'
  import SalariesSection from '../components/SalariesSection.svelte'
  import DiscountsGrouped from '../components/DiscountsGrouped.svelte'
  import TransfersSection from '../components/TransfersSection.svelte'
  import CollapsibleSection from '../components/CollapsibleSection.svelte'
  import ProfileModal from '../components/ProfileModal.svelte'
  import { theme, toggleTheme } from '../stores/theme'
  import { fetchAccounts, accountsStore } from '../stores/accounts'
  import { valuesHidden, toggleValuesHidden } from '../stores/privacy'
  import { collapsedSections, collapseAll, expandAll, SECTION_KEYS } from '../stores/ui'

  let profileOpen = false
  $: anyCollapsed = SECTION_KEYS.some(k => $collapsedSections[k])

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

  // Sincroniza currentRecord automaticamente com o store (reatividade garantida)
  $: if ($recordsStore.records && $recordsStore.records.length > 0) {
    currentRecord = $recordsStore.records[0]
  }

  // summaryKey muda sempre que qualquer valor relevante mudar
  $: summaryKey = JSON.stringify(currentRecord?.expenses?.map((e: any) => ({ id: e.id, valor: e.valor, eh_credito: e.eh_credito }))) +
    JSON.stringify(currentRecord?.discounts?.map((d: any) => ({ id: d.id, valor: d.valor }))) +
    JSON.stringify(currentRecord?.salaries?.map((s: any) => ({ id: s.id, valor: s.valor }))) +
    (currentRecord?.saldo_anterior || 0) +
    (currentRecord?.salario_bruto || 0)

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
      await fetchAccounts()
    }
  }

  const handleSalaryAccountChange = async (newAccountId: string) => {
    if (currentRecord) {
      const id = newAccountId ? parseInt(newAccountId) : null
      await updateRecord(currentRecord.id, { salario_account_id: id })
      currentRecord.salario_account_id = id
      await fetchAccounts()
    }
  }

  const handleBalanceChange = async (newValue: number) => {
    if (currentRecord) {
      await updateRecord(currentRecord.id, { saldo_anterior: newValue })
      currentRecord.saldo_anterior = newValue
    }
  }

  let saldoAnteriorLocked = true
  let syncingSaldo = false
  const handleSyncSaldoAnterior = async () => {
    if (!currentRecord) return
    syncingSaldo = true
    try {
      await syncSaldoAnterior(currentRecord.id, selectedMonth, selectedYear.toString())
    } catch (e: any) {
      alert(e.message || 'Erro ao sincronizar saldo')
    } finally {
      syncingSaldo = false
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
      <button on:click={() => anyCollapsed ? expandAll(SECTION_KEYS) : collapseAll(SECTION_KEYS)} class="btn-theme" title={anyCollapsed ? 'Expandir tudo' : 'Recolher tudo'}>
        {anyCollapsed ? '⏬' : '⏫'}
      </button>
      <button on:click={toggleValuesHidden} class="btn-theme" title={$valuesHidden ? 'Mostrar valores' : 'Ocultar valores'}>
        {$valuesHidden ? '🙈' : '👁️'}
      </button>
      <button on:click={toggleTheme} class="btn-theme" title="Alternar tema">
        {$theme === 'dark' ? '☀️' : '🌙'}
      </button>
      <button on:click={() => profileOpen = true} class="btn-avatar" title="Perfil">
        {($authStore.user?.nome || $authStore.user?.email || '?')[0].toUpperCase()}
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
      {#key summaryKey}
      <SummaryCards record={currentRecord} {cardFaturas} {investmentSummary} />
      {/key}

      <CollapsibleSection sectionKey="accounts" title="🏦 Contas" bare={true}>
        <AccountsSection refreshKey={budgetRefreshKey} on:change={() => fetchAccounts()} />
      </CollapsibleSection>

      <CollapsibleSection sectionKey="quickstats" title="⚡ Estatísticas rápidas" bare={true}>
        <QuickStats record={currentRecord} {cardFaturas} />
      </CollapsibleSection>

      <CollapsibleSection sectionKey="budget" title="🎯 Orçamento por categoria" bare={true}>
        <BudgetSection recordId={currentRecord.id} refreshKey={budgetRefreshKey} />
      </CollapsibleSection>
      <CollapsibleSection sectionKey="tagbudget" title="🏷 Orçamento por tag" bare={true}>
        <TagBudgetSection recordId={currentRecord.id} refreshKey={budgetRefreshKey} />
      </CollapsibleSection>

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
          📊 Painel
        </button>
      </div>

      {#if !showHistory}
        <div class="details-section">
          <div class="input-group">
            <label for="saldo-anterior-input">
              Saldo Anterior
              <span class="lock-icon" title="Travado: sincronizado com mês anterior. Clique no botão para sincronizar manualmente ou edite desbloqueando.">{saldoAnteriorLocked ? '🔒' : '🔓'}</span>
            </label>
            <div class="saldo-anterior-row">
              <input
                id="saldo-anterior-input"
                type="number"
                value={currentRecord.saldo_anterior}
                on:change={(e) => handleBalanceChange(parseFloat(e.currentTarget.value))}
                step="0.01"
                readonly={saldoAnteriorLocked}
                class={saldoAnteriorLocked ? 'locked' : ''}
              />
              <button type="button" class="btn-toggle-lock" on:click={() => saldoAnteriorLocked = !saldoAnteriorLocked} title={saldoAnteriorLocked ? 'Desbloquear edição manual' : 'Bloquear edição'}>
                {saldoAnteriorLocked ? '✏️' : '🔒'}
              </button>
              {#if currentRecord.saldo_anterior_calculado !== null && currentRecord.saldo_anterior_calculado !== undefined}
                <button type="button" class="btn-sync" on:click={handleSyncSaldoAnterior} title="Sincronizar com saldo final do mês anterior" disabled={syncingSaldo}>
                  {syncingSaldo ? '...' : '🔄 Sincronizar'}
                </button>
              {/if}
            </div>
            {#if currentRecord.saldo_anterior_calculado !== null && currentRecord.saldo_anterior_calculado !== undefined && Math.abs((currentRecord.saldo_anterior_calculado || 0) - (currentRecord.saldo_anterior || 0)) > 0.01}
              <div class="saldo-warning">
                ⚠️ Mês anterior fechou com <strong>R$ {(currentRecord.saldo_anterior_calculado || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</strong>
              </div>
            {:else if currentRecord.saldo_anterior_calculado === null}
              <div class="saldo-info">ℹ️ Não há registro do mês anterior</div>
            {/if}
          </div>

          <div class="input-group">
            <label for="salario-input">Salário Bruto</label>
            <div class="salary-row">
              <input
                id="salario-input"
                type="number"
                value={currentRecord.salario_bruto}
                on:change={(e) => handleSalaryChange(parseFloat(e.currentTarget.value))}
                step="0.01"
              />
              <select
                class="salary-account-select"
                value={currentRecord.salario_account_id || ''}
                on:change={(e) => handleSalaryAccountChange(e.currentTarget.value)}
                title="Conta onde o salário cai"
              >
                <option value="">— Conta padrão —</option>
                {#each $accountsStore.filter(a => a.ativa) as acc}
                  <option value={acc.id}>{acc.icone} {acc.nome}</option>
                {/each}
              </select>
            </div>
          </div>

          <CollapsibleSection sectionKey="salaries" title="💵 Salários adicionais" bare={true}>
            <SalariesSection
              recordId={currentRecord.id}
              salaries={currentRecord.salaries || []}
              month={selectedMonth}
              year={selectedYear}
            />
          </CollapsibleSection>

          <CollapsibleSection sectionKey="discounts" title="📉 Descontos e créditos" bare={true}>
            <DiscountsGrouped record={currentRecord} month={selectedMonth} year={selectedYear} />
          </CollapsibleSection>

          <CollapsibleSection sectionKey="transfers" title="🔁 Transferências" bare={true}>
            <TransfersSection
              recordId={currentRecord.id}
              transfers={currentRecord.transfers || []}
              month={selectedMonth}
              year={selectedYear}
            />
          </CollapsibleSection>

          <CollapsibleSection sectionKey="expenses" title="💸 Despesas" bare={true}>
            <ExpenseTable items={currentRecord?.expenses || []} recordId={currentRecord.id} month={selectedMonth} year={selectedYear} {cardFaturas} refreshKey={budgetRefreshKey} />
          </CollapsibleSection>

          <CollapsibleSection sectionKey="cards" title="💳 Cartões de crédito" bare={true}>
            <CardSection recordId={currentRecord.id} month={selectedMonth} year={selectedYear} refreshKey={budgetRefreshKey}
              on:faturasLoaded={(e) => cardFaturas = e.detail} />
          </CollapsibleSection>

          <CollapsibleSection sectionKey="investments" title="📈 Investimentos" bare={true}>
            <InvestmentSection recordId={currentRecord.id} on:summary={(e) => investmentSummary = e.detail} />
          </CollapsibleSection>
        </div>
      {:else}
        <HistoryChart month={selectedMonth} year={selectedYear} />
      {/if}
    {/if}
    {#if !loading && !currentRecord && !errorMsg}
      <p style="text-align:center;padding:2rem;color:#666">Nenhum registro encontrado para este mes.</p>
    {/if}
  </div>

  {#if profileOpen}
    <ProfileModal on:close={() => profileOpen = false} />
  {/if}
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

  .btn-avatar {
    background: rgba(255, 255, 255, 0.25);
    border: 2px solid white;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 0.95rem;
    color: white;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }
  .btn-avatar:hover { background: rgba(255,255,255,0.35); transform: scale(1.08); }

  .header-left {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.75rem;
  }

  .header-logo {
    width: 80px;
    height: 80px;
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

  .input-group input.locked {
    background: #f5f5f5;
    color: #666;
    cursor: not-allowed;
  }

  .lock-icon { font-size: 0.85rem; margin-left: 0.4rem; cursor: help; }

  .saldo-anterior-row, .salary-row {
    display: flex;
    gap: 0.5rem;
    align-items: stretch;
    flex-wrap: wrap;
  }

  .saldo-anterior-row input, .salary-row input {
    flex: 1;
    min-width: 150px;
  }

  .salary-account-select {
    padding: 0.5rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    background: #fff;
    font-size: 0.9rem;
    cursor: pointer;
    min-width: 180px;
  }
  .salary-account-select:focus {
    outline: none;
    border-color: #667eea;
  }

  :global([data-theme="dark"]) .salary-account-select {
    background: #1e1e1e;
    color: #ddd;
    border-color: #444;
  }

  .btn-toggle-lock, .btn-sync {
    padding: 0 0.75rem;
    border: 1px solid #ddd;
    background: #fff;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    white-space: nowrap;
    transition: all 0.15s;
  }
  .btn-toggle-lock:hover, .btn-sync:hover { background: #f0f4ff; border-color: #667eea; }
  .btn-sync { background: #f0f4ff; color: #667eea; font-weight: 500; }
  .btn-sync:hover { background: #667eea; color: #fff; }
  .btn-sync:disabled { opacity: 0.5; cursor: wait; }

  .saldo-warning {
    margin-top: 0.4rem;
    padding: 0.5rem 0.75rem;
    background: #fff8e1;
    border-left: 3px solid #ffa726;
    border-radius: 4px;
    font-size: 0.85rem;
    color: #6d4c00;
  }
  .saldo-info {
    margin-top: 0.4rem;
    padding: 0.5rem 0.75rem;
    background: #f5f5f5;
    border-radius: 4px;
    font-size: 0.85rem;
    color: #666;
  }

  :global([data-theme="dark"]) .input-group input.locked { background: #2a2a2a; color: #aaa; }
  :global([data-theme="dark"]) .btn-toggle-lock,
  :global([data-theme="dark"]) .btn-sync { background: #2a2a2a; border-color: #444; color: #ddd; }
  :global([data-theme="dark"]) .btn-sync { background: #1e2a4a; color: #99b3ff; }
  :global([data-theme="dark"]) .saldo-warning { background: #3a2e10; color: #ffd180; border-left-color: #ffa726; }
  :global([data-theme="dark"]) .saldo-info { background: #2a2a2a; color: #aaa; }
</style>
