<script lang="ts">
  import { login, register } from '../stores/auth'

  let email = ''
  let password = ''
  let isRegistering = false
  let loading = false
  let error = ''

  const handleSubmit = async () => {
    if (!email || !password) {
      error = 'Email e senha são obrigatórios'
      return
    }

    loading = true
    error = ''

    if (isRegistering) {
      await register(email, password)
    } else {
      await login(email, password)
    }

    loading = false
  }

  const toggleMode = () => {
    isRegistering = !isRegistering
    error = ''
  }
</script>

<div class="login-container">
  <div class="login-card">
    <h1>Controle Financeiro</h1>
    <p class="subtitle">{isRegistering ? 'Criar Conta' : 'Fazer Login'}</p>

    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="seu@email.com"
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="password">Senha</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          placeholder="••••••••"
          disabled={loading}
        />
      </div>

      {#if error}
        <div class="error-message">{error}</div>
      {/if}

      <button type="submit" disabled={loading} class="btn-primary">
        {loading ? 'Carregando...' : isRegistering ? 'Registrar' : 'Entrar'}
      </button>
    </form>

    <p class="toggle-text">
      {isRegistering ? 'Já tem conta?' : 'Não tem conta?'}
      <button type="button" on:click={toggleMode} class="toggle-btn">
        {isRegistering ? 'Fazer login' : 'Registrar'}
      </button>
    </p>
  </div>
</div>

<style>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .login-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    width: 100%;
    max-width: 400px;
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 0.5rem;
  }

  .subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    color: #333;
    font-weight: 500;
  }

  input {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
    transition: border-color 0.3s;
  }

  input:focus {
    outline: none;
    border-color: #667eea;
  }

  input:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
  }

  .error-message {
    background-color: #fee;
    color: #c33;
    padding: 0.75rem;
    border-radius: 5px;
    font-size: 0.9rem;
  }

  .btn-primary {
    padding: 0.75rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
  }

  .btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .toggle-text {
    text-align: center;
    color: #666;
    font-size: 0.9rem;
  }

  .toggle-btn {
    background: none;
    border: none;
    color: #667eea;
    cursor: pointer;
    font-weight: 600;
    padding: 0;
    text-decoration: underline;
  }

  .toggle-btn:hover {
    color: #764ba2;
  }
</style>
