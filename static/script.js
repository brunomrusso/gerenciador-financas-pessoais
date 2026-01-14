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
                            <button class="btn-edit" onclick="editarDesconto(this)">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                </svg>
                            </button>
                            <button class="btn-delete" onclick="excluirDesconto(this)">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    <line x1="10" y1="11" x2="10" y2="17"></line>
                                    <line x1="14" y1="11" x2="14" y2="17"></line>
                                </svg>
                            </button>
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
                                    <button class="btn-edit" onclick="">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                        </svg>
                                    </button>
                                    <button class="btn-delete" onclick="excluirItemCartao(this)">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <polyline points="3 6 5 6 21 6"></polyline>
                                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                            <line x1="10" y1="11" x2="10" y2="17"></line>
                                            <line x1="14" y1="11" x2="14" y2="17"></line>
                                        </svg>
                                    </button>
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
                const vencimento = d.vencimento || "";
                    
                // --- LÓGICA DE STATUS (PAGO / ATRASADO / NORMAL) ---
                let classeStatus = "";
                if (isPago) {
                    classeStatus = "linha-paga";
                } else if (vencimento) {
                    const dataVenc = new Date(vencimento + 'T00:00:00'); // Força fuso local
                    const hoje = new Date();
                    hoje.setHours(0, 0, 0, 0);

                    if (dataVenc < hoje) {
                        classeStatus = "linha-atrasada";
                    }
                }

                const checked = isPago ? 'checked' : '';    
                
                tabelaDespesas.innerHTML += `
                    <tr class="${classeStatus}" data-tipo="${d.tipo || 'Despesa'}">
                        <td style="text-align:center">
                            <div class="td-switch">
                                <label class="switch-table">
                                    <input type="checkbox" class="checkbox-pago" onchange="alternarStatusPago(this)" ${checked}>
                                    <span class="slider-table"></span>
                                </label>
                            </div>
                        </td>
                        <td>
                            <input type="date" class="form-control form-control-sm input-vencimento-tabela ${classeStatus}" 
                                    value="${vencimento}" onchange="reverificarAtraso(this)" readonly>
                        </td>   
                        <td>${d.descricao}</td>
                        <td>${d.categoria}</td>
                        <td>${formatarMoedaBR(d.valor)}</td>
                        <td ${corTipo}>${d.tipo || 'Despesa'}</td> 
                        <td>
                            <button class="btn-edit" onclick="editarDespesa(this)">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                </svg>
                            </button>
                            <button class="btn-delete" onclick="excluirDespesa(this)">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    <line x1="10" y1="11" x2="10" y2="17"></line>
                                    <line x1="14" y1="11" x2="14" y2="17"></line>
                                </svg>
                            </button>
                        </td>
                    </tr>`;
            });

            // --- 4. SINCRONIZAÇÃO E ATUALIZAÇÃO FINAL ---
            // Primeiro sincronizamos os cartões para garantir que os valores na tabela de despesas 
            // fiquem corretos antes de rodar os cálculos de saldo e o gráfico.
            if (typeof sincronizarTotaisCartoes === "function") {
                sincronizarTotaisCartoes();
            }

            if (data.listaCartoes) {
                cartoesDisponiveis = data.listaCartoes; // Atualiza a variável global
                atualizarSelectCartoes();              // Atualiza o <select> da tela
            }

            // Limpa a tabela antes de carregar (para não duplicar ao trocar de mês)
            document.querySelector('#tabelaInvestimentos tbody').innerHTML = "";

            // --- 5. PREENCHE INVESTIMENTOS ---
            const tabelaInvestimentos = document.querySelector('#tabelaInvestimentos tbody');
            if (tabelaInvestimentos) {
                tabelaInvestimentos.innerHTML = ""; // Limpa a tabela

                // Use "data" em vez de "dados"
                if (data.investimentos) {
                    try {
                        const lista = typeof data.investimentos === 'string' 
                            ? JSON.parse(data.investimentos) 
                            : data.investimentos;

                        if (Array.isArray(lista)) {
                            lista.forEach(inv => {
                                adicionarLinhaInvestimento(inv.nome || '', inv.tipo || '', inv.valor || 0);
                            });
                        }
                    } catch (e) {
                        console.error("Erro ao processar JSON de investimentos:", e);
                    }
                }
                calcularTotalInvestimentos();
            }

            calcularTudo();
            atualizarGrafico();
            
            if (typeof atualizarGraficoHistorico === "function") {
                atualizarGraficoHistorico();
            }
        });
}

function salvarExcel() {
    // 1. Início: Feedback visual de que o salvamento começou
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });

    // Mostra um "Salvando..." discreto
    Toast.fire({
        icon: 'info',
        title: 'Salvando dados...'
    });

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
            vencimento: tr.cells[1].querySelector('input').value,
            descricao: tr.cells[2].innerText,
            categoria: tr.cells[3].innerText,
            valor: limparMoeda(tr.cells[4].innerText),
            tipo: tr.cells[5].innerText.trim()
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
    
    const investimentos = [];
    document.querySelectorAll('#tabelaInvestimentos tbody tr').forEach(tr => {
        const nomeTexto = tr.cells[0].innerText.trim();
        const tipoTexto = tr.cells[1].innerText.trim();
        const valorNumerico = parseFloat(tr.cells[2].getAttribute('data-valor')) || 0;

        // Só adiciona se o nome não estiver vazio para evitar lixo no Excel
        if (nomeTexto !== "") { 
            investimentos.push({
                nome: nomeTexto,
                tipo: tipoTexto,
                valor: valorNumerico
            });
        }
    });

    const dados = {
        mes, ano,
        saldoAnterior: parseFloat(document.getElementById('saldoAnterior').value) || 0,
        salarioBruto: parseFloat(document.getElementById('salarioBruto').value) || 0,
        descontos, 
        despesas,
        detalhesCartao, // Simplificado (quando a chave e o nome da variável são iguais)
        investimentos,
        listaCartoes: cartoesDisponiveis
        
    };

    // 2. FETCH com animação de sucesso ao terminar
    fetch('/salvar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    })
    .then(res => res.json())
    .then(data => {
        // Sucesso: Notificação verde automática
        Toast.fire({
            icon: 'success',
            title: 'Dados sincronizados com o Excel!'
        });
    })
    .catch(err => {
        // Erro: Notificação vermelha
        Toast.fire({
            icon: 'error',
            title: 'Erro ao salvar os dados.'
        });
        console.error(err);
    });
}

function adicionarDespesa() {    
    const desc = document.getElementById('descricaoDespesa').value;
    const cat = document.getElementById('categoriaDespesa').value;
    const val = parseFloat(document.getElementById('valorDespesa').value) || 0;
    const tipo = document.getElementById('tipoMovimentacao').value; 
    const pago = document.getElementById('pagoDespesa').checked;
    
    // NOVO: Captura o vencimento (Tratamento: se não existir o ID ou valor, fica vazio)
    const vencimentoInput = document.getElementById('dataVencimento');
    const vencimento = vencimentoInput ? vencimentoInput.value : "";

    if (desc && val > 0) {
        const tabela = document.querySelector('#tabelaDespesas tbody');
        
        // --- LÓGICA DE STATUS (PAGO / ATRASADO / NORMAL) ---
        let classeStatus = "";
        if (pago) {
            classeStatus = "linha-paga";
        } else if (vencimento) {
            const dataVenc = new Date(vencimento + 'T00:00:00'); // Força fuso local
            const hoje = new Date();
            hoje.setHours(0, 0, 0, 0);

            if (dataVenc < hoje) {
                classeStatus = "linha-atrasada";
            }
        }

        const checked = pago ? 'checked' : '';        

        // Inserção na Tabela (Incluindo a nova coluna de Vencimento)
        tabela.innerHTML += `
            <tr class="${classeStatus}" data-tipo="${tipo}">
                <td style="text-align:center">
                    <div class="td-switch">
                        <label class="switch-table">
                            <input type="checkbox" class="checkbox-pago" onchange="alternarStatusPago(this)" ${checked}>
                            <span class="slider-table"></span>
                        </label>
                    </div>
                </td>
                <td>
                    <input type="date" class="form-control form-control-sm input-vencimento-tabela ${classeStatus}" 
                           value="${vencimento}" onchange="reverificarAtraso(this)">
                </td>
                <td>${desc}</td>
                <td>${cat}</td>
                <td data-valor="${val}">R$ ${val.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td style="color: ${tipo === 'Receita' ? '#4CAF50' : '#F44336'}">${tipo}</td>
                <td>
                    <button class="btn-edit" onclick="editarDespesa(this)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    </button>
                    <button class="btn-delete" onclick="excluirDespesa(this)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            <line x1="10" y1="11" x2="10" y2="17"></line>
                            <line x1="14" y1="11" x2="14" y2="17"></line>
                        </svg>
                    </button>
                </td>
            </tr>`;

        // Limpeza dos campos
        document.getElementById('descricaoDespesa').value = '';
        document.getElementById('valorDespesa').value = '';
        if (vencimentoInput) vencimentoInput.value = '';
        document.getElementById('pagoDespesa').checked = false;
        
        if (tipo === 'Despesa') {
            categoriasData[cat] = (categoriasData[cat] || 0) + val;
            atualizarGrafico();
        }

        calcularTudo();
        salvarEAtualizarHistorico();
        setTimeout(salvarExcel, 100);
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
    const categoria = linha.cells[2].innerText.trim();
    
    // Tenta pegar o valor bruto (se você tiver o atributo data-valor na célula do valor)
    // Se não tiver, ele usa o seu método de limpeza
    const celulaValor = linha.cells[3];
    const valor = celulaValor.hasAttribute('data-valor') 
        ? parseFloat(celulaValor.getAttribute('data-valor')) 
        : parseFloat(celulaValor.innerText.replace(/[R$\s.]/g, '').replace(',', '.')) || 0;

    // ALERTA MODERNO
    Swal.fire({
        title: 'Excluir lançamento?',
        text: `Você está removendo: ${linha.cells[1].innerText}`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true // Coloca o botão de cancelar à esquerda, padrão de UX
    }).then((result) => {
        if (result.isConfirmed) {
            // Lógica de atualização de categorias
            if (linha.getAttribute('data-tipo') === 'Despesa') {
                if (categoriasData[categoria]) {
                    categoriasData[categoria] -= valor;
                    if (categoriasData[categoria] < 0) categoriasData[categoria] = 0;
                }
            }

            // Remoção com efeito visual (opcional)
            linha.style.transition = "all 0.3s";
            linha.style.opacity = "0";
            
            setTimeout(() => {
                linha.remove();
                calcularTudo();
                if (typeof atualizarGrafico === 'function') atualizarGrafico();
                
                setTimeout(salvarExcel(), 100)
                // Feedback de sucesso (opcional)
                Swal.fire({
                    title: 'Excluído!',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false,
                    timerProgressBar: true,
                    willClose: () => {
                        // Dispara o salvamento exatamente quando o alerta está sumindo
                        salvarExcel();
                    }
                    });

                }, 1000);
        }
    });

}

// --- CÁLCULOS E CATEGORIAS ---
function atualizarLinhasCartoesPrincipais() {
    // 1. Criamos um mapa para acumular o total de cada cartão
    let totaisPorCartao = {};

    // 2. Percorremos a tabela de detalhamento de faturas
    document.querySelectorAll('#tabelaCartao tbody tr').forEach(tr => {
        const nomeCartao = "Cartão " + tr.cells[0].innerText.trim();
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
        const nomeCartao = "Cartão " + tr.cells[0].innerText.trim();
        const valor = limparValor(tr.cells[3].innerText);
        totaisPorCartao[nomeCartao] = (totaisPorCartao[nomeCartao] || 0) + valor;
    });

    const tabelaPrincipal = document.querySelector('#tabelaDespesas tbody');

    // 2. Para cada cartão que tem gasto, garantir que ele esteja na tabela principal
    for (const [nomeCartao, total] of Object.entries(totaisPorCartao)) {
        // Busca se já existe uma linha com esse cartão na tabela principal
        let linhaExistente = Array.from(tabelaPrincipal.querySelectorAll('tr'))
            .find(tr => tr.cells[3].innerText.trim() === nomeCartao);

        if (linhaExistente) {
            // Se já existe, apenas atualiza o valor na coluna 3
            linhaExistente.cells[4].innerText = total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            linhaExistente.cells[4].setAttribute('data-valor', total);
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
                    <td><input type="date" class="form-control form-control-sm" value=""></td> <td>Fatura Mensal</td> <td>${nomeCartao}</td> <td data-valor="${total}">${total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                    <td>Fatura Mensal</td>
                    <td>${nomeCartao}</td>
                    <td>${total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                    <td style="color: #F44336">Despesa</td>
                    <td>
                        <button class="btn-edit" onclick="editarDespesa(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                            </svg>
                        </button>
                        <button class="btn-delete" onclick="excluirDespesa(this)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                <line x1="10" y1="11" x2="10" y2="17"></line>
                                <line x1="14" y1="11" x2="14" y2="17"></line>
                            </svg>
                        </button>
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
                    <button class="btn-delete" onclick="excluirItemCartao(this)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            <line x1="10" y1="11" x2="10" y2="17"></line>
                            <line x1="14" y1="11" x2="14" y2="17"></line>
                        </svg>
                    </button>
                </td>
            </tr>`;

        // Limpa apenas os campos de descrição e valor
        inputDesc.value = '';
        inputValor.value = '';

        // --- ATUALIZAÇÕES EM CADEIA ---
        sincronizarTotaisCartoes(); // Soma os itens e joga o total na tabela principal
        atualizarGrafico();         // Reconstrói o gráfico de pizza com os novos detalhes
        calcularTudo();             // Atualiza os cards de saldo no topo
        setTimeout(salvarExcel(), 300)
        
    } else {
        alert("Por favor, preencha a descrição e o valor do item!");
    }
}

function excluirItemCartao(btn) {
    const trRemovido = btn.closest('tr');
    const descricaoItem = trRemovido.cells[1].innerText.trim();
    const nomeCartaoRemovido = trRemovido.cells[0].innerText.trim();

    Swal.fire({
        title: 'Remover da fatura?',
        text: `Você está excluindo: ${descricaoItem}`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, remover!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            // Efeito visual de saída
            trRemovido.style.transition = "all 0.3s";
            trRemovido.style.opacity = "0";

            setTimeout(() => {
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
                        // Se você usa data-valor na tabela principal, limpe-o também:
                        linhaPrincipal.cells[3].setAttribute('data-valor', '0');
                    }
                }

                // Atualizações do sistema
                sincronizarTotaisCartoes();
                if (typeof atualizarGrafico === 'function') atualizarGrafico();
                calcularTudo();

                // Feedback rápido de sucesso
                const Toast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1500,
                    timerProgressBar: true
                });
                Toast.fire({
                    icon: 'success',
                    title: 'Item removido'
                });
                setTimeout(salvarExcel(), 300)
            }, 300);
        }
    });
}

let cartoesDisponiveis = ["Nubank", "Inter"]; // Lista inicial

function atualizarSelectCartoes() {
    const select = document.getElementById('escolhaCartao');
    if (!select) return;
    
    select.innerHTML = '<option value="">Selecione o Cartão</option>';
    cartoesDisponiveis.forEach(nome => {
        select.innerHTML += `<option value="${nome}">${nome}</option>`;
    });
}

function cadastrarNovoCartao() {
    const input = document.getElementById('novoNomeCartao');
    const nome = input.value.trim();
    
    if (nome && !cartoesDisponiveis.includes(nome)) {
        cartoesDisponiveis.push(nome);
        input.value = '';
        renderizarListaGerenciamento();
        atualizarSelectCartoes();
        // Dica: Chame sua função de salvarExcel() aqui para persistir a lista
        setTimeout(salvarExcel(), 300)
    }
}

function excluirCartaoCadastrado(nome) {
    if (confirm(`Remover o cartão ${nome} da lista de opções?`)) {
        cartoesDisponiveis = cartoesDisponiveis.filter(c => c !== nome);
        renderizarListaGerenciamento();
        atualizarSelectCartoes();
        setTimeout(salvarExcel(), 300)
    }
}

function renderizarListaGerenciamento() {
    const lista = document.getElementById('listaCartoesCadastrados');
    lista.innerHTML = '';
    cartoesDisponiveis.forEach(nome => {
        lista.innerHTML += `
            <li style="display:flex; justify-content:space-between; padding:5px; border-bottom:1px solid #eee;">
                ${nome} 
                <span onclick="excluirCartaoCadastrado('${nome}')" style="cursor:pointer; color:red;">×</span>
            </li>`;
    });
}

// Funções para abrir/fechar o modal
function abrirModalCartoes() { document.getElementById('modalCartoes').style.display = 'block'; renderizarListaGerenciamento(); }
function fecharModalCartoes() { document.getElementById('modalCartoes').style.display = 'none'; }

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
        if (tr.cells[4]) {
            const valor = limparValor(tr.cells[4].innerText);
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

    // 4. Somar Tabela de Investimentos
    let totalInvestimentos = 0;
    document.querySelectorAll('#tabelaInvestimentos tbody tr').forEach(tr => {
        // Buscamos o valor no atributo data-valor que definimos anteriormente
        const celulaValor = tr.cells[2];
        if (celulaValor) {
            const valor = parseFloat(celulaValor.getAttribute('data-valor')) || 0;
            totalInvestimentos += valor;
        }
    });

    // Atualiza os Cards de Resumo
    document.getElementById('receitasBox').textContent = formatarMoeda(receitaTotalFinal);    
    document.getElementById('totalDespesasBox').textContent = formatarMoeda(totalDespesas);
    document.getElementById('saldoBox').textContent = formatarMoeda(saldoFinalCalculado);
    document.getElementById('investimentosBox').textContent = formatarMoeda(totalInvestimentos);
    
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

let chartHistorico; 
let dadosOriginais = []; // Nova variável para guardar o que vem do banco

function atualizarGraficoHistorico() {
    const mes = mesGlobal;
    const ano = document.getElementById('anoSelecionado').value;

    fetch(`/historico_6meses?mes=${mes}&ano=${ano}`)
        .then(res => res.json())
        .then(data => {
            dadosOriginais = data; // Guardamos os dados aqui para usar na troca de abas
            alternarGrafico('geral'); // Inicializa mostrando o Geral
        });
}

function alternarGrafico(tipo) {
    const ctx = document.getElementById('graficoHistorico').getContext('2d');
    
    // Atualiza visual dos botões (opcional, se você criou os IDs btnGeral e btnInvest)
    document.getElementById('btnGeral')?.classList.toggle('active', tipo === 'geral');
    document.getElementById('btnInvest')?.classList.toggle('active', tipo === 'investimentos');

    if (chartHistorico) chartHistorico.destroy();

    const labels = dadosOriginais.map(d => d.mes);
    let datasets = [];
    let tipoGrafico = 'bar';

    if (tipo === 'geral') {
        tipoGrafico = 'bar';
        const receitas = dadosOriginais.map(d => {
            const base = parseFloat(d.salarioBruto) || 0;
            const desc = parseFloat(d.totalDescontos) || 0;
            const cred = parseFloat(d.totalCreditos) || 0;
            const out  = parseFloat(d.outrasReceitas) || 0;
            const ant  = parseFloat(d.saldoAnterior) || 0;
            return (base - desc) + cred + out + ant;
        });
        const despesas = dadosOriginais.map(d => parseFloat(d.despesas) || 0);

        datasets = [
            { label: 'Receitas', data: receitas, backgroundColor: '#4CAF50', borderRadius: 5 },
            { label: 'Despesas', data: despesas, backgroundColor: '#F44336', borderRadius: 5 }
        ];
    } else {
        tipoGrafico = 'line';
        // Aqui pegamos o valor de investimentos do seu objeto data
        const investimentos = dadosOriginais.map(d => parseFloat(d.totalInvestido) || 0);

        datasets = [{
            label: 'Evolução Investimentos',
            data: investimentos,
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 4
        }];
    }

    chartHistorico = new Chart(ctx, {
        type: tipoGrafico,
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            plugins: { legend: { display: false },
                title: {
                display: true,
                text: 'Últimos 6 Meses',
                align: 'center', // Alinha à esquerda para não bater nos botões da direita
                font: {
                    size: 16,
                    weight: 'bold'
                },
                padding: {
                    top: 0,
                    bottom: 10
                }
            }
                    }, // Mostra legenda só no investimento
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { 
                        callback: (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), 
                        maxTicksLimit: 5 // Reduzi para 5 para despoluir ainda mais
                    }
                }
            }
        }
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
        if (tr.cells.length < 5) return;
        const cat = tr.cells[3].innerText.trim();
        const valor = extrairValor(tr.cells[4].innerText);
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
                <button class="btn-edit" onclick="editarDesconto(this)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                </button>
                <button class="btn-delete" onclick="excluirDesconto(this)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            </td>
        </tr>`;

        document.getElementById('descricaoDesconto').value = '';
        document.getElementById('valorDesconto').value = '';
        calcularTudo();
        setTimeout(salvarExcel, 300)
    }
}

function excluirDesconto(botao) {
    const linha = botao.closest('tr');
    const descricaoItem = linha.cells[0].innerText.trim();

    Swal.fire({
        title: 'Excluir desconto?',
        text: `Removendo: ${descricaoItem}`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            // Efeito visual de saída (fade out)
            linha.style.transition = "all 0.3s";
            linha.style.opacity = "0";

            setTimeout(() => {
                linha.remove();
                
                // Recalcula todos os totais do dashboard
                calcularTudo();

                // Notificação rápida no canto da tela
                const Toast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1500,
                    timerProgressBar: true
                });
                
                Toast.fire({
                    icon: 'success',
                    title: 'Desconto removido'
                });

                setTimeout(salvarExcel(), 300);
            }, 300);
        }
    });
}

function editarDespesa(botao) {
    const linha = botao.closest('tr');
    
    // Captura dos textos das células (Índices ajustados para a nova coluna Pago)
    const isPago = linha.cells[0].querySelector('input').checked;
    const vencimento = linha.cells[1].querySelector('input').value;
    const descricao = linha.cells[2].innerText.trim();
    const categoria = linha.cells[3].innerText.trim();
    const valorTexto = linha.cells[4].innerText;
    const tipo = linha.cells[5].innerText.trim();

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
    document.getElementById('dataVencimento').value = vencimento
    
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

// 2. Função que cria a linha estática na tabela
function adicionarLinhaInvestimento(nome, tipo, valor) {
    const tbody = document.querySelector('#tabelaInvestimentos tbody');
    const tr = document.createElement('tr');
    
    const valorFormatado = valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    tr.innerHTML = `
        <td>${nome}</td>
        <td>${tipo}</td>
        <td data-valor="${valor}">${valorFormatado}</td>
        <td style="text-align: center;">
            <button class="btn-edit" onclick="carregarParaEdicao(this)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            </button>
            <button class="btn-delete" onclick="removerInvestimento(this)">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
            </button>
        </td>
    `;
    tbody.appendChild(tr);
    calcularTotalInvestimentos();
}

function carregarParaEdicao(btn) {
    // 1. Localiza a linha (tr) onde o botão foi clicado
    const tr = btn.closest('tr');
    
    // 2. Captura os dados das células
    const nome = tr.cells[0].innerText;
    const tipo = tr.cells[1].innerText;
    // Pega o valor puro que salvamos no atributo data-valor
    const valor = tr.cells[2].getAttribute('data-valor');

    // 3. Joga os valores de volta para os campos de input abaixo da tabela
    document.getElementById('inv_nome').value = nome;
    document.getElementById('inv_tipo').value = tipo;

    const valorNumerico = parseFloat(
        valor.replace('R$', '')
                  .replace(/\s/g, '')
                  .replace(/\./g, '')
                  .replace(',', '.')
    ) || 0;

    document.getElementById('inv_valor').value = valorNumerico.toFixed(2);

    // 4. Remove a linha da tabela (ela será "re-adicionada" quando você clicar em Add)
    tr.remove();

    // 5. Recalcula os totais e atualiza o gráfico
    calcularTotalInvestimentos();
    
    // 6. Coloca o foco no campo nome para facilitar
    document.getElementById('inv_nome').focus();
}

// 1. Função que lê os campos de baixo e manda para a tabela
function adicionarInvestimentoManual() {
    const nomeEl = document.getElementById('inv_nome');
    const tipoEl = document.getElementById('inv_tipo');
    const valorEl = document.getElementById('inv_valor');

    if (!nomeEl || !valorEl) return;

    const nome = nomeEl.value;
    const tipo = tipoEl.value;
    const valorStr = valorEl.value;
    
    if (!nome.trim() || !valorStr.trim()) {
        alert("Preencha o nome e o valor!");
        return;
    }

    // Tente usar sua limparMoeda, mas se falhar, use um fallback básico
    let valor;
    try {
        valor = limparMoeda(valorStr);
    } catch (e) {
        // Fallback caso limparMoeda não exista
        valor = parseFloat(valorStr.replace(/[^\d,]/g, '').replace(',', '.')) || 0;
    }

    adicionarLinhaInvestimento(nome, tipo, valor);

    // Limpa os campos após adicionar
    nomeEl.value = '';
    valorEl.value = '';
    nomeEl.focus(); 

    setTimeout(salvarExcel(), 300)
}

function calcularTotalInvestimentos() {
    let total = 0;
    document.querySelectorAll('#tabelaInvestimentos tbody tr').forEach(tr => {
        const v = parseFloat(tr.cells[2].getAttribute('data-valor')) || 0;
        total += v;
    });
    
    // 1. Atualiza o Box de Resumo e o Rodapé da Tabela
    const display = document.getElementById('totalInvestimentoExibicao');
    if (display) display.innerText = total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    
    const box = document.getElementById('investimentosBox');
    if (box) box.textContent = total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    // 2. ATUALIZAÇÃO DO GRÁFICO (O "Pulo do Gato")
    // O último item do array dadosOriginais representa o mês atual
    if (typeof dadosOriginais !== 'undefined' && dadosOriginais.length > 0) {
        dadosOriginais[dadosOriginais.length - 1].totalInvestido = total;
        
        // Se o gráfico de investimentos estiver visível, redesenha ele
        const btnInvest = document.getElementById('btnInvest');
        if (btnInvest && btnInvest.classList.contains('active')) {
            alternarGrafico('investimentos');
        }
    }

    // Atualiza os demais cálculos de saldo
    if (typeof calcularTudo === "function") calcularTudo();
}

function removerInvestimento(btn) {
    const linha = btn.closest('tr');
    const descricaoItem = linha.cells[0].innerText.trim();
    const valorItem = linha.cells[2].innerText.trim();

    Swal.fire({
        title: 'Excluir investimento?',
        text: `Removendo: ${descricaoItem} (${valorItem})`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            // Efeito visual de saída
            linha.style.transition = "all 0.3s";
            linha.style.opacity = "0";

            setTimeout(() => {
                linha.remove();
                
                // Atualiza o total de investimentos e o gráfico
                calcularTotalInvestimentos();

                // Notificação rápida (Toast)
                const Toast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1500,
                    timerProgressBar: true
                });
                
                Toast.fire({
                    icon: 'success',
                    title: 'Investimento removido'
                });

                setTimeout(salvarExcel(), 300)
            }, 300);
        }
    });
}

function verificarClasseStatus(pago, vencimento) {
    if (pago) return "linha-paga";
    
    if (vencimento) {
        const dataVenc = new Date(vencimento + 'T00:00:00');
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0); // Compara apenas o dia

        if (dataVenc < hoje) {
            return "linha-atrasada";
        }
    }
    return ""; // Linha normal (pendente mas no prazo)
}

document.getElementById('salarioBruto').addEventListener('input', calcularTudo);
document.getElementById('saldoAnterior').addEventListener('input', calcularTudo);
document.getElementById('anoSelecionado').addEventListener('change', trocarMes);