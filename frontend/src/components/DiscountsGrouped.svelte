<script lang="ts">
  import { fetchRecords } from '../stores/records'
  import { accountsStore, fetchAccounts } from '../stores/accounts'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let record: any
  export let month: string = ''
  export let year: number = 0

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)

  const auth = () => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
  })

  // Estado de edição/adição por linha
  let addingForAccount: number | null = null
  let addingForOrphan = false
  let editingId: number | null = null
  let descricao = ''
  let valor = ''
  let recorrente = false
  let valorTipo: 'desconto' | 'credito' = 'desconto'

  const resetForm = () => {
    addingForAccount = null
    addingForOrphan = false
    editingId = null
    descricao = ''
    valor = ''
    recorrente = false
    valorTipo = 'desconto'
  }

  const startAdd = (accountId: number | null) => {
    resetForm()
    if (accountId === null) addingForOrphan = true
    else addingForAccount = accountId
  }

  const startEdit = (d: any) => {
    resetForm()
    editingId = d.id
    descricao = d.descricao
    valor = String(Math.abs(d.valor))
    recorrente = !!d.recorrente
    valorTipo = (d.valor || 0) < 0 ? 'desconto' : 'credito'
  }

  const refresh = async () => {
    await fetchRecords(month, year.toString())
    await fetchAccounts()
  }

  const handleSave = async (groupAccountId: number | null) => {
    const v = parseFloat(valor)
    if (!v || isNaN(v) || !descricao.trim()) return
    const signedValue = valorTipo === 'desconto' ? -Math.abs(v) : Math.abs(v)
    const body = {
      descricao: descricao.trim(),
      valor: signedValue,
      account_id: groupAccountId,
      recorrente
    }
    if (editingId) {
      await fetch(`/api/records/discounts/${editingId}`, {
        method: 'PUT', headers: auth(), body: JSON.stringify(body)
      })
    } else {
      await fetch(`/api/records/${record.id}/discounts`, {
        method: 'POST', headers: auth(), body: JSON.stringify(body)
      })
    }
    resetForm()
    await refresh()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Excluir este lançamento?')) return
    await fetch(`/api/records/discounts/${id}`, { method: 'DELETE', headers: auth() })
    await refresh()
  }

  // Calcula grupos: conta padrão recebe órfãos
  $: defaultAccount = $accountsStore.find(a => a.padrao)
  $: groups = (() => {
    const accs = $accountsStore.filter(a => a.ativa)
    const allDiscounts = record?.discounts || []
    const allSalaries = record?.salaries || []
    const primaryBruto = record?.salario_bruto || 0
    const primaryAccId = record?.salario_account_id || (defaultAccount?.id ?? null)

    const result: any[] = []
    for (const acc of accs) {
      const isPrimaryHere = primaryAccId === acc.id
      const isDefault = acc.padrao

      const salariesHere = allSalaries.filter((s: any) => s.account_id === acc.id)
      const bruto = (isPrimaryHere ? primaryBruto : 0) + salariesHere.reduce((s: number, x: any) => s + (x.valor || 0), 0)

      // discounts: account_id == this OR (default && account_id == null)
      const discountsHere = allDiscounts.filter((d: any) =>
        d.account_id === acc.id || (isDefault && (d.account_id === null || d.account_id === undefined))
      )

      // Mostrar grupo se tem bruto OU descontos
      if (bruto === 0 && discountsHere.length === 0) continue

      const totalDescontos = discountsHere.filter((d: any) => (d.valor || 0) < 0).reduce((s: number, d: any) => s + Math.abs(d.valor || 0), 0)
      const totalCreditos = discountsHere.filter((d: any) => (d.valor || 0) > 0).reduce((s: number, d: any) => s + (d.valor || 0), 0)
      const liquido = bruto + totalCreditos - totalDescontos

      result.push({
        account: acc,
        isPrimaryHere,
        primaryBruto: isPrimaryHere ? primaryBruto : 0,
        extraSalaries: salariesHere,
        discounts: discountsHere,
        bruto,
        totalDescontos,
        totalCreditos,
        liquido
      })
    }
    return result
  })()
</script>

<div class="discounts-grouped">
  <h2 class="section-title">Descontos e Créditos por Conta</h2>

  {#if groups.length === 0}
    <p class="empty">Adicione um salário para começar a registrar descontos.</p>
  {/if}

  {#each groups as g (g.account.id)}
    <div class="group-card" style="border-left: 4px solid {g.account.cor || '#667eea'}">
      <div class="group-header">
        <div class="group-title">
          <span class="acc-icon">{g.account.icone}</span>
          <strong>{g.account.nome}</strong>
          {#if g.isPrimaryHere}<span class="badge">Salário Principal</span>{/if}
        </div>
        <div class="group-totals">
          <span class="t-item"><span class="t-label">Bruto</span> <span class="t-val positive">{fmt(g.bruto)}</span></span>
          {#if g.totalCreditos > 0}
            <span class="t-item"><span class="t-label">+ Créditos</span> <span class="t-val positive">{fmt(g.totalCreditos)}</span></span>
          {/if}
          <span class="t-item"><span class="t-label">− Descontos</span> <span class="t-val negative">{fmt(g.totalDescontos)}</span></span>
          <span class="t-item liquido"><span class="t-label">Líquido</span> <span class="t-val">{fmt(g.liquido)}</span></span>
        </div>
      </div>

      {#if g.extraSalaries.length > 0 || g.isPrimaryHere}
        <div class="salaries-list">
          <span class="sub-label">Entradas:</span>
          {#if g.isPrimaryHere && g.primaryBruto > 0}
            <span class="sal-chip">Salário Bruto: <strong>{fmt(g.primaryBruto)}</strong></span>
          {/if}
          {#each g.extraSalaries as s}
            <span class="sal-chip">{s.descricao}: <strong>{fmt(s.valor)}</strong></span>
          {/each}
        </div>
      {/if}

      <div class="table-wrap">
      <table class="d-table">
        <thead>
          <tr>
            <th>Descrição</th>
            <th class="right">Valor</th>
            <th class="center hide-sm">Rec.</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each g.discounts as d (d.id)}
            {#if editingId === d.id}
              <tr class="edit-row">
                <td><input bind:value={descricao} class="inp" /></td>
                <td>
                  <div class="val-row">
                    <select bind:value={valorTipo} class="inp tipo-sel">
                      <option value="desconto">−</option>
                      <option value="credito">+</option>
                    </select>
                    <input type="number" step="0.01" bind:value={valor} class="inp right" />
                  </div>
                </td>
                <td class="center hide-sm"><input type="checkbox" bind:checked={recorrente} /></td>
                <td class="actions">
                  <button class="btn-save" on:click={() => handleSave(g.account.id)}>✓</button>
                  <button class="btn-cancel" on:click={resetForm}>✕</button>
                </td>
              </tr>
            {:else}
              <tr>
                <td>
                  <div>{d.descricao}</div>
                  {#if d.recorrente}<div class="sub-mobile">🔁 Recorrente</div>{/if}
                </td>
                <td class="right {(d.valor || 0) < 0 ? 'negative' : 'positive'}">
                  {(d.valor || 0) < 0 ? '−' : '+'} {fmt(Math.abs(d.valor || 0))}
                </td>
                <td class="center hide-sm">{d.recorrente ? '✓' : ''}</td>
                <td class="actions">
                  <button class="btn-edit" on:click={() => startEdit(d)} title="Editar">✏️</button>
                  <button class="btn-del" on:click={() => handleDelete(d.id)} title="Excluir">🗑️</button>
                </td>
              </tr>
            {/if}
          {/each}

          {#if addingForAccount === g.account.id}
            <tr class="edit-row">
              <td><input bind:value={descricao} placeholder="ex: INSS, Plano Saúde..." class="inp" /></td>
              <td>
                <div class="val-row">
                  <select bind:value={valorTipo} class="inp tipo-sel">
                    <option value="desconto">−</option>
                    <option value="credito">+</option>
                  </select>
                  <input type="number" step="0.01" placeholder="0,00" bind:value={valor} class="inp right" />
                </div>
              </td>
              <td class="center hide-sm"><input type="checkbox" bind:checked={recorrente} /></td>
              <td class="actions">
                <button class="btn-save" on:click={() => handleSave(g.account.id)}>✓</button>
                <button class="btn-cancel" on:click={resetForm}>✕</button>
              </td>
            </tr>
          {/if}
        </tbody>
      </table>
      </div>

      {#if addingForAccount !== g.account.id && editingId === null}
        <button class="btn-add-row" on:click={() => startAdd(g.account.id)}>+ Adicionar desconto/crédito</button>
      {/if}
    </div>
  {/each}
</div>

<style>
  .discounts-grouped { margin: 1rem 0; }
  .section-title { font-size: 1.1rem; color: #333; margin: 0 0 0.75rem 0; }
  .empty { color: #888; font-size: 0.9rem; padding: 1rem; background: #fafafa; border-radius: 6px; }

  .group-card {
    background: #fff;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }

  .group-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #eee;
  }
  .group-title { display: flex; align-items: center; gap: 0.5rem; font-size: 1rem; }
  .acc-icon { font-size: 1.2rem; }
  .badge { font-size: 0.7rem; background: #667eea; color: #fff; padding: 0.15rem 0.5rem; border-radius: 10px; }

  .group-totals { display: flex; gap: 0.75rem; flex-wrap: wrap; font-size: 0.85rem; }
  .t-item { display: flex; flex-direction: column; align-items: flex-end; }
  .t-label { font-size: 0.7rem; color: #888; text-transform: uppercase; }
  .t-val { font-weight: 600; }
  .t-val.positive { color: #4caf50; }
  .t-val.negative { color: #f44336; }
  .liquido .t-val { color: #667eea; font-size: 1rem; }

  .salaries-list {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.6rem;
    align-items: center;
    font-size: 0.8rem;
  }
  .sub-label { color: #888; font-size: 0.75rem; text-transform: uppercase; }
  .sal-chip { background: #f0f4ff; color: #4a5fc1; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; }

  .d-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .d-table th, .d-table td { padding: 0.45rem 0.5rem; border-bottom: 1px solid #f0f0f0; text-align: left; }
  .d-table th { font-size: 0.75rem; color: #888; text-transform: uppercase; font-weight: 600; }
  .d-table .right { text-align: right; }
  .d-table .center { text-align: center; }
  .d-table .positive { color: #4caf50; font-weight: 500; }
  .d-table .negative { color: #f44336; font-weight: 500; }

  .inp { padding: 0.35rem 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; box-sizing: border-box; width: 100%; }
  .inp.right { text-align: right; }
  .val-row { display: flex; gap: 0.3rem; }
  .tipo-sel { width: 50px; flex-shrink: 0; text-align: center; font-weight: 600; }

  .edit-row { background: #f7f9ff; }
  .actions { white-space: nowrap; text-align: right; }
  .actions button { background: none; border: none; cursor: pointer; padding: 0.25rem 0.4rem; font-size: 0.95rem; border-radius: 3px; }
  .actions button:hover { background: #f0f0f0; }
  .btn-save { color: #4caf50; }
  .btn-cancel { color: #f44336; }

  .btn-add-row {
    margin-top: 0.6rem;
    background: transparent;
    border: 1px dashed #ccc;
    color: #667eea;
    padding: 0.4rem 0.75rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.85rem;
    width: 100%;
  }
  .btn-add-row:hover { background: #f0f4ff; border-color: #667eea; }

  :global([data-theme="dark"]) .section-title { color: #eee; }
  :global([data-theme="dark"]) .empty { background: #1e1e1e; color: #888; }
  :global([data-theme="dark"]) .group-card { background: #1e1e1e; }
  :global([data-theme="dark"]) .group-header { border-color: #333; }
  :global([data-theme="dark"]) .d-table th, :global([data-theme="dark"]) .d-table td { border-color: #2a2a2a; }
  :global([data-theme="dark"]) .d-table th { color: #999; }
  :global([data-theme="dark"]) .inp { background: #2a2a2a; color: #ddd; border-color: #444; }
  :global([data-theme="dark"]) .edit-row { background: #1a2238; }
  :global([data-theme="dark"]) .sal-chip { background: #2a2f4a; color: #b3c0ff; }
  :global([data-theme="dark"]) .actions button:hover { background: #2a2a2a; }
  :global([data-theme="dark"]) .btn-add-row { border-color: #444; color: #99b3ff; }
  :global([data-theme="dark"]) .btn-add-row:hover { background: #1e2a4a; }

  .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; width: 100%; }
  .sub-mobile { display: none; font-size: 0.7rem; color: #888; margin-top: 2px; }
  :global([data-theme="dark"]) .sub-mobile { color: #999; }

  @media (max-width: 640px) {
    .group-card { padding: 0.6rem 0.6rem 0.5rem; }
    .group-header { gap: 0.4rem; }
    .group-totals { gap: 0.5rem; font-size: 0.78rem; }
    .salary-info { padding: 0.4rem 0.5rem; gap: 0.4rem; flex-wrap: wrap; }
    .sal-chip { font-size: 0.72rem; padding: 0.15rem 0.45rem; }
    .hide-sm { display: none !important; }
    .sub-mobile { display: block; }
    .d-table { font-size: 0.85rem; }
    .d-table th, .d-table td { padding: 0.35rem 0.3rem; }
    .actions button { padding: 0.4rem 0.5rem; min-width: 32px; min-height: 32px; }
    .section-title { font-size: 1rem; }
  }
</style>
