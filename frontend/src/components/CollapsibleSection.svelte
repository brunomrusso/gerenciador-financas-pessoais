<script lang="ts">
  import { collapsedSections, toggleSection } from '../stores/ui'

  export let sectionKey: string
  export let title: string = ''
  export let summary: string = ''
  export let bare: boolean = false  // se true, nao aplica wrapper visual (componente filho ja tem seu card)

  $: collapsed = !!$collapsedSections[sectionKey]
</script>

<div class="cs-wrap" class:bare>
  <button class="cs-header" on:click={() => toggleSection(sectionKey)} title={collapsed ? 'Expandir' : 'Recolher'}>
    <span class="chevron" class:rot={!collapsed}>▶</span>
    <span class="cs-title">{title}</span>
    {#if summary}<span class="cs-summary">{summary}</span>{/if}
  </button>

  {#if !collapsed}
    <div class="cs-body">
      <slot />
    </div>
  {/if}
</div>

<style>
  .cs-wrap {
    background: white;
    border-radius: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    overflow: hidden;
  }
  .cs-wrap.bare {
    background: transparent;
    box-shadow: none;
  }
  .cs-header {
    width: 100%;
    background: none;
    border: none;
    padding: 0.75rem 1rem;
    text-align: left;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
    color: #333;
    transition: background 0.15s;
  }
  .cs-header:hover { background: #f7f8fc; }
  .chevron {
    display: inline-block;
    font-size: 0.7rem;
    color: #999;
    transition: transform 0.18s;
    width: 12px;
  }
  .chevron.rot { transform: rotate(90deg); color: #667eea; }
  .cs-title { font-weight: 700; flex: 0 0 auto; }
  .cs-summary { color: #888; font-size: 0.8rem; font-weight: 400; margin-left: 0.5rem; }
  .cs-body { padding: 0; }
  .cs-wrap.bare .cs-body { padding: 0; }

  :global([data-theme="dark"]) .cs-wrap { background: #1e1e1e; }
  :global([data-theme="dark"]) .cs-header { color: #ddd; }
  :global([data-theme="dark"]) .cs-header:hover { background: #2a2a2a; }
  :global([data-theme="dark"]) .cs-summary { color: #999; }

  @media (max-width: 640px) {
    .cs-header { padding: 0.6rem 0.75rem; font-size: 0.88rem; }
    .cs-title { font-size: 0.92rem; }
  }
</style>
