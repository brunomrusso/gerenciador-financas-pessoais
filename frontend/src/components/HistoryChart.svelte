<script lang="ts">
  import { onMount } from 'svelte'
  import Chart from 'chart.js/auto'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'
  import { accountsStore } from '../stores/accounts'

  export let month: string
  export let year: number

  let chartContainer: HTMLCanvasElement
  let chart: Chart | null = null
  let pizzaCanvas: HTMLCanvasElement
  let pizzaChart: Chart | null = null
  let patrimonioCanvas: HTMLCanvasElement
  let patrimonioChart: Chart | null = null

  let range: 3 | 6 | 12 = 6
  let chartType: 'line' | 'bar' = 'line'
  let data: any[] = []
  let categorias: { categoria: string, total: number }[] = []
  let loading = false

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)

  const loadData = async () => {
    loading = true
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/records/history?month=${month}&year=${year}&months=${range}&detailed=1`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!response.ok) return
      const payload = await response.json()
      data = payload.historico || []
      categorias = payload.gastosPorCategoria || []
      renderChart()
      renderPizza()
      renderPatrimonio()
    } finally {
      loading = false
    }
  }

  const renderChart = () => {
    if (!chartContainer) return
    const ctx = chartContainer.getContext('2d')
    if (!ctx) return
    if (chart) chart.destroy()

    const labels = data.map((d: any) => d.mes)
    const receitas = data.map((d: any) => d.receitas || 0)
    const despesas = data.map((d: any) => (d.despesas || 0) + (d.despesasCartao || 0))
    const saldo = data.map((d: any) => d.saldoFinal || 0)

    const datasets: any[] = [
      {
        label: 'Receitas',
        data: receitas,
        borderColor: '#4caf50',
        backgroundColor: chartType === 'bar' ? '#4caf50' : 'rgba(76, 175, 80, 0.15)',
        fill: chartType === 'line',
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Despesas',
        data: despesas,
        borderColor: '#f44336',
        backgroundColor: chartType === 'bar' ? '#f44336' : 'rgba(244, 67, 54, 0.15)',
        fill: chartType === 'line',
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Saldo Final',
        data: saldo,
        borderColor: '#667eea',
        backgroundColor: chartType === 'bar' ? '#667eea' : 'rgba(102, 126, 234, 0.2)',
        fill: chartType === 'line',
        tension: 0.35,
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7
      }
    ]

    chart = new Chart(ctx, {
      type: chartType,
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: { label: (ctx: any) => `${ctx.dataset.label}: ${fmt(ctx.parsed.y)}` }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            ticks: { callback: (v: any) => fmt(Number(v)) }
          }
        }
      }
    })
  }

  const renderPizza = () => {
    if (!pizzaCanvas) return
    if (pizzaChart) pizzaChart.destroy()
    if (categorias.length === 0) return
    const top = categorias.slice(0, 8)
    const outros = categorias.slice(8).reduce((s, c) => s + c.total, 0)
    const labels = top.map(c => c.categoria)
    const values = top.map(c => c.total)
    if (outros > 0) { labels.push('Outros'); values.push(outros) }
    const colors = ['#667eea','#764ba2','#f44336','#ff9800','#4caf50','#2196f3','#9c27b0','#607d8b','#795548']
    pizzaChart = new Chart(pizzaCanvas, {
      type: 'doughnut',
      data: { labels, datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length), borderWidth: 2 }] },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } },
          tooltip: { callbacks: { label: (ctx: any) => `${ctx.label}: ${fmt(ctx.parsed)}` } }
        }
      }
    })
  }

  const renderPatrimonio = () => {
    if (!patrimonioCanvas) return
    if (patrimonioChart) patrimonioChart.destroy()
    if (data.length === 0) return
    const labels = data.map((d: any) => d.mes)
    const saldoContas = data.map((d: any) => d.saldoFinal || 0)
    const invest = data.map((d: any) => d.saldoInvestimentos || 0)
    const patrimonio = data.map((d: any) => d.patrimonio || 0)
    patrimonioChart = new Chart(patrimonioCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Saldo em Contas', data: saldoContas, borderColor: '#667eea', backgroundColor: 'rgba(102,126,234,0.15)', fill: true, tension: 0.35 },
          { label: 'Investimentos', data: invest, borderColor: '#4caf50', backgroundColor: 'rgba(76,175,80,0.15)', fill: true, tension: 0.35 },
          { label: 'Patrimônio Total', data: patrimonio, borderColor: '#9c27b0', backgroundColor: 'transparent', borderWidth: 3, tension: 0.35, pointRadius: 5 }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top' },
          tooltip: { callbacks: { label: (ctx: any) => `${ctx.dataset.label}: ${fmt(ctx.parsed.y)}` } }
        },
        scales: { y: { ticks: { callback: (v: any) => fmt(Number(v)) } } }
      }
    })
  }

  $: if (month && year && range && chartType) {
    loadData()
  }

  onMount(() => loadData())

  $: melhorMes = data.length ? data.reduce((a, b) => (a.saldoFinal > b.saldoFinal ? a : b)) : null
  $: piorMes = data.length ? data.reduce((a, b) => (a.saldoFinal < b.saldoFinal ? a : b)) : null
  $: mediaReceitas = data.length ? data.reduce((s, d) => s + (d.receitas || 0), 0) / data.length : 0
  $: mediaDespesas = data.length ? data.reduce((s, d) => s + (d.despesas || 0) + (d.despesasCartao || 0), 0) / data.length : 0
  $: totalReceitas = data.reduce((s, d) => s + (d.receitas || 0), 0)
  $: totalDespesas = data.reduce((s, d) => s + (d.despesas || 0) + (d.despesasCartao || 0), 0)
  $: totalEconomizado = totalReceitas - totalDespesas
  $: taxaPoupanca = totalReceitas > 0 ? ((totalReceitas - totalDespesas) / totalReceitas * 100) : 0
  $: comprometimento = totalReceitas > 0 ? (totalDespesas / totalReceitas * 100) : 0
  $: burnRate = mediaDespesas
  $: saldoAtualContas = $accountsStore.reduce((s, a: any) => s + (a.saldo || 0), 0)
  $: runwayMeses = burnRate > 0 ? (saldoAtualContas / burnRate) : 0
  $: patrimonioInicio = data.length ? (data[0].patrimonio || 0) : 0
  $: patrimonioFim = data.length ? (data[data.length - 1].patrimonio || 0) : 0
  $: variacaoPatrimonio = patrimonioInicio !== 0 ? ((patrimonioFim - patrimonioInicio) / Math.abs(patrimonioInicio) * 100) : 0
  $: topCategoria = categorias[0] || null
</script>

<div class="history-chart">
  <div class="hc-header">
    <h3>📊 Painel de Indicadores</h3>
    <div class="hc-controls">
      <div class="seg">
        <button class:active={range === 3} on:click={() => range = 3}>3m</button>
        <button class:active={range === 6} on:click={() => range = 6}>6m</button>
        <button class:active={range === 12} on:click={() => range = 12}>12m</button>
      </div>
      <div class="seg">
        <button class:active={chartType === 'line'} on:click={() => chartType = 'line'} title="Linha">📈</button>
        <button class:active={chartType === 'bar'} on:click={() => chartType = 'bar'} title="Barras">📊</button>
      </div>
    </div>
  </div>

  {#if data.length > 0}
    <div class="kpi-grid">
      <div class="kpi" class:pos={taxaPoupanca >= 20} class:warn={taxaPoupanca < 20 && taxaPoupanca >= 0} class:neg={taxaPoupanca < 0}>
        <span class="kpi-lbl">Taxa de Poupança</span>
        <span class="kpi-val">{taxaPoupanca.toFixed(1)}%</span>
        <span class="kpi-hint">{fmt(totalEconomizado)} no período</span>
      </div>
      <div class="kpi" class:pos={comprometimento <= 70} class:warn={comprometimento > 70 && comprometimento <= 90} class:neg={comprometimento > 90}>
        <span class="kpi-lbl">Comprometimento</span>
        <span class="kpi-val">{comprometimento.toFixed(1)}%</span>
        <span class="kpi-hint">da renda em despesas</span>
      </div>
      <div class="kpi">
        <span class="kpi-lbl">Burn Rate</span>
        <span class="kpi-val">{fmt(burnRate)}</span>
        <span class="kpi-hint">despesa média / mês</span>
      </div>
      <div class="kpi" class:pos={runwayMeses >= 6} class:warn={runwayMeses >= 3 && runwayMeses < 6} class:neg={runwayMeses < 3 && runwayMeses > 0}>
        <span class="kpi-lbl">Runway</span>
        <span class="kpi-val">{runwayMeses > 0 ? `${runwayMeses.toFixed(1)}m` : '—'}</span>
        <span class="kpi-hint">com saldo atual</span>
      </div>
      <div class="kpi" class:pos={variacaoPatrimonio >= 0} class:neg={variacaoPatrimonio < 0}>
        <span class="kpi-lbl">Variação Patrimônio</span>
        <span class="kpi-val">{variacaoPatrimonio >= 0 ? '+' : ''}{variacaoPatrimonio.toFixed(1)}%</span>
        <span class="kpi-hint">{fmt(patrimonioInicio)} → {fmt(patrimonioFim)}</span>
      </div>
      <div class="kpi" class:pos={totalEconomizado >= 0} class:neg={totalEconomizado < 0}>
        <span class="kpi-lbl">Total Economizado</span>
        <span class="kpi-val">{fmt(totalEconomizado)}</span>
        <span class="kpi-hint">{data.length} {data.length === 1 ? 'mês' : 'meses'}</span>
      </div>
    </div>
  {/if}

  <div class="chart-block">
    <h4>Receitas, Despesas e Saldo</h4>
    <div class="chart-wrap">
      <canvas bind:this={chartContainer}></canvas>
    </div>
  </div>

  {#if data.length > 0}
    <div class="two-cols">
      <div class="chart-block">
        <h4>Patrimônio Acumulado</h4>
        <div class="chart-wrap small">
          <canvas bind:this={patrimonioCanvas}></canvas>
        </div>
      </div>
      <div class="chart-block">
        <h4>Gastos por Categoria <span class="sub">({data.length} {data.length === 1 ? 'mês' : 'meses'})</span></h4>
        <div class="chart-wrap small">
          {#if categorias.length === 0}
            <p class="empty">Sem gastos no período.</p>
          {:else}
            <canvas bind:this={pizzaCanvas}></canvas>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  {#if data.length > 0}
    <div class="hc-stats">
      <div class="stat-box">
        <span class="stat-lbl">Média Receitas</span>
        <span class="stat-val pos">{fmt(mediaReceitas)}</span>
      </div>
      <div class="stat-box">
        <span class="stat-lbl">Média Despesas</span>
        <span class="stat-val neg">{fmt(mediaDespesas)}</span>
      </div>
      {#if melhorMes}
        <div class="stat-box">
          <span class="stat-lbl">Melhor mês</span>
          <span class="stat-val pos">{melhorMes.mes} ({fmt(melhorMes.saldoFinal)})</span>
        </div>
      {/if}
      {#if piorMes}
        <div class="stat-box">
          <span class="stat-lbl">Pior mês</span>
          <span class="stat-val neg">{piorMes.mes} ({fmt(piorMes.saldoFinal)})</span>
        </div>
      {/if}
      {#if topCategoria}
        <div class="stat-box">
          <span class="stat-lbl">Maior gasto (categoria)</span>
          <span class="stat-val neg">{topCategoria.categoria} ({fmt(topCategoria.total)})</span>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .history-chart {
    background: white;
    padding: 1.25rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  .hc-header { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
  h3 { margin: 0; color: #333; font-size: 1.05rem; }
  .hc-controls { display: flex; gap: 0.5rem; flex-wrap: wrap; }
  .seg { display: flex; background: #f0f0f0; border-radius: 6px; overflow: hidden; }
  .seg button { background: none; border: none; padding: 0.4rem 0.7rem; cursor: pointer; font-size: 0.8rem; color: #666; }
  .seg button.active { background: #667eea; color: white; font-weight: 600; }
  .chart-wrap { position: relative; height: 320px; }

  .hc-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; margin-top: 1rem; }
  .stat-box { background: #f8f9ff; padding: 0.5rem 0.75rem; border-radius: 6px; display: flex; flex-direction: column; gap: 2px; }
  .stat-lbl { font-size: 0.7rem; color: #777; text-transform: uppercase; font-weight: 600; }
  .stat-val { font-size: 0.9rem; font-weight: 700; }
  .stat-val.pos { color: #4caf50; }
  .stat-val.neg { color: #f44336; }

  /* KPIs */
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.6rem; margin: 1rem 0; }
  .kpi {
    background: #fafbff;
    border-left: 3px solid #667eea;
    padding: 0.6rem 0.8rem;
    border-radius: 6px;
    display: flex; flex-direction: column; gap: 2px;
  }
  .kpi.pos { border-left-color: #4caf50; }
  .kpi.neg { border-left-color: #f44336; background: #fff5f5; }
  .kpi.warn { border-left-color: #ff9800; }
  .kpi-lbl { font-size: 0.7rem; color: #777; text-transform: uppercase; font-weight: 600; letter-spacing: 0.3px; }
  .kpi-val { font-size: 1.15rem; font-weight: 700; color: #333; }
  .kpi.pos .kpi-val { color: #4caf50; }
  .kpi.neg .kpi-val { color: #f44336; }
  .kpi.warn .kpi-val { color: #f57c00; }
  .kpi-hint { font-size: 0.7rem; color: #999; }

  /* Chart blocks */
  .chart-block { margin-top: 1rem; }
  .chart-block h4 { margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #555; font-weight: 600; }
  .chart-block .sub { font-size: 0.75rem; color: #999; font-weight: 400; }
  .chart-wrap.small { height: 260px; }
  .two-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .empty { text-align: center; padding: 2rem; color: #999; font-style: italic; }

  :global([data-theme="dark"]) .history-chart { background: #1e1e1e; }
  :global([data-theme="dark"]) h3, :global([data-theme="dark"]) .chart-block h4 { color: #ddd; }
  :global([data-theme="dark"]) .kpi { background: #2a2a2a; }
  :global([data-theme="dark"]) .kpi.neg { background: #3a1f1f; }
  :global([data-theme="dark"]) .kpi-val { color: #eee; }
  :global([data-theme="dark"]) .kpi-lbl, :global([data-theme="dark"]) .kpi-hint { color: #aaa; }
  :global([data-theme="dark"]) .stat-box { background: #2a2a2a; }
  :global([data-theme="dark"]) .stat-lbl { color: #aaa; }
  :global([data-theme="dark"]) .seg { background: #2a2a2a; }
  :global([data-theme="dark"]) .seg button { color: #aaa; }

  @media (max-width: 640px) {
    .chart-wrap { height: 260px; }
    .chart-wrap.small { height: 230px; }
    .hc-controls { width: 100%; justify-content: flex-start; }
    .kpi-val { font-size: 1rem; }
  }
</style>
