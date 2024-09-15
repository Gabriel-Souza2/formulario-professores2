from datetime import timedelta
from django.utils import timezone
from formulario_professores.models import Aula
import requests
from celery import shared_task
from django.conf import settings
from datetime import datetime
import time

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
            enviar_notificacao_whatsapp.delay(aula.contato, mensagem)

            time.sleep(120)



def notificar_no_dia_da_aula(aula_id):
    """
    Task para notificar o professor no próprio dia da aula.
    """
    try:
        # Obter os detalhes da aula
        aula = Aula.objects.get(id=aula_id)
        
        # Verificar se a data da aula é hoje
        hoje = datetime.now().date()
        if aula.data_aulas == hoje:
            mensagem = aula.mensagem_notificacao or f"Sua aula de {aula.disciplina} está agendada para hoje."
            
            # Enviar a notificação via WhatsApp usando a Z-API
            enviar_notificacao_whatsapp(aula.contato, mensagem)

            time.sleep(120)

    except Aula.DoesNotExist:
        print("Aula não encontrada.")
    except Exception as e:
        print(f"Erro ao notificar no dia da aula: {e}")