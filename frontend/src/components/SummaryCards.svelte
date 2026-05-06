<script lang="ts">
  export let record: any
  export let cardFaturas: any[] = []
  export let investmentSummary: { saldo_total: number, aportes_mes: number, saques_mes: number, rendimentos_mes: number, liquido_mes: number } = {
    saldo_total: 0, aportes_mes: 0, saques_mes: 0, rendimentos_mes: 0, liquido_mes: 0
  }

  $: totalReceitas = (record.salario_bruto || 0) + (record.discounts?.filter((d: any) => d.valor > 0).reduce((sum: number, d: any) => sum + d.valor, 0) || 0)
  $: totalDescontos = record.discounts?.filter((d: any) => d.valor < 0).reduce((sum: number, d: any) => sum + Math.abs(d.valor), 0) || 0
  $: totalCartoes = cardFaturas.reduce((s: number, f: any) => s + (f.total || 0), 0)
  $: totalDespesas = (record.expenses?.reduce((sum: number, e: any) => sum + e.valor, 0) || 0) + totalCartoes
  // Saldo total acumulado de todas as contas de investimento
  $: totalInvestimentos = investmentSummary.saldo_total || 0
  // Líquido do mês (aportes - saques) afeta o caixa do mês
  $: liquidoInvestMes = investmentSummary.liquido_mes || 0
  $: saldoFinal = (record.saldo_anterior || 0) + totalReceitas - totalDescontos - totalDespesas - liquidoInvestMes

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }
</script>

<div class="summary-cards">
  <div class="card receitas">
    <div class="card-header">
      <h3>Receitas</h3>
    </div>
    <div class="card-value">{formatCurrency(totalReceitas)}</div>
  </div>

  <div class="card descontos">
    <div class="card-header">
      <h3>Descontos</h3>
    </div>
    <div class="card-value">{formatCurrency(totalDescontos)}</div>
  </div>

  <div class="card despesas">
    <div class="card-header">
      <h3>Despesas</h3>
    </div>
    <div class="card-value">{formatCurrency(totalDespesas)}</div>
  </div>

  <div class="card investimentos">
    <div class="card-header">
      <h3>Investimentos</h3>
    </div>
    <div class="card-value">{formatCurrency(totalInvestimentos)}</div>
  </div>

  <div class={`card saldo ${saldoFinal >= 0 ? 'positivo' : 'negativo'}`}>
    <div class="card-header">
      <h3>Saldo Final</h3>
    </div>
    <div class="card-value">{formatCurrency(saldoFinal)}</div>
  </div>
</div>

<style>
  .summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
  }

  .card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s, box-shadow 0.3s;
  }

  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  }

  .card-header {
    margin-bottom: 1rem;
  }

  .card-header h3 {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .card-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #333;
  }

  .receitas {
    border-left: 4px solid #4caf50;
  }

  .descontos {
    border-left: 4px solid #2196f3;
  }

  .despesas {
    border-left: 4px solid #ff9800;
  }

  .investimentos {
    border-left: 4px solid #9c27b0;
  }

  .saldo {
    border-left: 4px solid #667eea;
  }

  .saldo.positivo .card-value {
    color: #4caf50;
  }

  .saldo.negativo .card-value {
    color: #f44336;
  }
</style>
