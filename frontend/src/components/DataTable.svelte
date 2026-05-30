<script lang="ts">
  import { addDiscount, addExpense, addInvestment, fetchRecords } from '../stores/records'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let title: string
  export let items: any[] = []
  export let recordId: number
  export let type: 'discounts' | 'expenses' | 'investments'
  export let month: string = ''
  export let year: number = 0

  let newDesc = ''
  let newValor = ''
  let adding = false
  let saving = false

  let editingId: number | null = null
  let editDesc = ''
  let editValor = ''
  let editRecorrente = false
  let newRecorrente = false

  $: fmt = (value: number) => fmtMasked(value, $valuesHidden)

  const auth = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  })

  const endpoint = () => type === 'discounts' ? 'discounts' : type === 'investments' ? 'investments' : 'expenses'

  const handleAdd = async () => {
    if (!newDesc.trim() || !newValor) return
    saving = true
    try {
      const valor = parseFloat(newValor)
      if (type === 'discounts') {
        await fetch(`/api/records/${recordId}/discounts`, {
          method: 'POST',
          headers: auth(),
          body: JSON.stringify({ descricao: newDesc, valor, recorrente: newRecorrente })
        })
      } else if (type === 'expenses') await addExpense(recordId, newDesc, valor)
      else if (type === 'investments') await addInvestment(recordId, newDesc, valor)
      await fetchRecords(month, year.toString())
      newDesc = ''; newValor = ''; newRecorrente = false; adding = false
    } finally { saving = false }
  }

  const startEdit = (item: any) => {
    editingId = item.id
    editDesc = item.descricao || item.card_name || ''
    editValor = String(item.valor || '')
    editRecorrente = type === 'discounts' ? (item.recorrente || false) : false
  }

  const cancelEdit = () => { editingId = null }

  const saveEdit = async (item: any) => {
    const payload: any = { descricao: editDesc, valor: parseFloat(editValor) }
    if (type === 'discounts') payload.recorrente = editRecorrente
    await fetch(`/api/records/${endpoint()}/${item.id}`, {
      method: 'PUT', headers: auth(),
      body: JSON.stringify(payload)
    })
    editingId = null
    await fetchRecords(month, year.toString())
  }

  const handleDelete = async (item: any) => {
    if (!confirm(`Excluir "${item.descricao || item.card_name}"?`)) return
    await fetch(`/api/records/${endpoint()}/${item.id}`, {
      method: 'DELETE', headers: auth()
    })
    await fetchRecords(month, year.toString())
  }

  const getTotal = () => items?.reduce((sum, i) => sum + (i.valor || 0), 0) || 0
</script>

<div class="data-table">
  <div class="table-header">
    <h3>{title}</h3>
    <button class="btn-add" on:click={() => adding = !adding}>
      {adding ? 'Cancelar' : '+ Adicionar'}
    </button>
  </div>

  {#if adding}
    <div class="add-form">
      <input
        type="text"
        placeholder="Descricao"
        bind:value={newDesc}
        class="input-desc"
      />
      <input
        type="number"
        inputmode="decimal"
        placeholder="Valor (ex: -150.00)"
        bind:value={newValor}
        step="0.01"
        class="input-valor"
      />
      {#if type === 'discounts'}
        <label class="checkbox-label">
          <input type="checkbox" bind:checked={newRecorrente} />
          Recorrente
        </label>
      {/if}
      <button class="btn-save" on:click={handleAdd} disabled={saving}>
        {saving ? 'Salvando...' : 'Salvar'}
      </button>
    </div>
    <p class="hint">
      {#if type === 'discounts'}Use valor negativo para descontos (ex: -500.00), positivo para creditos.
      {:else if type === 'expenses'}Use valor negativo para despesas (ex: -150.00).
      {:else}Use valor positivo para investimentos (ex: 300.00).{/if}
    </p>
  {/if}

  <table>
    <thead>
      <tr>
        <th>Descricao</th>
        <th>Valor</th>
        {#if type === 'discounts'}<th style="width: 80px; text-align: center;">Recorrente</th>{/if}
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#if items && items.length > 0}
        {#each items as item (item.id)}
          {#if editingId === item.id}
            <tr class="edit-row">
              <td data-label="Descrição"><input type="text" bind:value={editDesc} class="edit-inp" /></td>
              <td data-label="Valor"><input type="number" inputmode="decimal" bind:value={editValor} step="0.01" class="edit-inp" /></td>
              {#if type === 'discounts'}
                <td data-label="Recorrente" style="text-align: center;">
                  <input type="checkbox" bind:checked={editRecorrente} />
                </td>
              {/if}
              <td class="action-td">
                <button class="btn-ok" on:click={() => saveEdit(item)}>✓</button>
                <button class="btn-cancel" on:click={cancelEdit}>✕</button>
              </td>
            </tr>
          {:else}
            <tr>
              <td data-label="Descrição">{item.descricao || item.card_name || '-'}</td>
              <td data-label="Valor" class={item.valor < 0 ? 'negative' : 'positive'}>{fmt(item.valor)}</td>
              {#if type === 'discounts'}
                <td data-label="Recorrente" style="text-align: center;">
                  {#if item.recorrente}
                    <span class="badge-recorrente">🔄</span>
                  {/if}
                </td>
              {/if}
              <td class="action-td">
                <button class="btn-edit" on:click={() => startEdit(item)} title="Editar">✎</button>
                <button class="btn-del" on:click={() => handleDelete(item)} title="Excluir">✕</button>
              </td>
            </tr>
          {/if}
        {/each}
        <tr class="total-row">
          <td data-label=""><strong>Total</strong></td>
          <td data-label="" class={getTotal() < 0 ? 'negative' : 'positive'}><strong>{fmt(getTotal())}</strong></td>
          {#if type === 'discounts'}<td></td>{/if}
          <td></td>
        </tr>
      {:else}
        <tr>
          <td colspan="3" class="empty">Nenhum lancamento. Clique em "+ Adicionar" para comecar.</td>
        </tr>
      {/if}
    </tbody>
  </table>
</div>

<style>
  .data-table {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
  }

  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  h3 { margin: 0; color: #333; font-size: 1.1rem; }

  .add-form {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
  }

  .input-desc { flex: 2; padding: 0.5rem; border: 1px solid #ddd; border-radius: 5px; min-width: 150px; }
  .input-valor { flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 5px; min-width: 120px; }

  .hint { font-size: 0.75rem; color: #888; margin: 0 0 1rem; }

  .btn-add {
    background: #667eea;
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.875rem;
  }

  .btn-save {
    background: #4caf50;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
  }

  .btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

  .btn-del {
    background: #f44336;
    color: white;
    border: none;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }

  .btn-edit {
    background: #2196f3;
    color: white;
    border: none;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .btn-ok {
    background: #4caf50;
    color: white;
    border: none;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .btn-cancel {
    background: #9e9e9e;
    color: white;
    border: none;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .action-td { display: flex; gap: 4px; align-items: center; justify-content: flex-start; padding: 0.5rem 0.75rem; }

  .edit-row td { background: #f0f4ff; }
  .edit-inp { width: 100%; padding: 0.3rem 0.5rem; border: 1px solid #667eea; border-radius: 4px; font-size: 0.875rem; color: #333; background: white; box-sizing: border-box; }

  table { width: 100%; border-collapse: collapse; }
  thead { background-color: #f5f5f5; }
  th { padding: 0.75rem; text-align: left; font-weight: 600; color: #666; border-bottom: 2px solid #ddd; font-size: 0.85rem; }
  td { padding: 0.65rem 0.75rem; border-bottom: 1px solid #eee; color: #222; font-size: 0.875rem; vertical-align: middle; }
  tr:last-child td { border-bottom: none; }

  .total-row { background: #f9f9f9; }
  .empty { text-align: center; color: #999; font-style: italic; }
  .positive { color: #4caf50; font-weight: 600; }
  .negative { color: #f44336; font-weight: 600; }
  .badge-recorrente { font-size: 1.1rem; }
  .checkbox-label { display: flex; align-items: center; gap: 0.5rem; white-space: nowrap; font-size: 0.875rem; }
  .checkbox-label input { cursor: pointer; }

  @media (max-width: 768px) {
    .data-table { padding: 0.85rem; margin-bottom: 1rem; }
    .input-desc, .input-valor { min-width: 100%; }
    .add-form { flex-direction: column; gap: 0.5rem; }
    .btn-save { width: 100%; padding: 0.7rem; font-size: 0.95rem; }

    /* Tabela vira cards no mobile */
    table, thead, tbody, tr, td { display: block; }
    thead { display: none; }
    tr {
      background: #fafbfc;
      border: 1px solid #eef0f5;
      border-radius: 8px;
      padding: 0.6rem 0.75rem;
      margin-bottom: 0.5rem;
    }
    tr.edit-row { background: #f0f4ff; border-color: #c5cae9; }
    tr.total-row { background: #f0f4ff; border-color: #667eea; }
    td {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.35rem 0;
      border: none !important;
      font-size: 0.92rem;
    }
    td::before {
      content: attr(data-label);
      font-weight: 600;
      color: #888;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }
    td.action-td {
      justify-content: flex-end;
      gap: 0.5rem;
      padding-top: 0.5rem;
      margin-top: 0.4rem;
      border-top: 1px solid #eef0f5 !important;
    }
    td.action-td::before { display: none; }
    .btn-edit, .btn-del, .btn-ok, .btn-cancel {
      width: 40px;
      height: 40px;
      font-size: 1rem;
    }
    .edit-inp { max-width: 60%; }
  }
</style>
