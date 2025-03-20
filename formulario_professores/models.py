from django.db import models
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from django.conf import settings

class Mensagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    dias_disparo = models.JSONField(blank=False)
    horario_disparo = models.TimeField(blank=False)
    contato = models.JSONField(blank=False)
    intervalo_disparo = models.IntegerField()
    mensagem_notificacao = models.TextField(blank=True)
    
    tipo_envio = models.CharField(
        max_length=15,
        choices=[
            ("texto_primeiro", "Texto Primeiro"),
            ("midia_primeiro", "Mídia Primeiro")
        ],
        default="texto_primeiro"
    )
    
    modo_envio = models.CharField(
        max_length=10,
        choices=[
            ("texto", "Somente Texto"),
            ("midia", "Somente Mídia"),
            ("ambos", "Ambos")
        ],
        default="ambos"
    )

    ordem_envio = models.IntegerField(default=0)  # Ordem de envio da mensagem

class Instancia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    id_instancia = models.CharField(max_length=255, unique=True)
    token_instancia = models.TextField()

    def __str__(self):
        return f"Instância {self.id_instancia} de {self.usuario.username}"
    
class Enviadas(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuário que enviou a mensagem
    texto = models.TextField()  # Conteúdo da mensagem
    data_envio = models.DateTimeField(auto_now_add=True)  # Data e hora do envio

    def __str__(self):
        return f"Mensagem enviada por {self.user.username} em {self.data_envio}"
    
class UserMessageLimit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    limite_diario = models.IntegerField(default=65)  # Define um limite padrão de 10 mensagens por dia

    def __str__(self):
        return f"{self.user.username} - Limite: {self.limite_diario} mensagens/dia"
    
    class Meta:
        verbose_name = "Limite de Mensagens do Usuário"
        verbose_name_plural = "Limites de Mensagens dos Usuários"

class Midia(models.Model):
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True, max_length=500)  # URL do arquivo no S3
    arquivo = models.FileField(upload_to='midia/', storage=S3Boto3Storage())  # Usando o S3 como storage
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='midias')

    def __str__(self):
        return self.nome
    
    def get_presigned_url(self):
        # Verifica se o arquivo está presente
        if not self.arquivo:
            return None
        
        # Conectar ao S3 com as credenciais configuradas no settings.py
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        try:
            # Gera o presigned URL com validade de 1 hora
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,  # Nome do bucket configurado no settings
                    'Key': self.arquivo.name  # Caminho do arquivo no S3
                },
                ExpiresIn=3600  # Link válido por 1 hora
            )
            return url
        except Exception as e:
            # Retorna None ou loga o erro caso ocorra alguma falha
            return None
        
    def delete(self, *args, **kwargs):
        """Exclui o arquivo do S3 antes de remover o objeto do banco de dados."""
        if self.arquivo:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            try:
                s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.arquivo.name)
            except Exception as e:
                print(f"Erro ao excluir do S3: {e}")

        # Agora exclui do banco
        super().delete(*args, **kwargs)


class MidiaMensagem(models.Model):
    mensagem = models.ForeignKey('Mensagem', on_delete=models.CASCADE, related_name="mensagem_midias")
    midia = models.ForeignKey(Midia, on_delete=models.CASCADE, related_name="midia_mensagens")
    
