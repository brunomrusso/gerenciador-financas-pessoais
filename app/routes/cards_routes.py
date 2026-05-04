from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import CreditCard, CardExpense, MonthlyRecord

bp = Blueprint('cards', __name__, url_prefix='/api/cards')

MONTHS = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def _advance_month(month_name: str, year: int, delta: int):
    idx = MONTHS.index(month_name) + delta
    return MONTHS[idx % 12], year + idx // 12


# ── Gerenciar cartões ────────────────────────────────────────────────────────

@bp.route('', methods=['GET'])
@jwt_required()
def get_cards():
    user_id = int(get_jwt_identity())
    cards = CreditCard.query.filter_by(user_id=user_id).order_by(CreditCard.nome).all()
    return jsonify([c.to_dict() for c in cards])


@bp.route('', methods=['POST'])
@jwt_required()
def create_card():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    nome = (data.get('nome') or '').strip()
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    card = CreditCard(user_id=user_id, nome=nome)
    db.session.add(card)
    db.session.commit()
    return jsonify(card.to_dict()), 201


@bp.route('/<int:card_id>', methods=['DELETE'])
@jwt_required()
def delete_card(card_id):
    user_id = int(get_jwt_identity())
    card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Cartão não encontrado'}), 404
    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Cartão deletado'}), 200


# ── Faturas do mês ───────────────────────────────────────────────────────────

@bp.route('/faturas/<int:record_id>', methods=['GET'])
@jwt_required()
def get_faturas(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404

    expenses = (CardExpense.query
                .join(CreditCard)
                .filter(CardExpense.record_id == record_id,
                        CreditCard.user_id == user_id)
                .order_by(CardExpense.created_at)
                .all())

    faturas: dict = {}
    for exp in expenses:
        cid = exp.card_id
        if cid not in faturas:
            faturas[cid] = {
                'card_id': cid,
                'card_nome': exp.card.nome,
                'total': 0.0,
                'expenses': []
            }
        faturas[cid]['total'] = round(faturas[cid]['total'] + exp.valor, 2)
        faturas[cid]['expenses'].append(exp.to_dict())

    return jsonify(list(faturas.values()))


# ── Despesas individuais do cartão ───────────────────────────────────────────

@bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_card_expense():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    card = CreditCard.query.filter_by(id=data.get('card_id'), user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Cartão não encontrado'}), 404

    base_record = MonthlyRecord.query.filter_by(id=data.get('record_id'), user_id=user_id).first()
    if not base_record:
        return jsonify({'error': 'Registro não encontrado'}), 404

    valor_total = float(data['valor'])
    parcelas = max(1, int(data.get('parcelas', 1)))
    valor_parcela = round(valor_total / parcelas, 2)
    descricao = data['descricao']
    categoria = data.get('categoria', 'Outros')
    data_str = data.get('data', '')

    created = []
    for i in range(parcelas):
        if i == 0:
            target = base_record
        else:
            m_name, m_year = _advance_month(base_record.month, int(base_record.year), i)
            target = MonthlyRecord.query.filter_by(
                user_id=user_id, month=m_name, year=m_year
            ).first()
            if not target:
                target = MonthlyRecord(
                    user_id=user_id, month=m_name, year=m_year,
                    saldo_anterior=0, salario_bruto=0
                )
                db.session.add(target)
                db.session.flush()

        exp = CardExpense(
            card_id=card.id,
            record_id=target.id,
            descricao=descricao,
            valor=valor_parcela,
            categoria=categoria,
            data=data_str,
            parcelas_total=parcelas,
            parcela_atual=i + 1
        )
        db.session.add(exp)
        created.append(exp)

    db.session.commit()
    return jsonify([e.to_dict() for e in created]), 201


@bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_card_expense(expense_id):
    user_id = int(get_jwt_identity())
    exp = (CardExpense.query
           .join(CreditCard)
           .filter(CardExpense.id == expense_id, CreditCard.user_id == user_id)
           .first())
    if not exp:
        return jsonify({'error': 'Despesa não encontrada'}), 404
    data = request.get_json()
    if 'descricao' in data:
        exp.descricao = data['descricao']
    if 'valor' in data:
        exp.valor = float(data['valor'])
    if 'categoria' in data:
        exp.categoria = data['categoria']
    if 'data' in data:
        exp.data = data['data']
    db.session.commit()
    return jsonify(exp.to_dict()), 200


@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_card_expense(expense_id):
    user_id = int(get_jwt_identity())
    exp = (CardExpense.query
           .join(CreditCard)
           .filter(CardExpense.id == expense_id, CreditCard.user_id == user_id)
           .first())
    if not exp:
        return jsonify({'error': 'Despesa não encontrada'}), 404
    db.session.delete(exp)
    db.session.commit()
    return jsonify({'message': 'Despesa deletada'}), 200
