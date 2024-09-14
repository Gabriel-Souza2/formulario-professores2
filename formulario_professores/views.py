from django.shortcuts import render, redirect
from .forms import AulaForm


# Create your views here.
def cadastrar_aula(request):
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            form.save()  # Salva os dados no banco de dados
            return redirect('sucesso')  # Redireciona para uma página de sucesso ou outra view
    else:
        form = AulaForm()

    return render(request, 'formulario.html', {'form': form})

def sucesso(request):
    return render(request, 'sucesso.html')