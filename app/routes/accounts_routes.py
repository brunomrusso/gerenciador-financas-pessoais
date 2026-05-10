from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models import (
    FinancialAccount, Discount, Expense, MonthlyRecord,
    InvestmentTransaction, InvestmentAccount, CardExpense, CreditCard
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

    # Salário: vai para a conta especificada em salario_account_id;
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

    # Discounts: positivos somam, negativos subtraem (já tem sinal)
    disc_total = db.session.query(db.func.coalesce(db.func.sum(Discount.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id, matches(Discount.account_id)).scalar()
    saldo += float(disc_total or 0)

    # Despesas/débitos (subtraem): não é Receita E não é crédito
    exp_total = db.session.query(db.func.coalesce(db.func.sum(Expense.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id,
                Expense.tipo != 'Receita',
                or_(Expense.eh_credito.is_(None), Expense.eh_credito == False),
                matches(Expense.account_id)).scalar()
    saldo -= float(exp_total or 0)

    # Receitas/créditos (somam): tipo='Receita' OU eh_credito=True
    rec_total = db.session.query(db.func.coalesce(db.func.sum(Expense.valor), 0)) \
        .join(MonthlyRecord) \
        .filter(MonthlyRecord.user_id == user_id,
                or_(Expense.tipo == 'Receita', Expense.eh_credito == True),
                matches(Expense.account_id)).scalar()
    saldo += float(rec_total or 0)

    # Faturas de cartão: caem na conta padrão (simplificação)
    if is_default:
        card_total = db.session.query(db.func.coalesce(db.func.sum(CardExpense.valor), 0)) \
            .join(CreditCard) \
            .filter(CreditCard.user_id == user_id).scalar()
        saldo -= float(card_total or 0)

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
