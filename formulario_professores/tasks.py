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
from .repositories import ZapiRepository
MAX_MENSAGENS_DIA = 65

def obter_tempo_ate_meia_noite():
    """Calcula quantos segundos faltam para meia-noite"""
    agora = datetime.now()
    meia_noite = datetime.combine(agora.date() + timedelta(days=1), datetime.min.time())  # Próxima meia-noite
    return int((meia_noite - agora).total_seconds())  # Segundos até meia-noite

@shared_task
def enviar_notificacao_whatsapp_texto(contato, mensagem, usuario_id):
    """
    Envia uma mensagem via WhatsApp usando a Z-API.
    :param professor_nome: Nome do professor
    :param contato: Número de WhatsApp do professor (deve incluir o código do país, ex: +5511999999999)
    :param mensagem: Mensagem a ser enviada
    """

    usuario = User.objects.get(id=usuario_id)
    instancia = Instancia.objects.get(usuario=usuario)
    # Configurar os detalhes da Z-API

    ZapiRepository.enviar_mensagem(
        instancia.id_instancia, 
        instancia.token_instancia, 
        settings.ZAPI_CLIENT_TOKEN, 
        contato, 
        mensagem 
    )
    
@shared_task
def enviar_notificacao_whatsapp_midia(contato, link, tipo, usuario_id):
    """
    Envia uma midia via WhatsApp usando a Z-API.
    :param contato: Número de WhatsApp do professor (deve incluir o código do país, ex: +5511999999999)
    :param mensagem: Mensagem a ser enviada
    """

    usuario = User.objects.get(id=usuario_id)
    instancia = Instancia.objects.get(usuario=usuario)
    # Configurar os detalhes da Z-API
    if tipo == 'video':

        ZapiRepository.enviar_video(
            instancia.id_instancia, 
            instancia.token_instancia, 
            settings.ZAPI_CLIENT_TOKEN, 
            contato, 
            link 
        )

    if tipo == 'imagem':

        ZapiRepository.enviar_imagem(
            instancia.id_instancia, 
            instancia.token_instancia, 
            settings.ZAPI_CLIENT_TOKEN, 
            contato, 
            link 
        )

    if tipo == 'imagem':

        ZapiRepository.enviar_audio(
            instancia.id_instancia, 
            instancia.token_instancia, 
            settings.ZAPI_CLIENT_TOKEN, 
            contato, 
            link 
        )
    
    

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

            if mensagem.modo_envio == "midia":
                midia_mensagem = mensagem.mensagem_midias.first()
                midia = midia_mensagem.midia
                link = midia.get_presigned_url()
                tipo = midia.tipo
                print(midia.nome)

                enviar_notificacao_whatsapp_midia.apply_async(args=[contato, link, tipo, usuario.id], countdown=delay) 

            if mensagem.modo_envio == "texto":
                   enviar_notificacao_whatsapp_texto.apply_async(args=[contato, mensagem.mensagem_notificacao, usuario.id], countdown=delay) 

            if mensagem.modo_envio == "ambos":

                midia_mensagem = mensagem.mensagem_midias.first()
                midia = midia_mensagem.midia
                link = midia.get_presigned_url()
                tipo = midia.tipo

                if mensagem.tipo_envio == 'texto_primeiro':
                    enviar_notificacao_whatsapp_texto.apply_async(args=[contato, mensagem.mensagem_notificacao, usuario.id], countdown=4)

                    enviar_notificacao_whatsapp_midia.apply_async(args=[contato, link, tipo, usuario.id], countdown=delay) 

                else:
                    enviar_notificacao_whatsapp_midia.apply_async(args=[contato, link, tipo, usuario.id], countdown=delay) 

                    
                    enviar_notificacao_whatsapp_texto.apply_async(args=[contato, mensagem.mensagem_notificacao, usuario.id], countdown=4)


            delay = mensagem.intervalo_disparo

            # Registra a mensagem no banco de dados
            Enviadas.objects.create(user=usuario, texto=mensagem.mensagem_notificacao)

            print(f"✅ Mensagem enviada para {contato}")
            
