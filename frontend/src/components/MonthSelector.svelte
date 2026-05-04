<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  const months = [
    'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]
  let selectedMonth = months[new Date().getMonth()]
  let selectedYear = new Date().getFullYear()

  const handleMonthClick = (month: string) => {
    selectedMonth = month
    dispatch('change', { month: selectedMonth, year: selectedYear })
  }

  const handleYearChange = (e: Event) => {
    const target = e.target as HTMLSelectElement
    selectedYear = parseInt(target.value)
    dispatch('change', { month: selectedMonth, year: selectedYear })
  }

  const goToCurrentMonth = () => {
    const now = new Date()
    selectedMonth = months[now.getMonth()]
    selectedYear = now.getFullYear()
    dispatch('change', { month: selectedMonth, year: selectedYear })
  }
</script>

<div class="month-selector">
  <div class="controls">
    <select value={selectedYear} on:change={handleYearChange} class="year-select">
      <option value={2024}>2024</option>
      <option value={2025}>2025</option>
      <option value={2026}>2026</option>
      <option value={2027}>2027</option>
    </select>

    <button on:click={goToCurrentMonth} class="btn-today">Hoje</button>
  </div>

  <div class="months-grid">
    {#each months as month}
      <button
        class={`month-btn ${selectedMonth === month ? 'active' : ''}`}
        on:click={() => handleMonthClick(month)}
      >
        {month.substring(0, 3)}
      </button>
    {/each}
  </div>
</div>

<style>
  .month-selector {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  .controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: center;
  }

  .year-select {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
    cursor: pointer;
  }

  .btn-today {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.2s;
  }

  .btn-today:hover {
    transform: translateY(-2px);
  }

  .months-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
    gap: 0.5rem;
  }

  .month-btn {
    padding: 0.75rem;
    border: 2px solid #ddd;
    background: white;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
    color: #333;
  }

  .month-btn:hover {
    border-color: #667eea;
    color: #667eea;
  }

  .month-btn.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-color: transparent;
  }
</style>
