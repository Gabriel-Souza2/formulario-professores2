# admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Enviadas, UserMessageLimit
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.utils import timezone

# Função para contar as mensagens enviadas no dia
def contar_mensagens_hoje(user):
    hoje = timezone.now().date()
    return Enviadas.objects.filter(user=user, data_envio__date=hoje).count()

# Customizando o painel do User no Django Admin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Usando o formulário customizado para criação
    form = CustomUserChangeForm  # Usando o formulário customizado para edição

    list_display = ('username', 'email', 'quantidade_mensagens_hoje')  # Campos a exibir

    # Função que será chamada para exibir o campo "quantidade_mensagens_hoje"
    def quantidade_mensagens_hoje(self, obj):
        return contar_mensagens_hoje(obj)
    quantidade_mensagens_hoje.admin_order_field = 'quantidade_mensagens_hoje'  # Permite ordenar a lista por esse campo
    quantidade_mensagens_hoje.short_description = 'Mensagens Enviadas Hoje'  # Texto da coluna

# Desregistrando o User original e registrando o User com a customização
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class UserMessageLimitAdmin(admin.ModelAdmin):
    list_display = ('user', 'limite_diario')

admin.site.register(UserMessageLimit, UserMessageLimitAdmin)
