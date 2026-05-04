<script lang="ts">
  import { onMount } from 'svelte'
  import Chart from 'chart.js/auto'

  export let month: string
  export let year: number

  let chartContainer: HTMLCanvasElement
  let chart: Chart | null = null

  onMount(async () => {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/records/history?month=${month}&year=${year}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) return

    const data = await response.json()

    const ctx = chartContainer.getContext('2d')
    if (!ctx) return

    if (chart) {
      chart.destroy()
    }

    chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map((d: any) => d.mes),
        datasets: [
          {
            label: 'Receitas',
            data: data.map((d: any) => d.salarioBruto + d.totalCreditos),
            backgroundColor: '#4caf50'
          },
          {
            label: 'Despesas',
            data: data.map((d: any) => d.despesas),
            backgroundColor: '#ff9800'
          },
          {
            label: 'Investimentos',
            data: data.map((d: any) => d.totalInvestido),
            backgroundColor: '#9c27b0'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'top'
          },
          title: {
            display: true,
            text: 'Histórico de 6 Meses'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  })
</script>

<div class="history-chart">
  <canvas bind:this={chartContainer}></canvas>
</div>

<style>
  .history-chart {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
</style>
