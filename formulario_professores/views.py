from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MensagemForm
from .models import Mensagem

import json


@login_required
def listar_aulas(request):
    mensagens = Mensagem.objects.filter(usuario=request.user)
    mensagens_formatadas = []
    for mensagem in mensagens:
        contato = mensagem.contato

        print(contato)
        semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sabado', 'Domingo']
        dias_disparos = []
        for dia in mensagem.dias_disparo:
            dias_disparos.append(semana[int(dia)])



        mensagens_formatadas.append({
            'dias_disparo': ", ".join(dias_disparos),
            'horario_disparo': mensagem.horario_disparo,
            'contato': ", ".join(contato),  # Se você precisar exibir como uma string
            'intervalo_disparo': mensagem.intervalo_disparo,
            'mensagem_notificacao': mensagem.mensagem_notificacao,
            'id': mensagem.id
        })
    return render(request, 'listar.html', {'mensagens': mensagens_formatadas})

@login_required
def cadastrar_aula(request):
    if request.method == 'POST':        
        form = MensagemForm(request.POST)
        print(form)
        if form.is_valid():
            aula = form.save(commit=False)  # Não salva ainda no banco de dados
            aula.usuario = request.user  # Associa o usuário logado à aula
            aula.save()  # Agora salva no banco de dados
            return redirect('listar_aulas')  # Redireciona para a listagem de aulas
        else:
            print(form.errors)
    else:
        form = MensagemForm()

    return render(request, 'formulario.html', {'form': form, 'titulo': 'Cadastrar mensagem', 'mensagem_botao': 'Enviar'})

@login_required
def editar_aula(request, mensagem_id):
    mensagem = get_object_or_404(Mensagem, id=mensagem_id)  # Busca a aula pelo ID ou retorna 404
    if request.method == 'POST':
        form = MensagemForm(request.POST, instance=mensagem)
        if form.is_valid():
            form.save()
            return redirect('listar_aulas')
    else:
        form = MensagemForm(instance=mensagem)
    return render(request, 'formulario.html', {'form': form, 'mensagem': mensagem, 'titulo': 'Editar Mensagem', 'mensagem_botao': 'Salvar'})

@login_required
def excluir_aula(request, aula_id):
    aula = get_object_or_404(Mensagem, id=aula_id)
    if request.method == 'POST':
        aula.delete()  # Exclui a aula
        return redirect('listar_aulas')
    return render(request, 'excluir.html', {'aula': aula})

@login_required
def sucesso(request):
    return render(request, 'sucesso.html')


from django.contrib.auth.views import LoginView
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def form_invalid(self, form):
        # Adiciona uma mensagem de erro ao contexto se o login falhar
        messages.error(self.request, 'Credenciais inválidas. Por favor, tente novamente.')
        return super().form_invalid(form)