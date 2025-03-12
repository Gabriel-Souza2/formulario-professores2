from datetime import timedelta
from django.utils import timezone
from formulario_professores.models import Mensagem
import requests
from celery import shared_task
from django.conf import settings
from datetime import datetime
import time

from django.utils.timezone import localtime
from .models import Mensagem
from datetime import datetime, timedelta
from django.core.cache import cache  

MAX_MENSAGENS_DIA = 65

def obter_tempo_ate_meia_noite():
    """Calcula quantos segundos faltam para meia-noite"""
    agora = datetime.now()
    meia_noite = datetime.combine(agora.date() + timedelta(days=1), datetime.min.time())  # Próxima meia-noite
    return int((meia_noite - agora).total_seconds())  # Segundos até meia-noite

@shared_task
def enviar_notificacao_whatsapp(contato, mensagem):
    """
    Envia uma mensagem via WhatsApp usando a Z-API.
    :param professor_nome: Nome do professor
    :param contato: Número de WhatsApp do professor (deve incluir o código do país, ex: +5511999999999)
    :param mensagem: Mensagem a ser enviada
    """
    # Configurar os detalhes da Z-API
    zapi_url = f"https://api.z-api.io/instances/{settings.ZAPI_INSTANCE_ID}/token/{settings.ZAPI_TOKEN}/send-text"
    
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

    # 🔹 Obtém quantas mensagens já foram enviadas hoje
    chave_contador = f"mensagens_enviadas_{datetime.today().date()}"
    mensagens_enviadas_hoje = cache.get(chave_contador, 0)

    print(f"📊 Mensagens enviadas hoje: {mensagens_enviadas_hoje}/{MAX_MENSAGENS_DIA}")


    if mensagens_enviadas_hoje >= MAX_MENSAGENS_DIA:
        print("🚨 Limite diário atingido! Nenhuma mensagem será enviada.")
        return

    for mensagem in mensagens:
        if mensagens_enviadas_hoje >= MAX_MENSAGENS_DIA:
            print("🚨 Limite atingido durante o envio! Parando envio.")
            break

        for contato in mensagem.contato:
            print(f"📩 Enviando mensagem para {contato}: {mensagem.mensagem_notificacao}")
            enviar_notificacao_whatsapp.delay(contato, mensagem.mensagem_notificacao)
            time.sleep(mensagem.intervalo_disparo)
            print(f"✅ Mensagem enviada para {contato}")
            mensagens_enviadas_hoje += 1

        timeout = obter_tempo_ate_meia_noite()
        cache.set(chave_contador, mensagens_enviadas_hoje, timeout=timeout)
