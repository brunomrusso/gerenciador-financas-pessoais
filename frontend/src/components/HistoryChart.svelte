<script lang="ts">
  import { onMount } from 'svelte'
  import Chart from 'chart.js/auto'

  export let month: string
  export let year: number

  let chartContainer: HTMLCanvasElement
  let chart: Chart | null = null
  let range: 3 | 6 | 12 = 6
  let chartType: 'line' | 'bar' = 'line'
  let data: any[] = []
  let loading = false

  const fmt = (v: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

  const loadData = async () => {
    loading = true
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/records/history?month=${month}&year=${year}&months=${range}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!response.ok) return
      data = await response.json()
      renderChart()
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

  $: if (month && year && range && chartType) {
    loadData()
  }

  onMount(() => loadData())

  $: melhorMes = data.length ? data.reduce((a, b) => (a.saldoFinal > b.saldoFinal ? a : b)) : null
  $: piorMes = data.length ? data.reduce((a, b) => (a.saldoFinal < b.saldoFinal ? a : b)) : null
  $: mediaReceitas = data.length ? data.reduce((s, d) => s + (d.receitas || 0), 0) / data.length : 0
  $: mediaDespesas = data.length ? data.reduce((s, d) => s + (d.despesas || 0) + (d.despesasCartao || 0), 0) / data.length : 0
</script>

<div class="history-chart">
  <div class="hc-header">
    <h3>Comparação entre meses</h3>
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

  <div class="chart-wrap">
    <canvas bind:this={chartContainer}></canvas>
  </div>

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

  @media (max-width: 640px) {
    .chart-wrap { height: 260px; }
    .hc-controls { width: 100%; justify-content: flex-start; }
  }
</style>
