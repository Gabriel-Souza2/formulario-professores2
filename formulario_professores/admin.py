from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import Enviadas, UserMessageLimit
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Função para contar as mensagens enviadas no dia
def contar_mensagens_hoje(user):
    hoje = timezone.now().date()
    return Enviadas.objects.filter(user=user, data_envio__date=hoje).count()

# Customizando o painel do User no Django Admin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Formulário customizado para criação
    form = CustomUserChangeForm  # Formulário customizado para edição
    model = User  # 🔹 Define explicitamente o modelo User

    list_display = ('username', 'email', 'quantidade_mensagens_hoje')  # Campos visíveis no painel

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )

    def quantidade_mensagens_hoje(self, obj):
        return contar_mensagens_hoje(obj)

    quantidade_mensagens_hoje.short_description = 'Mensagens Enviadas Hoje'

# Desregistrando o User original e registrando o User com a customização
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class UserMessageLimitAdmin(admin.ModelAdmin):
    list_display = ('user', 'limite_diario')

admin.site.register(UserMessageLimit, UserMessageLimitAdmin)
