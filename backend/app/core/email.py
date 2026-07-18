import resend
import random
import os

resend.api_key = os.getenv("RESEND_API_KEY")

REMETENTE = os.getenv("RESEND_FROM_EMAIL", "noreply@feelscoding.com.br")


def gerar_codigo_verificacao() -> str:
    return str(random.randint(100000, 999999))


def enviar_email_verificacao(destinatario: str, codigo: str):
    resend.Emails.send({
        "from": f"dIscovery <{REMETENTE}>",
        "to": [destinatario],
        "subject": "Código de verificação - dIscovery",
        "html": f"""
            <p>Olá!</p>
            <p>Seu código de verificação do dIscovery é: <strong>{codigo}</strong></p>
            <p>Esse código expira em 15 minutos.</p>
        """,
    })