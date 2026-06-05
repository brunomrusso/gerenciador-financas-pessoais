<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'
  import AccountHistory from './AccountHistory.svelte'

  let historyAccount: { id: number; nome: string } | null = null

  type Account = {
    id: number, nome: string, tipo: string, saldo_inicial: number,
    cor: string, icone: string, padrao: boolean, ativa: boolean, saldo: number
  }

  export let refreshKey: number = 0

  let accounts: Account[] = []
  let expanded = false
  let adding = false
  let editingId: number | null = null

  let formNome = ''
  let formTipo = 'corrente'
  let formSaldoInicial = ''
  let formIcone = '💰'
  let formCor = '#667eea'
  let formPadrao = false

  const TIPOS = [
    { val: 'corrente', label: 'Conta Corrente', icon: '🏦' },
    { val: 'poupanca', label: 'Poupança', icon: '🐖' },
    { val: 'carteira', label: 'Carteira', icon: '💵' },
    { val: 'outro', label: 'Outro', icon: '💰' },
  ]

  const ICONS = ['💰', '💳', '🏦', '🐖', '💵', '💎', '🎯']
  const CORES = ['#667eea', '#4caf50', '#f44336', '#ff9800', '#9c27b0', '#00bcd4', '#795548']

  const dispatch = createEventDispatcher()
  const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })
  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)

  export const reload = async () => {
    const r = await fetch('/api/accounts', { headers: auth() })
    if (r.ok) {
      accounts = await r.json()
      dispatch('change', accounts)
    }
  }

  const resetForm = () => {
    formNome = ''
    formTipo = 'corrente'
    formSaldoInicial = ''
    formIcone = '💰'
    formCor = '#667eea'
    formPadrao = false
    editingId = null
    adding = false
  }

  const startEdit = (acc: Account) => {
    editingId = acc.id
    formNome = acc.nome
    formTipo = acc.tipo
    formSaldoInicial = String(acc.saldo_inicial)
    formIcone = acc.icone
    formCor = acc.cor
    formPadrao = acc.padrao
    adding = true
  }

  const submit = async () => {
    if (!formNome.trim()) { alert('Nome é obrigatório'); return }
    const payload = {
      nome: formNome.trim(),
      tipo: formTipo,
      saldo_inicial: parseFloat(String(formSaldoInicial).replace(',', '.')) || 0,
      cor: formCor, icone: formIcone, padrao: formPadrao
    }
    const url = editingId ? `/api/accounts/${editingId}` : '/api/accounts'
    const method = editingId ? 'PATCH' : 'POST'
    const r = await fetch(url, { method, headers: auth(), body: JSON.stringify(payload) })
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      alert(err.error || 'Erro ao salvar')
      return
    }
    resetForm()
    await reload()
  }

  const remove = async (acc: Account) => {
    if (acc.padrao) { alert('Não é possível excluir a conta padrão'); return }
    if (!confirm(`Excluir "${acc.nome}"? Os lançamentos vinculados ficarão sem conta.`)) return
    const r = await fetch(`/api/accounts/${acc.id}`, { method: 'DELETE', headers: auth() })
    if (r.ok) await reload()
  }

  const setDefault = async (acc: Account) => {
    if (acc.padrao) return
    await fetch(`/api/accounts/${acc.id}`, { method: 'PATCH', headers: auth(), body: JSON.stringify({ padrao: true }) })
    await reload()
  }

  $: saldoTotal = accounts.reduce((s, a) => s + (a.saldo || 0), 0)

  // Recarrega sempre que refreshKey mudar (lançamentos novos)
  $: if (refreshKey >= 0) reload()

  // Ajuste de saldo (modal)
  let adjustAcc: Account | null = null
  let adjustValor = ''
  let savingAdjust = false
  function openAdjust(acc: Account) {
    adjustAcc = acc
    adjustValor = (acc.saldo || 0).toFixed(2).replace('.', ',')
  }
  function closeAdjust() { adjustAcc = null; adjustValor = '' }
  $: adjustNovo = parseFloat(String(adjustValor).replace(/\./g, '').replace(',', '.')) || 0
  $: adjustDelta = adjustAcc ? adjustNovo - (adjustAcc.saldo || 0) : 0
  async function saveAdjust() {
    if (!adjustAcc) return
    savingAdjust = true
    try {
      const novoInicial = (adjustAcc.saldo_inicial || 0) + adjustDelta
      const r = await fetch(`/api/accounts/${adjustAcc.id}`, {
        method: 'PATCH', headers: auth(),
        body: JSON.stringify({ saldo_inicial: novoInicial })
      })
      if (!r.ok) { alert('Erro ao ajustar saldo'); return }
      closeAdjust()
      await reload()
    } finally { savingAdjust = false }
  }

  onMount(() => reload())
</script>

<div class="acc-section">
  <div class="acc-header" on:click={() => expanded = !expanded}>
    <div class="acc-title">
      <span class="icon">🏦</span>
      <h3>Minhas Contas</h3>
      <span class="count">{accounts.length}</span>
    </div>
    <div class="acc-summary">
      <span class="saldo-total">{fmt(saldoTotal)}</span>
      <span class="chevron">{expanded ? '▴' : '▾'}</span>
    </div>
  </div>

  {#if expanded}
    <div class="acc-body">
      <div class="acc-grid">
        {#each accounts as acc (acc.id)}
          <div class="acc-card" style="border-left-color: {acc.cor};">
            <div class="acc-row-1">
              <span class="acc-icone">{acc.icone}</span>
              <div class="acc-info">
                <span class="acc-nome">
                  {acc.nome}
                  {#if acc.padrao}<span class="padrao-badge">Padrão</span>{/if}
                </span>
                <span class="acc-tipo-lbl">{TIPOS.find(t => t.val === acc.tipo)?.label || acc.tipo}</span>
              </div>
            </div>
            <div class="acc-saldo" class:negativo={acc.saldo < 0}>{fmt(acc.saldo)}</div>
            <div class="acc-actions">
              <button class="btn-mini" title="Histórico" on:click={() => historyAccount = { id: acc.id, nome: acc.nome }}>📜</button>
              <button class="btn-mini" title="Ajustar saldo" on:click={() => openAdjust(acc)}>🎯</button>
              {#if !acc.padrao}
                <button class="btn-mini" title="Tornar padrão" on:click={() => setDefault(acc)}>★</button>
              {/if}
              <button class="btn-mini" title="Editar" on:click={() => startEdit(acc)}>✎</button>
              {#if !acc.padrao}
                <button class="btn-mini btn-del" title="Excluir" on:click={() => remove(acc)}>🗑</button>
              {/if}
            </div>
          </div>
        {/each}
      </div>

      {#if adding}
        <div class="form-card">
          <h4>{editingId ? 'Editar conta' : 'Nova conta'}</h4>
          <div class="form-grid">
            <input class="inp" placeholder="Nome (ex: Itaú, Nubank)" bind:value={formNome} />
            <select class="inp" bind:value={formTipo}>
              {#each TIPOS as t}<option value={t.val}>{t.icon} {t.label}</option>{/each}
            </select>
            <input class="inp" type="text" inputmode="decimal" placeholder="Saldo inicial (R$)" bind:value={formSaldoInicial} />
            <div class="picker-row">
              <span class="picker-lbl">Ícone:</span>
              {#each ICONS as ic}
                <button type="button" class="picker-btn" class:sel={formIcone === ic} on:click={() => formIcone = ic}>{ic}</button>
              {/each}
            </div>
            <div class="picker-row">
              <span class="picker-lbl">Cor:</span>
              {#each CORES as c}
                <button type="button" class="cor-btn" class:sel={formCor === c} style="background:{c}" on:click={() => formCor = c}></button>
              {/each}
            </div>
            <label class="chk-padrao">
              <input type="checkbox" bind:checked={formPadrao} />
              Tornar conta padrão
            </label>
          </div>
          <div class="form-btns">
            <button class="btn-primary" on:click={submit}>{editingId ? 'Salvar' : 'Criar'}</button>
            <button class="btn-cancel" on:click={resetForm}>Cancelar</button>
          </div>
        </div>
      {:else}
        <button class="btn-add-acc" on:click={() => adding = true}>+ Nova conta</button>
      {/if}
    </div>
  {/if}
</div>

{#if historyAccount}
  <AccountHistory
    accountId={historyAccount.id}
    accountName={historyAccount.nome}
    onClose={() => historyAccount = null}
  />
{/if}

{#if adjustAcc}
  <div class="modal-overlay" on:click|self={closeAdjust}>
    <div class="modal-box">
      <p class="modal-title">🎯 Ajustar saldo — {adjustAcc.nome}</p>
      <p class="modal-sub">Saldo atual: <strong>{fmt(adjustAcc.saldo || 0)}</strong></p>
      <label class="adjust-label">Novo saldo (R$)</label>
      <input class="adjust-input" type="text" inputmode="decimal" bind:value={adjustValor} placeholder="0,00" />
      {#if Math.abs(adjustDelta) > 0.001}
        <p class="adjust-delta" class:positive={adjustDelta > 0} class:negative={adjustDelta < 0}>
          {adjustDelta > 0 ? '+' : ''}{fmt(adjustDelta)} será aplicado ao saldo inicial
        </p>
      {/if}
      <p class="adjust-help">A diferença será somada/subtraída do <em>saldo inicial</em> da conta sem afetar transações existentes.</p>
      <div class="adjust-btns">
        <button class="btn-primary" on:click={saveAdjust} disabled={savingAdjust || Math.abs(adjustDelta) < 0.001}>
          {savingAdjust ? 'Salvando...' : 'Aplicar ajuste'}
        </button>
        <button class="btn-cancel" on:click={closeAdjust}>Cancelar</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .acc-section { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); margin-bottom: 1.5rem; overflow: hidden; }
  .acc-header { display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.25rem; cursor: pointer; }
  .acc-header:hover { background: #f8f9ff; }
  .acc-title { display: flex; align-items: center; gap: 0.5rem; }
  .icon { font-size: 1.25rem; }
  h3 { margin: 0; font-size: 1.05rem; color: #333; }
  .count { background: #667eea; color: white; border-radius: 10px; padding: 1px 8px; font-size: 0.7rem; font-weight: 600; }

  .acc-summary { display: flex; align-items: center; gap: 0.5rem; }
  .saldo-total { font-weight: 700; font-size: 1rem; color: #333; }
  .chevron { color: #667eea; font-size: 0.85rem; }

  .acc-body { padding: 0 1rem 1rem; border-top: 1px solid #eee; }

  .acc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; padding: 0.75rem 0; }
  .acc-card {
    background: #f8f9ff;
    border-left: 4px solid #667eea;
    border-radius: 8px;
    padding: 0.7rem 0.85rem;
    display: flex; flex-direction: column; gap: 0.5rem;
  }
  .acc-row-1 { display: flex; align-items: center; gap: 0.6rem; }
  .acc-icone { font-size: 1.5rem; }
  .acc-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
  .acc-nome { font-weight: 600; color: #333; font-size: 0.92rem; display: flex; align-items: center; gap: 6px; }
  .acc-tipo-lbl { font-size: 0.72rem; color: #888; }
  .acc-saldo { font-size: 1.15rem; font-weight: 700; color: #333; }
  .acc-saldo.negativo { color: #f44336; }

  .padrao-badge { background: #ffd54f; color: #5d4037; font-size: 0.62rem; padding: 1px 6px; border-radius: 8px; font-weight: 600; }

  .acc-actions { display: flex; gap: 4px; }
  .btn-mini { background: #fff; border: 1px solid #ddd; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; color: #555; }
  .btn-mini:hover { background: #667eea; color: white; border-color: #667eea; }
  .btn-mini.btn-del:hover { background: #f44336; border-color: #f44336; }

  .form-card { background: #f0f4ff; border-radius: 8px; padding: 0.85rem; margin-top: 0.5rem; }
  .form-card h4 { margin: 0 0 0.6rem; font-size: 0.92rem; color: #333; }
  .form-grid { display: flex; flex-direction: column; gap: 0.5rem; }
  .inp { padding: 0.45rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.85rem; color: #333; background: #fff; }
  .picker-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .picker-lbl { font-size: 0.78rem; color: #666; font-weight: 600; min-width: 40px; }
  .picker-btn { background: #fff; border: 1px solid #ddd; width: 32px; height: 32px; border-radius: 4px; cursor: pointer; font-size: 1rem; }
  .picker-btn.sel { background: #667eea; border-color: #667eea; box-shadow: 0 0 0 2px rgba(102,126,234,0.2); }
  .cor-btn { width: 22px; height: 22px; border-radius: 50%; border: 2px solid transparent; cursor: pointer; }
  .cor-btn.sel { border-color: #333; box-shadow: 0 0 0 2px white inset; }
  .chk-padrao { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #555; }

  .form-btns { display: flex; gap: 0.5rem; margin-top: 0.6rem; }
  .btn-primary { background: #667eea; color: white; border: none; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer; font-weight: 600; }
  .btn-cancel { background: none; color: #888; border: 1px solid #ccc; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer; }

  .btn-add-acc {
    background: none; border: 1px dashed #c0c0d0; color: #667eea;
    padding: 0.55rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 500;
    width: 100%; margin-top: 0.5rem;
  }
  .btn-add-acc:hover { background: #f0f4ff; border-color: #667eea; }

  @media (max-width: 640px) {
    .acc-grid { grid-template-columns: 1fr; }
  }

  /* Modal de ajuste */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
  .modal-box { background: white; border-radius: 12px; padding: 1.25rem; width: 100%; max-width: 380px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
  .modal-title { margin: 0 0 0.25rem; font-size: 1rem; font-weight: 700; color: #333; }
  .modal-sub { margin: 0 0 0.85rem; font-size: 0.85rem; color: #666; }
  .adjust-label { display: block; font-size: 0.8rem; color: #555; font-weight: 600; margin-bottom: 0.3rem; }
  .adjust-input { width: 100%; box-sizing: border-box; padding: 0.6rem 0.75rem; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; font-weight: 600; color: #333; background: #fff; }
  .adjust-delta { margin: 0.5rem 0 0; font-size: 0.85rem; font-weight: 600; padding: 0.4rem 0.6rem; border-radius: 5px; }
  .adjust-delta.positive { color: #2e7d32; background: #e8f5e9; }
  .adjust-delta.negative { color: #c62828; background: #ffebee; }
  .adjust-help { margin: 0.6rem 0 0; font-size: 0.75rem; color: #888; line-height: 1.4; }
  .adjust-btns { display: flex; gap: 0.5rem; margin-top: 0.85rem; }
  .adjust-btns .btn-primary { flex: 1; }
  .adjust-btns .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

  :global([data-theme="dark"]) .modal-box { background: #1e1e1e; }
  :global([data-theme="dark"]) .modal-title { color: #eee; }
  :global([data-theme="dark"]) .modal-sub, :global([data-theme="dark"]) .adjust-label, :global([data-theme="dark"]) .adjust-help { color: #aaa; }
  :global([data-theme="dark"]) .adjust-input { background: #2a2a2a; color: #ddd; border-color: #444; }
</style>
