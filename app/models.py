from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    monthly_records = db.relationship('MonthlyRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class MonthlyRecord(db.Model):
    __tablename__ = 'monthly_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.String(20), nullable=False)
    saldo_anterior = db.Column(db.Float, default=0)
    salario_bruto = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    discounts = db.relationship('Discount', backref='record', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='record', lazy=True, cascade='all, delete-orphan')
    card_details = db.relationship('CardDetail', backref='record', lazy=True, cascade='all, delete-orphan')
    investments = db.relationship('Investment', backref='record', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month', name='unique_user_month'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'saldo_anterior': self.saldo_anterior,
            'salario_bruto': self.salario_bruto,
            'discounts': [d.to_dict() for d in self.discounts],
            'expenses': [e.to_dict() for e in self.expenses],
            'card_details': [c.to_dict() for c in self.card_details],
            'investments': [i.to_dict() for i in self.investments],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Discount(db.Model):
    __tablename__ = 'discounts'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), default='Despesa')
    categoria = db.Column(db.String(100), default='Outros')
    data = db.Column(db.String(10), nullable=True)
    pago = db.Column(db.Boolean, default=False)
    recorrente = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'tipo': self.tipo,
            'categoria': self.categoria or 'Outros',
            'data': self.data or '',
            'pago': self.pago or False,
            'recorrente': self.recorrente or False
        }

class CardDetail(db.Model):
    __tablename__ = 'card_details'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    card_name = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'card_name': self.card_name,
            'valor': self.valor
        }

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor
        }

class CreditCard(db.Model):
    __tablename__ = 'credit_cards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    card_expenses = db.relationship('CardExpense', backref='card', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {'id': self.id, 'nome': self.nome}


class CardExpense(db.Model):
    __tablename__ = 'card_expenses'

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'), nullable=False, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100), default='Outros')
    data = db.Column(db.String(10), nullable=True)
    parcelas_total = db.Column(db.Integer, default=1)
    parcela_atual = db.Column(db.Integer, default=1)
    group_id = db.Column(db.String(36), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'record_id': self.record_id,
            'descricao': self.descricao,
            'valor': self.valor,
            'categoria': self.categoria or 'Outros',
            'data': self.data or '',
            'parcelas_total': self.parcelas_total,
            'parcela_atual': self.parcela_atual,
            'group_id': self.group_id
        }


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'nome', name='unique_user_category'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome
        }
