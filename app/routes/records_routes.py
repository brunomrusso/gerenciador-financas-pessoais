from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import MonthlyRecord, Discount, Expense, CardDetail, Investment, Category
from datetime import datetime
import json

bp = Blueprint('records', __name__, url_prefix='/api/records')

@bp.route('', methods=['GET'])
@jwt_required()
def get_records():
    user_id = int(get_jwt_identity())
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = MonthlyRecord.query.filter_by(user_id=user_id)
    
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=int(year))
    
    records = query.all()
    return jsonify([r.to_dict() for r in records]), 200

@bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_record(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    return jsonify(record.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_record():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('month') or not data.get('year'):
        return jsonify({'error': 'Mês e ano são obrigatórios'}), 400
    
    existing = MonthlyRecord.query.filter_by(
        user_id=user_id,
        month=data['month'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'error': 'Registro para este mês já existe'}), 409
    
    record = MonthlyRecord(
        user_id=user_id,
        month=data['month'],
        year=data['year'],
        saldo_anterior=data.get('saldo_anterior', 0),
        salario_bruto=data.get('salario_bruto', 0)
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify(record.to_dict()), 201

@bp.route('/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_record(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    data = request.get_json()
    
    if 'saldo_anterior' in data:
        record.saldo_anterior = data['saldo_anterior']
    if 'salario_bruto' in data:
        record.salario_bruto = data['salario_bruto']
    
    record.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(record.to_dict()), 200

@bp.route('/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_record(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'message': 'Registro deletado com sucesso'}), 200

@bp.route('/<int:record_id>/discounts', methods=['POST'])
@jwt_required()
def add_discount(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('descricao') or data.get('valor') is None:
        return jsonify({'error': 'Descrição e valor são obrigatórios'}), 400
    
    discount = Discount(
        record_id=record_id,
        descricao=data['descricao'],
        valor=data['valor']
    )
    
    db.session.add(discount)
    db.session.commit()
    
    return jsonify(discount.to_dict()), 201

@bp.route('/discounts/<int:discount_id>', methods=['DELETE'])
@jwt_required()
def delete_discount(discount_id):
    user_id = int(get_jwt_identity())
    discount = Discount.query.join(MonthlyRecord).filter(
        Discount.id == discount_id,
        MonthlyRecord.user_id == user_id
    ).first()
    
    if not discount:
        return jsonify({'error': 'Desconto não encontrado'}), 404
    
    db.session.delete(discount)
    db.session.commit()
    
    return jsonify({'message': 'Desconto deletado com sucesso'}), 200

@bp.route('/<int:record_id>/expenses', methods=['POST'])
@jwt_required()
def add_expense(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('descricao') or data.get('valor') is None:
        return jsonify({'error': 'Descrição e valor são obrigatórios'}), 400
    
    expense = Expense(
        record_id=record_id,
        descricao=data['descricao'],
        valor=data['valor'],
        tipo=data.get('tipo', 'Despesa')
    )
    
    db.session.add(expense)
    db.session.commit()
    
    return jsonify(expense.to_dict()), 201

@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.join(MonthlyRecord).filter(
        Expense.id == expense_id,
        MonthlyRecord.user_id == user_id
    ).first()
    
    if not expense:
        return jsonify({'error': 'Despesa não encontrada'}), 404
    
    db.session.delete(expense)
    db.session.commit()
    
    return jsonify({'message': 'Despesa deletada com sucesso'}), 200

@bp.route('/<int:record_id>/investments', methods=['POST'])
@jwt_required()
def add_investment(record_id):
    user_id = int(get_jwt_identity())
    record = MonthlyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({'error': 'Registro não encontrado'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('descricao') or data.get('valor') is None:
        return jsonify({'error': 'Descrição e valor são obrigatórios'}), 400
    
    investment = Investment(
        record_id=record_id,
        descricao=data['descricao'],
        valor=data['valor']
    )
    
    db.session.add(investment)
    db.session.commit()
    
    return jsonify(investment.to_dict()), 201

@bp.route('/investments/<int:investment_id>', methods=['DELETE'])
@jwt_required()
def delete_investment(investment_id):
    user_id = int(get_jwt_identity())
    investment = Investment.query.join(MonthlyRecord).filter(
        Investment.id == investment_id,
        MonthlyRecord.user_id == user_id
    ).first()
    
    if not investment:
        return jsonify({'error': 'Investimento não encontrado'}), 404
    
    db.session.delete(investment)
    db.session.commit()
    
    return jsonify({'message': 'Investimento deletado com sucesso'}), 200

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    month = request.args.get('month')
    year = request.args.get('year')
    
    if not month or not year:
        return jsonify({'error': 'Mês e ano são obrigatórios'}), 400
    
    meses_lista = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    try:
        idx_ref = meses_lista.index(month)
        ano_ref = int(year)
    except (ValueError, IndexError):
        return jsonify({'error': 'Mês ou ano inválido'}), 400
    
    historico = []
    
    for i in range(5, -1, -1):
        temp_idx = idx_ref - i
        temp_ano = ano_ref
        
        if temp_idx < 0:
            temp_idx += 12
            temp_ano -= 1
        
        mes_alvo = meses_lista[temp_idx]
        
        res_mes = {
            "mes": f"{mes_alvo[:3]}/{str(temp_ano)[2:]}",
            "salarioBruto": 0,
            "totalDescontos": 0,
            "totalCreditos": 0,
            "outrasReceitas": 0,
            "saldoAnterior": 0,
            "despesas": 0,
            "totalInvestido": 0
        }
        
        record = MonthlyRecord.query.filter_by(
            user_id=user_id,
            year=temp_ano,
            month=mes_alvo
        ).first()
        
        if record:
            descontos_lista = [d.to_dict() for d in record.discounts]
            movimentacoes = [e.to_dict() for e in record.expenses]
            investimentos_lista = [i.to_dict() for i in record.investments]
            
            total_investido_mes = sum(float(inv.get('valor', 0)) for inv in investimentos_lista)
            total_creditos = sum(d['valor'] for d in descontos_lista if d['valor'] > 0)
            total_descontos = sum(abs(d['valor']) for d in descontos_lista if d['valor'] < 0)
            
            receitas_extras = sum(m['valor'] for m in movimentacoes if m.get('tipo') == 'Receita')
            total_despesas = sum(m['valor'] for m in movimentacoes if m.get('tipo', 'Despesa') == 'Despesa')
            
            res_mes["salarioBruto"] = record.salario_bruto or 0
            res_mes["saldoAnterior"] = record.saldo_anterior or 0
            res_mes["totalDescontos"] = total_descontos
            res_mes["totalCreditos"] = total_creditos
            res_mes["outrasReceitas"] = receitas_extras
            res_mes["despesas"] = total_despesas
            res_mes["totalInvestido"] = total_investido_mes
        
        historico.append(res_mes)
    
    return jsonify(historico), 200

@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = int(get_jwt_identity())
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([c.to_dict() for c in categories]), 200

@bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    existing = Category.query.filter_by(user_id=user_id, nome=data['nome']).first()
    if existing:
        return jsonify({'error': 'Categoria já existe'}), 409
    
    category = Category(user_id=user_id, nome=data['nome'])
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201
