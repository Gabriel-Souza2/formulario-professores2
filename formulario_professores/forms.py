from django import forms
from .models import Aula
import re

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['disciplina', 'quantidade_aulas', 'data_aulas', 'professor', 'contato', 'dias_antes', 'mensagem_notificacao']
        widgets = {
            'data_aulas': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'contato': forms.TextInput(attrs={ 'type':'tel','placeholder': 'Telefone de Contato', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'data_aulas': forms.DateInput(attrs={'type': 'date'}),
            'mensagem_notificacao': forms.Textarea(attrs={'rows': 3}),
        }

    # Validação personalizada para o campo 'contato'
    def clean_contato(self):
        contato = self.cleaned_data.get('contato')
        # Exigir que o número de telefone tenha tenha 10-15 caracteres
        if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', contato):
            raise forms.ValidationError('O número de telefone deve ter entre 10 e 15 caracteres.')
        return contato
    
    def __init__(self, *args, **kwargs):
        super(AulaForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
            if self.errors.get(field):
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-4 py-2 border border-red-500 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500'
                })