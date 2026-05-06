<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte'
  import TagInput from './TagInput.svelte'

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
  let addTags: string[] = []
  let saving = false

  // edit
  let editingExpId: number | null = null
  let editDesc = ''
  let editValor = ''
  let editData = ''
  let editCategoria = 'Outros'
  let editParcelas = '1'
  let editTags: string[] = []

  // modal de propagação
  type ModalCtx = { type: 'edit' | 'delete', expId: number, groupId: string, totalParcelas: number, payload?: any }
  let modal: ModalCtx | null = null

  // modal de mover
  let moveModal: { expId: number, group_id: string, parcelas_total: number } | null = null
  let moveMonth = ''
  let moveYear = 0
  const months = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

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
          parcelas: parseInt(addParcelas) || 1,
          tags: addTags
        })
      })
      addDesc = ''; addValor = ''; addData = ''; addParcelas = '1'; addCategoria = 'Outros'; addTags = []
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
    editParcelas = String(exp.parcelas_total || 1)
    editTags = Array.isArray(exp.tags) ? [...exp.tags] : []
  }

  const saveEdit = async (exp: any) => {
    const payload = {
      descricao: editDesc,
      valor: parseFloat(editValor),
      categoria: editCategoria,
      data: editData,
      parcelas_total: parseInt(editParcelas),
      tags: editTags
    }
    if (exp.group_id) {
      modal = { type: 'edit', expId: exp.id, groupId: exp.group_id, totalParcelas: exp.parcelas_total, payload }
    } else {
      await fetch(`${API}/expenses/${exp.id}`, { method: 'PUT', headers: auth(), body: JSON.stringify(payload) })
      editingExpId = null
      await loadFaturas()
    }
  }

  const deleteExpense = async (exp: any) => {
    if (exp.group_id && exp.parcelas_total > 1) {
      modal = { type: 'delete', expId: exp.id, groupId: exp.group_id, totalParcelas: exp.parcelas_total }
    } else {
      if (!confirm('Excluir esta despesa do cartão?')) return
      await fetch(`${API}/expenses/${exp.id}`, { method: 'DELETE', headers: auth() })
      await loadFaturas()
    }
  }

  const confirmModal = async (applyAll: boolean) => {
    if (!modal) return
    if (modal.type === 'delete') {
      await fetch(`${API}/expenses/${modal.expId}?delete_all=${applyAll}`, { method: 'DELETE', headers: auth() })
    } else {
      await fetch(`${API}/expenses/${modal.expId}`, {
        method: 'PUT', headers: auth(),
        body: JSON.stringify({ ...modal.payload, apply_to_all: applyAll })
      })
      editingExpId = null
    }
    modal = null
    await loadFaturas()
  }

  const startMove = (exp: any) => {
    moveModal = { expId: exp.id, group_id: exp.group_id, parcelas_total: exp.parcelas_total }
    moveMonth = month
    moveYear = year
  }

  const confirmMove = async () => {
    if (!moveModal || !moveMonth || !moveYear) return
    await fetch(`${API}/expenses/${moveModal.expId}/move`, {
      method: 'POST', headers: auth(),
      body: JSON.stringify({ month: moveMonth, year: moveYear })
    })
    moveModal = null
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
      <TagInput bind:tags={addTags} placeholder="tags..." />
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

  {#if modal}
    <div class="modal-overlay">
      <div class="modal-box">
        <p class="modal-title">
          {modal.type === 'delete' ? 'Excluir lançamento' : 'Aplicar edição'}
        </p>
        <p class="modal-sub">
          Este lançamento possui <strong>{modal.totalParcelas} parcelas</strong> em meses seguintes.
          {modal.type === 'delete' ? 'Deseja excluir:' : 'Deseja aplicar a:'}
        </p>
        <div class="modal-btns">
          <button class="btn-modal-one" on:click={() => confirmModal(false)}>Só esta parcela</button>
          <button class="btn-modal-all" on:click={() => confirmModal(true)}>Todas as {modal.totalParcelas} parcelas</button>
          <button class="btn-modal-cancel" on:click={() => modal = null}>Cancelar</button>
        </div>
      </div>
    </div>
  {/if}

  {#if moveModal}
    <div class="modal-overlay">
      <div class="modal-box">
        <p class="modal-title">Mover para outro mês</p>
        <p class="modal-sub">
          {moveModal.parcelas_total > 1 ? 'Todas as parcelas serão movidas a partir do mês selecionado.' : 'Mover este lançamento para:'}
        </p>
        <div class="move-selects">
          <select bind:value={moveMonth} class="inp">
            {#each months as m}<option>{m}</option>{/each}
          </select>
          <select bind:value={moveYear} class="inp">
            <option value={2024}>2024</option>
            <option value={2025}>2025</option>
            <option value={2026}>2026</option>
            <option value={2027}>2027</option>
          </select>
        </div>
        <div class="modal-btns">
          <button class="btn-modal-all" on:click={confirmMove}>Mover</button>
          <button class="btn-modal-cancel" on:click={() => moveModal = null}>Cancelar</button>
        </div>
      </div>
    </div>
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
                          <span class="parc-cur">{exp.parcela_atual}/</span><input type="number" bind:value={editParcelas} min="1" max="60" class="edit-inp" style="width:44px" />
                        </td>
                        <td><input type="number" bind:value={editValor} step="0.01" class="edit-inp narrow" /></td>
                        <td class="action-cell">
                          <button class="btn-ok" on:click={() => saveEdit(exp)}>✓</button>
                          <button class="btn-cancel" on:click={() => editingExpId = null}>✕</button>
                        </td>
                      </tr>
                    {:else}
                      <tr>
                        <td class="desc">
                          {exp.descricao}
                          {#if Array.isArray(exp.tags) && exp.tags.length > 0}
                            <span class="row-tags">{#each exp.tags as t}<span class="tag-mini">#{t}</span>{/each}</span>
                          {/if}
                        </td>
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
                          <button class="btn-move" on:click={() => startMove(exp)} title="Mover para outro mês">➜</button>
                          <button class="btn-del" on:click={() => deleteExpense(exp)}>✕</button>
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

  .fatura-body { padding: 0 0.5rem 0.5rem; overflow-x: auto; -webkit-overflow-scrolling: touch; }

  table { width: 100%; border-collapse: collapse; }
  th { padding: 0.4rem 0.5rem; font-size: 0.78rem; color: #777; font-weight: 600; border-bottom: 1px solid #eee; text-align: left; white-space: nowrap; }
  td { padding: 0.25rem 0.4rem; font-size: 0.85rem; color: #333; border-bottom: 1px solid #f5f5f5; white-space: nowrap; vertical-align: middle; line-height: 1.2; }
  .desc { white-space: normal; font-weight: 500; }

  .parcela-cell { text-align: center; }
  .parc-badge { background: #e8eeff; color: #667eea; border-radius: 8px; padding: 1px 5px; font-size: 0.7rem; line-height: 1.3; }
  .parc-badge.single { background: #f0f0f0; color: #888; }
  .cat-badge { background: #eef; color: #667eea; padding: 1px 6px; border-radius: 8px; font-size: 0.7rem; line-height: 1.3; }
  .row-tags { display: inline-flex; gap: 4px; margin-left: 6px; flex-wrap: wrap; }
  .tag-mini { background: #e8eaff; color: #3949ab; border-radius: 8px; padding: 1px 6px; font-size: 0.7rem; }

  .action-cell { display: flex; gap: 4px; align-items: center; }
  .btn-edit { background: #2196f3; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; display: inline-flex; align-items: center; justify-content: center; }
  .btn-move { background: #ff9800; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; display: inline-flex; align-items: center; justify-content: center; }
  .btn-del  { background: #f44336; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; font-size: 0.7rem;  display: inline-flex; align-items: center; justify-content: center; }
  .btn-ok   { background: #4caf50; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
  .btn-cancel { background: #9e9e9e; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }

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

  .parc-cur { font-size: 0.78rem; color: #667eea; }

  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 1000; display: flex; align-items: center; justify-content: center; }
  .modal-box { background: white; border-radius: 12px; padding: 1.5rem; max-width: 360px; width: 90%; box-shadow: 0 8px 32px rgba(0,0,0,.2); }
  .modal-title { margin: 0 0 0.5rem; font-size: 1.05rem; font-weight: 700; color: #333; }
  .modal-sub { margin: 0 0 1.25rem; font-size: 0.875rem; color: #555; line-height: 1.5; }
  .modal-btns { display: flex; flex-direction: column; gap: 0.5rem; }
  .btn-modal-one { padding: 0.55rem 1rem; border: 2px solid #667eea; background: white; color: #667eea; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.875rem; }
  .btn-modal-one:hover { background: #f0f0ff; }
  .btn-modal-all { padding: 0.55rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.875rem; }
  .btn-modal-all:hover { background: #5568d8; }
  .btn-modal-cancel { padding: 0.45rem 1rem; background: none; color: #999; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }

  .move-selects { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
  .move-selects .inp { flex: 1; }

  .card-section { width: 100%; box-sizing: border-box; max-width: 100%; }

  @media (max-width: 640px) {
    .card-section { padding: 1rem; }
    .fatura-header { padding: 0.6rem; gap: 0.5rem; font-size: 0.85rem; }
    .card-count { display: none; }
    .fatura-body table { min-width: 480px; }
    .fatura-body th { padding: 0.35rem 0.3rem; font-size: 0.72rem; }
    .fatura-body td { padding: 0.25rem 0.3rem; font-size: 0.78rem; }
  }
</style>
