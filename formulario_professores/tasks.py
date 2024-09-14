from datetime import timedelta
from django.utils import timezone
from .models import Aula
import requests
from celery import shared_task
from django.conf import settings

@shared_task
def enviar_notificacao_whatsapp(professor_nome, contato, mensagem):
    """
    Envia uma mensagem via WhatsApp usando a Z-API.
    :param professor_nome: Nome do professor
    :param contato: Número de WhatsApp do professor (deve incluir o código do país, ex: +5511999999999)
    :param mensagem: Mensagem a ser enviada
    """
    # Configurar os detalhes da Z-API
    zapi_url = f"https://api.z-api.io/instances/{settings.ZAPI_INSTANCE_ID}/token/{settings.ZAPI_TOKEN}/send-messages"
    
    # Conteúdo da mensagem a ser enviada
    payload = {
        "phone": contato,
        "message": f"Olá, {professor_nome}! {mensagem}"
    }

    # Fazer a requisição POST para a API da Z-API
    try:
        response = requests.post(zapi_url, json=payload)
        response.raise_for_status()  # Levanta uma exceção para status HTTP >= 400
        return response.json()  # Retorna a resposta da API se tudo ocorrer bem
    except requests.RequestException as e:
        print(f"Erro ao enviar a mensagem para o WhatsApp: {e}")
        return None


@shared_task
def verificar_aulas_e_notificar():
    """
    Verifica as aulas que estão chegando e envia notificações para os professores.
    """
    hoje = timezone.now().date()
    
    # Obtenha todas as aulas que ainda não ocorreram
    aulas = Aula.objects.filter(data_aulas__gte=hoje)
    
    for aula in aulas:
        data_aviso = aula.data_aulas - timedelta(days=aula.dias_antes)
        if data_aviso <= hoje:
            # Use o campo `mensagem_notificacao` ou uma mensagem padrão
            mensagem = aula.mensagem_notificacao or f"Sua aula de {aula.disciplina} está agendada para {aula.data_aulas}."
            
            # Enviar a mensagem via WhatsApp
            enviar_notificacao_whatsapp.delay(aula.professor, aula.contato, mensagem)
