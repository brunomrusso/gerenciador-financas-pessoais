<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte'
  import { authStore, loadUser } from '../stores/auth'
  import TutorialModal from './TutorialModal.svelte'

  const BOT_USERNAME = (import.meta.env.VITE_TELEGRAM_BOT_USERNAME as string) || 'meucashflow_bot'

  const dispatch = createEventDispatcher()
  const close = () => dispatch('close')

  let showTutorial = false

  let nome = ''
  let currentPassword = ''
  let newPassword = ''
  let confirmPassword = ''

  let savingProfile = false
  let savingPassword = false
  let msgProfile = ''
  let msgPassword = ''
  let errProfile = ''
  let errPassword = ''

  let exportingData = false
  let deletePassword = ''
  let deletingAccount = false
  let errDelete = ''
  let showDeleteConfirm = false

  let tgCode: string | null = null
  let tgStatus: { linked: boolean; username: string | null } | null = null
  let tgLoading = false
  let tgError = ''

  const auth = () => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`,
  })

  $: nome = $authStore.user?.nome || ''

  onMount(() => {
    fetchTelegramStatus()
  })

  async function saveProfile() {
    savingProfile = true
    msgProfile = ''
    errProfile = ''
    try {
      const r = await fetch('/api/auth/me', {
        method: 'PUT',
        headers: auth(),
        body: JSON.stringify({ nome }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error || 'Erro ao salvar')
      msgProfile = 'Nome atualizado!'
      await loadUser()
    } catch (e: any) {
      errProfile = e.message
    } finally {
      savingProfile = false
    }
  }

  async function changePassword() {
    if (newPassword !== confirmPassword) {
      errPassword = 'Senhas novas não conferem'
      return
    }
    if (newPassword.length < 6) {
      errPassword = 'Mínimo de 6 caracteres'
      return
    }
    savingPassword = true
    msgPassword = ''
    errPassword = ''
    try {
      const r = await fetch('/api/auth/me', {
        method: 'PUT',
        headers: auth(),
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error || 'Erro ao trocar senha')
      msgPassword = 'Senha alterada com sucesso!'
      currentPassword = ''
      newPassword = ''
      confirmPassword = ''
    } catch (e: any) {
      errPassword = e.message
    } finally {
      savingPassword = false
    }
  }

  async function fetchTelegramStatus() {
    try {
      const r = await fetch('/api/telegram/status', { headers: auth() })
      if (r.ok) tgStatus = await r.json()
    } catch {}
  }

  async function generateCode() {
    tgLoading = true
    tgError = ''
    try {
      const r = await fetch('/api/telegram/link-code', { method: 'POST', headers: auth() })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error || 'Erro')
      tgCode = data.code
    } catch (e: any) {
      tgError = e.message
    } finally {
      tgLoading = false
    }
  }

  async function unlink() {
    if (!confirm('Desvincular Telegram?')) return
    try {
      await fetch('/api/telegram/unlink', { method: 'DELETE', headers: auth() })
      tgStatus = { linked: false, username: null }
      tgCode = null
    } catch {}
  }

  async function exportData() {
    exportingData = true
    try {
      const r = await fetch('/api/auth/export', { headers: auth() })
      const data = await r.json()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `cashflow-dados-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e: any) {
      alert('Erro ao exportar: ' + e.message)
    } finally {
      exportingData = false
    }
  }

  async function deleteAccount() {
    if (!deletePassword) { errDelete = 'Informe sua senha para confirmar.'; return }
    deletingAccount = true
    errDelete = ''
    try {
      const r = await fetch('/api/auth/me', {
        method: 'DELETE',
        headers: auth(),
        body: JSON.stringify({ password: deletePassword })
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error || 'Erro ao deletar conta')
      localStorage.removeItem('token')
      window.location.href = '/'
    } catch (e: any) {
      errDelete = e.message
    } finally {
      deletingAccount = false
    }
  }
</script>

<div class="overlay" on:click|self={close}>
  <div class="modal">
    <header>
      <h2>👤 Meu Perfil</h2>
      <button class="btn-close" on:click={close}>✕</button>
    </header>

    <div class="body">
      <section>
        <h3>Informações pessoais</h3>
        <label>
          Nome
          <input type="text" bind:value={nome} placeholder="Seu nome" />
        </label>
        <label>
          Email
          <input type="email" value={$authStore.user?.email || ''} disabled />
        </label>
        {#if msgProfile}<div class="ok">{msgProfile}</div>{/if}
        {#if errProfile}<div class="err">{errProfile}</div>{/if}
        <button class="btn-primary" on:click={saveProfile} disabled={savingProfile}>
          {savingProfile ? 'Salvando...' : 'Salvar nome'}
        </button>
      </section>

      <section>
        <h3>🔒 Trocar senha</h3>
        <label>
          Senha atual
          <input type="password" bind:value={currentPassword} />
        </label>
        <label>
          Nova senha (mín. 6)
          <input type="password" bind:value={newPassword} />
        </label>
        <label>
          Confirmar nova senha
          <input type="password" bind:value={confirmPassword} />
        </label>
        {#if msgPassword}<div class="ok">{msgPassword}</div>{/if}
        {#if errPassword}<div class="err">{errPassword}</div>{/if}
        <button class="btn-primary" on:click={changePassword} disabled={savingPassword || !currentPassword || !newPassword}>
          {savingPassword ? 'Trocando...' : 'Trocar senha'}
        </button>
      </section>

      <section class="danger-zone">
        <h3>⚙️ Dados da conta</h3>
        <p class="hint">Baixe uma cópia de todos os seus dados financeiros em formato JSON.</p>
        <button class="btn-export" on:click={exportData} disabled={exportingData}>
          {exportingData ? 'Exportando...' : '📤 Exportar todos os dados'}
        </button>

        <div class="delete-section">
          {#if !showDeleteConfirm}
            <button class="btn-delete-toggle" on:click={() => showDeleteConfirm = true}>
              🗑️ Deletar minha conta
            </button>
          {:else}
            <div class="delete-confirm">
              <p class="warn">⚠️ Ação irreversível. Todos os seus dados serão permanentemente apagados.</p>
              <label class="del-label">
                Confirme sua senha
                <input type="password" bind:value={deletePassword} placeholder="Senha atual" />
              </label>
              {#if errDelete}<div class="err">{errDelete}</div>{/if}
              <div class="del-actions">
                <button class="btn-cancel-del" on:click={() => { showDeleteConfirm = false; deletePassword = ''; errDelete = '' }}>Cancelar</button>
                <button class="btn-danger" on:click={deleteAccount} disabled={deletingAccount || !deletePassword}>
                  {deletingAccount ? 'Deletando...' : '🗑️ Confirmar exclusão'}
                </button>
              </div>
            </div>
          {/if}
        </div>
      </section>

      <section>
        <div class="tg-header">
          <h3>🤖 Telegram</h3>
          <button class="btn-help" on:click={() => (showTutorial = true)} title="Como usar o bot">
            📖 Como usar?
          </button>
        </div>
        {#if tgStatus?.linked}
          <p class="ok">✅ Vinculado{tgStatus.username ? ` como @${tgStatus.username}` : ''}</p>
          <button class="btn-danger" on:click={unlink}>Desvincular</button>
        {:else}
          <p class="hint">Vincule seu Telegram para lançar despesas/receitas pelo bot.</p>
          {#if tgCode}
            <div class="code-box">
              <div class="code">{tgCode}</div>
              <p class="hint">No Telegram, abra o bot e envie:<br><code>/start {tgCode}</code></p>
              <p class="hint-sm">Válido por 10 minutos.</p>
            </div>
          {:else}
            <button class="btn-primary" on:click={generateCode} disabled={tgLoading}>
              {tgLoading ? 'Gerando...' : 'Gerar código de vinculação'}
            </button>
          {/if}
          {#if tgError}<div class="err">{tgError}</div>{/if}
        {/if}
      </section>
    </div>
  </div>
</div>

{#if showTutorial}
  <TutorialModal botUsername={BOT_USERNAME} on:close={() => (showTutorial = false)} />
{/if}

<style>
  .overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.5);
    display: flex; align-items: center; justify-content: center;
    z-index: 1000; padding: 1rem;
  }
  .modal {
    background: white; border-radius: 12px;
    width: 100%; max-width: 560px;
    max-height: 90vh; overflow-y: auto;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
  }
  header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.25rem; border-bottom: 1px solid #eee;
    position: sticky; top: 0; background: white; z-index: 1;
  }
  h2 { margin: 0; font-size: 1.15rem; color: #333; }
  .btn-close { background: none; border: none; font-size: 1.3rem; cursor: pointer; color: #999; }
  .body { padding: 1.25rem; display: flex; flex-direction: column; gap: 1.5rem; }
  section {
    background: #fafbfc;
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid #eef0f5;
  }
  section h3 { margin: 0 0 0.75rem; font-size: 0.95rem; color: #555; }
  label { display: flex; flex-direction: column; gap: 4px; font-size: 0.82rem; color: #555; margin-bottom: 0.6rem; }
  input {
    padding: 0.55rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.9rem;
    background: white;
  }
  input:disabled { background: #f5f5f5; color: #888; }
  input:focus { outline: none; border-color: #667eea; }
  .btn-primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 6px;
    cursor: pointer; font-weight: 600;
    font-size: 0.875rem;
    margin-top: 0.5rem;
  }
  .btn-primary:hover { transform: translateY(-1px); }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
  .btn-danger {
    background: #f44336; color: white;
    border: none; padding: 0.5rem 1rem;
    border-radius: 6px; cursor: pointer;
    font-size: 0.85rem;
  }
  .btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }
  .btn-export {
    background: #e8f5e9; color: #2e7d32;
    border: 1px solid #a5d6a7; padding: 0.5rem 1rem;
    border-radius: 6px; cursor: pointer;
    font-size: 0.85rem; font-weight: 600;
    margin-bottom: 0.75rem;
  }
  .btn-export:hover { background: #c8e6c9; }
  .btn-export:disabled { opacity: 0.6; cursor: not-allowed; }
  .delete-section { margin-top: 0.25rem; }
  .btn-delete-toggle {
    background: none; border: 1px solid #ffcdd2;
    color: #c62828; padding: 0.45rem 1rem;
    border-radius: 6px; cursor: pointer;
    font-size: 0.85rem;
  }
  .btn-delete-toggle:hover { background: #fff5f5; }
  .delete-confirm {
    background: #fff5f5; border: 1px solid #ffcdd2;
    border-radius: 8px; padding: 0.85rem;
    display: flex; flex-direction: column; gap: 0.6rem;
  }
  .warn { color: #c62828; font-size: 0.83rem; font-weight: 600; margin: 0; }
  .del-label { display: flex; flex-direction: column; gap: 4px; font-size: 0.82rem; color: #555; }
  .del-actions { display: flex; gap: 0.5rem; }
  .btn-cancel-del {
    padding: 0.45rem 0.85rem;
    border: 1px solid #ddd; background: none;
    color: #777; border-radius: 6px; cursor: pointer;
    font-size: 0.85rem;
  }
  .ok { color: #2e7d32; font-size: 0.85rem; margin: 0.25rem 0; }
  .err { color: #c62828; font-size: 0.85rem; margin: 0.25rem 0; }
  .hint { color: #777; font-size: 0.83rem; margin: 0 0 0.5rem; }
  .hint-sm { color: #999; font-size: 0.75rem; margin: 0.4rem 0 0; }
  code { background: #eef; color: #5568d8; padding: 2px 6px; border-radius: 4px; }
  .code-box {
    background: white; border: 2px dashed #667eea;
    padding: 1rem; border-radius: 8px; text-align: center;
    margin-top: 0.5rem;
  }
  .code {
    font-size: 2rem; font-weight: 700; letter-spacing: 0.4rem;
    color: #667eea; font-family: 'Fira Code', monospace;
  }

  :global([data-theme="dark"]) .modal { background: #1e1e1e; }
  :global([data-theme="dark"]) header { border-color: #333; background: #1e1e1e; }
  :global([data-theme="dark"]) h2 { color: #eee; }
  :global([data-theme="dark"]) section { background: #2a2a2a; border-color: #333; }
  :global([data-theme="dark"]) section h3 { color: #ccc; }
  :global([data-theme="dark"]) label { color: #aaa; }
  :global([data-theme="dark"]) input { background: #1e1e1e; color: #ddd; border-color: #444; }
  :global([data-theme="dark"]) input:disabled { background: #2a2a2a; color: #777; }
  :global([data-theme="dark"]) .code-box { background: #1e1e1e; }

  .tg-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.6rem;
  }
  .tg-header h3 { margin: 0; }
  .btn-help {
    background: #eef0f9;
    color: #5568d8;
    border: 1px solid #c5cae9;
    padding: 0.3rem 0.7rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
  }
  .btn-help:hover {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }
  :global([data-theme="dark"]) .btn-help { background: #2a2a3a; color: #b3c0ff; border-color: #3d3d50; }
</style>
