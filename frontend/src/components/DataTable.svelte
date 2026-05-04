<script lang="ts">
  import { addDiscount, addExpense, addInvestment, fetchRecords } from '../stores/records'

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

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
  }

  const handleAdd = async () => {
    if (!newDesc.trim() || !newValor) return
    saving = true
    try {
      const valor = parseFloat(newValor)
      if (type === 'discounts') await addDiscount(recordId, newDesc, valor)
      else if (type === 'expenses') await addExpense(recordId, newDesc, valor)
      else if (type === 'investments') await addInvestment(recordId, newDesc, valor)
      await fetchRecords(month, year.toString())
      newDesc = ''
      newValor = ''
      adding = false
    } finally {
      saving = false
    }
  }

  const handleDelete = async (item: any) => {
    const endpoint = type === 'discounts' ? 'discounts' : type === 'expenses' ? 'expenses' : 'investments'
    const token = localStorage.getItem('token')
    await fetch(`/api/records/${endpoint}/${item.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
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
        placeholder="Valor (ex: -150.00)"
        bind:value={newValor}
        step="0.01"
        class="input-valor"
      />
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
        <th></th>
      </tr>
    </thead>
    <tbody>
      {#if items && items.length > 0}
        {#each items as item (item.id)}
          <tr>
            <td>{item.descricao || item.card_name || '-'}</td>
            <td class={item.valor < 0 ? 'negative' : 'positive'}>
              {formatCurrency(item.valor)}
            </td>
            <td>
              <button class="btn-del" on:click={() => handleDelete(item)}>x</button>
            </td>
          </tr>
        {/each}
        <tr class="total-row">
          <td><strong>Total</strong></td>
          <td class={getTotal() < 0 ? 'negative' : 'positive'}><strong>{formatCurrency(getTotal())}</strong></td>
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
    width: 24px;
    height: 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.75rem;
    line-height: 1;
  }

  table { width: 100%; border-collapse: collapse; }
  thead { background-color: #f5f5f5; }
  th { padding: 0.75rem; text-align: left; font-weight: 600; color: #666; border-bottom: 2px solid #ddd; }
  td { padding: 0.75rem; border-bottom: 1px solid #eee; }
  tr:last-child td { border-bottom: none; }

  .total-row { background: #f9f9f9; }
  .empty { text-align: center; color: #999; font-style: italic; }
  .positive { color: #4caf50; font-weight: 600; }
  .negative { color: #f44336; font-weight: 600; }
</style>
