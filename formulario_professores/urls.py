from django.urls import path


from . import views

urlpatterns = [
    path('cadastrar/', views.cadastrar_aula, name='cadastrar_aula'),
    path('sucesso/', views.sucesso, name='sucesso'),  # Uma página simples de sucesso
]