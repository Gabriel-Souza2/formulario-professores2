from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AulaForm
from .models import Aula


@login_required
def listar_aulas(request):
    aulas = Aula.objects.filter(usuario=request.user)
    return render(request, 'listar.html', {'aulas': aulas})

@login_required
def cadastrar_aula(request):
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)  # Não salva ainda no banco de dados
            aula.usuario = request.user  # Associa o usuário logado à aula
            aula.save()  # Agora salva no banco de dados
            return redirect('listar_aulas')  # Redireciona para a listagem de aulas
    else:
        form = AulaForm()
    return render(request, 'formulario.html', {'form': form, 'titulo': 'Cadastrar aula', 'mensagem_botao': 'Enviar'})

@login_required
def editar_aula(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id)  # Busca a aula pelo ID ou retorna 404
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            return redirect('listar_aulas')
    else:
        form = AulaForm(instance=aula)
    return render(request, 'formulario.html', {'form': form, 'aula': aula, 'titulo': 'Editar aula', 'mensagem_botao': 'Salvar'})

@login_required
def excluir_aula(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id)
    if request.method == 'POST':
        aula.delete()  # Exclui a aula
        return redirect('listar_aulas')
    return render(request, 'excluir.html', {'aula': aula})

@login_required
def sucesso(request):
    return render(request, 'sucesso.html')