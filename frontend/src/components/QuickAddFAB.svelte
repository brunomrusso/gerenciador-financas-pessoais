<script lang="ts">
  import { createEventDispatcher } from 'svelte'
  import { accountsStore } from '../stores/accounts'

  export let recordId: number
  export let categorias: string[] = ['Moradia','Alimentacao','Transporte','Saude','Educacao','Lazer','Cartao','Outros']

  const dispatch = createEventDispatcher()

  const API_BASE = '/api'
  const token = () => localStorage.getItem('token')
  const auth = () => ({ 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` })

  let open = false
  let modal: 'expense' | 'card' | null = null

  // expense form
  let eDesc = ''
  let eValor = ''
  let eData = new Date().toISOString().split('T')[0]
  let eCategoria = 'Outros'
  let eSaving = false

  // card form
  let cards: any[] = []
  let cCardId: number | null = null
  let cDesc = ''
  let cValor = ''
  let cData = new Date().toISOString().split('T')[0]
  let cCategoria = 'Outros'
  let cParcelas = '1'
  let cSaving = false

  function toggleOpen() { open = !open }

  async function openCard() {
    open = false
    if (!cards.length) {
      const r = await fetch(`${API_BASE}/cards`, { headers: auth() })
      cards = await r.json()
    }
    cCardId = cards[0]?.id ?? null
    modal = 'card'
  }

  function openExpense() { open = false; modal = 'expense' }
  function closeModal() { modal = null }

  async function saveExpense() {
    if (!eDesc.trim() || !eValor || !recordId) return
    eSaving = true
    try {
      const r = await fetch(`${API_BASE}/records/${recordId}/expenses`, {
        method: 'POST', headers: auth(),
        body: JSON.stringify({ descricao: eDesc, valor: parseFloat(eValor), data: eData, categoria: eCategoria })
      })
      if (r.ok) {
        eDesc = ''; eValor = ''; eCategoria = 'Outros'; eData = new Date().toISOString().split('T')[0]
        modal = null
        dispatch('saved')
      }
    } finally { eSaving = false }
  }

  async function saveCard() {
    if (!cDesc.trim() || !cValor || !cCardId || !recordId) return
    cSaving = true
    try {
      const r = await fetch(`${API_BASE}/cards/expenses`, {
        method: 'POST', headers: auth(),
        body: JSON.stringify({
          card_id: cCardId, record_id: recordId,
          descricao: cDesc, valor: parseFloat(cValor),
          data: cData, categoria: cCategoria,
          parcelas: parseInt(cParcelas) || 1
        })
      })
      if (r.ok) {
        cDesc = ''; cValor = ''; cCategoria = 'Outros'; cParcelas = '1'; cData = new Date().toISOString().split('T')[0]
        modal = null
        dispatch('saved')
      }
    } finally { cSaving = false }
  }
</script>

<!-- Speed dial overlay (fecha ao clicar fora) -->
{#if open}
  <div class="fab-backdrop" on:click={() => open = false} on:keydown={(e) => e.key === 'Escape' && (open = false)} role="button" tabindex="-1" aria-label="Fechar menu"></div>
{/if}

<!-- Speed dial actions -->
<div class="fab-wrap">
  {#if open}
    <div class="fab-actions">
      <button class="fab-action card-action" on:click={openCard}>
        <span class="fab-action-icon">💳</span>
        <span class="fab-action-label">Cartão</span>
      </button>
      <button class="fab-action expense-action" on:click={openExpense}>
        <span class="fab-action-icon">💸</span>
        <span class="fab-action-label">Despesa</span>
      </button>
    </div>
  {/if}

  <button class="fab-btn" class:fab-open={open} on:click={toggleOpen} title="Lançamento rápido">
    <span class="fab-icon">{open ? '✕' : '+'}</span>
  </button>
</div>

<!-- Modal Despesa Rápida -->
{#if modal === 'expense'}
  <div class="qa-overlay" on:click|self={closeModal} on:keydown={(e) => e.key === 'Escape' && closeModal()} role="dialog" aria-modal="true">
    <div class="qa-modal">
      <div class="qa-header">
        <span>💸 Despesa rápida</span>
        <button class="qa-close" on:click={closeModal}>✕</button>
      </div>
      <div class="qa-body">
        <input type="text" placeholder="Descrição *" bind:value={eDesc} class="qa-inp" />
        <div class="qa-row">
          <input type="number" inputmode="decimal" placeholder="Valor *" bind:value={eValor} step="0.01" class="qa-inp" />
          <input type="date" bind:value={eData} class="qa-inp" />
        </div>
        <select bind:value={eCategoria} class="qa-inp">
          {#each categorias as cat}<option>{cat}</option>{/each}
        </select>
      </div>
      <div class="qa-footer">
        <button class="qa-btn-cancel" on:click={closeModal}>Cancelar</button>
        <button class="qa-btn-save" on:click={saveExpense} disabled={eSaving || !eDesc.trim() || !eValor}>
          {eSaving ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Modal Cartão Rápido -->
{#if modal === 'card'}
  <div class="qa-overlay" on:click|self={closeModal} on:keydown={(e) => e.key === 'Escape' && closeModal()} role="dialog" aria-modal="true">
    <div class="qa-modal">
      <div class="qa-header">
        <span>💳 Lançamento no cartão</span>
        <button class="qa-close" on:click={closeModal}>✕</button>
      </div>
      {#if cards.length === 0}
        <div class="qa-body">
          <p class="qa-empty">Nenhum cartão cadastrado. Acesse a seção de Cartões para criar um.</p>
        </div>
        <div class="qa-footer">
          <button class="qa-btn-cancel" on:click={closeModal}>Fechar</button>
        </div>
      {:else}
        <div class="qa-body">
          <select bind:value={cCardId} class="qa-inp">
            {#each cards as c}<option value={c.id}>{c.nome}</option>{/each}
          </select>
          <input type="text" placeholder="Descrição *" bind:value={cDesc} class="qa-inp" />
          <div class="qa-row">
            <input type="number" inputmode="decimal" placeholder="Valor *" bind:value={cValor} step="0.01" class="qa-inp" />
            <input type="date" bind:value={cData} class="qa-inp" />
          </div>
          <div class="qa-row">
            <select bind:value={cCategoria} class="qa-inp">
              {#each categorias as cat}<option>{cat}</option>{/each}
            </select>
            <div class="qa-parc-wrap">
              <label class="qa-parc-lbl" for="parc-fab-inp">Parcelas</label>
              <input id="parc-fab-inp" type="number" inputmode="numeric" min="1" max="60" bind:value={cParcelas} class="qa-inp" style="width:70px" />
            </div>
          </div>
        </div>
        <div class="qa-footer">
          <button class="qa-btn-cancel" on:click={closeModal}>Cancelar</button>
          <button class="qa-btn-save" on:click={saveCard} disabled={cSaving || !cDesc.trim() || !cValor}>
            {cSaving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .fab-backdrop {
    position: fixed; inset: 0; z-index: 498;
  }

  .fab-wrap {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    z-index: 499;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.65rem;
  }

  .fab-btn {
    width: 56px; height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(102,126,234,0.5);
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .fab-btn:hover { transform: scale(1.08); box-shadow: 0 6px 22px rgba(102,126,234,0.65); }
  .fab-btn.fab-open { transform: rotate(45deg); }
  .fab-icon { font-size: 1.6rem; line-height: 1; font-weight: 300; }

  .fab-actions {
    display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;
    animation: fab-slide-up 0.18s ease-out;
  }
  @keyframes fab-slide-up {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .fab-action {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.45rem 0.85rem 0.45rem 0.6rem;
    border-radius: 24px;
    border: none;
    cursor: pointer;
    font-size: 0.88rem;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18);
    color: white;
    transition: transform 0.15s;
  }
  .fab-action:hover { transform: translateX(-4px); }
  .expense-action { background: linear-gradient(135deg, #43a047, #2e7d32); }
  .card-action    { background: linear-gradient(135deg, #667eea, #764ba2); }
  .fab-action-icon { font-size: 1.05rem; }
  .fab-action-label { white-space: nowrap; }

  /* Quick add modal */
  .qa-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1200;
    display: flex; align-items: flex-end; justify-content: center;
  }
  @media (min-width: 500px) {
    .qa-overlay { align-items: center; }
  }

  .qa-modal {
    background: white;
    width: 100%; max-width: 440px;
    border-radius: 16px 16px 0 0;
    box-shadow: 0 -4px 30px rgba(0,0,0,0.2);
    overflow: hidden;
  }
  @media (min-width: 500px) {
    .qa-modal { border-radius: 16px; }
  }

  .qa-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.25rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 700; font-size: 1rem;
  }
  .qa-close {
    background: rgba(255,255,255,0.2); border: none;
    color: white; font-size: 1rem;
    width: 28px; height: 28px; border-radius: 8px; cursor: pointer;
  }
  .qa-close:hover { background: rgba(255,255,255,0.35); }

  .qa-body { padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.6rem; }

  .qa-inp {
    width: 100%;
    padding: 0.55rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 0.9rem;
    color: #333;
    background: #fff;
    color-scheme: light;
    box-sizing: border-box;
  }
  .qa-inp:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.12); }

  .qa-row { display: flex; gap: 0.5rem; }
  .qa-row .qa-inp { flex: 1; }

  .qa-parc-wrap { display: flex; flex-direction: column; gap: 2px; }
  .qa-parc-lbl { font-size: 0.7rem; color: #888; }

  .qa-empty { text-align: center; color: #888; font-style: italic; padding: 0.5rem 0; font-size: 0.9rem; }

  .qa-footer {
    display: flex; gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    border-top: 1px solid #eee;
    background: #fafbfc;
  }
  .qa-btn-cancel {
    flex: 1;
    padding: 0.6rem; border: 1px solid #ddd;
    background: none; color: #777; border-radius: 8px;
    cursor: pointer; font-size: 0.9rem;
  }
  .qa-btn-save {
    flex: 2;
    padding: 0.6rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none; border-radius: 8px;
    cursor: pointer; font-weight: 600; font-size: 0.9rem;
    transition: opacity 0.15s;
  }
  .qa-btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Dark mode */
  :global([data-theme="dark"]) .qa-modal { background: #1e1e2e; }
  :global([data-theme="dark"]) .qa-inp { background: #2a2a3e; color: #e8e8f0; border-color: #3a3a52; color-scheme: dark; }
  :global([data-theme="dark"]) .qa-footer { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .qa-btn-cancel { border-color: #3a3a52; color: #9090a8; }
  :global([data-theme="dark"]) .qa-empty { color: #7070a0; }
</style>
