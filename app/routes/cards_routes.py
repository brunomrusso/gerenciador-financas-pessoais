from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import CreditCard, CardExpense, MonthlyRecord
from uuid import uuid4

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
    tags_in = data.get('tags')
    if isinstance(tags_in, list):
        tags_str = ','.join(str(t).strip() for t in tags_in if str(t).strip()) or None
    else:
        tags_str = ((tags_in or '').strip() or None)

    group_id = str(uuid4())
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
            tags=tags_str,
            parcelas_total=parcelas,
            parcela_atual=i + 1,
            group_id=group_id
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
    apply_to_all = data.get('apply_to_all', False)
    new_parcelas = int(data.get('parcelas_total', exp.parcelas_total))

    if apply_to_all and exp.group_id:
        group_exps = (CardExpense.query
                      .join(CreditCard)
                      .filter(CardExpense.group_id == exp.group_id,
                              CreditCard.user_id == user_id)
                      .order_by(CardExpense.parcela_atual)
                      .all())

        if new_parcelas != exp.parcelas_total:
            base_exp = next((e for e in group_exps if e.parcela_atual == 1), group_exps[0])
            base_record = MonthlyRecord.query.get(base_exp.record_id)
            card_id = exp.card_id
            descricao = data.get('descricao', exp.descricao)
            valor_parcela = float(data.get('valor', exp.valor))
            categoria = data.get('categoria', exp.categoria)
            data_str = data.get('data', exp.data)
            gid = exp.group_id

            for ge in group_exps:
                db.session.delete(ge)
            db.session.flush()

            created = []
            for i in range(new_parcelas):
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
                new_exp = CardExpense(
                    card_id=card_id, record_id=target.id,
                    descricao=descricao, valor=valor_parcela,
                    categoria=categoria, data=data_str,
                    parcelas_total=new_parcelas, parcela_atual=i + 1,
                    group_id=gid
                )
                db.session.add(new_exp)
                created.append(new_exp)

            db.session.commit()
            return jsonify([e.to_dict() for e in created]), 200
        else:
            for ge in group_exps:
                if 'descricao' in data: ge.descricao = data['descricao']
                if 'valor' in data: ge.valor = float(data['valor'])
                if 'categoria' in data: ge.categoria = data['categoria']
                if 'data' in data: ge.data = data['data']
                if 'tags' in data:
                    tg = data['tags']
                    ge.tags = (','.join(str(t).strip() for t in tg if str(t).strip()) or None) if isinstance(tg, list) else ((tg or '').strip() or None)
            db.session.commit()
            return jsonify(exp.to_dict()), 200
    else:
        if 'descricao' in data: exp.descricao = data['descricao']
        if 'valor' in data: exp.valor = float(data['valor'])
        if 'categoria' in data: exp.categoria = data['categoria']
        if 'data' in data: exp.data = data['data']
        if 'parcelas_total' in data: exp.parcelas_total = int(data['parcelas_total'])
        if 'tags' in data:
            tg = data['tags']
            exp.tags = (','.join(str(t).strip() for t in tg if str(t).strip()) or None) if isinstance(tg, list) else ((tg or '').strip() or None)
        db.session.commit()
        return jsonify(exp.to_dict()), 200


@bp.route('/expenses/<int:expense_id>/move', methods=['POST'])
@jwt_required()
def move_card_expense(expense_id):
    user_id = int(get_jwt_identity())
    exp = (CardExpense.query
           .join(CreditCard)
           .filter(CardExpense.id == expense_id, CreditCard.user_id == user_id)
           .first())
    if not exp:
        return jsonify({'error': 'Despesa não encontrada'}), 404

    data = request.get_json()
    target_month = data.get('month')
    target_year = int(data.get('year'))
    if not target_month or not target_year:
        return jsonify({'error': 'month e year são obrigatórios'}), 400

    target_record = MonthlyRecord.query.filter_by(
        user_id=user_id, month=target_month, year=target_year
    ).first()
    if not target_record:
        target_record = MonthlyRecord(
            user_id=user_id, month=target_month, year=target_year,
            saldo_anterior=0, salario_bruto=0
        )
        db.session.add(target_record)
        db.session.flush()

    card_id = exp.card_id
    descricao = exp.descricao
    valor_parcela = exp.valor
    categoria = exp.categoria
    data_str = exp.data
    parcelas_total = exp.parcelas_total
    group_id = exp.group_id

    if group_id and parcelas_total > 1:
        group_exps = (CardExpense.query
                      .join(CreditCard)
                      .filter(CardExpense.group_id == group_id,
                              CreditCard.user_id == user_id)
                      .order_by(CardExpense.parcela_atual)
                      .all())
        for ge in group_exps:
            db.session.delete(ge)
        db.session.flush()

        created = []
        for i in range(parcelas_total):
            if i == 0:
                target = target_record
            else:
                m_name, m_year = _advance_month(target_month, target_year, i)
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
            new_exp = CardExpense(
                card_id=card_id, record_id=target.id,
                descricao=descricao, valor=valor_parcela,
                categoria=categoria, data=data_str,
                parcelas_total=parcelas_total, parcela_atual=i + 1,
                group_id=group_id
            )
            db.session.add(new_exp)
            created.append(new_exp)

        db.session.commit()
        return jsonify([e.to_dict() for e in created]), 200
    else:
        exp.record_id = target_record.id
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

    delete_all = request.args.get('delete_all', 'false').lower() == 'true'

    if delete_all and exp.group_id:
        group_exps = (CardExpense.query
                      .join(CreditCard)
                      .filter(CardExpense.group_id == exp.group_id,
                              CreditCard.user_id == user_id)
                      .all())
        for ge in group_exps:
            db.session.delete(ge)
    else:
        db.session.delete(exp)

    db.session.commit()
    return jsonify({'message': 'Despesa deletada'}), 200
