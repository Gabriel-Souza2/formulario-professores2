# Generated by Django 5.1.1 on 2024-09-14 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formulario_professores', '0002_aula_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='aula',
            name='dias_antes',
            field=models.IntegerField(default=3, help_text='Quantos dias antes você deseja ser avisado?'),
        ),
        migrations.AddField(
            model_name='aula',
            name='mensagem_notificacao',
            field=models.TextField(blank=True, help_text='Mensagem personalizada para a notificação.'),
        ),
    ]
