<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte'
  import { valuesHidden } from '../stores/privacy'
  import { fmtMasked } from '../utils/format'

  export let recordId: number

  type Account = { id: number, nome: string, tipo: string, saldo: number }
  type Tx = { id: number, account_id: number, record_id: number | null, tipo: string, valor: number, descricao: string, data: string }

  let accounts: Account[] = []
  let transactions: Record<number, Tx[]> = {}
  let expanded: Record<number, boolean> = {}
  let summaryData = { saldo_total: 0, aportes_mes: 0, saques_mes: 0, rendimentos_mes: 0, liquido_mes: 0 }

  let showAddAccount = false
  let newAccName = ''
  let newAccTipo = 'Geral'

  let txModal: { accountId: number, accountName: string, saldo: number, tipo: 'aporte' | 'saque' | 'rendimento' } | null = null
  let txValor = ''
  let txDesc = ''
  let txData = ''

  let confirmDelAcc: { id: number, nome: string } | null = null

  const dispatch = createEventDispatcher()

  const API = '/api/investments'
  const auth = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` })
  $: fmt = (v: number) => fmtMasked(v, $valuesHidden)

  const loadSummary = async () => {
    const url = recordId ? `${API}/summary?record_id=${recordId}` : `${API}/summary`
    const r = await fetch(url, { headers: auth() })
    if (r.ok) {
      const data = await r.json()
      accounts = data.accounts || []
      summaryData = {
        saldo_total: data.saldo_total,
        aportes_mes: data.aportes_mes,
        saques_mes: data.saques_mes,
        rendimentos_mes: data.rendimentos_mes,
        liquido_mes: data.liquido_mes
      }
      dispatch('summary', summaryData)
    }
  }

  const loadTxs = async (accountId: number) => {
    if (!recordId) return
    const r = await fetch(`${API}/${accountId}/transactions?record_id=${recordId}`, { headers: auth() })
    if (r.ok) {
      transactions = { ...transactions, [accountId]: await r.json() }
    }
  }

  const toggle = async (accId: number) => {
    expanded = { ...expanded, [accId]: !expanded[accId] }
    if (expanded[accId]) await loadTxs(accId)
  }

  const addAccount = async () => {
    if (!newAccName.trim()) return
    const r = await fetch(API, { method: 'POST', headers: auth(), body: JSON.stringify({ nome: newAccName.trim(), tipo: newAccTipo }) })
    if (r.ok) {
      newAccName = ''
      newAccTipo = 'Geral'
      showAddAccount = false
      await loadSummary()
    }
  }

  const openTx = (acc: Account, tipo: 'aporte' | 'saque' | 'rendimento') => {
    txModal = { accountId: acc.id, accountName: acc.nome, saldo: acc.saldo, tipo }
    txValor = ''
    txDesc = ''
    txData = new Date().toISOString().slice(0, 10)
  }

  const submitTx = async () => {
    if (!txModal) return
    const valor = parseFloat(String(txValor).replace(',', '.'))
    if (!valor || valor <= 0) {
      alert('Informe um valor válido')
      return
    }
    if (txModal.tipo === 'saque' && valor > txModal.saldo) {
      alert(`Saque maior que saldo disponível (${fmt(txModal.saldo)})`)
      return
    }
    const r = await fetch(`${API}/${txModal.accountId}/transactions`, {
      method: 'POST', headers: auth(),
      body: JSON.stringify({
        tipo: txModal.tipo, valor, descricao: txDesc, data: txData, record_id: recordId
      })
    })
    if (r.ok) {
      const accId = txModal.accountId
      txModal = null
      await loadSummary()
      if (expanded[accId]) await loadTxs(accId)
    } else {
      const err = await r.json().catch(() => ({}))
      alert(err.error || 'Erro ao salvar movimentação')
    }
  }

  const deleteTx = async (tx: Tx) => {
    if (!confirm('Excluir esta movimentação?')) return
    await fetch(`${API}/transactions/${tx.id}`, { method: 'DELETE', headers: auth() })
    await loadSummary()
    await loadTxs(tx.account_id)
  }

  const deleteAccount = async () => {
    if (!confirmDelAcc) return
    await fetch(`${API}/${confirmDelAcc.id}`, { method: 'DELETE', headers: auth() })
    confirmDelAcc = null
    await loadSummary()
  }

  $: if (recordId) loadSummary()

  const tipoLabel = (t: string) => t === 'aporte' ? 'Aporte' : t === 'saque' ? 'Saque' : t === 'rendimento' ? 'Rendimento' : t
  const tipoIcon  = (t: string) => t === 'aporte' ? '⬆' : t === 'saque' ? '⬇' : '✨'
  const tipoColor = (t: string) => t === 'aporte' ? '#2196f3' : t === 'saque' ? '#f44336' : '#4caf50'
</script>

<div class="inv-section">
  <div class="inv-header">
    <div class="inv-title">
      <span class="icon">💰</span>
      <h3>Investimentos</h3>
    </div>
    <button class="btn-add" on:click={() => showAddAccount = !showAddAccount}>
      {showAddAccount ? '✕' : '+ Conta'}
    </button>
  </div>

  <div class="inv-totals">
    <div class="total-box main">
      <span class="lbl">Saldo Total</span>
      <span class="val">{fmt(summaryData.saldo_total)}</span>
    </div>
    <div class="total-box">
      <span class="lbl">Aportes mês</span>
      <span class="val pos">{fmt(summaryData.aportes_mes)}</span>
    </div>
    <div class="total-box">
      <span class="lbl">Saques mês</span>
      <span class="val neg">{fmt(summaryData.saques_mes)}</span>
    </div>
    <div class="total-box">
      <span class="lbl">Rendimento mês</span>
      <span class="val pos">{fmt(summaryData.rendimentos_mes)}</span>
    </div>
  </div>

  {#if showAddAccount}
    <div class="add-acc-form">
      <input class="inp" placeholder="Nome da conta (ex: CDB Banco X)" bind:value={newAccName} />
      <input class="inp small" placeholder="Tipo (CDB, Tesouro...)" bind:value={newAccTipo} />
      <button class="btn-save" on:click={addAccount}>Criar</button>
    </div>
  {/if}

  {#if accounts.length === 0}
    <p class="empty">Nenhuma conta de investimento. Crie uma para começar.</p>
  {:else}
    <div class="acc-list">
      {#each accounts as acc (acc.id)}
        <div class="acc-card">
          <div class="acc-row">
            <button class="acc-info" on:click={() => toggle(acc.id)}>
              <span class="acc-icon">📈</span>
              <div class="acc-meta">
                <span class="acc-nome">{acc.nome}</span>
                <span class="acc-tipo">{acc.tipo}</span>
              </div>
              <span class="acc-saldo">{fmt(acc.saldo)}</span>
              <span class="chevron">{expanded[acc.id] ? '▴' : '▾'}</span>
            </button>
            <div class="acc-actions">
              <button class="btn-aporte" on:click={() => openTx(acc, 'aporte')} title="Aporte">⬆</button>
              <button class="btn-saque" on:click={() => openTx(acc, 'saque')} title="Saque">⬇</button>
              <button class="btn-rend" on:click={() => openTx(acc, 'rendimento')} title="Rendimento">✨</button>
              <button class="btn-del" on:click={() => confirmDelAcc = { id: acc.id, nome: acc.nome }} title="Excluir conta">🗑</button>
            </div>
          </div>

          {#if expanded[acc.id]}
            <div class="tx-body">
              {#if !transactions[acc.id] || transactions[acc.id].length === 0}
                <p class="empty-tx">Sem movimentações neste mês.</p>
              {:else}
                <table>
                  <thead>
                    <tr><th>Tipo</th><th>Descrição</th><th>Data</th><th class="r">Valor</th><th></th></tr>
                  </thead>
                  <tbody>
                    {#each transactions[acc.id] as tx (tx.id)}
                      <tr>
                        <td><span class="tx-tipo" style:color={tipoColor(tx.tipo)}>{tipoIcon(tx.tipo)} {tipoLabel(tx.tipo)}</span></td>
                        <td>{tx.descricao || '-'}</td>
                        <td>{tx.data || '-'}</td>
                        <td class="r" style:color={tipoColor(tx.tipo)}>
                          {tx.tipo === 'saque' ? '-' : '+'}{fmt(tx.valor)}
                        </td>
                        <td><button class="btn-del-sm" on:click={() => deleteTx(tx)}>🗑</button></td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if txModal}
  <div class="modal-overlay" on:click|self={() => txModal = null}>
    <div class="modal-box">
      <p class="modal-title">{tipoLabel(txModal.tipo)} — {txModal.accountName}</p>
      <p class="modal-sub">Saldo atual: {fmt(txModal.saldo)}</p>

      <input class="inp full" type="text" inputmode="decimal" placeholder="Valor (R$)" bind:value={txValor} />
      <input class="inp full" type="text" placeholder="Descrição (opcional)" bind:value={txDesc} />
      <input class="inp full" type="date" bind:value={txData} />

      <div class="modal-btns">
        <button class="btn-modal-all" on:click={submitTx}>Confirmar</button>
        <button class="btn-modal-cancel" on:click={() => txModal = null}>Cancelar</button>
      </div>
    </div>
  </div>
{/if}

{#if confirmDelAcc}
  <div class="modal-overlay" on:click|self={() => confirmDelAcc = null}>
    <div class="modal-box">
      <p class="modal-title">Excluir conta</p>
      <p class="modal-sub">Tem certeza que deseja excluir <strong>{confirmDelAcc.nome}</strong> e todas as suas movimentações?</p>
      <div class="modal-btns">
        <button class="btn-modal-all danger" on:click={deleteAccount}>Excluir</button>
        <button class="btn-modal-cancel" on:click={() => confirmDelAcc = null}>Cancelar</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .inv-section { background: white; padding: 1rem 1.25rem 1.25rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.1); margin-bottom: 1.5rem; }
  .inv-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
  .inv-title { display: flex; align-items: center; gap: 0.5rem; }
  .icon { font-size: 1.2rem; }
  h3 { margin: 0; font-size: 1.05rem; color: #333; }

  .btn-add { background: #667eea; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 5px; cursor: pointer; font-size: 0.85rem; }

  .inv-totals { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 1rem; }
  .total-box { background: #f8f9ff; border-radius: 8px; padding: 0.6rem 0.75rem; display: flex; flex-direction: column; gap: 2px; }
  .total-box.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
  .total-box.main .lbl { color: rgba(255,255,255,0.85); }
  .total-box.main .val { color: white; }
  .lbl { font-size: 0.7rem; color: #777; text-transform: uppercase; font-weight: 600; }
  .val { font-size: 1rem; font-weight: 700; color: #333; }
  .val.pos { color: #4caf50; }
  .val.neg { color: #f44336; }

  .add-acc-form { display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; background: #f9f9ff; padding: 0.6rem; border-radius: 8px; }
  .inp { padding: 0.45rem 0.6rem; border: 1px solid #ddd; border-radius: 5px; font-size: 0.875rem; color: #333; background: #fff; box-sizing: border-box; flex: 1; min-width: 140px; }
  .inp.small { flex: 0 0 160px; }
  .inp.full { width: 100%; flex: 1 1 100%; margin-bottom: 0.5rem; }
  .btn-save { background: #4caf50; color: white; border: none; padding: 0.45rem 1rem; border-radius: 5px; cursor: pointer; }

  .empty { color: #999; font-style: italic; text-align: center; padding: 1rem; margin: 0; font-size: 0.875rem; }
  .empty-tx { color: #999; font-style: italic; text-align: center; padding: 0.5rem; margin: 0; font-size: 0.8rem; }

  .acc-list { display: flex; flex-direction: column; gap: 0.5rem; }
  .acc-card { border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }
  .acc-row { display: flex; align-items: center; gap: 0.5rem; background: #f8f9ff; padding: 0.6rem 0.75rem; }
  .acc-info { flex: 1; display: flex; align-items: center; gap: 0.6rem; background: none; border: none; cursor: pointer; text-align: left; padding: 0; min-width: 0; }
  .acc-icon { font-size: 1.1rem; }
  .acc-meta { display: flex; flex-direction: column; flex: 1; min-width: 0; }
  .acc-nome { font-weight: 600; color: #333; font-size: 0.92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .acc-tipo { font-size: 0.7rem; color: #888; }
  .acc-saldo { font-weight: 700; color: #333; font-size: 1rem; }
  .chevron { color: #667eea; font-size: 0.85rem; }

  .acc-actions { display: flex; gap: 4px; }
  .acc-actions button { width: 30px; height: 30px; border-radius: 4px; border: none; color: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 0.85rem; }
  .btn-aporte { background: #2196f3; }
  .btn-saque { background: #f44336; }
  .btn-rend { background: #4caf50; }
  .btn-del { background: #9e9e9e; }

  .tx-body { padding: 0 0.75rem 0.75rem; overflow-x: auto; }
  .tx-body table { width: 100%; border-collapse: collapse; min-width: 360px; }
  .tx-body th { padding: 0.4rem 0.4rem; font-size: 0.75rem; color: #777; font-weight: 600; border-bottom: 1px solid #eee; text-align: left; }
  .tx-body td { padding: 0.3rem 0.4rem; font-size: 0.82rem; color: #333; border-bottom: 1px solid #f5f5f5; }
  .tx-body th.r, .tx-body td.r { text-align: right; }
  .tx-tipo { font-weight: 600; font-size: 0.8rem; }
  .btn-del-sm { background: #f44336; color: white; border: none; width: 22px; height: 22px; border-radius: 4px; cursor: pointer; font-size: 0.7rem; }

  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
  .modal-box { background: white; padding: 1.25rem; border-radius: 10px; max-width: 380px; width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
  .modal-title { margin: 0 0 0.25rem; font-weight: 700; font-size: 1.05rem; color: #333; }
  .modal-sub { margin: 0 0 0.75rem; font-size: 0.85rem; color: #666; }
  .modal-btns { display: flex; flex-direction: column; gap: 0.5rem; }
  .btn-modal-all { padding: 0.55rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.875rem; }
  .btn-modal-all.danger { background: #f44336; }
  .btn-modal-cancel { padding: 0.45rem 1rem; background: none; color: #999; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }

  @media (max-width: 640px) {
    .inv-section { padding: 0.75rem; }
    .inv-totals { grid-template-columns: 1fr 1fr; }
    .acc-row { flex-wrap: wrap; }
    .acc-saldo { font-size: 0.95rem; }
    .acc-actions button { width: 26px; height: 26px; font-size: 0.78rem; }
    .inp.small { flex: 1 1 100%; }
  }
</style>
