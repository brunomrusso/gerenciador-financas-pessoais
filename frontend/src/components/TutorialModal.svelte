<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  export let botUsername: string = 'SeuBot_bot'

  const dispatch = createEventDispatcher()
  const close = () => dispatch('close')

  $: botLink = `https://t.me/${botUsername.replace(/^@/, '')}`
</script>

<div class="overlay" on:click|self={close} role="dialog">
  <div class="modal">
    <header>
      <h2>📖 Como usar o bot do Telegram</h2>
      <button class="btn-close" on:click={close}>✕</button>
    </header>

    <div class="body">
      <section class="hero-step">
        <span class="emoji">🤖</span>
        <h3>Lance despesas e receitas direto do celular</h3>
        <p>Sem abrir o site. Em segundos. Tudo sincronizado com seu painel.</p>
      </section>

      <section>
        <h4>🔧 Configurar (1 vez só)</h4>
        <ol>
          <li>
            Abra o bot no Telegram:
            <a href={botLink} target="_blank" rel="noopener" class="bot-link">
              @{botUsername.replace(/^@/, '')}
            </a>
            e toque em <strong>Iniciar</strong>.
          </li>
          <li>
            Aqui no app, na seção <strong>🤖 Telegram</strong>, clique em
            <strong>Gerar código de vinculação</strong>.
          </li>
          <li>
            Copie o código de 6 dígitos e envie no bot:
            <code>/start 123456</code>
          </li>
          <li>✅ Pronto! Vinculado para sempre nesse celular.</li>
        </ol>
      </section>

      <section>
        <h4>💬 Comandos principais</h4>
        <table class="cmd-table">
          <tbody>
            <tr><td><code>/menu</code></td><td>Abre o menu com botões</td></tr>
            <tr><td><code>/saldo</code></td><td>Mostra saldo das suas contas</td></tr>
            <tr><td><code>/help</code></td><td>Exibe ajuda no próprio bot</td></tr>
            <tr><td><code>/unlink</code></td><td>Desvincula este celular</td></tr>
          </tbody>
        </table>
      </section>

      <section>
        <h4>💸 Exemplo: lançar uma despesa</h4>
        <ol class="example">
          <li>Envie <code>/menu</code></li>
          <li>Toque em <strong>💸 Despesa</strong></li>
          <li>Escolha a conta (Nubank, Caixa…)</li>
          <li>Digite o valor: <code>45.90</code></li>
          <li>Digite a descrição: <em>Almoço</em></li>
          <li>Escolha a categoria</li>
          <li>Toque em <strong>Confirmar</strong> ✅</li>
        </ol>
      </section>

      <section class="faq">
        <h4>❓ Perguntas frequentes</h4>
        <details>
          <summary>O bot é seguro?</summary>
          <p>Sim. Cada vínculo usa código único e expirável (10 min). Ninguém vê os dados dos outros.</p>
        </details>
        <details>
          <summary>Posso usar em mais de um celular?</summary>
          <p>Apenas um por vez. Vincular outro celular desvincula o anterior automaticamente.</p>
        </details>
        <details>
          <summary>Posso editar o que lancei pelo bot?</summary>
          <p>Sim — abra o app web e edite normalmente. É um lançamento como qualquer outro.</p>
        </details>
        <details>
          <summary>O bot demora pra responder?</summary>
          <p>Pode demorar até 30s na primeira interação do dia (servidor "acordando"). Depois fica instantâneo.</p>
        </details>
      </section>
    </div>

    <footer>
      <a href={botLink} target="_blank" rel="noopener" class="btn-primary">
        🤖 Abrir bot no Telegram
      </a>
      <button class="btn-secondary" on:click={close}>Fechar</button>
    </footer>
  </div>
</div>

<style>
  .overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.55);
    display: flex; align-items: center; justify-content: center;
    z-index: 1100; padding: 1rem;
  }
  .modal {
    background: white; border-radius: 14px;
    width: 100%; max-width: 620px;
    max-height: 92vh;
    display: flex; flex-direction: column;
    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    overflow: hidden;
  }
  header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid #eee;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  header h2 { margin: 0; font-size: 1.1rem; }
  .btn-close {
    background: rgba(255,255,255,0.2); border: none;
    color: white; font-size: 1.1rem;
    width: 32px; height: 32px; border-radius: 8px;
    cursor: pointer;
  }
  .btn-close:hover { background: rgba(255,255,255,0.35); }

  .body {
    padding: 1.25rem;
    overflow-y: auto;
    flex: 1;
  }
  section { margin-bottom: 1.5rem; }
  h3 { margin: 0.4rem 0 0.5rem; font-size: 1.05rem; color: #333; }
  h4 { margin: 0 0 0.6rem; font-size: 0.95rem; color: #444; }
  p { margin: 0.4rem 0; line-height: 1.5; color: #555; font-size: 0.9rem; }

  .hero-step {
    text-align: center;
    background: linear-gradient(135deg, #f5f7ff, #faf5ff);
    padding: 1.5rem 1rem;
    border-radius: 12px;
    border: 1px solid #e8eaff;
  }
  .hero-step .emoji { font-size: 2.5rem; }
  .hero-step h3 { font-size: 1.15rem; }
  .hero-step p { color: #666; }

  ol { margin: 0; padding-left: 1.4rem; }
  ol li {
    margin: 0.5rem 0; line-height: 1.5;
    color: #555; font-size: 0.9rem;
  }
  ol.example li { color: #444; }
  code {
    background: #eef0f9; color: #5568d8;
    padding: 2px 7px; border-radius: 4px;
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: 0.85em;
  }
  strong { color: #333; }
  em { color: #667eea; font-style: normal; font-weight: 500; }

  .bot-link {
    display: inline-block;
    color: #667eea; text-decoration: none;
    background: #eef0f9; padding: 2px 10px;
    border-radius: 6px; margin: 0 4px;
    font-weight: 600; font-size: 0.88rem;
  }
  .bot-link:hover { background: #667eea; color: white; }

  .cmd-table {
    width: 100%;
    border-collapse: collapse;
    background: #fafbfc;
    border-radius: 8px;
    overflow: hidden;
  }
  .cmd-table td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid #eef0f5;
    font-size: 0.88rem;
    color: #555;
  }
  .cmd-table tr:last-child td { border-bottom: none; }
  .cmd-table td:first-child { width: 110px; }

  .faq details {
    background: #fafbfc;
    border: 1px solid #eef0f5;
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    margin-bottom: 0.5rem;
  }
  .faq details[open] { background: #f5f7ff; border-color: #c5cae9; }
  .faq summary {
    cursor: pointer;
    font-weight: 600;
    font-size: 0.88rem;
    color: #444;
    list-style: none;
    position: relative;
    padding-right: 1.5rem;
  }
  .faq summary::after {
    content: '+';
    position: absolute; right: 0; top: 0;
    color: #667eea; font-size: 1.1rem; line-height: 1;
  }
  .faq details[open] summary::after { content: '−'; }
  .faq details p {
    margin: 0.5rem 0 0;
    font-size: 0.85rem;
    color: #666;
  }

  footer {
    display: flex; gap: 0.75rem;
    padding: 1rem 1.25rem;
    border-top: 1px solid #eee;
    background: #fafbfc;
    flex-wrap: wrap;
  }
  .btn-primary {
    flex: 1;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none;
    text-align: center;
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(102,126,234,0.4);
  }
  .btn-secondary {
    background: #eef0f5;
    color: #555; border: none;
    padding: 0.7rem 1.2rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.9rem;
  }

  @media (max-width: 560px) {
    .modal { max-height: 100vh; border-radius: 0; }
    footer { flex-direction: column; }
    .btn-primary, .btn-secondary { width: 100%; }
  }

  :global([data-theme="dark"]) .modal { background: #1e1e1e; }
  :global([data-theme="dark"]) .body { color: #ddd; }
  :global([data-theme="dark"]) h3,
  :global([data-theme="dark"]) h4 { color: #eee; }
  :global([data-theme="dark"]) p,
  :global([data-theme="dark"]) ol li { color: #bbb; }
  :global([data-theme="dark"]) strong { color: #eee; }
  :global([data-theme="dark"]) .hero-step { background: #2a2a3a; border-color: #3d3d50; }
  :global([data-theme="dark"]) .cmd-table { background: #2a2a2a; }
  :global([data-theme="dark"]) .cmd-table td { border-color: #333; color: #ccc; }
  :global([data-theme="dark"]) .faq details { background: #2a2a2a; border-color: #333; }
  :global([data-theme="dark"]) .faq details[open] { background: #2a2a3a; border-color: #3d3d50; }
  :global([data-theme="dark"]) .faq summary { color: #ddd; }
  :global([data-theme="dark"]) .faq details p { color: #bbb; }
  :global([data-theme="dark"]) footer { background: #2a2a2a; border-color: #333; }
  :global([data-theme="dark"]) .btn-secondary { background: #333; color: #ddd; }
  :global([data-theme="dark"]) code { background: #2a2a3a; color: #b3c0ff; }
  :global([data-theme="dark"]) .bot-link { background: #2a2a3a; color: #b3c0ff; }
</style>
