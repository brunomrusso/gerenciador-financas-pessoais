<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  export let tags: string[] = []
  export let placeholder = 'Adicionar tag (Enter)'
  export let suggestions: string[] = []

  let inputValue = ''
  const dispatch = createEventDispatcher<{ change: string[] }>()

  const addTag = (raw: string) => {
    const t = (raw || '').trim().replace(/,$/, '').toLowerCase()
    if (!t) return
    if (tags.includes(t)) return
    tags = [...tags, t]
    inputValue = ''
    dispatch('change', tags)
  }

  const removeTag = (tag: string) => {
    tags = tags.filter(t => t !== tag)
    dispatch('change', tags)
  }

  const onKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addTag(inputValue)
    } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
      tags = tags.slice(0, -1)
      dispatch('change', tags)
    }
  }

  $: filteredSuggestions = suggestions.filter(s =>
    s && !tags.includes(s.toLowerCase()) &&
    (!inputValue.trim() || s.toLowerCase().includes(inputValue.toLowerCase()))
  ).slice(0, 6)
</script>

<div class="tag-input">
  <div class="tag-row">
    {#each tags as tag (tag)}
      <span class="tag-chip">
        {tag}
        <button type="button" class="x" on:click={() => removeTag(tag)}>×</button>
      </span>
    {/each}
    <input
      type="text"
      class="t-inp"
      {placeholder}
      bind:value={inputValue}
      on:keydown={onKeydown}
      on:blur={() => addTag(inputValue)}
    />
  </div>
  {#if filteredSuggestions.length > 0 && inputValue.trim()}
    <div class="t-sugg">
      {#each filteredSuggestions as s (s)}
        <button type="button" class="t-sugg-btn" on:mousedown|preventDefault={() => addTag(s)}>{s}</button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .tag-input { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 140px; }
  .tag-row {
    display: flex; flex-wrap: wrap; align-items: center; gap: 4px;
    padding: 4px 6px; min-height: 34px;
    border: 1px solid #ddd; border-radius: 5px; background: white;
  }
  .tag-chip {
    display: inline-flex; align-items: center; gap: 4px;
    background: #e8eaff; color: #3949ab; border-radius: 12px;
    padding: 2px 4px 2px 10px; font-size: 0.78rem; font-weight: 500;
  }
  .x { background: none; border: none; color: #5c6bc0; font-size: 0.95rem; cursor: pointer; padding: 0 4px; line-height: 1; }
  .x:hover { color: #c62828; }
  .t-inp {
    flex: 1; border: none; outline: none; padding: 4px 6px; font-size: 0.85rem;
    background: transparent; color: #333; min-width: 80px;
  }
  .t-sugg { display: flex; flex-wrap: wrap; gap: 4px; padding: 2px 0; }
  .t-sugg-btn {
    background: #f0f0f4; border: 1px solid #e0e0e8; color: #555;
    padding: 2px 8px; border-radius: 10px; font-size: 0.72rem; cursor: pointer;
  }
  .t-sugg-btn:hover { background: #667eea; color: white; border-color: #667eea; }
</style>
