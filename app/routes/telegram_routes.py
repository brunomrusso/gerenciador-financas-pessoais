"""Rotas para vincular conta web ao Telegram via codigo de 6 digitos."""
import random
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import TelegramLink, TelegramLinkCode

bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')


def _gen_code() -> str:
    return f'{random.randint(0, 999999):06d}'


@bp.route('/link-code', methods=['POST'])
@jwt_required()
def create_link_code():
    """Gera codigo de 6 digitos valido por 10min para vincular Telegram."""
    user_id = int(get_jwt_identity())

    # Limpa codigos expirados deste user
    TelegramLinkCode.query.filter(
        TelegramLinkCode.user_id == user_id,
        TelegramLinkCode.expires_at < datetime.utcnow()
    ).delete(synchronize_session=False)

    # Gera codigo unico
    for _ in range(20):
        code = _gen_code()
        if not TelegramLinkCode.query.filter_by(code=code).first():
            break
    else:
        return jsonify({'error': 'Falha ao gerar codigo, tente novamente'}), 500

    item = TelegramLinkCode(
        user_id=user_id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'code': code, 'expires_in_minutes': 10}), 200


@bp.route('/status', methods=['GET'])
@jwt_required()
def link_status():
    user_id = int(get_jwt_identity())
    link = TelegramLink.query.filter_by(user_id=user_id).first()
    return jsonify({
        'linked': bool(link),
        'username': link.username if link else None,
        'linked_at': link.linked_at.isoformat() if link and link.linked_at else None,
    }), 200


@bp.route('/unlink', methods=['DELETE'])
@jwt_required()
def unlink():
    user_id = int(get_jwt_identity())
    TelegramLink.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': 'Desvinculado'}), 200
