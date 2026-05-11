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
    salario_account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    discounts = db.relationship('Discount', backref='record', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='record', lazy=True, cascade='all, delete-orphan')
    card_details = db.relationship('CardDetail', backref='record', lazy=True, cascade='all, delete-orphan')
    investments = db.relationship('Investment', backref='record', lazy=True, cascade='all, delete-orphan')
    salaries = db.relationship('Salary', backref='record', lazy=True, cascade='all, delete-orphan')
    transfers = db.relationship('Transfer', backref='record', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month', name='unique_user_month'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'saldo_anterior': self.saldo_anterior,
            'salario_bruto': self.salario_bruto,
            'salario_account_id': self.salario_account_id,
            'salaries': [s.to_dict() for s in self.salaries],
            'transfers': [t.to_dict() for t in self.transfers],
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
    account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    recorrente = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'valor': self.valor,
            'account_id': self.account_id,
            'recorrente': self.recorrente or False
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
    tags = db.Column(db.String(255), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    eh_credito = db.Column(db.Boolean, default=False)
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
            'recorrente': self.recorrente or False,
            'tags': [t.strip() for t in (self.tags or '').split(',') if t.strip()],
            'account_id': self.account_id,
            'eh_credito': self.eh_credito or False
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
    tags = db.Column(db.String(255), nullable=True)
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
            'group_id': self.group_id,
            'tags': [t.strip() for t in (self.tags or '').split(',') if t.strip()]
        }


class FinancialAccount(db.Model):
    """Conta financeira: corrente, poupança, carteira, etc."""
    __tablename__ = 'financial_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(30), default='corrente')  # corrente, poupanca, carteira, outro
    saldo_inicial = db.Column(db.Float, default=0)
    cor = db.Column(db.String(20), default='#667eea')
    icone = db.Column(db.String(10), default='💰')
    padrao = db.Column(db.Boolean, default=False)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo or 'corrente',
            'saldo_inicial': float(self.saldo_inicial or 0),
            'cor': self.cor or '#667eea',
            'icone': self.icone or '💰',
            'padrao': bool(self.padrao),
            'ativa': bool(self.ativa)
        }


class InvestmentAccount(db.Model):
    __tablename__ = 'investment_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), default='Geral')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship('InvestmentTransaction', backref='account', lazy=True, cascade='all, delete-orphan')

    def saldo(self):
        total = 0.0
        for t in self.transactions:
            if t.tipo == 'aporte' or t.tipo == 'rendimento':
                total += float(t.valor or 0)
            elif t.tipo == 'saque':
                total -= float(t.valor or 0)
        return round(total, 2)

    def to_dict(self, include_saldo=True):
        d = {'id': self.id, 'nome': self.nome, 'tipo': self.tipo or 'Geral'}
        if include_saldo:
            d['saldo'] = self.saldo()
        return d


class InvestmentTransaction(db.Model):
    __tablename__ = 'investment_transactions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('investment_accounts.id'), nullable=False, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=True, index=True)
    tipo = db.Column(db.String(20), nullable=False)  # aporte, saque, rendimento
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    data = db.Column(db.String(10), nullable=True)
    financial_account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'record_id': self.record_id,
            'tipo': self.tipo,
            'valor': float(self.valor or 0),
            'descricao': self.descricao or '',
            'data': self.data or '',
            'financial_account_id': self.financial_account_id
        }


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    orcamento = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'nome', name='unique_user_category'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'orcamento': self.orcamento or 0
        }


class Salary(db.Model):
    """Salário/renda de um mês. Permite múltiplas entradas em contas diferentes."""
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=False, default='Salário')
    valor = db.Column(db.Float, nullable=False, default=0)
    account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    recorrente = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao or 'Salário',
            'valor': float(self.valor or 0),
            'account_id': self.account_id,
            'recorrente': bool(self.recorrente)
        }


class Transfer(db.Model):
    """Transferência entre contas: sai de from_account_id e entra em to_account_id.
    Não afeta o saldo total do mês (cancela)."""
    __tablename__ = 'transfers'

    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('monthly_records.id'), nullable=False, index=True)
    descricao = db.Column(db.String(255), nullable=True)
    valor = db.Column(db.Float, nullable=False, default=0)
    from_account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'), nullable=True, index=True)
    data = db.Column(db.String(10), nullable=True)  # YYYY-MM-DD
    recorrente = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao or '',
            'valor': float(self.valor or 0),
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'data': self.data,
            'recorrente': bool(self.recorrente)
        }
