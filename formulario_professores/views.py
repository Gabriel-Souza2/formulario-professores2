from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MensagemForm, MidiaForm
from .models import Mensagem, Instancia, Enviadas, UserMessageLimit, Midia, MidiaMensagem
from django.http import JsonResponse
from .repositories import ZapiRepository
import uuid
from django.utils.timezone import now


import json


@login_required
def listar_aulas(request):
    instancia = Instancia.objects.filter(usuario=request.user).first()

    if not instancia:
        id_aleatorio = str(uuid.uuid4())[:5]  
        user_name = request.user.username  
        name = f't3a-cannon-{user_name}-{id_aleatorio}'  

        result = ZapiRepository.criar_instancia(name)  

        status = False

        if result and result.get("id") and result.get("token"):
            id_instancia = result.get('id')
            token_instancia = result.get('token')

            instancia = Instancia(
                usuario=request.user,
                id_instancia=id_instancia,
                token_instancia=token_instancia
            )
            instancia.save()
    
    else:
        result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
        status = result.get('connected', False)

    mensagens = Mensagem.objects.filter(usuario=request.user)
    mensagens_formatadas = []
    
    for mensagem in mensagens:
        semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        dias_disparos = [semana[int(dia)] for dia in mensagem.dias_disparo]

        midia_mensagem = mensagem.mensagem_midias.first()

        if midia_mensagem:
            midia = midia_mensagem.midia
        else:
            midia = None

        mensagens_formatadas.append({
            'dias_disparo': ", ".join(dias_disparos),
            'horario_disparo': mensagem.horario_disparo,
            'contato': ", ".join(mensagem.contato),
            'intervalo_disparo': mensagem.intervalo_disparo,
            'mensagem_notificacao': mensagem.mensagem_notificacao,
            'id': mensagem.id,
            'midia': midia
        })

    # 📊 **Calculando as mensagens enviadas hoje pelo usuário
    hoje = now().date()
    mensagens_enviadas = Enviadas.objects.filter(user=request.user, data_envio__date=hoje).count()

    # 🔹 **Buscando o limite de mensagens do usuário**
    limite = UserMessageLimit.objects.filter(user=request.user).first()
    limite_diario = limite.limite_diario if limite else 65  # Se não houver registro, assume 10 como padrão

    return render(request, 'listar.html', {
        'mensagens': mensagens_formatadas,
        'status': status,
        'mensagens_enviadas': mensagens_enviadas,
        'limite_diario': limite_diario,
    })

@login_required
def cadastrar_aula(request):
    midias = Midia.objects.filter(usuario=request.user)
    instancia = Instancia.objects.filter(usuario=request.user).first()
    result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
    status = result.get('connected', False)
    if request.method == 'POST':        
        form = MensagemForm(request.POST)
        if form.is_valid():
            menssagem = form.save(commit=False)  # Não salva ainda no banco de dados
            menssagem.usuario = request.user  # Associa o usuário logado à menssagem
            menssagem.save()  # Agora salva no banco de dados

            id_midia = request.POST.get('midia')

            if id_midia:

                midia = Midia.objects.filter(id=id_midia).first()

                MidiaMensagem.objects.create(
                    mensagem = menssagem,
                    midia = midia
                )

            return redirect('listar_aulas')  # Redireciona para a listagem de aulas
        else:
            print(form.errors)
    else:
        form = MensagemForm()

    return render(request, 'formulario.html', {
        'form': form, 
        'titulo': 'Cadastrar mensagem', 
        'mensagem_botao': 'Enviar', 
        'midias': midias,
        'status': status
    })

@login_required
def editar_aula(request, mensagem_id):
    mensagem = get_object_or_404(Mensagem, id=mensagem_id)  # Busca a aula pelo ID ou retorna 404
    midia_mensagem = mensagem.mensagem_midias.first()
    midias = Midia.objects.filter(usuario=request.user)

    instancia = Instancia.objects.filter(usuario=request.user).first()
    result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
    status = result.get('connected', False)
    if midia_mensagem:
        midia = midia_mensagem.midia
    else:
        midia = None
    if request.method == 'POST':
        form = MensagemForm(request.POST, instance=mensagem)
        if form.is_valid():
            form.save()
            return redirect('listar_aulas')
    else:
        form = MensagemForm(instance=mensagem)
    return render(request, 'formulario.html', {
        'form': form, 
        'mensagem': mensagem, 
        'titulo': 'Editar Mensagem', 
        'mensagem_botao': 'Salvar', 
        'midia_select': midia, 
        'midias': midias,
        'status': status
    })

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
    
def instancia(request):
    if not request.user.is_authenticated:
        return render(request, 'instancia.html', {'error': 'Usuário não autenticado'})

    # Buscar a instância do usuário autenticado
    instancia = Instancia.objects.filter(usuario=request.user).first()

    if instancia:
        # Buscar o QR code associado à instância
        qr_result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)

        if qr_result.get("value"):
            qr_code = qr_result.get("value")
        else: 
            qr_code = None
        status = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)


        contexto = {
            'id_instancia': instancia.id_instancia,
            'token_instancia': instancia.token_instancia,
            'qr_code_img_tag': qr_code,
            'status': status
        }
    else:
        contexto = {}

    return render(request, 'instancia.html', contexto)

def criar_instancia(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')

        if nome:
            result = ZapiRepository.criar_instancia(nome)


            if result and result.get("id") and result.get("token")  :
                mensagem = "Instância criada com sucesso!"
                sucesso = True

                id_instancia = result.get('id')
                token_instancia = result.get('token')

                # Salvando no banco de dados
                instancia = Instancia(
                    usuario=request.user,  # Supondo que o usuário logado esteja fazendo a requisição
                    id_instancia=id_instancia,
                    token_instancia=token_instancia
                )
                instancia.save()

                # Obtendo o QR code para a instância
                instancia = Instancia.objects.get(id_instancia=result.get("id"))
                qr_result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
                
                if qr_result.get("status") == "success":
                    qr_code_base64 = qr_result.get("image_base64")  # Recebe o QR code em base64
                    qr_code_img_tag = f"data:image/png;base64,{qr_code_base64}"  # Formata como string base64
                else:
                    qr_code_img_tag = None  # Caso o QR code não tenha sido encontrado
                    mensagem_qr = qr_result.get("message", "Erro ao obter QR Code")
            else:
                mensagem = result.get('message', 'Erro desconhecido.')
                sucesso = False
                qr_code_img_tag = None  # Caso haja erro na criação da instância

        else:
            mensagem = "Nome não fornecido."
            sucesso = False
            qr_code_img_tag = None  # Caso o nome não tenha sido fornecido

        # Retornando para o template com a mensagem e QR code base64
        return render(request, 'instancia.html', {
            'sucesso': sucesso, 
            'mensagem': mensagem,
            'qr_code_img_tag': qr_code_img_tag
        })

    return render(request, 'instancia.html')

def desconectar_instancia(request):
    instancia = Instancia.objects.filter(usuario=request.user).first()
    result = ZapiRepository.desconectar(instancia.id_instancia, instancia.token_instancia)

    if result.get("value") == True:
        status = False
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
        return render(request, 'listar.html', {'mensagens': mensagens_formatadas, 'status': status})

@login_required
def upload_midia(request):
    instancia = Instancia.objects.filter(usuario=request.user).first()
    result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
    status = result.get('connected', False)

    if request.method == "POST":
        form = MidiaForm(request.POST, request.FILES)
        if form.is_valid():
            midia = form.save(commit=False) # Isso irá salvar o arquivo e gerar o link
            midia.usuario = request.user
            midia.save()

            midias = Midia.objects.filter(usuario=request.user)
            return render(request, 'listar_midias.html', {'form': form, 'midias': midias})
    else:
        form = MidiaForm()
    return render(request, 'upload.html', {'form': form, 'status': status})

@login_required
def listar_midias(request):
    instancia = Instancia.objects.filter(usuario=request.user).first()
    result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
    status = result.get('connected', False)

    midias = Midia.objects.filter(usuario=request.user)  # Filtra apenas mídias do usuário logado
    return render(request, 'listar_midias.html', {'midias': midias, 'status': status})

@login_required
def editar_midia(request, midia_id):
    midia = get_object_or_404(Midia, id=midia_id, usuario=request.user)  # Garante que só o dono pode editar

    instancia = Instancia.objects.filter(usuario=request.user).first()
    result = ZapiRepository.get_qrcode(instancia.id_instancia, instancia.token_instancia)
    status = result.get('connected', False)

    if request.method == "POST":
        form = MidiaForm(request.POST, request.FILES, instance=midia)
        if form.is_valid():
            form.save()
            return redirect('listar_midias')
    else:
        form = MidiaForm(instance=midia)

    return render(request, 'editar_midia.html', {'form': form, 'status': status})

@login_required
def excluir_midia(request, midia_id):
    midia = get_object_or_404(Midia, id=midia_id, usuario=request.user)
    midia.delete()
    return redirect('listar_midias')

def gerar_presigned_url(request, midia_id):
    # Obtém o objeto Midia
    midia = Midia.objects.get(id=midia_id)
    
    # Chama o método get_presigned_url
    url = midia.get_presigned_url()
    
    if url:
        # Redireciona para o URL gerado
        return redirect(url)
    else:
        # Se não houver URL (caso o arquivo não tenha sido encontrado), redireciona para uma página de erro ou outra URL
        return redirect('erro')  # Substitua 'erro' pela URL ou view de erro que você deseja