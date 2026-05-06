from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import InvestmentAccount, InvestmentTransaction, MonthlyRecord

bp = Blueprint('investments', __name__, url_prefix='/api/investments')


@bp.route('', methods=['GET'])
@jwt_required()
def list_accounts():
    user_id = int(get_jwt_identity())
    accounts = InvestmentAccount.query.filter_by(user_id=user_id).order_by(InvestmentAccount.nome).all()
    return jsonify([a.to_dict() for a in accounts]), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    nome = (data.get('nome') or '').strip()
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    tipo = (data.get('tipo') or 'Geral').strip() or 'Geral'
    acc = InvestmentAccount(user_id=user_id, nome=nome, tipo=tipo)
    db.session.add(acc)
    db.session.commit()
    return jsonify(acc.to_dict()), 201


@bp.route('/<int:account_id>', methods=['PATCH'])
@jwt_required()
def update_account(account_id):
    user_id = int(get_jwt_identity())
    acc = InvestmentAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not acc:
        return jsonify({'error': 'Conta não encontrada'}), 404
    data = request.get_json() or {}
    if 'nome' in data: acc.nome = data['nome']
    if 'tipo' in data: acc.tipo = data['tipo']
    db.session.commit()
    return jsonify(acc.to_dict()), 200


@bp.route('/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id):
    user_id = int(get_jwt_identity())
    acc = InvestmentAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not acc:
        return jsonify({'error': 'Conta não encontrada'}), 404
    db.session.delete(acc)
    db.session.commit()
    return jsonify({'message': 'Conta removida'}), 200


@bp.route('/<int:account_id>/transactions', methods=['GET'])
@jwt_required()
def list_transactions(account_id):
    user_id = int(get_jwt_identity())
    acc = InvestmentAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not acc:
        return jsonify({'error': 'Conta não encontrada'}), 404
    record_id = request.args.get('record_id', type=int)
    q = InvestmentTransaction.query.filter_by(account_id=account_id)
    if record_id:
        q = q.filter_by(record_id=record_id)
    txs = q.order_by(InvestmentTransaction.data.desc(), InvestmentTransaction.id.desc()).all()
    return jsonify([t.to_dict() for t in txs]), 200


@bp.route('/<int:account_id>/transactions', methods=['POST'])
@jwt_required()
def create_transaction(account_id):
    user_id = int(get_jwt_identity())
    acc = InvestmentAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not acc:
        return jsonify({'error': 'Conta não encontrada'}), 404
    data = request.get_json() or {}
    tipo = (data.get('tipo') or '').lower().strip()
    if tipo not in ('aporte', 'saque', 'rendimento'):
        return jsonify({'error': "tipo deve ser 'aporte', 'saque' ou 'rendimento'"}), 400
    try:
        valor = float(data.get('valor') or 0)
    except (TypeError, ValueError):
        return jsonify({'error': 'Valor inválido'}), 400
    if valor <= 0:
        return jsonify({'error': 'Valor deve ser positivo'}), 400

    record_id = data.get('record_id')
    if record_id:
        rec = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not rec:
            return jsonify({'error': 'Mês não encontrado'}), 404

    if tipo == 'saque' and valor > acc.saldo():
        return jsonify({'error': 'Saque maior que saldo disponível'}), 400

    tx = InvestmentTransaction(
        account_id=account_id,
        record_id=record_id,
        tipo=tipo,
        valor=valor,
        descricao=(data.get('descricao') or '').strip() or None,
        data=data.get('data') or '',
        financial_account_id=data.get('financial_account_id') or None
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({**tx.to_dict(), 'saldo_atual': acc.saldo()}), 201


@bp.route('/transactions/<int:tx_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(tx_id):
    user_id = int(get_jwt_identity())
    tx = (InvestmentTransaction.query
          .join(InvestmentAccount)
          .filter(InvestmentTransaction.id == tx_id, InvestmentAccount.user_id == user_id)
          .first())
    if not tx:
        return jsonify({'error': 'Transação não encontrada'}), 404
    db.session.delete(tx)
    db.session.commit()
    return jsonify({'message': 'Transação removida'}), 200


@bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    """Retorna saldo total + movimentações de um record (mes)."""
    user_id = int(get_jwt_identity())
    record_id = request.args.get('record_id', type=int)
    accounts = InvestmentAccount.query.filter_by(user_id=user_id).all()
    saldo_total = sum(a.saldo() for a in accounts)

    aportes_mes = saques_mes = rendimentos_mes = 0.0
    if record_id:
        txs = (InvestmentTransaction.query
               .join(InvestmentAccount)
               .filter(InvestmentAccount.user_id == user_id,
                       InvestmentTransaction.record_id == record_id)
               .all())
        for t in txs:
            if t.tipo == 'aporte': aportes_mes += float(t.valor or 0)
            elif t.tipo == 'saque': saques_mes += float(t.valor or 0)
            elif t.tipo == 'rendimento': rendimentos_mes += float(t.valor or 0)

    return jsonify({
        'saldo_total': round(saldo_total, 2),
        'aportes_mes': round(aportes_mes, 2),
        'saques_mes': round(saques_mes, 2),
        'rendimentos_mes': round(rendimentos_mes, 2),
        'liquido_mes': round(aportes_mes - saques_mes, 2),
        'accounts': [a.to_dict() for a in accounts]
    }), 200
