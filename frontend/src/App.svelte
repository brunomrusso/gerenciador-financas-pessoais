<script lang="ts">
  import { onMount } from 'svelte'
  import Login from './pages/Login.svelte'
  import Dashboard from './pages/Dashboard.svelte'
  import { authStore } from './stores/auth'

  let isAuthenticated = false

  onMount(() => {
    authStore.subscribe(value => {
      isAuthenticated = !!value.token
    })
  })
</script>

<main>
  {#if isAuthenticated}
    <Dashboard />
  {:else}
    <Login />
  {/if}
</main>

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
