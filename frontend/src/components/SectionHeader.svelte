<script lang="ts">
  import { collapsedSections, toggleSection } from '../stores/ui'

  export let sectionKey: string
  export let title: string = ''
  export let summary: string = ''

  $: collapsed = !!$collapsedSections[sectionKey]
</script>

<button class="sh-toggle" on:click={() => toggleSection(sectionKey)} title={collapsed ? 'Expandir' : 'Recolher'}>
  <span class="chevron" class:rot={!collapsed}>▶</span>
  {#if title}<span class="sh-title">{title}</span>{/if}
  {#if summary}<span class="sh-summary">{summary}</span>{/if}
  <slot />
</button>

<style>
  .sh-toggle {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    text-align: left;
    color: inherit;
    font: inherit;
  }
  .chevron {
    display: inline-block;
    font-size: 0.75rem;
    color: #999;
    transition: transform 0.18s;
  }
  .chevron.rot { transform: rotate(90deg); }
  .sh-title { font-weight: 700; }
  .sh-summary { color: #888; font-size: 0.78rem; margin-left: 0.4rem; font-weight: 400; }
</style>
