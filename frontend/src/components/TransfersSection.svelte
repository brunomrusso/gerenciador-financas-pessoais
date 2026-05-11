<script lang="ts">
  import { fetchRecords } from '../stores/records'
  import { accountsStore, fetchAccounts } from '../stores/accounts'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let recordId: number
  export let transfers: any[] = []
  export let month: string = ''
  export let year: number = 0

  let adding = false
  let editingId: number | null = null
  let descricao = ''
  let valor = ''
  let fromId = ''
  let toId = ''
  let data = ''
  let recorrente = false

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)

  const auth = () => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
  })

  const reset = () => {
    adding = false
    editingId = null
    descricao = ''
    valor = ''
    fromId = ''
    toId = ''
    data = ''
    recorrente = false
  }

  const startAdd = () => {
    reset()
    adding = true
    data = new Date().toISOString().slice(0, 10)
  }

  const startEdit = (t: any) => {
    reset()
    editingId = t.id
    descricao = t.descricao || ''
    valor = String(t.valor || '')
    fromId = String(t.from_account_id || '')
    toId = String(t.to_account_id || '')
    data = t.data || ''
    recorrente = !!t.recorrente
  }

  const refresh = async () => {
    await fetchRecords(month, year.toString())
    await fetchAccounts()
  }

  const handleSave = async () => {
    const v = parseFloat(valor)
    if (!v || isNaN(v) || !fromId || !toId) return
    if (fromId === toId) { alert('Conta de origem e destino devem ser diferentes'); return }
    const body = {
      descricao,
      valor: v,
      from_account_id: parseInt(fromId),
      to_account_id: parseInt(toId),
      data: data || null,
      recorrente
    }
    if (editingId) {
      await fetch(`/api/records/transfers/${editingId}`, {
        method: 'PUT', headers: auth(), body: JSON.stringify(body)
      })
    } else {
      await fetch(`/api/records/${recordId}/transfers`, {
        method: 'POST', headers: auth(), body: JSON.stringify(body)
      })
    }
    reset()
    await refresh()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Excluir esta transferência?')) return
    await fetch(`/api/records/transfers/${id}`, { method: 'DELETE', headers: auth() })
    await refresh()
  }

  const accountName = (id: number | null) => {
    if (!id) return '?'
    const acc = $accountsStore.find(a => a.id === id)
    return acc ? `${acc.icone} ${acc.nome}` : '?'
  }

  $: total = (transfers || []).reduce((s: number, x: any) => s + (x.valor || 0), 0)
  $: activeAccounts = $accountsStore.filter(a => a.ativa)
</script>

<div class="transfers-section">
  <div class="t-header">
    <h3>🔁 Transferências entre Contas</h3>
    {#if !adding && editingId === null}
      <button type="button" class="btn-add" on:click={startAdd}>+ Adicionar</button>
    {/if}
  </div>

  {#if transfers.length === 0 && !adding}
    <p class="empty">Nenhuma transferência neste mês.</p>
  {:else}
    <table class="t-table">
      <thead>
        <tr>
          <th>Descrição</th>
          <th>De → Para</th>
          <th class="right">Valor</th>
          <th>Data</th>
          <th class="center">Rec.</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each transfers as t (t.id)}
          {#if editingId === t.id}
            <tr class="edit-row">
              <td><input bind:value={descricao} placeholder="ex: Reserva..." class="inp" /></td>
              <td>
                <div class="from-to">
                  <select bind:value={fromId} class="inp">
                    <option value="">De...</option>
                    {#each activeAccounts as a}<option value={String(a.id)}>{a.icone} {a.nome}</option>{/each}
                  </select>
                  <span class="arrow">→</span>
                  <select bind:value={toId} class="inp">
                    <option value="">Para...</option>
                    {#each activeAccounts as a}<option value={String(a.id)}>{a.icone} {a.nome}</option>{/each}
                  </select>
                </div>
              </td>
              <td><input type="number" step="0.01" bind:value={valor} class="inp right" /></td>
              <td><input type="date" bind:value={data} class="inp" /></td>
              <td class="center"><input type="checkbox" bind:checked={recorrente} /></td>
              <td class="actions">
                <button class="btn-save" on:click={handleSave}>✓</button>
                <button class="btn-cancel" on:click={reset}>✕</button>
              </td>
            </tr>
          {:else}
            <tr>
              <td>{t.descricao || '—'}</td>
              <td class="from-to-display">
                <span class="acc-pill from">{accountName(t.from_account_id)}</span>
                <span class="arrow">→</span>
                <span class="acc-pill to">{accountName(t.to_account_id)}</span>
              </td>
              <td class="right value-cell">{fmt(t.valor)}</td>
              <td>{t.data || '—'}</td>
              <td class="center">{t.recorrente ? '✓' : ''}</td>
              <td class="actions">
                <button class="btn-edit" on:click={() => startEdit(t)} title="Editar">✏️</button>
                <button class="btn-del" on:click={() => handleDelete(t.id)} title="Excluir">🗑️</button>
              </td>
            </tr>
          {/if}
        {/each}
        {#if adding}
          <tr class="edit-row">
            <td><input bind:value={descricao} placeholder="ex: Reserva..." class="inp" /></td>
            <td>
              <div class="from-to">
                <select bind:value={fromId} class="inp">
                  <option value="">De...</option>
                  {#each activeAccounts as a}<option value={String(a.id)}>{a.icone} {a.nome}</option>{/each}
                </select>
                <span class="arrow">→</span>
                <select bind:value={toId} class="inp">
                  <option value="">Para...</option>
                  {#each activeAccounts as a}<option value={String(a.id)}>{a.icone} {a.nome}</option>{/each}
                </select>
              </div>
            </td>
            <td><input type="number" step="0.01" placeholder="0,00" bind:value={valor} class="inp right" /></td>
            <td><input type="date" bind:value={data} class="inp" /></td>
            <td class="center"><input type="checkbox" bind:checked={recorrente} /></td>
            <td class="actions">
              <button class="btn-save" on:click={handleSave}>✓</button>
              <button class="btn-cancel" on:click={reset}>✕</button>
            </td>
          </tr>
        {/if}
      </tbody>
      {#if transfers.length > 0}
        <tfoot>
          <tr>
            <td colspan="2"><strong>Total movimentado</strong></td>
            <td class="right"><strong>{fmt(total)}</strong></td>
            <td colspan="3" class="hint">(não afeta saldo total)</td>
          </tr>
        </tfoot>
      {/if}
    </table>
  {/if}
</div>

<style>
  .transfers-section { margin: 1rem 0; padding: 1rem; background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .t-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
  .t-header h3 { margin: 0; font-size: 1rem; color: #333; }
  .btn-add { background: #667eea; color: #fff; border: none; padding: 0.4rem 0.8rem; border-radius: 5px; cursor: pointer; font-size: 0.85rem; }
  .btn-add:hover { background: #5568d3; }
  .empty { color: #888; font-size: 0.85rem; margin: 0; }
  .t-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .t-table th, .t-table td { padding: 0.5rem; border-bottom: 1px solid #eee; text-align: left; vertical-align: middle; }
  .t-table th { font-weight: 600; color: #666; font-size: 0.75rem; text-transform: uppercase; }
  .t-table .right { text-align: right; }
  .t-table .center { text-align: center; }
  .value-cell { color: #667eea; font-weight: 600; }
  .from-to, .from-to-display { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
  .arrow { color: #888; font-weight: bold; }
  .acc-pill { padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.82rem; }
  .acc-pill.from { background: #ffe4e4; color: #c62828; }
  .acc-pill.to { background: #d4edda; color: #155724; }
  .inp { padding: 0.35rem 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; box-sizing: border-box; min-width: 100px; }
  .inp.right { text-align: right; min-width: 90px; }
  .edit-row { background: #f7f9ff; }
  .actions { white-space: nowrap; text-align: right; }
  .actions button { background: none; border: none; cursor: pointer; padding: 0.25rem 0.4rem; font-size: 0.95rem; border-radius: 3px; }
  .actions button:hover { background: #f0f0f0; }
  .btn-save { color: #4caf50; }
  .btn-cancel { color: #f44336; }
  tfoot { background: #f9f9f9; }
  tfoot td { padding: 0.6rem 0.5rem; }
  .hint { color: #888; font-size: 0.75rem; font-style: italic; }

  :global([data-theme="dark"]) .transfers-section { background: #1e1e1e; }
  :global([data-theme="dark"]) .t-header h3 { color: #eee; }
  :global([data-theme="dark"]) .t-table th { color: #aaa; }
  :global([data-theme="dark"]) .t-table th, :global([data-theme="dark"]) .t-table td { border-color: #333; }
  :global([data-theme="dark"]) .inp { background: #2a2a2a; color: #ddd; border-color: #444; }
  :global([data-theme="dark"]) .edit-row { background: #1a2238; }
  :global([data-theme="dark"]) tfoot { background: #2a2a2a; }
  :global([data-theme="dark"]) .acc-pill.from { background: #4a1f1f; color: #ff9b9b; }
  :global([data-theme="dark"]) .acc-pill.to { background: #1f4a26; color: #8eee9d; }
  :global([data-theme="dark"]) .actions button:hover { background: #2a2a2a; }
</style>
