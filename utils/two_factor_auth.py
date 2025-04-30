"""
Módulo para autenticação de dois fatores.
Oferece suporte para 2FA via e-mail, SMS (usando Twilio) ou TOTP (Time-based One-Time Password).
"""
import os
import hmac
import base64
import hashlib
import time
import random
import string
import pyotp
import qrcode
from io import BytesIO
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

# Configuração do logger
logger = logging.getLogger(__name__)

# Cache de tokens temporários (em produção, isso deveria estar em Redis ou banco de dados)
# {user_id: {'token': token, 'expires_at': datetime, 'type': 'email|sms|totp'}}
TEMP_TOKENS = {}


class TwoFactorAuth:
    """
    Gerenciador de autenticação de dois fatores.
    Suporta métodos:
    - E-mail: envia um código de verificação por e-mail
    - SMS: envia um código de verificação por SMS (via Twilio)
    - TOTP: usa um aplicativo autenticador (Google Authenticator, Authy, etc.)
    """
    
    def __init__(self, app=None):
        """Inicializa o gerenciador de 2FA."""
        self.app = app
        
        # Chave secreta para TOTP
        self.totp_key = os.environ.get('TOTP_SECRET_KEY', 'zelopack-totp-secret')
        
        # Tempo de expiração do token (minutos)
        self.token_expiration = 15
    
    def generate_email_token(self, user_id: int, email: str) -> Tuple[str, datetime]:
        """
        Gera um token para autenticação via e-mail.
        
        Args:
            user_id: ID do usuário
            email: Endereço de e-mail para enviar o token
            
        Returns:
            Tuple contendo o token e a data de expiração
        """
        # Gerar token aleatório de 6 dígitos
        token = ''.join(random.choices(string.digits, k=6))
        
        # Definir expiração
        expires_at = datetime.now() + timedelta(minutes=self.token_expiration)
        
        # Armazenar no cache
        TEMP_TOKENS[user_id] = {
            'token': token,
            'expires_at': expires_at,
            'type': 'email',
            'destination': email
        }
        
        return token, expires_at
    
    def generate_sms_token(self, user_id: int, phone_number: str) -> Tuple[str, datetime]:
        """
        Gera um token para autenticação via SMS.
        
        Args:
            user_id: ID do usuário
            phone_number: Número de telefone para enviar o token
            
        Returns:
            Tuple contendo o token e a data de expiração
        """
        # Gerar token aleatório de 6 dígitos
        token = ''.join(random.choices(string.digits, k=6))
        
        # Definir expiração
        expires_at = datetime.now() + timedelta(minutes=self.token_expiration)
        
        # Armazenar no cache
        TEMP_TOKENS[user_id] = {
            'token': token,
            'expires_at': expires_at,
            'type': 'sms',
            'destination': phone_number
        }
        
        return token, expires_at
    
    def setup_totp(self, user_id: int, username: str) -> Dict[str, Any]:
        """
        Configura TOTP para um usuário.
        
        Args:
            user_id: ID do usuário
            username: Nome de usuário
            
        Returns:
            Dicionário com informações de configuração TOTP
        """
        # Gerar chave secreta
        secret_key = pyotp.random_base32()
        
        # Criar URI para QR code
        totp = pyotp.TOTP(secret_key)
        uri = totp.provisioning_uri(name=username, issuer_name="Zelopack")
        
        # Gerar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter imagem para base64
        buffer = BytesIO()
        img.save(buffer)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Retornar informações
        return {
            'secret_key': secret_key,
            'uri': uri,
            'qr_code': qr_code_base64
        }
    
    def verify_totp(self, user_id: int, token: str, secret_key: str) -> bool:
        """
        Verifica um token TOTP.
        
        Args:
            user_id: ID do usuário
            token: Token TOTP
            secret_key: Chave secreta do usuário
            
        Returns:
            True se o token for válido, False caso contrário
        """
        totp = pyotp.TOTP(secret_key)
        return totp.verify(token)
    
    def verify_token(self, user_id: int, token: str) -> bool:
        """
        Verifica um token de 2FA.
        
        Args:
            user_id: ID do usuário
            token: Token a ser verificado
            
        Returns:
            True se o token for válido, False caso contrário
        """
        # Verificar se o usuário tem um token pendente
        if user_id not in TEMP_TOKENS:
            logger.warning(f"Nenhum token pendente para o usuário {user_id}")
            return False
        
        token_info = TEMP_TOKENS[user_id]
        
        # Verificar se o token expirou
        if datetime.now() > token_info['expires_at']:
            logger.warning(f"Token expirado para o usuário {user_id}")
            del TEMP_TOKENS[user_id]
            return False
        
        # Verificar o token
        if token_info['token'] == token:
            logger.info(f"Token válido para o usuário {user_id}")
            del TEMP_TOKENS[user_id]
            return True
        
        logger.warning(f"Token inválido para o usuário {user_id}")
        return False
    
    def send_token_by_email(self, user_id: int, email: str) -> bool:
        """
        Gera e envia um token por e-mail.
        
        Args:
            user_id: ID do usuário
            email: Endereço de e-mail
            
        Returns:
            True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            token, expires_at = self.generate_email_token(user_id, email)
            
            # Obter configurações do app
            if self.app:
                with self.app.app_context():
                    from models import SystemConfig
                    
                    # Obter configurações de e-mail
                    smtp_server = SystemConfig.query.filter_by(key='email.smtp_server').first()
                    smtp_port = SystemConfig.query.filter_by(key='email.smtp_port').first()
                    smtp_username = SystemConfig.query.filter_by(key='email.smtp_username').first()
                    smtp_password = SystemConfig.query.filter_by(key='email.smtp_password').first()
                    smtp_encryption = SystemConfig.query.filter_by(key='email.smtp_encryption').first()
                    from_email = SystemConfig.query.filter_by(key='email.from_email').first()
                    from_name = SystemConfig.query.filter_by(key='email.from_name').first()
                    
                    # Verificar se todas as configurações estão disponíveis
                    if not (smtp_server and smtp_port and smtp_username and smtp_password and from_email):
                        logger.error("Configurações de e-mail incompletas")
                        return False
                    
                    # Configurações
                    smtp_config = {
                        'server': smtp_server.value,
                        'port': int(smtp_port.value),
                        'username': smtp_username.value,
                        'password': smtp_password.value,
                        'encryption': smtp_encryption.value if smtp_encryption else 'tls',
                        'from_email': from_email.value,
                        'from_name': from_name.value if from_name else 'Sistema Zelopack'
                    }
                    
                    # Enviar e-mail
                    return self._send_email(
                        email=email,
                        subject='Código de Verificação - Zelopack',
                        body=f"Seu código de verificação é: {token}\n\nEste código expira em {self.token_expiration} minutos.",
                        html_body=f"""
                            <h2>Verificação de Dois Fatores</h2>
                            <p>Seu código de verificação é:</p>
                            <h1 style="font-size: 32px; letter-spacing: 5px; font-weight: bold; padding: 10px; background-color: #f5f5f5; display: inline-block;">{token}</h1>
                            <p>Este código expira em {self.token_expiration} minutos.</p>
                            <p>Se você não solicitou este código, ignore este e-mail.</p>
                        """,
                        smtp_config=smtp_config
                    )
            else:
                logger.error("App não disponível para envio de e-mail")
                return False
        
        except Exception as e:
            logger.error(f"Erro ao enviar token por e-mail: {str(e)}")
            return False
    
    def send_token_by_sms(self, user_id: int, phone_number: str) -> bool:
        """
        Gera e envia um token por SMS.
        
        Args:
            user_id: ID do usuário
            phone_number: Número de telefone
            
        Returns:
            True se o SMS foi enviado com sucesso, False caso contrário
        """
        try:
            token, expires_at = self.generate_sms_token(user_id, phone_number)
            
            # Obter configurações do app
            if self.app:
                with self.app.app_context():
                    from models import SystemConfig
                    
                    # Obter configurações de SMS
                    twilio_account_sid = SystemConfig.query.filter_by(key='twilio.account_sid').first()
                    twilio_auth_token = SystemConfig.query.filter_by(key='twilio.auth_token').first()
                    twilio_phone_number = SystemConfig.query.filter_by(key='twilio.phone_number').first()
                    
                    # Verificar se todas as configurações estão disponíveis
                    if not (twilio_account_sid and twilio_auth_token and twilio_phone_number):
                        logger.error("Configurações de SMS incompletas")
                        return False
                    
                    # Enviar SMS via Twilio
                    from twilio.rest import Client
                    client = Client(twilio_account_sid.value, twilio_auth_token.value)
                    
                    message = client.messages.create(
                        body=f"Seu código de verificação Zelopack é: {token}. Válido por {self.token_expiration} minutos.",
                        from_=twilio_phone_number.value,
                        to=phone_number
                    )
                    
                    logger.info(f"SMS enviado com SID: {message.sid}")
                    return True
            else:
                logger.error("App não disponível para envio de SMS")
                return False
        
        except Exception as e:
            logger.error(f"Erro ao enviar token por SMS: {str(e)}")
            return False
    
    def _send_email(self, email: str, subject: str, body: str, html_body: str, smtp_config: Dict[str, Any]) -> bool:
        """
        Envia um e-mail usando as configurações especificadas.
        
        Args:
            email: Endereço de e-mail do destinatário
            subject: Assunto do e-mail
            body: Corpo de texto do e-mail
            html_body: Corpo HTML do e-mail
            smtp_config: Configurações SMTP
            
        Returns:
            True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
            msg['To'] = email
            
            # Adicionar partes
            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Conectar ao servidor
            if smtp_config['encryption'] == 'ssl':
                server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
            else:
                server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
                
                if smtp_config['encryption'] == 'tls':
                    server.starttls()
            
            # Login
            if smtp_config['username'] and smtp_config['password']:
                server.login(smtp_config['username'], smtp_config['password'])
            
            # Enviar e-mail
            server.sendmail(
                smtp_config['from_email'],
                email,
                msg.as_string()
            )
            
            # Fechar conexão
            server.quit()
            
            logger.info(f"E-mail enviado para {email}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {str(e)}")
            return False