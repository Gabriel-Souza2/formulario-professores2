from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Aula(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    disciplina = models.CharField(max_length=100)
    quantidade_aulas = models.IntegerField()
    data_aulas = models.DateField()
    professor = models.CharField(max_length=100)
    contato = models.CharField(max_length=20)

    dias_antes = models.IntegerField(default=3, help_text="Quantos dias antes você deseja ser avisado?")
    
    mensagem_notificacao = models.TextField(blank=True, help_text="Mensagem personalizada para a notificação.")

    def __str__(self):
        return f'{self.disciplina} - {self.professor}'