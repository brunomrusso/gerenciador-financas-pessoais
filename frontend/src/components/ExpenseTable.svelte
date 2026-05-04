<script lang="ts">
  import { fetchRecords } from '../stores/records'
  import Chart from 'chart.js/auto'

  export let items: any[] = []
  export let recordId: number
  export let month: string = ''
  export let year: number = 0

  const categorias = ['Moradia', 'Alimentacao', 'Transporte', 'Saude', 'Educacao', 'Lazer', 'Cartao', 'Outros']

  let newDesc = '', newValor = '', newCategoria = 'Outros', newData = '', newPago = false
  let adding = false, saving = false
  let editingId: number | null = null
  let editDesc = '', editValor = '', editCategoria = 'Outros', editData = '', editPago = false
  let chartCanvas: HTMLCanvasElement
  let chart: Chart | null = null

  const fmt = (v: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)
  const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })
  const getTotal = () => items?.reduce((s, i) => s + (i.valor || 0), 0) || 0

  const handleAdd = async () => {
    if (!newDesc.trim() || !newValor) return
    saving = true
    try {
      await fetch(`/api/records/${recordId}/expenses`, {
        method: 'POST', headers: auth(),
        body: JSON.stringify({ descricao: newDesc, valor: parseFloat(newValor), categoria: newCategoria, data: newData, pago: newPago })
      })
      await fetchRecords(month, year.toString())
      newDesc = ''; newValor = ''; newCategoria = 'Outros'; newData = ''; newPago = false; adding = false
    } finally { saving = false }
  }

  const startEdit = (item: any) => {
    editingId = item.id
    editDesc = item.descricao || ''
    editValor = String(item.valor || '')
    editCategoria = item.categoria || 'Outros'
    editData = item.data || ''
    editPago = item.pago || false
  }

  const cancelEdit = () => { editingId = null }

  const saveEdit = async (item: any) => {
    await fetch(`/api/records/expenses/${item.id}`, {
      method: 'PUT', headers: auth(),
      body: JSON.stringify({ descricao: editDesc, valor: parseFloat(editValor), categoria: editCategoria, data: editData, pago: editPago })
    })
    editingId = null
    await fetchRecords(month, year.toString())
  }

  const togglePago = async (item: any) => {
    await fetch(`/api/records/expenses/${item.id}`, { method: 'PUT', headers: auth(), body: JSON.stringify({ pago: !item.pago }) })
    await fetchRecords(month, year.toString())
  }

  const handleDelete = async (item: any) => {
    if (!confirm(`Excluir "${item.descricao}"?`)) return
    await fetch(`/api/records/expenses/${item.id}`, { method: 'DELETE', headers: auth() })
    await fetchRecords(month, year.toString())
  }

  const buildChart = () => {
    if (!chartCanvas || !items?.length) return
    const grouped: Record<string, number> = {}
    items.forEach(i => { const c = i.categoria || 'Outros'; grouped[c] = (grouped[c] || 0) + Math.abs(i.valor || 0) })
    const labels = Object.keys(grouped)
    const colors = ['#667eea','#764ba2','#f44336','#ff9800','#4caf50','#2196f3','#9c27b0','#607d8b']
    if (chart) chart.destroy()
    chart = new Chart(chartCanvas, {
      type: 'pie',
      data: { labels, datasets: [{ data: Object.values(grouped), backgroundColor: colors.slice(0, labels.length), borderWidth: 2 }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Por Categoria' } } }
    })
  }

  $: if (items) setTimeout(buildChart, 100)
</script>

<div class="expense-wrap">
  <div class="table-section">
    <div class="table-header">
      <h3>Despesas</h3>
      <button class="btn-add" on:click={() => { adding = !adding; editingId = null }}>
        {adding ? 'Cancelar' : '+ Adicionar'}
      </button>
    </div>

    {#if adding}
      <div class="add-form">
        <input type="text" placeholder="Descricao *" bind:value={newDesc} class="inp full" />
        <input type="number" placeholder="Valor (ex: -150.00)" bind:value={newValor} step="0.01" class="inp half" />
        <select bind:value={newCategoria} class="inp half">
          {#each categorias as cat}<option>{cat}</option>{/each}
        </select>
        <input type="date" bind:value={newData} class="inp half" />
        <label class="chk-label">
          <input type="checkbox" bind:checked={newPago} /> Pago
        </label>
        <button class="btn-save" on:click={handleAdd} disabled={saving}>{saving ? '...' : 'Salvar'}</button>
      </div>
    {/if}

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Descricao</th>
            <th class="hide-sm">Categoria</th>
            <th class="hide-sm">Data</th>
            <th>Valor</th>
            <th>Pago</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#if items && items.length > 0}
            {#each items as item (item.id)}
              {#if editingId === item.id}
                <tr class="edit-row">
                  <td><input type="text" bind:value={editDesc} class="edit-inp" /></td>
                  <td class="hide-sm"><select bind:value={editCategoria} class="edit-inp">{#each categorias as c}<option>{c}</option>{/each}</select></td>
                  <td class="hide-sm"><input type="date" bind:value={editData} class="edit-inp" /></td>
                  <td><input type="number" bind:value={editValor} step="0.01" class="edit-inp" /></td>
                  <td><input type="checkbox" bind:checked={editPago} /></td>
                  <td class="action-cell">
                    <button class="btn-ok" on:click={() => saveEdit(item)}>✓</button>
                    <button class="btn-cancel-edit" on:click={cancelEdit}>✕</button>
                  </td>
                </tr>
              {:else}
                <tr class={item.pago ? 'pago-row' : ''}>
                  <td class="desc-cell">{item.descricao || '-'}</td>
                  <td class="hide-sm"><span class="badge">{item.categoria || 'Outros'}</span></td>
                  <td class="hide-sm">{item.data || '-'}</td>
                  <td class={item.valor < 0 ? 'negative' : 'positive'}>{fmt(item.valor)}</td>
                  <td><input type="checkbox" checked={item.pago} on:change={() => togglePago(item)} /></td>
                  <td class="action-cell">
                    <button class="btn-edit" on:click={() => startEdit(item)} title="Editar">✎</button>
                    <button class="btn-del" on:click={() => handleDelete(item)} title="Excluir">✕</button>
                  </td>
                </tr>
              {/if}
            {/each}
            <tr class="total-row">
              <td colspan="2"><strong>Total</strong></td>
              <td class="hide-sm"></td>
              <td class={getTotal() < 0 ? 'negative' : 'positive'}><strong>{fmt(getTotal())}</strong></td>
              <td colspan="2"></td>
            </tr>
          {:else}
            <tr><td colspan="6" class="empty">Nenhuma despesa. Clique em "+ Adicionar".</td></tr>
          {/if}
        </tbody>
      </table>
    </div>
  </div>

  {#if items && items.length > 0}
    <div class="chart-section">
      <canvas bind:this={chartCanvas}></canvas>
    </div>
  {/if}
</div>

<style>
  .expense-wrap { display: flex; gap: 1.5rem; margin-bottom: 1.5rem; align-items: flex-start; flex-wrap: wrap; }
  .table-section { flex: 2; background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); min-width: 0; width: 100%; }
  .chart-section { flex: 1; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); min-width: 200px; max-width: 280px; }
  .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  h3 { margin: 0; color: #333; font-size: 1.1rem; }

  .add-form { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; align-items: center; background: #f9f9ff; border-radius: 8px; padding: 0.75rem; }
  .inp { padding: 0.45rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.875rem; color: #333; background: white; box-sizing: border-box; }
  .inp.full { flex: 1 1 100%; }
  .inp.half { flex: 1 1 140px; }
  .chk-label { display: flex; align-items: center; gap: 5px; font-size: 0.875rem; color: #333; }

  .btn-add { background: #667eea; color: white; border: none; padding: 0.45rem 1rem; border-radius: 6px; cursor: pointer; font-size: 0.875rem; white-space: nowrap; }
  .btn-save { background: #4caf50; color: white; border: none; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer; }
  .btn-save:disabled { opacity: 0.6; }
  .btn-edit { background: #2196f3; color: white; border: none; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
  .btn-del { background: #f44336; color: white; border: none; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
  .btn-ok { background: #4caf50; color: white; border: none; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; }
  .btn-cancel-edit { background: #9e9e9e; color: white; border: none; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; }
  .action-cell { display: flex; gap: 4px; align-items: center; }

  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; min-width: 320px; }
  thead { background: #f5f5f5; }
  th { padding: 0.6rem 0.5rem; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #ddd; font-size: 0.82rem; white-space: nowrap; }
  td { padding: 0.55rem 0.5rem; border-bottom: 1px solid #eee; font-size: 0.875rem; color: #333; }
  .desc-cell { color: #222; font-weight: 500; }
  .edit-inp { width: 100%; padding: 0.3rem; border: 1px solid #667eea; border-radius: 4px; font-size: 0.82rem; color: #333; box-sizing: border-box; }
  .edit-row td { background: #f0f4ff; }
  .pago-row td { opacity: 0.5; text-decoration: line-through; }
  .badge { background: #eef; color: #667eea; padding: 2px 7px; border-radius: 10px; font-size: 0.75rem; }
  .total-row td { background: #f9f9f9; font-size: 0.9rem; }
  .empty { text-align: center; color: #999; font-style: italic; padding: 1.5rem; }
  .positive { color: #4caf50; font-weight: 600; }
  .negative { color: #f44336; font-weight: 600; }

  @media (max-width: 640px) {
    .expense-wrap { flex-direction: column; }
    .chart-section { max-width: 100%; width: 100%; }
    .hide-sm { display: none; }
    .table-section { padding: 1rem; }
    h3 { font-size: 1rem; }
  }
</style>
