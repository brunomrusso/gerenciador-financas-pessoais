"""Envio de email via Resend API.

Fallback em dev: imprime no console se RESEND_API_KEY ausente.
"""
import os


def send_email(to: str, subject: str, html: str) -> bool:
    """Envia email. Retorna True se enviado ou impresso no console."""
    api_key = os.getenv('RESEND_API_KEY')
    sender = os.getenv('RESEND_FROM', 'onboarding@resend.dev')

    if not api_key:
        print(f'[Mailer DEV] Para: {to}')
        print(f'[Mailer DEV] Assunto: {subject}')
        print(f'[Mailer DEV] HTML:\n{html}\n')
        return True

    try:
        import requests
        resp = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'from': sender,
                'to': [to],
                'subject': subject,
                'html': html,
            },
            timeout=10,
        )
        if resp.status_code >= 400:
            print(f'[Mailer ERRO] {resp.status_code}: {resp.text}')
            return False
        return True
    except Exception as e:
        print(f'[Mailer ERRO] {e}')
        return False


def send_password_reset(email: str, link: str, nome: str = '') -> bool:
    saudacao = f'Olá {nome},' if nome else 'Olá,'
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; max-width: 560px; margin: 0 auto; padding: 24px; color: #333;">
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 32px; border-radius: 12px; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 28px;">💰 CashFlow</h1>
        <p style="margin: 8px 0 0; opacity: 0.9;">Recuperação de senha</p>
      </div>
      <div style="background: #fff; padding: 32px; border: 1px solid #eee; border-top: none; border-radius: 0 0 12px 12px;">
        <p>{saudacao}</p>
        <p>Recebemos uma solicitação para redefinir sua senha. Clique no botão abaixo para criar uma nova senha (válido por 15 minutos):</p>
        <p style="text-align: center; margin: 32px 0;">
          <a href="{link}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block;">Redefinir senha</a>
        </p>
        <p style="font-size: 13px; color: #777;">Se você não solicitou, ignore este email. Sua senha continua a mesma.</p>
        <p style="font-size: 12px; color: #999; word-break: break-all;">Link direto: {link}</p>
      </div>
    </body>
    </html>
    """
    return send_email(email, 'Redefinição de senha — CashFlow', html)
