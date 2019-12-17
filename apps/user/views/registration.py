from django.shortcuts import render
from apps.user import models

def register(request):
    dados = {
        'estados': models.Estado.objects.all(),
        'paises' : models.Pais.objects.all(),
        'tipo_inscricoes' : models.Tipo_Inscricao.objects.all(),
        'titulos': models.Titulacao.objects.all()
    }

    return render(request, 'user/registration.html', { 'dados': dados })
    