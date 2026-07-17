import smtplib
import random
from email.mime.text import MIMEText
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def gerar_codigo_verificacao() -> str:
    return str(random.randint(100000, 999999))


def enviar_email_verificacao(destinatario: str, codigo: str):
    corpo = f"""
    Olá!

    Seu código de verificação do dIscovery é: {codigo}

    Esse código expira em 15 minutos.
    """
    msg = MIMEText(corpo)
    msg["Subject"] = "Código de verificação - dIscovery"
    msg["From"] = SMTP_USER
    msg["To"] = destinatario

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())