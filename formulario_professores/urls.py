from django.urls import path
from django.contrib.auth import views as auth_views



from . import views

urlpatterns = [
    path('cadastrar/', views.cadastrar_aula, name='cadastrar_aula'),
    path('sucesso/', views.sucesso, name='sucesso'),  # Uma página simples de sucesso
    path('aulas/', views.listar_aulas, name='listar_aulas'),
    path('editar/<int:aula_id>/', views.editar_aula, name='editar_aula'),
    path('excluir/<int:aula_id>/', views.excluir_aula, name='excluir_aula'),

    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]