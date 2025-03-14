from django import forms
from .models import Mensagem
import re

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class MensagemForm(forms.ModelForm):
    contato = forms.CharField(
        required=False,
        label="Contatos",
        help_text="Informe os contatos separados por vírgula.",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': "Exemplo: 11999999999, 88999999999",
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    dias_disparo = forms.MultipleChoiceField(
        choices=[(str(i), dia) for i, dia in enumerate(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'])],
        help_text="Selecione os dias para disparo.",
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    horario_disparo = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Selecione o horário para o disparo."
    )

    class Meta:
        model = Mensagem
        exclude = ['usuario']
        fields = ['dias_disparo', 'horario_disparo', 'contato', 'intervalo_disparo', 'mensagem_notificacao']
        widgets = {
            'intervalo_disparo': forms.NumberInput(attrs={
                'min': 1,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'mensagem_notificacao': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

    def clean_contato(self):
        """Formata os contatos corretamente."""
        contatos_raw = self.cleaned_data.get('contato', '')

        if not contatos_raw.strip():
            raise forms.ValidationError("O campo de contatos é obrigatório.")

        # Separa os contatos por vírgula e remove espaços extras
        contatos = [c.strip() for c in contatos_raw.split(',') if c.strip()]

        if not contatos:
            raise forms.ValidationError("Informe pelo menos um número de contato.")

        contatos_formatados = []
        for contato in contatos:
            contato_limpo = re.sub(r'\D', '', contato)  # Remove caracteres não numéricos

            if contato_limpo.startswith('55') and (len(contato_limpo) == 12 or len(contato_limpo) == 13):
                contato_formatado = f'+{contato_limpo}'
            elif len(contato_limpo) == 10 or len(contato_limpo) == 11:
                contato_formatado = f'+55{contato_limpo}'
            else:
                raise forms.ValidationError(f"O número {contato} não é válido. Ele deve ter 10 ou 11 dígitos após o DDD.")

            contatos_formatados.append(contato_formatado)

        # Retorna os contatos formatados como **string separada por vírgula**
        return ", ".join(contatos_formatados)

    def save(self, commit=True):
        """Salva os contatos como lista no JSONField."""
        instance = super().save(commit=False)

        contatos_string = self.cleaned_data.get("contato", "")
        instance.contato = contatos_string.split(", ")  # Converte de volta para lista

        if commit:
            instance.save()

        return instance

    def __init__(self, *args, **kwargs):
        """Converte lista de contatos para string ao carregar o formulário."""
        super(MensagemForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk and isinstance(self.instance.contato, list):
            self.fields['contato'].initial = ", ".join(self.instance.contato)  # Exibe como string no formulário


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')  # Campos que você quer exibir no form

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')  # Campos que você quer exibir no form