<script lang="ts">
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked, fmtCompact } from '../utils/format'

  export let record: any
  export let cardFaturas: any[] = []
  export let investmentSummary: { saldo_total: number, aportes_mes: number, saques_mes: number, rendimentos_mes: number, liquido_mes: number } = {
    saldo_total: 0, aportes_mes: 0, saques_mes: 0, rendimentos_mes: 0, liquido_mes: 0
  }

  $: totalSalariosExtras = (record.salaries || []).reduce((s: number, x: any) => s + (x.valor || 0), 0)
  $: totalReceitas = (record.salario_bruto || 0) + totalSalariosExtras + (record.discounts?.filter((d: any) => d.valor > 0).reduce((sum: number, d: any) => sum + d.valor, 0) || 0)
  $: totalDescontos = record.discounts?.filter((d: any) => d.valor < 0).reduce((sum: number, d: any) => sum + Math.abs(d.valor), 0) || 0
  $: totalCartoes = cardFaturas.reduce((s: number, f: any) => s + (f.total || 0), 0)
  $: totalDebitos = (record.expenses?.filter((e: any) => !e.eh_credito).reduce((sum: number, e: any) => sum + (e.valor || 0), 0) || 0) + totalCartoes
  $: totalCreditos = record.expenses?.filter((e: any) => e.eh_credito).reduce((sum: number, e: any) => sum + (e.valor || 0), 0) || 0
  $: totalDespesas = totalDebitos
  // Saldo total acumulado de todas as contas de investimento
  $: totalInvestimentos = investmentSummary.saldo_total || 0
  // Líquido do mês (aportes - saques) afeta o caixa do mês
  $: liquidoInvestMes = investmentSummary.liquido_mes || 0
  $: saldoFinal = (record.saldo_anterior || 0) + totalReceitas + totalCreditos - totalDescontos - totalDebitos - liquidoInvestMes

  $: formatCurrency = (value: number) => fmtMasked(value, $valuesHidden)
  $: formatCompact = (value: number) => fmtCompact(value, $valuesHidden)
</script>

<div class="summary-cards">
  <div class="card receitas">
    <div class="card-header">
      <h3>Receitas</h3>
    </div>
    <div class="card-value full">{formatCurrency(totalReceitas)}</div>
    <div class="card-value compact">{formatCompact(totalReceitas)}</div>
  </div>

  <div class="card descontos">
    <div class="card-header">
      <h3>Descontos</h3>
    </div>
    <div class="card-value full">{formatCurrency(totalDescontos)}</div>
    <div class="card-value compact">{formatCompact(totalDescontos)}</div>
  </div>

  <div class="card despesas">
    <div class="card-header">
      <h3>Despesas</h3>
    </div>
    <div class="card-value full">{formatCurrency(totalDespesas)}</div>
    <div class="card-value compact">{formatCompact(totalDespesas)}</div>
  </div>

  <div class="card investimentos">
    <div class="card-header">
      <h3>Investimentos</h3>
    </div>
    <div class="card-value full">{formatCurrency(totalInvestimentos)}</div>
    <div class="card-value compact">{formatCompact(totalInvestimentos)}</div>
  </div>

  <div class={`card saldo ${saldoFinal >= 0 ? 'positivo' : 'negativo'}`}>
    <div class="card-header">
      <h3>Saldo Final</h3>
    </div>
    <div class="card-value full">{formatCurrency(saldoFinal)}</div>
    <div class="card-value compact">{formatCompact(saldoFinal)}</div>
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

  /* Padrao: mostra valor completo (R$ X), oculta compacto */
  .card-value.compact { display: none; }

  @media (max-width: 768px) {
    .summary-cards {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.6rem;
      margin: 1rem 0;
    }
    .card { padding: 0.7rem 0.7rem; border-radius: 8px; min-width: 0; overflow: hidden; }
    .card-header { margin-bottom: 0.3rem; }
    .card-header h3 { font-size: 0.68rem; letter-spacing: 0.3px; }

    /* Cards pequenos (Receitas/Descontos/Despesas/Invest): troca para compacto */
    .card:not(.saldo) .card-value.full { display: none; }
    .card:not(.saldo) .card-value.compact {
      display: block;
      font-size: 1.15rem;
      font-weight: 700;
      white-space: nowrap;
    }

    /* Saldo final ocupa linha inteira: mantem valor completo, mas com clamp */
    .card.saldo { grid-column: 1 / -1; }
    .card.saldo .card-value.full {
      font-size: clamp(1.1rem, 5.5vw, 1.5rem);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
  @media (max-width: 360px) {
    .summary-cards { gap: 0.45rem; }
    .card { padding: 0.55rem 0.55rem; }
    .card:not(.saldo) .card-value.compact { font-size: 1rem; }
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
