"""Bot Telegram com menus inline para lancamentos.

Comandos:
- /start <codigo>: vincula conta usando codigo de 6 digitos gerado no app
- /menu, /start (apos vinculado): mostra menu principal
- /saldo: saldo total das contas
- /unlink: desvincula

Fluxos por menu (inline keyboard):
- Nova despesa: conta -> valor -> descricao -> categoria -> confirma
- Nova receita: conta -> valor -> descricao -> confirma
- Saldo: lista todas as contas
- Resumo: receitas/despesas do mes atual
"""
import os
import functools
from datetime import datetime, date

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)
from telegram.request import HTTPXRequest


MONTHS_PT = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


# Estado de conversacao por chat_id (em memoria, reset ao reiniciar bot)
STATE: dict = {}


def _flask_app():
    """Acessa o app Flask injetado no modulo."""
    return _STATE_APP['app']


_STATE_APP = {'app': None}


# ──────────────────── Helpers ────────────────────

def with_app_ctx(func):
    """Decorator que garante app_context Flask em handlers async do bot."""
    @functools.wraps(func)
    async def wrapper(update, context):
        app = _flask_app()
        if app is None:
            return await func(update, context)
        with app.app_context():
            return await func(update, context)
    return wrapper


def _format_brl(v: float) -> str:
    return f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def _get_user_id(chat_id: int):
    """Retorna user_id vinculado ao chat ou None. Requer app_context ativo."""
    from app.models import TelegramLink
    link = TelegramLink.query.filter_by(chat_id=chat_id).first()
    return link.user_id if link else None


def _current_record(user_id: int):
    """Pega/cria registro do mes atual."""
    from app.models import MonthlyRecord
    today = date.today()
    year = today.year
    month = MONTHS_PT[today.month - 1]
    rec = MonthlyRecord.query.filter_by(user_id=user_id, year=year, month=month).first()
    if not rec:
        rec = MonthlyRecord(user_id=user_id, year=year, month=month,
                            saldo_anterior=0, salario_bruto=0)
        from app import db
        db.session.add(rec)
        db.session.commit()
    return rec


def _accounts(user_id: int):
    from app.models import FinancialAccount
    return FinancialAccount.query.filter_by(user_id=user_id, ativa=True).order_by(
        FinancialAccount.padrao.desc(), FinancialAccount.nome).all()


def _categorias(user_id: int):
    from app.models import Category
    cats = Category.query.filter_by(user_id=user_id).order_by(Category.nome).all()
    return [c.nome for c in cats] or ['Mercado', 'Transporte', 'Lazer', 'Saude', 'Outros']


# ──────────────────── Comandos ────────────────────

@with_app_ctx
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args or []

    # Tentativa de vincular com codigo
    if args and len(args[0]) == 6 and args[0].isdigit():
        return await _try_link(update, args[0])

    user_id = _get_user_id(chat_id)
    if not user_id:
        await update.message.reply_text(
            '👋 Olá! Sou o bot do CashFlow.\n\n'
            'Para vincular sua conta:\n'
            '1️⃣ Entre no app web\n'
            '2️⃣ Abra seu perfil → Telegram\n'
            '3️⃣ Gere um código de 6 dígitos\n'
            '4️⃣ Envie aqui: /start SEU_CODIGO\n\n'
            'Exemplo: /start 123456'
        )
        return

    await _show_menu(update, context)


async def _try_link(update: Update, code: str):
    from datetime import datetime
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    with _flask_app().app_context():
        from app import db
        from app.models import TelegramLink, TelegramLinkCode

        link_code = TelegramLinkCode.query.filter_by(code=code).first()
        if not link_code:
            await update.message.reply_text('❌ Código inválido.')
            return
        if link_code.expires_at < datetime.utcnow():
            db.session.delete(link_code)
            db.session.commit()
            await update.message.reply_text('⏱ Código expirado. Gere outro no app.')
            return

        # Remove vinculo anterior se houver
        TelegramLink.query.filter_by(chat_id=chat_id).delete()
        TelegramLink.query.filter_by(user_id=link_code.user_id).delete()

        link = TelegramLink(user_id=link_code.user_id, chat_id=chat_id, username=username)
        db.session.add(link)
        db.session.delete(link_code)
        db.session.commit()

    await update.message.reply_text(
        '✅ Conta vinculada com sucesso!\n\nDigite /menu para começar.'
    )


@with_app_ctx
async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_menu(update, context)


async def _show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = _get_user_id(chat_id)
    if not user_id:
        await update.message.reply_text('Use /start primeiro para vincular sua conta.')
        return

    STATE.pop(chat_id, None)

    keyboard = [
        [InlineKeyboardButton('💸 Nova despesa', callback_data='new_expense'),
         InlineKeyboardButton('💰 Nova receita', callback_data='new_income')],
        [InlineKeyboardButton('🔁 Transferência', callback_data='new_transfer'),
         InlineKeyboardButton('📊 Saldo', callback_data='saldo')],
        [InlineKeyboardButton('📋 Resumo do mês', callback_data='resumo')],
    ]
    msg = '🏠 *Menu principal*\n\nO que deseja fazer?'
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


@with_app_ctx
async def cmd_unlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    from app import db
    from app.models import TelegramLink
    TelegramLink.query.filter_by(chat_id=chat_id).delete()
    db.session.commit()
    STATE.pop(chat_id, None)
    await update.message.reply_text('🔌 Desvinculado. Use /start <código> para vincular novamente.')


@with_app_ctx
async def cmd_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = _get_user_id(chat_id)
    if not user_id:
        await update.message.reply_text('Use /start primeiro.')
        return
    await _send_saldo(update, user_id)


async def _send_saldo(update: Update, user_id: int):
    with _flask_app().app_context():
        from app.routes.accounts_routes import _compute_balance
        accs = _accounts(user_id)
        lines = []
        total = 0.0
        for a in accs:
            s = _compute_balance(a, accs)
            total += s
            lines.append(f'{a.icone or "💰"} *{a.nome}*: {_format_brl(s)}')
        text = '*💼 Saldos*\n\n' + '\n'.join(lines) + f'\n\n*Total:* {_format_brl(total)}'

    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')


# ──────────────────── Callbacks (botoes) ────────────────────

@with_app_ctx
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    user_id = _get_user_id(chat_id)
    if not user_id:
        await query.message.reply_text('Use /start <código> primeiro.')
        return

    data = query.data or ''

    if data == 'cancel':
        STATE.pop(chat_id, None)
        await query.message.reply_text('❌ Cancelado.')
        await _show_menu(update, context)
        return

    if data == 'menu':
        await _show_menu(update, context)
        return

    if data == 'saldo':
        await _send_saldo(update, user_id)
        return

    if data == 'resumo':
        await _send_resumo(update, user_id)
        return

    if data == 'new_expense':
        STATE[chat_id] = {'flow': 'expense', 'step': 'account'}
        await _ask_account(query, user_id, 'Despesa')
        return

    if data == 'new_income':
        STATE[chat_id] = {'flow': 'income', 'step': 'account'}
        await _ask_account(query, user_id, 'Receita')
        return

    if data == 'new_transfer':
        STATE[chat_id] = {'flow': 'transfer', 'step': 'from'}
        await _ask_account(query, user_id, 'De qual conta?', key='from')
        return

    # Selecao de conta
    if data.startswith('acc:'):
        await _handle_account_selection(update, context, chat_id, user_id, data)
        return

    # Selecao de categoria
    if data.startswith('cat:'):
        st = STATE.get(chat_id) or {}
        st['categoria'] = data[4:]
        st['step'] = 'confirm'
        STATE[chat_id] = st
        await _confirm(update, context, chat_id)
        return

    if data == 'confirm:yes':
        await _save_entry(update, context, chat_id, user_id)
        return


async def _ask_account(query, user_id: int, title: str, key: str = 'account'):
    accs = _accounts(user_id)
    if not accs:
        await query.message.reply_text('⚠️ Você não tem contas ativas. Cadastre uma no app.')
        return
    kb = [[InlineKeyboardButton(f'{a.icone or "💰"} {a.nome}', callback_data=f'acc:{key}:{a.id}')] for a in accs]
    kb.append([InlineKeyboardButton('❌ Cancelar', callback_data='cancel')])
    await query.message.reply_text(f'*{title}* — escolha a conta:', reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def _handle_account_selection(update, context, chat_id, user_id, data):
    # acc:<key>:<id>
    parts = data.split(':')
    key = parts[1]
    acc_id = int(parts[2])
    st = STATE.get(chat_id) or {}
    flow = st.get('flow')

    if flow == 'transfer':
        if key == 'from':
            st['from_account_id'] = acc_id
            st['step'] = 'to'
            STATE[chat_id] = st
            await _ask_account(update.callback_query, user_id, 'Para qual conta?', key='to')
            return
        if key == 'to':
            if acc_id == st.get('from_account_id'):
                await update.callback_query.message.reply_text('⚠️ Conta de destino deve ser diferente da origem.')
                return
            st['to_account_id'] = acc_id
            st['step'] = 'valor'
            STATE[chat_id] = st
            await update.callback_query.message.reply_text('Digite o *valor* da transferência (ex: 250.00):', parse_mode='Markdown')
            return

    # despesa/receita
    st['account_id'] = acc_id
    st['step'] = 'valor'
    STATE[chat_id] = st
    await update.callback_query.message.reply_text('Digite o *valor* (ex: 49.90):', parse_mode='Markdown')


async def _confirm(update, context, chat_id):
    st = STATE.get(chat_id) or {}
    flow = st.get('flow')
    user_id = _get_user_id(chat_id)
    accs = {a.id: a for a in _accounts(user_id)}

    if flow == 'expense':
        acc = accs.get(st.get('account_id'))
        text = (f'*Confirmar despesa*\n\n'
                f'💸 Valor: {_format_brl(st["valor"])}\n'
                f'📝 Descrição: {st.get("descricao") or "—"}\n'
                f'🏦 Conta: {acc.icone if acc else ""} {acc.nome if acc else ""}\n'
                f'🏷 Categoria: {st.get("categoria") or "Outros"}')
    elif flow == 'income':
        acc = accs.get(st.get('account_id'))
        text = (f'*Confirmar receita*\n\n'
                f'💰 Valor: {_format_brl(st["valor"])}\n'
                f'📝 Descrição: {st.get("descricao") or "—"}\n'
                f'🏦 Conta: {acc.icone if acc else ""} {acc.nome if acc else ""}')
    elif flow == 'transfer':
        af = accs.get(st.get('from_account_id'))
        at = accs.get(st.get('to_account_id'))
        text = (f'*Confirmar transferência*\n\n'
                f'🔁 Valor: {_format_brl(st["valor"])}\n'
                f'De: {af.nome if af else ""}\n'
                f'Para: {at.nome if at else ""}')
    else:
        return

    kb = [[InlineKeyboardButton('✅ Salvar', callback_data='confirm:yes'),
           InlineKeyboardButton('❌ Cancelar', callback_data='cancel')]]
    msg_target = update.callback_query.message if update.callback_query else update.message
    await msg_target.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')


async def _save_entry(update, context, chat_id, user_id):
    st = STATE.get(chat_id) or {}
    flow = st.get('flow')
    msg = update.callback_query.message

    with _flask_app().app_context():
        from app import db
        from app.models import Expense, Transfer
        rec = _current_record(user_id)

        if flow == 'expense':
            e = Expense(
                record_id=rec.id,
                descricao=st.get('descricao') or 'Despesa via Telegram',
                valor=float(st['valor']),
                tipo='Despesa',
                categoria=st.get('categoria') or 'Outros',
                account_id=st.get('account_id'),
                data=date.today().isoformat(),
                pago=True,
            )
            db.session.add(e)
            db.session.commit()
            await msg.reply_text('✅ Despesa registrada!')
        elif flow == 'income':
            e = Expense(
                record_id=rec.id,
                descricao=st.get('descricao') or 'Receita via Telegram',
                valor=float(st['valor']),
                tipo='Receita',
                categoria='Receita',
                account_id=st.get('account_id'),
                data=date.today().isoformat(),
                pago=True,
            )
            db.session.add(e)
            db.session.commit()
            await msg.reply_text('✅ Receita registrada!')
        elif flow == 'transfer':
            t = Transfer(
                record_id=rec.id,
                descricao='Transferência via Telegram',
                valor=float(st['valor']),
                from_account_id=st.get('from_account_id'),
                to_account_id=st.get('to_account_id'),
                data=date.today().isoformat(),
            )
            db.session.add(t)
            db.session.commit()
            await msg.reply_text('✅ Transferência registrada!')

    STATE.pop(chat_id, None)
    await _show_menu(update, context)


# ──────────────────── Mensagens de texto ────────────────────

@with_app_ctx
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (update.message.text or '').strip()

    user_id = _get_user_id(chat_id)
    if not user_id:
        await update.message.reply_text('Use /start <código> para vincular sua conta.')
        return

    st = STATE.get(chat_id)
    if not st:
        await _show_menu(update, context)
        return

    step = st.get('step')

    # Captura valor
    if step == 'valor':
        try:
            valor = float(text.replace(',', '.').replace('R$', '').strip())
            if valor <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text('⚠️ Valor inválido. Digite só o número (ex: 49.90):')
            return
        st['valor'] = valor
        flow = st.get('flow')
        if flow == 'transfer':
            st['step'] = 'confirm'
            STATE[chat_id] = st
            await _confirm(update, context, chat_id)
        else:
            st['step'] = 'descricao'
            STATE[chat_id] = st
            await update.message.reply_text('Digite uma *descrição* curta (ou envie "—" para pular):', parse_mode='Markdown')
        return

    if step == 'descricao':
        st['descricao'] = '' if text in ('-', '—', '/skip') else text
        flow = st.get('flow')
        if flow == 'expense':
            cats = _categorias(user_id)
            kb = []
            row = []
            for c in cats[:12]:
                row.append(InlineKeyboardButton(c, callback_data=f'cat:{c}'))
                if len(row) == 2:
                    kb.append(row)
                    row = []
            if row:
                kb.append(row)
            kb.append([InlineKeyboardButton('❌ Cancelar', callback_data='cancel')])
            st['step'] = 'categoria'
            STATE[chat_id] = st
            await update.message.reply_text('Escolha a *categoria*:', reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        else:
            st['step'] = 'confirm'
            STATE[chat_id] = st
            await _confirm(update, context, chat_id)
        return


# ──────────────────── Resumo ────────────────────

async def _send_resumo(update, user_id: int):
    with _flask_app().app_context():
        from app.models import MonthlyRecord, Expense, Salary
        today = date.today()
        rec = MonthlyRecord.query.filter_by(
            user_id=user_id, year=today.year, month=MONTHS_PT[today.month - 1]
        ).first()
        if not rec:
            text = '📋 Sem registro neste mês ainda.'
        else:
            despesas = sum(e.valor for e in rec.expenses if e.tipo != 'Receita' and not e.eh_credito) if rec.expenses else 0
            receitas_extra = sum(e.valor for e in rec.expenses if e.tipo == 'Receita' or e.eh_credito) if rec.expenses else 0
            salarios = (rec.salario_bruto or 0) + sum(s.valor for s in (rec.salaries or []))
            liquido = salarios + receitas_extra - despesas
            text = (f'*📋 Resumo {rec.month}/{rec.year}*\n\n'
                    f'💰 Receitas: {_format_brl(salarios + receitas_extra)}\n'
                    f'💸 Despesas: {_format_brl(despesas)}\n'
                    f'📊 Líquido: {_format_brl(liquido)}')
    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(text, parse_mode='Markdown')


# ──────────────────── Setup ────────────────────

def run_bot(flask_app):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print('[Telegram] TELEGRAM_BOT_TOKEN ausente, bot nao iniciado.')
        return

    _STATE_APP['app'] = flask_app

    # Timeouts generosos para Render free (cold start lento)
    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=30.0,
        write_timeout=30.0,
        connect_timeout=30.0,
        pool_timeout=10.0,
    )
    app = Application.builder().token(token).request(request).build()
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('menu', cmd_menu))
    app.add_handler(CommandHandler('saldo', cmd_saldo))
    app.add_handler(CommandHandler('unlink', cmd_unlink))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    print('[Telegram] Bot rodando (polling)...')
    app.run_polling(close_loop=False, stop_signals=None)
