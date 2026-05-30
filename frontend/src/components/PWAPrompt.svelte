<script lang="ts">
  import { onMount } from 'svelte'

  let updateAvailable = false
  let installPrompt: any = null
  let canInstall = false
  let installed = false

  let updateSW: ((reload?: boolean) => Promise<void>) | null = null

  onMount(async () => {
    // Detecta se ja esta rodando como PWA instalado
    if (window.matchMedia('(display-mode: standalone)').matches ||
        (window.navigator as any).standalone === true) {
      installed = true
    }

    // Captura evento de instalacao (Chrome/Edge/Android)
    window.addEventListener('beforeinstallprompt', (e: Event) => {
      e.preventDefault()
      installPrompt = e
      // Nao mostra automaticamente para evitar incomodar; usuario clica no botao
      const dismissed = localStorage.getItem('pwa_install_dismissed')
      if (!dismissed && !installed) canInstall = true
    })

    window.addEventListener('appinstalled', () => {
      installed = true
      canInstall = false
      installPrompt = null
    })

    // Registra service worker e detecta atualizacao
    try {
      const { registerSW } = await import('virtual:pwa-register')
      updateSW = registerSW({
        onNeedRefresh() {
          updateAvailable = true
        },
        onOfflineReady() {
          console.log('[PWA] App pronto para uso offline')
        },
      })
    } catch (e) {
      // virtual module so existe em build com VitePWA
    }
  })

  const install = async () => {
    if (!installPrompt) return
    installPrompt.prompt()
    const { outcome } = await installPrompt.userChoice
    if (outcome === 'accepted') {
      installed = true
    }
    installPrompt = null
    canInstall = false
  }

  const dismiss = () => {
    canInstall = false
    localStorage.setItem('pwa_install_dismissed', '1')
  }

  const applyUpdate = () => {
    if (updateSW) updateSW(true)
    updateAvailable = false
  }
</script>

{#if updateAvailable}
  <div class="pwa-toast update">
    <span>🔄 Nova versão disponível</span>
    <button class="btn-update" on:click={applyUpdate}>Atualizar</button>
  </div>
{/if}

{#if canInstall && !installed}
  <div class="pwa-toast install">
    <div class="install-text">
      <strong>📱 Instalar CashFlow</strong>
      <small>Acesse direto da tela inicial, sem navegador</small>
    </div>
    <div class="install-actions">
      <button class="btn-install" on:click={install}>Instalar</button>
      <button class="btn-dismiss" on:click={dismiss} title="Dispensar">✕</button>
    </div>
  </div>
{/if}

<style>
  .pwa-toast {
    position: fixed;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.18);
    padding: 0.85rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    z-index: 1200;
    max-width: 92vw;
    width: max-content;
    animation: slideUp 0.25s ease;
  }
  @keyframes slideUp {
    from { transform: translate(-50%, 30px); opacity: 0; }
    to { transform: translate(-50%, 0); opacity: 1; }
  }

  .pwa-toast.update {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-color: transparent;
    font-size: 0.88rem;
    font-weight: 500;
  }

  .install-text { display: flex; flex-direction: column; gap: 2px; }
  .install-text strong { font-size: 0.92rem; color: #333; }
  .install-text small { font-size: 0.75rem; color: #777; }

  .install-actions { display: flex; gap: 0.4rem; align-items: center; }

  .btn-install {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.85rem;
    white-space: nowrap;
  }
  .btn-update {
    background: white;
    color: #667eea;
    border: none;
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.85rem;
  }
  .btn-dismiss {
    background: #f5f5f7;
    border: none;
    width: 32px; height: 32px;
    border-radius: 50%;
    cursor: pointer;
    color: #666;
    font-size: 0.8rem;
  }
  .btn-dismiss:hover { background: #e8e8ee; }

  @media (max-width: 480px) {
    .pwa-toast { width: calc(100vw - 1.5rem); max-width: none; }
  }

  :global([data-theme="dark"]) .pwa-toast { background: #2a2a2a; border-color: #333; }
  :global([data-theme="dark"]) .install-text strong { color: #eee; }
  :global([data-theme="dark"]) .install-text small { color: #999; }
  :global([data-theme="dark"]) .btn-dismiss { background: #333; color: #ccc; }
</style>
