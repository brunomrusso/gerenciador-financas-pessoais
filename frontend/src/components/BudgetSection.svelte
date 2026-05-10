<script lang="ts">
  import { onMount } from 'svelte'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let recordId: number
  export let refreshKey: number = 0

  type BudgetItem = {
    categoria: string
    orcamento: number
    gasto: number
    restante: number
    percentual: number
    excedeu: boolean
  }

  let items: BudgetItem[] = []
  let loading = false
  let editing: string | null = null
  let editValor = ''
  let expanded = false

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)
  const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })

  const load = async () => {
    if (!recordId) return
    loading = true
    try {
      const r = await fetch(`/api/records/${recordId}/budget-status`, { headers: auth() })
      if (r.ok) items = await r.json()
    } finally {
      loading = false
    }
  }

  const startEdit = (it: BudgetItem) => {
    editing = it.categoria
    editValor = it.orcamento ? String(it.orcamento) : ''
  }

  const saveEdit = async (nome: string) => {
    const raw = String(editValor ?? '').replace(',', '.')
    const orcamento = parseFloat(raw) || 0
    const r = await fetch('/api/records/categories/budget', {
      method: 'PUT', headers: auth(),
      body: JSON.stringify({ nome, orcamento })
    })
    if (!r.ok) {
      const err = await r.text()
      console.error('Erro ao salvar orçamento:', r.status, err)
      alert('Erro ao salvar orçamento')
      return
    }
    editing = null
    await load()
  }

  $: if (recordId || refreshKey) load()

  $: itemsComOrcamento = items.filter(i => i.orcamento > 0)
  $: itemsSemOrcamento = items.filter(i => i.orcamento === 0)
  $: alerts = itemsComOrcamento.filter(i => i.excedeu)
  $: warnings = itemsComOrcamento.filter(i => !i.excedeu && i.percentual >= 80)
  $: totalOrcamento = itemsComOrcamento.reduce((s, i) => s + i.orcamento, 0)
  $: totalGasto = itemsComOrcamento.reduce((s, i) => s + i.gasto, 0)

  let showAddOther = false

  const barColor = (pct: number, excedeu: boolean) => {
    if (excedeu) return '#f44336'
    if (pct >= 80) return '#ff9800'
    if (pct >= 50) return '#ffc107'
    return '#4caf50'
  }
</script>

<div class="budget-section">
  <div class="budget-header" on:click={() => expanded = !expanded} on:keydown={(e) => e.key === 'Enter' && (expanded = !expanded)} role="button" tabindex="0">
    <div class="budget-title">
      <span class="icon">🎯</span>
      <h3>Orçamento por Categoria</h3>
      {#if alerts.length > 0}
        <span class="badge-alert">{alerts.length} estouro{alerts.length > 1 ? 's' : ''}</span>
      {:else if warnings.length > 0}
        <span class="badge-warn">{warnings.length} próximo{warnings.length > 1 ? 's' : ''} do limite</span>
      {/if}
    </div>
    <div class="budget-summary">
      {#if totalOrcamento > 0}
        <span class="summary-text">{fmt(totalGasto)} / {fmt(totalOrcamento)}</span>
      {/if}
      <span class="chevron">{expanded ? '▴' : '▾'}</span>
    </div>
  </div>

  {#if expanded}
    <div class="budget-body">
      {#if loading}
        <p class="empty">Carregando...</p>
      {:else if itemsComOrcamento.length === 0 && itemsSemOrcamento.length === 0}
        <p class="empty">Sem categorias. Adicione despesas ou defina um orçamento.</p>
      {:else if itemsComOrcamento.length === 0}
        <p class="empty">Nenhum orçamento definido ainda. Use o atalho abaixo para começar.</p>
      {:else}
        {#each itemsComOrcamento as it (it.categoria)}
          <div class="bud-row" class:over={it.excedeu}>
            <div class="bud-info">
              <div class="bud-cat-line">
                <span class="bud-cat">{it.categoria}</span>
                {#if editing === it.categoria}
                  <div class="edit-wrap">
                    <input
                      type="number"
                      step="0.01"
                      bind:value={editValor}
                      placeholder="0,00"
                      class="bud-inp"
                      on:keydown={(e) => e.key === 'Enter' && saveEdit(it.categoria)}
                    />
                    <button class="btn-save-bud" on:click={() => saveEdit(it.categoria)}>✓</button>
                    <button class="btn-cancel-bud" on:click={() => editing = null}>✕</button>
                  </div>
                {:else}
                  <button class="bud-edit-btn" on:click={() => startEdit(it)}>
                    {it.orcamento > 0 ? `${fmt(it.gasto)} / ${fmt(it.orcamento)}` : 'Definir orçamento ✎'}
                  </button>
                {/if}
              </div>
              {#if it.orcamento > 0 && editing !== it.categoria}
                <div class="bud-progress-wrap">
                  <div
                    class="bud-progress"
                    style:width={`${Math.min(it.percentual, 100)}%`}
                    style:background={barColor(it.percentual, it.excedeu)}
                  ></div>
                </div>
                <div class="bud-meta">
                  <span class="bud-pct">{it.percentual.toFixed(1)}%</span>
                  {#if it.excedeu}
                    <span class="bud-rest over-text">⚠ Excedeu {fmt(-it.restante)}</span>
                  {:else}
                    <span class="bud-rest">Resta {fmt(it.restante)}</span>
                  {/if}
                </div>
              {:else if editing !== it.categoria}
                <div class="bud-meta">
                  <span class="bud-only-spent">Gasto: {fmt(it.gasto)}</span>
                </div>
              {/if}
            </div>
          </div>
        {/each}
      {/if}

      {#if itemsSemOrcamento.length > 0}
        <div class="add-other">
          {#if !showAddOther}
            <button class="btn-add-other" on:click={() => showAddOther = true}>
              + Definir orçamento para outra categoria ({itemsSemOrcamento.length})
            </button>
          {:else}
            <div class="add-other-list">
              <div class="add-other-header">
                <span class="add-other-title">Categorias sem orçamento</span>
                <button class="btn-close-other" on:click={() => { showAddOther = false; editing = null }}>✕</button>
              </div>
              {#each itemsSemOrcamento as it (it.categoria)}
                <div class="other-row">
                  {#if editing === it.categoria}
                    <span class="other-name">{it.categoria}</span>
                    <div class="edit-wrap">
                      <input
                        type="number"
                        step="0.01"
                        bind:value={editValor}
                        placeholder="0,00"
                        class="bud-inp"
                        on:keydown={(e) => e.key === 'Enter' && saveEdit(it.categoria)}
                      />
                      <button class="btn-save-bud" on:click={() => saveEdit(it.categoria)}>✓</button>
                      <button class="btn-cancel-bud" on:click={() => editing = null}>✕</button>
                    </div>
                  {:else}
                    <div class="other-info">
                      <span class="other-name">{it.categoria}</span>
                      <span class="other-spent">Gasto: {fmt(it.gasto)}</span>
                    </div>
                    <button class="btn-set-budget" on:click={() => startEdit(it)}>+ Definir</button>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .budget-section {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,.1);
    margin-bottom: 1.5rem;
    overflow: hidden;
  }

  .budget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    cursor: pointer;
    user-select: none;
  }
  .budget-header:hover { background: #f9f9ff; }

  .budget-title { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
  .icon { font-size: 1.25rem; }
  h3 { margin: 0; color: #333; font-size: 1.05rem; font-weight: 600; }

  .badge-alert { background: #ffebee; color: #c62828; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
  .badge-warn  { background: #fff3e0; color: #ef6c00; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }

  .budget-summary { display: flex; align-items: center; gap: 0.75rem; }
  .summary-text { font-size: 0.85rem; color: #666; font-weight: 500; }
  .chevron { color: #667eea; font-size: 0.85rem; }

  .budget-body {
    padding: 0.75rem 1.25rem 1.25rem;
    border-top: 1px solid #f0f0f0;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .empty { color: #999; font-style: italic; text-align: center; padding: 1rem; margin: 0; font-size: 0.875rem; }

  .bud-row {
    padding: 0.5rem 0.6rem;
    background: #fafafa;
    border-radius: 6px;
    border-left: 3px solid #667eea;
  }
  .bud-row.over { border-left-color: #f44336; background: #fff5f5; }

  .bud-cat-line { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem; flex-wrap: wrap; }
  .bud-cat { font-weight: 600; color: #333; font-size: 0.92rem; }
  .bud-edit-btn {
    background: none; border: 1px dashed #ccc; color: #666; cursor: pointer;
    font-size: 0.8rem; padding: 3px 8px; border-radius: 5px;
  }
  .bud-edit-btn:hover { background: #eef; color: #667eea; border-color: #667eea; }

  .edit-wrap { display: flex; gap: 0.3rem; align-items: center; }
  .bud-inp { width: 110px; padding: 0.3rem 0.5rem; border: 1px solid #667eea; border-radius: 5px; font-size: 0.85rem; color: #333; background: #fff; }
  .btn-save-bud { background: #4caf50; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; }
  .btn-cancel-bud { background: #9e9e9e; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; }

  .bud-progress-wrap {
    width: 100%;
    height: 8px;
    background: #ececec;
    border-radius: 4px;
    overflow: hidden;
  }
  .bud-progress {
    height: 100%;
    transition: width .25s ease, background .25s ease;
    border-radius: 4px;
  }

  .bud-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; font-size: 0.75rem; color: #666; }
  .bud-pct { font-weight: 600; color: #444; }
  .bud-rest { color: #4caf50; font-weight: 500; }
  .over-text { color: #c62828; font-weight: 600; }
  .bud-only-spent { color: #888; font-style: italic; }

  .add-other { margin-top: 0.25rem; }
  .btn-add-other {
    width: 100%;
    background: none;
    border: 1px dashed #c0c0d0;
    color: #667eea;
    padding: 0.55rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.82rem;
    font-weight: 500;
  }
  .btn-add-other:hover { background: #f0f4ff; border-color: #667eea; }

  .add-other-list { background: #f8f9ff; border-radius: 6px; padding: 0.5rem 0.6rem; }
  .add-other-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; }
  .add-other-title { font-size: 0.78rem; color: #777; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; }
  .btn-close-other { background: none; border: none; color: #999; cursor: pointer; font-size: 0.95rem; padding: 2px 6px; }

  .other-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.5rem;
    border-bottom: 1px solid #ececec;
    flex-wrap: wrap;
  }
  .other-row:last-child { border-bottom: none; }
  .other-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
  .other-name { font-weight: 600; color: #333; font-size: 0.85rem; }
  .other-spent { font-size: 0.72rem; color: #888; }

  .btn-set-budget {
    background: #667eea;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.78rem;
    font-weight: 500;
  }
  .btn-set-budget:hover { background: #5568d8; }

  @media (max-width: 640px) {
    .budget-header { padding: 0.75rem; }
    h3 { font-size: 0.95rem; }
    .summary-text { font-size: 0.78rem; }
    .budget-body { padding: 0.5rem 0.75rem 1rem; }
    .bud-cat { font-size: 0.85rem; }
  }
</style>
