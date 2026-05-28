from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models import (
    FinancialAccount, Discount, Expense, MonthlyRecord,
    InvestmentTransaction, InvestmentAccount, CardExpense, CreditCard, Salary, Transfer,
    CardPayment
)

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')


def _ensure_default(user_id):
    """Garante que o usuário tem ao menos uma conta padrão."""
    has_any = FinancialAccount.query.filter_by(user_id=user_id).count() > 0
    if not has_any:
        default = FinancialAccount(
            user_id=user_id, nome='Conta Principal', tipo='corrente',
            saldo_inicial=0, padrao=True, icone='💳'
        )
        db.session.add(default)
        db.session.commit()


def _compute_balance(account, all_accounts):
    """Saldo da conta = saldo_inicial + receitas - despesas, considerando movimentos
    com account_id == this OR (sem account_id E this for a padrão)."""
    user_id = account.user_id
    is_default = account.padrao

    # IDs de outras contas para identificar movimentos "sem conta" como pertencentes à padrão
    def matches(col):
        if is_default:
            return or_(col == account.id, col.is_(None))
        return col == account.id

    saldo = float(account.saldo_inicial or 0)

    # Salário primário do MonthlyRecord: vai para a conta especificada em salario_account_id;
    # se não especificado, cai na conta padrão (compatibilidade com registros antigos)
    sal_this = db.session.query(db.func.coalesce(db.func.sum(MonthlyRecord.salario_bruto), 0)) \
        .filter(MonthlyRecord.user_id == user_id,
                MonthlyRecord.salario_account_id == account.id).scalar()
    saldo += float(sal_this or 0)
    if is_default:
        sal_orphan = db.session.query(db.func.coalesce(db.func.sum(MonthlyRecord.salario_bruto), 0)) \
            .filter(MonthlyRecord.user_id == user_id,
                    MonthlyRecord.salario_account_id.is_(None)).scalar()
        saldo += float(sal_orphan or 0)

    # Salários adicionais (tabela salaries): seguem a regra de matches() (account_id ou null=padrão)
    extra_sal = db.session.query(db.func.coalesce(db.func.sum(Salary.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id, matches(Salary.account_id)).scalar()
    saldo += float(extra_sal or 0)

    # Discounts: positivos somam, negativos subtraem (já tem sinal)
    disc_total = db.session.query(db.func.coalesce(db.func.sum(Discount.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id, matches(Discount.account_id)).scalar()
    saldo += float(disc_total or 0)

    # Despesas/débitos (subtraem): não é Receita E não é crédito E está marcada como paga
    exp_total = db.session.query(db.func.coalesce(db.func.sum(Expense.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id,
                Expense.tipo != 'Receita',
                or_(Expense.eh_credito.is_(None), Expense.eh_credito == False),
                Expense.pago == True,
                matches(Expense.account_id)).scalar()
    saldo -= float(exp_total or 0)

    # Receitas/créditos (somam): tipo='Receita' OU eh_credito=True
    rec_total = db.session.query(db.func.coalesce(db.func.sum(Expense.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id,
                or_(Expense.tipo == 'Receita', Expense.eh_credito == True),
                matches(Expense.account_id)).scalar()
    saldo += float(rec_total or 0)

    # Faturas de cartão:
    # 1) Pagamentos explicitos: cada CardPayment desconta da conta indicada
    paid_from_this = db.session.query(db.func.coalesce(db.func.sum(CardPayment.valor), 0)) \
        .join(CreditCard, CardPayment.card_id == CreditCard.id) \
        .filter(CreditCard.user_id == user_id, CardPayment.account_id == account.id).scalar()
    saldo -= float(paid_from_this or 0)

    # 2) Fallback: fatura sem pagamentos cai inteira na conta padrao
    if is_default:
        # totais por (card, year, month)
        fatura_totais = db.session.query(
            CardExpense.card_id,
            MonthlyRecord.year,
            MonthlyRecord.month,
            db.func.coalesce(db.func.sum(CardExpense.valor), 0).label('total')
        ).join(CreditCard).join(MonthlyRecord, CardExpense.record_id == MonthlyRecord.id) \
         .filter(CreditCard.user_id == user_id) \
         .group_by(CardExpense.card_id, MonthlyRecord.year, MonthlyRecord.month).all()
        for cid, year, month, total in fatura_totais:
            paid = db.session.query(db.func.coalesce(db.func.sum(CardPayment.valor), 0)) \
                .filter(CardPayment.card_id == cid,
                        CardPayment.year == year,
                        CardPayment.month == month).scalar()
            paid = float(paid or 0)
            total = float(total or 0)
            if paid <= 0:
                # nenhum pagamento explicito: cai na padrao
                saldo -= total
            elif paid < total:
                # parcial: o restante cai na padrao
                saldo -= (total - paid)

    # Investimentos: aporte sai, saque entra; rendimentos não afetam conta
    aportes = db.session.query(db.func.coalesce(db.func.sum(InvestmentTransaction.valor), 0)) \
        .join(InvestmentAccount) \
        .filter(InvestmentAccount.user_id == user_id,
                InvestmentTransaction.tipo == 'aporte',
                matches(InvestmentTransaction.financial_account_id)).scalar()
    saques = db.session.query(db.func.coalesce(db.func.sum(InvestmentTransaction.valor), 0)) \
        .join(InvestmentAccount) \
        .filter(InvestmentAccount.user_id == user_id,
                InvestmentTransaction.tipo == 'saque',
                matches(InvestmentTransaction.financial_account_id)).scalar()
    saldo -= float(aportes or 0)
    saldo += float(saques or 0)

    # Transferências: sai da from_account, entra na to_account
    out_total = db.session.query(db.func.coalesce(db.func.sum(Transfer.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id,
                Transfer.from_account_id == account.id).scalar()
    in_total = db.session.query(db.func.coalesce(db.func.sum(Transfer.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id,
                Transfer.to_account_id == account.id).scalar()
    saldo -= float(out_total or 0)
    saldo += float(in_total or 0)

    return round(saldo, 2)


@bp.route('', methods=['GET'])
@jwt_required()
def list_accounts():
    user_id = int(get_jwt_identity())
    _ensure_default(user_id)
    accounts = FinancialAccount.query.filter_by(user_id=user_id).order_by(
        FinancialAccount.padrao.desc(), FinancialAccount.nome
    ).all()
    result = []
    for acc in accounts:
        d = acc.to_dict()
        d['saldo'] = _compute_balance(acc, accounts)
        result.append(d)
    return jsonify(result), 200


MONTHS_PT = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def _month_index(name: str) -> int:
    """Aceita nomes com ou sem acento (ex.: 'Marco' ou 'Março')."""
    if not name:
        return 0
    norm = name.strip().lower().replace('ç', 'c').replace('ã', 'a').replace('á', 'a')
    for i, m in enumerate(MONTHS_PT):
        m_norm = m.lower().replace('ç', 'c').replace('ã', 'a').replace('á', 'a')
        if norm == m_norm:
            return i
    return 0


def _record_date(record, day: str = '01') -> str:
    """Retorna data ISO YYYY-MM-DD para um record (usado quando o item não tem data)."""
    if not record:
        return ''
    mi = _month_index(record.month) + 1
    return f"{record.year:04d}-{mi:02d}-{day}"


@bp.route('/<int:account_id>/history', methods=['GET'])
@jwt_required()
def account_history(account_id):
    """Retorna timeline cronológica de todas as transações que afetam o saldo desta conta."""
    user_id = int(get_jwt_identity())
    account = FinancialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Conta não encontrada'}), 404

    is_default = account.padrao
    events = []

    # Função helper: linha de evento
    def add(date, type_, descricao, valor, source_id=None, record=None, extra=None):
        ev = {
            'date': date or '',
            'type': type_,
            'descricao': descricao,
            'valor': round(float(valor), 2),
            'source_id': source_id,
            'month': record.month if record else None,
            'year': record.year if record else None,
        }
        if extra:
            ev.update(extra)
        events.append(ev)

    # Match: registros desta conta ou (se padrão) aqueles sem conta atribuída
    def matches(account_id_val):
        if account_id_val == account.id:
            return True
        if is_default and (account_id_val is None):
            return True
        return False

    # 1) Salário primário (MonthlyRecord.salario_bruto)
    records = MonthlyRecord.query.filter_by(user_id=user_id).all()
    for r in records:
        if (r.salario_bruto or 0) > 0 and matches(r.salario_account_id):
            add(_record_date(r), 'salary_primary', 'Salário', r.salario_bruto, r.id, r)

    # 2) Salários extras
    extra_salaries = (Salary.query.join(MonthlyRecord)
                      .filter(MonthlyRecord.user_id == user_id).all())
    for s in extra_salaries:
        if matches(s.account_id):
            add(_record_date(s.record), 'salary_extra', s.descricao or 'Salário', s.valor, s.id, s.record)

    # 3) Descontos/Créditos da tabela discounts (positivos somam, negativos subtraem)
    discounts = (Discount.query.join(MonthlyRecord)
                 .filter(MonthlyRecord.user_id == user_id).all())
    for d in discounts:
        if matches(d.account_id):
            type_ = 'credit_misc' if (d.valor or 0) > 0 else 'discount'
            add(_record_date(d.record), type_, d.descricao, d.valor, d.id, d.record)

    # 4) Despesas (Expense) — débitos negativos, créditos positivos
    expenses = (Expense.query.join(MonthlyRecord)
                .filter(MonthlyRecord.user_id == user_id).all())
    for e in expenses:
        if matches(e.account_id):
            if e.eh_credito:
                add(e.data or _record_date(e.record), 'expense_credit', e.descricao, e.valor, e.id, e.record,
                    {'categoria': e.categoria, 'pago': e.pago})
            else:
                # Apenas despesas pagas afetam o saldo da conta
                if not e.pago:
                    continue
                add(e.data or _record_date(e.record), 'expense', e.descricao, -abs(e.valor or 0), e.id, e.record,
                    {'categoria': e.categoria, 'pago': e.pago})

    # 5) Transferências
    transfers = (Transfer.query.join(MonthlyRecord)
                 .filter(MonthlyRecord.user_id == user_id).all())
    for t in transfers:
        if t.from_account_id == account.id:
            add(t.data or _record_date(t.record), 'transfer_out',
                t.descricao or 'Transferência saída', -abs(t.valor or 0), t.id, t.record,
                {'to_account_id': t.to_account_id})
        if t.to_account_id == account.id:
            add(t.data or _record_date(t.record), 'transfer_in',
                t.descricao or 'Transferência entrada', abs(t.valor or 0), t.id, t.record,
                {'from_account_id': t.from_account_id})

    # 6) Investimentos (aportes saem, saques entram)
    inv_txs = (InvestmentTransaction.query.join(InvestmentAccount)
               .filter(InvestmentAccount.user_id == user_id).all())
    for it in inv_txs:
        if matches(it.financial_account_id):
            if it.tipo == 'aporte':
                add(it.data or '', 'investment_aporte',
                    f'Aporte: {it.account.nome if it.account else ""}',
                    -abs(it.valor or 0), it.id, None,
                    {'investment_account_id': it.account_id})
            elif it.tipo == 'saque':
                add(it.data or '', 'investment_saque',
                    f'Saque: {it.account.nome if it.account else ""}',
                    abs(it.valor or 0), it.id, None,
                    {'investment_account_id': it.account_id})

    # 7) Pagamentos de fatura desta conta (CardPayment)
    card_payments = (CardPayment.query.join(CreditCard, CardPayment.card_id == CreditCard.id)
                     .filter(CreditCard.user_id == user_id,
                             CardPayment.account_id == account.id).all())
    for cp in card_payments:
        card = CreditCard.query.get(cp.card_id)
        add('', 'card_payment',
            f'Pagamento fatura {card.nome if card else ""} ({cp.month}/{cp.year})',
            -abs(cp.valor or 0), cp.id, None,
            {'card_id': cp.card_id, 'year': cp.year, 'month': cp.month})

    # 8) Faturas de cartão pendentes (sem pagamento explicito) caem na padrao
    if is_default:
        # Agrupa por (card_id, year, month)
        fatura_totais = db.session.query(
            CardExpense.card_id, MonthlyRecord.year, MonthlyRecord.month,
            db.func.coalesce(db.func.sum(CardExpense.valor), 0).label('total')
        ).join(CreditCard).join(MonthlyRecord, CardExpense.record_id == MonthlyRecord.id) \
         .filter(CreditCard.user_id == user_id) \
         .group_by(CardExpense.card_id, MonthlyRecord.year, MonthlyRecord.month).all()
        for cid, year, month, total in fatura_totais:
            paid = db.session.query(db.func.coalesce(db.func.sum(CardPayment.valor), 0)) \
                .filter(CardPayment.card_id == cid,
                        CardPayment.year == year,
                        CardPayment.month == month).scalar()
            pendente = float(total or 0) - float(paid or 0)
            if pendente > 0.01:
                card = CreditCard.query.get(cid)
                add('', 'card_pending',
                    f'Fatura pendente {card.nome if card else ""} ({month}/{year})',
                    -round(pendente, 2), cid, None,
                    {'card_id': cid, 'year': year, 'month': month})

    # Ordena: data desc, depois id desc
    events.sort(key=lambda e: (e['date'] or '0000-00-00', e.get('source_id') or 0), reverse=True)

    # Saldo inicial como evento ancorado
    if account.saldo_inicial:
        events.append({
            'date': '',
            'type': 'initial_balance',
            'descricao': 'Saldo inicial',
            'valor': round(float(account.saldo_inicial), 2),
            'source_id': None,
            'month': None,
            'year': None,
        })

    return jsonify({
        'account': account.to_dict(),
        'events': events,
        'total': len(events)
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    nome = (data.get('nome') or '').strip()
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    # Se for marcada como padrão, desmarca as outras
    if data.get('padrao'):
        FinancialAccount.query.filter_by(user_id=user_id, padrao=True).update({'padrao': False})

    acc = FinancialAccount(
        user_id=user_id,
        nome=nome,
        tipo=data.get('tipo') or 'corrente',
        saldo_inicial=float(data.get('saldo_inicial') or 0),
        cor=data.get('cor') or '#667eea',
        icone=data.get('icone') or '💰',
        padrao=bool(data.get('padrao'))
    )
    # Se é a primeira, força padrão
    if FinancialAccount.query.filter_by(user_id=user_id).count() == 0:
        acc.padrao = True

    db.session.add(acc)
    db.session.commit()
    return jsonify(acc.to_dict()), 201


@bp.route('/<int:account_id>', methods=['PATCH'])
@jwt_required()
def update_account(account_id):
    user_id = int(get_jwt_identity())
    acc = FinancialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not acc:
        return jsonify({'error': 'Conta não encontrada'}), 404
    data = request.get_json() or {}

    if 'padrao' in data and data['padrao']:
        FinancialAccount.query.filter_by(user_id=user_id, padrao=True).update({'padrao': False})
        acc.padrao = True
    elif 'padrao' in data:
        acc.padrao = bool(data['padrao'])

    if 'nome' in data: acc.nome = data['nome']
    if 'tipo' in data: acc.tipo = data['tipo']
    if 'saldo_inicial' in data: acc.saldo_inicial = float(data['saldo_inicial'])
    if 'cor' in data: acc.cor = data['cor']
    if 'icone' in data: acc.icone = data['icone']
    if 'ativa' in data: acc.ativa = bool(data['ativa'])

    db.session.commit()
    return jsonify(acc.to_dict()), 200


@bp.route('/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id):
    user_id = int(get_jwt_identity())
    acc = FinancialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not acc:
        return jsonify({'error': 'Conta não encontrada'}), 404
    if acc.padrao:
        return jsonify({'error': 'Não é possível excluir a conta padrão'}), 400
    # Desvincular movimentos para evitar quebra
    Expense.query.filter_by(account_id=account_id).update({'account_id': None})
    Discount.query.filter_by(account_id=account_id).update({'account_id': None})
    InvestmentTransaction.query.filter_by(financial_account_id=account_id).update({'financial_account_id': None})
    db.session.delete(acc)
    db.session.commit()
    return jsonify({'message': 'Conta removida'}), 200
