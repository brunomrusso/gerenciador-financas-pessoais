<script lang="ts">
  import { onMount } from 'svelte'
  import { fetchRecords } from '../stores/records'
  import Chart from 'chart.js/auto'
  import TagInput from './TagInput.svelte'
  import { accountsStore, fetchAccounts } from '../stores/accounts'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let items: any[] = []
  export let recordId: number
  export let month: string = ''
  export let year: number = 0
  export let cardFaturas: any[] = []
  export let refreshKey: number = 0

  const DEFAULT_CATS = ['Moradia', 'Alimentacao', 'Transporte', 'Saude', 'Educacao', 'Lazer', 'Cartao', 'Outros']
  let categorias: string[] = [...DEFAULT_CATS]
  let customCats: {id: number, nome: string}[] = []
  let newCatName = ''
  let showCatManager = false

  const todayISO = () => new Date().toISOString().split('T')[0]
  let newDesc = '', newValor = '', newCategoria = 'Outros', newData = todayISO(), newPago = false, newRecorrente = false, newEhCredito = false
  let newTags: string[] = []
  let newAccountId: number | '' = ''
  let adding = false, saving = false
  let editingId: number | null = null
  let editDesc = '', editValor = '', editCategoria = 'Outros', editData = '', editPago = false, editRecorrente = false, editEhCredito = false
  let editTags: string[] = []
  let editAccountId: number | '' = ''

  let filterCat = ''
  let filterStatus = ''
  let filterText = ''
  let filterTag = ''
  let filterAccount: number | '' = ''
  let sortBy = 'data'
  let sortDir: 'asc' | 'desc' = 'desc'

  let chartCanvas: HTMLCanvasElement
  let chart: Chart | null = null
  let copyMsg = ''

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)
  const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })

  const loadCats = async () => {
    const r = await fetch('/api/records/categories', { headers: auth() })
    if (r.ok) {
      customCats = await r.json()
      categorias = [...DEFAULT_CATS, ...customCats.map((c: any) => c.nome).filter((n: string) => !DEFAULT_CATS.includes(n))]
    }
  }

  const addCat = async () => {
    if (!newCatName.trim()) return
    const r = await fetch('/api/records/categories', { method: 'POST', headers: auth(), body: JSON.stringify({ nome: newCatName.trim() }) })
    if (r.ok) { newCatName = ''; await loadCats() }
  }

  const deleteCat = async (id: number) => {
    await fetch(`/api/records/categories/${id}`, { method: 'DELETE', headers: auth() })
    await loadCats()
  }

  $: filtered = (() => {
    let list = items || []
    if (filterText) list = list.filter(i => i.descricao?.toLowerCase().includes(filterText.toLowerCase()))
    if (filterCat) list = list.filter(i => (i.categoria || 'Outros') === filterCat)
    if (filterTag) list = list.filter(i => Array.isArray(i.tags) && i.tags.includes(filterTag))
    if (filterStatus === 'pago') list = list.filter(i => i.pago)
    if (filterStatus === 'pendente') list = list.filter(i => !i.pago)
    if (filterAccount !== '') list = list.filter(i => (i.account_id || null) === (filterAccount || null))
    list = [...list].sort((a, b) => {
      let va: any, vb: any
      if (sortBy === 'valor') { va = a.valor; vb = b.valor }
      else if (sortBy === 'descricao') { va = a.descricao?.toLowerCase(); vb = b.descricao?.toLowerCase() }
      else { va = a.data || ''; vb = b.data || '' }
      if (va < vb) return sortDir === 'asc' ? -1 : 1
      if (va > vb) return sortDir === 'asc' ? 1 : -1
      return 0
    })
    return list
  })()

  const toggleSort = (col: string) => {
    if (sortBy === col) sortDir = sortDir === 'asc' ? 'desc' : 'asc'
    else { sortBy = col; sortDir = 'asc' }
  }

  $: getDebitoTotal = () => (items || []).filter((i: any) => !i.eh_credito).reduce((s: number, i: any) => s + (i.valor || 0), 0)
  $: getCreditoTotal = () => (items || []).filter((i: any) => i.eh_credito).reduce((s: number, i: any) => s + (i.valor || 0), 0)
  $: debitoCount = (items || []).filter((i: any) => !i.eh_credito).length
  $: getTotal = () => getDebitoTotal()
  $: getFilteredTotal = () => filtered.filter((i: any) => !i.eh_credito).reduce((s: number, i: any) => s + (i.valor || 0), 0)
  $: cardTotal = cardFaturas.reduce((s: number, f: any) => s + (f.total || 0), 0)
  $: if (refreshKey) {} // força reatividade quando refreshKey muda

  $: allTags = (() => {
    const set = new Set<string>()
    items?.forEach((i: any) => Array.isArray(i.tags) && i.tags.forEach((t: string) => set.add(t)))
    cardFaturas?.forEach((f: any) => f.expenses?.forEach((e: any) => Array.isArray(e.tags) && e.tags.forEach((t: string) => set.add(t))))
    return Array.from(set).sort()
  })()

  const handleAdd = async () => {
    if (!newDesc.trim() || !newValor) return
    saving = true
    try {
      await fetch(`/api/records/${recordId}/expenses`, {
        method: 'POST', headers: auth(),
        body: JSON.stringify({ descricao: newDesc, valor: parseFloat(newValor), categoria: newCategoria, data: newData, pago: newPago, recorrente: newRecorrente, tags: newTags, account_id: newAccountId || null, eh_credito: newEhCredito })
      })
      await fetchRecords(month, year.toString())
      await fetchAccounts()
      newDesc = ''; newValor = ''; newCategoria = 'Outros'; newData = todayISO(); newPago = false; newRecorrente = false; newEhCredito = false; newTags = []; newAccountId = ''; adding = false
    } finally { saving = false }
  }

  const startEdit = (item: any) => {
    editingId = item.id; editDesc = item.descricao || ''; editValor = String(item.valor || '')
    editCategoria = item.categoria || 'Outros'; editData = item.data || ''; editPago = item.pago || false; editRecorrente = item.recorrente || false; editEhCredito = item.eh_credito || false
    editTags = Array.isArray(item.tags) ? [...item.tags] : []
    editAccountId = item.account_id || ''
  }

  const cancelEdit = () => { editingId = null }

  const saveEdit = async (item: any) => {
    await fetch(`/api/records/expenses/${item.id}`, {
      method: 'PUT', headers: auth(),
      body: JSON.stringify({ descricao: editDesc, valor: parseFloat(editValor), categoria: editCategoria, data: editData, pago: editPago, recorrente: editRecorrente, tags: editTags, account_id: editAccountId || null, eh_credito: editEhCredito })
    })
    editingId = null
    await fetchRecords(month, year.toString())
    await fetchAccounts()
  }

  const togglePago = async (item: any) => {
    await fetch(`/api/records/expenses/${item.id}`, { method: 'PUT', headers: auth(), body: JSON.stringify({ pago: !item.pago }) })
    await fetchRecords(month, year.toString())
    await fetchAccounts()
  }

  const handleDelete = async (item: any) => {
    if (!confirm(`Excluir "${item.descricao}"?`)) return
    await fetch(`/api/records/expenses/${item.id}`, { method: 'DELETE', headers: auth() })
    await fetchRecords(month, year.toString())
    await fetchAccounts()
  }

  const exportExcel = () => {
    const token = localStorage.getItem('token')
    const url = `/api/records/${recordId}/export`
    const a = document.createElement('a')
    fetch(url, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.blob())
      .then(blob => { a.href = URL.createObjectURL(blob); a.download = `financas_${month}_${year}.xlsx`; a.click() })
  }

  const copyRecurring = async () => {
    const r = await fetch(`/api/records/${recordId}/copy-recurring`, { method: 'POST', headers: auth() })
    const data = await r.json()
    if (r.ok) {
      copyMsg = data.copiadas > 0 ? `${data.copiadas} despesa(s) recorrente(s) copiada(s)!` : 'Nenhuma despesa recorrente no mês anterior.'
      await fetchRecords(month, year.toString())
      await fetchAccounts()
    } else {
      copyMsg = data.error || 'Erro ao copiar recorrentes.'
    }
    setTimeout(() => copyMsg = '', 4000)
  }

  const buildChart = () => {
    if (!chartCanvas) return
    const grouped: Record<string, number> = {}
    items?.forEach((i: any) => { const c = i.categoria || 'Outros'; grouped[c] = (grouped[c] || 0) + Math.abs(i.valor || 0) })
    cardFaturas?.forEach((f: any) => f.expenses?.forEach((e: any) => {
      const c = e.categoria || 'Cartao'
      grouped[c] = (grouped[c] || 0) + Math.abs(e.valor || 0)
    }))
    if (!Object.keys(grouped).length) return
    const labels = Object.keys(grouped)
    const colors = ['#667eea','#764ba2','#f44336','#ff9800','#4caf50','#2196f3','#9c27b0','#607d8b','#795548','#00bcd4']
    if (chart) chart.destroy()
    chart = new Chart(chartCanvas, {
      type: 'pie',
      data: { labels, datasets: [{ data: Object.values(grouped), backgroundColor: colors.slice(0, labels.length), borderWidth: 2 }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom' }, title: { display: true, text: 'Por Categoria' } } }
    })
  }

  const CATS_PER_PAGE = 5
  let catPage = 0

  $: catRows = (() => {
    const grouped: Record<string, number> = {}
    items?.forEach((i: any) => {
      const c = i.categoria || 'Outros'
      grouped[c] = (grouped[c] || 0) + Math.abs(i.valor || 0)
    })
    cardFaturas?.forEach((f: any) => f.expenses?.forEach((e: any) => {
      const c = e.categoria || 'Cartao'
      grouped[c] = (grouped[c] || 0) + Math.abs(e.valor || 0)
    }))
    return Object.entries(grouped).sort((a, b) => b[1] - a[1])
  })()

  $: catTotal = catRows.reduce((s, [, v]) => s + v, 0)
  $: catTotalPages = Math.ceil(catRows.length / CATS_PER_PAGE)
  $: catPageRows = catRows.slice(catPage * CATS_PER_PAGE, (catPage + 1) * CATS_PER_PAGE)
  $: { if (catRows) catPage = 0 }

  onMount(() => loadCats())
  $: if (items || cardFaturas) setTimeout(buildChart, 100)
</script>

<div class="expense-wrap">
  <div class="table-section">
    <div class="table-header">
      <h3>Despesas</h3>
      <div class="header-actions">
        <button class="btn-sm btn-green" on:click={copyRecurring} title="Copiar recorrentes do mês anterior">↻ Recorrentes</button>
        <button class="btn-sm btn-export" on:click={exportExcel} title="Exportar para Excel">⬇ Excel</button>
        <button class="btn-sm btn-cat" on:click={() => showCatManager = !showCatManager}>⚙ Categorias</button>
        <button class="btn-add" on:click={() => { adding = !adding; editingId = null; if (adding && !newData) newData = todayISO() }}>
          {adding ? 'Cancelar' : '+ Adicionar'}
        </button>
      </div>
    </div>

    {#if copyMsg}
      <p class="copy-msg">{copyMsg}</p>
    {/if}

    {#if showCatManager}
      <div class="cat-manager">
        <strong>Categorias personalizadas</strong>
        <div class="cat-list">
          {#each customCats as cat}
            <span class="cat-chip">{cat.nome}<button on:click={() => deleteCat(cat.id)}>✕</button></span>
          {/each}
        </div>
        <div class="cat-add-row">
          <input type="text" placeholder="Nova categoria..." bind:value={newCatName} class="inp-cat" on:keydown={(e) => e.key === 'Enter' && addCat()} />
          <button class="btn-sm btn-green" on:click={addCat}>Adicionar</button>
        </div>
      </div>
    {/if}

    {#if adding}
      <div class="add-form">
        <input type="text" placeholder="Descricao *" bind:value={newDesc} class="inp full" />
        <input type="number" inputmode="decimal" placeholder="Valor (ex: -150.00)" bind:value={newValor} step="0.01" class="inp half" />
        <select bind:value={newCategoria} class="inp half">
          {#each categorias as cat}<option>{cat}</option>{/each}
        </select>
        <input type="date" bind:value={newData} class="inp half" />
        <select bind:value={newAccountId} class="inp half" title="Conta">
          <option value="">Conta padrão</option>
          {#each $accountsStore as a (a.id)}<option value={a.id}>{a.icone} {a.nome}</option>{/each}
        </select>
        <TagInput bind:tags={newTags} suggestions={allTags} />
        <label class="chk-label"><input type="checkbox" bind:checked={newPago} /> Pago</label>
        <label class="chk-label"><input type="checkbox" bind:checked={newRecorrente} /> Recorrente</label>
        <label class="chk-label"><input type="checkbox" bind:checked={newEhCredito} /> É crédito?</label>
        <button class="btn-save" on:click={handleAdd} disabled={saving}>{saving ? '...' : 'Salvar'}</button>
      </div>
    {/if}

    <div class="filter-bar">
      <input type="text" placeholder="🔍 Buscar..." bind:value={filterText} class="inp-filter" />
      <select bind:value={filterCat} class="inp-filter-sm">
        <option value="">Todas categorias</option>
        {#each categorias as cat}<option>{cat}</option>{/each}
      </select>
      <select bind:value={filterStatus} class="inp-filter-sm">
        <option value="">Todos status</option>
        <option value="pago">Pago</option>
        <option value="pendente">Pendente</option>
      </select>
      <select bind:value={filterAccount} class="inp-filter-sm">
        <option value="">Todas contas</option>
        {#each $accountsStore.filter(a => a.ativa) as a (a.id)}<option value={a.id}>{a.icone} {a.nome}</option>{/each}
      </select>
      {#if allTags.length > 0}
        <select bind:value={filterTag} class="inp-filter-sm">
          <option value="">Todas tags</option>
          {#each allTags as t}<option value={t}>#{t}</option>{/each}
        </select>
      {/if}
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th on:click={() => toggleSort('descricao')} class="sortable">Descricao {sortBy==='descricao' ? (sortDir==='asc'?'↑':'↓') : ''}</th>
            <th class="hide-sm">Categoria</th>
            <th class="hide-sm sortable" on:click={() => toggleSort('data')}>Data {sortBy==='data' ? (sortDir==='asc'?'↑':'↓') : ''}</th>
            <th class="sortable" on:click={() => toggleSort('valor')}>Valor {sortBy==='valor' ? (sortDir==='asc'?'↑':'↓') : ''}</th>
            <th>Pago</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#if filtered.length > 0}
            {#each filtered as item (item.id)}
              {#if editingId === item.id}
                <tr class="edit-row">
                  <td><input type="text" bind:value={editDesc} class="edit-inp" /></td>
                  <td class="hide-sm"><select bind:value={editCategoria} class="edit-inp">{#each categorias as c}<option>{c}</option>{/each}</select></td>
                  <td class="hide-sm">
                    <input type="date" bind:value={editData} class="edit-inp" />
                    <div class="tag-edit-wrap"><TagInput bind:tags={editTags} suggestions={allTags} placeholder="tags..." /></div>
                  </td>
                  <td><input type="number" inputmode="decimal" bind:value={editValor} step="0.01" class="edit-inp narrow" /></td>
                  <td>
                    <label class="chk-label-sm"><input type="checkbox" bind:checked={editPago} /> Pago</label>
                    <label class="chk-label-sm"><input type="checkbox" bind:checked={editRecorrente} /> Rec.</label>
                    <label class="chk-label-sm"><input type="checkbox" bind:checked={editEhCredito} /> Crédito</label>
                  </td>
                  <td class="action-cell">
                    <button class="btn-ok" on:click={() => saveEdit(item)}>✓</button>
                    <button class="btn-cancel-edit" on:click={cancelEdit}>✕</button>
                  </td>
                </tr>
              {:else}
                <tr class={item.pago ? 'pago-row' : ''}>
                  <td class="desc-cell" data-label="Descrição">
                    {item.descricao || '-'}
                    {#if item.recorrente}<span class="rec-badge" title="Recorrente">↻</span>{/if}
                    {#if Array.isArray(item.tags) && item.tags.length > 0}
                      <span class="row-tags">
                        {#each item.tags as t}
                          <span class="tag-mini" on:click={() => filterTag = t}>#{t}</span>
                        {/each}
                      </span>
                    {/if}
                  </td>
                  <td class="hide-sm" data-label="Categoria">
                    <span class="badge">{item.categoria || 'Outros'}</span>
                    {#if item.account_id}
                      {@const acc = $accountsStore.find(a => a.id === item.account_id)}
                      {#if acc}<span class="acc-badge" style="background:{acc.cor}22; color:{acc.cor}">{acc.icone} {acc.nome}</span>{/if}
                    {/if}
                  </td>
                  <td class="hide-sm" data-label="Data">{item.data || '-'}</td>
                  <td data-label="Valor" class={item.eh_credito ? 'positive' : (item.tipo === 'Receita' ? 'positive' : 'negative')}>
                    {#if item.eh_credito}<span class="credit-badge">✓ Crédito</span>{/if}
                    {fmt(item.valor)}
                  </td>
                  <td data-label="Pago" class="pago-cell"><input type="checkbox" checked={item.pago} on:change={() => togglePago(item)} /></td>
                  <td class="action-cell">
                    <button class="btn-edit" on:click={() => startEdit(item)} title="Editar">✎</button>
                    <button class="btn-del" on:click={() => handleDelete(item)} title="Excluir">✕</button>
                  </td>
                </tr>
              {/if}
            {/each}
          {:else}
            <tr><td colspan="6" class="empty">{(items?.length || 0) > 0 ? 'Nenhuma despesa corresponde ao filtro.' : 'Nenhuma despesa. Clique em "+ Adicionar".'}</td></tr>
          {/if}
        </tbody>
        <tfoot>
          {#if getCreditoTotal() > 0}
          <tr class="total-row">
            <td colspan="2"><strong>Total créditos</strong></td>
            <td class="hide-sm"></td>
            <td class="positive"><strong>{fmt(getCreditoTotal())}</strong></td>
            <td colspan="2"></td>
          </tr>
          {/if}
          <tr class="total-row">
            <td colspan="2"><strong>Total débitos ({debitoCount})</strong></td>
            <td class="hide-sm"></td>
            <td class="negative"><strong>{fmt(getDebitoTotal())}</strong></td>
            <td colspan="2"></td>
          </tr>
          {#if cardTotal > 0}
          <tr class="total-row">
            <td colspan="2"><strong>Total cartões</strong></td>
            <td class="hide-sm"></td>
            <td class="negative"><strong>{fmt(cardTotal)}</strong></td>
            <td colspan="2"></td>
          </tr>
          {/if}
          <tr class="total-row grand-total">
            <td colspan="2"><strong>Total geral</strong></td>
            <td class="hide-sm"></td>
            <td class={getDebitoTotal() + cardTotal - getCreditoTotal() >= 0 ? 'negative' : 'positive'}><strong>{fmt(getDebitoTotal() + cardTotal - getCreditoTotal())}</strong></td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>

  {#if (items && items.length > 0) || cardFaturas.length > 0}
    <div class="chart-section">
      <canvas bind:this={chartCanvas} class="chart-canvas"></canvas>

      {#if catRows.length > 0}
        <div class="cat-table-wrap">
          <table class="cat-table">
            <thead>
              <tr><th>Categoria</th><th>Total</th><th>%</th></tr>
            </thead>
            <tbody>
              {#each catPageRows as [cat, val]}
                <tr>
                  <td class="cat-name">{cat}</td>
                  <td class="cat-val negative">{fmt(val)}</td>
                  <td class="cat-pct">{catTotal > 0 ? ((val / catTotal) * 100).toFixed(1) : '0.0'}%</td>
                </tr>
              {/each}
            </tbody>
          </table>

          {#if catTotalPages > 1}
            <div class="cat-pager">
              <button class="pager-btn" disabled={catPage === 0} on:click={() => catPage--}>‹</button>
              <span class="pager-info">{catPage + 1} / {catTotalPages}</span>
              <button class="pager-btn" disabled={catPage >= catTotalPages - 1} on:click={() => catPage++}>›</button>
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .expense-wrap { display: flex; gap: 1.5rem; margin-bottom: 1.5rem; align-items: stretch; flex-wrap: wrap; width: 100%; box-sizing: border-box; }
  .table-section { flex: 2; background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); min-width: 0; max-width: 100%; box-sizing: border-box; overflow: hidden; }
  .chart-section { flex: 1; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); min-width: 260px; max-width: 340px; display: flex; flex-direction: column; gap: 0.75rem; }
  .chart-canvas { width: 100% !important; }

  .table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem; }
  h3 { margin: 0; color: #333; font-size: 1.1rem; }
  .header-actions { display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center; }

  .btn-add { background: #667eea; color: white; border: none; padding: 0.45rem 1rem; border-radius: 6px; cursor: pointer; font-size: 0.875rem; white-space: nowrap; }
  .btn-sm { border: none; padding: 0.4rem 0.7rem; border-radius: 5px; cursor: pointer; font-size: 0.78rem; white-space: nowrap; color: white; }
  .btn-green { background: #4caf50; }
  .btn-export { background: #ff9800; }
  .btn-cat { background: #607d8b; }
  .btn-save { background: #4caf50; color: white; border: none; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer; }
  .btn-save:disabled { opacity: 0.6; }
  .btn-edit { background: #2196f3; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; display: inline-flex; align-items: center; justify-content: center; }
  .btn-del { background: #f44336; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; font-size: 0.7rem; display: inline-flex; align-items: center; justify-content: center; }
  .btn-ok { background: #4caf50; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
  .btn-cancel-edit { background: #9e9e9e; color: white; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
  .action-cell { display: flex; gap: 4px; align-items: center; }

  .copy-msg { background: #e8f5e9; color: #2e7d32; padding: 0.5rem 0.75rem; border-radius: 5px; font-size: 0.85rem; margin-bottom: 0.5rem; }

  .cat-manager { background: #f9f9ff; border: 1px solid #ddd; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem; }
  .cat-manager strong { font-size: 0.875rem; color: #333; }
  .cat-list { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.5rem 0; }
  .cat-chip { background: #eef; color: #667eea; padding: 3px 8px; border-radius: 12px; font-size: 0.78rem; display: flex; align-items: center; gap: 4px; }
  .cat-chip button { background: none; border: none; cursor: pointer; color: #667eea; font-size: 0.7rem; padding: 0; line-height: 1; }
  .cat-add-row { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
  .inp-cat { flex: 1; padding: 0.35rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; }

  .filter-bar { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
  .inp-filter { flex: 2; min-width: 140px; padding: 0.4rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; color: #333; background: #fff; color-scheme: light; }
  .inp-filter-sm { flex: 1; min-width: 120px; padding: 0.4rem 0.5rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; color: #333; background: #fff; color-scheme: light; }

  .add-form { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; align-items: center; background: #f9f9ff; border-radius: 8px; padding: 0.75rem; }
  .inp { padding: 0.45rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.875rem; color: #333; background: #fff; box-sizing: border-box; color-scheme: light; }
  .inp.full { flex: 1 1 100%; }
  .inp.half { flex: 1 1 140px; }
  .chk-label { display: flex; align-items: center; gap: 5px; font-size: 0.875rem; color: #333; }
  .chk-label-sm { display: flex; align-items: center; gap: 3px; font-size: 0.75rem; color: #333; white-space: nowrap; }

  .table-wrap { overflow-x: auto; overflow-y: auto; max-height: 460px; -webkit-overflow-scrolling: touch; width: 100%; }
  table { width: 100%; border-collapse: collapse; min-width: 300px; }
  thead { background: #f5f5f5; position: sticky; top: 0; z-index: 2; }
  tfoot { position: sticky; bottom: 0; z-index: 2; }
  th { padding: 0.6rem 0.5rem; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #ddd; font-size: 0.82rem; white-space: nowrap; }
  th.sortable { cursor: pointer; user-select: none; }
  th.sortable:hover { color: #667eea; }
  td { padding: 0.3rem 0.5rem; border-bottom: 1px solid #eee; font-size: 0.875rem; color: #222; vertical-align: middle; white-space: nowrap; line-height: 1.2; }
  .desc-cell { color: #222; font-weight: 500; white-space: normal; }
  .edit-inp { width: 100%; padding: 0.3rem; border: 1px solid #667eea; border-radius: 4px; font-size: 0.82rem; color: #333; background: #fff; color-scheme: light; box-sizing: border-box; }
  .edit-inp.narrow { max-width: 90px; }
  .edit-row td { background: #f0f4ff; }
  .pago-row td { opacity: 0.5; text-decoration: line-through; }
  .badge { background: #eef; color: #667eea; padding: 1px 6px; border-radius: 8px; font-size: 0.7rem; line-height: 1.3; }
  .rec-badge { background: #e8f5e9; color: #4caf50; font-size: 0.65rem; border-radius: 4px; padding: 1px 3px; margin-left: 4px; line-height: 1.3; }
  .credit-badge { background: #e8f5e9; color: #4caf50; font-size: 0.7rem; border-radius: 4px; padding: 2px 5px; margin-right: 4px; line-height: 1.3; font-weight: 500; display: inline-block; }
  .acc-badge { display: inline-block; padding: 1px 6px; border-radius: 8px; font-size: 0.68rem; margin-left: 4px; line-height: 1.3; font-weight: 500; }
  .row-tags { display: inline-flex; gap: 4px; margin-left: 6px; flex-wrap: wrap; }
  .tag-mini { background: #e8eaff; color: #3949ab; border-radius: 8px; padding: 1px 6px; font-size: 0.7rem; cursor: pointer; transition: background-color .2s; }
  .tag-mini:hover { background: #c5cae9; }
  .tag-edit-wrap { margin-top: 4px; }
  .total-row td { background: #f9f9f9; font-size: 0.9rem; border-top: 1px solid #ddd; }
  .grand-total td { background: #f0f0ff; font-size: 0.95rem; border-top: 2px solid #ddd; }
  .empty { text-align: center; color: #999; font-style: italic; padding: 1.5rem; }
  .positive { color: #4caf50; font-weight: 600; }
  .negative { color: #f44336; font-weight: 600; }

  .cat-table-wrap { border-top: 1px solid #eee; padding-top: 0.5rem; }
  .cat-table { width: 100%; border-collapse: collapse; }
  .cat-table th { padding: 0.35rem 0.4rem; font-size: 0.75rem; color: #777; font-weight: 600; border-bottom: 1px solid #eee; text-align: left; }
  .cat-table td { padding: 0.35rem 0.4rem; font-size: 0.8rem; color: #333; border-bottom: 1px solid #f5f5f5; }
  .cat-name { color: #444; }
  .cat-val { font-weight: 600; }
  .cat-pct { color: #888; text-align: right; }
  .cat-pager { display: flex; align-items: center; justify-content: center; gap: 0.75rem; margin-top: 0.5rem; }
  .pager-btn { background: #667eea; color: white; border: none; width: 26px; height: 26px; border-radius: 50%; cursor: pointer; font-size: 1rem; display: inline-flex; align-items: center; justify-content: center; }
  .pager-btn:disabled { background: #ccc; cursor: default; }
  .pager-info { font-size: 0.8rem; color: #666; }

  /* Compactacao da cat-table no mobile e desktop */
  .cat-table-wrap {
    max-height: 240px;
    overflow-y: auto;
  }

  @media (max-width: 768px) {
    .expense-wrap { flex-direction: column; gap: 0.75rem; margin-bottom: 0.75rem; }
    .chart-section { max-width: 100%; width: 100%; padding: 0.75rem; }

    /* Cat-table compacta no mobile */
    .cat-table-wrap { max-height: 200px; }
    .cat-table th { padding: 0.25rem 0.3rem; font-size: 0.68rem; }
    .cat-table td { padding: 0.28rem 0.3rem; font-size: 0.75rem; }
    .cat-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 110px; }
    .cat-val { font-size: 0.75rem; }
    .cat-pct { font-size: 0.72rem; }

    .table-section { padding: 0.6rem; flex: 1 1 100%; }
    .table-wrap { max-height: 65vh; overflow-y: auto; }
    h3 { font-size: 0.95rem; }
    .header-actions { gap: 0.3rem; flex-wrap: wrap; }
    .btn-sm { padding: 0.35rem 0.55rem; font-size: 0.72rem; min-height: 30px; }
    .btn-add { padding: 0.4rem 0.75rem; font-size: 0.8rem; }
    .filter-bar { gap: 0.3rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
    .inp-filter, .inp-filter-sm { flex: 1 1 100%; min-width: 0; max-width: 100%; width: 100%; padding: 0.45rem; font-size: 0.85rem; box-sizing: border-box; }
    .filter-bar select { max-width: 100%; min-width: 0; box-sizing: border-box; }
    .pager-btn { width: 32px; height: 32px; font-size: 0.95rem; }
    .add-form { flex-direction: column; gap: 0.4rem; padding: 0.6rem; align-items: stretch; flex-wrap: nowrap; }
    .add-form .inp.half, .add-form .inp.full { width: 100%; max-width: 100%; flex: 1 1 100%; min-width: 0; }
    .add-form select { width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; }
    .add-form input:not([type="checkbox"]):not([type="radio"]) { width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; }
    .add-form input[type="date"] { -webkit-appearance: none; appearance: none; display: block; }
    .add-form input[type="checkbox"] { width: auto; flex: 0 0 auto; }
    .add-form .chk-label { align-self: flex-start; width: auto; }

    /* Estilo extrato: cada despesa = linha compacta */
    table { min-width: 0; width: 100%; display: block; }
    thead, tfoot { display: none; }
    tbody { display: block; }

    tr {
      display: grid;
      grid-template-columns: 1fr auto auto;
      column-gap: 0.5rem;
      row-gap: 2px;
      padding: 0.45rem 0.55rem;
      border-bottom: 1px solid #eef0f5;
      margin: 0;
      align-items: center;
    }
    tr:last-child { border-bottom: none; }
    tr.pago-row { opacity: 0.55; }

    td { border: none !important; padding: 0; font-size: 0.8rem; min-height: 0; }
    td::before { display: none; }

    /* Linha 1: descrição (col 1) + valor (col 2-3) */
    td.desc-cell {
      grid-column: 1; grid-row: 1;
      font-weight: 600;
      font-size: 0.88rem;
      color: #333;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      padding-right: 0.4rem;
    }
    td.desc-cell .row-tags { display: none; }
    td.desc-cell .rec-badge { font-size: 0.7rem; margin-left: 3px; opacity: 0.7; }

    td[data-label="Valor"] {
      grid-column: 2 / 4; grid-row: 1;
      font-weight: 700;
      font-size: 0.92rem;
      text-align: right;
      white-space: nowrap;
    }

    /* Linha 2: cat/conta (col 1) | pago (col 2) | acoes (col 3) */
    td.hide-sm[data-label="Categoria"] {
      grid-column: 1; grid-row: 2;
      display: flex !important;
      gap: 4px;
      flex-wrap: nowrap;
      overflow: hidden;
      font-size: 0.66rem;
      color: #888;
      align-items: center;
    }
    td.hide-sm[data-label="Data"] { display: none !important; }

    td.pago-cell {
      grid-column: 2; grid-row: 2;
      display: inline-flex !important;
      align-items: center;
      padding: 0 0.3rem 0 0;
    }
    td.pago-cell input { transform: scale(0.9); margin: 0; }

    td.action-cell {
      grid-column: 3; grid-row: 2;
      display: flex;
      justify-content: flex-end;
      gap: 0.25rem;
      align-items: center;
    }
    .btn-edit, .btn-del { width: 26px; height: 26px; font-size: 0.7rem; border-radius: 4px; }
    .badge { font-size: 0.62rem; padding: 1px 5px; }
    .acc-badge { font-size: 0.62rem; padding: 1px 5px; }
    .credit-badge { display: none; }

    /* Edit-row mobile: bem compacto e vertical */
    tr.edit-row {
      display: block;
      background: #f0f4ff;
      padding: 0.6rem 0.7rem;
      margin: 0.35rem 0;
      border: 1px solid #c5cae9;
      border-radius: 8px;
    }
    tr.edit-row td { display: block; padding: 0.3rem 0; }
    tr.edit-row td::before {
      content: attr(data-label);
      display: block; margin-bottom: 3px;
      font-size: 0.68rem; color: #667; font-weight: 600;
      text-transform: uppercase;
    }
    tr.edit-row .edit-inp, tr.edit-row select.edit-inp {
      width: 100%; box-sizing: border-box;
      padding: 0.45rem 0.55rem; font-size: 0.88rem;
    }
    tr.edit-row .narrow { max-width: 100%; }
    tr.edit-row .chk-label-sm { display: inline-flex; margin-right: 0.7rem; margin-top: 0.3rem; font-size: 0.78rem; }
    tr.edit-row td.action-cell {
      display: flex;
      gap: 0.5rem;
      padding-top: 0.5rem;
      justify-content: flex-end;
      grid-column: auto; grid-row: auto;
      border-top: none !important;
    }
    tr.edit-row td.action-cell .btn-ok,
    tr.edit-row td.action-cell .btn-cancel-edit { width: 36px; height: 36px; }
  }
</style>
