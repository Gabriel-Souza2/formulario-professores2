from django.db import models

# Create your models here.
class Aula(models.Model):
    disciplina = models.CharField(max_length=100)
    quantidade_aulas = models.IntegerField()
    data_aulas = models.DateField()
    professor = models.CharField(max_length=100)
    contato = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.disciplina} - {self.professor}'