<script lang="ts">
  import { login, register, authStore } from '../stores/auth'

  let isLogin = true
  let nome = ''
  let email = ''
  let password = ''

  let showForgot = false
  let forgotEmail = ''
  let forgotMsg = ''
  let forgotLoading = false

  $: errorMsg = $authStore.error
  $: loading = $authStore.loading

  async function handleSubmit() {
    if (isLogin) {
      await login(email, password)
    } else {
      await register(email, password, nome)
    }
  }

  async function submitForgot() {
    forgotLoading = true
    forgotMsg = ''
    try {
      await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail }),
      })
      forgotMsg = 'Se o email estiver cadastrado, você receberá instruções em alguns minutos.'
    } catch {
      forgotMsg = 'Erro ao enviar. Tente novamente.'
    } finally {
      forgotLoading = false
    }
  }
</script>

<div class="login-page">
  <!-- Lado esquerdo: hero/branding -->
  <aside class="hero">
    <div class="hero-inner">
      <img src="/assets/logo.png" alt="CashFlow" class="hero-logo" />
      <h1>CashFlow</h1>
      <p class="tagline">Controle financeiro completo, simples e bonito.</p>

      <ul class="features">
        <li>
          <span class="ico">📊</span>
          <div>
            <strong>Visão completa</strong>
            <small>Receitas, despesas, cartões e investimentos num só lugar</small>
          </div>
        </li>
        <li>
          <span class="ico">💳</span>
          <div>
            <strong>Múltiplas contas</strong>
            <small>Divida faturas entre Nubank, Caixa e mais</small>
          </div>
        </li>
        <li>
          <span class="ico">🤖</span>
          <div>
            <strong>Bot Telegram</strong>
            <small>Lance gastos pelo celular em segundos</small>
          </div>
        </li>
        <li>
          <span class="ico">🎯</span>
          <div>
            <strong>Orçamentos</strong>
            <small>Defina metas por categoria e tags</small>
          </div>
        </li>
      </ul>

      <p class="copy">Feito por Bruno · 100% gratuito</p>
    </div>
  </aside>

  <!-- Lado direito: formulario -->
  <main class="form-side">
    <div class="form-card">
      <img src="/assets/logo.png" alt="CashFlow" class="form-logo" />
      <h2>{isLogin ? 'Bem-vindo de volta' : 'Criar conta'}</h2>
      <p class="sub">{isLogin ? 'Acesse seu painel financeiro.' : 'Comece a controlar suas finanças hoje.'}</p>

      <div class="tabs">
        <button class:active={isLogin} on:click={() => (isLogin = true)} type="button">Entrar</button>
        <button class:active={!isLogin} on:click={() => (isLogin = false)} type="button">Cadastrar</button>
      </div>

      {#if !showForgot}
        <form on:submit|preventDefault={handleSubmit}>
          {#if !isLogin}
            <label>
              Nome <span class="opt">(opcional)</span>
              <input type="text" bind:value={nome} placeholder="Como devemos te chamar?" />
            </label>
          {/if}
          <label>
            Email
            <input type="email" bind:value={email} required placeholder="seu@email.com" />
          </label>
          <label>
            Senha
            <input type="password" bind:value={password} required placeholder="Mínimo 6 caracteres" />
          </label>

          {#if errorMsg}<div class="err">{errorMsg}</div>{/if}

          <button type="submit" class="btn-primary" disabled={loading}>
            {loading ? 'Carregando...' : isLogin ? 'Entrar' : 'Criar conta'}
          </button>

          {#if isLogin}
            <p class="forgot">
              <button type="button" class="link" on:click={() => (showForgot = true)}>
                Esqueci minha senha
              </button>
            </p>
          {/if}
        </form>
      {:else}
        <form on:submit|preventDefault={submitForgot}>
          <p class="info">Digite seu email cadastrado e enviaremos um link para redefinir sua senha.</p>
          <label>
            Email
            <input type="email" bind:value={forgotEmail} required placeholder="seu@email.com" />
          </label>
          {#if forgotMsg}<div class="ok">{forgotMsg}</div>{/if}
          <button type="submit" class="btn-primary" disabled={forgotLoading}>
            {forgotLoading ? 'Enviando...' : 'Enviar link de recuperação'}
          </button>
          <p class="forgot">
            <button type="button" class="link" on:click={() => (showForgot = false)}>← Voltar para o login</button>
          </p>
        </form>
      {/if}
    </div>
  </main>
</div>

<style>
  .login-page {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    background: white;
  }

  /* Hero */
  .hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem 2.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.15), transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(255,255,255,0.1), transparent 50%);
    pointer-events: none;
  }
  .hero-inner { max-width: 460px; position: relative; z-index: 1; }
  .hero-logo {
    width: 110px; height: 110px;
    object-fit: contain;
    background: white;
    border-radius: 24px;
    padding: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    margin-bottom: 1.5rem;
  }
  .hero h1 {
    font-size: 3rem;
    margin: 0 0 0.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
  }
  .tagline { font-size: 1.1rem; opacity: 0.92; margin: 0 0 2.5rem; line-height: 1.5; }

  .features { list-style: none; padding: 0; margin: 0 0 2.5rem; display: flex; flex-direction: column; gap: 1rem; }
  .features li {
    display: flex; gap: 0.9rem; align-items: flex-start;
    background: rgba(255,255,255,0.1);
    padding: 0.85rem 1rem;
    border-radius: 12px;
    backdrop-filter: blur(10px);
  }
  .features .ico { font-size: 1.5rem; flex-shrink: 0; }
  .features strong { display: block; font-size: 0.95rem; margin-bottom: 2px; }
  .features small { opacity: 0.85; font-size: 0.82rem; line-height: 1.4; }
  .copy { font-size: 0.78rem; opacity: 0.7; margin: 0; }

  /* Form */
  .form-side {
    display: flex; align-items: center; justify-content: center;
    padding: 3rem 2rem;
    background: #fafbfc;
  }
  .form-card {
    width: 100%;
    max-width: 400px;
    background: white;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  }
  .form-logo { display: none; }
  h2 { margin: 0 0 0.4rem; color: #333; font-size: 1.5rem; }
  .sub { color: #888; font-size: 0.9rem; margin: 0 0 1.5rem; }

  .tabs {
    display: grid; grid-template-columns: 1fr 1fr;
    background: #f0f1f5;
    padding: 4px;
    border-radius: 10px;
    margin-bottom: 1.5rem;
  }
  .tabs button {
    background: none; border: none;
    padding: 0.55rem;
    border-radius: 7px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    color: #777;
    transition: all 0.18s;
  }
  .tabs button.active { background: white; color: #667eea; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }

  form { display: flex; flex-direction: column; gap: 0.9rem; }
  label { display: flex; flex-direction: column; gap: 6px; font-size: 0.82rem; color: #555; font-weight: 500; }
  .opt { color: #aaa; font-weight: 400; font-size: 0.78rem; }
  input {
    padding: 0.75rem 0.85rem;
    border: 1px solid #e0e3eb;
    border-radius: 8px;
    font-size: 0.92rem;
    background: white;
    transition: all 0.15s;
  }
  input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }
  .err { background: #fee; color: #c33; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.82rem; }
  .ok { background: #e8f5e9; color: #2e7d32; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.82rem; }
  .info { font-size: 0.85rem; color: #666; margin: 0 0 0.5rem; line-height: 1.5; }
  .btn-primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none;
    padding: 0.85rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 0.5rem;
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(102,126,234,0.4); }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

  .forgot { text-align: center; margin: 0.5rem 0 0; }
  .link {
    background: none; border: none; color: #667eea;
    cursor: pointer; font-size: 0.85rem;
    text-decoration: underline;
  }

  @media (max-width: 880px) {
    .login-page { grid-template-columns: 1fr; }
    .hero { padding: 2rem 1.5rem; min-height: auto; }
    .hero h1 { font-size: 2.2rem; }
    .hero-logo { width: 80px; height: 80px; }
    .features { gap: 0.6rem; margin-bottom: 1.5rem; }
    .features li { padding: 0.6rem 0.8rem; }
    .form-side { padding: 2rem 1rem; }
    .form-card { padding: 2rem 1.5rem; box-shadow: none; }
  }
</style>
