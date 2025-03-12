from django.db import models
from django.contrib.auth.models import User

class Mensagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    dias_disparo = models.JSONField(blank=False, help_text="Dias da semana para disparo (0=Segunda, 1=Terça, ..., 6=Domingo)")
    horario_disparo = models.TimeField(help_text="Horário para disparo de mensagens", blank=False)
    contato = models.JSONField(blank=False)
    intervalo_disparo = models.IntegerField(help_text="Intervalo de disparo de mensagens")
    mensagem_notificacao = models.TextField(blank=True, help_text="Mensagem personalizada para a notificação.")

    def save(self, *args, **kwargs):
        super(Mensagem, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.mensagem_notificacao} - {self.horario_disparo}'
    
    def to_dict(self):
        return {
            'dias_disparo': self.dias_disparo,
            'horario_disparo': str(self.horario_disparo),
            'contato': self.contato,
            'intervalo_disparo': self.intervalo_disparo,
            'mensagem_notificacao': self.mensagem_notificacao,
            'id': self.id
        }
