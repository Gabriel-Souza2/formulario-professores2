from datetime import timedelta
from django.utils import timezone
from formulario_professores.models import Mensagem
import requests
from celery import shared_task
from django.conf import settings
from datetime import datetime
import time

from django.utils.timezone import localtime
from .models import Mensagem, Instancia, User, Enviadas, UserMessageLimit
from datetime import datetime, timedelta
from django.core.cache import cache  

MAX_MENSAGENS_DIA = 65

def obter_tempo_ate_meia_noite():
    """Calcula quantos segundos faltam para meia-noite"""
    agora = datetime.now()
    meia_noite = datetime.combine(agora.date() + timedelta(days=1), datetime.min.time())  # Próxima meia-noite
    return int((meia_noite - agora).total_seconds())  # Segundos até meia-noite

@shared_task
def enviar_notificacao_whatsapp(contato, mensagem, usuario_id):
    """
    Envia uma mensagem via WhatsApp usando a Z-API.
    :param professor_nome: Nome do professor
    :param contato: Número de WhatsApp do professor (deve incluir o código do país, ex: +5511999999999)
    :param mensagem: Mensagem a ser enviada
    """

    usuario = User.objects.get(id=usuario_id)
    instancia = Instancia.objects.get(usuario=usuario)
    # Configurar os detalhes da Z-API
    zapi_url = f"https://api.z-api.io/instances/{instancia.id_instancia}/token/{instancia.token_instancia}/send-text"
    
    # Conteúdo da mensagem a ser enviada
    payload = {
        "phone": contato,
        "message": f"{mensagem}"
    }

    # Fazer a requisição POST para a API da Z-API
    try:
        response = requests.post(zapi_url, json=payload, headers={'Content-Type': "application/json", 'Client-Token': settings.ZAPI_CLIENT_TOKEN})
        response.raise_for_status()  # Levanta uma exceção para status HTTP >= 400
        return response.json()  # Retorna a resposta da API se tudo ocorrer bem
    except requests.RequestException as e:
        print(f"Erro ao enviar a mensagem para o WhatsApp: {e}")
        return None
    
    

@shared_task
def verificar_disparos():
    agora = localtime().time()  # Hora atual do servidor
    dia_atual = str(datetime.today().weekday())  # Obtém o número do dia (0=Segunda, 6=Domingo)
    
    print(f"⏳ Verificando disparos - Hora Atual: {agora}, Dia Atual: {dia_atual}")

    mensagens = Mensagem.objects.filter(
        horario_disparo__hour=agora.hour, 
        horario_disparo__minute=agora.minute,  # Agora considerando minuto
        dias_disparo__contains=dia_atual
    )

    # 🔹 Verificar quantas mensagens um usuário já enviou hoje
    for mensagem in mensagens:
        usuario = mensagem.usuario
        hoje = timezone.now().date()  # Obtém a data atual

        # Obtém o limite diário do usuário (ou usa um padrão se não existir)
        limite_mensagens = UserMessageLimit.objects.filter(user=usuario).first()
        if not limite_mensagens:
            limite_diario = 65  # Defina um valor padrão se o usuário não tiver um limite definido
        else:
            limite_diario = limite_mensagens.limite_diario

        # Contabiliza as mensagens enviadas hoje
        mensagens_enviadas_hoje = Enviadas.objects.filter(
            user=usuario, 
            data_envio__date=hoje
        ).count()

        print(f"📊 Mensagens enviadas hoje pelo usuário {usuario.username}: {mensagens_enviadas_hoje}/{limite_diario}")

        if mensagens_enviadas_hoje >= limite_diario:
            print(f"🚨 Limite diário de mensagens atingido para {usuario.username}! Nenhuma mensagem será enviada.")
            continue  # Pula para o próximo usuário se o limite for atingido

        delay = 0
        for contato in mensagem.contato:
            print(f"📩 Enviando mensagem para {contato}: {mensagem.mensagem_notificacao}")
            
            # Envia a mensagem via task do Celery
            enviar_notificacao_whatsapp.apply_async(args=[contato, mensagem.mensagem_notificacao, usuario.id], countdown=delay)

            delay = mensagem.intervalo_disparo

            # Registra a mensagem no banco de dados
            Enviadas.objects.create(user=usuario, texto=mensagem.mensagem_notificacao)

            print(f"✅ Mensagem enviada para {contato}")
            
