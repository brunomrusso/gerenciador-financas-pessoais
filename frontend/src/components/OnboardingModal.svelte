<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  export let userName: string = ''

  const dispatch = createEventDispatcher()

  let step = 0
  const totalSteps = 4

  const steps = [
    { icon: '👋', title: 'Bem-vindo ao CashFlow!' },
    { icon: '💡', title: 'Como funciona' },
    { icon: '📱', title: 'Dicas de uso' },
    { icon: '🚀', title: 'Tudo pronto!' },
  ]

  function next() { if (step < totalSteps - 1) step++ }
  function prev() { if (step > 0) step-- }
  function finish() { dispatch('done') }
  function skip()   { dispatch('done') }
</script>

<div class="ob-overlay">
  <div class="ob-modal">
    <!-- Progress bar -->
    <div class="ob-progress">
      {#each steps as _, i}
        <div class="ob-dot" class:active={i === step} class:done={i < step}></div>
      {/each}
    </div>

    <!-- Content -->
    <div class="ob-body">
      {#if step === 0}
        <div class="ob-step">
          <div class="ob-emoji">👋</div>
          <h2>Olá{userName ? `, ${userName}` : ''}!</h2>
          <p class="ob-lead">Seu controle financeiro pessoal está pronto. Vamos fazer um tour rápido?</p>
          <div class="ob-feature-list">
            <div class="ob-feature">
              <span>💸</span>
              <div>
                <strong>Despesas e receitas</strong>
                <p>Registre todos os seus gastos e entradas do mês.</p>
              </div>
            </div>
            <div class="ob-feature">
              <span>💳</span>
              <div>
                <strong>Cartões de crédito</strong>
                <p>Gerencie faturas e parcelamentos automaticamente.</p>
              </div>
            </div>
            <div class="ob-feature">
              <span>📈</span>
              <div>
                <strong>Investimentos</strong>
                <p>Acompanhe aportes, saques e rendimentos.</p>
              </div>
            </div>
          </div>
        </div>

      {:else if step === 1}
        <div class="ob-step">
          <div class="ob-emoji">💡</div>
          <h2>Como funciona</h2>
          <div class="ob-steps-list">
            <div class="ob-step-item">
              <span class="ob-num">1</span>
              <div>
                <strong>Selecione o mês</strong>
                <p>Use os botões no topo para navegar entre meses. Cada mês tem seus próprios dados.</p>
              </div>
            </div>
            <div class="ob-step-item">
              <span class="ob-num">2</span>
              <div>
                <strong>Preencha o salário e saldo anterior</strong>
                <p>No início de cada mês, informe seu salário bruto e o saldo que sobrou do mês passado.</p>
              </div>
            </div>
            <div class="ob-step-item">
              <span class="ob-num">3</span>
              <div>
                <strong>Lance suas despesas</strong>
                <p>Adicione despesas nas seções abaixo. Use as categorias para organizar seus gastos.</p>
              </div>
            </div>
            <div class="ob-step-item">
              <span class="ob-num">4</span>
              <div>
                <strong>Acompanhe o resumo</strong>
                <p>Os cards no topo mostram receita, despesas e saldo final em tempo real.</p>
              </div>
            </div>
          </div>
        </div>

      {:else if step === 2}
        <div class="ob-step">
          <div class="ob-emoji">📱</div>
          <h2>Dicas de uso</h2>
          <div class="ob-tips">
            <div class="ob-tip">
              <span class="tip-icon">➕</span>
              <div>
                <strong>Botão flutuante (+)</strong>
                <p>Use o botão roxo no canto inferior direito para lançamentos rápidos — sem abrir seções.</p>
              </div>
            </div>
            <div class="ob-tip">
              <span class="tip-icon">🌙</span>
              <div>
                <strong>Modo escuro</strong>
                <p>Toque no ícone 🌙 no cabeçalho para ativar o tema escuro.</p>
              </div>
            </div>
            <div class="ob-tip">
              <span class="tip-icon">👁️</span>
              <div>
                <strong>Ocultar valores</strong>
                <p>Toque no 👁️ para esconder todos os valores — útil em lugares públicos.</p>
              </div>
            </div>
            <div class="ob-tip">
              <span class="tip-icon">🤖</span>
              <div>
                <strong>Bot do Telegram</strong>
                <p>Lance despesas diretamente pelo Telegram sem abrir o app. Configure em Perfil → Telegram.</p>
              </div>
            </div>
          </div>
        </div>

      {:else if step === 3}
        <div class="ob-step ob-final">
          <div class="ob-emoji big">🚀</div>
          <h2>Tudo pronto!</h2>
          <p class="ob-lead">Seu painel está configurado e pronto para uso. Comece lançando o salário do mês atual.</p>
          <div class="ob-checklist">
            <div class="ob-check">✅ Conta criada</div>
            <div class="ob-check">✅ Painel carregado</div>
            <div class="ob-check">⬜ Preencher salário do mês</div>
            <div class="ob-check">⬜ Lançar primeiras despesas</div>
          </div>
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <div class="ob-footer">
      {#if step > 0}
        <button class="ob-btn-back" on:click={prev}>← Voltar</button>
      {:else}
        <button class="ob-btn-skip" on:click={skip}>Pular</button>
      {/if}

      {#if step < totalSteps - 1}
        <button class="ob-btn-next" on:click={next}>Próximo →</button>
      {:else}
        <button class="ob-btn-finish" on:click={finish}>Começar! 🎉</button>
      {/if}
    </div>
  </div>
</div>

<style>
  .ob-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 2000;
    display: flex; align-items: center; justify-content: center;
    padding: 1rem;
  }

  .ob-modal {
    background: white;
    border-radius: 18px;
    width: 100%; max-width: 520px;
    max-height: 90vh;
    display: flex; flex-direction: column;
    box-shadow: 0 24px 64px rgba(0,0,0,0.35);
    overflow: hidden;
  }

  .ob-progress {
    display: flex; gap: 6px; justify-content: center;
    padding: 1rem 1.25rem 0.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  .ob-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: rgba(255,255,255,0.35);
    transition: all 0.2s;
  }
  .ob-dot.active { background: white; width: 24px; border-radius: 4px; }
  .ob-dot.done   { background: rgba(255,255,255,0.7); }

  .ob-body {
    flex: 1; overflow-y: auto;
    padding: 1.5rem 1.5rem 0.5rem;
  }

  .ob-step { display: flex; flex-direction: column; gap: 1rem; }

  .ob-emoji {
    font-size: 2.5rem; text-align: center;
    background: linear-gradient(135deg, #f5f7ff, #faf5ff);
    padding: 1rem; border-radius: 16px;
    border: 1px solid #e8eaff;
  }
  .ob-emoji.big { font-size: 3.5rem; padding: 1.5rem; }

  h2 { margin: 0; font-size: 1.3rem; color: #2a2a3e; text-align: center; }
  p { margin: 0; font-size: 0.9rem; color: #555; line-height: 1.5; }

  .ob-lead { text-align: center; font-size: 0.95rem; color: #666; }

  .ob-feature-list { display: flex; flex-direction: column; gap: 0.65rem; }
  .ob-feature {
    display: flex; gap: 0.75rem; align-items: flex-start;
    background: #f8f9ff; padding: 0.7rem; border-radius: 10px;
    border: 1px solid #eef0f8;
  }
  .ob-feature > span { font-size: 1.3rem; flex-shrink: 0; }
  .ob-feature strong { display: block; font-size: 0.88rem; color: #333; margin-bottom: 2px; }
  .ob-feature p { font-size: 0.8rem; color: #666; }

  .ob-steps-list { display: flex; flex-direction: column; gap: 0.75rem; }
  .ob-step-item { display: flex; gap: 0.75rem; align-items: flex-start; }
  .ob-num {
    width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; font-weight: 700; font-size: 0.8rem;
    display: flex; align-items: center; justify-content: center;
    margin-top: 1px;
  }
  .ob-step-item strong { display: block; font-size: 0.88rem; color: #333; margin-bottom: 2px; }
  .ob-step-item p { font-size: 0.8rem; color: #666; }

  .ob-tips { display: flex; flex-direction: column; gap: 0.65rem; }
  .ob-tip {
    display: flex; gap: 0.75rem; align-items: flex-start;
    padding: 0.65rem; border-radius: 10px;
    background: #fafbff; border: 1px solid #eef0f8;
  }
  .tip-icon { font-size: 1.2rem; flex-shrink: 0; }
  .ob-tip strong { display: block; font-size: 0.88rem; color: #333; margin-bottom: 2px; }
  .ob-tip p { font-size: 0.8rem; color: #666; }

  .ob-final { align-items: center; }
  .ob-checklist { display: flex; flex-direction: column; gap: 0.4rem; width: 100%; }
  .ob-check {
    padding: 0.55rem 0.85rem; border-radius: 8px;
    background: #f5f7ff; border: 1px solid #e8eaff;
    font-size: 0.88rem; color: #444;
  }

  .ob-footer {
    display: flex; gap: 0.5rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid #eee;
    background: #fafbfc;
  }
  .ob-btn-back, .ob-btn-skip {
    padding: 0.6rem 1rem;
    border: 1px solid #ddd; background: none;
    color: #777; border-radius: 8px;
    cursor: pointer; font-size: 0.9rem;
    white-space: nowrap;
  }
  .ob-btn-skip { border: none; color: #bbb; font-size: 0.85rem; }
  .ob-btn-next {
    flex: 1;
    padding: 0.6rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none; border-radius: 8px;
    cursor: pointer; font-weight: 600; font-size: 0.9rem;
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .ob-btn-next:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(102,126,234,0.4); }
  .ob-btn-finish {
    flex: 1;
    padding: 0.6rem;
    background: linear-gradient(135deg, #43a047, #2e7d32);
    color: white; border: none; border-radius: 8px;
    cursor: pointer; font-weight: 700; font-size: 0.95rem;
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .ob-btn-finish:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(67,160,71,0.4); }

  @media (max-width: 540px) {
    .ob-modal { max-height: 100vh; border-radius: 0; }
    .ob-body { padding: 1.25rem 1rem 0.5rem; }
    .ob-footer { padding: 0.75rem 1rem; }
  }

  /* Dark mode */
  :global([data-theme="dark"]) .ob-modal { background: #1e1e2e; }
  :global([data-theme="dark"]) h2 { color: #e0e0e8; }
  :global([data-theme="dark"]) p { color: #a0a0b8; }
  :global([data-theme="dark"]) .ob-lead { color: #9090a8; }
  :global([data-theme="dark"]) .ob-emoji { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .ob-feature { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .ob-feature strong { color: #e0e0e8; }
  :global([data-theme="dark"]) .ob-feature p { color: #9090a8; }
  :global([data-theme="dark"]) .ob-step-item strong { color: #e0e0e8; }
  :global([data-theme="dark"]) .ob-step-item p { color: #9090a8; }
  :global([data-theme="dark"]) .ob-tip { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .ob-tip strong { color: #e0e0e8; }
  :global([data-theme="dark"]) .ob-tip p { color: #9090a8; }
  :global([data-theme="dark"]) .ob-check { background: #252535; border-color: #3a3a52; color: #c0c0d0; }
  :global([data-theme="dark"]) .ob-footer { background: #252535; border-color: #3a3a52; }
  :global([data-theme="dark"]) .ob-btn-back { border-color: #3a3a52; color: #9090a8; }
  :global([data-theme="dark"]) .ob-btn-skip { color: #505070; }
</style>
