<script lang="ts">
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let recordId: number
  export let refreshKey: number = 0

  type TagBudgetItem = {
    tag: string
    orcamento: number
    gasto: number
    restante: number
    percentual: number
    excedeu: boolean
  }

  let items: TagBudgetItem[] = []
  let loading = false
  let editing: string | null = null
  let editValor = ''
  let expanded = false
  let showAddOther = false
  let newTagName = ''

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)
  const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })

  const load = async () => {
    if (!recordId) return
    loading = true
    try {
      const r = await fetch(`/api/records/${recordId}/tag-budget-status`, { headers: auth() })
      if (r.ok) items = await r.json()
    } finally {
      loading = false
    }
  }

  const startEdit = (it: TagBudgetItem) => {
    editing = it.tag
    editValor = it.orcamento ? String(it.orcamento) : ''
  }

  const saveEdit = async (tag: string) => {
    const raw = String(editValor ?? '').replace(',', '.')
    const orcamento = parseFloat(raw) || 0
    const r = await fetch('/api/records/tag-budgets', {
      method: 'PUT', headers: auth(),
      body: JSON.stringify({ tag, orcamento })
    })
    if (!r.ok) {
      alert('Erro ao salvar orçamento de tag')
      return
    }
    editing = null
    await load()
  }

  const removeBudget = async (tag: string) => {
    if (!confirm(`Remover orçamento da tag "${tag}"?`)) return
    await fetch(`/api/records/tag-budgets/${encodeURIComponent(tag)}`, {
      method: 'DELETE', headers: auth()
    })
    await load()
  }

  const addNewTag = async () => {
    const tag = newTagName.trim().toLowerCase()
    if (!tag) return
    editing = tag
    editValor = ''
    newTagName = ''
    // Garante que aparece como item editável mesmo se ainda não tem gasto
    if (!items.find(i => i.tag === tag)) {
      items = [...items, { tag, orcamento: 0, gasto: 0, restante: 0, percentual: 0, excedeu: false }]
    }
  }

  $: if (recordId || refreshKey) load()

  $: itemsComOrcamento = items.filter(i => i.orcamento > 0)
  $: itemsSemOrcamento = items.filter(i => i.orcamento === 0)
  $: alerts = itemsComOrcamento.filter(i => i.excedeu)
  $: warnings = itemsComOrcamento.filter(i => !i.excedeu && i.percentual >= 80)
  $: totalOrcamento = itemsComOrcamento.reduce((s, i) => s + i.orcamento, 0)
  $: totalGasto = itemsComOrcamento.reduce((s, i) => s + i.gasto, 0)

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
      <span class="icon">🏷️</span>
      <h3>Orçamento por Tag</h3>
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
      {:else if items.length === 0}
        <p class="empty">Sem tags. Adicione tags nas despesas ou defina abaixo.</p>
      {:else if itemsComOrcamento.length === 0}
        <p class="empty">Nenhum orçamento por tag definido. Use o atalho abaixo.</p>
      {:else}
        {#each itemsComOrcamento as it (it.tag)}
          <div class="bud-row" class:over={it.excedeu}>
            <div class="bud-info">
              <div class="bud-cat-line">
                <span class="bud-cat">#{it.tag}</span>
                {#if editing === it.tag}
                  <div class="edit-wrap">
                    <input
                      type="number" inputmode="decimal" step="0.01" bind:value={editValor}
                      placeholder="0,00" class="bud-inp"
                      on:keydown={(e) => e.key === 'Enter' && saveEdit(it.tag)}
                    />
                    <button class="btn-save-bud" on:click={() => saveEdit(it.tag)}>✓</button>
                    <button class="btn-cancel-bud" on:click={() => editing = null}>✕</button>
                  </div>
                {:else}
                  <div class="actions-row">
                    <button class="bud-edit-btn" on:click={() => startEdit(it)}>
                      {fmt(it.gasto)} / {fmt(it.orcamento)} ✎
                    </button>
                    <button class="btn-remove" on:click={() => removeBudget(it.tag)} title="Remover orçamento">🗑️</button>
                  </div>
                {/if}
              </div>
              {#if editing !== it.tag}
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
              {/if}
            </div>
          </div>
        {/each}
      {/if}

      <div class="add-other">
        {#if !showAddOther}
          <button class="btn-add-other" on:click={() => showAddOther = true}>
            + Definir orçamento para tag {itemsSemOrcamento.length > 0 ? `(${itemsSemOrcamento.length} sem orçamento)` : ''}
          </button>
        {:else}
          <div class="add-other-list">
            <div class="add-other-header">
              <span class="add-other-title">Definir orçamento de tag</span>
              <button class="btn-close-other" on:click={() => { showAddOther = false; editing = null; newTagName = '' }}>✕</button>
            </div>

            <div class="new-tag-row">
              <input
                type="text" placeholder="nova tag (ex: lazer)"
                bind:value={newTagName} class="new-tag-inp"
                on:keydown={(e) => e.key === 'Enter' && addNewTag()}
              />
              <button class="btn-set-budget" on:click={addNewTag} disabled={!newTagName.trim()}>+ Adicionar</button>
            </div>

            {#each itemsSemOrcamento as it (it.tag)}
              <div class="other-row">
                {#if editing === it.tag}
                  <span class="other-name">#{it.tag}</span>
                  <div class="edit-wrap">
                    <input
                      type="number" inputmode="decimal" step="0.01" bind:value={editValor}
                      placeholder="0,00" class="bud-inp"
                      on:keydown={(e) => e.key === 'Enter' && saveEdit(it.tag)}
                    />
                    <button class="btn-save-bud" on:click={() => saveEdit(it.tag)}>✓</button>
                    <button class="btn-cancel-bud" on:click={() => editing = null}>✕</button>
                  </div>
                {:else}
                  <div class="other-info">
                    <span class="other-name">#{it.tag}</span>
                    <span class="other-spent">Gasto: {fmt(it.gasto)}</span>
                  </div>
                  <button class="btn-set-budget" on:click={() => startEdit(it)}>+ Definir</button>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .budget-section { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); margin-bottom: 1.5rem; overflow: hidden; }
  .budget-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; cursor: pointer; user-select: none; }
  .budget-header:hover { background: #f9f9ff; }
  .budget-title { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
  .icon { font-size: 1.25rem; }
  h3 { margin: 0; color: #333; font-size: 1.05rem; font-weight: 600; }
  .badge-alert { background: #ffebee; color: #c62828; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
  .badge-warn  { background: #fff3e0; color: #ef6c00; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
  .budget-summary { display: flex; align-items: center; gap: 0.75rem; }
  .summary-text { font-size: 0.85rem; color: #666; font-weight: 500; }
  .chevron { color: #667eea; font-size: 0.85rem; }
  .budget-body { padding: 0.75rem 1.25rem 1.25rem; border-top: 1px solid #f0f0f0; display: flex; flex-direction: column; gap: 0.6rem; }
  .empty { color: #999; font-style: italic; text-align: center; padding: 1rem; margin: 0; font-size: 0.875rem; }
  .bud-row { padding: 0.5rem 0.6rem; background: #fafafa; border-radius: 6px; border-left: 3px solid #9c27b0; }
  .bud-row.over { border-left-color: #f44336; background: #fff5f5; }
  .bud-cat-line { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem; flex-wrap: wrap; }
  .bud-cat { font-weight: 600; color: #9c27b0; font-size: 0.92rem; }
  .actions-row { display: flex; gap: 0.3rem; align-items: center; }
  .bud-edit-btn { background: none; border: 1px dashed #ccc; color: #666; cursor: pointer; font-size: 0.8rem; padding: 3px 8px; border-radius: 5px; }
  .bud-edit-btn:hover { background: #f9efff; color: #9c27b0; border-color: #9c27b0; }
  .btn-remove { background: none; border: none; cursor: pointer; padding: 3px 6px; font-size: 0.85rem; border-radius: 4px; }
  .btn-remove:hover { background: #ffebee; }
  .edit-wrap { display: flex; gap: 0.3rem; align-items: center; }
  .bud-inp { width: 110px; padding: 0.3rem 0.5rem; border: 1px solid #9c27b0; border-radius: 5px; font-size: 0.85rem; color: #333; background: #fff; }
  .btn-save-bud { background: #4caf50; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; }
  .btn-cancel-bud { background: #9e9e9e; color: white; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; }
  .bud-progress-wrap { width: 100%; height: 8px; background: #ececec; border-radius: 4px; overflow: hidden; }
  .bud-progress { height: 100%; transition: width .25s ease, background .25s ease; border-radius: 4px; }
  .bud-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; font-size: 0.75rem; color: #666; }
  .bud-pct { font-weight: 600; color: #444; }
  .bud-rest { color: #4caf50; font-weight: 500; }
  .over-text { color: #c62828; font-weight: 600; }
  .add-other { margin-top: 0.25rem; }
  .btn-add-other { width: 100%; background: none; border: 1px dashed #c0c0d0; color: #9c27b0; padding: 0.55rem; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 500; }
  .btn-add-other:hover { background: #f9efff; border-color: #9c27b0; }
  .add-other-list { background: #fbf6ff; border-radius: 6px; padding: 0.5rem 0.6rem; }
  .add-other-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; }
  .add-other-title { font-size: 0.78rem; color: #777; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; }
  .btn-close-other { background: none; border: none; color: #999; cursor: pointer; font-size: 0.95rem; padding: 2px 6px; }
  .new-tag-row { display: flex; gap: 0.4rem; margin-bottom: 0.5rem; }
  .new-tag-inp { flex: 1; padding: 0.4rem 0.5rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; }
  .other-row { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; padding: 0.4rem 0.5rem; border-bottom: 1px solid #ececec; flex-wrap: wrap; }
  .other-row:last-child { border-bottom: none; }
  .other-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
  .other-name { font-weight: 600; color: #9c27b0; font-size: 0.85rem; }
  .other-spent { font-size: 0.72rem; color: #888; }
  .btn-set-budget { background: #9c27b0; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.78rem; font-weight: 500; }
  .btn-set-budget:hover { background: #7e22ce; }
  .btn-set-budget:disabled { background: #ccc; cursor: not-allowed; }

  :global([data-theme="dark"]) .budget-section { background: #1e1e1e; }
  :global([data-theme="dark"]) .budget-header:hover { background: #2a2a2a; }
  :global([data-theme="dark"]) h3 { color: #eee; }
  :global([data-theme="dark"]) .budget-body { border-color: #333; }
  :global([data-theme="dark"]) .bud-row { background: #2a2a2a; }
  :global([data-theme="dark"]) .bud-row.over { background: #3a1f1f; }
  :global([data-theme="dark"]) .add-other-list { background: #2a1f33; }
  :global([data-theme="dark"]) .new-tag-inp { background: #2a2a2a; color: #ddd; border-color: #444; }
  :global([data-theme="dark"]) .bud-inp { background: #2a2a2a; color: #ddd; }
  :global([data-theme="dark"]) .bud-progress-wrap { background: #333; }
</style>
