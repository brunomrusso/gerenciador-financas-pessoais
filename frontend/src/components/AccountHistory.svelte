<script lang="ts">
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let accountId: number
  export let accountName: string = ''
  export let onClose: () => void = () => {}

  let events: any[] = []
  let loading = true
  let error = ''
  let filterType = ''
  let search = ''

  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)
  const auth = () => ({ Authorization: `Bearer ${localStorage.getItem('token')}` })

  const TYPE_LABELS: Record<string, { label: string; icon: string; class: string }> = {
    initial_balance:   { label: 'Saldo inicial', icon: '🏁', class: 'neutral' },
    salary_primary:    { label: 'Salário',       icon: '💼', class: 'income' },
    salary_extra:      { label: 'Salário extra', icon: '💼', class: 'income' },
    credit_misc:       { label: 'Crédito',       icon: '➕', class: 'income' },
    discount:          { label: 'Desconto',      icon: '➖', class: 'expense' },
    expense:           { label: 'Despesa',       icon: '🛒', class: 'expense' },
    expense_credit:    { label: 'Reembolso',     icon: '↩️', class: 'income' },
    transfer_in:       { label: 'Transf. recebida', icon: '⬇️', class: 'income' },
    transfer_out:      { label: 'Transf. enviada',  icon: '⬆️', class: 'expense' },
    investment_aporte: { label: 'Aporte',        icon: '📈', class: 'expense' },
    investment_saque:  { label: 'Saque inv.',    icon: '📉', class: 'income' },
    card_expense:      { label: 'Fatura cartão', icon: '💳', class: 'expense' },
  }

  const load = async () => {
    loading = true
    error = ''
    try {
      const r = await fetch(`/api/accounts/${accountId}/history`, { headers: auth() })
      if (!r.ok) throw new Error('Erro ao carregar histórico')
      const data = await r.json()
      events = data.events || []
    } catch (e: any) {
      error = e.message
    } finally {
      loading = false
    }
  }

  $: if (accountId) load()

  $: filteredEvents = events.filter(ev => {
    if (filterType && ev.type !== filterType) return false
    if (search && !(ev.descricao || '').toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  $: totalIn = filteredEvents.filter(e => e.valor > 0).reduce((s, e) => s + e.valor, 0)
  $: totalOut = filteredEvents.filter(e => e.valor < 0).reduce((s, e) => s + Math.abs(e.valor), 0)
  $: uniqueTypes = [...new Set(events.map(e => e.type))]

  const formatDate = (d: string) => {
    if (!d) return '—'
    const [y, m, day] = d.split('-')
    return `${day}/${m}/${y}`
  }
</script>

<div class="history-overlay" on:click={onClose} role="dialog">
  <div class="history-modal" on:click|stopPropagation role="document">
    <header>
      <div>
        <h3>📜 Histórico — {accountName}</h3>
        <span class="subtitle">Toda movimentação que afetou esta conta</span>
      </div>
      <button class="btn-close" on:click={onClose} aria-label="Fechar">✕</button>
    </header>

    {#if loading}
      <p class="empty">Carregando...</p>
    {:else if error}
      <p class="empty err">{error}</p>
    {:else if events.length === 0}
      <p class="empty">Sem movimentações registradas.</p>
    {:else}
      <div class="filters">
        <input type="text" placeholder="🔍 Buscar..." bind:value={search} class="inp-filter" />
        <select bind:value={filterType} class="inp-filter">
          <option value="">Todos tipos</option>
          {#each uniqueTypes as t}
            <option value={t}>{TYPE_LABELS[t]?.icon} {TYPE_LABELS[t]?.label || t}</option>
          {/each}
        </select>
      </div>

      <div class="totals">
        <span class="total-in">↑ Entradas: <strong>{fmt(totalIn)}</strong></span>
        <span class="total-out">↓ Saídas: <strong>{fmt(totalOut)}</strong></span>
        <span class="total-net">Líquido: <strong>{fmt(totalIn - totalOut)}</strong></span>
        <span class="count">{filteredEvents.length} {filteredEvents.length === 1 ? 'evento' : 'eventos'}</span>
      </div>

      <div class="timeline">
        {#each filteredEvents as ev (ev.type + '-' + ev.source_id + '-' + ev.date)}
          {@const meta = TYPE_LABELS[ev.type] || { label: ev.type, icon: '•', class: 'neutral' }}
          <div class="event-row {meta.class}">
            <div class="ev-icon">{meta.icon}</div>
            <div class="ev-main">
              <div class="ev-line-1">
                <span class="ev-desc">{ev.descricao}</span>
                <span class="ev-valor {ev.valor < 0 ? 'neg' : 'pos'}">
                  {ev.valor < 0 ? '−' : '+'} {fmt(Math.abs(ev.valor))}
                </span>
              </div>
              <div class="ev-line-2">
                <span class="ev-type">{meta.label}</span>
                {#if ev.categoria}<span class="ev-tag">{ev.categoria}</span>{/if}
                {#if ev.month && ev.year}<span class="ev-period">{ev.month}/{ev.year}</span>{/if}
                <span class="ev-date">{formatDate(ev.date)}</span>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .history-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.5);
    display: flex; align-items: center; justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }
  .history-modal {
    background: #fff; border-radius: 12px;
    width: 100%; max-width: 720px;
    max-height: 85vh;
    display: flex; flex-direction: column;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  }
  header { display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem 1.25rem; border-bottom: 1px solid #eee; }
  h3 { margin: 0 0 0.25rem 0; font-size: 1.1rem; color: #333; }
  .subtitle { font-size: 0.8rem; color: #888; }
  .btn-close { background: none; border: none; font-size: 1.3rem; cursor: pointer; color: #999; padding: 0 0.5rem; }
  .btn-close:hover { color: #333; }

  .empty { text-align: center; padding: 2rem; color: #888; font-style: italic; }
  .err { color: #c62828; }

  .filters { display: flex; gap: 0.5rem; padding: 0.75rem 1.25rem; border-bottom: 1px solid #f0f0f0; }
  .inp-filter { flex: 1; padding: 0.4rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; }

  .totals {
    display: flex; gap: 1rem; flex-wrap: wrap;
    padding: 0.6rem 1.25rem; background: #fafafa;
    font-size: 0.82rem; color: #666;
    border-bottom: 1px solid #f0f0f0;
  }
  .total-in strong { color: #4caf50; }
  .total-out strong { color: #f44336; }
  .total-net strong { color: #667eea; }
  .count { margin-left: auto; color: #999; font-size: 0.78rem; }

  .timeline { overflow-y: auto; padding: 0.5rem 0.75rem; flex: 1; }

  .event-row {
    display: flex; gap: 0.75rem; align-items: flex-start;
    padding: 0.6rem 0.6rem;
    border-bottom: 1px solid #f3f3f3;
    transition: background 0.15s;
  }
  .event-row:hover { background: #fafbff; }
  .event-row:last-child { border-bottom: none; }

  .ev-icon {
    font-size: 1.3rem;
    flex-shrink: 0;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    background: #f5f5f5; border-radius: 50%;
  }
  .event-row.income .ev-icon { background: #e8f5e9; }
  .event-row.expense .ev-icon { background: #ffebee; }

  .ev-main { flex: 1; min-width: 0; }
  .ev-line-1 { display: flex; justify-content: space-between; align-items: baseline; gap: 0.75rem; }
  .ev-desc { font-weight: 500; color: #333; font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .ev-valor { font-weight: 600; font-size: 0.92rem; flex-shrink: 0; }
  .ev-valor.pos { color: #4caf50; }
  .ev-valor.neg { color: #f44336; }

  .ev-line-2 { display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.72rem; color: #888; margin-top: 2px; }
  .ev-type { background: #eef; color: #667eea; padding: 1px 6px; border-radius: 8px; font-weight: 500; }
  .ev-tag { background: #f0f0f0; padding: 1px 6px; border-radius: 8px; }
  .ev-period { color: #aaa; }
  .ev-date { margin-left: auto; color: #999; }

  :global([data-theme="dark"]) .history-modal { background: #1e1e1e; }
  :global([data-theme="dark"]) header { border-color: #333; }
  :global([data-theme="dark"]) h3 { color: #eee; }
  :global([data-theme="dark"]) .filters { border-color: #333; }
  :global([data-theme="dark"]) .inp-filter { background: #2a2a2a; color: #ddd; border-color: #444; }
  :global([data-theme="dark"]) .totals { background: #2a2a2a; border-color: #333; color: #aaa; }
  :global([data-theme="dark"]) .event-row { border-color: #2a2a2a; }
  :global([data-theme="dark"]) .event-row:hover { background: #252550; }
  :global([data-theme="dark"]) .ev-desc { color: #ddd; }
  :global([data-theme="dark"]) .ev-icon { background: #2a2a2a; }
  :global([data-theme="dark"]) .event-row.income .ev-icon { background: #1f3f25; }
  :global([data-theme="dark"]) .event-row.expense .ev-icon { background: #3f1f1f; }
  :global([data-theme="dark"]) .ev-type { background: #2a2f4a; color: #b3c0ff; }
  :global([data-theme="dark"]) .ev-tag { background: #333; color: #bbb; }

  @media (max-width: 640px) {
    .history-modal { max-height: 95vh; }
    .filters { padding: 0.5rem 0.75rem; flex-direction: column; }
    .totals { padding: 0.5rem 0.75rem; gap: 0.5rem; }
    .ev-icon { width: 28px; height: 28px; font-size: 1.1rem; }
    .ev-desc { font-size: 0.85rem; }
  }
</style>
