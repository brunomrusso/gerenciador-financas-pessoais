<script lang="ts">
  import { onMount, afterUpdate } from 'svelte'
  import { fetchRecords } from '../stores/records'
  import Chart from 'chart.js/auto'

  export let items: any[] = []
  export let recordId: number
  export let month: string = ''
  export let year: number = 0

  let newDesc = ''
  let newValor = ''
  let newCategoria = 'Outros'
  let newData = ''
  let newPago = false
  let adding = false
  let saving = false
  let chartCanvas: HTMLCanvasElement
  let chart: Chart | null = null

  const categorias = ['Moradia', 'Alimentacao', 'Transporte', 'Saude', 'Educacao', 'Lazer', 'Cartao', 'Outros']

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

  const getAuthHeader = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  })

  const handleAdd = async () => {
    if (!newDesc.trim() || !newValor) return
    saving = true
    try {
      await fetch(`/api/records/${recordId}/expenses`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({
          descricao: newDesc,
          valor: parseFloat(newValor),
          categoria: newCategoria,
          data: newData,
          pago: newPago
        })
      })
      await fetchRecords(month, year.toString())
      newDesc = ''; newValor = ''; newCategoria = 'Outros'; newData = ''; newPago = false
      adding = false
    } finally {
      saving = false
    }
  }

  const togglePago = async (item: any) => {
    await fetch(`/api/records/expenses/${item.id}`, {
      method: 'PUT',
      headers: getAuthHeader(),
      body: JSON.stringify({ pago: !item.pago })
    })
    await fetchRecords(month, year.toString())
  }

  const handleDelete = async (item: any) => {
    await fetch(`/api/records/expenses/${item.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    await fetchRecords(month, year.toString())
  }

  const getTotal = () => items?.reduce((s, i) => s + (i.valor || 0), 0) || 0

  const buildChart = () => {
    if (!chartCanvas || !items || items.length === 0) return
    const grouped: Record<string, number> = {}
    items.forEach(i => {
      const cat = i.categoria || 'Outros'
      grouped[cat] = (grouped[cat] || 0) + Math.abs(i.valor || 0)
    })
    const labels = Object.keys(grouped)
    const data = Object.values(grouped)
    const colors = ['#667eea','#764ba2','#f44336','#ff9800','#4caf50','#2196f3','#9c27b0','#607d8b']

    if (chart) chart.destroy()
    chart = new Chart(chartCanvas, {
      type: 'pie',
      data: {
        labels,
        datasets: [{ data, backgroundColor: colors.slice(0, labels.length), borderWidth: 2 }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'right' },
          title: { display: true, text: 'Despesas por Categoria' }
        }
      }
    })
  }

  $: if (items) setTimeout(buildChart, 100)
</script>

<div class="expense-wrap">
  <div class="table-section">
    <div class="table-header">
      <h3>Despesas</h3>
      <button class="btn-add" on:click={() => adding = !adding}>
        {adding ? 'Cancelar' : '+ Adicionar'}
      </button>
    </div>

    {#if adding}
      <div class="add-form">
        <input type="text" placeholder="Descricao" bind:value={newDesc} class="inp" />
        <input type="number" placeholder="Valor (ex: -150.00)" bind:value={newValor} step="0.01" class="inp-sm" />
        <select bind:value={newCategoria} class="inp-sm">
          {#each categorias as cat}<option>{cat}</option>{/each}
        </select>
        <input type="date" bind:value={newData} class="inp-sm" />
        <label class="chk-label">
          <input type="checkbox" bind:checked={newPago} /> Pago
        </label>
        <button class="btn-save" on:click={handleAdd} disabled={saving}>
          {saving ? '...' : 'Salvar'}
        </button>
      </div>
    {/if}

    <table>
      <thead>
        <tr>
          <th>Descricao</th>
          <th>Categoria</th>
          <th>Data</th>
          <th>Valor</th>
          <th>Pago</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#if items && items.length > 0}
          {#each items as item (item.id)}
            <tr class={item.pago ? 'pago-row' : ''}>
              <td>{item.descricao || '-'}</td>
              <td><span class="badge">{item.categoria || 'Outros'}</span></td>
              <td>{item.data || '-'}</td>
              <td class={item.valor < 0 ? 'negative' : 'positive'}>{formatCurrency(item.valor)}</td>
              <td>
                <input type="checkbox" checked={item.pago} on:change={() => togglePago(item)} />
              </td>
              <td><button class="btn-del" on:click={() => handleDelete(item)}>x</button></td>
            </tr>
          {/each}
          <tr class="total-row">
            <td colspan="3"><strong>Total</strong></td>
            <td class={getTotal() < 0 ? 'negative' : 'positive'}><strong>{formatCurrency(getTotal())}</strong></td>
            <td colspan="2"></td>
          </tr>
        {:else}
          <tr><td colspan="6" class="empty">Nenhuma despesa. Clique em "+ Adicionar".</td></tr>
        {/if}
      </tbody>
    </table>
  </div>

  {#if items && items.length > 0}
    <div class="chart-section">
      <canvas bind:this={chartCanvas}></canvas>
    </div>
  {/if}
</div>

<style>
  .expense-wrap { display: flex; gap: 2rem; margin-bottom: 1.5rem; align-items: flex-start; flex-wrap: wrap; }
  .table-section { flex: 2; background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); min-width: 300px; }
  .chart-section { flex: 1; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); min-width: 220px; max-width: 320px; }
  .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  h3 { margin: 0; color: #333; font-size: 1.1rem; }
  .add-form { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1rem; align-items: center; }
  .inp { flex: 2; padding: 0.4rem; border: 1px solid #ddd; border-radius: 5px; min-width: 130px; }
  .inp-sm { flex: 1; padding: 0.4rem; border: 1px solid #ddd; border-radius: 5px; min-width: 100px; }
  .chk-label { display: flex; align-items: center; gap: 4px; font-size: 0.875rem; }
  .btn-add { background: #667eea; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 5px; cursor: pointer; font-size: 0.875rem; }
  .btn-save { background: #4caf50; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 5px; cursor: pointer; }
  .btn-save:disabled { opacity: 0.6; }
  .btn-del { background: #f44336; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; }
  table { width: 100%; border-collapse: collapse; }
  thead { background: #f5f5f5; }
  th { padding: 0.6rem; text-align: left; font-weight: 600; color: #666; border-bottom: 2px solid #ddd; font-size: 0.85rem; }
  td { padding: 0.6rem; border-bottom: 1px solid #eee; font-size: 0.875rem; }
  .pago-row td { opacity: 0.55; text-decoration: line-through; }
  .badge { background: #eef; color: #667eea; padding: 2px 6px; border-radius: 10px; font-size: 0.75rem; }
  .total-row { background: #f9f9f9; }
  .empty { text-align: center; color: #999; font-style: italic; }
  .positive { color: #4caf50; font-weight: 600; }
  .negative { color: #f44336; font-weight: 600; }
</style>
