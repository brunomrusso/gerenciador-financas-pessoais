<script lang="ts">
  export let record: any
  export let cardFaturas: any[] = []

  const fmt = (v: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

  // Usa data LOCAL (não UTC) para evitar bug de fuso à noite
  const toLocalISO = (d: Date) => {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${y}-${m}-${day}`
  }
  const today = new Date()
  const todayStr = toLocalISO(today)
  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - today.getDay())
  const startOfWeekStr = toLocalISO(startOfWeek)

  type Item = { valor: number, data?: string }

  const sumOnDay = (items: Item[], day: string) => items.filter(i => (i.data || '').startsWith(day)).reduce((s, i) => s + (i.valor || 0), 0)
  const sumSince = (items: Item[], since: string) => items.filter(i => (i.data || '') >= since).reduce((s, i) => s + (i.valor || 0), 0)
  const sumAll = (items: Item[]) => items.reduce((s, i) => s + (i.valor || 0), 0)

  $: expensesAll = (record?.expenses || []) as Item[]
  $: cardAll = cardFaturas.flatMap((f: any) => (f.expenses || [])) as Item[]

  $: gastosHoje = sumOnDay(expensesAll, todayStr) + sumOnDay(cardAll, todayStr)
  $: gastosSemana = sumSince(expensesAll, startOfWeekStr) + sumSince(cardAll, startOfWeekStr)
  $: gastosMes = sumAll(expensesAll) + sumAll(cardAll)
  $: numLancamentos = expensesAll.length + cardAll.length

  $: maiorGasto = [...expensesAll, ...cardAll]
    .filter(i => (i.valor || 0) > 0)
    .sort((a, b) => (b.valor || 0) - (a.valor || 0))[0]
</script>

<div class="quickstats">
  <div class="qs-header">
    <span class="qs-icon">⚡</span>
    <h3>Resumo Rápido</h3>
  </div>
  <div class="qs-grid">
    <div class="qs-card today">
      <div class="qs-lbl">Hoje</div>
      <div class="qs-val">{fmt(gastosHoje)}</div>
    </div>
    <div class="qs-card week">
      <div class="qs-lbl">Esta Semana</div>
      <div class="qs-val">{fmt(gastosSemana)}</div>
    </div>
    <div class="qs-card month">
      <div class="qs-lbl">Este Mês</div>
      <div class="qs-val">{fmt(gastosMes)}</div>
    </div>
    <div class="qs-card count">
      <div class="qs-lbl">Lançamentos</div>
      <div class="qs-val">{numLancamentos}</div>
    </div>
    {#if maiorGasto}
      <div class="qs-card biggest">
        <div class="qs-lbl">Maior Gasto</div>
        <div class="qs-val">{fmt(maiorGasto.valor || 0)}</div>
      </div>
    {/if}
  </div>
</div>

<style>
  .quickstats {
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,.1);
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
  }
  .qs-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
  .qs-icon { font-size: 1.2rem; }
  h3 { margin: 0; font-size: 1.05rem; color: #333; }

  .qs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.6rem;
  }
  .qs-card {
    padding: 0.7rem 0.85rem;
    border-radius: 8px;
    background: #f8f9ff;
    border-left: 4px solid #667eea;
    display: flex; flex-direction: column; gap: 4px;
  }
  .qs-card.today { border-left-color: #f44336; }
  .qs-card.week  { border-left-color: #ff9800; }
  .qs-card.month { border-left-color: #2196f3; }
  .qs-card.count { border-left-color: #9c27b0; }
  .qs-card.biggest { border-left-color: #4caf50; }

  .qs-lbl { font-size: 0.7rem; color: #777; text-transform: uppercase; font-weight: 600; letter-spacing: 0.3px; }
  .qs-val { font-size: 1.05rem; font-weight: 700; color: #333; }

  @media (max-width: 640px) {
    .quickstats { padding: 0.75rem; }
    .qs-grid { grid-template-columns: 1fr 1fr; }
    .qs-val { font-size: 0.95rem; }
  }
</style>
