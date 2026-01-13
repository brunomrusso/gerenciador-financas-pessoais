let chart; // variável global para o gráfico
let mesGlobal = "Janeiro"; // Variável global para rastrear o mês selecionado

// --- INICIALIZAÇÃO ---

window.onload = function() {
    carregarCategorias(); // Carrega as categorias e depois chama carregarExcel
    
    const urlParams = new URLSearchParams(window.location.search);
    const mesUrl = urlParams.get('mes');
    const anoUrl = urlParams.get('ano');

    if (mesUrl && anoUrl) {
        document.getElementById('anoSelecionado').value = anoUrl;
        // Simula o clique no botão do mês da URL
        marcarBotaoMesAtivo(mesUrl);
        mesGlobal = mesUrl;
        carregarExcel();
        atualizarGrafico();
    } else {
        irParaMesAtual(); // Se não houver URL, vai para o mês atual
    }
};

// --- LÓGICA DOS BOTÕES DE PERÍODO ---

function selecionarMes(mes, elemento) {
    mesGlobal = mes; 
    
    // Interface: Remove 'active' de todos e coloca no que foi clicado
    document.querySelectorAll('.btn-mes').forEach(btn => btn.classList.remove('active'));
    elemento.classList.add('active');

    // Carrega os dados do novo período
    carregarExcel();
}

function marcarBotaoMesAtivo(nomeMes) {
    const botoes = document.querySelectorAll('.btn-mes');
    botoes.forEach(btn => {
        // Compara o texto do botão (Jan, Fev...) com o início do nome do mês
        if (nomeMes.toLowerCase().startsWith(btn.innerText.toLowerCase())) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function trocarMes() {
    // Chamada quando o select de ANO muda
    carregarExcel();
}

function irParaMesAtual() {
    const hoje = new Date();
    const meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];

    const nomeMesAtual = meses[hoje.getMonth()];
    const anoAtual = hoje.getFullYear();

    document.getElementById('anoSelecionado').value = anoAtual;
    mesGlobal = nomeMesAtual;

    marcarBotaoMesAtivo(nomeMesAtual);
    carregarExcel();
}

// --- INTEGRAÇÃO EXCEL ---

function carregarExcel() {
    const mes = mesGlobal; 
    const ano = document.getElementById('anoSelecionado').value;    

    const formatarMoedaBR = (valor) => {
        return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };

    fetch(`/carregar?mes=${mes}&ano=${ano}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('saldoAnterior').value = data.saldoAnterior;
            document.getElementById('salarioBruto').value = data.salarioBruto;

            // --- 1. PREENCHE DESCONTOS ---
            const tabelaDescontos = document.querySelector('#tabelaDescontos tbody');
            tabelaDescontos.innerHTML = '';
            data.descontos.forEach(d => {
                const tipo = d.valor > 0 ? 'Crédito' : 'Desconto';
                const sinal = tipo === 'Crédito' ? '+' : '-';
                const cor = tipo === 'Crédito' ? '#4CAF50' : '#F44336';
                const valorFormatado = Math.abs(d.valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

                tabelaDescontos.innerHTML += `
                    <tr data-tipo="${tipo}">
                        <td>${d.descricao}</td>
                        <td style="color: ${cor}; font-weight: bold;">${sinal} ${valorFormatado}</td>
                        <td>
                            <button class="btn-edit" onclick="editarDesconto(this)">✏️</button>
                            <button class="btn-delete" onclick="excluirDesconto(this)">🗑️</button>
                        </td>
                    </tr>`;
            });

            // --- 2. PREENCHE DETALHAMENTO DO CARTÃO (NOVO BLOCO) ---
            const tabelaCartao = document.querySelector('#tabelaCartao tbody');
            if (tabelaCartao) {
                tabelaCartao.innerHTML = '';
                if (data.detalhesCartao) {
                    data.detalhesCartao.forEach(item => {
                        tabelaCartao.innerHTML += `
                            <tr>
                                <td>${item.cartaoOrigem}</td>
                                <td>${item.descricao}</td>
                                <td>${item.categoria}</td>
                                <td>${formatarMoedaBR(item.valor)}</td>
                                <td style="text-align:center">
                                    <button class="btn-delete" onclick="excluirItemCartao(this)">🗑️</button>
                                </td>
                            </tr>`;
                    });
                }
            }

            // --- 3. PREENCHE DESPESAS ---
            const tabelaDespesas = document.querySelector('#tabelaDespesas tbody');
            tabelaDespesas.innerHTML = '';
            categoriasData = getCategoriasFromSelect(); 

            data.despesas.forEach(d => {                
                const corTipo = d.tipo === 'Receita' ? 'style="color: #4CAF50; font-weight: bold;"' : 'style="color: #F44336;"';
                const isPago = d.pago === true || d.pago === "true";
                const classePaga = isPago ? 'class="linha-paga"' : '';
                const checked = isPago ? 'checked' : '';
                
                tabelaDespesas.innerHTML += `
                    <tr ${classePaga} data-tipo="${d.tipo || 'Despesa'}">
                        <td style="text-align:center">
                            <div class="td-switch">
                                <label class="switch-table">
                                    <input type="checkbox" class="checkbox-pago" onchange="alternarStatusPago(this)" ${checked}>
                                    <span class="slider-table"></span>
                                </label>
                            </div>
                        </td>   
                        <td>${d.descricao}</td>
                        <td>${d.categoria}</td>
                        <td>${formatarMoedaBR(d.valor)}</td>
                        <td ${corTipo}>${d.tipo || 'Despesa'}</td> 
                        <td>
                            <button class="btn-edit" onclick="editarDespesesa(this)">✏️</button>
                            <button class="btn-delete" onclick="excluirDespesa(this)">🗑️</button>
                        </td>
                    </tr>`;
            });

            // --- 4. SINCRONIZAÇÃO E ATUALIZAÇÃO FINAL ---
            // Primeiro sincronizamos os cartões para garantir que os valores na tabela de despesas 
            // fiquem corretos antes de rodar os cálculos de saldo e o gráfico.
            if (typeof sincronizarTotaisCartoes === "function") {
                sincronizarTotaisCartoes();
            }

            calcularTudo();
            atualizarGrafico();
            
            if (typeof atualizarGraficoHistorico === "function") {
                atualizarGraficoHistorico();
            }
        });
}

function salvarExcel() {
    const mes = mesGlobal;
    const ano = document.getElementById('anoSelecionado').value;

    // Definição da função de limpeza (usaremos este nome em todos os lugares abaixo)
    const limparMoeda = (texto) => {
        if (!texto) return 0;
        let limpo = texto.replace('R$', '').replace(/\s/g, '').replace(/\./g, '').replace(',', '.');
        return parseFloat(limpo) || 0;
    };

    const descontos = [];
    document.querySelectorAll('#tabelaDescontos tbody tr').forEach(tr => {
        descontos.push({
            descricao: tr.cells[0].innerText,
            valor: limparMoeda(tr.cells[1].innerText)
        });
    });

    const despesas = [];
    document.querySelectorAll('#tabelaDespesas tbody tr').forEach(tr => {
        despesas.push({
            pago: tr.cells[0].querySelector('input').checked,
            descricao: tr.cells[1].innerText,
            categoria: tr.cells[2].innerText,
            valor: limparMoeda(tr.cells[3].innerText),
            tipo: tr.cells[4].innerText.trim()
        });
    });

    const detalhesCartao = [];
    document.querySelectorAll('#tabelaCartao tbody tr').forEach(tr => {
        detalhesCartao.push({
            cartaoOrigem: tr.cells[0].innerText,
            descricao: tr.cells[1].innerText,
            categoria: tr.cells[2].innerText,
            valor: limparMoeda(tr.cells[3].innerText) // AJUSTADO: era limparValor, mudamos para limparMoeda
        });
    });    

    const dados = {
        mes, ano,
        saldoAnterior: parseFloat(document.getElementById('saldoAnterior').value) || 0,
        salarioBruto: parseFloat(document.getElementById('salarioBruto').value) || 0,
        descontos, 
        despesas,
        detalhesCartao // Simplificado (quando a chave e o nome da variável são iguais)
    };

    fetch('/salvar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    }).then(res => res.json())
      .then(data => alert('Dados salvos com sucesso!'));
}

function adicionarDespesa() {
    const desc = document.getElementById('descricaoDespesa').value;
    const cat = document.getElementById('categoriaDespesa').value;
    const val = parseFloat(document.getElementById('valorDespesa').value) || 0;
    const tipo = document.getElementById('tipoMovimentacao').value; 
    const pago = document.getElementById('pagoDespesa').checked;

    if (desc && val > 0) {
        const tabela = document.querySelector('#tabelaDespesas tbody');
        const classePaga = pago ? 'class="linha-paga"' : ''; // Classe definida aqui
        const checked = pago ? 'checked' : '';        

        // AJUSTE: Aplicamos ${classePaga} na <tr>
        tabela.innerHTML += `
            <tr ${classePaga} data-tipo="${tipo}">
                <td style="text-align:center">
                    <div class="td-switch">
                        <label class="switch-table">
                            <input type="checkbox" class="checkbox-pago" onchange="alternarStatusPago(this)" ${checked}>
                            <span class="slider-table"></span>
                        </label>
                    </div>
                </td>
                <td>${desc}</td>
                <td>${cat}</td>
                <td>R$ ${val.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td style="color: ${tipo === 'Receita' ? '#4CAF50' : '#F44336'}">${tipo}</td>
                <td>
                    <button class="btn-edit" onclick="editarDespesa(this)">✏️</button>
                    <button class="btn-delete" onclick="excluirDespesa(this)">🗑️</button>
                </td>
            </tr>`;

        document.getElementById('descricaoDespesa').value = '';
        document.getElementById('valorDespesa').value = '';
        document.getElementById('pagoDespesa').checked = false;
        
        // Atualiza o gráfico de PIZZA (categorias)
        if (tipo === 'Despesa') {
            categoriasData[cat] = (categoriasData[cat] || 0) + val;
            atualizarGrafico();
        }

        // 1. Recalcula os cards de resumo (topo)
        calcularTudo();

        salvarEAtualizarHistorico();
    }
}

// Função auxiliar para garantir a ordem das operações
function salvarEAtualizarHistorico() {
    // Chamamos sua função de salvar
    salvarExcelSilencioso().then(() => {
        // Agora que o Python atualizou o Excel, o gráfico de 6 meses vai ler o valor novo
        atualizarGraficoHistorico();
    });
}

// Crie esta versão "silenciosa" do salvar para não ficar aparecendo "Dados salvos" toda hora
function salvarExcelSilencioso() {
    const mes = mesGlobal;
    const ano = document.getElementById('anoSelecionado').value;

    const limparMoeda = (texto) => {
        if (!texto) return 0;
        let limpo = texto.replace('R$', '').replace(/\s/g, '').replace(/\./g, '').replace(',', '.');
        return parseFloat(limpo) || 0;
    };

    const descontos = [];
    document.querySelectorAll('#tabelaDescontos tbody tr').forEach(tr => {
        descontos.push({
            descricao: tr.cells[0].innerText,
            valor: limparMoeda(tr.cells[1].innerText)
        });
    });

    const despesas = [];
    document.querySelectorAll('#tabelaDespesas tbody tr').forEach(tr => {
        despesas.push({
            pago: tr.cells[0].querySelector('input').checked,
            descricao: tr.cells[1].innerText,
            categoria: tr.cells[2].innerText,
            valor: limparMoeda(tr.cells[3].innerText),
            tipo: tr.cells[4].innerText.trim()
        });
    });

    const dados = {
        mes, ano,
        saldoAnterior: parseFloat(document.getElementById('saldoAnterior').value) || 0,
        salarioBruto: parseFloat(document.getElementById('salarioBruto').value) || 0,
        descontos, despesas
    };

    return fetch('/salvar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    });
}

function excluirDespesa(botao) {
    const linha = botao.closest('tr');
    // AJUSTE DE ÍNDICES: Categoria agora é 2 e Valor agora é 3
    const categoria = linha.cells[2].innerText.trim();
    const valorStr = linha.cells[3].innerText.replace('R$ ', '').replace(/\./g, '').replace(',', '.');
    const valor = parseFloat(valorStr);

    if (confirm("Deseja realmente excluir?")) {
        if (linha.getAttribute('data-tipo') === 'Despesa') {
            categoriasData[categoria] -= valor;
            if (categoriasData[categoria] < 0) categoriasData[categoria] = 0;
        }
        linha.remove();
        calcularTudo();
        atualizarGrafico();
    }
}

// --- CÁLCULOS E CATEGORIAS ---
function atualizarLinhasCartoesPrincipais() {
    // 1. Criamos um mapa para acumular o total de cada cartão
    let totaisPorCartao = {};

    // 2. Percorremos a tabela de detalhamento de faturas
    document.querySelectorAll('#tabelaCartao tbody tr').forEach(tr => {
        const nomeCartao = tr.cells[0].innerText.trim();
        const valor = limparValor(tr.cells[3].innerText);
        
        totaisPorCartao[nomeCartao] = (totaisPorCartao[nomeCartao] || 0) + valor;
    });

    // 3. Atualizamos as linhas na tabela principal
    // Procuramos na tabela de Despesas linhas onde a Categoria seja igual ao nome do cartão
    document.querySelectorAll('#tabelaDespesas tbody tr').forEach(tr => {
        const categoriaLinha = tr.cells[2].innerText.trim();
        
        // Se a categoria da linha principal for um dos cartões (ex: "Cartão Nubank")
        if (totaisPorCartao.hasOwnProperty(categoriaLinha)) {
            const novoTotal = totaisPorCartao[categoriaLinha];
            tr.cells[3].innerText = novoTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        }
    });
}

function sincronizarTotaisCartoes() {
    let totaisPorCartao = {};

    // 1. Soma tudo que está na tabela de faturas, agrupando por nome do cartão
    document.querySelectorAll('#tabelaCartao tbody tr').forEach(tr => {
        const nomeCartao = tr.cells[0].innerText.trim();
        const valor = limparValor(tr.cells[3].innerText);
        totaisPorCartao[nomeCartao] = (totaisPorCartao[nomeCartao] || 0) + valor;
    });

    const tabelaPrincipal = document.querySelector('#tabelaDespesas tbody');

    // 2. Para cada cartão que tem gasto, garantir que ele esteja na tabela principal
    for (const [nomeCartao, total] of Object.entries(totaisPorCartao)) {
        // Busca se já existe uma linha com esse cartão na tabela principal
        let linhaExistente = Array.from(tabelaPrincipal.querySelectorAll('tr'))
            .find(tr => tr.cells[2].innerText.trim() === nomeCartao);

        if (linhaExistente) {
            // Se já existe, apenas atualiza o valor na coluna 3
            linhaExistente.cells[3].innerText = total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        } else {
            // Se NÃO existe, adiciona a linha automaticamente na tabela principal
            tabelaPrincipal.innerHTML += `
                <tr class="linha-paga" data-tipo="Despesa">
                    <td style="text-align:center">
                        <div class="td-switch">
                            <label class="switch-table">
                                <input type="checkbox" class="checkbox-pago" onchange="alternarStatusPago(this)" checked>
                                <span class="slider-table"></span>
                            </label>
                        </div>
                    </td>
                    <td>Fatura Mensal</td>
                    <td>${nomeCartao}</td>
                    <td>${total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                    <td style="color: #F44336">Despesa</td>
                    <td>
                        <button class="btn-edit" onclick="editarDespesa(this)">✏️</button>
                        <button class="btn-delete" onclick="excluirDespesa(this)">🗑️</button>
                    </td>
                </tr>`;
        }
    }
}

function adicionarItemCartao() {
    // Coleta os elementos
    const selectCartaoOrigem = document.getElementById('escolhaCartao'); // Ex: "Cartão Nubank"
    const inputDesc = document.getElementById('descCartao');
    const selectCategoria = document.getElementById('categoriaCartao'); // Categorias reais (Mercado, etc)
    const inputValor = document.getElementById('valCartao');

    const cartaoNome = selectCartaoOrigem.value;
    const desc = inputDesc.value;
    const cat = selectCategoria.value;
    const val = parseFloat(inputValor.value) || 0;

    if (desc && val > 0 && cartaoNome !== "") {
        const tbody = document.querySelector('#tabelaCartao tbody');
        
        // Insere a nova linha na tabela de detalhamento
        tbody.innerHTML += `
            <tr>
                <td>${cartaoNome}</td>
                <td>${desc}</td>
                <td>${cat}</td>
                <td>R$ ${val.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td style="text-align:center">
                    <button class="btn-delete" onclick="excluirItemCartao(this)">🗑️</button>
                </td>
            </tr>`;

        // Limpa apenas os campos de descrição e valor
        inputDesc.value = '';
        inputValor.value = '';

        // --- ATUALIZAÇÕES EM CADEIA ---
        sincronizarTotaisCartoes(); // Soma os itens e joga o total na tabela principal
        atualizarGrafico();         // Reconstrói o gráfico de pizza com os novos detalhes
        calcularTudo();             // Atualiza os cards de saldo no topo
        
    } else {
        alert("Por favor, preencha a descrição e o valor do item!");
    }
}

function excluirItemCartao(btn) {
    if(confirm("Deseja remover este item da fatura?")) {
        const trRemovido = btn.closest('tr');
        const nomeCartaoRemovido = trRemovido.cells[0].innerText.trim();
        trRemovido.remove();
        
        // Verifica se ainda existe algum item para esse cartão na tabela de cartões
        const aindaTemItens = Array.from(document.querySelectorAll('#tabelaCartao tbody tr'))
            .some(tr => tr.cells[0].innerText.trim() === nomeCartaoRemovido);

        // Se não houver mais nenhum gasto nesse cartão, zeramos ele na tabela principal
        if (!aindaTemItens) {
            const linhaPrincipal = Array.from(document.querySelectorAll('#tabelaDespesas tbody tr'))
                .find(tr => tr.cells[2].innerText.trim() === nomeCartaoRemovido);
            if (linhaPrincipal) {
                linhaPrincipal.cells[3].innerText = "R$ 0,00";
            }
        }

        sincronizarTotaisCartoes();
        atualizarGrafico();
        calcularTudo();
    }
}

function getCategoriasFromSelect() {
    const select = document.getElementById('categoriaDespesa');
    const categorias = {};
    for (let i = 0; i < select.options.length; i++) {
        const nome = select.options[i].value;
        categorias[nome] = 0;
    }
    return categorias;
}

let categoriasData = {};

function carregarCategorias() {
    fetch('/categorias')
        .then(res => res.json())
        .then(categorias => {
            const selectPrincipal = document.getElementById('categoriaDespesa');
            const selectCartao = document.getElementById('categoriaCartao'); // O novo select
            
            selectPrincipal.innerHTML = '';
            if (selectCartao) selectCartao.innerHTML = ''; // Limpa se existir
            
            categoriasData = {};

            categorias.forEach(cat => {
                // 1. Adiciona no Select da Tabela Principal (TUDO)
                const opt1 = document.createElement('option');
                opt1.value = cat;
                opt1.textContent = cat;
                selectPrincipal.appendChild(opt1);

                // 2. Adiciona no Select do Cartão (APENAS o que não for "Cartão")
                if (selectCartao && !cat.startsWith("Cartão")) {
                    const opt2 = document.createElement('option');
                    opt2.value = cat;
                    opt2.textContent = cat;
                    selectCartao.appendChild(opt2);
                }

                categoriasData[cat] = 0;
            });
        });
}

function calcularTudo() {
    // FUNÇÃO AUXILIAR ULTRA ROBUSTA
    const limparValor = (valor) => {
        if (valor === null || valor === undefined || valor === "") return 0;
        if (typeof valor === 'number') return valor;
        
        let texto = valor.toString();
        if (texto.includes(',') && texto.includes('.')) {
            texto = texto.replace(/\./g, '').replace(',', '.');
        } else if (texto.includes(',')) {
            texto = texto.replace(',', '.');
        }
        
        let apenasNumeros = texto.replace(/[R$\s\+]/g, '');
        return parseFloat(apenasNumeros) || 0;
    };

    // 1. Pegar valores dos campos de input
    const salarioBase = limparValor(document.getElementById('salarioBruto').value);
    const saldoAnterior = limparValor(document.getElementById('saldoAnterior').value);
    
    let totalCreditosFolha = 0;      // Acumula apenas o que for Crédito (+)
    let apenasDescontosEfetivos = 0; // Acumula apenas o que for Desconto (-)
    let outrasReceitas = 0;
    let totalDespesas = 0;

    // 2. Somar Tabela de Lançamentos de Folha (Créditos e Descontos)
    document.querySelectorAll('#tabelaDescontos tbody tr').forEach(tr => {
        if (tr.cells[1]) {
            const textoValor = tr.cells[1].innerText;
            const valor = limparValor(textoValor);
            const tipo = tr.getAttribute('data-tipo') || (textoValor.includes('+') ? 'Crédito' : 'Desconto');

            if (tipo === 'Crédito') {
                totalCreditosFolha += valor;
            } else {
                apenasDescontosEfetivos += Math.abs(valor);
            }
        }
    });

    // 3. Somar Tabela de Movimentações (Despesas e Receitas)
    document.querySelectorAll('#tabelaDespesas tbody tr').forEach(tr => {
        if (tr.cells[3]) {
            const valor = limparValor(tr.cells[3].innerText);
            const tipo = tr.getAttribute('data-tipo') || 'Despesa'; 

            if (tipo === 'Receita') {
                outrasReceitas += valor;
            } else {
                totalDespesas += valor;
            }
        }
    });

    // --- CÁLCULOS FINAIS ---
    
    // Salário Líquido = Bruto - Descontos + Créditos
    const salarioLiquidoReal = (salarioBase - apenasDescontosEfetivos) + totalCreditosFolha;
    
    // Receita Total = Salário Líquido + Receitas da Tabela + Saldo Anterior
    const receitaTotalFinal = salarioLiquidoReal + outrasReceitas + saldoAnterior;
    
    const saldoFinalCalculado = receitaTotalFinal - totalDespesas;

    // 4. Atualizar a Interface
    const formatarMoeda = (v) => {
        const valorFormatado = Math.abs(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        return v < 0 ? `- ${valorFormatado}` : valorFormatado;
    };

    // Atualiza os Cards de Resumo
    document.getElementById('receitasBox').textContent = formatarMoeda(receitaTotalFinal);    
    document.getElementById('totalDespesasBox').textContent = formatarMoeda(totalDespesas);
    document.getElementById('saldoBox').textContent = formatarMoeda(saldoFinalCalculado);
    document.getElementById('investimentosBox').textContent = formatarMoeda(0);
    
    // ATUALIZAÇÃO DO CAMPO DESCONTOS: Exibe apenas a soma dos descontos, valor positivo.
    const inputDescontos = document.getElementById('salarioDescontos');
    inputDescontos.value = formatarMoeda(apenasDescontosEfetivos); 
    inputDescontos.style.color = "#F44336"; // Sempre vermelho por serem descontos

    // Porcentagem de Descontos sobre o Salário Bruto
    if (salarioBase > 0) {
        const perc = (apenasDescontosEfetivos / salarioBase) * 100;
        document.getElementById('porcentagemDesconto').value = perc.toFixed(1);
    } else {
        document.getElementById('porcentagemDesconto').value = "0";
    }
}

let paginaAtualLegenda = 0;
const itensPorPagina = 3; // Defina quantas linhas quer por página
let dadosCategoriasGlobais = []; // Para guardar a lista ordenada

function mudarPaginaLegenda(direcao) {
    const totalPaginas = Math.ceil(dadosCategoriasGlobais.length / itensPorPagina);
    paginaAtualLegenda += direcao;

    // Impede de sair dos limites
    if (paginaAtualLegenda < 0) paginaAtualLegenda = 0;
    if (paginaAtualLegenda >= totalPaginas) paginaAtualLegenda = totalPaginas - 1;

    renderizarTabelaLegenda();
}

function limparValor(valorTexto) {
    if (!valorTexto) return 0;
    // Remove R$, espaços e pontos de milhar, troca vírgula por ponto
    return parseFloat(valorTexto.replace('R$', '').replace(/\s/g, '').replace(/\./g, '').replace(',', '.')) || 0;
}

function renderizarTabelaLegenda() {
    const tbody = document.querySelector('#tabelaLegenda tbody');
    const controlePaginacao = document.getElementById('controlePaginacao');
    
    if (!tbody) return; 

    const totalItens = dadosCategoriasGlobais.length;
    const totalPaginas = Math.ceil(totalItens / itensPorPagina);

    // Mostra ou esconde o bloco de setas dependendo da quantidade de categorias
    if (controlePaginacao) {
        controlePaginacao.style.display = totalItens > itensPorPagina ? 'flex' : 'none';
    }

    tbody.innerHTML = '';

    const inicio = paginaAtualLegenda * itensPorPagina;
    const itensExibir = dadosCategoriasGlobais.slice(inicio, inicio + itensPorPagina);

    itensExibir.forEach((item) => {
        tbody.innerHTML += `
            <tr>
                <td style="text-align: center; width: 30px;">
                    <span class="cor-bolinha" style="background-color: ${item.cor};"></span>
                </td>
                <td>${item.nome}</td>
                <td style="font-weight: bold; text-align: right;">${item.percentual}%</td>
            </tr>
        `;
    });

    // Atualiza o texto "1 / 2" e o estado dos botões que você enviou no HTML
    const infoPg = document.getElementById('infoPaginaLegenda');
    const btnAnt = document.getElementById('btnAntLegenda');
    const btnProx = document.getElementById('btnProxLegenda');

    if (infoPg) infoPg.textContent = `${paginaAtualLegenda + 1} / ${totalPaginas || 1}`;
    if (btnAnt) btnAnt.disabled = (paginaAtualLegenda === 0);
    if (btnProx) btnProx.disabled = (paginaAtualLegenda >= totalPaginas - 1);
}

// --- GRÁFICO ---
let chartHistorico; // Variável global

function atualizarGraficoHistorico() {
    const mes = mesGlobal;
    const ano = document.getElementById('anoSelecionado').value;

    fetch(`/historico_6meses?mes=${mes}&ano=${ano}`)
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('graficoHistorico').getContext('2d');
            if (chartHistorico) chartHistorico.destroy();

            const labels = data.map(d => d.mes);
            
            const receitas = data.map(d => {
                // FÓRMULA IDÊNTICA AO SEU CALCULAR_TUDO()
                const base = parseFloat(d.salarioBruto) || 0;
                const desc = parseFloat(d.totalDescontos) || 0;
                const cred = parseFloat(d.totalCreditos) || 0;
                const out  = parseFloat(d.outrasReceitas) || 0;
                const ant  = parseFloat(d.saldoAnterior) || 0;

                return (base - desc) + cred + out + ant;
            });

            const despesas = data.map(d => parseFloat(d.despesas) || 0);

            chartHistorico = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Receitas', data: receitas, backgroundColor: '#4CAF50', borderRadius: 5 },
                        { label: 'Despesas', data: despesas, backgroundColor: '#F44336', borderRadius: 5 }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }
                        }
                    }
                }
            });
        });
}

function atualizarGrafico() {
    const ctx = document.getElementById('graficoCategorias');
    if (!ctx) return; // Segurança caso o elemento sumiu
    
    const context = ctx.getContext('2d');
    if (chart) chart.destroy();

    // 1. Resetar categoriasData para garantir soma limpa
    // Se categoriasData não existir, inicializamos como objeto vazio
    if (typeof categoriasData === 'undefined') {
        window.categoriasData = {};
    }
    Object.keys(categoriasData).forEach(cat => categoriasData[cat] = 0);

    // Função interna de limpeza ultra-segura
    const extrairValor = (texto) => {
        if (!texto) return 0;
        let limpo = texto.replace('R$', '').replace(/\s/g, '').replace(/\./g, '').replace(',', '.');
        return parseFloat(limpo) || 0;
    };

    // 2. Somar da Tabela de Despesas
    document.querySelectorAll('#tabelaDespesas tbody tr').forEach(tr => {
        if (tr.cells.length < 4) return;
        const cat = tr.cells[2].innerText.trim();
        const valor = extrairValor(tr.cells[3].innerText);
        const tipo = tr.getAttribute('data-tipo') || 'Despesa';

        if (tipo === 'Despesa' && !cat.startsWith("Cartão")) {
            if (!categoriasData.hasOwnProperty(cat)) categoriasData[cat] = 0;
            categoriasData[cat] += valor;
        }
    });

    // 3. Somar da Tabela de Cartão
    document.querySelectorAll('#tabelaCartao tbody tr').forEach(tr => {
        if (tr.cells.length < 4) return;
        const catReal = tr.cells[2].innerText.trim();
        const valor = extrairValor(tr.cells[3].innerText);
        
        if (!categoriasData.hasOwnProperty(catReal)) categoriasData[catReal] = 0;
        categoriasData[catReal] += valor;
    });

    // 4. Transformar em Array para o Chart.js
    dadosCategoriasGlobais = Object.keys(categoriasData)
        .map((cat, i) => {
            const coresPadrao = ['#4CAF50', '#2E7D32', '#81C784', '#A5D6A7', '#C8E6C9', '#1B5E20', '#2ecc71', '#27ae60'];
            return {
                nome: cat,
                valor: categoriasData[cat],
                cor: coresPadrao[i % coresPadrao.length]
            };
        })
        .filter(item => item.valor > 0)
        .sort((a, b) => b.valor - a.valor);

    console.log("Dados processados para o gráfico:", dadosCategoriasGlobais);

    const total = dadosCategoriasGlobais.reduce((acc, curr) => acc + curr.valor, 0);

    if (total === 0) {
        console.warn("Nenhum valor encontrado para gerar o gráfico.");
        return;
    }

    dadosCategoriasGlobais.forEach(item => {
        item.percentual = ((item.valor / total) * 100).toFixed(1);
    });

    // 5. Renderizar
    paginaAtualLegenda = 0; 
    if (typeof renderizarTabelaLegenda === "function") renderizarTabelaLegenda(); 

    chart = new Chart(context, {
        type: 'pie',
        data: {
            labels: dadosCategoriasGlobais.map(i => i.nome),
            datasets: [{
                data: dadosCategoriasGlobais.map(i => i.valor),
                backgroundColor: dadosCategoriasGlobais.map(i => i.cor)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                datalabels: {
                    formatter: (value) => ((value / total) * 100).toFixed(1) + '%',
                    color: '#fff',
                    font: { weight: 'bold', size: 11 },
                    display: (ctx) => (ctx.dataset.data[ctx.dataIndex] / total) > 0.05
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}
function alternarStatusPago(checkbox) {
    const linha = checkbox.closest('tr');
    if (checkbox.checked) {
        linha.classList.add('linha-paga');
    } else {
        linha.classList.remove('linha-paga');
    }
    calcularTudo(); // Recalcula se necessário
}

// --- EVENTOS E EDIÇÃO ---

function adicionarDesconto() {
    const descricao = document.getElementById('descricaoDesconto').value;
    const valorInput = document.getElementById('valorDesconto').value;
    // Pega se é Crédito ou Desconto do select que adicionaremos no HTML
    const tipo = document.getElementById('tipoLancamentoFolha').value; 
    
    const valor = parseFloat(valorInput) || 0;

    if (descricao && valor > 0) {
        const tabela = document.querySelector('#tabelaDescontos tbody');
        
        const valorFormatado = valor.toLocaleString('pt-BR', { 
            style: 'currency', 
            currency: 'BRL' 
        });

        // Definimos a cor: Verde para crédito, vermelho para desconto
        const cor = tipo === 'Crédito' ? '#4CAF50' : '#F44336';
        const sinal = tipo === 'Crédito' ? '+' : '-';

        // Inserimos o atributo data-tipo para a função calcularTudo identificar
        tabela.innerHTML += `<tr data-tipo="${tipo}">
            <td>${descricao}</td>
            <td style="color: ${cor}; font-weight: bold;">${sinal} ${valorFormatado}</td>
            <td>
                <button class="btn-edit" onclick="editarDesconto(this)">✏️</button>
                <button class="btn-delete" onclick="excluirDesconto(this)">🗑️</button>
            </td>
        </tr>`;

        document.getElementById('descricaoDesconto').value = '';
        document.getElementById('valorDesconto').value = '';
        calcularTudo();
    }
}

function excluirDesconto(botao) {
    if (confirm("Deseja realmente excluir este desconto?")) {
        botao.closest('tr').remove();
        calcularTudo();
    }
}

function editarDespesa(botao) {
    const linha = botao.closest('tr');
    
    // Captura dos textos das células (Índices ajustados para a nova coluna Pago)
    const descricao = linha.cells[1].innerText.trim();
    const categoria = linha.cells[2].innerText.trim();
    const valorTexto = linha.cells[3].innerText;
    const tipo = linha.cells[4].innerText.trim();
    const isPago = linha.cells[0].querySelector('input').checked;

    // LIMPEZA DO VALOR: Remove R$, espaços, pontos de milhar e troca vírgula por ponto
    // Exemplo: "R$ 1.250,50" -> "1250.50"
    const valorNumerico = parseFloat(
        valorTexto.replace('R$', '')
                  .replace(/\s/g, '')
                  .replace(/\./g, '')
                  .replace(',', '.')
    ) || 0;

    // 1. Preenche Descrição
    document.getElementById('descricaoDespesa').value = descricao;

    // 2. Preenche Categoria (Garante que o valor existe no select)
    const selectCat = document.getElementById('categoriaDespesa');
    selectCat.value = categoria; 
    
    // Caso o valor não tenha sido encontrado no select (por erro de trim ou case), 
    // tentamos forçar a seleção manual:
    if (selectCat.value !== categoria) {
        Array.from(selectCat.options).forEach(opt => {
            if (opt.text.trim() === categoria) selectCat.value = opt.value;
        });
    }

    // 3. Preenche Valor (Deve ser apenas o número puro para input type="number")
    document.getElementById('valorDespesa').value = valorNumerico;

    // 4. Preenche Tipo e Pago
    document.getElementById('tipoMovimentacao').value = tipo;
    document.getElementById('pagoDespesa').checked = isPago;
    
    // --- Lógica de atualização do gráfico ANTES de remover ---
    if (tipo === 'Despesa' && categoriasData[categoria] !== undefined) {
        categoriasData[categoria] -= valorNumerico;
        if (categoriasData[categoria] < 0) categoriasData[categoria] = 0;
    }

    // Remove a linha e atualiza a tela
    linha.remove();
    calcularTudo();
    atualizarGrafico();
}

function editarDesconto(botao) {
    const linha = botao.closest('tr');
    
    // 1. Recupera a descrição
    const descricao = linha.cells[0].innerText;
    
    // 2. Recupera o valor limpando R$, espaços, pontos de milhar e tratando a vírgula
    let valorTexto = linha.cells[1].innerText;
    // Remove tudo que não é número ou vírgula
    let valorLimpo = valorTexto.replace(/[R$\s\.\+\-]/g, '').replace(',', '.');
    const valorNumerico = parseFloat(valorLimpo) || 0;

    // 3. Recupera o tipo (Crédito ou Desconto) que salvamos no atributo data-tipo
    const tipo = linha.getAttribute('data-tipo');

    // 4. Alimenta os campos de volta para edição
    document.getElementById('descricaoDesconto').value = descricao;
    document.getElementById('valorDesconto').value = valorNumerico;
    
    // Se o campo select existir, define o valor dele (Crédito ou Desconto)
    if (tipo) {
        document.getElementById('tipoLancamentoFolha').value = tipo;
    }

    // 5. Remove a linha e recalcula
    linha.remove();
    calcularTudo();
}

document.getElementById('salarioBruto').addEventListener('input', calcularTudo);
document.getElementById('saldoAnterior').addEventListener('input', calcularTudo);
document.getElementById('anoSelecionado').addEventListener('change', trocarMes);