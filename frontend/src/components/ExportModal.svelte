<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { valuesHidden } from '../stores/privacy'

  export let record: any
  export let cardFaturas: any[] = []
  export let selectedMonth: string = ''
  export let selectedYear: number = new Date().getFullYear()

  const dispatch = createEventDispatcher()
  const close = () => dispatch('close')

  const fmt = (v: number) =>
    $valuesHidden ? '****' : v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  $: expenses    = record?.expenses    || []
  $: discounts   = record?.discounts   || []
  $: salaries    = record?.salaries    || []
  $: transfers   = record?.transfers   || []
  $: totalExpenses   = expenses.reduce((s: number, e: any) => s + (e.valor || 0), 0)
  $: totalDiscounts  = discounts.reduce((s: number, d: any) => s + (d.valor || 0), 0)
  $: totalSalaries   = salaries.reduce((s: number, x: any) => s + (x.valor || 0), 0)
  $: totalCardExp    = cardFaturas.reduce((s: number, f: any) =>
      s + (f.expenses || []).reduce((fs: number, e: any) => fs + (e.valor || 0), 0), 0)
  $: byCat = expenses.reduce((m: Record<string, number>, e: any) => {
    const k = e.categoria || 'Outros'
    m[k] = (m[k] || 0) + (e.valor || 0)
    return m
  }, {} as Record<string, number>)
  $: byCatEntries = (Object.entries(byCat) as [string, number][]).sort((a, b) => b[1] - a[1])
  $: totalIn  = (record?.salario_bruto || 0) + totalSalaries + totalDiscounts
  $: totalOut = totalExpenses + totalCardExp
  $: saldoFinal = (record?.saldo_anterior || 0) + totalIn - totalOut

  // ── CSV Export ────────────────────────────────────────────
  function escCsv(v: any) {
    const s = String(v ?? '')
    return s.includes(',') || s.includes('"') || s.includes('\n')
      ? `"${s.replace(/"/g, '""')}"`
      : s
  }

  function buildCsv(): string {
    const rows: string[] = []
    const sep = ','
    const title = `${selectedMonth} ${selectedYear}`

    rows.push(`CashFlow - Relatório Mensal - ${title}`)
    rows.push('')

    rows.push('=== RESUMO ===')
    rows.push(`Saldo Anterior${sep}${(record?.saldo_anterior || 0).toFixed(2)}`)
    rows.push(`Salário Bruto${sep}${(record?.salario_bruto || 0).toFixed(2)}`)
    rows.push(`Outros Salários${sep}${totalSalaries.toFixed(2)}`)
    rows.push(`Outros Créditos${sep}${totalDiscounts.toFixed(2)}`)
    rows.push(`Total Despesas${sep}${totalExpenses.toFixed(2)}`)
    rows.push(`Total Cartão${sep}${totalCardExp.toFixed(2)}`)
    rows.push(`Saldo Final${sep}${saldoFinal.toFixed(2)}`)
    rows.push('')

    if (expenses.length) {
      rows.push('=== DESPESAS ===')
      rows.push(['Descrição','Categoria','Data','Valor'].map(escCsv).join(sep))
      expenses.forEach((e: any) => {
        rows.push([e.descricao, e.categoria || 'Outros', e.data || '', (e.valor || 0).toFixed(2)].map(escCsv).join(sep))
      })
      rows.push('')
    }

    if (cardFaturas.length) {
      rows.push('=== CARTÃO DE CRÉDITO ===')
      rows.push(['Cartão','Descrição','Categoria','Data','Parcela','Valor'].map(escCsv).join(sep))
      cardFaturas.forEach((f: any) => {
        ;(f.expenses || []).forEach((e: any) => {
          const parc = e.parcelas_total > 1 ? `${e.parcela_atual}/${e.parcelas_total}` : '1/1'
          rows.push([f.nome || f.card_nome || 'Cartão', e.descricao, e.categoria || 'Outros', e.data || '', parc, (e.valor || 0).toFixed(2)].map(escCsv).join(sep))
        })
      })
      rows.push('')
    }

    if (discounts.length) {
      rows.push('=== OUTROS CRÉDITOS / DESCONTOS ===')
      rows.push(['Descrição','Valor'].map(escCsv).join(sep))
      discounts.forEach((d: any) => {
        rows.push([d.descricao, (d.valor || 0).toFixed(2)].map(escCsv).join(sep))
      })
      rows.push('')
    }

    if (transfers.length) {
      rows.push('=== TRANSFERÊNCIAS ===')
      rows.push(['Descrição','Valor','Data'].map(escCsv).join(sep))
      transfers.forEach((t: any) => {
        rows.push([t.descricao, (t.valor || 0).toFixed(2), t.data || ''].map(escCsv).join(sep))
      })
    }

    return rows.join('\n')
  }

  function downloadCsv() {
    const csv = buildCsv()
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cashflow-${selectedMonth}-${selectedYear}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  function printReport() {
    window.print()
  }
</script>

<div class="exp-overlay" on:click|self={close} on:keydown={(e) => e.key === 'Escape' && close()} role="dialog" aria-modal="true">
  <div class="exp-modal">
    <div class="exp-header">
      <div>
        <h2>📊 Relatório — {selectedMonth} {selectedYear}</h2>
        <p class="exp-sub">Exportar ou imprimir os dados do mês</p>
      </div>
      <button class="exp-close" on:click={close}>✕</button>
    </div>

    <div class="exp-body">
      <!-- Summary cards -->
      <div class="sum-grid">
        <div class="sum-card income">
          <span class="sum-lbl">Total Entradas</span>
          <span class="sum-val">R$ {fmt(totalIn + (record?.saldo_anterior || 0))}</span>
        </div>
        <div class="sum-card expense">
          <span class="sum-lbl">Total Saídas</span>
          <span class="sum-val">R$ {fmt(totalOut)}</span>
        </div>
        <div class="sum-card balance" class:negative={saldoFinal < 0}>
          <span class="sum-lbl">Saldo Final</span>
          <span class="sum-val">R$ {fmt(saldoFinal)}</span>
        </div>
      </div>

      <!-- Details -->
      <div class="det-grid">
        <div class="det-row">
          <span>Saldo anterior</span>
          <span>R$ {fmt(record?.saldo_anterior || 0)}</span>
        </div>
        <div class="det-row">
          <span>Salário bruto</span>
          <span>R$ {fmt(record?.salario_bruto || 0)}</span>
        </div>
        {#if totalSalaries > 0}
        <div class="det-row">
          <span>Outros salários</span>
          <span>R$ {fmt(totalSalaries)}</span>
        </div>
        {/if}
        {#if totalDiscounts > 0}
        <div class="det-row">
          <span>Outros créditos</span>
          <span>R$ {fmt(totalDiscounts)}</span>
        </div>
        {/if}
        <div class="det-divider"></div>
        <div class="det-row">
          <span>Despesas ({expenses.length})</span>
          <span class="neg">− R$ {fmt(totalExpenses)}</span>
        </div>
        {#if totalCardExp > 0}
        <div class="det-row">
          <span>Cartão ({cardFaturas.reduce((s, f) => s + (f.expenses?.length || 0), 0)} lançamentos)</span>
          <span class="neg">− R$ {fmt(totalCardExp)}</span>
        </div>
        {/if}
      </div>

      <!-- Expense breakdown by category -->
      {#if expenses.length > 0}
        <div class="cat-section">
          <h4>Por categoria</h4>
          <div class="cat-bars">
            {#each byCatEntries as [cat, val]}
              <div class="cat-bar-row">
                <span class="cat-name">{cat}</span>
                <div class="cat-bar-bg">
                  <div class="cat-bar-fill" style="width:{Math.min(100, (val/totalExpenses)*100).toFixed(0)}%"></div>
                </div>
                <span class="cat-val">R$ {fmt(val)}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <div class="exp-footer">
      <button class="btn-cancel" on:click={close}>Fechar</button>
      <button class="btn-csv" on:click={downloadCsv}>
        📥 Baixar CSV (Excel)
      </button>
      <button class="btn-print" on:click={printReport}>
        🖨️ Imprimir / PDF
      </button>
    </div>
  </div>
</div>

<style>
  .exp-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.55);
    z-index: 1100;
    display: flex; align-items: center; justify-content: center;
    padding: 1rem;
  }

  .exp-modal {
    background: white;
    border-radius: 14px;
    width: 100%; max-width: 560px;
    max-height: 90vh;
    display: flex; flex-direction: column;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
  }

  .exp-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    padding: 1.1rem 1.25rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  .exp-header h2 { margin: 0; font-size: 1.05rem; }
  .exp-sub { margin: 3px 0 0; font-size: 0.8rem; opacity: 0.85; }
  .exp-close {
    background: rgba(255,255,255,0.2); border: none;
    color: white; font-size: 1.1rem;
    width: 30px; height: 30px; border-radius: 8px; cursor: pointer;
    flex-shrink: 0;
  }
  .exp-close:hover { background: rgba(255,255,255,0.35); }

  .exp-body {
    flex: 1; overflow-y: auto;
    padding: 1.25rem;
    display: flex; flex-direction: column; gap: 1rem;
  }

  .sum-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.6rem;
  }
  @media (max-width: 480px) { .sum-grid { grid-template-columns: 1fr; } }

  .sum-card {
    padding: 0.75rem;
    border-radius: 10px;
    display: flex; flex-direction: column; gap: 3px;
  }
  .sum-card.income  { background: #f0faf0; border: 1px solid #c8e6c9; }
  .sum-card.expense { background: #fff5f5; border: 1px solid #ffcdd2; }
  .sum-card.balance { background: #f0f4ff; border: 1px solid #c5cae9; }
  .sum-card.balance.negative { background: #fff5f5; border-color: #ffcdd2; }
  .sum-lbl { font-size: 0.72rem; color: #666; }
  .sum-val { font-size: 0.95rem; font-weight: 700; color: #333; }
  .sum-card.expense .sum-val { color: #c62828; }
  .sum-card.balance.negative .sum-val { color: #c62828; }
  .sum-card.income .sum-val { color: #2e7d32; }

  .det-grid {
    background: #fafbfc;
    border: 1px solid #eef0f5;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    display: flex; flex-direction: column; gap: 0.4rem;
  }
  .det-row {
    display: flex; justify-content: space-between;
    font-size: 0.88rem; color: #444;
  }
  .det-divider { border-top: 1px dashed #ddd; margin: 0.25rem 0; }
  .neg { color: #c62828; }

  .cat-section h4 { margin: 0 0 0.6rem; font-size: 0.88rem; color: #555; }
  .cat-bars { display: flex; flex-direction: column; gap: 0.45rem; }
  .cat-bar-row {
    display: grid; grid-template-columns: 110px 1fr 80px;
    gap: 0.5rem; align-items: center;
  }
  .cat-name { font-size: 0.78rem; color: #444; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cat-bar-bg { background: #eef0f5; border-radius: 4px; height: 8px; overflow: hidden; }
  .cat-bar-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 4px; transition: width 0.4s; }
  .cat-val { font-size: 0.78rem; color: #444; text-align: right; }

  .exp-footer {
    display: flex; gap: 0.5rem;
    padding: 0.85rem 1.25rem;
    border-top: 1px solid #eee;
    background: #fafbfc;
    flex-wrap: wrap;
  }
  .btn-cancel {
    padding: 0.55rem 0.85rem;
    border: 1px solid #ddd; background: none;
    color: #777; border-radius: 8px;
    cursor: pointer; font-size: 0.85rem;
  }
  .btn-csv {
    flex: 1;
    padding: 0.55rem;
    background: #e8f5e9; color: #2e7d32;
    border: 1px solid #a5d6a7; border-radius: 8px;
    cursor: pointer; font-weight: 600; font-size: 0.88rem;
    transition: background 0.15s;
  }
  .btn-csv:hover { background: #c8e6c9; }
  .btn-print {
    flex: 1;
    padding: 0.55rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none; border-radius: 8px;
    cursor: pointer; font-weight: 600; font-size: 0.88rem;
    transition: opacity 0.15s;
  }
  .btn-print:hover { opacity: 0.9; }

  @media print {
    :global(.dashboard-header),
    :global(.month-selector),
    :global(.summary-cards),
    :global(.tabs) { display: none !important; }
    .exp-overlay { position: static; background: none; padding: 0; }
    .exp-modal { max-height: none; box-shadow: none; border-radius: 0; }
    .exp-header { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
    .exp-footer { display: none; }
  }

  /* Dark mode */
  :global([data-theme="dark"]) .exp-modal { background: #1e1e2e; }
  :global([data-theme="dark"]) .det-grid { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .det-row { color: #c0c0d0; }
  :global([data-theme="dark"]) .det-divider { border-color: #3a3a52; }
  :global([data-theme="dark"]) .sum-card.income  { background: #1a2e1a; border-color: #2e4a2e; }
  :global([data-theme="dark"]) .sum-card.expense { background: #2e1a1a; border-color: #4a2e2e; }
  :global([data-theme="dark"]) .sum-card.balance { background: #1a1e2e; border-color: #3a3a52; }
  :global([data-theme="dark"]) .sum-lbl { color: #9090a8; }
  :global([data-theme="dark"]) .sum-val { color: #e0e0e8; }
  :global([data-theme="dark"]) .sum-card.income .sum-val  { color: #81c784; }
  :global([data-theme="dark"]) .sum-card.expense .sum-val { color: #ef9a9a; }
  :global([data-theme="dark"]) .cat-section h4 { color: #9090a8; }
  :global([data-theme="dark"]) .cat-name { color: #c0c0d0; }
  :global([data-theme="dark"]) .cat-bar-bg { background: #2a2a3e; }
  :global([data-theme="dark"]) .cat-val { color: #c0c0d0; }
  :global([data-theme="dark"]) .exp-footer { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .btn-cancel { border-color: #3a3a52; color: #9090a8; }
  :global([data-theme="dark"]) .btn-csv { background: #1a2e1a; color: #81c784; border-color: #2e4a2e; }
  :global([data-theme="dark"]) .btn-csv:hover { background: #1e3a1e; }
</style>
