<script lang="ts">
  export let title: string
  export let items: any[] = []

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(Math.abs(value))
  }
</script>

<div class="data-table">
  <h3>{title}</h3>
  <table>
    <thead>
      <tr>
        <th>Descrição</th>
        <th>Valor</th>
      </tr>
    </thead>
    <tbody>
      {#if items && items.length > 0}
        {#each items as item (item.id)}
          <tr>
            <td>{item.descricao || item.card_name}</td>
            <td class={item.valor < 0 ? 'negative' : 'positive'}>
              {formatCurrency(item.valor)}
            </td>
          </tr>
        {/each}
      {:else}
        <tr>
          <td colspan="2" class="empty">Nenhum registro</td>
        </tr>
      {/if}
    </tbody>
  </table>
</div>

<style>
  .data-table {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
  }

  h3 {
    margin: 0 0 1rem 0;
    color: #333;
    font-size: 1.1rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  thead {
    background-color: #f5f5f5;
  }

  th {
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    color: #666;
    border-bottom: 2px solid #ddd;
  }

  td {
    padding: 0.75rem;
    border-bottom: 1px solid #eee;
  }

  tr:last-child td {
    border-bottom: none;
  }

  .empty {
    text-align: center;
    color: #999;
    font-style: italic;
  }

  .positive {
    color: #4caf50;
    font-weight: 600;
  }

  .negative {
    color: #f44336;
    font-weight: 600;
  }
</style>
