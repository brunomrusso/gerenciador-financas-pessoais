<script lang="ts">
  export let token: string

  let newPassword = ''
  let confirm = ''
  let loading = false
  let msg = ''
  let err = ''

  async function submit() {
    err = ''
    msg = ''
    if (newPassword !== confirm) {
      err = 'As senhas não conferem'
      return
    }
    if (newPassword.length < 6) {
      err = 'Mínimo de 6 caracteres'
      return
    }
    loading = true
    try {
      const r = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error || 'Erro')
      msg = 'Senha redefinida! Redirecionando para login...'
      setTimeout(() => { window.location.href = '/' }, 2000)
    } catch (e: any) {
      err = e.message
    } finally {
      loading = false
    }
  }
</script>

<div class="rp-wrap">
  <div class="rp-card">
    <img src="/assets/logo.png" alt="CashFlow" class="logo" />
    <h1>Nova senha</h1>
    <p class="sub">Defina uma nova senha para sua conta CashFlow.</p>

    <form on:submit|preventDefault={submit}>
      <label>
        Nova senha
        <input type="password" bind:value={newPassword} placeholder="Mínimo 6 caracteres" />
      </label>
      <label>
        Confirmar senha
        <input type="password" bind:value={confirm} placeholder="Repita a senha" />
      </label>

      {#if err}<div class="err">{err}</div>{/if}
      {#if msg}<div class="ok">{msg}</div>{/if}

      <button type="submit" class="btn-primary" disabled={loading || !newPassword || !confirm}>
        {loading ? 'Salvando...' : 'Redefinir senha'}
      </button>

      <p class="link"><a href="/">← Voltar para o login</a></p>
    </form>
  </div>
</div>

<style>
  .rp-wrap {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
  }
  .rp-card {
    background: white;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    max-width: 420px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    text-align: center;
  }
  .logo { width: 72px; height: 72px; object-fit: contain; margin-bottom: 0.75rem; }
  h1 { margin: 0; font-size: 1.5rem; color: #333; }
  .sub { color: #777; margin: 0.5rem 0 1.5rem; font-size: 0.9rem; }
  form { display: flex; flex-direction: column; gap: 1rem; text-align: left; }
  label { display: flex; flex-direction: column; gap: 6px; font-size: 0.85rem; color: #555; }
  input {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 0.95rem;
  }
  input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }
  .err { background: #fee; color: #c33; padding: 0.6rem; border-radius: 6px; font-size: 0.85rem; }
  .ok { background: #e8f5e9; color: #2e7d32; padding: 0.6rem; border-radius: 6px; font-size: 0.85rem; }
  .btn-primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none;
    padding: 0.85rem; border-radius: 8px;
    font-weight: 600; cursor: pointer; font-size: 0.95rem;
  }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
  .link { text-align: center; margin: 0; font-size: 0.85rem; }
  .link a { color: #667eea; text-decoration: none; }
</style>
