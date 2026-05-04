<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte'

  export let recordId: number
  export let month: string = ''
  export let year: number = 0
  export let categorias: string[] = ['Moradia','Alimentacao','Transporte','Saude','Educacao','Lazer','Cartao','Outros']

  const dispatch = createEventDispatcher()

  const API = '/api/cards'
  const token = () => localStorage.getItem('token')
  const auth = (extra: Record<string, string> = {}) => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token()}`,
    ...extra
  })
  const fmt = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

  // ── state ────────────────────────────────────────────────────────────────
  let cards: any[] = []
  let faturas: any[] = []
  let expandedCard: number | null = null
  let showCardManager = false

  let newCardName = ''
  let savingCard = false

  // add expense form
  let adding = false
  let addCardId: number | null = null
  let addDesc = ''
  let addValor = ''
  let addData = ''
  let addParcelas = '1'
  let addCategoria = 'Outros'
  let saving = false

  // edit
  let editingExpId: number | null = null
  let editDesc = ''
  let editValor = ''
  let editData = ''
  let editCategoria = 'Outros'

  // ── load ─────────────────────────────────────────────────────────────────
  const loadCards = async () => {
    const r = await fetch(API, { headers: auth() })
    cards = await r.json()
    if (cards.length && addCardId === null) addCardId = cards[0].id
  }

  const loadFaturas = async () => {
    if (!recordId) return
    const r = await fetch(`${API}/faturas/${recordId}`, { headers: auth() })
    faturas = await r.json()
    dispatch('faturasLoaded', faturas)
  }

  onMount(async () => {
    await loadCards()
    await loadFaturas()
  })

  $: if (recordId) loadFaturas()

  // ── cards CRUD ───────────────────────────────────────────────────────────
  const createCard = async () => {
    if (!newCardName.trim()) return
    savingCard = true
    try {
      const r = await fetch(API, {
        method: 'POST', headers: auth(),
        body: JSON.stringify({ nome: newCardName.trim() })
      })
      const c = await r.json()
      cards = [...cards, c]
      newCardName = ''
      if (!addCardId) addCardId = c.id
    } finally { savingCard = false }
  }

  const deleteCard = async (id: number) => {
    if (!confirm('Excluir este cartão e todas as despesas associadas?')) return
    await fetch(`${API}/${id}`, { method: 'DELETE', headers: auth() })
    cards = cards.filter(c => c.id !== id)
    faturas = faturas.filter(f => f.card_id !== id)
    if (addCardId === id) addCardId = cards[0]?.id ?? null
  }

  // ── expense CRUD ─────────────────────────────────────────────────────────
  const handleAdd = async () => {
    if (!addDesc.trim() || !addValor || !addCardId) return
    saving = true
    try {
      await fetch(`${API}/expenses`, {
        method: 'POST', headers: auth(),
        body: JSON.stringify({
          card_id: addCardId,
          record_id: recordId,
          descricao: addDesc,
          valor: parseFloat(addValor),
          categoria: addCategoria,
          data: addData,
          parcelas: parseInt(addParcelas) || 1
        })
      })
      addDesc = ''; addValor = ''; addData = ''; addParcelas = '1'; addCategoria = 'Outros'
      adding = false
      await loadFaturas()
    } finally { saving = false }
  }

  const startEdit = (exp: any) => {
    editingExpId = exp.id
    editDesc = exp.descricao
    editValor = String(exp.valor)
    editData = exp.data || ''
    editCategoria = exp.categoria || 'Outros'
  }

  const saveEdit = async () => {
    await fetch(`${API}/expenses/${editingExpId}`, {
      method: 'PUT', headers: auth(),
      body: JSON.stringify({ descricao: editDesc, valor: parseFloat(editValor), categoria: editCategoria, data: editData })
    })
    editingExpId = null
    await loadFaturas()
  }

  const deleteExpense = async (id: number) => {
    if (!confirm('Excluir esta despesa do cartão?')) return
    await fetch(`${API}/expenses/${id}`, { method: 'DELETE', headers: auth() })
    await loadFaturas()
  }

  const toggle = (cardId: number) => {
    expandedCard = expandedCard === cardId ? null : cardId
  }
</script>

<div class="card-section">
  <div class="section-header">
    <h3>💳 Cartões de Crédito</h3>
    <div class="header-btns">
      <button class="btn-sm btn-gray" on:click={() => showCardManager = !showCardManager}>
        ⚙ Gerenciar Cartões
      </button>
      {#if cards.length > 0}
        <button class="btn-sm btn-purple" on:click={() => { adding = !adding; editingExpId = null }}>
          {adding ? 'Cancelar' : '+ Lançar despesa'}
        </button>
      {/if}
    </div>
  </div>

  {#if showCardManager}
    <div class="card-manager">
      <strong>Meus Cartões</strong>
      <div class="chip-list">
        {#each cards as c}
          <span class="chip">{c.nome}
            <button on:click={() => deleteCard(c.id)}>✕</button>
          </span>
        {/each}
        {#if cards.length === 0}
          <span class="empty-chips">Nenhum cartão cadastrado.</span>
        {/if}
      </div>
      <div class="new-card-row">
        <input type="text" placeholder="Nome do cartão (ex: Nubank)" bind:value={newCardName}
          class="inp-card" on:keydown={(e) => e.key === 'Enter' && createCard()} />
        <button class="btn-sm btn-green" on:click={createCard} disabled={savingCard}>
          {savingCard ? '...' : 'Adicionar'}
        </button>
      </div>
    </div>
  {/if}

  {#if adding && cards.length > 0}
    <div class="add-form">
      <select bind:value={addCardId} class="inp">
        {#each cards as c}<option value={c.id}>{c.nome}</option>{/each}
      </select>
      <input type="text" placeholder="Descrição *" bind:value={addDesc} class="inp flex2" />
      <select bind:value={addCategoria} class="inp">
        {#each categorias as cat}<option>{cat}</option>{/each}
      </select>
      <input type="number" placeholder="Valor total *" bind:value={addValor} step="0.01" class="inp" />
      <input type="date" bind:value={addData} class="inp" />
      <div class="parcelas-wrap">
        <label class="inp-label">Parcelas</label>
        <input type="number" min="1" max="60" bind:value={addParcelas} class="inp inp-narrow" />
      </div>
      <button class="btn-save" on:click={handleAdd} disabled={saving}>
        {saving ? 'Salvando...' : 'Salvar'}
      </button>
    </div>
    {#if parseInt(addParcelas) > 1}
      <p class="parcelas-hint">
        💡 {parseInt(addParcelas)}× de {fmt(parseFloat(addValor || '0') / parseInt(addParcelas))} —
        lançamentos criados nos próximos meses automaticamente.
      </p>
    {/if}
  {/if}

  {#if faturas.length === 0 && cards.length === 0}
    <p class="empty-msg">Nenhum cartão cadastrado. Clique em "⚙ Gerenciar Cartões" para começar.</p>
  {:else if faturas.length === 0}
    <p class="empty-msg">Sem faturas neste mês.</p>
  {:else}
    <div class="faturas-list">
      {#each faturas as fatura}
        <div class="fatura-card">
          <button class="fatura-header" on:click={() => toggle(fatura.card_id)}>
            <span class="card-icon">💳</span>
            <span class="card-nome">{fatura.card_nome}</span>
            <span class="card-count">{fatura.expenses.length} lançamento(s)</span>
            <span class="card-total negative">{fmt(fatura.total)}</span>
            <span class="chevron">{expandedCard === fatura.card_id ? '▲' : '▼'}</span>
          </button>

          {#if expandedCard === fatura.card_id}
            <div class="fatura-body">
              <table>
                <thead>
                  <tr>
                    <th>Descrição</th>
                    <th>Categoria</th>
                    <th>Data</th>
                    <th>Parcela</th>
                    <th>Valor</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {#each fatura.expenses as exp}
                    {#if editingExpId === exp.id}
                      <tr class="edit-row">
                        <td><input type="text" bind:value={editDesc} class="edit-inp" /></td>
                        <td><select bind:value={editCategoria} class="edit-inp">{#each categorias as cat}<option>{cat}</option>{/each}</select></td>
                        <td><input type="date" bind:value={editData} class="edit-inp" /></td>
                        <td class="parcela-cell">
                          {exp.parcela_atual}/{exp.parcelas_total}
                        </td>
                        <td><input type="number" bind:value={editValor} step="0.01" class="edit-inp narrow" /></td>
                        <td class="action-cell">
                          <button class="btn-ok" on:click={saveEdit}>✓</button>
                          <button class="btn-cancel" on:click={() => editingExpId = null}>✕</button>
                        </td>
                      </tr>
                    {:else}
                      <tr>
                        <td class="desc">{exp.descricao}</td>
                        <td><span class="cat-badge">{exp.categoria || 'Outros'}</span></td>
                        <td>{exp.data || '—'}</td>
                        <td class="parcela-cell">
                          {#if exp.parcelas_total > 1}
                            <span class="parc-badge">{exp.parcela_atual}/{exp.parcelas_total}</span>
                          {:else}
                            <span class="parc-badge single">1×</span>
                          {/if}
                        </td>
                        <td class="negative">{fmt(exp.valor)}</td>
                        <td class="action-cell">
                          <button class="btn-edit" on:click={() => startEdit(exp)}>✎</button>
                          <button class="btn-del" on:click={() => deleteExpense(exp.id)}>✕</button>
                        </td>
                      </tr>
                    {/if}
                  {/each}
                </tbody>
              </table>
            </div>
          {/if}
        </div>
      {/each}

      <div class="total-row">
        <span>Total Cartões</span>
        <span class="negative">{fmt(faturas.reduce((s, f) => s + f.total, 0))}</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .card-section {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,.1);
    margin-bottom: 1.5rem;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  h3 { margin: 0; color: #333; font-size: 1.1rem; }

  .header-btns { display: flex; gap: 0.4rem; flex-wrap: wrap; }

  .btn-sm { border: none; padding: 0.4rem 0.75rem; border-radius: 5px; cursor: pointer; font-size: 0.8rem; color: white; white-space: nowrap; }
  .btn-gray { background: #607d8b; }
  .btn-purple { background: #667eea; }
  .btn-green { background: #4caf50; }

  .card-manager {
    background: #f9f9ff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
  }
  .card-manager strong { font-size: 0.875rem; color: #333; }
  .chip-list { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.5rem 0; }
  .chip { background: #e8eeff; color: #667eea; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; display: flex; align-items: center; gap: 4px; }
  .chip button { background: none; border: none; cursor: pointer; color: #667eea; font-size: 0.7rem; padding: 0; line-height: 1; }
  .empty-chips { font-size: 0.8rem; color: #aaa; font-style: italic; }
  .new-card-row { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
  .inp-card { flex: 1; padding: 0.35rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; }

  .add-form { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; background: #f9f9ff; border-radius: 8px; padding: 0.75rem; align-items: flex-end; }
  .inp { padding: 0.4rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.875rem; color: #333; background: #fff; box-sizing: border-box; color-scheme: light; min-width: 100px; }
  .inp.flex2 { flex: 2 1 180px; }
  .inp-label { font-size: 0.75rem; color: #666; display: block; margin-bottom: 2px; }
  .inp-narrow { width: 70px; }
  .parcelas-wrap { display: flex; flex-direction: column; }
  .parcelas-hint { font-size: 0.8rem; color: #667eea; margin-bottom: 0.5rem; padding: 0 0.25rem; }
  .btn-save { background: #4caf50; color: white; border: none; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer; white-space: nowrap; }
  .btn-save:disabled { opacity: 0.6; }

  .empty-msg { text-align: center; color: #999; font-style: italic; padding: 1rem; }

  .faturas-list { display: flex; flex-direction: column; gap: 0.5rem; }

  .fatura-card { border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }

  .fatura-header {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #f7f7ff;
    border: none;
    cursor: pointer;
    text-align: left;
    font-size: 0.9rem;
  }
  .fatura-header:hover { background: #eeeeff; }
  .card-icon { font-size: 1.1rem; }
  .card-nome { font-weight: 600; color: #333; flex: 1; }
  .card-count { font-size: 0.75rem; color: #888; }
  .card-total { font-weight: 700; font-size: 1rem; }
  .chevron { color: #667eea; font-size: 0.7rem; margin-left: auto; }

  .fatura-body { padding: 0 0.5rem 0.5rem; }

  table { width: 100%; border-collapse: collapse; }
  th { padding: 0.4rem 0.5rem; font-size: 0.78rem; color: #777; font-weight: 600; border-bottom: 1px solid #eee; text-align: left; white-space: nowrap; }
  td { padding: 0.45rem 0.5rem; font-size: 0.85rem; color: #333; border-bottom: 1px solid #f5f5f5; white-space: nowrap; vertical-align: middle; }
  .desc { white-space: normal; font-weight: 500; }

  .parcela-cell { text-align: center; }
  .parc-badge { background: #e8eeff; color: #667eea; border-radius: 10px; padding: 2px 6px; font-size: 0.75rem; }
  .parc-badge.single { background: #f0f0f0; color: #888; }
  .cat-badge { background: #eef; color: #667eea; padding: 2px 7px; border-radius: 10px; font-size: 0.75rem; }

  .action-cell { display: flex; gap: 4px; align-items: center; }
  .btn-edit { background: #2196f3; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; display: inline-flex; align-items: center; justify-content: center; }
  .btn-del  { background: #f44336; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;  display: inline-flex; align-items: center; justify-content: center; }
  .btn-ok   { background: #4caf50; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
  .btn-cancel { background: #9e9e9e; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }

  .edit-row td { background: #f0f4ff; }
  .edit-inp { width: 100%; padding: 0.3rem; border: 1px solid #667eea; border-radius: 4px; font-size: 0.82rem; color: #333; background: #fff; color-scheme: light; box-sizing: border-box; }
  .edit-inp.narrow { max-width: 90px; }

  .total-row {
    display: flex;
    justify-content: space-between;
    padding: 0.6rem 1rem;
    background: #f9f9f9;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    color: #333;
    margin-top: 0.25rem;
  }

  .negative { color: #f44336; font-weight: 600; }

  @media (max-width: 640px) {
    .card-section { padding: 1rem; }
    .fatura-header { padding: 0.6rem; gap: 0.5rem; font-size: 0.85rem; }
    .card-count { display: none; }
  }
</style>
