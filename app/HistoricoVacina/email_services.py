import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("email_service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class EmailService:
    """Serviço para envio de e-mails."""
    
    MOCK = True  # ⚡ Ative para mock (apenas log) / False para envio real

    def __init__(self):
        self.host = os.getenv("EMAIL_HOST")
        self.port = int(os.getenv("EMAIL_PORT", 587))
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")
        self.email_from = os.getenv("EMAIL_FROM", self.user)

    def enviar_confirmacao_vacina(self, destinatario, nome_usuario, vacina, data):
        """Envia e-mail de confirmação de registro de vacina."""
        assunto = f"Confirmação de Registro - {vacina}"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2b6cb0;">Olá, {nome_usuario}!</h2>
            <p>Seu registro da vacina <strong>{vacina}</strong> aplicada em <strong>{data}</strong> foi adicionado com sucesso ao sistema ImuneTrack.</p>
            <p>Mantenha seu histórico vacinal sempre atualizado!</p>
            <hr style="border:none;border-top:1px solid #ccc;">
            <small style="color: #555;">Este é um e-mail automático. Não responda.</small>
        </body>
        </html>
        """

        # 🚀 Modo Mock: apenas log
        if self.MOCK:
            logger.info(f"[MOCK] E-mail para {destinatario} com assunto '{assunto}' enviado com sucesso!")
            logger.info(f"[MOCK] Corpo do e-mail: {html}")
            return True

        # Envio real via SMTP (não funcionará no Render)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = self.email_from
        msg["To"] = destinatario
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
                logger.info(f"E-mail enviado para {destinatario}")
            return True
        except Exception as e:
            logger.error(f"Falha ao enviar e-mail para {destinatario}: {e}")
            return False

# Instância global
email_service = EmailService()
