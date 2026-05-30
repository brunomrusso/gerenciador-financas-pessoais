<script lang="ts">
  import { onMount } from 'svelte'
  import Login from './pages/Login.svelte'
  import Dashboard from './pages/Dashboard.svelte'
  import ResetPassword from './pages/ResetPassword.svelte'
  import PWAPrompt from './components/PWAPrompt.svelte'
  import { authStore } from './stores/auth'

  let isAuthenticated = false
  let route = window.location.pathname

  function getResetToken(): string | null {
    if (!route.startsWith('/reset')) return null
    const params = new URLSearchParams(window.location.search)
    return params.get('token')
  }

  onMount(() => {
    authStore.subscribe(value => {
      isAuthenticated = !!value.token
    })
    window.addEventListener('popstate', () => { route = window.location.pathname })
  })

  $: resetToken = getResetToken()
</script>

<main>
  {#if resetToken}
    <ResetPassword token={resetToken} />
  {:else if isAuthenticated}
    <Dashboard />
  {:else}
    <Login />
  {/if}
</main>

<PWAPrompt />

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
  }

  main {
    width: 100%;
    min-height: 100vh;
  }
</style>
