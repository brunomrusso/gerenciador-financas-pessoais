<script lang="ts">
  import { fetchRecords } from '../stores/records'
  import { accountsStore, fetchAccounts } from '../stores/accounts'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let recordId: number
  export let salaries: any[] = []
  export let month: string = ''
  export let year: number = 0

  let adding = false
  let editingId: number | null = null
  let descricao = ''
  let valor = ''
  let accountId = ''
  let recorrente = false

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)

  const auth = () => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
  })

  const reset = () => {
    descricao = ''
    valor = ''
    accountId = ''
    recorrente = false
    adding = false
    editingId = null
  }

  const refresh = async () => {
    await fetchRecords(month, year.toString())
    await fetchAccounts()
  }

  const startAdd = () => {
    reset()
    adding = true
  }

  const startEdit = (s: any) => {
    editingId = s.id
    descricao = s.descricao || 'Salário'
    valor = String(s.valor || '')
    accountId = s.account_id ? String(s.account_id) : ''
    recorrente = !!s.recorrente
  }

  const handleSave = async () => {
    const v = parseFloat(valor)
    if (!v || isNaN(v)) return
    const body = {
      descricao: descricao || 'Salário',
      valor: v,
      account_id: accountId ? parseInt(accountId) : null,
      recorrente
    }
    if (editingId) {
      await fetch(`/api/records/salaries/${editingId}`, {
        method: 'PUT', headers: auth(), body: JSON.stringify(body)
      })
    } else {
      await fetch(`/api/records/${recordId}/salaries`, {
        method: 'POST', headers: auth(), body: JSON.stringify(body)
      })
    }
    reset()
    await refresh()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Excluir este salário?')) return
    await fetch(`/api/records/salaries/${id}`, { method: 'DELETE', headers: auth() })
    await refresh()
  }

  const accountName = (id: number | null) => {
    if (!id) return '— padrão —'
    const acc = $accountsStore.find((a: any) => a.id === id)
    return acc ? `${acc.icone} ${acc.nome}` : '?'
  }

  $: total = (salaries || []).reduce((s: number, x: any) => s + (x.valor || 0), 0)
</script>

<div class="salaries-section">
  <div class="sal-header">
    <h3>Salários adicionais</h3>
    {#if !adding && editingId === null}
      <button type="button" class="btn-add" on:click={startAdd}>+ Adicionar</button>
    {/if}
  </div>

  {#if salaries.length === 0 && !adding}
    <p class="empty">Nenhum salário adicional.</p>
  {:else}
    <table class="sal-table">
      <thead>
        <tr>
          <th>Descrição</th>
          <th>Conta</th>
          <th class="right">Valor</th>
          <th>Rec.</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each salaries as s (s.id)}
          {#if editingId === s.id}
            <tr class="edit-row">
              <td><input bind:value={descricao} class="inp" /></td>
              <td>
                <select bind:value={accountId} class="inp">
                  <option value="">— padrão —</option>
                  {#each $accountsStore.filter(a => a.ativa) as acc}
                    <option value={String(acc.id)}>{acc.icone} {acc.nome}</option>
                  {/each}
                </select>
              </td>
              <td><input type="number" step="0.01" bind:value={valor} class="inp right" /></td>
              <td><input type="checkbox" bind:checked={recorrente} /></td>
              <td class="actions">
                <button class="btn-save" on:click={handleSave}>✓</button>
                <button class="btn-cancel" on:click={reset}>✕</button>
              </td>
            </tr>
          {:else}
            <tr>
              <td>{s.descricao}</td>
              <td class="acc-cell">{accountName(s.account_id)}</td>
              <td class="right positive">{fmt(s.valor)}</td>
              <td>{s.recorrente ? '✓' : ''}</td>
              <td class="actions">
                <button class="btn-edit" on:click={() => startEdit(s)} title="Editar">✏️</button>
                <button class="btn-del" on:click={() => handleDelete(s.id)} title="Excluir">🗑️</button>
              </td>
            </tr>
          {/if}
        {/each}
        {#if adding}
          <tr class="edit-row">
            <td><input bind:value={descricao} placeholder="ex: Freela" class="inp" /></td>
            <td>
              <select bind:value={accountId} class="inp">
                <option value="">— padrão —</option>
                {#each $accountsStore.filter(a => a.ativa) as acc}
                  <option value={String(acc.id)}>{acc.icone} {acc.nome}</option>
                {/each}
              </select>
            </td>
            <td><input type="number" step="0.01" placeholder="0,00" bind:value={valor} class="inp right" /></td>
            <td><input type="checkbox" bind:checked={recorrente} /></td>
            <td class="actions">
              <button class="btn-save" on:click={handleSave}>✓</button>
              <button class="btn-cancel" on:click={reset}>✕</button>
            </td>
          </tr>
        {/if}
      </tbody>
      {#if salaries.length > 0}
        <tfoot>
          <tr>
            <td colspan="2"><strong>Total adicional</strong></td>
            <td class="right positive"><strong>{fmt(total)}</strong></td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      {/if}
    </table>
  {/if}
</div>

<style>
  .salaries-section { margin: 1rem 0; padding: 1rem; background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .sal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
  .sal-header h3 { margin: 0; font-size: 1rem; color: #333; }
  .btn-add { background: #667eea; color: #fff; border: none; padding: 0.4rem 0.8rem; border-radius: 5px; cursor: pointer; font-size: 0.85rem; }
  .btn-add:hover { background: #5568d3; }
  .empty { color: #888; font-size: 0.85rem; margin: 0; }
  .sal-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .sal-table th, .sal-table td { padding: 0.5rem; border-bottom: 1px solid #eee; text-align: left; }
  .sal-table th { font-weight: 600; color: #666; font-size: 0.8rem; }
  .sal-table .right { text-align: right; }
  .sal-table .positive { color: #4caf50; font-weight: 500; }
  .acc-cell { font-size: 0.85rem; color: #555; }
  .inp { width: 100%; padding: 0.35rem 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; box-sizing: border-box; }
  .inp.right { text-align: right; }
  .edit-row { background: #f7f9ff; }
  .actions { white-space: nowrap; }
  .actions button { background: none; border: none; cursor: pointer; padding: 0.25rem 0.4rem; font-size: 0.95rem; border-radius: 3px; }
  .actions button:hover { background: #f0f0f0; }
  .btn-save { color: #4caf50; }
  .btn-cancel { color: #f44336; }
  tfoot { background: #f9f9f9; }
  tfoot td { padding: 0.6rem 0.5rem; }

  :global([data-theme="dark"]) .salaries-section { background: #1e1e1e; }
  :global([data-theme="dark"]) .sal-header h3 { color: #eee; }
  :global([data-theme="dark"]) .sal-table th { color: #aaa; }
  :global([data-theme="dark"]) .sal-table th, :global([data-theme="dark"]) .sal-table td { border-color: #333; }
  :global([data-theme="dark"]) .acc-cell { color: #bbb; }
  :global([data-theme="dark"]) .inp { background: #2a2a2a; color: #ddd; border-color: #444; }
  :global([data-theme="dark"]) .edit-row { background: #1a2238; }
  :global([data-theme="dark"]) tfoot { background: #2a2a2a; }
  :global([data-theme="dark"]) .actions button:hover { background: #2a2a2a; }
</style>
