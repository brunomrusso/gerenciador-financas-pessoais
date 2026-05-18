"""Bot Telegram em thread separada do Flask.

Usa python-telegram-bot 21.x em modo polling.
"""
import os
import threading


def start_bot_thread(flask_app):
    """Inicia o bot em uma thread daemon."""
    def run():
        try:
            import asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
            from app.telegram_bot.bot import run_bot
            run_bot(flask_app)
        except Exception as e:
            print(f'[Telegram] Erro fatal: {e}')

    t = threading.Thread(target=run, daemon=True, name='telegram-bot')
    t.start()
