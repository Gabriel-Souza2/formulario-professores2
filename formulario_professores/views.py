from django.shortcuts import render, redirect, get_object_or_404
from .forms import AulaForm
from .models import Aula


# Create your views here.
def listar_aulas(request):
    aulas = Aula.objects.all()  # Busca todas as aulas cadastradas
    return render(request, 'listar.html', {'aulas': aulas})

def cadastrar_aula(request):
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            form.save()  # Salva os dados no banco de dados
            return redirect('sucesso')  # Redireciona para uma página de sucesso ou outra view
    else:
        form = AulaForm()

    return render(request, 'formulario.html', {'form': form})

def editar_aula(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id)  # Busca a aula pelo ID ou retorna 404
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            return redirect('listar_aulas')
    else:
        form = AulaForm(instance=aula)
    return render(request, 'editar_aula.html', {'form': form, 'aula': aula})

def sucesso(request):
    return render(request, 'sucesso.html')